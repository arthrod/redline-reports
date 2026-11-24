"""Pin the judge-repeatability figures to data/judge_regrades.csv.

FACTS.md, DATA-AUDIT.md, the 0.14 report, the harness report and the Monday and
Thursday posts quote these numbers. The CSV lists every RedlineBench trial with two
GLM-5.3-Flash grade.json files under the same path in the public trajectories: the
original grading and the 30 October regrade.
"""

import csv
import statistics
from pathlib import Path

import pytest

DATA = Path(__file__).resolve().parent.parent / "data" / "judge_regrades.csv"
REGRADE_ARCHIVE = "colab_bench-2026-10-30-regrade"


def load() -> list[dict[str, str]]:
    with DATA.open(newline="") as fh:
        return list(csv.DictReader(fh))


def gaps(rows: list[dict[str, str]]) -> list[float]:
    return [abs(float(r["regrade"]) - float(r["first_grade"])) for r in rows]


def test_one_row_per_regraded_trial() -> None:
    rows = load()
    assert len(rows) == 47
    assert len({(r["job"], r["trial_name"]) for r in rows}) == 47


def test_every_second_grade_comes_from_the_regrade_archive() -> None:
    rows = load()
    assert {r["regrade_archive"] for r in rows} == {REGRADE_ARCHIVE}
    assert REGRADE_ARCHIVE not in {r["first_archive"] for r in rows}


def test_gap_column_matches_the_two_grades() -> None:
    for r, g in zip(load(), gaps(load()), strict=True):
        # The CSV stores six decimals, so the gap may differ from the rounded grades by one unit.
        assert float(r["abs_gap"]) == pytest.approx(g, abs=2e-6)


def test_published_figures_across_all_47() -> None:
    g = gaps(load())
    assert round(statistics.mean(g), 3) == 0.108
    assert round(statistics.median(g), 3) == 0.062
    assert max(g) == pytest.approx(0.5, abs=1e-9)
    # Two grades per trial: the sample standard deviation is |a - b| / sqrt(2).
    assert round(statistics.mean(x / 2**0.5 for x in g), 3) == 0.077


def test_published_figures_for_the_35_that_changed() -> None:
    changed = [x for x in gaps(load()) if x > 0]
    assert len(changed) == 35
    assert round(statistics.mean(changed), 3) == 0.146
    assert round(statistics.median(changed), 3) == 0.097


def test_regrades_inside_the_paired_comparisons() -> None:
    inside = [r for r in load() if r["in_paired_comparison"] == "true"]
    assert len(inside) == 17
    assert {r["job"] for r in inside} == {
        "deepseek-full-b",
        "jubarte-ds-v9-rest",
        "jubarte-ds-v12",
        "jubarte-ds-v12-rest",
    }
