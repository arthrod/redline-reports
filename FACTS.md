# Every number in this repository, with its source

Scope: the six cohorts in `reports/jubarte-six-cohorts.md` and nothing else. Every figure in the report, the harness article and the five posts is on this page.

Two scripts produce every figure:

- `uv run python scripts/cohorts.py` reads `data/cohort_trials.csv`.
- `uv run python scripts/harness.py` reads `data/harness_responses.parquet` and `data/harness_requests.csv`.

`uv run pytest` pins the headline figures, so a change to the data fails a test instead of drifting silently.

## The cohorts

| Cohort | Agent | Benchmark | jubarte build | Judge, both arms | jubarte trials | Control |
|---|---|---|---|---|---:|---|
| 0.14.0 DeepSeek | DeepSeek-V4.1-Flash-1017, Claude Code 2.1.310 | RedlineBench | 0.14.0 (`f4c352db…`) | GLM-5.3-Flash | 560 (17 jobs) | `deepseek-full-b`, 131 trials |
| 0.14.0 Nemotron | Nemotron 3.5 Lightning 30B-A3B, Claude Code, one RTX 5090 | RedlineBench, 12 tasks | 0.14.0 | GLM-5.3-Flash | 144 (11 jobs) | `nemotron-full-5090`, 160 trials |
| 0.15.0 DeepSeek | DeepSeek-V4.1-Flash-1017, Claude Code | RedlineBench | 0.15.0 (`469c7ff4…`) | GLM-5.3-Flash | 147 (2 jobs) | `deepseek-full-b` |
| 0.16 Harvey | DeepSeek-V4.1-Flash, Claude Code, Harbor Hub | Harvey LAB redline tasks | 0.16.x | LAB judge: gpt-5.4 (106 trials), then gpt-6-luna (74) | 90 | 90, paired A/B |
| 0.17 Harvey | DeepSeek Flash 1017, Claude Code, self-hosted MI355X | Harvey LAB editing tasks, 16 | 0.17.x | LAB judge, gpt-6-luna | 48 | 48 |
| Muse Spark 1.3 | Muse Spark 1.3 Contributor | RedlineBench | not recorded | gpt-6.1-sol panel | 140 | 158 |

The control always uses the benchmark's own tooling: RedlineBench's Python docx scripts and contract-redliner skill, or Harvey LAB's docx skill.

## Paired results (report, section 1)

| Cohort | Tasks | Control | jubarte | Change (95% CI) | Better/worse/equal | Minutes | Output | Input |
|---|---:|---:|---:|---|---|---|---|---|
| 0.14.0 DeepSeek | 130 | 0.503 | 0.497 | −0.007 (−0.030 to +0.016) | 57/56/17 | 18.3 → 10.3 | 44.2k → 21.5k | 2.54M → 1.39M |
| 0.14.0 Nemotron | 12 | 0.401 | 0.308 | −0.093 (−0.170 to −0.018) | 4/7/1 | 30.8 → 24.1 | 64.4k → 67.4k | 4.05M → 4.80M |
| 0.15.0 DeepSeek | 125 | 0.503 | 0.501 | −0.003 (−0.028 to +0.024) | 36/43/46 | 18.4 → 10.1 | 44.4k → 20.2k | 2.57M → 1.24M |
| 0.16 Harvey | 90 | 0.936 | 0.941 | +0.006 (−0.004 to +0.017) | 33/24/33 | 37.2 → 32.4 | 53.3k → 46.5k | 10.45M → 8.95M |
| 0.17 Harvey | 16 | 0.925 | 0.923 | −0.002 (−0.026 to +0.022) | 8/8/0 | 28.4 → 26.6 | 143.5k → 133.1k | 17.20M → 16.16M |
| Muse Spark 1.3 | 140 | 0.297 | 0.316 | +0.019 (−0.033 to +0.071) | 57/60/23 | 48.8 → 36.1 | 226.3k → 180.7k | 3.98M → 2.93M |

Method:

- A task's score is the mean of its graded trials.
- The interval is a bootstrap over tasks: 10,000 draws, seed 20261122, with tasks sorted so the draw is reproducible.
- Input tokens are Harbor's totals, which count DeepSeek's uncached input twice (see "Prices" below).

## Inside the 0.14.0 DeepSeek cohort (report, section 3)

- The 12 tuning tasks (10 with a control grade): +0.030 (−0.017 to +0.080).
- Every other task (120): −0.010 (−0.034 to +0.014).
- `ds-v12-rest`: +0.002 (−0.029 to +0.032).
- `ds-v9-rest`: −0.025 (−0.060 to +0.008).
- `study-v14-rest`: +0.015 (−0.013 to +0.044).
- `study-v14`: −0.050 (−0.106 to +0.000).
- `study-v13`: −0.090 (−0.150 to −0.035), the only DeepSeek job whose interval excludes zero.
- Draft means on the tuning tasks run from 0.510 (`ds-v3`) to 0.576 (`ds-v9`).
- Minutes fell 37% to 57% in every job.

## Inside the Nemotron cohort

- Control on the 12 tasks: 0.401.
- Job means: v1 0.059, v2 0.349, v3 0.351, v4 0.308, v5 0.272, v6 0.331, v7 0.255, v8 0.303, v9 0.425, v10 0.368, v11 0.360.
- Only v9 is above the control.

## By negotiation round (report, section 4)

| Round | 0.14.0 DeepSeek | 0.15.0 DeepSeek | Muse Spark 1.3 |
|---|---|---|---|
| 1 | −0.060 (−0.127 to +0.017) | −0.092 (−0.179 to +0.017) | −0.001 (−0.059 to +0.058) |
| 2 | +0.017 (−0.024 to +0.058) | +0.040 (+0.001 to +0.082) | +0.017 (−0.090 to +0.128) |
| 3 | +0.014 (−0.018 to +0.048) | +0.006 (−0.035 to +0.053) | +0.077 (−0.004 to +0.156) |
| 4 | −0.038 (−0.083 to +0.007) | −0.035 (−0.085 to +0.016) | −0.031 (−0.135 to +0.070) |

## Outcomes of the jubarte trials (report, section 5)

| | 0.14.0 DeepSeek | Nemotron | 0.15.0 DeepSeek | 0.16 Harvey | 0.17 Harvey | Muse |
|---|---:|---:|---:|---:|---:|---:|
| Graded | 546 | 131 | 134 | 90 | 44 | 140 |
| Not graded | 14 | 13 | 13 | 0 | 4 | 0 |
| Timeouts, still graded | 0 | 12 | 0 | 1 | 0 | 33 |
| Zeros | 22 | 43 | 6 | 0 | 0 | 41 (29 are timeouts) |
| Median score | 0.487 | 0.179 | 0.514 | 0.962 | 0.948 | 0.315 |

Control timeouts:

- DeepSeek: 1 in 131.
- Nemotron: 25 in 160.
- Muse: 78 in 158.

## Harness (harness article)

- **Responses.** 63,274 from 63,380 requests. Every request sent adaptive thinking with display `updates`, effort `high`, `max_tokens` 16,384, and `clear_thinking_20251015` with `keep: all`.
- **How often the model thought.** DeepSeek: 83.8% (0.14.0), 86.5% (0.15.0) and 82.4% (control) of responses. Nemotron: 100%.
- **How long, when it thought** (median / 90th percentile, characters):
  - 0.14.0 jubarte: 698 / 15,367.
  - 0.15.0 jubarte: 746 / 16,020.
  - DeepSeek control: 1,788 / 17,842.
  - Nemotron: 356 jubarte and 275 control.
- **Per trial, DeepSeek** (responses / thinking characters):
  - Control: 69.8 / 366.8k.
  - 0.14.0: 39.5 / 180.2k.
  - 0.15.0: 35.8 / 173.9k.
  - Thinking share: 86% to 89%.
- **Stops at the output limit.** DeepSeek: 358 responses, all at exactly 6,897 reported tokens (largest otherwise 6,892). Nemotron: 66, all at 16,384. Median thinking about 70.8k characters, no visible text. About a third of DeepSeek trials hit the limit at least once.
- **Token accounting:**
  - `thinking_tokens` is 0 on every response.
  - DeepSeek runs 9.92 characters per reported output token (fitted about 10 to 11); Nemotron runs about 4.
  - DeepSeek reports `cache_creation_input_tokens` equal to `input_tokens` on 36,192 of 36,193 responses.
- **Signatures.** All 32,208 DeepSeek thinking blocks are unsigned; all 27,081 Nemotron blocks are signed.

## Prices (report, section 6)

Per trial, from the logs, uncached input counted once, cache-write surcharges excluded:

| | Uncached input | Cached input | DeepSeek on OpenRouter | Weekday peak | Opus 5.5 list |
|---|---:|---:|---:|---:|---:|
| DeepSeek control | 114k | 2.32M | $0.051 | $0.102 | $1.81 |
| 0.14.0 DeepSeek | 107k | 1.21M | $0.033 | $0.066 | $1.11 |
| 0.15.0 DeepSeek | 108k | 1.05M | $0.032 | $0.063 | $1.05 |

Prices per million tokens, from OpenRouter's public model list (`openrouter.ai/api/v1/models`), fetched 2026-11-22:

- DeepSeek V4.1 Flash 1017 (`deepseek/deepseek-v4.1-flash-1017`): $0.15 in, $0.003 cached, $0.60 out. Doubled ($0.30, $0.006, $1.20) on weekdays 01:00–04:00 and 06:00–10:00 UTC.
- Nemotron 3.5 Lightning 30B-A3B (`nvidia/nemotron-3.5-lightning`): $0.07 in, $0.04 cached, $0.20 out.
- Muse Spark 1.3 Contributor (`meta/muse-spark-1.3-contributor`): $0.10 in, $0.002 cached, $0.20 out.
- Claude Opus 5.5 list: $4, $0.20 cached, $5 cache write, $20 out. Hypothetical: no Claude model was the agent.

What was actually paid: a flat Synthetic subscription for the DeepSeek cohorts, local GPUs for Nemotron, a rented MI355X node for 0.17 Harvey.

## Every metric, both arms (report, section 6 and Appendix A)

Per trial, means, benchmark's tools → jubarte. Medians and per-run figures are in Appendix A and `data/metrics_by_cohort.csv` / `data/metrics_by_run.csv`, pinned by `tests/test_metrics.py`.

| Cohort | API calls | Agent min | Inference min | Output tokens | OpenRouter $ | Opus list $ |
|---|---:|---:|---:|---:|---:|---:|
| 0.14.0 DeepSeek | 70 → 39 | 18.5 → 10.7 | 17.4 → 9.4 | 44.5k → 21.8k | 0.051 → 0.033 | 1.81 → 1.11 |
| 0.14.0 Nemotron | 101 → 99 | 30.6 → 24.1 | 28.8 → 20.6 | 72.3k → 65.7k | 0.329 → 0.341 | 19.41 → 20.07 |
| 0.15.0 DeepSeek | 70 → 36 | 18.5 → 10.0 | 17.4 → 8.8 | 44.5k → 20.4k | 0.051 → 0.032 | 1.81 → 1.05 |
| 0.16 Harvey | 158 → 133 | 37.2 → 32.4 | 34.0 → 28.1 | 53.3k → 46.5k | 0.132 → 0.120 | 4.87 → 4.35 |
| 0.17 Harvey | 168 → 163 | 28.5 → 26.9 | n/a | 144.0k → 134.7k | 2.68 → 2.55 | 71.95 → 68.39 |
| Muse Spark 1.3 | 47 → 34 | 48.8 → 36.1 | n/a → 35.0 | 226.3k → 181.0k | 0.076 → 0.064 | 6.22 → 5.04 |

- Inference is 86% to 97% of agent working time wherever session logs exist.
- The non-inference remainder per trial grew with jubarte: DeepSeek 1.1 → 1.3 (0.14.0) / 1.4 (0.15.0) minutes, Nemotron 2.0 → 3.5, 0.16 Harvey 3.2 → 4.4.
- Median seconds per call: DeepSeek 13.9 → 14.6 (0.14.0) / 15.1 (0.15.0); Nemotron 16.0 → 11.2; 0.16 Harvey 12.8 → 12.9; Muse (jubarte arm) 56.6.
- Nemotron and 0.17 Harvey reported no prompt caching, so their cost estimates are inflated. OpenRouter $ is the base rate; DeepSeek's weekday peak doubles it.

## Run dates (UTC)

- DeepSeek control: Oct 27 22:05 to Oct 28 05:13.
- 0.14.0 DeepSeek: Oct 28 05:14 to Oct 30 15:46.
- 0.15.0 DeepSeek: Oct 30 21:21 to Oct 31 02:05.
- Nemotron control: Oct 26 02:59 to 12:32. Nemotron jubarte: Oct 26 12:33 to Oct 27 00:10.
- 0.16 Harvey: Nov 1 to 4.
- 0.17 Harvey: Nov 4 23:33 to Nov 5 02:56.
- Muse: jubarte arm Oct 16 21:02 to Oct 17 02:50, before its control (Oct 17 to 18).

## Where the claims stop

- No cohort shows a score gain whose interval excludes zero. Nemotron shows a loss.
- No equivalence margin was tested: "no difference detected" is not "equal".
- The arms were never interleaved. A provider-side change between them cannot be ruled out.
- Scores do not compare across cohorts, because the judges differ.
- No Claude or other frontier model was the agent.
- Muse's jubarte build is unrecorded, and its jubarte arm ran first.

## Sources

- Task definitions: <https://huggingface.co/datasets/arthrod/redline-bench-jubarte-tasks>.
- Trials, all six cohorts and nothing else: <https://huggingface.co/datasets/arthrod/redline-bench-jubarte-six-cohorts>.
- RedlineBench: Crosby Legal and micro1, <https://huggingface.co/datasets/crosbylegal/RedlineBench>.
- Harvey LAB: <https://github.com/harveyai/harvey-labs>.
