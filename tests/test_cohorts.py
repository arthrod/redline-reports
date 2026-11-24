"""Tests for scripts/cohorts.py.

The unit tests use small inputs with known answers. The regression tests pin the figures the
reports publish, so a change to data/cohort_trials.csv or to the pairing shows up as a failing test.
"""

import cohorts
import numpy as np
import polars as pl
import pytest


@pytest.fixture(scope="module")
def data() -> pl.DataFrame:
    return cohorts.load()


def test_boot_is_seeded_and_brackets_the_mean() -> None:
    d = np.random.default_rng(1).normal(0.02, 0.05, 50)
    lo, hi = cohorts.boot(d)
    assert (lo, hi) == cohorts.boot(d)
    assert lo <= d.mean() <= hi


def test_boot_constant_difference_has_zero_width() -> None:
    assert cohorts.boot(np.full(10, 0.1)) == pytest.approx((0.1, 0.1))


def test_boot_rejects_empty_input() -> None:
    with pytest.raises(ValueError):
        cohorts.boot(np.array([]))


def test_pair_averages_repeats_within_a_task() -> None:
    def rows(arm: str, scores: list[tuple[str, float | None]]) -> pl.DataFrame:
        return pl.DataFrame(
            {
                "pair_key": [k for k, _ in scores],
                "score": [s for _, s in scores],
                "minutes": [1.0] * len(scores),
                "input_tokens": [1] * len(scores),
                "output_tokens": [1] * len(scores),
                "cache_read_tokens": [0] * len(scores),
            }
        )

    j = rows("jubarte", [("a", 0.4), ("a", 0.6), ("b", None), ("b", 0.2)])
    k = rows("control", [("a", 0.3), ("b", 0.1), ("c", 0.9)])
    p = cohorts.pair(j, k).sort("pair_key")
    assert p["pair_key"].to_list() == ["a", "b"]
    assert p["s"].to_list() == pytest.approx([0.5, 0.2])
    assert p["s_c"].to_list() == pytest.approx([0.3, 0.1])


def test_pct() -> None:
    assert cohorts.pct(18.3, 10.3) == "-44%"


def test_every_cohort_uses_one_judge_per_arm(data: pl.DataFrame) -> None:
    graded = data.filter(pl.col("score").is_not_null())
    judges = graded.group_by("cohort").agg(pl.col("judge").unique())
    for cohort, js in judges.iter_rows():
        assert len(js) == 1, (cohort, js)


PAIRED = {
    "0.14.0 DeepSeek": (130, 0.503, 0.497, "-0.007", "57/56/17"),
    "0.14.0 Nemotron": (12, 0.401, 0.308, "-0.093", "4/7/1"),
    "0.15.0 DeepSeek": (125, 0.503, 0.501, "-0.003", "31/39/55"),
    "0.16 Harvey": (90, 0.936, 0.941, "+0.006", "33/24/33"),
    "0.17 Harvey": (16, 0.925, 0.923, "-0.002", "8/8/0"),
    "Muse Spark 1.3": (140, 0.297, 0.316, "+0.019", "57/60/23"),
}


def test_paired_table_matches_the_report(data: pl.DataFrame) -> None:
    p = {r["cohort"]: r for r in cohorts.paired(data).iter_rows(named=True)}
    for cohort, (tasks, control, jubarte, change, wlt) in PAIRED.items():
        r = p[cohort]
        assert (r["tasks"], r["control"], r["jubarte"], r["change"], r["won_lost_tied"]) == (
            tasks,
            control,
            jubarte,
            change,
            wlt,
        ), cohort


def test_rounding_noise_counts_as_tied() -> None:
    # Task means built from different numbers of trials can differ by ~1e-17 when the scores are
    # equal. Those tasks are ties, not wins or losses.
    third = 1 / 3
    rows = [
        {"cohort": "0.15.0 DeepSeek", "arm": "control", "pair_key": "a", "score": 0.1 + 0.2, "minutes": 1.0},
        {"cohort": "0.15.0 DeepSeek", "arm": "jubarte", "pair_key": "a", "score": 0.3, "minutes": 1.0},
        {"cohort": "0.15.0 DeepSeek", "arm": "control", "pair_key": "b", "score": third, "minutes": 1.0},
        {"cohort": "0.15.0 DeepSeek", "arm": "jubarte", "pair_key": "b", "score": 0.5, "minutes": 1.0},
        {"cohort": "0.15.0 DeepSeek", "arm": "control", "pair_key": "c", "score": 0.5, "minutes": 1.0},
        {"cohort": "0.15.0 DeepSeek", "arm": "jubarte", "pair_key": "c", "score": third, "minutes": 1.0},
    ]
    d = pl.DataFrame(rows).with_columns(
        pl.lit(1.0).alias("input_tokens"),
        pl.lit(1.0).alias("output_tokens"),
        pl.lit(1.0).alias("cache_read_tokens"),
    )
    assert (0.1 + 0.2) - 0.3 != 0  # the noise this test is about
    assert cohorts.won_lost_tied(cohorts.pair_frame(d, "0.15.0 DeepSeek")) == "1/1/1"


def test_only_nemotron_interval_excludes_zero(data: pl.DataFrame) -> None:
    for r in cohorts.paired(data).iter_rows(named=True):
        lo, hi = (float(x) for x in r["ci95"].split(" to "))
        if r["cohort"] == "0.14.0 Nemotron":
            assert hi < 0, r["cohort"]
        else:
            assert lo <= 0 <= hi, r["cohort"]


def test_main_prints_every_section(capsys: pytest.CaptureFixture[str]) -> None:
    cohorts.main()
    out = capsys.readouterr().out
    for title, _ in cohorts.SECTIONS:
        assert f"## {title}" in out


def test_report_outcome_table_matches_status(data: pl.DataFrame) -> None:
    """Section 5's outcome rows in the report are status(), cell for cell."""
    rows = {
        "Graded": "1 graded",
        "Finished, not graded": "2 finished, not graded",
        "Agent failed, not graded": "3 agent failed, not graded",
        "Never started": "4 never started",
    }
    report = (cohorts.ROOT / "reports" / "jubarte-six-cohorts.md").read_text().splitlines()
    header = next(line for line in report if line.startswith("| | 0.14.0 DeepSeek"))
    names = [c.strip() for c in header.strip("|").split("|")][1:]
    s = {r["status"]: r for r in cohorts.status(data).iter_rows(named=True)}
    for line in report:
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells[0] in rows:
            got = {n: int(c.split()[0]) for n, c in zip(names, cells[1:], strict=True)}
            assert got == {n: s[rows[cells[0]]][n] for n in names}, cells[0]


def test_never_started_trials_are_not_a_task(data: pl.DataFrame) -> None:
    """0.17 Harvey ran 16 tasks, three per arm; the four trials per arm that never started carry
    no task id, and a null must not count as a 17th task."""
    h = data.filter((pl.col("cohort") == "0.17 Harvey") & pl.col("task").is_null())
    assert h.height == 8
    o = {r["cohort"]: r for r in cohorts.overview(data).iter_rows(named=True)}
    assert o["0.17 Harvey"]["tasks"] == 16
    j = cohorts.jobs(data).filter(pl.col("cohort") == "0.17 Harvey")
    assert j["tasks"].to_list() == [16]


def test_report_states_the_harvey_017_task_count(data: pl.DataFrame) -> None:
    o = {r["cohort"]: r for r in cohorts.overview(data).iter_rows(named=True)}
    report = (cohorts.ROOT / "reports" / "jubarte-six-cohorts.md").read_text()
    assert f"48 trials over {o['0.17 Harvey']['tasks']} tasks" in report
    assert "17 tasks" not in report
