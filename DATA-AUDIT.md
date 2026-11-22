# Data audit: the six cohorts

Date: 2026-11-22.

Scope: the trials behind `reports/jubarte-six-cohorts.md` and `harness/report.md`, and nothing else. For each cohort, this records where its trials are stored, what the public tables get wrong, and what is not public yet.

## Verdict

Five of the six cohorts are public, trial by trial, in `arthrod/redline-bench-deepseek-trajectories`. The sixth, Muse Spark 1.3, is half public: its control arm's trajectories and token totals are in `arthrod/redline-bench-jubarte-trajectories` (`data/redline_bench_extra_trials.parquet`, 140 of 158 trials with a trajectory). Its jubarte arm, including the session logs behind Appendix A, is only in a private local archive, so that arm has no public source until it is published.

The public tables contain errors that affect how these cohorts read (below). None of them changes a score in the report, because `data/cohort_trials.csv` was rebuilt from the trial files themselves.

## Where each cohort is stored

| Cohort | Dataset and folder | jubarte jobs | Control job |
|---|---|---|---|
| 0.14.0 DeepSeek | `redline-bench-deepseek-trajectories`, `redlinebench/` | `jubarte-ds-v2` to `jubarte-ds-v12` (no v6; `ds-v4-b` reruns half of v4), `jubarte-ds-v9-rest`, `jubarte-ds-v12-rest`, `jubarte-study-v13`, `v14`, `v14-rest`, `v15` | `deepseek-full-b` |
| 0.14.0 Nemotron | same, `redlinebench/` | `jubarte-v1` to `jubarte-v11` (`jubarte-v6-v3rep` is v6) | `nemotron-full-5090` |
| 0.15.0 DeepSeek | same, `redlinebench/` | `jubarte-study-v14b-015`, `jubarte-study-v14b-015-retry` | `deepseek-full-b` |
| 0.16 Harvey | same, `harvey_lab/` | `harvey-hub-ab`, lab arm | same job, base arm |
| 0.17 Harvey | same, `harvey_lab_017/` | lab arm | base arm |
| Muse Spark 1.3 | jubarte arm: private local archive only. Control: `redline-bench-jubarte-trajectories`, `data/redline_bench_extra_trials.parquet` | `muse-1-3-contributor-total` | `muse-1-3-contributor-total-ooriginal` |

How to tell the builds apart:

- The binary for each RedlineBench trial is in `trials.jubarte_sha256`: `f4c352db…` is 0.14.0 linux-aarch64, and `469c7ff4…` is 0.15.0.
- Muse trials carry no binary hash.

## Grades: one judge per cohort

Some trials carry more than one `grade.json`:

- a second grade from the same judge;
- a three-judge panel grade, on task `redline-s1-t4-g11a`;
- for Muse, grades from GLM-5.3-Flash as well as gpt-6.1-sol.

Averaging every grade a trial has would mix judges. The Muse jubarte arm would then read +0.046 instead of +0.019, because only that arm carries GLM grades.

`data/cohort_trials.csv` keeps one judge per cohort:

- GLM-5.3-Flash for the DeepSeek and Nemotron cohorts.
- gpt-6.1-sol for Muse.
- A score of 0 from the validity gate, which applies before any judge, is kept in both arms.
- For Harvey, the LAB judge's reward as recorded.

The `judge` and `n_grades` columns say which judge was used and how many of its grades were averaged.

## Errors in the public tables

1. **`redlinebench/trials.parquet` under-reports results.** `has_result` is true for 189 rows, yet the cohort jobs alone hold over 1,000 `result.json` files. For example, all 12 `jubarte-v7` trials show `has_result = false`, and all 12 have a `result.json`. `model_name` is mostly null. Fix: regenerate the table from `result.json`.
2. **The card's headline is the 0.15.0 cohort, described as part of the 0.14 study.** The 0.494 vs 0.492 headline is `jubarte-study-v14b-015`, which ran 0.15.0. Fix: add a binary-version column and name the cohort.
3. **Grade folders are counted as trials.** Rows under `runs/` are grade folders, not trials. Fix: count trials by `result.json`.
4. **`harvey_lab/trials.parquet` has one extra row.** A folder named `analysis` was read in as a trial (empty `task` and `pair`, null reward). The 0.16 cohort is 90 pairs and 180 trials. Fix: drop the row.
5. **The `jubarte_version: jubarte 0.12.0` field in the archive manifests is not the agents' binary.** It is the converter that turned `.docx` into Markdown for storage. Fix: rename it `docx_converter_version`.
6. **Harbor's input totals count DeepSeek's uncached input twice.** The provider reports `cache_creation_input_tokens` equal to `input_tokens` on 36,192 of 36,193 responses, and Harbor adds both. The report prices DeepSeek from the session logs instead (`harness/report.md`, section 5). Fix: note it on the card, next to the token columns.

## Accounted for, and how

- **Task `redline-s1-t4-g11a`.** GLM-5.3-Flash ran out of output on it, so only a panel graded it. It is left out of every paired comparison. That is why the DeepSeek cohorts pair 130 and 125 tasks.
- **Nine RedlineBench tasks have no `deepseek-full-b` control.** They are left out of the DeepSeek pairings. Two of them are among the 12 tuning tasks.
- **Harvey 0.16's judge changed mid-study.** gpt-5.4 graded 106 trials and gpt-6-luna graded 74. Each trial's `local-verifier/judge.txt` names its judge.
- **Harvey 0.16 pairs that died on credit.** Three pairs failed when the provider's credit ran out and are excluded from the 90. Counting them as losses would charge a billing event to the tool.
- **Harvey 0.17 trials that never started.** Four jubarte and four control trials have no grade. They are recorded as missing, not as zero.
- **Muse ordering.** The jubarte arm ran Oct 16 to 17, before the control (Oct 17 to 18). The build is unrecorded.

## Per-trial metrics (report, Appendix A)

`data/trial_metrics.csv` adds API calls, inference minutes and split token counts to every trial. Where they come from, and what is missing:

- Session logs (Claude Code JSONL): both DeepSeek cohorts and their control, Nemotron, both arms of 0.16 Harvey, and the Muse jubarte arm. These give calls, tokens and inference time.
- ATIF trajectories only: both arms of 0.17 Harvey and the Muse control. These give calls and tokens but no inference time, because trajectories carry no tool-result timestamps.
- No log at all: 20 Nemotron control and 13 Nemotron jubarte trials, 9 trials of the 0.15.0 jubarte arm, 4 per arm in 0.17 Harvey (never started), and 18 Muse control trials (no trajectory recorded).
- Check: summed per-response tokens equal Harbor's `result.json` totals on more than 95% of trials (`tests/test_metrics.py`).
- Two servers reported no prompt caching: Nemotron's local GPU and the 0.17 Harvey MI355X node. Their input is all uncached, which inflates any per-token cost estimate.

## To do before the posts link to the data

1. Publish the Muse Spark 1.3 jubarte trials (`muse-1-3-contributor-total`, with session logs) to the public dataset, or mark the Muse jubarte arm in the report as unpublished.
2. Apply fixes 1 to 6 to the dataset cards.
3. Download the Harvey 0.16 Harbor Hub jobs before Hub retention lapses. Their IDs are in `scripts-and-logs/runs/hub-queue.tsv` of the private `harvey-redline-hub-ab-2026-11` dataset. Then compare their trial IDs with `harvey_lab/`.
