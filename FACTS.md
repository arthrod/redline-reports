# Numbers used in every piece, with where each comes from

Every figure in the posts, the report and the artifacts is on this page.

## What was run

| Benchmark | Owner | Tasks | Agent harness | Model | jubarte | Judge |
|---|---|---|---|---|---|---|
| RedlineBench | Crosby + micro1 | 140 (3 scenarios × 4 turns) | Claude Code | DeepSeek-V4.1-Flash | 0.14.0 / 0.15.0 | GLM-5.3-Flash, one judge |
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
| RedlineBench, DeepSeek, Claude Code, 0.15.0 skill | 134 | 0.494 | 0.492 | −0.002 |
| RedlineBench, DeepSeek, Claude Code, held-out set | 127 | 0.489 | 0.493 | +0.004 |
| RedlineBench, DeepSeek, pi, 0.15.0 skill | 134 | 0.494 (Claude Code plain) | 0.486 | −0.008 |
| RedlineBench, Haiku 5.5, first 69 | 69 | 0.394 | 0.427 | +0.033 (35 wins, 24 losses, 10 ties) |
| RedlineBench, Haiku 5.5, second block | 33 | 0.430 | 0.412 | −0.018 (12 wins, 8 losses, 13 ties) |
| RedlineBench, GLM-5.3-flash | 40 | 0.350 | 0.364 | +0.014 (15 / 10 / 15) |
| RedlineBench, Nemotron 3.5 Lightning | 12 | 0.401 | 0.425 | +0.024 |
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

- 16–17 October: 140 trials, the jubarte arm of that comparison. Regraded by the
  gpt-6.1-sol panel, the arms score 0.316 (jubarte) and 0.297 (control), +0.019 over
  140 paired tasks. Data:
  https://huggingface.co/datasets/arthrod/redline-bench-jubarte-six-cohorts
- 18 October, first launch: 30 trials. Every one failed at authentication (20) or was
  cancelled (10).
- 18 October, relaunch: 150 trials over the same 140 tasks, 10 of them cancelled
  backups. 100 have a reward, mean 0.292, but two judge panels gave them (48
  gpt-6.1-sol, 26 Claude Haiku 5.5) and 26 are zeros recorded without a judge, so that
  mean compares with nothing. On the 74 tasks with a gpt-6.1-sol grade or such a zero
  it averages 0.221, against 0.238 for the 16–17 October arm and 0.268 for the control
  on the same tasks. Data: `muse_oct18_relaunch` in the jubarte dataset.

## Where the claim "always fewer tokens and less time" does not hold

1. Haiku 5.5 on jubarte 0.12.0 took 2 minutes longer per attempt and cost 7 cents
   more per scored task. Its cached input fell 14% and nothing else moved.
2. On Harvey LAB, jubarte cost more on individual pairs where the document already
   carried the other side's tracked changes (for example 8.9M v 3.2M tokens and
   22.6 v 13.6 minutes on one repo/securities-lending pair). The mean still fell.
3. Codex was never run without jubarte. Its 41 jubarte trials (hardest tasks first)
   scored 0.160 against 0.202 for plain Claude Code on the same tasks, and wrote
   40-126k output tokens per trial, more than plain Claude Code.

The accurate sentence: in every run since jubarte 0.14, with every model, mean time
and mean tokens fell while the score stayed inside the noise.

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
