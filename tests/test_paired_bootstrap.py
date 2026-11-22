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
        ("ds-v12-heldout", 127, 0.004, (48, 40, 39)),
        ("ds-v9-heldout", 127, -0.024, (45, 51, 31)),
        ("study-v14-heldout", 113, 0.002, (35, 35, 43)),
        ("study-v13", 33, -0.068, (7, 16, 10)),
        ("ds-v12-all", 139, 0.008, (55, 42, 42)),
        ("study-v14b-015", 134, -0.000, (35, 44, 55)),
    ],
)
def test_published_figures_match_the_data(arm: str, tasks: int, diff: float, wlt: tuple[int, int, int]) -> None:
    rows = pb.load(pb.DATA)
    s = pb.summarize(*rows[arm])
    assert s["tasks"] == tasks
    assert s["diff"] == pytest.approx(diff, abs=1e-9)
    assert (s["wins"], s["losses"], s["ties"]) == wlt


def test_study_v13_interval_excludes_zero_and_held_out_v12_spans_it() -> None:
    rows = pb.load(pb.DATA)
    assert pb.summarize(*rows["study-v13"])["hi"] < 0
    s = pb.summarize(*rows["ds-v12-heldout"])
    assert s["lo"] < 0 < s["hi"]


def test_script_runs_as_main(capsys: pytest.CaptureFixture[str]) -> None:
    runpy.run_path(str(REPO / "scripts" / "paired_bootstrap.py"), run_name="__main__")
    assert "ds-v12-heldout: 127 tasks" in capsys.readouterr().out
