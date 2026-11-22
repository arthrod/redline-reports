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
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

SEED = 20261122
DRAWS = 10_000


def summarize(control: np.ndarray, jubarte: np.ndarray) -> dict[str, float | int]:
    diff = jubarte - control
    rng = np.random.default_rng(SEED)
    boot = diff[rng.integers(0, len(diff), (DRAWS, len(diff)))].mean(axis=1)
    return {
        "tasks": len(diff),
        "control": round(float(control.mean()), 3),
        "jubarte": round(float(jubarte.mean()), 3),
        "diff": round(float(diff.mean()), 3),
        "lo": round(float(np.percentile(boot, 2.5)), 3),
        "hi": round(float(np.percentile(boot, 97.5)), 3),
        "wins": int((diff > 0).sum()),
        "losses": int((diff < 0).sum()),
        "ties": int((diff == 0).sum()),
    }


def main(path: Path) -> None:
    rows: dict[str, list[tuple[float, float]]] = defaultdict(list)
    with path.open(newline="") as fh:
        for r in csv.DictReader(fh):
            rows[r["arm"]].append((float(r["control"]), float(r["jubarte"])))
    for arm, pairs in rows.items():
        a = np.array(pairs)
        s = summarize(a[:, 0], a[:, 1])
        print(f"{arm}: {s['tasks']} tasks, {s['control']} vs {s['jubarte']}, "
              f"{s['diff']:+.3f} ({s['lo']:+.3f} to {s['hi']:+.3f}), "
              f"W/L/T {s['wins']}/{s['losses']}/{s['ties']}")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent / "data" / "task_pairs.csv")
