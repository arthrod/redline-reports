"""Tests for tools/extract_trial_metrics.py, on small hand-built session logs and trajectories."""

import json
import sys
from typing import Any

import extract_trial_metrics as x
import httpx2
import polars as pl
import pytest
from huggingface_hub.errors import RepositoryNotFoundError

KEY = ("job", "trial")


def line(kind: str, at: str, **kw: Any) -> str:
    return json.dumps({"type": kind, "timestamp": f"2026-10-17T00:{at}Z", **kw})


def reply(at: str, mid: str, out: int, model: str = "m") -> str:
    usage = {"input_tokens": 10, "cache_read_input_tokens": 100, "cache_creation_input_tokens": 5, "output_tokens": out}
    return line("assistant", at, message={"id": mid, "model": model, "usage": usage})


def test_session_log_counts_responses_tokens_and_inference_time() -> None:
    text = "\n".join(
        [
            line("user", "00:00"),
            reply("00:30", "a", 7),  # 30 s after the prompt
            reply("00:40", "a", 7),  # the same response, still streaming: ends at 00:40
            line("user", "01:00"),  # tool result
            reply("01:20", "b", 3),
            reply("01:25", "s", 9, model="<synthetic>"),  # not a model call
            "not json",
        ]
    )
    r = x.from_session(KEY, [text])
    assert r is not None
    assert (r["api_calls"], r["in_uncached"], r["cache_read"], r["cache_write"], r["out"]) == (2, 20, 200, 10, 10)
    assert r["inference_min"] == pytest.approx((40 + 20) / 60)
    assert r["call_gap_min"] == pytest.approx(40 / 60)  # first response ends 00:40, last 01:20


def test_a_response_logged_in_two_files_counts_once() -> None:
    a = "\n".join([line("user", "00:00"), reply("00:30", "a", 7)])
    both = "\n".join([line("user", "00:00"), reply("00:30", "a", 7), line("user", "01:00"), reply("01:20", "b", 3)])
    r = x.from_session(KEY, [a, both])
    assert r is not None
    assert (r["api_calls"], r["out"]) == (2, 10)


def test_session_without_responses_gives_no_row() -> None:
    assert x.from_session(KEY, [line("user", "00:00")]) is None


def test_trajectory_counts_calls_and_splits_cached_input() -> None:
    steps: list[dict[str, Any]] = [
        {"source": "user"},
        {
            "source": "agent",
            "timestamp": "2026-11-05T00:00:00Z",
            "llm_call_count": 2,
            "metrics": {"prompt_tokens": 1000, "cached_tokens": 900, "completion_tokens": 50},
        },
        {
            "source": "agent",
            "timestamp": "2026-11-05T00:03:00Z",
            "metrics": {
                "prompt_tokens": 500,
                "completion_tokens": 20,
                "extra": {"cache_read_input_tokens": 300, "cache_creation_input_tokens": 100},
            },
        },
        {"source": "agent"},  # no metrics: not a model call
    ]
    r = x.from_atif(KEY, steps)
    assert r is not None
    assert (r["api_calls"], r["in_uncached"], r["cache_read"], r["cache_write"], r["out"]) == (3, 200, 1200, 100, 70)
    assert r["inference_min"] is None
    assert r["call_gap_min"] == pytest.approx(3.0)
    assert x.from_atif(KEY, [{"source": "user"}]) is None


def no_access() -> list[str]:
    request = httpx2.Request("GET", "https://huggingface.co/api/datasets/" + x.PRIVATE)
    raise RepositoryNotFoundError("401", response=httpx2.Response(401, request=request))


def test_private_archive_out_of_reach_gives_no_shards(capsys: pytest.CaptureFixture[str]) -> None:
    assert x.private_shards(no_access) == []
    assert "Muse jubarte" in capsys.readouterr().err


def test_other_listing_errors_still_stop_the_run() -> None:
    def broken() -> list[str]:
        raise ValueError("bad listing")

    with pytest.raises(ValueError):
        x.private_shards(broken)


def test_only_data_shards_are_read() -> None:
    assert x.private_shards(lambda: ["a/files-0001.parquet", "README.md"]) == ["a/files-0001.parquet"]


def test_a_trial_split_across_shards_is_read_whole() -> None:
    first = pl.DataFrame({"trial_name": ["t1", "t2"], "text": [reply("00:10", "a", 4), reply("00:10", "c", 1)]})
    second = pl.DataFrame({"trial_name": ["t1"], "text": [reply("00:20", "b", 6)]})
    rows = {r["trial_name"]: r for r in x.muse_rows([first, second])}
    assert sorted(rows) == ["t1", "t2"]
    assert (rows["t1"]["api_calls"], rows["t1"]["out"]) == (2, 10)


def test_a_trial_twice_in_the_output_is_an_error() -> None:
    row = {"job": "j", "trial_name": "t", "api_calls": 1}
    assert x.metrics_frame([row, {**row, "trial_name": "u"}]).height == 2
    with pytest.raises(ValueError, match="j/t"):
        x.metrics_frame([row, {**row, "api_calls": 2}])


def session(trial: str, out: int, job: str = "", path: str = "") -> dict[str, str]:
    text = "\n".join([line("user", "00:00"), reply("00:30", f"{trial}-r", out)])
    row = {"trial_name": trial, "path_in_trial": "agent/sessions/projects/-app/s.jsonl", "text": text}
    return {**row, **({"job": job} if job else {}), **({"path": path} if path else {})}


def atif_step(minute: int) -> str:
    return json.dumps({"source": "agent", "timestamp": f"2026-11-05T00:0{minute}:00Z", "metrics": {"prompt_tokens": 9}})


class Archive:
    """Stands in for HfApi: lists two data shards and a card, or refuses like a private repo."""

    readable = True

    def list_repo_files(self, repo: str, repo_type: str) -> list[str]:
        assert (repo, repo_type) == (x.PRIVATE, "dataset")
        if not self.readable:
            no_access()
        return ["a/files-1.parquet", "a/files-2.parquet", "b/files-3.parquet", "README.md"]


def run_main(tmp_path: Any, monkeypatch: pytest.MonkeyPatch, readable: bool) -> pl.DataFrame:
    muse = f"runs/{x.MUSE_JOB}/t/"
    lazy: dict[str, list[dict[str, Any]]] = {
        x.DS + "redlinebench/files-*.parquet": [session("d1", 4, job="ds"), session("d2", 5, job="other")],
        x.DS + "harvey_lab/files-*.parquet": [session("h1", 6)],
        x.LA + "a/files-1.parquet": [session("m1", 7, path=muse), session("x9", 1, path="runs/other/t/")],
        x.LA + "a/files-2.parquet": [{**session("m1", 8, path=muse), "text": reply("00:50", "m1-late", 8)}],
        x.LA + "b/files-3.parquet": [{"something": "else"}],
        x.JT: [{"job": f"{x.MUSE_JOB}-ooriginal", "trial_name": "c1", "trajectory_json": json.dumps([])},
               {"job": f"{x.MUSE_JOB}-ooriginal", "trial_name": "c2",
                "trajectory_json": json.dumps({"steps": [json.loads(atif_step(1)), json.loads(atif_step(4))]})},
               {"job": f"{x.MUSE_JOB}-ooriginal", "trial_name": "c3", "trajectory_json": None}],
        x.DS + "harvey_lab_017/steps/part-*.parquet": [
            {"trial_uuid": "u1", "step_index": i, "step_json": atif_step(i)} for i in (0, 2)
        ],
    }  # fmt: skip
    trials = {x.DS + "harvey_lab_017/trials/part-00000.parquet": [{"uuid": "u1", "trial": "e1"}]}
    monkeypatch.setattr(pl, "scan_parquet", lambda p: pl.LazyFrame(lazy[p]))
    monkeypatch.setattr(pl, "read_parquet", lambda p: pl.DataFrame(trials[p]))
    archive = Archive()
    archive.readable = readable
    monkeypatch.setattr("huggingface_hub.HfApi", lambda: archive)
    (tmp_path / "data").mkdir()
    cohorts = [
        ("0.14.0 DeepSeek", "ds", "d1"),
        ("0.16 Harvey", "harvey-hub-ab", "h1"),
        ("Muse Spark 1.3", x.MUSE_JOB, "m1"),
        ("Muse Spark 1.3", f"{x.MUSE_JOB}-ooriginal", "c2"),
        ("0.17 Harvey", "harvey-0.17", "e1"),
    ]
    pl.DataFrame(cohorts, schema=["cohort", "job", "trial_name"], orient="row").with_columns(
        arm=pl.lit("jubarte")
    ).write_csv(tmp_path / x.CSV)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["extract", "out.csv"])
    x.main()
    return pl.read_csv(tmp_path / "out.csv")


def test_main_writes_one_row_per_trial_from_every_source(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    out = run_main(tmp_path, monkeypatch, readable=True)
    got = {r["trial_name"]: (r["source"], r["api_calls"], r["out"]) for r in out.iter_rows(named=True)}
    assert got == {
        "d1": ("session log", 1, 4),
        "h1": ("session log", 1, 6),
        "m1": ("session log", 2, 15),  # one response in each shard
        "c2": ("trajectory", 2, 0),
        "e1": ("trajectory", 2, 0),
    }


def test_main_still_writes_the_public_rows_without_the_private_archive(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    out = run_main(tmp_path, monkeypatch, readable=False)
    assert out.height == 5
    assert out.filter(pl.col("api_calls").is_null())["trial_name"].to_list() == ["m1"]
