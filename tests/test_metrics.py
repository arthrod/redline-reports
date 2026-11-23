"""Tests for scripts/metrics.py.

Unit tests use a small frame with known answers. The regression tests pin the figures the report
publishes from data/trial_metrics.csv.
"""

from pathlib import Path

import metrics
import polars as pl
import pytest

ROW = {
    "cohort": "0.15.0 DeepSeek",
    "job": "j",
    "arm": "control",
    "model": "deepseek-v4.1-flash-1017",
    "score": 0.5,
    "minutes": 10.0,
    "inference_min": 5.0,
    "api_calls": 10,
    "in_uncached": 1_000_000,
    "cache_read": 1_000_000,
    "cache_write": 1_000_000,
    "out": 1_000_000,
    "source": "session log",
}


def frame(tmp_path: Path, rows: list[dict[str, object]]) -> pl.DataFrame:
    p = tmp_path / "m.csv"
    pl.DataFrame(rows).write_csv(p)
    return metrics.load(str(p))


def test_deepseek_cost_ignores_double_counted_cache_write(tmp_path: Path) -> None:
    d = frame(tmp_path, [ROW])
    # OpenRouter 0.15 + 0.003 + 0.60 per million each; cache write not billed; peak doubles
    assert d["cost_openrouter"][0] == pytest.approx(0.753)
    assert d["cost_openrouter_peak"][0] == pytest.approx(1.506)
    assert d["cost_opus"][0] == pytest.approx(4.0 + 0.20 + 20.0)


def test_other_models_use_their_own_rate_and_pay_cache_write_at_opus(tmp_path: Path) -> None:
    d = frame(tmp_path, [{**ROW, "model": "muse-spark-1.3-contributor"}])
    assert d["cost_openrouter"][0] == pytest.approx(0.10 + 0.002 + 0.20)
    assert d["cost_openrouter_peak"][0] == d["cost_openrouter"][0]
    assert d["cost_opus"][0] == pytest.approx(4.0 + 0.20 + 5.0 + 20.0)
    n = frame(tmp_path, [{**ROW, "model": "nemotron-3.5-lightning-30b-a3b"}])
    assert n["cost_openrouter"][0] == pytest.approx(0.07 + 0.04 + 0.20)


def test_unknown_model_has_no_openrouter_cost(tmp_path: Path) -> None:
    assert frame(tmp_path, [{**ROW, "model": "other"}])["cost_openrouter"][0] is None


def test_cell_formats_mean_and_median() -> None:
    assert metrics.cell(1234.6, 1000.0, 0) == "1,235 / 1,000"
    assert metrics.cell(None, 1.0, 1) == "n/a"


def test_aggregated_reports_mean_and_median_per_arm(tmp_path: Path) -> None:
    rows = [
        {**ROW, "score": 0.1},
        {**ROW, "score": 0.2},
        {**ROW, "score": 0.9},
        {**ROW, "arm": "jubarte", "score": 0.4},
    ]
    t = metrics.aggregated(frame(tmp_path, rows), [("score", "Score", 2)])
    assert t["Arm"].to_list() == ["benchmark's tools", "jubarte"]
    assert t["Trials"].to_list() == [3, 1]
    assert t["Score"].to_list() == ["0.40 / 0.20", "0.40 / 0.40"]


def test_per_run_splits_jobs_and_missing_fields_show_na(tmp_path: Path) -> None:
    rows = [{**ROW, "job": "a"}, {**ROW, "job": "b", "inference_min": None}]
    t = metrics.per_run(frame(tmp_path, rows), [("inference_min", "Inference minutes", 1)])
    assert t["Run"].to_list() == ["a", "b"]
    assert t["Inference minutes"].to_list() == ["5.0 / 5.0", "n/a"]


def test_coverage_counts_fields_present(tmp_path: Path) -> None:
    rows = [ROW, {**ROW, "api_calls": None, "inference_min": None, "source": None}]
    c = metrics.coverage(frame(tmp_path, rows))
    assert c.row(0, named=True)["With API calls"] == 1
    assert c.row(0, named=True)["Source"] == "session log"


def test_numeric_keeps_unformatted_values(tmp_path: Path) -> None:
    n = metrics.numeric(frame(tmp_path, [ROW, {**ROW, "score": 0.7}]), ["cohort"])
    assert n["score_mean"][0] == pytest.approx(0.6)
    assert n["score_median"][0] == pytest.approx(0.6)
    assert n["trials"][0] == 2


@pytest.fixture(scope="module")
def real() -> pl.DataFrame:
    return metrics.load()


@pytest.mark.parametrize(
    ("cohort", "arm", "label", "field", "digits", "expected"),
    [
        ("0.15.0 DeepSeek", "benchmark's tools", "API calls", "api_calls", 0, "70 / 66"),
        ("0.15.0 DeepSeek", "jubarte", "API calls", "api_calls", 0, "36 / 32"),
        ("0.15.0 DeepSeek", "jubarte", "Inference minutes", "inference_min", 1, "8.8 / 8.3"),
        ("0.15.0 DeepSeek", "jubarte", "Cost", "cost_openrouter_peak", 3, "0.063 / 0.060"),
        ("0.14.0 Nemotron", "jubarte", "Score", "score", 3, "0.307 / 0.179"),
        ("0.16 Harvey", "jubarte", "API calls", "api_calls", 0, "133 / 123"),
        ("0.17 Harvey", "benchmark's tools", "Output", "out", 0, "143,955 / 144,762"),
        ("Muse Spark 1.3", "benchmark's tools", "Minutes", "minutes", 1, "48.8 / 60.0"),
        ("Muse Spark 1.3", "jubarte", "Cost", "cost_opus", 2, "5.04 / 4.91"),
        ("0.15.0 DeepSeek", "jubarte", "Cost", "cost_openrouter", 3, "0.032 / 0.030"),
        ("0.14.0 Nemotron", "benchmark's tools", "Cost", "cost_openrouter", 3, "0.329 / 0.289"),
        ("Muse Spark 1.3", "benchmark's tools", "Cost", "cost_openrouter", 3, "0.076 / 0.078"),
    ],
)
def test_published_aggregates(
    real: pl.DataFrame, cohort: str, arm: str, label: str, field: str, digits: int, expected: str
) -> None:
    t = metrics.aggregated(real, [(field, label, digits)])
    row = t.filter((pl.col("Cohort") == cohort) & (pl.col("Arm") == arm))
    assert row[label].to_list() == [expected]


def test_trajectory_cohorts_have_no_inference_time(real: pl.DataFrame) -> None:
    t = metrics.aggregated(real, [("inference_min", "Inference minutes", 1)])
    na = t.filter(pl.col("Inference minutes") == "n/a")
    assert sorted(zip(na["Cohort"], na["Arm"], strict=True)) == [
        ("0.17 Harvey", "benchmark's tools"),
        ("0.17 Harvey", "jubarte"),
        ("Muse Spark 1.3", "benchmark's tools"),
    ]


def test_extracted_tokens_match_harbor_totals(real: pl.DataFrame) -> None:
    d = real.filter(pl.col("api_calls").is_not_null() & (pl.col("input_tokens") > 0))
    total_in = d["in_uncached"] + d["cache_read"] + d["cache_write"]
    n = d.height
    in_match = sum(abs(a - b) <= 1 for a, b in zip(total_in.to_list(), d["input_tokens"].to_list(), strict=True)) / n
    out_match = sum(abs(a - b) <= 1 for a, b in zip(d["out"].to_list(), d["output_tokens"].to_list(), strict=True)) / n
    assert in_match > 0.95
    assert out_match > 0.95


def test_main_writes_exports(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    src = Path(metrics.DATA).resolve()
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "trial_metrics.csv").write_bytes(src.read_bytes())
    monkeypatch.chdir(tmp_path)
    metrics.main()
    assert "## Per run: Tokens" in capsys.readouterr().out
    assert (tmp_path / "data" / "metrics_by_run.csv").exists()
