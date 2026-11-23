# Which datasets the posts and reports use

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

## How the main source breaks down

`redline-bench-deepseek-trajectories`, by viewer config:

| Config | Rows | Rough rows used | What was read |
|---|---:|---:|---|
| `redlinebench_trials` | 1,409 | 1,409 | every row (the audit rebuilt this table) |
| `redlinebench_files` | 39,611 | about 5,600 to 7,100 | `result.json`, `config.json`, `grade.json`, `agent/trajectory.json` (about 5,600), plus `reward.json` (1,486) |
| `harvey_lab_trials` | 181 | 181 | every row, including the `analysis` row flagged as bogus |
| `harvey_lab_files` | 8,561 | about 700 | judge, reward and trajectory files |
| `harvey_lab_017_trials` and `_design` | 185 | 185 | every row (the 88 observed and 8 missing slots) |
| `harvey_lab_017_steps` | 14,924 | 0 | step-level data was not used. If the 0.17 token totals came from it, add 14,924 rows and the share rises to about 35% |
| `harvey_lab_017_documents` and `_tasks` | 1,943 | 0 | not used |

## What this means

- Almost every published number rests on one public dataset, `redline-bench-deepseek-trajectories`, and on one part of it: the per-trial results, grades and trajectories. The bulky parts (documents, steps, most per-trial files) went unused.
- The two private datasets were used only to check that runs exist (the audit). No score, token or time figure in the posts comes from them. The pi figure (134 trials, 0.486) is the exception: those runs are only in the private local archive. See `DATA-AUDIT.md`.
- `redline-bench-jubarte-trajectories` is used for the older Haiku and GLM comparisons on jubarte 0.12.0 and, since 2026-11-23, for the Muse Spark 1.3 relaunch figures in `FACTS.md` (`muse_oct18_relaunch`). `redline-bench-jubarte-six-cohorts` supplies the Muse Spark 1.3 paired comparison.

## How the estimate was made

- Row totals per config come from the Hugging Face dataset viewer's size endpoint.
- The file counts per name in `redlinebench_files` and `harvey_lab_files` come from reading the `path` column of the public parquet files.
- Everything else is read off the sources each document names (`FACTS.md`, `reports/jubarte-0.14-redlinebench.md`, `DATA-AUDIT.md`). It was not traced call by call. Treat each figure as correct to within a factor of about two.
