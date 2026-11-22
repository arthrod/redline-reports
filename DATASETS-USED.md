# Which datasets the report and posts use

Date: 2026-11-22. Scope: the six cohorts in `reports/jubarte-six-cohorts.md` and the harness article.

| Dataset | Visibility | What was read | Feeds |
|---|---|---|---|
| [`redline-bench-jubarte-six-cohorts`](https://huggingface.co/datasets/arthrod/redline-bench-jubarte-six-cohorts) | public | everything below, cut to the six cohorts | the published copy of every trial |
| `redline-bench-deepseek-trajectories`, `redlinebench/` | public | `result.json`, `config.json`, `grade.json` and the Claude Code session logs of the jobs listed in `DATA-AUDIT.md` | the 0.14.0 DeepSeek, 0.14.0 Nemotron and 0.15.0 DeepSeek cohorts; the harness article |
| `redline-bench-deepseek-trajectories`, `harvey_lab/` | public | per-trial reward, judge and token files | the 0.16 Harvey cohort |
| `redline-bench-deepseek-trajectories`, `harvey_lab_017/` | public | trial and design tables | the 0.17 Harvey cohort |
| `redline-bench-jubarte-tasks` | public | the 140 task definitions | task ids and negotiation rounds |
| private local archive | private | the Muse Spark 1.3 jubarte job | the Muse Spark 1.3 jubarte arm; now public in the six-cohort dataset |

Every score, time and token figure is in `data/cohort_trials.csv` (one row per trial). Every per-response figure is in `data/harness_responses.parquet`. The scripts in `scripts/` read only those files.
