"""Regression tests for scripts/harness.py: the facts harness/report.md rests on."""

import polars as pl
import pytest

import harness


@pytest.fixture(scope="module")
def frames() -> tuple[pl.DataFrame, pl.DataFrame]:
    return harness.load()


def test_every_request_asked_for_adaptive_thinking(frames: tuple[pl.DataFrame, pl.DataFrame]) -> None:
    r, _ = frames
    assert r["thinking"].unique().to_list() == ['{"display": "updates", "type": "adaptive"}']
    assert r["effort"].unique().to_list() == ["high"]
    assert r["max_tokens"].unique().to_list() == [16384]


def test_deepseek_stops_at_6897_and_nemotron_at_16384(frames: tuple[pl.DataFrame, pl.DataFrame]) -> None:
    _, m = frames
    c = {r["arm"]: (r["min_reported"], r["max_reported"]) for r in harness.capped(m).iter_rows(named=True)}
    assert set(c) == set(harness.ORDER)
    for a, v in c.items():
        assert v == ((6897, 6897) if "DeepSeek" in a else (16384, 16384)), a
    big = dict(harness.largest_uncapped(m).iter_rows())
    assert big["DeepSeek"] < 6897


def test_thinking_tokens_always_zero_and_deepseek_unsigned(frames: tuple[pl.DataFrame, pl.DataFrame]) -> None:
    _, m = frames
    for r in harness.thinking(m).iter_rows(named=True):
        assert r["max_reported_thinking_tokens"] == 0
        assert r["redacted_blocks"] == 0
        signed = r["thinking_blocks"] - r["unsigned_blocks"]
        assert signed == (0 if "DeepSeek" in r["arm"] else r["thinking_blocks"]), r["arm"]


def test_deepseek_reports_uncached_input_as_cache_write(frames: tuple[pl.DataFrame, pl.DataFrame]) -> None:
    _, m = frames
    d = dict(harness.double_counted(m).select("family", "input_equals_cache_write").iter_rows())
    assert d["DeepSeek"] > 0.9999
    assert d["Nemotron"] == 0


def test_main_prints_every_section(capsys: pytest.CaptureFixture[str]) -> None:
    harness.main()
    out = capsys.readouterr().out
    assert out.count("\n## ") + out.startswith("## ") == 12
