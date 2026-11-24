# Numbers used in every piece, with where each comes from

Every figure in the posts, the report and the artifacts is on this page.

## jubarte 0.14 on RedlineBench: the numbers this week's posts use (added 2026-11-22)

Source for every row: `reports/jubarte-0.14-redlinebench.md`, rebuilt from the `result.json`, `grade.json` and `agent/trajectory.json` of every trial in `redline-bench-deepseek-trajectories/redlinebench/`. Binary `f4c352db…` (0.14.0) in every jubarte trial of the per-task table and the 0.14-arms column below. The whole-archive column also counts the controls and runs on other versions, including the 0.15.0 arm `jubarte-study-v14b-015`.

| Per task, 127 held-out tasks (`jubarte-ds-v12-rest` against `deepseek-full` + `deepseek-full-b`) | Scripts | jubarte 0.14 | Change |
|---|---:|---:|---:|
| Score | 0.491 | 0.495 | +0.004 (95% CI −0.026 to +0.033); 48 better, 40 worse, 39 equal |
| Agent minutes | 18.5 | 9.2 | −50% |
| Turns | 71 | 37 | −48% |
| Input tokens | 2.61M | 1.40M | −46% |
| Output tokens | 44.5k | 20.8k | −53% |
| At Claude Opus 5.5 list | $2.29 | $1.32 | −43% |

The "held-out 127" row further down (0.489 vs 0.493) is this same run; it took one grade per trial where a trial had two. This page now averages both.

| Scale | 0.14 arms | Whole RedlineBench archive |
|---|---:|---:|
| Runs with a result | 716 (30 jobs) | 1,357 (49 jobs) |
| Run time, summed | 157.8 h | 414.5 h |
| Input / output tokens | 1.43B / 21.1M | 3.29B / 46.2M |
| Agent turns | 35,496 | 78,524 |
| Runs per task | 2 to 27, median 3 | 4 to 42, median 7.5 |
| At DeepSeek list / Sonnet 5.5 / Opus 5.5 | | $702 / $4,839 / $9,679 |

Development set against held-out (DeepSeek, same control):

- The best drafts scored up to 0.579 against 0.515 on the 12 tuning tasks.
- On the 127 held-out tasks, ds-v12 scored +0.004 and ds-v9 scored −0.024.

Nemotron 30B-A3B: 10 of 11 drafts below the control on the 12 tasks (lowest 0.059 against 0.401). A twelfth run, `jubarte-v12-boxdown`, is left out: in 10 of its 12 trials the agent exited within seconds with no output.

Judge repeatability: 47 trials have two GLM-5.3-Flash `grade.json` files under the same path in the public trajectories: the original grade and a regrade from 30 October (archive `colab_bench-2026-10-30-regrade`). 35 got a different score the second time and 12 the same. Across all 47 the two grades differ by 0.108 on average (median 0.062, largest 0.5), a mean per-trial standard deviation of 0.077; across the 35 that changed, by 0.146 (median 0.097). Only those 35 also have two `reward.json` files. The 47 are the trials that happened to be regraded, not a random sample; 17 of them are in the paired comparisons. List: `data/judge_regrades.csv`.

## Corrections (2026-11-22)

- RedlineBench's judge reads the markup (an annotated view with deletions, insertions and comment markers). Only Harvey LAB's extractor reads accepted text. The harness report said both read accepted text; it no longer does.
- The 134-task row (0.494 vs 0.492) is jubarte **0.15.0** (`jubarte-study-v14b-015`, binary `469c7ff4…`), not 0.14.
- The Harvey A/B has 180 trials (90 pairs). The public table has 181 rows because a folder named `analysis` was read in as a trial.
- The 41 Codex trials and the 134 pi trials are not in the public dataset yet (see `DATA-AUDIT.md`).

## What was run

| Benchmark | Owner | Tasks | Agent harness | Model | jubarte | Judge |
|---|---|---|---|---|---|---|
| RedlineBench | Crosby + micro1 | 140 (3 scenarios × 4 turns) | Claude Code | DeepSeek-V4.1-Flash | 0.14.0 (all jobs except `jubarte-study-v14b-015`, which is 0.15.0) | GLM-5.3-Flash, one judge |
| RedlineBench | same | 134 common | pi | DeepSeek-V4.1-Flash | 0.15.0 | same |
| RedlineBench | same | 41 (hardest first) | Codex | DeepSeek-V4.1-Flash | 0.15.0 | same |
| RedlineBench | same | 69 + 33 | Claude Code | Claude Haiku 5.5 | 0.12.0 | Crosby's panel |
| RedlineBench | same | 40 paired | Claude Code | GLM-5.3-flash | 0.12.0 | Crosby's panel |
| RedlineBench | same | 12 | Claude Code | Nemotron 3.5 Lightning | 0.14.0 | GLM-5.3-Flash |
| Harvey LAB, redline tasks | Harvey | 90 pairs | Claude Code | DeepSeek-V4.1-Flash | 0.16.0 | gpt-5.4 (53 pairs), gpt-6-luna (37) |

The control arm is always the benchmark's own tooling: RedlineBench's Python docx
scripts, and Harvey LAB's docx skill with its `redline.py`.

## Scores (higher is better)

| Run | Tasks | Benchmark's own tools | jubarte | Difference |
|---|---|---|---|---|
| RedlineBench, DeepSeek, Claude Code, 0.15.0 binary | 134 | 0.494 (0.493 averaging double grades) | 0.492 | −0.002 (−0.000) |
| RedlineBench, DeepSeek, Claude Code, held-out set, 0.14.0 | 127 | 0.489 (0.491 averaging double grades) | 0.493 (0.495) | +0.004 |
| RedlineBench, DeepSeek, pi, 0.15.0 skill | 134 | 0.494 (Claude Code plain) | 0.486 | −0.008 |
| RedlineBench, Haiku 5.5, first 69 | 69 | 0.394 | 0.427 | +0.033 (35 wins, 24 losses, 10 ties) |
| RedlineBench, Haiku 5.5, second block | 33 | 0.430 | 0.412 | −0.018 (12 wins, 8 losses, 13 ties) |
| RedlineBench, GLM-5.3-flash | 40 | 0.350 | 0.364 | +0.014 (15 / 10 / 15) |
| RedlineBench, Nemotron 3.5 Lightning | 12 | 0.401 | 0.425 | +0.024, the best of 11 drafts; the other 10 scored 0.059 to 0.368 |
| Harvey LAB redline tasks, DeepSeek | 90 pairs | 0.936 | 0.941 | +0.006, standard error 0.005 (33 / 24 / 33) |

Per-task noise on RedlineBench is about ±0.04, and Harvey's judge moves about 0.02
between runs. None of these differences is outside the noise except Haiku's first 69.

## Time and tokens (lower is better)

| Run | Measure | Own tools | jubarte | Change |
|---|---|---|---|---|
| RedlineBench, DeepSeek, held-out 127 | agent minutes per task | 18.6 | 9.2 | −51% |
| same | input tokens per task | 2.61M | 1.40M | −46% |
| same | output tokens per task | 44.5k | 20.8k | −53% |
| RedlineBench, DeepSeek, 134 tasks, 0.15.0 | output tokens | 44.8k | 20.4k | −54% |
| same | input tokens | 2.60M | 1.27M | −51% |
| same, pi instead of Claude Code | output tokens | 44.8k | 15.0k | −67% |
| same, pi | input tokens | 2.60M | 1.42M | −45% |
| RedlineBench, GLM-5.3-flash | minutes per attempt | 102 | 68 | −33% |
| same | output tokens per attempt | 0.24M | 0.18M | −25% |
| same | tasks that finished with a valid score, of 69 | 42 | 59 | +17 tasks |
| Harvey LAB, 90 pairs | minutes per task | 37.2 | 32.4 | −13% |
| same | tokens per task | 10.4M | 8.9M | −14% |
| Harvey LAB, first 10 pairs | hard tool failures | 38 | 5 | |
| RedlineBench, Haiku 5.5, 0.12.0 | minutes per attempt | 24 | 26 | **+8%** |
| same | cached input per attempt | 9.9M | 8.5M | −14% |
| same | output per attempt | 0.30M | 0.30M | 0 |
| same | estimated cost per scored task | $0.91 | $0.98 | **+8%** |

## A later study on jubarte 0.17

Data: `harvey_lab_017/` in the DeepSeek dataset linked under Sources. Harvey LAB tasks, DeepSeek-V4.1-Flash
in Claude Code on a self-hosted node, jubarte 0.17 against LAB's tools: 88 trials,
44 matched pairs, 16 tasks, up to 3 repeats.

| Measure | LAB tools | jubarte 0.17 | Change |
|---|---|---|---|
| Task-balanced mean score | 0.925 | 0.923 | −0.002, 95% interval −0.026 to +0.022 |
| Minutes per trial | 28.4 | 26.6 | −6.4% |
| Input tokens per trial | 17.2M | 16.2M | −6.1% |
| Output tokens per trial | 143k | 133k | −7.2% |

Its own card says the design prevents a causal efficiency claim. It is the only run
on 0.17 and it is not yet used in the posts, the report or the artifact.

Other models in the archives were run with the benchmark's own tools only, so they
add no jubarte comparison: Muse Glimmer 30B (44 graded, 0.269; public since 2026-11-23
as `redlinebench_muse_glimmer_trials` in the DeepSeek dataset), Qwen 3.8 27B (21
graded, 0.106), and DeepSeek at low effort (33 valid, 0.405).

Updated 2026-11-23: an earlier version of this file listed Muse Spark 1.3 Contributor
here and said its jubarte arm failed at authentication on every trial. Both were
wrong. Its run with the benchmark's tools (158 trials, 52 valid, mean 0.385 as first
graded) is the control of a paired comparison, and Muse was launched with jubarte
three times:

- 16 to 17 October: 140 trials, the jubarte arm of that comparison. Regraded by the
  gpt-6.1-sol panel, the arms score 0.316 (jubarte) and 0.297 (control), +0.019 over
  140 paired tasks. Data:
  https://huggingface.co/datasets/arthrod/redline-bench-jubarte-six-cohorts
- 18 October, first launch: 30 trials. Every one failed at authentication (20) or was
  cancelled (10).
- 18 October, relaunch: 150 trials over the same 140 tasks, 10 of them cancelled
  backups. 100 have a reward, mean 0.292, but two judge panels gave them (48
  gpt-6.1-sol, 26 Claude Haiku 5.5) and 26 are zeros recorded without a judge, so that
  mean compares with nothing. On the 74 tasks with a gpt-6.1-sol grade or such a zero
  it averages 0.221, against 0.238 for the 16 to 17 October arm and 0.268 for the control
  on the same tasks. Data: the `muse_oct18_relaunch` config of `redline-bench-jubarte-trajectories`.

## Where the claim "always fewer tokens and less time" does not hold

1. Haiku 5.5 on jubarte 0.12.0 took 2 minutes longer per attempt and cost 7 cents
   more per scored task. Its cached input fell 14% and nothing else moved.
2. On Harvey LAB, jubarte cost more on individual pairs where the document already
   carried the other side's tracked changes (for example 8.9M v 3.2M tokens and
   22.6 v 13.6 minutes on one repo/securities-lending pair). The mean still fell.
3. Codex was never run without jubarte. Its 41 jubarte trials (hardest tasks first)
   scored 0.160 against 0.202 for plain Claude Code on the same tasks, and wrote
   40-126k output tokens per trial, more than plain Claude Code. That is a cross-harness
   comparison: with no plain-Codex control, it says nothing about whether jubarte helps
   or hurts Codex against Codex's own tools.
4. One short 0.14 arm lost on score. `jubarte-study-v13` (33 tasks, 12 of them
   development tasks) scored 0.455 against 0.523: −0.068 (−0.121 to −0.018), 7 wins
   and 16 losses. Its time and input still fell (8.4 v 19.6 minutes, 1.09M v 2.65M).

The accurate sentence: with DeepSeek-V4.1-Flash in Claude Code, in every 0.14 and 0.15
arm on RedlineBench and in the Harvey LAB studies, mean time and mean tokens fell. No
score difference was detected in any full-length arm; one 33-task arm, study-v13,
scored lower (item 4). It does not hold for every model: Nemotron 30B scored below its
0.401 control with 10 of 11 skill drafts (0.059 to 0.368) on the 12 development tasks.
The lowest drafts sit far below judge noise; the closest, v10 at 0.368, is 0.032 below,
inside the ±0.04 per-task noise above. No interval was computed for these means. Two
details: v2's trial on `redline-s3-t4-g09a` failed the validity gate in its own verifier
and scores 0, which puts v2 at 0.349 (the `glm` column of `data/per_job.csv`, 0.381,
averages only its 11 GLM grades); v3's trial on `redline-s2-t3-g04a` has no grade at all
and is left out, so v3's 0.351 covers 11 tasks, on which the control scored 0.406. A
twelfth run, `jubarte-v12-boxdown`, is not counted: in 10 of its 12 trials the agent
exited within seconds with no output.
Codex (item 3) has no control of its own.

## What the grading cannot see

- Harvey LAB's grader reads the document with every tracked change accepted. It
  cannot tell a redline from clean text. With the older extractor it also dropped
  Word comments; under Harvey's current extractor, which shows comments, the first
  19 pairs moved from 0.890 / 0.876 to 0.936 / 0.938.
- One control-arm "redline" (capital-markets indenture markup) had 39 strikethrough
  formatting runs and 0 tracked insertions or deletions. jubarte's had 38 insertions
  and 39 deletions.
- On one repo/securities-lending first turn the control arm accepted the other
  side's markup and re-issued only its own: all 182 insertions under one name.
  jubarte's file kept 191 of theirs and added 89 of ours.

## Where jubarte lost points on RedlineBench

- Turn 1 (clean template): 0.258 v 0.280 on the held-out set. A rewritten paragraph
  was marked one word at a time: 254 tracked spans per trial against 73, with a
  median insertion of 9 characters against 209.
- Agents with a one-flag strike used it too much. Rubric items "Accepts X": 62 lost,
  9 gained. Items "Rejects X": 47 gained, 12 lost.

## Release

- jubarte 0.19.0, 2026-11-21, Apache-2.0. Releases up to 0.18.0 stay AGPL-3.0-only.
- Live on GitHub (`jandira-tech/jubarte`), crates.io (`jubarte`), PyPI
  (`jubarte-docx`), npm (`jubarte-wasm`). Checked 2026-11-21.
- 36 MB installed (14 MB download). It replaces 850 MB of tools in Anthropic's `docx`
  skill and 1,793 MB in OpenAI's `doc` skill (measured 2026-10-04, Ubuntu 24.04).
- The benchmark runs used 0.12.0 to 0.16.0. 0.19.0 has not been benchmarked.

## Sources

- Full trial directories for the DeepSeek runs on both benchmarks and the 0.17 study:
  https://huggingface.co/datasets/arthrod/redline-bench-deepseek-trajectories
- Agent transcripts for the Haiku and GLM runs:
  https://huggingface.co/datasets/arthrod/redline-bench-jubarte-trajectories
- Install sizes and the script-by-script replacement notes:
  https://github.com/jandira-tech/jubarte/tree/main/docs/adoption
