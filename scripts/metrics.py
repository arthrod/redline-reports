"""Mean and median per trial, by cohort and by run, for both arms.

Reads data/trial_metrics.csv (one row per trial: data/cohort_trials.csv plus API calls,
token usage and inference time from the session logs or trajectories). Every cell is
"mean / median" over the trials that have the field.

Run: uv run python scripts/metrics.py
"""

import polars as pl
from cohorts import configure

DATA = "data/trial_metrics.csv"

# USD per million tokens: uncached input, cache read, cache write, output.
# OpenRouter's public model list (openrouter.ai/api/v1/models), fetched 2026-11-22. OpenRouter lists
# no cache-write price for these models. DeepSeek V4.1 Flash 1017 doubles every rate on weekdays
# 01:00-04:00 and 06:00-10:00 UTC; the other two models have one rate.
OPENROUTER = {
    "deepseek": (0.15, 0.003, 0.0, 0.60),  # deepseek/deepseek-v4.1-flash-1017
    "nemotron": (0.07, 0.04, 0.0, 0.20),  # nvidia/nemotron-3.5-lightning (30B-A3B)
    "muse": (0.10, 0.002, 0.0, 0.20),  # meta/muse-spark-1.3-contributor
}
DEEPSEEK_PEAK = 2.0
OPUS = (4.0, 0.20, 5.0, 20.0)  # Claude Opus 5.5 list, hypothetical

COHORTS = ["0.14.0 DeepSeek", "0.14.0 Nemotron", "0.15.0 DeepSeek", "0.16 Harvey", "0.17 Harvey", "Muse Spark 1.3"]

TABLES: dict[str, list[tuple[str, str, int]]] = {
    "Score, time and API calls": [
        ("score", "Score", 3),
        ("minutes", "Agent working minutes", 1),
        ("inference_min", "Inference minutes", 1),
        ("api_calls", "API calls", 0),
    ],
    "Tokens": [
        ("in_uncached", "Input, uncached", 0),
        ("cache_read", "Input, cache read", 0),
        ("cache_write", "Cache write (as reported)", 0),
        ("out", "Output", 0),
    ],
    "Estimated cost per trial (USD)": [
        ("cost_openrouter", "OpenRouter, agent model", 3),
        ("cost_openrouter_peak", "OpenRouter, DeepSeek weekday peak", 3),
        ("cost_opus", "Claude Opus 5.5 list (hypothetical)", 2),
    ],
}


# Section 6 headline: same basis as the score table in section 1.
PAIRED_FIELDS: list[tuple[str, str, int]] = [
    ("api_calls", "API calls", 0),
    ("minutes", "Agent minutes", 1),
    ("inference_min", "Inference minutes", 1),
    ("in_uncached", "Input, uncached", 0),
    ("cache_read", "Input, cache read", 0),
    ("out", "Output tokens", 0),
    ("cost_openrouter", "Est. cost, OpenRouter", 3),
    ("cost_opus", "Est. cost, Opus 5.5 list", 2),
]


def load(path: str = DATA) -> pl.DataFrame:
    """Trial rows with the cost estimates added.

    DeepSeek's provider reports every uncached input token again as a cache write, so cache
    writes are never billed for DeepSeek models. The peak column doubles DeepSeek's rates and
    equals the base column for the other models.
    """
    d = pl.read_csv(path, infer_schema_length=10000)
    model = pl.col("model").str.to_lowercase().fill_null("")
    ds = model.str.contains("deepseek")
    write = pl.when(ds).then(0).otherwise(pl.col("cache_write"))

    def price(p: tuple[float, float, float, float], cw: pl.Expr) -> pl.Expr:
        return (pl.col("in_uncached") * p[0] + pl.col("cache_read") * p[1] + cw * p[2] + pl.col("out") * p[3]) / 1e6

    base = pl.lit(None, dtype=pl.Float64)
    for key, p in OPENROUTER.items():
        base = pl.when(model.str.contains(key)).then(price(p, write)).otherwise(base)
    return d.with_columns(base.alias("cost_openrouter")).with_columns(
        pl.when(ds)
        .then(pl.col("cost_openrouter") * DEEPSEEK_PEAK)
        .otherwise(pl.col("cost_openrouter"))
        .alias("cost_openrouter_peak"),
        price(OPUS, write).alias("cost_opus"),
    )


def cell(mean: float | None, median: float | None, digits: int) -> str:
    """Format a mean / median pair."""
    if mean is None or median is None:
        return "n/a"

    def f(v: float) -> str:
        return f"{v:,.{digits}f}"

    return f"{f(mean)} / {f(median)}"


def summary(d: pl.DataFrame, by: list[str], fields: list[tuple[str, str, int]]) -> pl.DataFrame:
    """One row per group and arm: trial count, model, then mean / median for each field."""
    agg = [pl.len().alias("Trials"), pl.col("model").drop_nulls().mode().first().alias("Model")]
    for col, _, _ in fields:
        agg += [pl.col(col).mean().alias(f"{col}_mean"), pl.col(col).median().alias(f"{col}_median")]
    g = d.group_by([*by, "arm"]).agg(agg)
    order = {c: i for i, c in enumerate(COHORTS)}
    g = g.with_columns(
        pl.col("cohort").replace_strict(order, default=99).alias("_o"),
        (pl.col("arm") == "jubarte").alias("_a"),
    ).sort(["_o", "_a", *by[1:]])
    out = g.select(
        *by,
        pl.col("arm").replace({"control": "benchmark's tools"}).alias("Arm"),
        "Model",
        "Trials",
    )
    return out.with_columns(
        *[
            pl.Series(
                label,
                [cell(m, md, digits) for m, md in zip(g[f"{col}_mean"], g[f"{col}_median"], strict=True)],
            )
            for col, label, digits in fields
        ]
    )


def aggregated(d: pl.DataFrame, fields: list[tuple[str, str, int]]) -> pl.DataFrame:
    """Per cohort and arm."""
    return summary(d, ["cohort"], fields).rename({"cohort": "Cohort"})


def per_run(d: pl.DataFrame, fields: list[tuple[str, str, int]]) -> pl.DataFrame:
    """Per cohort, job and arm. Control jobs repeat under each cohort that uses them."""
    return summary(d, ["cohort", "job"], fields).rename({"cohort": "Cohort", "job": "Run"})


def coverage(d: pl.DataFrame) -> pl.DataFrame:
    """Where each cohort's calls and tokens come from, and how many trials have them."""
    return (
        d.group_by("cohort", "arm")
        .agg(
            pl.len().alias("Trials"),
            pl.col("source").drop_nulls().mode().first().alias("Source"),
            pl.col("api_calls").is_not_null().sum().alias("With API calls"),
            pl.col("inference_min").is_not_null().sum().alias("With inference time"),
            pl.col("score").is_not_null().sum().alias("Graded"),
        )
        .with_columns(pl.col("cohort").replace_strict({c: i for i, c in enumerate(COHORTS)}, default=99).alias("_o"))
        .sort("_o", "arm")
        .drop("_o")
        .rename({"cohort": "Cohort", "arm": "Arm"})
    )


def paired_means(d: pl.DataFrame) -> pl.DataFrame:
    """Per cohort and arm: each task's mean over its graded trials, averaged over the paired tasks.

    The same tasks as the score table (section 1): a task counts when both arms have a graded
    trial. Means per trial over all trials compare different task sets when the arms cover
    different tasks (the Nemotron control ran 140 tasks, its jubarte arm 12).
    """
    cols = [c for c, _, _ in PAIRED_FIELDS]
    tasks = (
        d.filter(pl.col("score").is_not_null())
        .group_by("cohort", "arm", "pair_key")
        .agg([pl.col(c).mean() for c in cols])
    )
    both = tasks.group_by("cohort", "pair_key").agg(pl.col("arm").n_unique().alias("arms")).filter(pl.col("arms") == 2)
    return (
        tasks.join(both.select("cohort", "pair_key"), on=["cohort", "pair_key"])
        .group_by("cohort", "arm")
        .agg(pl.len().alias("tasks"), *[pl.col(c).mean() for c in cols])
        .sort("cohort", "arm")
    )


def paired_table(d: pl.DataFrame) -> pl.DataFrame:
    """paired_means as one row per cohort, each cell "benchmark's tools -> jubarte"."""
    m = paired_means(d)
    rows = []
    for c in COHORTS:
        r = {
            a: m.filter((pl.col("cohort") == c) & (pl.col("arm") == a)).row(0, named=True)
            for a in ("control", "jubarte")
        }
        row: dict[str, str] = {"Cohort": c, "Tasks": str(r["control"]["tasks"])}
        for col, label, digits in PAIRED_FIELDS:
            row[label] = " -> ".join(
                "n/a" if r[a][col] is None else f"{r[a][col]:,.{digits}f}" for a in ("control", "jubarte")
            )
        rows.append(row)
    return pl.DataFrame(rows)


def numeric(d: pl.DataFrame, by: list[str]) -> pl.DataFrame:
    """Unformatted mean and median of every field, for data/ exports."""
    cols = [c for fields in TABLES.values() for c, _, _ in fields]
    agg = [pl.len().alias("trials"), pl.col("model").drop_nulls().mode().first().alias("model")]
    for c in cols:
        agg += [pl.col(c).mean().alias(f"{c}_mean"), pl.col(c).median().alias(f"{c}_median")]
    return d.group_by([*by, "arm"]).agg(agg).sort([*by, "arm"])


def main() -> None:
    configure()
    pl.Config.set_fmt_str_lengths(80)
    d = load()
    numeric(d, ["cohort"]).write_csv("data/metrics_by_cohort.csv")
    numeric(d, ["cohort", "job"]).write_csv("data/metrics_by_run.csv")
    paired_means(d).write_csv("data/metrics_paired_by_cohort.csv")
    print("## Paired by task, as in section 1 (section 6 headline)\n")
    print(paired_table(d))
    print()
    print("## Coverage\n")
    print(coverage(d))
    for title, fields in TABLES.items():
        print(f"\n## Aggregated by cohort: {title}\n")
        print(aggregated(d, fields))
    for title, fields in TABLES.items():
        print(f"\n## Per run: {title}\n")
        print(per_run(d, fields))


if __name__ == "__main__":
    main()
