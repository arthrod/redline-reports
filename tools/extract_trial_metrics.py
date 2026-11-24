"""Per-trial API calls, token usage and inference time for the six cohorts, both arms.

Writes data/trial_metrics.csv: one row per trial in data/cohort_trials.csv,
with the per-trial fields of that file plus:

  source            "session log" (Claude Code JSONL) or "trajectory" (ATIF steps)
  api_calls         model responses (session log: unique message ids, synthetic ones excluded;
                    trajectory: sum of llm_call_count over agent steps)
  in_uncached, cache_read, cache_write, out   summed from per-response usage
  inference_min     session log only: for each response, time from the last event before it
                    (prompt or tool result) to its last streamed line, summed. Null for
                    trajectory sources, which carry no tool-result timestamps.
  call_gap_min      trajectory and session log: time from the end of the first response to the
                    end of the last. It includes tool execution between them and leaves out the
                    first response's own latency, so it is not a bound on inference time.

Sources: the public redline-bench-deepseek-trajectories (DeepSeek, Nemotron, both Harvey cohorts),
the public redline-bench-jubarte-trajectories (Muse control trajectories) and the private
redline-bench-local-archive (Muse jubarte session logs). Without access to the private archive the
Muse jubarte rows come out empty and the rest is still written.

A trial's session files are read together: a response is counted once even if two files log it,
and a trial whose files sit in more than one shard of the archive is read whole.

Run from the repository root: uv run python tools/extract_trial_metrics.py [output.csv]
"""

from __future__ import annotations

import json
import sys
from collections.abc import Callable, Iterable
from datetime import datetime
from typing import Any

import polars as pl

CSV = "data/cohort_trials.csv"
DS = "hf://datasets/arthrod/redline-bench-deepseek-trajectories/"
PRIVATE = "arthrod/redline-bench-local-archive"
LA = f"hf://datasets/{PRIVATE}/"
JT = "hf://datasets/arthrod/redline-bench-jubarte-trajectories/data/redline_bench_extra_trials.parquet"
SESSION = r"^agent/sessions/projects/-app/[^/]+\.jsonl$"
MUSE_JOB = "muse-1-3-contributor-total"

Row = dict[str, Any]


def ts(s: str | None) -> datetime | None:
    return datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None


def from_session(key: tuple[str, str], texts: list[str]) -> Row | None:
    """One trial's metrics from all of its session files. A message id is one response, in any file."""
    msgs: dict[str, Row] = {}
    for text in texts:
        events = []
        for line in text.splitlines():
            if not line.strip():
                continue
            try:
                o = json.loads(line)
            except Exception:
                continue
            if o.get("type") in ("assistant", "user", "system") and o.get("timestamp"):
                events.append(o)
        prev_other = None
        for o in events:
            t = ts(o["timestamp"])
            if o["type"] != "assistant":
                prev_other = t
                continue
            m = o.get("message") or {}
            if m.get("model") == "<synthetic>":
                continue
            mid = m.get("id") or o.get("uuid")
            r = msgs.setdefault(mid, dict(start=prev_other, end=t, usage={}, usage_at=None))
            if r["start"] is None:  # a copy that opens on the response itself has no start; another copy may
                r["start"] = prev_other
            r["end"] = max(r["end"], t)
            if m.get("usage") and (r["usage_at"] is None or t >= r["usage_at"]):  # newest usage, in any file order
                r["usage"], r["usage_at"] = m["usage"], t
    if not msgs:
        return None
    tok = dict(in_uncached=0, cache_read=0, cache_write=0, out=0)
    inference = 0.0
    for r in msgs.values():
        u = r["usage"]
        tok["in_uncached"] += u.get("input_tokens") or 0
        tok["cache_read"] += u.get("cache_read_input_tokens") or 0
        tok["cache_write"] += u.get("cache_creation_input_tokens") or 0
        tok["out"] += u.get("output_tokens") or 0
        if r["start"] is not None:
            inference += max(0.0, (r["end"] - r["start"]).total_seconds())
    ends = [r["end"] for r in msgs.values()]
    return dict(
        job=key[0],
        trial_name=key[1],
        source="session log",
        api_calls=len(msgs),
        **tok,
        inference_min=inference / 60,
        call_gap_min=(max(ends) - min(ends)).total_seconds() / 60,
    )


def from_atif(key: tuple[str, str], steps: list[Row]) -> Row | None:
    """One trial's metrics from its ATIF steps; agent steps without metrics made no model call."""
    calls = 0
    tok = dict(in_uncached=0, cache_read=0, cache_write=0, out=0)
    stamps: list[datetime] = []
    for s in steps:
        if s.get("source") != "agent" or not s.get("metrics"):
            continue
        mt = s["metrics"]
        ex = mt.get("extra") or {}
        cr = ex.get("cache_read_input_tokens") or mt.get("cached_tokens") or 0
        cw = ex.get("cache_creation_input_tokens") or 0
        calls += s.get("llm_call_count") or 1
        tok["cache_read"] += cr
        tok["cache_write"] += cw
        tok["in_uncached"] += max(0, (mt.get("prompt_tokens") or 0) - cr - cw)
        tok["out"] += mt.get("completion_tokens") or 0
        if t := ts(s.get("timestamp")):
            stamps.append(t)
    if calls == 0:
        return None
    return dict(
        job=key[0],
        trial_name=key[1],
        source="trajectory",
        api_calls=calls,
        **tok,
        inference_min=None,
        call_gap_min=(max(stamps) - min(stamps)).total_seconds() / 60 if stamps else None,
    )


def log(*a: object) -> None:
    print(*a, file=sys.stderr, flush=True)


def private_shards(list_files: Callable[[], list[str]]) -> list[str]:
    """The private archive's data shards, or none when this reader cannot see the archive."""
    from huggingface_hub.errors import RepositoryNotFoundError  # GatedRepoError is a subclass

    try:
        files = list_files()
    except RepositoryNotFoundError as e:
        log(f"{PRIVATE} is not readable with this token ({e}); the Muse jubarte rows stay empty")
        return []
    return [f for f in files if "/files-" in f]


def muse_rows(shards: Iterable[pl.DataFrame]) -> list[Row]:
    """Muse jubarte metrics, one row per trial, from (trial_name, text) session files in any shard."""
    texts: dict[str, list[str]] = {}
    for d in shards:
        for trial, text in d.select("trial_name", "text").iter_rows():
            if text:
                texts.setdefault(trial, []).append(text)
    rows = (from_session((MUSE_JOB, trial), t) for trial, t in texts.items())
    return [r for r in rows if r]


def metrics_frame(rows: list[Row]) -> pl.DataFrame:
    """One row per (job, trial_name). A trial read twice is a bug upstream, not a row to drop."""
    m = pl.DataFrame(rows)
    dup = m.filter(pl.struct("job", "trial_name").is_duplicated())
    if dup.height:
        names = sorted({f"{j}/{t}" for j, t in dup.select("job", "trial_name").iter_rows()})
        raise ValueError(f"trials read more than once: {', '.join(names)}")
    return m


def main() -> None:
    from huggingface_hub import HfApi

    c = pl.read_csv(CSV, infer_schema_length=10000)
    rows: list[Row | None] = []

    # 1. RedlineBench DeepSeek and Nemotron cohorts, both arms: public session logs
    for job in c.filter(~pl.col("cohort").str.contains("Harvey|Muse"))["job"].unique().to_list():
        d = (
            pl.scan_parquet(DS + "redlinebench/files-*.parquet")
            .filter((pl.col("job") == job) & pl.col("path_in_trial").str.contains(SESSION))
            .select("trial_name", "text")
            .collect()
        )
        for (trial,), g in d.group_by("trial_name"):
            rows.append(from_session((job, str(trial)), [t for t in g["text"] if t]))
        log("redlinebench", job, d["trial_name"].n_unique())

    # 2. Harvey 0.16: public session logs, keyed by trial name
    h = (
        pl.scan_parquet(DS + "harvey_lab/files-*.parquet")
        .filter(pl.col("path_in_trial").str.contains(SESSION))
        .select("trial_name", "text")
        .collect()
    )
    for (trial,), g in h.group_by("trial_name"):
        rows.append(from_session(("harvey-hub-ab", str(trial)), [t for t in g["text"] if t]))
    log("harvey 0.16", h["trial_name"].n_unique())

    # 3. Muse jubarte arm: session logs in the private local archive
    def shard(f: str) -> pl.DataFrame:
        lf = pl.scan_parquet(LA + f)
        if "path" not in lf.collect_schema().names():
            return pl.DataFrame(schema={"trial_name": pl.String, "text": pl.String})
        d = (
            lf.filter(pl.col("path").str.contains(f"/{MUSE_JOB}/") & pl.col("path_in_trial").str.contains(SESSION))
            .select("trial_name", "text")
            .collect()
        )
        if d.height:
            log("muse jubarte", f, d["trial_name"].n_unique())
        return d

    api = HfApi()
    files = private_shards(lambda: api.list_repo_files(PRIVATE, repo_type="dataset"))
    rows.extend(muse_rows(shard(f) for f in files))

    # 4. Muse control: only ATIF trajectories survive
    m = (
        pl.scan_parquet(JT)
        .filter(pl.col("job") == f"{MUSE_JOB}-ooriginal")
        .select("trial_name", "trajectory_json")
        .collect()
    )
    for trial, tj in m.iter_rows():
        if tj:
            st = json.loads(tj)
            steps = st if isinstance(st, list) else st.get("steps", [])
            rows.append(from_atif((f"{MUSE_JOB}-ooriginal", trial), steps))
    log("muse control", m.height)

    # 5. Harvey 0.17: ATIF steps
    tr = pl.read_parquet(DS + "harvey_lab_017/trials/part-00000.parquet").select("uuid", "trial")
    st17 = (
        pl.scan_parquet(DS + "harvey_lab_017/steps/part-*.parquet")
        .select("trial_uuid", "step_index", "step_json")
        .collect()
        .join(tr, left_on="trial_uuid", right_on="uuid")
        .sort("trial", "step_index")
    )
    for (trial,), g in st17.group_by("trial"):
        rows.append(from_atif(("harvey-0.17", str(trial)), [json.loads(x) for x in g["step_json"]]))
    log("harvey 0.17", st17["trial"].n_unique())

    out = c.join(metrics_frame([r for r in rows if r]), on=["job", "trial_name"], how="left")
    path = sys.argv[1] if len(sys.argv) > 1 else "data/trial_metrics.csv"
    out.write_csv(path)
    log(
        out.group_by("cohort", "arm")
        .agg(
            pl.len(),
            pl.col("api_calls").is_not_null().sum().alias("with_calls"),
            pl.col("inference_min").is_not_null().sum().alias("with_inf"),
        )
        .sort("cohort", "arm")
    )


if __name__ == "__main__":
    main()
