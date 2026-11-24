# Which datasets the reports and posts use

This file has one section per report:

1. [The six-cohort report](#1-the-six-cohort-report): `reports/jubarte-six-cohorts.md` and `harness/report.md`.
2. [The 0.14 report and the whole archive](#2-the-014-report-and-the-whole-archive): `reports/jubarte-0.14-redlinebench.md`, `FACTS.md`, the posts and the lawyer drafts.

## 1. The six-cohort report

Date: 2026-11-22. Scope: the six cohorts in `reports/jubarte-six-cohorts.md` and the harness article.

| Dataset | Visibility | What was read | Feeds |
|---|---|---|---|
| [`redline-bench-jubarte-six-cohorts`](https://huggingface.co/datasets/arthrod/redline-bench-jubarte-six-cohorts) | public | everything below, cut to the six cohorts | the published copy of every trial |
| `redline-bench-deepseek-trajectories`, `redlinebench/` | public | `result.json`, `config.json`, `grade.json` and the Claude Code session logs of the jobs listed in `DATA-AUDIT.md` | the 0.14.0 DeepSeek, 0.14.0 Nemotron and 0.15.0 DeepSeek cohorts; the harness article |
| `redline-bench-deepseek-trajectories`, `harvey_lab/` | public | per-trial reward, judge and token files | the 0.16 Harvey cohort |
| `redline-bench-deepseek-trajectories`, `harvey_lab_017/` | public | trial and design tables | the 0.17 Harvey cohort |
| `redline-bench-jubarte-tasks` | public | the 140 task definitions | task ids and negotiation rounds |
| private local archive | private | the Muse Spark 1.3 jubarte job | the Muse Spark 1.3 jubarte arm; now public in the six-cohort dataset |

Every score, time and token figure in sections 1 to 5 is in `data/cohort_trials.csv` (one row per trial), read by `scripts/cohorts.py`. Every per-response figure is in `data/harness_responses.parquet` and `data/harness_requests.csv`, read by `scripts/harness.py`. API calls, inference minutes and the split of input tokens are in `data/trial_metrics.csv`, read by `scripts/metrics.py` for section 6's headline and Appendix A; `tools/extract_trial_metrics.py` builds that file from the datasets below. The scripts in `scripts/` read only those files.

## 2. The 0.14 report and the whole archive

Date: 2026-11-22. Scope: every number in this repository as of PR #1 (`rewrite/0.14-focus`).

A row counts as **used** if anything in it fed a number, a table or a claim. A row that was only listed, or only matched by a path search that returned nothing, does not count. Row totals are what the Hugging Face viewer shows. "Used" figures are rough estimates, not exact counts.

| Dataset | Visibility | Rows | Used | Rough rows used | Share |
|---|---|---:|---|---:|---:|
| `redline-bench-deepseek-trajectories` | public | 66,814 | yes, the main source | about 9,000 | about 13% |
| `redline-bench-jubarte-tasks` | public | 140 | yes | 140 | 100% |
| `redline-bench-jubarte-trajectories` | public | 1,563 | yes, only for the Haiku and GLM rows on 0.12.0 | about 300 | about 20% |
| `redline-bench-local-archive` | private | 60,312 | a little: the audit found the pi and Cline runs here | about 600 to 1,000 | about 1% to 2% |
| `harvey-redline-hub-ab-2026-11` | private | 5,753 | barely: the audit cites `hub-queue.tsv` and the excluded-pair notes | under 50 | under 1% |
| **Total** | | **134,582** | | **about 10,000 to 11,000** | **about 8%** |

Updated 2026-11-23: `FACTS.md` now also uses `redline-bench-jubarte-six-cohorts` (the Muse Spark 1.3 paired comparison, 298 trials) and the `muse_oct18_relaunch` config of `redline-bench-jubarte-trajectories` (150 trials). The table above predates both and has not been recomputed.

### How the main source breaks down

`redline-bench-deepseek-trajectories`, by viewer config:

| Config | Rows | Rough rows used | What was read |
|---|---:|---:|---|
| `redlinebench_trials` | 1,409 | 1,409 | every row (the audit rebuilt this table) |
| `redlinebench_files` | 39,611 | about 5,600 to 7,100 | `result.json`, `config.json`, `grade.json`, `agent/trajectory.json` (about 5,600), plus `reward.json` (1,486) |
| `harvey_lab_trials` | 181 | 181 | every row, including the `analysis` row flagged as bogus |
| `harvey_lab_files` | 8,561 | about 700 | judge, reward and trajectory files |
| `harvey_lab_017_trials` and `_design` | 185 | 185 | every row (the 88 observed and 8 missing slots) |
| `harvey_lab_017_steps` | 14,924 | 0 | not used. The 0.17 token totals come from the trials table: its 88 `S0` rows hold 1,482,533,214 input tokens, the report's 1.48 B. Summed over all 89 rows, the trials table and the steps give the same 1,496,858,846 input tokens |
| `harvey_lab_017_documents` and `_tasks` | 1,943 | 0 | not used |

### What this means

- Almost every published number rests on one public dataset, `redline-bench-deepseek-trajectories`, and on one part of it: the per-trial results, grades and trajectories. The bulky parts (documents, steps, most per-trial files) went unused.
- The two private datasets were used only to check that runs exist (the audit). No score, token or time figure in the posts comes from them. The pi figure (134 trials, 0.486) is the exception: those runs are only in the private local archive. See `DATA-AUDIT.md`.
- `redline-bench-jubarte-trajectories` is used for the older Haiku and GLM comparisons on jubarte 0.12.0 and, since 2026-11-23, for the Muse Spark 1.3 relaunch figures in `FACTS.md` (`muse_oct18_relaunch`). `redline-bench-jubarte-six-cohorts` supplies the Muse Spark 1.3 paired comparison.

### How the estimate was made

- Row totals per config come from the Hugging Face dataset viewer's size endpoint.
- The file counts per name in `redlinebench_files` and `harvey_lab_files` come from reading the `path` column of the public parquet files.
- Everything else is read off the sources each document names (`FACTS.md`, `reports/jubarte-0.14-redlinebench.md`, `DATA-AUDIT.md`). It was not traced call by call. Treat each figure as correct to within a factor of about two.
