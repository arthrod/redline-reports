"""Recompute every score, time and token table in reports/jubarte-six-cohorts.md.

    uv run python scripts/cohorts.py

Input: data/cohort_trials.csv, one row per trial in the six cohorts and their controls.

Pairing: per task (per A/B pair for the 0.16 Harvey cohort), the mean score of every graded
jubarte trial against the mean of every graded control trial on the same task. The interval
is a bootstrap over tasks: 10,000 draws, seed 20261122. Each cohort is graded by one judge in
both arms (see the `judge` column). A task is tied when the two means differ by less than
1e-12, so floating-point noise is not counted as a win or a loss.

Token columns are Harbor's `agent_result` totals. For the DeepSeek provider these count uncached
input twice (once as input, once as cache write); scripts/harness.py prices from the session logs
instead.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt
import polars as pl

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "cohort_trials.csv"
ORDER = ["0.14.0 DeepSeek", "0.14.0 Nemotron", "0.15.0 DeepSeek", "0.16 Harvey", "0.17 Harvey", "Muse Spark 1.3"]
REDLINEBENCH_ROUNDS = ["0.14.0 DeepSeek", "0.15.0 DeepSeek", "Muse Spark 1.3"]
SEED = 20261122
# Task means averaged from different numbers of trials can differ by ~1e-17 when equal.
TIE = 1e-12


def configure() -> None:
    pl.Config.set_tbl_formatting("MARKDOWN")
    pl.Config.set_tbl_hide_dataframe_shape(True)
    pl.Config.set_tbl_hide_column_data_types(True)
    pl.Config.set_tbl_rows(100)
    pl.Config.set_tbl_cols(30)
    pl.Config.set_tbl_width_chars(400)


def num(x: Any) -> float:
    return float(x)


def load(path: Path = DATA) -> pl.DataFrame:
    return pl.read_csv(path, infer_schema_length=10000)


def boot(d: npt.NDArray[np.float64], n: int = 10_000, seed: int = SEED) -> tuple[float, float]:
    """95% percentile interval of the mean of d, resampling its elements."""
    if len(d) == 0:
        raise ValueError("no paired tasks")
    rng = np.random.default_rng(seed)
    means = d[rng.integers(0, len(d), size=(n, len(d)))].mean(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def per_task(x: pl.DataFrame) -> pl.DataFrame:
    return (
        x.filter(pl.col("score").is_not_null())
        .group_by("pair_key")
        .agg(
            pl.col("score").mean().alias("s"),
            pl.col("minutes").mean().alias("m"),
            pl.col("input_tokens").mean().alias("i"),
            pl.col("output_tokens").mean().alias("o"),
            pl.col("cache_read_tokens").mean().alias("c"),
        )
    )


def pair(jubarte: pl.DataFrame, control: pl.DataFrame) -> pl.DataFrame:
    # sorted, so the seeded bootstrap draws the same tasks on every run
    return per_task(jubarte).join(per_task(control), on="pair_key", suffix="_c").sort("pair_key")


def arm(d: pl.DataFrame, cohort: str, name: str) -> pl.DataFrame:
    return d.filter((pl.col("cohort") == cohort) & (pl.col("arm") == name))


def pair_frame(d: pl.DataFrame, cohort: str) -> pl.DataFrame:
    """One cohort's paired tasks: jubarte against its control."""
    return pair(arm(d, cohort, "jubarte"), arm(d, cohort, "control"))


def won_lost_tied(p: pl.DataFrame) -> str:
    """Tasks where jubarte scored higher / lower / the same, ignoring floating-point noise."""
    dd = (p["s"] - p["s_c"]).to_numpy()
    won, lost = int((dd > TIE).sum()), int((dd < -TIE).sum())
    return f"{won}/{lost}/{len(dd) - won - lost}"


def pct(a: float, b: float) -> str:
    return f"{(b - a) / a * 100:+.0f}%"


def diff_row(p: pl.DataFrame) -> dict[str, Any]:
    d = (p["s"] - p["s_c"]).to_numpy()
    lo, hi = boot(d)
    return {
        "tasks": p.height,
        "control": round(num(p["s_c"].mean()), 3),
        "jubarte": round(num(p["s"].mean()), 3),
        "change": f"{d.mean():+.3f}",
        "ci95": f"{lo:+.3f} to {hi:+.3f}",
    }


def overview(d: pl.DataFrame) -> pl.DataFrame:
    rows = []
    for c in ORDER:
        j = arm(d, c, "jubarte")
        g = j.filter(pl.col("score").is_not_null())["score"]
        rows.append(
            {
                "cohort": c,
                "trials": j.height,
                "graded": g.len(),
                "tasks": j["task"].n_unique(),
                "jobs": j["job"].n_unique(),
                "mean": round(num(g.mean()), 3),
                "median": round(num(g.median()), 3),
                "middle_half": f"{num(g.quantile(0.25)):.2f}-{num(g.quantile(0.75)):.2f}",
                "scored_zero": int((g == 0).sum()),
                "median_minutes": round(num(j["minutes"].median()), 1),
                "median_input_M": round(num(j["input_tokens"].median()) / 1e6, 2),
                "median_output_k": round(num(j["output_tokens"].median()) / 1e3, 1),
            }
        )
    return pl.DataFrame(rows)


def paired(d: pl.DataFrame) -> pl.DataFrame:
    rows = []
    for c in ORDER:
        p = pair_frame(d, c)
        mc, mj = num(p["m_c"].mean()), num(p["m"].mean())
        oc, oj = num(p["o_c"].mean()), num(p["o"].mean())
        ic, ij = num(p["i_c"].mean()), num(p["i"].mean())
        rows.append(
            {
                "cohort": c,
                **diff_row(p),
                "won_lost_tied": won_lost_tied(p),
                "minutes": f"{mc:.1f} -> {mj:.1f} ({pct(mc, mj)})",
                "output": f"{oc / 1e3:.1f}k -> {oj / 1e3:.1f}k ({pct(oc, oj)})",
                "input": f"{ic / 1e6:.2f}M -> {ij / 1e6:.2f}M ({pct(ic, ij)})",
            }
        )
    return pl.DataFrame(rows)


def status(d: pl.DataFrame) -> pl.DataFrame:
    j = d.filter(pl.col("arm") == "jubarte").with_columns(
        pl.when(pl.col("score").is_not_null())
        .then(pl.lit("1 graded"))
        .when(pl.col("complete").str.contains("never started"))
        .then(pl.lit("4 never started"))
        .when(pl.col("failure") != "none")
        .then(pl.lit("3 agent failed, not graded"))
        .otherwise(pl.lit("2 finished, not graded"))
        .alias("status")
    )
    return wide(j, "status")


def failures(d: pl.DataFrame) -> pl.DataFrame:
    return wide(d.filter(pl.col("arm") == "jubarte"), "failure")


def bands(d: pl.DataFrame) -> pl.DataFrame:
    band = (
        pl.when(pl.col("score").is_null())
        .then(pl.lit("5 no grade"))
        .when(pl.col("score") == 0)
        .then(pl.lit("1 zero"))
        .when(pl.col("score") <= 0.33)
        .then(pl.lit("2 above 0 to 0.33"))
        .when(pl.col("score") <= 0.66)
        .then(pl.lit("3 0.34 to 0.66"))
        .otherwise(pl.lit("4 0.67 to 1"))
    )
    return wide(d.filter(pl.col("arm") == "jubarte").with_columns(band.alias("band")), "band")


def wide(j: pl.DataFrame, col: str) -> pl.DataFrame:
    present = set(j["cohort"].unique().to_list())
    return (
        j.group_by("cohort", col)
        .len()
        .pivot(on="cohort", index=col, values="len")
        .fill_null(0)
        .select([col] + [c for c in ORDER if c in present])
        .sort(col)
    )


def jobs(d: pl.DataFrame) -> pl.DataFrame:
    return (
        d.filter(pl.col("arm") == "jubarte")
        .group_by("cohort", "job")
        .agg(
            pl.len().alias("trials"),
            pl.col("task").n_unique().alias("tasks"),
            pl.col("score").mean().round(3).alias("mean"),
            pl.col("minutes").median().round(1).alias("median_minutes"),
        )
        .sort("cohort", "job")
    )


def inside(d: pl.DataFrame) -> pl.DataFrame:
    """Each job of 30+ tasks, and the 12 tuning tasks against the rest, against the cohort's control."""
    rows = []
    for c in ORDER:
        j = arm(d, c, "jubarte")
        k = arm(d, c, "control")
        groups = [
            (job, j.filter(pl.col("job") == job))
            for job in j["job"].unique().sort().to_list()
            if j.filter(pl.col("job") == job)["task"].n_unique() >= 30
        ]
        drafts = j.group_by("job").agg(pl.col("task").n_unique().alias("n")).filter(pl.col("n") == 12)["job"]
        if c != "0.14.0 Nemotron" and drafts.len():
            tune = j.filter(pl.col("job").is_in(drafts.implode()))["task"].unique()
            groups += [
                ("all jobs, the 12 tuning tasks", j.filter(pl.col("task").is_in(tune.implode()))),
                ("all jobs, every other task", j.filter(~pl.col("task").is_in(tune.implode()))),
            ]
        for name, x in groups:
            p = pair(x, k)
            if p.height < 5:
                continue
            rows.append(
                {
                    "cohort": c,
                    "jubarte_runs": name,
                    "trials": x.height,
                    **diff_row(p),
                    "minutes": f"{num(p['m_c'].mean()):.1f} -> {num(p['m'].mean()):.1f}",
                }
            )
    return pl.DataFrame(rows)


def rounds(d: pl.DataFrame) -> pl.DataFrame:
    """RedlineBench cohorts split by negotiation round (the -tN- in the task id)."""
    rows = []
    for c in REDLINEBENCH_ROUNDS:
        x = d.filter(pl.col("cohort") == c).with_columns(pl.col("task").str.extract(r"-t(\d)-").alias("round"))
        for r in sorted(x["round"].drop_nulls().unique().to_list()):
            y = x.filter(pl.col("round") == r)
            p = pair(y.filter(pl.col("arm") == "jubarte"), y.filter(pl.col("arm") == "control"))
            rows.append(
                {
                    "cohort": c,
                    "round": r,
                    **diff_row(p),
                    "minutes": f"{num(p['m_c'].mean()):.1f} -> {num(p['m'].mean()):.1f}",
                }
            )
    return pl.DataFrame(rows)


SECTIONS = [
    ("Overview (jubarte arm of each cohort)", overview),
    ("Paired against the control, same tasks", paired),
    ("Status of every jubarte trial", status),
    ("Recorded failure", failures),
    ("Score bands", bands),
    ("Jobs inside each cohort", jobs),
    ("Inside the cohorts: each job of 30+ tasks, and the tuning tasks, against the cohort's control", inside),
    ("RedlineBench cohorts by negotiation round", rounds),
]


def main() -> None:
    configure()
    d = load()
    for title, fn in SECTIONS:
        print(f"## {title}")
        print(fn(d))
        print()


if __name__ == "__main__":
    main()
