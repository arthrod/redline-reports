"""Recompute every table in harness/report.md.

    uv run python scripts/harness.py

Inputs:
- data/harness_requests.csv: the request parameters Claude Code sent, one row per arm and distinct
  parameter set, with the number of requests and trials that carried it.
- data/harness_responses.parquet: one row per model response, read from the Claude Code session
  logs (agent/sessions/projects/-app/*.jsonl) of every RedlineBench trial in the three
  DeepSeek and Nemotron cohorts and their two controls. Log lines that share a message id are one
  response. `thinking_chars`, `text_chars` and `tool_chars` count the characters in the thinking,
  text and tool-input blocks; `out`, `inp`, `cache_read`, `cache_write` and `thinking_tokens` are
  the usage numbers the provider returned; `sig_empty` counts thinking blocks with no signature.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import polars as pl
from cohorts import configure

ROOT = Path(__file__).resolve().parents[1]
REQUESTS = ROOT / "data" / "harness_requests.csv"
RESPONSES = ROOT / "data" / "harness_responses.parquet"
ORDER = ["0.14.0 DeepSeek", "0.15.0 DeepSeek", "DeepSeek control", "0.14.0 Nemotron", "Nemotron control"]
CAPPED = pl.col("stop") == "max_tokens"
THINKS = pl.col("n_thinking") > 0


def load() -> tuple[pl.DataFrame, pl.DataFrame]:
    r = pl.read_csv(REQUESTS)
    m = pl.read_parquet(RESPONSES).with_columns(
        (pl.col("text_chars") + pl.col("tool_chars")).alias("visible_chars"),
        pl.when(pl.col("arm").str.contains("DeepSeek"))
        .then(pl.lit("DeepSeek"))
        .otherwise(pl.lit("Nemotron"))
        .alias("family"),
    )
    return r, m


def ordered(df: pl.DataFrame) -> pl.DataFrame:
    return df.sort(pl.col("arm").replace_strict(ORDER, list(range(len(ORDER)))))


def requests(r: pl.DataFrame) -> pl.DataFrame:
    return ordered(r.select("arm", "model", "thinking", "effort", "max_tokens", "ctx", "requests", "trials"))


def thinking(m: pl.DataFrame) -> pl.DataFrame:
    return ordered(
        m.group_by("arm").agg(
            pl.len().alias("responses"),
            THINKS.mean().round(3).alias("with_thinking"),
            pl.col("thinking_chars").filter(THINKS).median().alias("median_chars_when_thinking"),
            pl.col("thinking_chars").filter(THINKS).quantile(0.9).alias("p90_chars"),
            pl.col("thinking_chars").max().alias("max_chars"),
            pl.col("n_thinking").sum().alias("thinking_blocks"),
            pl.col("sig_empty").sum().alias("unsigned_blocks"),
            pl.col("n_redacted").sum().alias("redacted_blocks"),
            pl.col("thinking_tokens").max().alias("max_reported_thinking_tokens"),
        )
    )


def length_bands(m: pl.DataFrame) -> pl.DataFrame:
    band = (
        pl.when(pl.col("thinking_chars") == 0)
        .then(pl.lit("1 none"))
        .when(pl.col("thinking_chars") <= 200)
        .then(pl.lit("2 1-200"))
        .when(pl.col("thinking_chars") <= 1000)
        .then(pl.lit("3 201-1,000"))
        .when(pl.col("thinking_chars") <= 5000)
        .then(pl.lit("4 1,001-5,000"))
        .when(pl.col("thinking_chars") <= 20000)
        .then(pl.lit("5 5,001-20,000"))
        .otherwise(pl.lit("6 over 20,000"))
    )
    return (
        m.with_columns(band.alias("thinking_chars"))
        .group_by("family", "thinking_chars")
        .len()
        .with_columns((pl.col("len") / pl.col("len").sum().over("family")).round(3).alias("share"))
        .sort("family", "thinking_chars")
    )


def by_position(m: pl.DataFrame) -> pl.DataFrame:
    pos = (
        pl.when(pl.col("turn") == 0)
        .then(pl.lit("1 first response"))
        .when(pl.col("turn") <= 5)
        .then(pl.lit("2 responses 2-6"))
        .when(pl.col("turn") <= 20)
        .then(pl.lit("3 responses 7-21"))
        .when(pl.col("turn") <= 50)
        .then(pl.lit("4 responses 22-51"))
        .otherwise(pl.lit("5 response 52 on"))
    )
    return ordered(
        m.with_columns(pos.alias("position"))
        .group_by("arm", "position")
        .agg(
            pl.len().alias("responses"),
            THINKS.mean().round(2).alias("with_thinking"),
            pl.col("thinking_chars").median().alias("median_chars"),
            pl.col("thinking_chars").quantile(0.9).alias("p90_chars"),
        )
        .sort("position")
    )


def trials(m: pl.DataFrame) -> pl.DataFrame:
    return m.group_by("arm", "trial").agg(
        pl.len().alias("responses"),
        pl.col("n_tool").sum().alias("tool_calls"),
        pl.col("thinking_chars").sum().alias("think"),
        pl.col("visible_chars").sum().alias("visible"),
        pl.col("out").sum().alias("out"),
        CAPPED.sum().alias("capped"),
        pl.col("out").filter(CAPPED).sum().alias("capped_out"),
        pl.col("inp").sum().alias("inp"),
        pl.col("cache_read").sum().alias("cache_read"),
    )


def per_trial(m: pl.DataFrame) -> pl.DataFrame:
    return ordered(
        trials(m)
        .group_by("arm")
        .agg(
            pl.len().alias("trials"),
            pl.col("responses").mean().round(1),
            pl.col("tool_calls").mean().round(1),
            (pl.col("think").mean() / 1e3).round(1).alias("thinking_kchars"),
            (pl.col("visible").mean() / 1e3).round(1).alias("visible_kchars"),
            (pl.col("think").sum() / (pl.col("think").sum() + pl.col("visible").sum()))
            .round(3)
            .alias("thinking_share"),
            pl.col("out").mean().round(0).alias("reported_output_tokens"),
        )
    )


def capped(m: pl.DataFrame) -> pl.DataFrame:
    per = (
        trials(m)
        .group_by("arm")
        .agg(
            (pl.col("capped") > 0).mean().round(3).alias("trials_with_one"),
            (pl.col("capped_out").sum() / pl.col("out").sum()).round(3).alias("share_of_reported_output"),
        )
    )
    return ordered(
        m.filter(CAPPED)
        .group_by("arm")
        .agg(
            pl.len().alias("capped_responses"),
            pl.col("out").min().alias("min_reported"),
            pl.col("out").max().alias("max_reported"),
            pl.col("thinking_chars").median().alias("median_thinking_chars"),
            pl.col("visible_chars").median().alias("median_visible_chars"),
            (pl.col("n_tool") > 0).mean().round(2).alias("share_with_a_tool_call"),
        )
        .join(per, on="arm")
    )


def largest_uncapped(m: pl.DataFrame) -> pl.DataFrame:
    return m.filter(~CAPPED).group_by("family").agg(pl.col("out").max().alias("largest_uncapped_output"))


def chars_per_token(m: pl.DataFrame) -> pl.DataFrame:
    x = m.filter(~THINKS & ~CAPPED & (pl.col("visible_chars") > 2000))
    return (
        x.group_by("family")
        .agg(
            pl.len().alias("responses"),
            (pl.col("visible_chars") / pl.col("out")).median().round(2).alias("chars_per_token"),
        )
        .sort("family")
    )


def token_fit(m: pl.DataFrame) -> pl.DataFrame:
    """Least squares: reported output tokens against thinking and visible characters."""
    rows = []
    for fam in ["DeepSeek", "Nemotron"]:
        y = m.filter((pl.col("family") == fam) & ~CAPPED & pl.col("out").is_not_null())
        a = y.select("thinking_chars", "visible_chars", "out").to_numpy().astype(float)
        coef, *_ = np.linalg.lstsq(np.c_[a[:, 0], a[:, 1], np.ones(len(a))], a[:, 2], rcond=None)
        rows.append(
            {
                "family": fam,
                "responses": len(a),
                "tokens_per_thinking_char": round(float(coef[0]), 4),
                "tokens_per_visible_char": round(float(coef[1]), 4),
                "intercept": round(float(coef[2])),
            }
        )
    return pl.DataFrame(rows)


def cache(m: pl.DataFrame) -> pl.DataFrame:
    return ordered(
        trials(m)
        .with_columns((pl.col("inp") + pl.col("cache_read")).alias("total"))
        .group_by("arm")
        .agg(
            (pl.col("total").mean() / 1e6).round(2).alias("input_M"),
            (pl.col("cache_read").mean() / 1e6).round(2).alias("cache_read_M"),
            (pl.col("inp").mean() / 1e3).round(0).alias("uncached_k"),
            (pl.col("cache_read").sum() / pl.col("total").sum()).round(3).alias("cached_share"),
        )
    )


# USD per million tokens: uncached input, cache read, output. DeepSeek V4.1 Flash 1017 on OpenRouter
# (fetched 2026-11-22) at its base rate and at its weekday peak (01:00-04:00, 06:00-10:00 UTC).
PRICES = {
    "DeepSeek on OpenRouter": (0.15, 0.003, 0.60),
    "DeepSeek on OpenRouter, weekday peak": (0.30, 0.006, 1.20),
    "Claude Opus 5.5 list": (4.0, 0.20, 20.0),
}


def double_counted(m: pl.DataFrame) -> pl.DataFrame:
    """How often the provider reported the same number as uncached input and as cache write."""
    return (
        m.group_by("family")
        .agg(
            pl.len().alias("responses"),
            (pl.col("inp") == pl.col("cache_write")).mean().round(5).alias("input_equals_cache_write"),
            (pl.col("cache_write") > 0).mean().round(3).alias("with_a_cache_write"),
        )
        .sort("family")
    )


def price(m: pl.DataFrame) -> pl.DataFrame:
    """DeepSeek arms' price per trial, uncached input counted once, cache-write surcharges left out."""
    t = (
        trials(m)
        .filter(~pl.col("arm").str.contains("Nemotron"))
        .group_by("arm")
        .agg(pl.col("inp").mean(), pl.col("cache_read").mean(), pl.col("out").mean())
    )
    rows = []
    for a, inp, cr, out in t.select("arm", "inp", "cache_read", "out").iter_rows():
        row: dict[str, object] = {"arm": a}
        for name, (p_in, p_cached, p_out) in PRICES.items():
            row[name] = round((inp * p_in + cr * p_cached + out * p_out) / 1e6, 3)
        rows.append(row)
    return ordered(pl.DataFrame(rows))


def main() -> None:
    configure()
    pl.Config.set_fmt_str_lengths(120)
    r, m = load()
    sections = [
        ("1. What Claude Code asked for", requests(r)),
        ("2. How often the model thought, and how much (per response)", thinking(m)),
        ("3. Responses by thinking length, in characters", length_bands(m)),
        ("4. Thinking by position in the trial", by_position(m)),
        ("5. Per trial: where the output went", per_trial(m)),
        ("6. Responses that stopped at the output limit", capped(m)),
        ("6b. Largest reported output on a response that did not stop at the limit", largest_uncapped(m)),
        ("7. Characters per reported output token (no thinking, over 2,000 visible characters)", chars_per_token(m)),
        ("7b. Reported output tokens fitted on characters", token_fit(m)),
        ("8. Input per trial: cached and uncached", cache(m)),
        ("8b. Uncached input reported again as cache write", double_counted(m)),
        ("9. DeepSeek price per trial from the logs", price(m)),
    ]
    for title, df in sections:
        print(f"## {title}")
        print(df)
        print()


if __name__ == "__main__":
    main()
