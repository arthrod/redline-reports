"""Tests for scripts/paired_bootstrap.py.

Unit tests use small fixtures with known answers; the regression tests pin the
figures the reports publish, so a change to data/task_pairs.csv or to the
bootstrap shows up as a failing test instead of a silent drift.
"""

import csv
import runpy
from pathlib import Path

import numpy as np
import paired_bootstrap as pb
import pytest

REPO = Path(__file__).resolve().parent.parent


def write_pairs(path: Path, rows: list[tuple[str, str, float, float]]) -> Path:
    with path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["arm", "task", "dev_task", "control", "jubarte"])
        for arm, task, control, jubarte in rows:
            w.writerow([arm, task, "false", control, jubarte])
    return path


def test_summarize_counts_wins_losses_and_ties() -> None:
    control = np.array([0.5, 0.5, 0.5, 0.2])
    jubarte = np.array([0.7, 0.3, 0.5, 0.4])
    s = pb.summarize(control, jubarte)
    assert s["tasks"] == 4
    assert (s["wins"], s["losses"], s["ties"]) == (2, 1, 1)
    assert s["control"] == pytest.approx(0.425)
    assert s["jubarte"] == pytest.approx(0.475)
    assert s["diff"] == pytest.approx(0.05)


def test_summarize_interval_brackets_the_mean_and_is_seeded() -> None:
    rng = np.random.default_rng(1)
    control = rng.uniform(0, 1, 50)
    jubarte = control + rng.normal(0.02, 0.05, 50)
    first = pb.summarize(control, jubarte)
    second = pb.summarize(control, jubarte)
    assert first == second
    assert first["lo"] <= first["diff"] <= first["hi"]


def test_summarize_constant_difference_gives_a_zero_width_interval() -> None:
    control = np.full(10, 0.4)
    s = pb.summarize(control, control + 0.1)
    assert s["lo"] == s["hi"] == pytest.approx(0.1)
    assert s["wins"] == 10


def test_summarize_rejects_mismatched_or_empty_input() -> None:
    with pytest.raises(ValueError):
        pb.summarize(np.array([0.1, 0.2]), np.array([0.1]))
    with pytest.raises(ValueError):
        pb.summarize(np.array([]), np.array([]))


def test_main_prints_one_line_per_arm(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = write_pairs(
        tmp_path / "pairs.csv",
        [("a", "t1", 0.5, 0.7), ("a", "t2", 0.5, 0.3), ("b", "t1", 0.2, 0.2)],
    )
    pb.main(path)
    lines = capsys.readouterr().out.splitlines()
    assert lines[0].startswith("a: 2 tasks, 0.500 vs 0.500, +0.000")
    assert lines[0].endswith("W/L/T 1/1/0")
    assert lines[1].startswith("b: 1 tasks, 0.200 vs 0.200, +0.000 (+0.000 to +0.000)")


@pytest.mark.parametrize(
    ("arm", "tasks", "diff", "wlt"),
    [
        ("ds-v12-heldout", 120, 0.002, (45, 37, 38)),
        ("ds-v9-heldout", 120, -0.024, (43, 47, 30)),
        ("study-v14-heldout", 106, -0.002, (31, 32, 43)),
        ("study-v13", 27, -0.090, (4, 13, 10)),
        ("ds-v12-all", 130, 0.004, (50, 39, 41)),
        ("ds-v9-all", 130, -0.018, (49, 49, 32)),
        ("study-v14-all", 116, 0.000, (34, 34, 48)),
        ("study-v14b-015", 125, -0.003, (31, 39, 55)),
        ("study-v15", 9, -0.061, (1, 7, 1)),
    ],
)
def test_published_figures_match_the_data(arm: str, tasks: int, diff: float, wlt: tuple[int, int, int]) -> None:
    rows = pb.load(pb.DATA)
    s = pb.summarize(*rows[arm])
    assert s["tasks"] == tasks
    assert s["diff"] == pytest.approx(diff, abs=1e-9)
    assert (s["wins"], s["losses"], s["ties"]) == wlt


PUBLISHED_BOUNDS = [
    ("ds-v12-heldout", -0.029, 0.032),
    ("ds-v9-heldout", -0.058, 0.008),
    ("study-v14-heldout", -0.028, 0.025),
    ("study-v13", -0.149, -0.035),
    ("ds-v12-all", -0.025, 0.032),
    ("ds-v9-all", -0.050, 0.012),
    ("study-v14-all", -0.025, 0.026),
    ("study-v14b-015", -0.028, 0.023),
]


@pytest.mark.parametrize(("arm", "lo", "hi"), PUBLISHED_BOUNDS)
def test_published_interval_bounds_match_the_data(arm: str, lo: float, hi: float) -> None:
    s = pb.summarize(*pb.load(pb.DATA)[arm])
    assert s["lo"] == pytest.approx(lo, abs=1e-9)
    assert s["hi"] == pytest.approx(hi, abs=1e-9)


@pytest.mark.parametrize("arm", [arm for arm, _, _ in PUBLISHED_BOUNDS])
def test_bootstrap_bounds_agree_with_a_normal_approximation(arm: str) -> None:
    # Independent check of the interval level: for a mean of 27 to 130 paired
    # differences, a 95% percentile bootstrap sits within a few thousandths of
    # mean +/- 1.96 standard errors. A 90% interval would miss by 0.004 or more.
    control, jubarte = pb.load(pb.DATA)[arm]
    s = pb.summarize(control, jubarte)
    d = jubarte - control
    se = float(d.std()) / np.sqrt(d.size)
    assert s["lo"] == pytest.approx(float(d.mean()) - 1.96 * se, abs=0.0035)
    assert s["hi"] == pytest.approx(float(d.mean()) + 1.96 * se, abs=0.0035)


def test_study_v13_interval_excludes_zero_and_held_out_v12_spans_it() -> None:
    rows = pb.load(pb.DATA)
    assert pb.summarize(*rows["study-v13"])["hi"] < 0
    s = pb.summarize(*rows["ds-v12-heldout"])
    assert s["lo"] < 0 < s["hi"]


def test_script_runs_as_main(capsys: pytest.CaptureFixture[str]) -> None:
    runpy.run_path(str(REPO / "scripts" / "paired_bootstrap.py"), run_name="__main__")
    assert "ds-v12-heldout: 120 tasks" in capsys.readouterr().out


NO_FULL_B_CONTROL = {
    "redline-s1-t1-g01a", "redline-s1-t1-g01b", "redline-s1-t1-g01c", "redline-s1-t1-g01d", "redline-s1-t1-g01e",
    "redline-s1-t2-g01a", "redline-s1-t2-g01b", "redline-s1-t2-g01c", "redline-s1-t2-g02b",
}


def test_no_arm_pairs_a_task_the_deepseek_full_b_control_never_ran() -> None:
    with pb.DATA.open(newline="") as fh:
        tasks = {r["task"] for r in csv.DictReader(fh)}
    assert tasks.isdisjoint(NO_FULL_B_CONTROL)
    assert "redline-s1-t4-g11a" not in tasks  # graded only by the panel
