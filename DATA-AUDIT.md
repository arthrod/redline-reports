# Data audit: is every run accounted for?

This file has one section per report:

1. [The six-cohort report](#1-the-six-cohort-report): `reports/jubarte-six-cohorts.md` and `harness/report.md`.
2. [The 0.14 report and the whole archive](#2-the-014-report-and-the-whole-archive): `reports/jubarte-0.14-redlinebench.md`, `FACTS.md`, the posts and the lawyer drafts.

## 1. The six-cohort report

Date: 2026-11-22.

Scope: the trials behind `reports/jubarte-six-cohorts.md` and `harness/report.md`, and nothing else. For each cohort, this records where its trials are stored and what the public tables get wrong.

### Verdict

All six cohorts are public, trial by trial, in [`arthrod/redline-bench-jubarte-six-cohorts`](https://huggingface.co/datasets/arthrod/redline-bench-jubarte-six-cohorts), which holds these cohorts and nothing else. It was cut from the sources in the table below. The Muse Spark 1.3 jubarte arm, including the session logs behind Appendix A, was public for the first time there; before, it was only in a private local archive.

The public tables contained six errors that affected how these cohorts read (below). Five were fixed on the Hub on Nov. 23, and the live cards were checked again on Nov. 24. The sixth, Harbor's double-counted input, is on no card yet. None of them changes a score in the report, because `data/cohort_trials.csv` was rebuilt from the trial files themselves.

### Where each cohort is stored

Sources the six-cohort dataset was cut from:

| Cohort | Dataset and folder | jubarte jobs | Control job |
|---|---|---|---|
| 0.14.0 DeepSeek | `redline-bench-deepseek-trajectories`, `redlinebench/` | `jubarte-ds-v2` to `jubarte-ds-v12` (no v6; `ds-v4-b` reruns half of v4), `jubarte-ds-v9-rest`, `jubarte-ds-v12-rest`, `jubarte-study-v13`, `v14`, `v14-rest`, `v15` | `deepseek-full-b` |
| 0.14.0 Nemotron | same, `redlinebench/` | `jubarte-v1` to `jubarte-v11` (`jubarte-v6-v3rep` is v6) | `nemotron-full-5090` |
| 0.15.0 DeepSeek | same, `redlinebench/` | `jubarte-study-v14b-015`, `jubarte-study-v14b-015-retry` | `deepseek-full-b` |
| 0.16 Harvey | same, `harvey_lab/` | `harvey-hub-ab`, lab arm | same job, base arm |
| 0.17 Harvey | same, `harvey_lab_017/` | lab arm | base arm |
| Muse Spark 1.3 | jubarte arm: private local archive. Control: `redline-bench-jubarte-trajectories`, `data/redline_bench_extra_trials.parquet` | `muse-1-3-contributor-total` | `muse-1-3-contributor-total-ooriginal` |

How to tell the builds apart:

- The binary for each RedlineBench trial is in `trials.jubarte_sha256`: `f4c352db…` is 0.14.0 linux-aarch64, and `469c7ff4…` is 0.15.0.
- Muse trials carry no binary hash.

### Grades: one judge per cohort

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

### Errors in the public tables

1. **`redlinebench/trials.parquet` under-reports results.** `has_result` is true for 189 rows, yet the cohort jobs alone hold over 1,000 `result.json` files. For example, all 12 `jubarte-v7` trials show `has_result = false`, and all 12 have a `result.json`. `model_name` is mostly null. Fix: regenerate the table from `result.json`. **Fixed Nov. 23:** the table now has one row per trial directory, 1,406 rows, 1,357 with a `result.json`; `has_result` agrees with the files and `model_name` is set on every row.
2. **The card's headline is the 0.15.0 cohort, described as part of the 0.14 study.** The 0.494 vs 0.492 headline is `jubarte-study-v14b-015`, which ran 0.15.0. Fix: add a binary-version column and name the cohort. **Fixed Nov. 23:** the card's table has a jubarte-build column and one row per comparison, and its headline row is 0.15.0: 125 tasks, 0.503 against 0.501.
3. **Grade folders are counted as trials.** Rows under `runs/` are grade folders, not trials. Fix: count trials by `result.json`. **Fixed Nov. 23:** the 1,218 grade folders moved to `redlinebench/grade_folders.parquet`, and the card states 1,406 trial directories in 52 jobs, 1,357 of them with a `result.json`.
4. **`harvey_lab/trials.parquet` has one extra row.** A folder named `analysis` was read in as a trial (empty `task` and `pair`, null reward). The 0.16 cohort is 90 pairs and 180 trials. Fix: drop the row. **Fixed Nov. 23:** the row is gone, and the table and the card say 180.
5. **The `jubarte_version: jubarte 0.12.0` field in the archive manifests is not the agents' binary.** It is the converter that turned `.docx` into Markdown for storage. Fix: rename it `docx_converter_version`. **Fixed Nov. 23** in all 12 `manifest.json` files of the local archive; its public copy in the six-cohort dataset's `archive/` followed on Nov. 24.
6. **Harbor's input totals count DeepSeek's uncached input twice.** The provider reports `cache_creation_input_tokens` equal to `input_tokens` on 36,192 of 36,193 responses, and Harbor adds both. The report prices DeepSeek from the session logs instead (`harness/report.md`, section 5). Fix: note it on the card, next to the token columns. **Still open:** on Nov. 24 neither the `redline-bench-deepseek-trajectories` card nor the six-cohort card mentions it.

### Accounted for, and how

- **Task `redline-s1-t4-g11a`.** GLM-5.3-Flash ran out of output on it, so only a panel graded it. It is left out of every paired comparison. That task and the nine the `deepseek-full-b` control never ran (`redline-s1-t1-g01a` to `g01e`, `redline-s1-t2-g01a` to `g01c`, `redline-s1-t2-g02b`) are why 0.14.0 DeepSeek pairs 130 tasks, not 140.
- **Nine RedlineBench tasks have no `deepseek-full-b` control.** They are left out of the DeepSeek pairings. Two of them are among the 12 tuning tasks.
- **Harvey 0.16's judge changed mid-study.** gpt-5.4 graded 106 trials and gpt-6-luna graded 74. Each trial's `local-verifier/judge.txt` names its judge.
- **Harvey 0.16 pairs that died on credit.** Three pairs failed when the provider's credit ran out and are excluded from the 90. Counting them as losses would charge a billing event to the tool.
- **Harvey 0.17 trials that never started.** Four jubarte and four control trials have no grade. They are recorded as missing, not as zero.
- **Muse ordering.** The jubarte arm started first. It ran Oct 16 21:02 to Oct 17 02:50 UTC. The control started at 02:36, near the end of the jubarte arm, and ran to 12:46, so the arms overlap by 14 minutes. The build is unrecorded.

### Per-trial metrics (report, Appendix A)

`data/trial_metrics.csv` adds API calls, inference minutes and split token counts to every trial. Where they come from, and what is missing:

- Session logs (Claude Code JSONL): both DeepSeek cohorts and their control, Nemotron, both arms of 0.16 Harvey, and the Muse jubarte arm. These give calls, tokens and inference time.
- ATIF trajectories only: both arms of 0.17 Harvey and the Muse control. These give calls and tokens but no inference time, because trajectories carry no tool-result timestamps.
- No log at all: 20 Nemotron control and 13 Nemotron jubarte trials, 9 trials of the 0.15.0 jubarte arm, 4 per arm in 0.17 Harvey (never started), and 18 Muse control trials (no trajectory recorded).
- Check: summed per-response tokens equal Harbor's `result.json` totals on more than 95% of trials (`tests/test_metrics.py`).
- Two servers reported no prompt caching: Nemotron's local GPU and the 0.17 Harvey MI355X node. Their input is all uncached, which inflates any per-token cost estimate.

### To do before the posts link to the data

1. Done: the Muse Spark 1.3 jubarte trials (`muse-1-3-contributor-total`, 140 trials, each with its session log) are public as `files/muse_jubarte.parquet` in `arthrod/redline-bench-jubarte-six-cohorts`.
2. Done for fixes 1 to 5 (Nov. 23). Still to do: fix 6, a note on the card next to the token columns.
3. Download the Harvey 0.16 Harbor Hub jobs before Hub retention lapses. Their IDs are in `scripts-and-logs/runs/hub-queue.tsv` of the private `harvey-redline-hub-ab-2026-11` dataset. Then compare their trial IDs with `harvey_lab/`.

## 2. The 0.14 report and the whole archive

Date: 2026-11-22. Re-checked 2026-11-23 against the Hugging Face datasets under `arthrod` (private ones included), the local disk, and Harbor Hub; the Hub datasets were checked again on 2026-11-24. The first pass could not reach `~/temp/T/colab_bench`, `~/.harbor` or Harbor Hub. The re-check could. Where the two passes disagree, the re-check is what is written here.

### Verdict

The runs are preserved, the 41 Codex trials included: they sit in the private archive, and the first pass missed them. The seven dataset-card errors listed below were fixed on the Hub on Nov. 23 (late UTC), and a measurer confirms each fix against the live datasets. An eighth, found on Nov. 24, was fixed the same day (DOCX storage, below). Nothing found here changes a score.

**New on Nov. 23, and urgent.** At 22:21 UTC, both private archives were copied in full into the public `redline-bench-jubarte-six-cohorts`, under `archive/`. That made two of the private datasets in the table below readable by anyone; a third followed on Nov. 24 (update below). The copy includes:

- local agent state: `.empryo` sessions, memory SQLite databases, `.crush` databases and shell output (`colab_bench-2026-11-22-b/agent_state.parquet`, 150 MB);
- the packed `redline-bench/.scratch` (`scratch-2026-11-22/files.parquet`, 188 MB);
- every Harvey Hub working file.

The pack notes say keys and the owner's email were redacted, but the content was packed for a private archive. That card does not mention `archive/` at all. Decide whether this copy should stay public.

**Decided Nov. 24: the `archive/` copies stay public as they are.** The scan below found no secret at commit 22601207. Values replaced in earlier commits (an expired signed token, and hashes that could confirm the redacted email) remain readable in the Hub's revision history. Squashing that history was the alternative; it would break every existing link pinned to a commit.

**Update, Nov. 24.** Between 00:13 and 00:18 UTC two more datasets were copied into the same `archive/`: the private `jubarte-skill-ab-2026-11-04` (the Harvey 0.17 MI355X study, with its steps, documents and proxy logs) and the public `redline-bench-deepseek-trajectories`. `redline-bench-local-archive` was brought up to its source's head. Three of the private datasets in the table are now readable by anyone. Each archived README is its source's current README with its links pointed into `archive/`, and the six-cohorts card now describes `archive/` (commit 22601207). A pattern scan of all 4,389 files at that commit, unpacked through parquet, base64, gzip, zstd, zip and tar, matched no secret: its nine distinct hits are environment-variable names, hashes, a file path, prose, and the default Postgres password that Langfuse publishes in its own setup files.

### Where everything is

| Dataset | Visibility | What it holds | Trials |
|---|---|---|---:|
| `redline-bench-deepseek-trajectories` | public; also copied into the six-cohorts `archive/` since Nov. 24 | `redlinebench/`: RedlineBench runs Oct. 25 to 31 (jubarte 0.14.0 and 0.15.0, controls, open-model smokes); since Nov. 23 also `muse_glimmer_trials.parquet`, the 76 finished Muse Glimmer 30B trials, and `grade_folders.parquet`, the 1,218 grade folders that used to sit in the trials table. `harvey_lab/`: Harvey Hub A/B (0.16.0+). `harvey_lab_017/`: Harvey 0.17 study | 1,357 + 180 + 88 |
| `redline-bench-jubarte-tasks` | public | the 140 RedlineBench task definitions | 140 tasks |
| `redline-bench-jubarte-trajectories` | public | `main` 785: Claude Haiku 5.5 and GLM-5.3-flash. `incomplete` 69: the same two models. `extra` 289: DeepSeek-V4.1-Flash 75, the Muse Spark 1.3 control 158, 30 trials of the Muse Spark 1.3 jubarte relaunch of Oct. 18, aborted GLM 26. Since Nov. 23, `muse_trials` 150: the other trials of that relaunch, none of them among the 30 | 1,293 |
| `redline-bench-jubarte-six-cohorts` | public (created Nov. 22) | the six cohorts of `reports/jubarte-six-cohorts.md`, trial by trial, the Muse Spark 1.3 jubarte arm included; `writeups/`, `code/`; `archive/`, full copies of other datasets: since Nov. 23 22:21 UTC `redline-bench-local-archive` and `harvey-redline-hub-ab-2026-11` (both private), `redline-bench-jubarte-trajectories` and `redline-bench-jubarte-tasks`; since Nov. 24 00:13 to 00:18 UTC also `jubarte-skill-ab-2026-11-04` (private) and `redline-bench-deepseek-trajectories`, with `redline-bench-local-archive` brought up to its source's head | six cohorts |
| `redline-bench-local-archive` | private; public copy since Nov. 23 | root `data/` (repo working tree, Oct. 26), `colab_bench-2026-10-27` to `10-31` and `10-30-regrade`, `jubarte-study-2026-10-30`, `jubarte-study-v14b-2026-10-31`, `redline-bench-tree-2026-11-02` (the pi, Cline and Codex runs); added Nov. 22: `colab_bench-2026-11-22` and `-b` (the last of `colab_bench`) and `scratch-2026-11-22` (`redline-bench/.scratch`) | 1,066 + colab folders + 611 |
| `harvey-redline-hub-ab-2026-11` | private; public copy since Nov. 23 | Harvey Hub grades, analysis (FINDINGS, reviews, 180 prosecution reports, 47 arbiter reports), scripts, logs, `hub-queue.tsv` with the 93 Hub job IDs, and the whole working folder as `archive/harvey-redline-full.tar.zst` (about 9.4 GB raw) | 180 |
| `jubarte-skill-ab-2026-11-04` | private; public copy since Nov. 24 (00:15 UTC) | Harvey 0.17 MI355X study: 96 registered slots, 88 observed, steps, documents, proxy logs | 88 |
| `T-jubarte-loop-releases` | private | release workspaces 0.14.0 to 0.17.0 | n/a |
| `T-logs-archive` | private | 8,158 `.log` and `.console` files (about 8.0 GB raw) | n/a |

### The Codex and pi trials: found, but not in a trial table

**The 41 Codex trials are in `redline-bench-local-archive/redline-bench-tree-2026-11-02/`.** The first pass said they matched no job in any dataset. That was wrong.

| Job | Trials, each with a `result.json` |
|---|---:|
| `jubarte-study-codex-hyper-hard5` | 3 |
| `jubarte-study-codex-hyper-rest-01` | 10 |
| `jubarte-study-codex-hyper-rest-02` | 10 |
| `jubarte-study-codex-hyper-rest-03` | 4 |
| `jubarte-study-codex-hyper-rest-04` | 10 |
| `jubarte-study-codex-hyper-rest-05` | 4 |
| **Total** | **41** |

The same folder holds:

- Codex smokes: `jubarte-study-codex-smoke-g07a` (2) and `jubarte-study-codex-native-g07a` (1).
- 14 Codex trials from failed or retried launches: `_failed-codex-hyper-rest-03-uvcache` (6), `_hyper-402-codex-hyper-rest-05` (6), `_retry-codex-hyper-hard5` (2).
- The pi runs: `jubarte-study-pi-anth-v14b-015` (140 trials), `jubarte-study-pi-v14b-015` (35), and the pi smokes.
- The Cline smokes: `jubarte-study-cline-smoke-jubarte` and `-plain`.

Which pi trials make up the 134 that `FACTS.md` and `harness/report.md` report was not re-derived here.

Since Nov. 23 these trials can be read publicly through the six-cohorts `archive/` copy. They are still not in any documented public trial table. Until they are, the posts and `harness/report.md` should cite them as archived, not as published.

### The seven card errors: fixed on Nov. 23

Before the fix, a read-only measurer run against the live Hub (kept outside this repository) failed all seven. After the fix it passes all seven. Two commits:

- `redline-bench-deepseek-trajectories` [cc19d235](https://huggingface.co/datasets/arthrod/redline-bench-deepseek-trajectories/commit/cc19d235a5dcfc5644c68ee4842c002dea45cf12) (public), made on top of b49c2003.
- `redline-bench-local-archive` [ebb83be8](https://huggingface.co/datasets/arthrod/redline-bench-local-archive/commit/ebb83be8632a4034e26d395bf33deef63012ed25) (private), made on top of 692dbeb2.

1. **pi and Codex claim.** The card claimed `redlinebench/` held pi and Codex runs. It now says there are none: all 1,406 `config.json` files in `redlinebench/` name `claude-code`. The pi, Cline and Codex trials are in `redline-bench-tree-2026-11-02/` within the private `redline-bench-local-archive`; since Nov. 23 that archive has had a public copy in the six-cohorts `archive/` (section above). They are in no documented trial table.
2. **Headline.** The card's main table now has a jubarte-build column and one row per comparison. 0.494 / 0.492 is gone. The headline row is now **0.15.0**: `jubarte-study-v14b-015` and its retry against `deepseek-full-b`, 125 tasks, 0.503 against 0.501. Two rows were added with it, both on 0.14.0:
   - DeepSeek, 130 tasks, 0.503 against 0.497.
   - Nemotron, 12 tasks, 0.401 against 0.308.

   All figures are from the six-cohort report. The card's summary sentence no longer says the score did not change across the board: it names the Nemotron loss.
3. **`redlinebench/trials.parquet` rebuilt.** It now has one row per trial directory. Each row comes from the archive's own trial tables, and `has_result` is set from whether a `result.json` exists:
   - 1,406 rows, 1,357 with a `result.json`;
   - 0 rows without a directory, 0 directories without a row;
   - `has_result` agrees with the files on every row;
   - `model_name` is set on every row.

   The 191 trial rows the old table did have came through unchanged. The 1,218 grade-folder rows moved to `redlinebench/grade_folders.parquet` (config `redlinebench_grade_folders`). Of those, 47 are audit copies of trials that are also in the trials table.
4. **Counts.** The card states 1,406 trial directories in 52 jobs, 1,357 with a `result.json` (49 jobs), and 1,218 grade folders. Three jobs have no `result.json`: `_aborted-deepseek-smoke-for-full`, `_aborted-jubarte-ds-v9-memkill` and `k2-smoke-high-b2048`. The fourth the audit listed, `truncated-grades`, holds only grade folders.
5. **`harvey_lab/trials.parquet`:** the `analysis` row was dropped, leaving 180 rows, and the card says 180.
6. **Manifest field.** `jubarte_version` was renamed to `docx_converter_version` in all 12 `manifest.json` files of the archive, not only the root one. `archiver.py verify` does not read the key. The archived copies of `archiver.py` still write the old name, and the README says so.
7. **Local-archive README.** It now has a folder index and one section for each missing folder. Each section is written from the folder's `manifest.json`, trial table and `NOTES.md`. Writing them turned up one discrepancy: `colab_bench-2026-11-22-b/NOTES.md` says `twins_index.parquet` has 18,313 rows, but the file has 16,624.

How the fix was checked:

- Before upload, pi with GLM-5.3 reviewed both diffs. It caught two errors in the README draft and one unsupported sentence in the card. All three were corrected before upload.
- The Hub's dataset viewer had not finished processing the new commit when this was written.

**Stale until Nov. 24:** the public six-cohorts `archive/` copy held the local archive as it was at 692dbeb2, with the old README and manifest key. At 00:18 UTC on Nov. 24 it was brought up to its source's head: all 12 archived `manifest.json` files now carry `docx_converter_version` and none `jubarte_version`, and the archived README is the corrected one, its links pointed into `archive/`.

### An eighth card error, found and fixed Nov. 24

The `redline-bench-deepseek-trajectories` card says RedlineBench `.docx` files "are stored as Markdown with tracked changes in CriticMarkup (`kind = docx_markdown`), not as bytes". The data says otherwise. All 1,362 `.docx` rows in the 55 `redlinebench/files-*.parquet` shards keep the original Word file in `content` (every one starts with the zip signature `PK\x03\x04`). 1,361 also carry the CriticMarkup rendering in `text`, and one is `docx_unconverted`. The card should say both are kept. Its archived copy in the six-cohorts dataset repeated the sentence.

Fixed on Nov. 24 in both: [c3cc2580](https://huggingface.co/datasets/arthrod/redline-bench-deepseek-trajectories/commit/c3cc25807a23b424fb448a3be9603e7bcce84a52) on `redline-bench-deepseek-trajectories` and [af5586fa](https://huggingface.co/datasets/arthrod/redline-bench-jubarte-six-cohorts/commit/af5586fa2a9010e621b9c8fb36335e2201919385) on the six-cohorts copy. Each card now says all 1,362 `.docx` rows keep the Word file, and 1,361 of them also carry the CriticMarkup rendering. Each also documents the 47 regrades below: they share paths with the first grades, and the `archive` column tells them apart. A read-only measurer, kept outside this repository, checks the live HEAD of both cards: 6 checks failed before the fix and pass after it.

### Accounted for, and how

- **The three Harvey pairs that died on credit.** They died at Synthetic credit 0% with `ApiRateLimitError` and were graded 0.0 on no deliverable. They are excluded from the 90 pairs and kept, with trials, reviews and arbiter reports, in `analysis/excluded-credit-0pct/`. Correct: counting them as losses would charge a billing event to the tool.
- **Four early Hub jobs** (83d0516d, 8c6295fd, 7ef83246, a955fdc1) were cancelled before scoring. They had no `/app` artifact, the judge hit the OpenRouter 402, and jubarte was built for aarch64 only (`scripts-and-logs/HANDOFF.md`). They are not in any trial table, which is correct, but the card should say so.
- **Harvey judges changed mid-study.** gpt-5.4 graded until 2026-11-03 19:40Z (106 trials), and gpt-6-luna graded after that (74). Each pair shares a judge, and each trial's `local-verifier/judge.txt` names it. gpt-5.6-luna graded 12 trials between 19:40 and 19:50Z and was dropped as too expensive. Those 12 were regraded with gpt-6-luna, and the 5.6 grades are kept in `local-verifier-luna56/`.
- **Harvey 0.17 missing slots.** Eight of 96 registered slots never started (four per arm). They are in `design` with reward missing, not zero.
- **RedlineBench control.** `deepseek-full-b` ran once per task, but only on 131 of the 140 tasks. These nine never ran: `redline-s1-t1-g01a` to `g01e`, `redline-s1-t2-g01a` to `g01c`, and `redline-s1-t2-g02b`.
  - One more task, `redline-s1-t4-g11a`, has no GLM grade because GLM hit its output limit 8 times. The 3-judge panel graded it instead, and it is left out of every paired comparison.
  - That is why the 0.14.0 DeepSeek cohort pairs 130 tasks, not 140. The 0.14 report's comparisons use 130 (the full set), 120 (held-out: 130 minus the 10 development tasks the control ran) and 106 (study-v14 held-out).
  - Until 2026-11-24 the 0.14 report took the control for those nine tasks from an earlier job, `deepseek-full`, which gave 139, 127 and 113.
- **Double GLM grades: the 47 are confirmed, but the counts still conflict.** The first pass found 47 RedlineBench trials with two GLM grades; their per-trial standard deviation averages 0.077, and the two grades differ by 0.108 on average. Re-derived on Nov. 24 from all 1,259 GLM-5.3-Flash `grade.json` rows (1,212 distinct paths) in the RedlineBench files of `redline-bench-deepseek-trajectories`: 47 of those paths, all under `runs/rejudge-synthetic/GLM-5.3-Flash/`, are stored twice, once from the first grading and once from `colab_bench-2026-10-30-regrade`. The two judge outputs differ in text every time; in 35 pairs the score differs too, and in 12 it is the same. Across all 47 the gap averages 0.108 (median 0.062, largest 0.5) and the per-trial standard deviation 0.077, as published. The two grades share one path (as do the two `reward.json` copies of the 35 changed trials), so the file path alone cannot tell them apart; the `archive` column can, and since Nov. 24 the card says so. But `data/cohort_trials.csv` (section 1) gives an `n_grades` of 2 to 10 for every GLM-graded trial in the six cohorts. That does not square with 47 double-graded trials, and it was not re-derived here. Reconcile the two counts before citing either. 17 of the 47 are in the 0.14 report's paired comparisons (5 `deepseek-full-b`, 8 `jubarte-ds-v9-rest`, 3 `jubarte-ds-v12-rest`, 1 `jubarte-ds-v12`), whose per-task scores average both grades. List with both grades and their archives: `data/judge_regrades.csv`.

### Harbor Hub

The Harvey runs are on Harbor Hub as 93 jobs; the IDs are in `scripts-and-logs/runs/hub-queue.tsv` of `harvey-redline-hub-ab-2026-11`. Hub copies carry no reward (verification was off; grading was local). Every Hub trial that was graded is also in the HF archive and in the public `harvey_lab/` table, so losing Hub retention would lose nothing scored.

Checked Nov. 23 with `harbor hub job status`: the first and last IDs in sorted order (0068fa72…, fac5e650…) each still show 2 completed trials. The jobs were not downloaded.

### Local folders, as of Nov. 23

Before this audit ran, two folders it had marked unreachable or unarchived were packed to the private archive on Nov. 22 and then deleted:

- `~/temp/T/colab_bench` was packed to `colab_bench-2026-11-22/` and `-b/`. Not packed: Harvey's own tasks as downloaded, `.env` and caches.
- `redline-bench/.scratch` was packed to `scratch-2026-11-22/`. Not packed: clean git clones, virtualenvs and caches.

In `~/temp/T/redline-bench`:

| Path | Size | State | Action |
|---|---:|---|---|
| `.scratch/` | 276 KB | packed and cleared on Nov. 22; only `jubarte-adoption*` is left | none |
| `.worktrees/redline-bench-colab` | gone | deleted unpacked on Nov. 22; the pack notes say its job folders are in `redline-bench-deepseek-trajectories` and its tasks in `redline-bench-jubarte-tasks` | none |
| `archive/` | 373 MB | archived on Oct. 26 (root `data/` of the local archive); the five `redline-bench-tree-2026-11-02.*` build logs are still only here, not in the HF folder | copy the five logs into the HF folder |
| `experiments/mimo-jubarte-0-12/results/` | empty | holds only `.gitkeep` | confirm the 0.12 results were never run, or find them |
| `.gitignore` | | one uncommitted change (adds `.scratch/`) | commit it; `.scratch/` is archived |
| `publication-2026-11-22/` | | new, untracked: the 0.14 report, `FACTS.md`, `DATA-AUDIT.md`, `harness/` and posts | commit or archive |

Other folders:

- `~/.harbor`: holds only `credentials.json`; there is no local job cache.
- `jubarte-redlines/bench-reports`: 214 MB with no Codex files. Not otherwise audited.

### Numbers in this audit

Every count above comes from reading `result.json`, `config.json`, `grade.json` and `agent/trajectory.json` for every row of `redline-bench-deepseek-trajectories`, and from the dataset manifests. The Nov. 23 counts come from the trial tables and file listings of the datasets themselves. The per-job table is `data/per_job.csv`.
