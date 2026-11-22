# Redline reports

[![ci](https://github.com/arthrod/redline-reports/actions/workflows/ci.yml/badge.svg)](https://github.com/arthrod/redline-reports/actions/workflows/ci.yml)
[![data: CC-BY-4.0](https://img.shields.io/badge/data-CC--BY--4.0-blue)](https://huggingface.co/datasets/arthrod/redline-bench-jubarte-six-cohorts)

What happened when AI agents redlined contracts with [jubarte](https://github.com/jandira-tech/jubarte) instead of the tools two legal benchmarks ship with: Crosby's RedlineBench and the redline tasks in Harvey's Legal Agent Benchmark (LAB). The repository covers six cohorts of runs: jubarte 0.14.0 with DeepSeek and with Nemotron, 0.15.0 with DeepSeek, 0.16 and 0.17 on Harvey LAB, and Muse Spark 1.3.

The short version:

- **No score gain was detected in any cohort.** Five cohorts show no difference, with intervals that include zero. The sixth, Nemotron 30B, scored lower with jubarte: −0.093 (−0.170 to −0.018).
- **Less work in five of six.** With DeepSeek on RedlineBench, agent time fell 44% to 45% and output 51% to 54%. On Harvey's tasks the saving was 6% to 14%, and with Muse 20% to 26%. On Nemotron, jubarte saved no tokens.
- **The harness has quirks.** Claude Code sends Claude's thinking settings to every model. DeepSeek's reported output never exceeded 6,897 tokens, and the provider's usage numbers undercount output and double-count uncached input.

| | |
|---|---|
| [`reports/jubarte-six-cohorts.md`](reports/jubarte-six-cohorts.md) | The six cohorts: design, paired results, results by job and by negotiation round, failures, time, tokens and price |
| [`harness/report.md`](harness/report.md) | What Claude Code asks of models that are not Claude: adaptive thinking, the 6,897-token ceiling, usage numbers that do not add up, unsigned thinking, and how a tool cut thinking |
| [`lawyers/`](lawyers) | Five short posts for lawyers who follow the technology, Monday to Friday |
| [`FACTS.md`](FACTS.md) | Every number used above, with its source, and where the claims stop |
| [`DATA-AUDIT.md`](DATA-AUDIT.md) | Where each cohort's trials are stored, and what the public tables get wrong |
| [`artifacts/`](artifacts) | Four single-file pages that run jubarte in the browser |
| [`data/`](data) | `cohort_trials.csv` (one row per trial), `trial_metrics.csv` (the same trials plus API calls, inference time and split tokens), `metrics_by_cohort.csv` and `metrics_by_run.csv` (report Appendix A), `harness_responses.parquet` (one row per model response), `harness_requests.csv` |

## Install and reproduce

Requires [uv](https://docs.astral.sh/uv/).

```sh
git clone https://github.com/arthrod/redline-reports && cd redline-reports
uv sync --locked
uv run python scripts/cohorts.py   # every table in the report
uv run python scripts/harness.py   # every table in the harness article
uv run python scripts/metrics.py   # report Appendix A: every metric, mean and median, by cohort and by run
uv run --with huggingface_hub python tools/extract_trial_metrics.py   # rebuilds data/trial_metrics.csv
```

## Development

```sh
uv run ruff check && uv run ruff format --check
uv run mypy
uv run pytest     # fails under 90% coverage; pins the published figures
```

CI runs the same steps on every pull request.

## The artifacts

| File | What it does |
|---|---|
| `is-it-really-a-redline.html` | Drop a Word file and see whether its markup is real tracked changes or only formatting |
| `word-to-pdf.html` | Word to PDF, with tracked changes and comments printed as Word prints them |
| `redline-two-drafts.html` | Compare two drafts into a Word file with real tracked changes |
| `jubarte-desk.html` | Review changes one by one, compare, scrub names, validate, and print to PDF |

The last three fetch the jubarte 0.19.0 WebAssembly build from cdn.jsdelivr.net. Documents stay in the browser tab.

## Data

Every trial in the six cohorts, and nothing else, is public at <https://huggingface.co/datasets/arthrod/redline-bench-jubarte-six-cohorts>: one row per trial in `data/trials.parquet`, and every file of every trial (session logs, deliverables, grades) under `files/`.

## Licence

- Reports and data: CC-BY-4.0.
- jubarte: Apache-2.0 from 0.19.0.
- The benchmarks belong to their authors. RedlineBench is MIT (code) and CC-BY-4.0 (data); Harvey's LAB is MIT.
