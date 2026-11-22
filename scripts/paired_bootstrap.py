#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy"]
# ///
"""Recompute the paired score differences and 95% intervals in the reports.

Reads data/task_pairs.csv (one row per arm and task: the GLM-5.3-Flash score with the
benchmark's scripts and with jubarte, each the mean of that task's graded trials) and
prints, per arm: tasks, means, difference, a task-level bootstrap interval (10,000
draws, seed 20261122), and wins, losses and ties.

The interval bounds are Monte Carlo estimates. Across 200 seeds on this file they
move by up to about 0.003 (more for the 14-task arm), so a bound printed here can
differ from the reports' figure in the third decimal. No sign changes: study-v13's
upper bound stays below zero on every seed, and every other interval spans zero.
"""

import csv
from collections import defaultdict
from pathlib import Path

import numpy as np

SEED = 20261122
DRAWS = 10_000
DATA = Path(__file__).resolve().parent.parent / "data" / "task_pairs.csv"

type Pairs = tuple[np.ndarray, np.ndarray]
type Summary = dict[str, float | int]


def load(path: Path) -> dict[str, Pairs]:
    """Read the pairs file into {arm: (control scores, jubarte scores)}, in file order."""
    rows: dict[str, list[tuple[float, float]]] = defaultdict(list)
    with path.open(newline="") as fh:
        for r in csv.DictReader(fh):
            rows[r["arm"]].append((float(r["control"]), float(r["jubarte"])))
    return {arm: (np.array([c for c, _ in v]), np.array([j for _, j in v])) for arm, v in rows.items()}


def _r(x: float) -> float:
    """Round to 3 decimals; floating-point noise around zero prints as +0.000, a real -0.0004 as -0.000."""
    return 0.0 if abs(x) < 1e-12 else round(x, 3)


def summarize(control: np.ndarray, jubarte: np.ndarray) -> Summary:
    """Means, paired difference, task-level bootstrap interval and win/loss/tie counts."""
    if control.shape != jubarte.shape or control.size == 0:
        raise ValueError("control and jubarte must be non-empty arrays of the same length")
    diff = jubarte - control
    rng = np.random.default_rng(SEED)
    boot = diff[rng.integers(0, len(diff), (DRAWS, len(diff)))].mean(axis=1)
    return {
        "tasks": len(diff),
        "control": _r(float(control.mean())),
        "jubarte": _r(float(jubarte.mean())),
        "diff": _r(float(diff.mean())),
        "lo": _r(float(np.percentile(boot, 2.5))),
        "hi": _r(float(np.percentile(boot, 97.5))),
        "wins": int((diff > 0).sum()),
        "losses": int((diff < 0).sum()),
        "ties": int((diff == 0).sum()),
    }


def format_line(arm: str, s: Summary) -> str:
    return (
        f"{arm}: {s['tasks']} tasks, {s['control']:.3f} vs {s['jubarte']:.3f}, "
        f"{s['diff']:+.3f} ({s['lo']:+.3f} to {s['hi']:+.3f}), "
        f"W/L/T {s['wins']}/{s['losses']}/{s['ties']}"
    )


def main(path: Path) -> None:
    for arm, (control, jubarte) in load(path).items():
        print(format_line(arm, summarize(control, jubarte)))


if __name__ == "__main__":
    main(DATA)
