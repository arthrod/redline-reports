# Data audit: is every run accounted for?

Date: 2026-11-22. Checked: the Hugging Face datasets under `arthrod`, the local folder `~/temp/T/redline-bench`, and the Harbor Hub job lists preserved inside those datasets.

Not reachable from this session: `~/temp/T/colab_bench`, `~/temp/T/1-blog-posts`, `~/.harbor`, and Harbor Hub itself (no Harbor credentials here). Their status below rests on what the HF archives and run logs say about them, not on a direct look.

## Verdict

The runs in the Hugging Face datasets are preserved. One set is not confirmed: the 41 Codex trials are in none of the datasets checked, and their presumed local copy (`~/temp/T/colab_bench`) could not be inspected, so their preservation is unconfirmed until someone looks there. The public description of the runs has seven errors, and two local folders hold unarchived material. Nothing found here changes a score. Fix the dataset cards before any post links to them.

## Where everything is

| Dataset | Visibility | What it holds | Trials |
|---|---|---|---:|
| `redline-bench-deepseek-trajectories` | public | `redlinebench/`: RedlineBench runs Oct 25 to 31 (jubarte 0.14.0 and 0.15.0, controls, open-model smokes). `harvey_lab/`: Harvey Hub A/B (0.16.0+). `harvey_lab_017/`: Harvey 0.17 study. `redlinebench_muse_glimmer_trials` (added 2026-11-23): the 76 finished Muse Glimmer 30B trials | 1,357 + 180 + 88 |
| `redline-bench-jubarte-tasks` | public | the 140 RedlineBench task definitions | 140 tasks |
| `redline-bench-jubarte-trajectories` | public | the older Claude Haiku runs on jubarte 0.11 and 0.12 (`main` 785, `extra` 289, `incomplete` 69); `muse_oct18_relaunch` (added 2026-11-23): 150 Muse Spark 1.3 trials from the 18 October jubarte relaunch | 1,143 + 150 |
| `redline-bench-jubarte-six-cohorts` | public | one `trials` table across six cohorts (DeepSeek 0.14.0 and 0.15.0, Nemotron 0.14.0, Harvey 0.16 and 0.17, Muse Spark 1.3) plus file tables. Mostly subsets of the datasets above; the Muse Spark 1.3 arms (140 jubarte, 158 control) are public only here | 1,847 rows |
| `redline-bench-local-archive` | private | root `data/` (repo working tree, Oct 26), `colab_bench-2026-10-27` to `10-31` and `10-30-regrade`, `jubarte-study-2026-10-30`, `jubarte-study-v14b-2026-10-31`, `redline-bench-tree-2026-11-02` | 1,066 + colab folders + 611 |
| `harvey-redline-hub-ab-2026-11` | private | Harvey Hub grades, analysis (FINDINGS, reviews, 180 prosecution reports, 47 arbiter reports), scripts, logs, `hub-queue.tsv` with the 93 Hub job IDs, and the whole working folder as `archive/harvey-redline-full.tar.zst` (about 9.4 GB raw) | 180 |
| `jubarte-skill-ab-2026-11-04` | private | Harvey 0.17 MI355X study: 96 registered slots, 88 observed, steps, documents, proxy logs | 88 |
| `T-jubarte-loop-releases` | private | release workspaces 0.14.0 to 0.17.0 | n/a |
| `T-logs-archive` | private | 8,158 `.log` and `.console` files (about 8.0 GB raw) | n/a |

How these were checked: each dataset was read through the Hugging Face API from this session, with private ones through the owner's token. On 2026-11-22 the five datasets named in the PR review (`redline-bench-deepseek-trajectories`, `harvey-redline-hub-ab-2026-11`, `redline-bench-local-archive`, `redline-bench-jubarte-trajectories`, `redline-bench-jubarte-tasks`) were listed again and match the folders above. A path search for `codex` in the first three returned no file. On 2026-11-23 `redline-bench-jubarte-six-cohorts` and the two new Muse tables were read as well, and the Muse figures in `FACTS.md` were recomputed from them.

## The one gap that could mean lost data

**The 41 Codex trials are in no dataset I could read.**

- `redline-reports/FACTS.md` and `harness/report.md` report 41 Codex trials: 0.160 mean; 18 trials after a "continue" nudge at 0.259; 40k to 126k output tokens per trial.
- They also report 134 pi trials (0.486).
- The pi trials are plausibly the `tasks-pi-*` jobs in the private `redline-bench-tree-2026-11-02/`.
- The Codex trials match no job name, task folder or config in any HF dataset above. They most likely sit only in `~/temp/T/colab_bench` (not reachable from this session).
- Archive them to HF before that folder is cleaned, and add them to the public dataset. Until then, every Codex number in the posts and the harness report has no public source.

## Errors to fix

1. **The deepseek card claims pi and Codex runs that are not in it.** It says `redlinebench/` "also holds runs with pi and Codex as the harness." All 1,406 `config.json` files in `redlinebench/` name `claude-code`.
   - The pi and Cline runs exist, but only in the private `redline-bench-tree-2026-11-02/` (`tasks-pi-v14b-015`, `tasks-pi-anth-v14b-015`, `tasks-pi-smoke-jubarte`, `tasks-cline-smoke-jubarte`), all on jubarte 0.15.0.
   - No Codex arm was found in any dataset I could read.
   - Fix: publish those trials into the public dataset, or drop the claim.
2. **The headline is a 0.15.0 number inside a 0.14.0 study.** The card's 0.494 vs 0.492 is `jubarte-study-v14b-015`, which ran binary `469c7ff4…` (0.15.0, confirmed from the agents' own `jubarte --version` output). Every other jubarte job whose agents printed a version ran `f4c352db…` (0.14.0); the card lists them as "skill iterations" without the binary. Fix: add a binary-version column and say which row is the headline.
3. **`redlinebench/trials.parquet` under-reports results.**
   - `has_result` is true for 189 rows, while 1,357 `result.json` files exist. For example, all 12 `jubarte-v7` trials show `has_result = false` and all 12 have a `result.json`.
   - `model_name` is mostly null.
   - Fix: regenerate the table from `result.json`, as this audit did.
4. **"1,409 trial directories in 53 jobs" counts grade folders as trials.**
   - 1,218 of the 1,409 rows are grade folders under `runs/`.
   - 1,357 directories carry a `result.json`, across 49 jobs. Four jobs have none: `_aborted-deepseek-smoke-for-full`, `_aborted-jubarte-ds-v9-memkill`, `k2-smoke-high-b2048`, `truncated-grades`.
   - Fix: state both counts.
5. **`harvey_lab/trials.parquet` has 180 trials, not 181.** One row is a folder named `analysis` read in as a lab trial (empty `task` and `pair`, null reward and tokens). The 90 pairs are right. Fix: drop the row and change the card to 180.
6. **The archive manifests say `jubarte_version: jubarte 0.12.0`.** That is the converter that turned `.docx` into Markdown for storage, not the binary the agents ran. Fix: rename the field `docx_converter_version`.
7. **The local-archive README stops at Oct 28.** It documents `colab_bench-2026-10-27` to `10-28c`. It does not document `10-29`, `10-30`, `10-30-regrade`, `10-31`, `jubarte-study-2026-10-30`, `jubarte-study-v14b-2026-10-31` or `redline-bench-tree-2026-11-02` (611 trials, the pi and Cline runs). Fix: add one section per folder.

## Accounted for, and how

- **The three Harvey pairs that died on credit.** They died at Synthetic credit 0% with `ApiRateLimitError` and were graded 0.0 on no deliverable. They are excluded from the 90 pairs and kept, with trials, reviews and arbiter reports, in `analysis/excluded-credit-0pct/`. Correct: counting them as losses would charge a billing event to the tool.
- **Four early Hub jobs** (83d0516d, 8c6295fd, 7ef83246, a955fdc1) were cancelled before scoring: no artifact, the judge at OpenRouter 402, jubarte built for aarch64 only. The handoff records them. They are not in any trial table, which is correct, but say so on the card.
- **Harvey judges changed mid-study.** gpt-5.4 graded until 2026-11-03 19:40Z, gpt-6-luna after. Each pair shares a judge, and each trial's `local-verifier/judge.txt` names it. A 12-trial gpt-5.6-luna batch was regraded and kept separately.
- **Harvey 0.17 missing slots.** Eight of 96 registered slots never started. They are in `design` with reward missing, not zero.
- **RedlineBench control.** Ran once per task. One task (`redline-s1-t4-g11a`) has no GLM grade because GLM hit its output limit 8 times. A 3-judge panel (gpt-5.4-mini, claude-haiku-4-5, gemini-3.1-flash-lite) graded it in the DeepSeek control (`deepseek-full-b`), both full 0.14 jubarte arms (`jubarte-ds-v9-rest`, `jubarte-ds-v12-rest`) and the Nemotron control. It is left out of every paired comparison: the full-set comparisons (ds-v9, ds-v12) use 139 tasks, not 140, the ds-v9 and ds-v12 held-out comparisons use 127 (139 minus the 12 development tasks), and the study-v14 held-out comparison uses 113.
- **Judge repeatability.** 47 RedlineBench trials carry two GLM grades; the two grades differ by 0.108 on average (median 0.062, largest 0.5), a mean per-trial standard deviation of 0.077. These 47 are the trials that happened to be regraded, not a random sample.

## Harbor Hub

The Harvey runs are on Harbor Hub as 93 jobs; the IDs are in `scripts-and-logs/runs/hub-queue.tsv` of `harvey-redline-hub-ab-2026-11`. Hub copies carry no reward (verification was off; grading was local). The 180 graded trials are in the HF archive and the public `harvey_lab/` table. Whether every trial in the 93 Hub jobs is also in the archive has not been checked: I could not list the Hub from here. Before Hub retention lapses, download every job in that file (`harbor hub job download <id>`) and compare its trial IDs with the archive.

## Local folders still holding unarchived material

In `~/temp/T/redline-bench`:

| Path | Size | State | Action |
|---|---:|---|---|
| `.scratch/` | 4.6 GB | just added to `.gitignore` (uncommitted), in no archive path list | archive to HF before any cleanup. It holds investigation work and PR drafts (`.scratch/codex/pr-body.md`, `.scratch/rel0131w/pr-body.md`) |
| `.worktrees/redline-bench-colab` | 546 MB | untracked worktree of `crosbylegal/redline-bench` | push or archive |
| `archive/` | 373 MB | archived on Oct 26 (root `data/` of the local archive); the 2026-11-02 build logs are newer and live only here | copy the five `redline-bench-tree-2026-11-02.*` logs into the HF folder |
| `experiments/mimo-jubarte-0-12/results/` | empty | holds only `.gitkeep` | confirm the 0.12 results were never run, or find them |
| `.gitignore` | | one uncommitted change (adds `.scratch/`) | commit after `.scratch/` is archived |

Not checked, because unreachable: `~/temp/T/colab_bench` (the harness, `harvey-redline` was deleted after upload per the HF card), `~/.harbor` (local Harbor job cache), and `jubarte-redlines/bench-reports`.

## Numbers in this audit

Every count above comes from reading `result.json`, `config.json`, `grade.json` and `agent/trajectory.json` for every row of `redline-bench-deepseek-trajectories`, and from the dataset manifests. The per-job table is in `data/per_job.csv`.
