# jubarte in six cohorts: no score gain detected, and less work in five of them

Report date: 2026-11-22.

Scope: six groups of runs, called cohorts here, and nothing else. In each cohort an AI agent redlined contracts with jubarte, and a control run of the same agent on the same tasks used the benchmark's own tooling.

| Cohort | Benchmark | Agent model, harness | jubarte build |
|---|---|---|---|
| 0.14.0 DeepSeek | RedlineBench, 140 tasks | DeepSeek-V4.1-Flash-1017 in Claude Code 2.1.310 | 0.14.0 |
| 0.14.0 Nemotron | RedlineBench, 12 tasks | Nemotron 3.5 Lightning 30B-A3B in Claude Code 2.1.310, one RTX 5090 | 0.14.0 |
| 0.15.0 DeepSeek | RedlineBench, 135 tasks | DeepSeek-V4.1-Flash-1017 in Claude Code 2.1.310 | 0.15.0 |
| 0.16 Harvey | Harvey LAB redline tasks, 90 A/B pairs | DeepSeek-V4.1-Flash in Claude Code, on Harbor Hub | 0.16.x |
| 0.17 Harvey | Harvey LAB editing tasks, 17 tasks | DeepSeek Flash 1017 in Claude Code, served on a self-hosted MI355X | 0.17.x |
| Muse Spark 1.3 | RedlineBench, 140 tasks | Muse Spark 1.3 Contributor | not recorded |

Data: every trial in the six cohorts, and nothing else, is in one public dataset: [`arthrod/redline-bench-jubarte-six-cohorts`](https://huggingface.co/datasets/arthrod/redline-bench-jubarte-six-cohorts).

Disclosure: Arthur Souza Rodrigues writes jubarte (Jandira Technologies) and ran every trial here. RedlineBench is by Crosby Legal and micro1, and the Legal Agent Benchmark (LAB) is by Harvey. No one at Crosby, micro1, Harvey, DeepSeek, NVIDIA or Synthetic reviewed this report.

## 1. The answer, in one table

Each row pairs a task's jubarte trials with the same task's control trials and averages the difference. Scores run from 0 to 1.

| Cohort | Tasks | Control | jubarte | Change (95% CI) | Better / worse / equal | Agent minutes | Output tokens | Input tokens |
|---|---:|---:|---:|---|---|---|---|---|
| 0.14.0 DeepSeek | 130 | 0.503 | 0.497 | −0.007 (−0.030 to +0.016) | 57 / 56 / 17 | 18.3 → 10.3 (−44%) | 44.2k → 21.5k (−51%) | 2.54M → 1.39M (−45%) |
| 0.14.0 Nemotron | 12 | 0.401 | 0.308 | **−0.093 (−0.170 to −0.018)** | 4 / 7 / 1 | 30.8 → 24.1 (−22%) | 64.4k → 67.4k (+5%) | 4.05M → 4.80M (+19%) |
| 0.15.0 DeepSeek | 125 | 0.503 | 0.501 | −0.003 (−0.028 to +0.024) | 31 / 39 / 55 | 18.4 → 10.1 (−45%) | 44.4k → 20.2k (−54%) | 2.57M → 1.24M (−52%) |
| 0.16 Harvey | 90 pairs | 0.936 | 0.941 | +0.006 (−0.004 to +0.017) | 33 / 24 / 33 | 37.2 → 32.4 (−13%) | 53.3k → 46.5k (−13%) | 10.45M → 8.95M (−14%) |
| 0.17 Harvey | 16 | 0.925 | 0.923 | −0.002 (−0.026 to +0.022) | 8 / 8 / 0 | 28.4 → 26.6 (−6%) | 143.5k → 133.1k (−7%) | 17.20M → 16.16M (−6%) |
| Muse Spark 1.3 | 140 | 0.297 | 0.316 | +0.019 (−0.033 to +0.071) | 57 / 60 / 23 | 48.8 → 36.1 (−26%) | 226.3k → 180.7k (−20%) | 3.98M → 2.93M (−26%) |

How to read it:

- **Score.** In five cohorts no difference was detected: every interval includes zero. No equivalence margin was set, so this means "no difference detected", not "equal". In the sixth, Nemotron, jubarte scored lower, and its interval excludes zero.
- **Work.** In those same five cohorts the agent finished sooner and used fewer tokens. The saving was largest with DeepSeek on RedlineBench, where time and output roughly halved, and smallest on Harvey's tasks (6% to 14%).
- **Comparing cohorts.** Each cohort has its own judge, the same in both of its arms (section 2), except 0.16 Harvey, whose judge changed from gpt-5.4 to gpt-6-luna during the run (section 3). Scores compare within a row, not across rows: Harvey's 0.94 and RedlineBench's 0.50 come from different rubrics and different judges.

Method:

- A task's score in each arm is the mean of its graded trials. Its minutes and tokens are averaged over the same graded trials, so an attempt that was never graded (it never started, or the grader failed) counts in neither the score nor the cost. Appendix A counts every trial.
- The interval is a bootstrap over tasks (10,000 draws, seed 20261122).
- A task counts as equal when the two arms' means differ by less than 10⁻¹², which is floating-point noise.
- Tasks without a graded trial in both arms are left out. That is why the DeepSeek rows have 130 and 125 tasks, not 140, and 0.17 Harvey has 16 of its 17.
- Input tokens are Harbor's totals. For the DeepSeek provider these count uncached input twice; the prices in section 6 correct for it.
- `uv run python scripts/cohorts.py` recomputes sections 1 to 5 from `data/cohort_trials.csv`. Section 6's per-response tables come from `scripts/harness.py` (`data/harness_responses.parquet`, `data/harness_requests.csv`); its headline table and Appendix A come from `scripts/metrics.py` (`data/trial_metrics.csv`). Section 8 lists every input.

## 2. What each cohort is

| Cohort | jubarte arm | Control arm | Judge, both arms | Dates (UTC) |
|---|---|---|---|---|
| 0.14.0 DeepSeek | 560 trials in 17 jobs | `deepseek-full-b`, one run per task | GLM-5.3-Flash, benchmark rubric | control Oct 27 22:05 to Oct 28 05:13; jubarte Oct 28 05:14 to Oct 30 15:46 |
| 0.14.0 Nemotron | 144 trials in 11 jobs, 12 tasks each | `nemotron-full-5090`, 140 tasks | GLM-5.3-Flash | control Oct 26 02:59 to 12:32; jubarte Oct 26 12:33 to Oct 27 00:10 |
| 0.15.0 DeepSeek | 147 trials in 2 jobs (`study-v14b-015` and a 6-trial retry) | `deepseek-full-b` | GLM-5.3-Flash | jubarte Oct 30 21:21 to Oct 31 02:05 |
| 0.16 Harvey | 90 trials, `harvey-hub-ab` | 90 trials, paired A/B | Harvey's LAB judge: gpt-5.4 for 106 trials, then gpt-6-luna for 74 | Nov 1 to Nov 4 |
| 0.17 Harvey | 48 trials over 17 tasks, two to four per task | 48 trials, the same tasks and counts | Harvey's LAB judge, gpt-6-luna | Nov 4 23:33 to Nov 5 02:56 |
| Muse Spark 1.3 | 140 trials, `muse-1-3-contributor-total` | `muse-1-3-contributor-total-ooriginal` | gpt-6.1-sol panel | jubarte Oct 16 21:02 to Oct 17 02:50; control Oct 17 02:36 to 12:46 |

Three design facts matter for every row:

- **The arms were not interleaved.** In each RedlineBench cohort, the jubarte arm ran after the control (Muse is the exception: its jubarte arm ran first). Model, harness and grader were pinned, but a change at the model provider between those days cannot be ruled out. The time and token differences are observed differences between arms run hours or days apart, not controlled causal estimates.
- **The control ran once per task.** Control run-to-run variance is not measured here.
- **A zero is sometimes a gate, not a judgment.** On RedlineBench, a deliverable with no tracked changes scores 0 without reaching the judge. That applies equally to both arms.

## 3. Cohort by cohort

### 0.14.0 DeepSeek: 560 trials, no difference detected

The cohort is the whole 0.14.0 study on DeepSeek. Its jobs fall into three groups:

- 11 skill drafts, each run on the same 12 tuning tasks (`ds-v2` to `ds-v12`; `ds-v4-b` reran half of `ds-v4`).
- Two drafts carried to the other 128 tasks (`ds-v9-rest`, `ds-v12-rest`).
- A study pass (`study-v13`, `v14`, `v14-rest`, `v15`).

Every job against the same control:

| jubarte runs | Trials | Paired tasks | Control | jubarte | Change (95% CI) | Minutes |
|---|---:|---:|---:|---:|---|---|
| `ds-v12-rest` | 128 | 120 | 0.499 | 0.501 | +0.002 (−0.029 to +0.032) | 18.3 → 9.1 |
| `ds-v9-rest` | 128 | 120 | 0.499 | 0.474 | −0.025 (−0.060 to +0.008) | 18.3 → 11.0 |
| `study-v14-rest` | 98 | 89 | 0.458 | 0.473 | +0.015 (−0.013 to +0.044) | 18.3 → 11.5 |
| `study-v14` | 33 | 27 | 0.572 | 0.521 | −0.050 (−0.106 to +0.000) | 18.7 → 8.1 |
| `study-v13` | 33 | 27 | 0.572 | 0.481 | **−0.090 (−0.150 to −0.035)** | 18.7 → 8.0 |
| All jobs, the 12 tuning tasks | 153 | 10 | 0.552 | 0.582 | +0.030 (−0.017 to +0.080) | 18.4 → 11.6 |
| All jobs, every other task | 407 | 120 | 0.499 | 0.490 | −0.010 (−0.034 to +0.014) | 18.3 → 10.2 |

Two of the 12 tuning tasks have no control grade, which is why that row pairs 10.

Three readings:

- **The tuning tasks flattered the skill.** The drafts were written while watching 12 tasks. There, jubarte led by 0.030; on the 120 tasks it never saw, it trailed by 0.010. Draft means on the tuning tasks ran from 0.510 (`ds-v3`) to 0.576 (`ds-v9`). The best of them, `ds-v9`, then lost 0.025 on the other tasks. A gain found on a dozen hand-watched tasks did not carry over.
- **One study job lost outright.** `study-v13` is the only DeepSeek job whose interval excludes zero. `study-v15`, 14 tasks, averaged 0.213 and is too small to pair.
- **The time saving held in every job, the losing one included.** Agent minutes fell by 37% to 57%.

### 0.14.0 Nemotron: the one cohort where jubarte lost

Eleven skill drafts on the same 12 tasks, on a 30B-parameter model with 3B active, served from one GPU. Against a control of 0.401 on those tasks, only `jubarte-v9` came out ahead (0.425). The others ranged from 0.059 (`v1`) to 0.368 (`v10`). Pooled, the cohort lost 0.093, and the interval excludes zero.

It also did not save work. Output rose 5% and input 19%. Agent minutes fell 22%, partly because 12 jubarte trials hit the agent timeout, which caps their time. Another 13 ended in runtime errors and were not graded.

The binary was the same 0.14.0 in all eleven drafts; only the skill text changed. On this model, the instructions cost more than the tool saved. Section 6 shows one mechanism: Nemotron thinks on every response, and a long skill gives it more to think about.

### 0.15.0 DeepSeek: the same result on the next build

One study job (141 trials, 135 tasks) plus a 6-trial retry. Against the same control: −0.003 (−0.028 to +0.024), with time down 45% and output down 54%. The main job alone, on its 119 paired tasks: +0.004 (−0.022 to +0.031).

The study changed builds between 0.14.0 and 0.15.0 with the same skill, and the result did not move.

### 0.16 Harvey: 90 A/B pairs, a small saving

Harvey LAB's redline tasks, run in pairs on Harbor Hub. Each pair is one task, run once in each arm. The result was +0.006 (−0.004 to +0.017), with time, input and output each about 13% lower.

The judge changed during the run: gpt-5.4 graded 106 trials and gpt-6-luna graded 74. A pair can therefore straddle the two judges. Harvey's judge also moves about 0.02 between runs of the same file, which is larger than the difference measured here.

LAB's scores sit near the ceiling (median 0.962 in the jubarte arm). There is little room for any tool to move them.

### 0.17 Harvey: 17 tasks, no material saving

LAB editing tasks on a self-hosted MI355X, 48 trials per arm over 17 tasks (two to four per task): −0.002 (−0.026 to +0.022) on the 16 tasks graded in both arms, with about 6% less time and tokens. Four trials in each arm never started, so 44 of 48 were graded in each; one graded jubarte trial is flagged as a failed execution. At 16 tasks, a saving of a few percent cannot be told apart from run-to-run variation.

### Muse Spark 1.3: no difference detected, and two caveats

On all 140 RedlineBench tasks: +0.019 (−0.033 to +0.071), with 26% less time and input and 20% less output. The judge is a gpt-6.1-sol panel in both arms.

Two caveats, both stated plainly:

- **The jubarte build was not recorded.** The trials carry no binary hash.
- **The jubarte arm ran first.** It ran Oct 16 21:02 to Oct 17 02:50 UTC. The control started at 02:36, near the end of the jubarte arm, and ran to 12:46, so the arms overlap by 14 minutes.

Timeouts weigh on both arms. The jubarte arm hit the agent timeout in 33 of 140 trials, and 29 of those scored zero. The control hit it in 78 of 158 trials. Timed-out trials were still graded on whatever the agent had saved.

## 4. Where jubarte gains and loses within RedlineBench

Each RedlineBench task is one round of a four-round negotiation (the `-tN-` in its id). Split by round:

| Round | 0.14.0 DeepSeek | 0.15.0 DeepSeek | Muse Spark 1.3 |
|---|---|---|---|
| 1, first markup of a clean draft | −0.060 (−0.127 to +0.017), 9 tasks | −0.092 (−0.179 to +0.017), 9 | −0.001 (−0.059 to +0.058), 14 |
| 2 | +0.017 (−0.024 to +0.058), 38 | **+0.040 (+0.001 to +0.082)**, 38 | +0.017 (−0.090 to +0.128), 42 |
| 3 | +0.014 (−0.018 to +0.048), 42 | +0.006 (−0.035 to +0.053), 42 | +0.077 (−0.004 to +0.156), 42 |
| 4, closing round | −0.038 (−0.083 to +0.007), 41 | −0.035 (−0.085 to +0.016), 36 | −0.031 (−0.135 to +0.070), 42 |

The pattern is the same in all three cohorts. jubarte does a little better in the middle rounds, where the agent answers the other side's markup, and a little worse in the first and last rounds. Only one cell excludes zero (0.15.0, round 2, barely), so treat this as a direction to test, not a finding.

The first round is where the agent rewrites a clean draft. With a tool that marks every change, a rewritten paragraph becomes dozens of small insertions and deletions. That is a plausible reason the first round scores lower, but this report does not test it.

## 5. Failures and the shape of the scores

Every jubarte trial, by outcome:

| | 0.14.0 DeepSeek | 0.14.0 Nemotron | 0.15.0 DeepSeek | 0.16 Harvey | 0.17 Harvey | Muse Spark 1.3 |
|---|---:|---:|---:|---:|---:|---:|
| Trials | 560 | 144 | 147 | 90 | 48 | 140 |
| Graded | 546 | 131 | 134 | 90 | 44 | 140 |
| Agent failed, not graded | 12 (cancelled) | 13 (runtime errors) | 12 (6 cancelled, 3 non-zero exit, 3 runtime errors) | 0 | 0 | 0 |
| Finished, not graded | 2 | 0 | 1 | 0 | 0 | 0 |
| Never started | 0 | 0 | 0 | 0 | 4 | 0 |
| Hit the agent timeout, still graded | 0 | 12 | 0 | 1 | 0 | 33 |
| Scored zero | 22 | 43 | 6 | 0 | 0 | 41 |
| Scored above 0.66 | 147 | 26 | 38 | 89 | 44 | 18 |
| Median score | 0.487 | 0.179 | 0.514 | 0.962 | 0.948 | 0.315 |

The three "finished, not graded" trials are on `redline-s1-t4-g11a`. No trial on that task, in either arm, has a GLM-5.3-Flash grade, so it drops out of every comparison.

Nemotron's median of 0.179 against a mean of 0.307 says most of its trials were poor and a few were good. Of Muse's 41 zeros, 29 are timeouts.

The control arms, for comparison:

- DeepSeek: 1 timeout and 6 zeros in 131 trials.
- Nemotron: 25 timeouts, 8 cancelled and 38 zeros in 160 trials.
- Muse: 78 timeouts, 17 cancelled and 47 zeros in 158 trials.
- 0.17 Harvey: 4 of 48 trials ungraded, the same count as the jubarte arm.

## 6. Time, tokens and money

The session logs of the three DeepSeek and Nemotron cohorts and their controls record every model response: 63,274 of them. Per trial:

| | Model responses | Tool calls | Output tokens (reported) | Input, cached | Input, uncached |
|---|---:|---:|---:|---:|---:|
| DeepSeek control | 69.8 | 69.8 | 44.5k | 2.32M | 114k |
| 0.14.0 DeepSeek | 39.5 | 42.8 | 21.8k | 1.21M | 107k |
| 0.15.0 DeepSeek | 35.8 | 39.3 | 20.4k | 1.05M | 108k |
| Nemotron control (140 tasks) | 101.2 | 102.6 | 72.3k | none reported | 4.49M |
| 0.14.0 Nemotron (12 tasks) | 98.5 | 108.8 | 65.7k | none reported | 4.69M |

With DeepSeek, jubarte halved the number of model responses and with it the cached re-reads of the conversation. Uncached input, the part billed at full price, barely moved (114k to 107k). So the bill fell less than the token count.

Price per trial from the same logs, with uncached input counted once and cache-write surcharges left out (so the Claude figures are a floor). DeepSeek's prices are OpenRouter's for `deepseek/deepseek-v4.1-flash-1017` on 2026-11-22: $0.15 in, $0.003 cached and $0.60 out per million tokens, doubled on weekdays 01:00–04:00 and 06:00–10:00 UTC.

| | DeepSeek on OpenRouter | Weekday peak | Claude Opus 5.5 list ($4, $0.20, $20) |
|---|---:|---:|---:|
| DeepSeek control | $0.051 | $0.102 | $1.81 |
| 0.14.0 DeepSeek | $0.033 (−35%) | $0.066 | $1.11 (−39%) |
| 0.15.0 DeepSeek | $0.032 (−38%) | $0.063 | $1.05 (−42%) |

The Opus column is a hypothetical: it prices the same tokens as if a Claude model had produced them, to show what the saving is worth at frontier prices. No Claude model was the agent in any cohort. Nemotron ran on a local GPU; at OpenRouter's price for it, $0.07 in and $0.20 out per million, a trial costs about $0.33 (Appendix A).

What was actually paid for the DeepSeek cohorts was a flat Synthetic subscription with weekly credits, not per-token billing. The 0.17 Harvey cohort ran on a rented MI355X node.

### All six cohorts, both arms

The headline, on the same tasks as section 1: each task's mean over its graded trials, averaged over the paired tasks. Benchmark's tools → jubarte.

| Cohort | Tasks | API calls | Agent minutes | Inference minutes | Output tokens | Est. cost, OpenRouter | Est. cost, Opus list |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0.14.0 DeepSeek | 130 | 70 → 38 | 18.3 → 10.3 | 17.3 → 9.2 | 44.3k → 21.5k | $0.051 → $0.032 | $1.80 → $1.08 |
| 0.14.0 Nemotron | 12 | 95 → 98 | 30.8 → 24.1 | 28.6 → 20.6 | 63.4k → 65.7k | $0.292 → $0.341 | $17.23 → $20.03 |
| 0.15.0 DeepSeek | 125 | 70 → 35 | 18.4 → 10.1 | 17.3 → 8.8 | 44.4k → 20.2k | $0.051 → $0.031 | $1.81 → $1.04 |
| 0.16 Harvey | 90 | 158 → 133 | 37.2 → 32.4 | 34.0 → 28.1 | 53.3k → 46.5k | $0.132 → $0.120 | $4.87 → $4.35 |
| 0.17 Harvey | 16 | 168 → 159 | 28.4 → 26.6 | n/a | 143.5k → 133.1k | $2.67 → $2.50 | $71.68 → $67.31 |
| Muse Spark 1.3 | 140 | 47 → 34 | 48.8 → 36.1 | n/a → 35.0 | 226.3k → 181.0k | $0.076 → $0.064 | $6.22 → $5.04 |

`scripts/metrics.py` prints this table; the unformatted values are in `data/metrics_paired_by_cohort.csv`. OpenRouter prices are at the base rate; DeepSeek's weekday peak doubles them. Nemotron's and 0.17 Harvey's costs are inflated because their servers reported no caching. Appendix A has every metric per trial, as mean and median, by cohort and by run. Per trial, the two Nemotron arms cover different tasks (140 against 12), so compare arms in this table, not there.

What the logs show:

- **Time is inference.** Where session logs exist, waiting on the model was 85% to 97% of agent working time. The rest (tools, file reads and Word conversion) did not shrink with jubarte: 1.08 minutes in both arms of 0.14.0 DeepSeek, and up in the other three cohorts with logs in both arms (0.15.0 DeepSeek 1.10 to 1.35, Nemotron 2.22 to 3.51, 0.16 Harvey 3.17 to 4.39). The savings came from the model side.
- **For DeepSeek, the saving follows the call count.** Calls fell 45% (0.14.0) and 50% (0.15.0), and inference time fell about as much, at a steady 14 to 15 seconds of model time per call. In 0.17 Harvey, calls fell 5% and time 6%.
- **Nemotron is the exception.** On its 12 tasks, calls rose 4% and the OpenRouter estimate 17%, yet time fell 22%, because model time per call fell from 18.1 to 12.5 seconds. Its jubarte arm pools eleven different drafts against one control run, so this is a lead, not a measured effect.
- **Muse is slow per call.** In its jubarte arm a call took 62 seconds of model time (its control has no session logs), against 12 to 18 seconds for the other models. Muse made fewer calls than any other model, in both arms, and still timed out the most.

A separate harness article, "What Claude Code asks of models that are not Claude", covers why output and thinking behave as they do here, including a fixed output ceiling on DeepSeek responses and a provider report that counts uncached input twice.

## 7. Limits

- **Not interleaved.** See section 2. A provider-side change between arms cannot be ruled out.
- **One control run per task**, so control variance is not measured.
- **Judges differ by cohort.** Each is used in both arms of its cohort (0.16 Harvey's changed model during the run), but a GLM-5.3-Flash score and a gpt-6.1-sol score are not on the same scale. None of the RedlineBench judges is Crosby's own panel, so these scores do not compare with Crosby's leaderboard.
- **The judge is noisy.** Harvey's judge moves about 0.02 between runs. A single task's difference says little; only the cohort average carries weight.
- **The DeepSeek cohort includes its tuning tasks.** Section 3 separates them; the cohort-level figure does not.
- **No frontier model as the agent.** A frontier model may take fewer turns on its own, which could shrink the time saving.
- **Muse's build is unrecorded, and its arms ran in reverse order.**

## 8. Reproduce

Data:

- `data/cohort_trials.csv`: one row per trial in the six cohorts and their controls. It records cohort, arm, job, task, the pairing key, the judge, the single-judge score, minutes and tokens.
- `data/harness_responses.parquet` and `data/harness_requests.csv`: per-response figures for section 6, from the Claude Code session logs.
- `data/trial_metrics.csv`: `cohort_trials.csv` plus, per trial, API calls, inference minutes and tokens split into uncached, cache read and cache write. It is built by `tools/extract_trial_metrics.py` from the session logs and trajectories. `data/metrics_by_cohort.csv` and `data/metrics_by_run.csv` hold the Appendix A means and medians; `data/metrics_paired_by_cohort.csv` holds the section 6 headline. `data/openrouter_models_2026-11-22.json` is the OpenRouter price snapshot.
- Raw trials, public, six cohorts only: [`hf://datasets/arthrod/redline-bench-jubarte-six-cohorts`](https://huggingface.co/datasets/arthrod/redline-bench-jubarte-six-cohorts):
  - `data/trials.parquet` is `data/trial_metrics.csv`, one row per trial.
  - `files/redlinebench.parquet` holds every file of the DeepSeek and Nemotron trials and their controls, session logs included.
  - `files/harvey_016.parquet` holds 0.16 Harvey; `files/harvey_017_*.parquet` hold 0.17 Harvey.
  - `files/muse_jubarte.parquet` and `files/muse_control_trials.parquet` hold Muse Spark 1.3.
- The 140 task definitions: `hf://datasets/arthrod/redline-bench-jubarte-tasks`.

Scores are single-judge:

- For the DeepSeek and Nemotron cohorts, only GLM-5.3-Flash grades count, plus validity-gate zeros.
- For Muse, only gpt-6.1-sol panel grades count, plus validity-gate zeros.
- Where a trial carries grades from other judges, they are ignored.

Commands:

```sh
uv run python scripts/cohorts.py   # sections 1 to 5
uv run python scripts/harness.py   # section 6 per-response tables, and the harness article's
uv run python scripts/metrics.py   # section 6 headline and Appendix A
uv run pytest                      # pins the published figures
```

## 9. Rights

- RedlineBench tasks and documents: Crosby Legal and micro1. Code MIT, data CC-BY-4.0.
- Harvey LAB material: Harvey AI, MIT.
- Trajectories, deliverables and grades from these runs: CC-BY-4.0.

Not affiliated with or endorsed by Crosby, micro1, Harvey, DeepSeek, NVIDIA, Synthetic or Anthropic. The contracts are synthetic benchmark material, and nothing here is legal advice.

## Appendix A. Every metric, aggregated and per run

Each cell is **mean / median per trial**. "Benchmark's tools" is the control arm; "jubarte" is the arm with jubarte. Generated by `scripts/metrics.py` from `data/trial_metrics.csv` (one row per trial). The same figures, unformatted, are in `data/metrics_by_cohort.csv` and `data/metrics_by_run.csv`.

How each field is measured:

- **Score**: the cohort's judge grade, as in section 1. Ungraded trials are left out of the score only.
- **Agent working minutes**: Harbor's `agent_execution` start to finish, from `result.json`. Timed-out trials count at the cap (60 minutes for Muse; 78 of 158 control trials and 33 of 140 jubarte trials reached it), so those medians are censored.
- **Inference minutes**: from the Claude Code session log. For each model response, the time from the last event before it (the prompt or a tool result) to its last streamed line, summed over the trial. It is n/a where only an ATIF trajectory survives (0.17 Harvey, both arms; Muse control), because trajectories carry no tool-result timestamps.
- **API calls**: model responses. In session logs, unique message ids, excluding Claude Code's synthetic messages; in trajectories, the sum of `llm_call_count`.
- **Tokens**: summed from each response's usage. "Input, uncached" plus "Input, cache read" plus "Cache write" equals Harbor's `n_input_tokens` on more than 95% of trials (pinned in `tests/test_metrics.py`).
  - DeepSeek's provider reports every uncached input token a second time as a cache write, so for the DeepSeek cohorts the "Cache write" column repeats "Input, uncached"; it is not extra input.
  - Nemotron (run on a local GPU) and the 0.17 Harvey server (self-hosted on an MI355X) reported no caching at all, so their whole conversation counts as uncached input on every call.
- **Estimated cost**: price times tokens. Uncached input is counted once; DeepSeek's duplicate cache write is not billed. The agent model's price is OpenRouter's, from its public model list on 2026-11-22, per million tokens:
  - DeepSeek V4.1 Flash 1017 (`deepseek/deepseek-v4.1-flash-1017`): $0.15 in, $0.003 cached, $0.60 out. On weekdays 01:00–04:00 and 06:00–10:00 UTC every rate doubles, which gives the "weekday peak" column.
  - Nemotron 3.5 Lightning 30B-A3B (`nvidia/nemotron-3.5-lightning`): $0.07 in, $0.04 cached, $0.20 out.
  - Muse Spark 1.3 Contributor (`meta/muse-spark-1.3-contributor`): $0.10 in, $0.002 cached, $0.20 out.
  - Nemotron and Muse have one rate, so their peak column repeats the base. OpenRouter lists no cache-write price for any of the three.
  - "Claude Opus 5.5 list" ($4 in, $0.20 cached, $5 cache write, $20 out) is hypothetical: it prices the same tokens as if a Claude model had produced them.
  - For Nemotron and 0.17 Harvey, which reported no caching, both prices are inflated, because a provider with prompt caching would bill most of that input at the cached rate.
  - What was actually paid differs again: a flat Synthetic subscription for the DeepSeek cohorts, local GPUs for Nemotron, and a rented node for 0.17 Harvey.
- **Model**: the model id recorded in the trials.

Coverage: trials that never started or left no log have no calls or tokens. The "With …" columns show how many trials each figure rests on. The 0.14.0 DeepSeek and Nemotron jubarte arms pool every tuning job (mostly 12-task runs on the same tuning tasks) with the full runs. Read their aggregated rows with that in mind; the per-run tables separate them.

### A.1 Coverage

| Cohort          | Arm     | Trials | Source      | With API calls | With inference time | Graded |
|-----------------|---------|--------|-------------|----------------|---------------------|--------|
| 0.14.0 DeepSeek | control | 131    | session log | 131            | 131                 | 130    |
| 0.14.0 DeepSeek | jubarte | 560    | session log | 560            | 560                 | 546    |
| 0.14.0 Nemotron | control | 160    | session log | 140            | 140                 | 140    |
| 0.14.0 Nemotron | jubarte | 144    | session log | 131            | 131                 | 131    |
| 0.15.0 DeepSeek | control | 131    | session log | 131            | 131                 | 130    |
| 0.15.0 DeepSeek | jubarte | 147    | session log | 138            | 138                 | 134    |
| 0.16 Harvey     | control | 90     | session log | 90             | 90                  | 90     |
| 0.16 Harvey     | jubarte | 90     | session log | 90             | 90                  | 90     |
| 0.17 Harvey     | control | 48     | trajectory  | 44             | 0                   | 44     |
| 0.17 Harvey     | jubarte | 48     | trajectory  | 44             | 0                   | 44     |
| Muse Spark 1.3  | control | 158    | trajectory  | 140            | 0                   | 140    |
| Muse Spark 1.3  | jubarte | 140    | session log | 140            | 140                 | 140    |

### A.2 Aggregated by cohort: Score, time and API calls

| Cohort          | Arm               | Model                                   | Trials | Score         | Agent working minutes | Inference minutes | API calls |
|-----------------|-------------------|-----------------------------------------|--------|---------------|-----------------------|-------------------|-----------|
| 0.14.0 DeepSeek | benchmark's tools | deepseek-v4.1-flash-1017                | 131    | 0.503 / 0.514 | 18.5 / 15.8           | 17.4 / 14.8       | 70 / 66   |
| 0.14.0 DeepSeek | jubarte           | deepseek-v4.1-flash-1017                | 560    | 0.486 / 0.487 | 10.7 / 10.0           | 9.4 / 8.9         | 39 / 36   |
| 0.14.0 Nemotron | benchmark's tools | nemotron-3.5-lightning-30b-a3b          | 160    | 0.350 / 0.346 | 30.6 / 24.9           | 28.8 / 23.3       | 101 / 92  |
| 0.14.0 Nemotron | jubarte           | nemotron-3.5-lightning-30b-a3b          | 144    | 0.307 / 0.179 | 24.1 / 17.7           | 20.6 / 14.3       | 99 / 82   |
| 0.15.0 DeepSeek | benchmark's tools | deepseek-v4.1-flash-1017                | 131    | 0.503 / 0.514 | 18.5 / 15.8           | 17.4 / 14.8       | 70 / 66   |
| 0.15.0 DeepSeek | jubarte           | deepseek-v4.1-flash-1017                | 147    | 0.492 / 0.514 | 10.0 / 9.5            | 8.8 / 8.3         | 36 / 32   |
| 0.16 Harvey     | benchmark's tools | hf:deepseek-ai/deepseek-v4.1-flash-1017 | 90     | 0.936 / 0.962 | 37.2 / 35.0           | 34.0 / 31.8       | 158 / 153 |
| 0.16 Harvey     | jubarte           | hf:deepseek-ai/deepseek-v4.1-flash-1017 | 90     | 0.941 / 0.962 | 32.4 / 30.6           | 28.1 / 26.8       | 133 / 123 |
| 0.17 Harvey     | benchmark's tools | deepseek-flash-1017                     | 48     | 0.921 / 0.947 | 28.5 / 27.8           | n/a               | 168 / 158 |
| 0.17 Harvey     | jubarte           | deepseek-flash-1017                     | 48     | 0.918 / 0.948 | 26.9 / 25.7           | n/a               | 163 / 153 |
| Muse Spark 1.3  | benchmark's tools | muse-spark-1.3-contributor              | 158    | 0.297 / 0.266 | 48.8 / 60.0           | n/a               | 47 / 40   |
| Muse Spark 1.3  | jubarte           | muse-spark-1.3-contributor              | 140    | 0.316 / 0.315 | 36.1 / 35.3           | 35.0 / 34.2       | 34 / 32   |

### A.3 Aggregated by cohort: Tokens

| Cohort          | Arm               | Model                                   | Trials | Input, uncached         | Input, cache read     | Cache write (as reported) | Output            |
|-----------------|-------------------|-----------------------------------------|--------|-------------------------|-----------------------|---------------------------|-------------------|
| 0.14.0 DeepSeek | benchmark's tools | deepseek-v4.1-flash-1017                | 131    | 113,911 / 112,966       | 2,321,846 / 2,121,519 | 113,911 / 112,966         | 44,509 / 38,152   |
| 0.14.0 DeepSeek | jubarte           | deepseek-v4.1-flash-1017                | 560    | 107,171 / 105,071       | 1,209,805 / 1,114,330 | 107,092 / 104,726         | 21,820 / 21,054   |
| 0.14.0 Nemotron | benchmark's tools | nemotron-3.5-lightning-30b-a3b          | 160    | 4,490,391 / 3,923,036   | 0 / 0                 | 0 / 0                     | 72,256 / 68,118   |
| 0.14.0 Nemotron | jubarte           | nemotron-3.5-lightning-30b-a3b          | 144    | 4,688,562 / 3,805,416   | 0 / 0                 | 0 / 0                     | 65,740 / 50,733   |
| 0.15.0 DeepSeek | benchmark's tools | deepseek-v4.1-flash-1017                | 131    | 113,911 / 112,966       | 2,321,846 / 2,121,519 | 113,911 / 112,966         | 44,509 / 38,152   |
| 0.15.0 DeepSeek | jubarte           | deepseek-v4.1-flash-1017                | 147    | 107,854 / 106,198       | 1,051,054 / 876,228   | 107,854 / 106,198         | 20,371 / 19,192   |
| 0.16 Harvey     | benchmark's tools | hf:deepseek-ai/deepseek-v4.1-flash-1017 | 90     | 475,468 / 470,419       | 9,498,302 / 9,113,882 | 473,728 / 452,009         | 53,256 / 50,118   |
| 0.16 Harvey     | jubarte           | hf:deepseek-ai/deepseek-v4.1-flash-1017 | 90     | 451,424 / 429,468       | 8,047,822 / 7,681,576 | 450,269 / 429,468         | 46,492 / 44,134   |
| 0.17 Harvey     | benchmark's tools | deepseek-flash-1017                     | 48     | 17,268,785 / 16,946,464 | 0 / 0                 | 0 / 0                     | 143,955 / 144,762 |
| 0.17 Harvey     | jubarte           | deepseek-flash-1017                     | 48     | 16,425,151 / 15,763,987 | 0 / 0                 | 0 / 0                     | 134,683 / 128,898 |
| Muse Spark 1.3  | benchmark's tools | muse-spark-1.3-contributor              | 158    | 235,601 / 202,738       | 3,744,578 / 3,085,706 | 0 / 0                     | 226,331 / 228,452 |
| Muse Spark 1.3  | jubarte           | muse-spark-1.3-contributor              | 140    | 220,239 / 184,727       | 2,714,755 / 2,441,670 | 0 / 0                     | 180,984 / 170,598 |

### A.4 Aggregated by cohort: Estimated cost per trial (USD)

| Cohort          | Arm               | Model                                   | Trials | OpenRouter, agent model | OpenRouter, DeepSeek weekday peak | Claude Opus 5.5 list (hypothetical) |
|-----------------|-------------------|-----------------------------------------|--------|-------------------------|-----------------------------------|-------------------------------------|
| 0.14.0 DeepSeek | benchmark's tools | deepseek-v4.1-flash-1017                | 131    | 0.051 / 0.046           | 0.102 / 0.092                     | 1.81 / 1.64                         |
| 0.14.0 DeepSeek | jubarte           | deepseek-v4.1-flash-1017                | 560    | 0.033 / 0.031           | 0.066 / 0.062                     | 1.11 / 1.04                         |
| 0.14.0 Nemotron | benchmark's tools | nemotron-3.5-lightning-30b-a3b          | 160    | 0.329 / 0.289           | 0.329 / 0.289                     | 19.41 / 17.06                       |
| 0.14.0 Nemotron | jubarte           | nemotron-3.5-lightning-30b-a3b          | 144    | 0.341 / 0.277           | 0.341 / 0.277                     | 20.07 / 16.34                       |
| 0.15.0 DeepSeek | benchmark's tools | deepseek-v4.1-flash-1017                | 131    | 0.051 / 0.046           | 0.102 / 0.092                     | 1.81 / 1.64                         |
| 0.15.0 DeepSeek | jubarte           | deepseek-v4.1-flash-1017                | 147    | 0.032 / 0.030           | 0.063 / 0.060                     | 1.05 / 0.97                         |
| 0.16 Harvey     | benchmark's tools | hf:deepseek-ai/deepseek-v4.1-flash-1017 | 90     | 0.132 / 0.130           | 0.264 / 0.260                     | 4.87 / 4.71                         |
| 0.16 Harvey     | jubarte           | hf:deepseek-ai/deepseek-v4.1-flash-1017 | 90     | 0.120 / 0.119           | 0.240 / 0.238                     | 4.35 / 4.21                         |
| 0.17 Harvey     | benchmark's tools | deepseek-flash-1017                     | 48     | 2.677 / 2.630           | 5.353 / 5.260                     | 71.95 / 70.76                       |
| 0.17 Harvey     | jubarte           | deepseek-flash-1017                     | 48     | 2.545 / 2.442           | 5.089 / 4.884                     | 68.39 / 65.55                       |
| Muse Spark 1.3  | benchmark's tools | muse-spark-1.3-contributor              | 158    | 0.076 / 0.078           | 0.076 / 0.078                     | 6.22 / 6.52                         |
| Muse Spark 1.3  | jubarte           | muse-spark-1.3-contributor              | 140    | 0.064 / 0.064           | 0.064 / 0.064                     | 5.04 / 4.91                         |

### A.5 Per run: Score, time and API calls

| Cohort          | Run                                  | Arm               | Model                                   | Trials | Score         | Agent working minutes | Inference minutes | API calls |
|-----------------|--------------------------------------|-------------------|-----------------------------------------|--------|---------------|-----------------------|-------------------|-----------|
| 0.14.0 DeepSeek | deepseek-full-b                      | benchmark's tools | deepseek-v4.1-flash-1017                | 131    | 0.503 / 0.514 | 18.5 / 15.8           | 17.4 / 14.8       | 70 / 66   |
| 0.14.0 DeepSeek | jubarte-ds-v10                       | jubarte           | deepseek-v4.1-flash-1017                | 12     | 0.562 / 0.606 | 13.4 / 13.1           | 11.8 / 11.4       | 44 / 46   |
| 0.14.0 DeepSeek | jubarte-ds-v11                       | jubarte           | deepseek-v4.1-flash-1017                | 12     | 0.548 / 0.558 | 11.1 / 10.8           | 9.9 / 9.3         | 36 / 36   |
| 0.14.0 DeepSeek | jubarte-ds-v12                       | jubarte           | deepseek-v4.1-flash-1017                | 12     | 0.566 / 0.623 | 9.9 / 10.1            | 9.1 / 9.4         | 39 / 32   |
| 0.14.0 DeepSeek | jubarte-ds-v12-rest                  | jubarte           | deepseek-v4.1-flash-1017                | 128    | 0.494 / 0.512 | 9.3 / 9.0             | 8.4 / 8.1         | 37 / 34   |
| 0.14.0 DeepSeek | jubarte-ds-v2                        | jubarte           | deepseek-v4.1-flash-1017                | 12     | 0.570 / 0.603 | 13.4 / 12.8           | 11.8 / 11.9       | 51 / 48   |
| 0.14.0 DeepSeek | jubarte-ds-v3                        | jubarte           | deepseek-v4.1-flash-1017                | 12     | 0.510 / 0.496 | 12.7 / 12.0           | 10.5 / 10.1       | 48 / 50   |
| 0.14.0 DeepSeek | jubarte-ds-v4                        | jubarte           | deepseek-v4.1-flash-1017                | 12     | 0.573 / 0.518 | 9.8 / 9.8             | 8.2 / 8.1         | 33 / 28   |
| 0.14.0 DeepSeek | jubarte-ds-v4-b                      | jubarte           | deepseek-v4.1-flash-1017                | 6      | 0.531 / 0.558 | 16.1 / 16.3           | 14.5 / 14.8       | 59 / 60   |
| 0.14.0 DeepSeek | jubarte-ds-v5                        | jubarte           | deepseek-v4.1-flash-1017                | 12     | 0.523 / 0.505 | 13.1 / 12.4           | 11.2 / 11.0       | 48 / 47   |
| 0.14.0 DeepSeek | jubarte-ds-v7                        | jubarte           | deepseek-v4.1-flash-1017                | 12     | 0.527 / 0.505 | 12.5 / 12.1           | 10.1 / 10.1       | 47 / 44   |
| 0.14.0 DeepSeek | jubarte-ds-v8                        | jubarte           | deepseek-v4.1-flash-1017                | 12     | 0.562 / 0.622 | 14.8 / 12.0           | 11.9 / 9.6        | 51 / 40   |
| 0.14.0 DeepSeek | jubarte-ds-v9                        | jubarte           | deepseek-v4.1-flash-1017                | 12     | 0.576 / 0.577 | 12.0 / 10.1           | 9.5 / 8.8         | 43 / 38   |
| 0.14.0 DeepSeek | jubarte-ds-v9-rest                   | jubarte           | deepseek-v4.1-flash-1017                | 128    | 0.465 / 0.487 | 11.1 / 10.2           | 9.8 / 8.9         | 42 / 36   |
| 0.14.0 DeepSeek | jubarte-study-v13                    | jubarte           | deepseek-v4.1-flash-1017                | 33     | 0.453 / 0.387 | 8.4 / 8.3             | 7.4 / 7.2         | 32 / 29   |
| 0.14.0 DeepSeek | jubarte-study-v14                    | jubarte           | deepseek-v4.1-flash-1017                | 33     | 0.475 / 0.414 | 8.9 / 8.5             | 8.2 / 7.7         | 37 / 33   |
| 0.14.0 DeepSeek | jubarte-study-v14-rest               | jubarte           | deepseek-v4.1-flash-1017                | 98     | 0.476 / 0.502 | 11.0 / 10.6           | 9.9 / 9.6         | 36 / 34   |
| 0.14.0 DeepSeek | jubarte-study-v15                    | jubarte           | deepseek-v4.1-flash-1017                | 14     | 0.213 / 0.170 | 10.7 / 9.9            | 8.8 / 8.6         | 36 / 37   |
| 0.14.0 Nemotron | nemotron-full-5090                   | benchmark's tools | nemotron-3.5-lightning-30b-a3b          | 160    | 0.350 / 0.346 | 30.6 / 24.9           | 28.8 / 23.3       | 101 / 92  |
| 0.14.0 Nemotron | jubarte-v1                           | jubarte           | nemotron-3.5-lightning-30b-a3b          | 12     | 0.059 / 0.000 | 38.0 / 40.5           | 33.6 / 34.2       | 75 / 74   |
| 0.14.0 Nemotron | jubarte-v10                          | jubarte           | nemotron-3.5-lightning-30b-a3b          | 12     | 0.368 / 0.316 | 19.3 / 17.3           | 16.0 / 14.0       | 125 / 93  |
| 0.14.0 Nemotron | jubarte-v11                          | jubarte           | nemotron-3.5-lightning-30b-a3b          | 12     | 0.360 / 0.316 | 11.1 / 9.1            | 9.1 / 7.4         | 67 / 58   |
| 0.14.0 Nemotron | jubarte-v2                           | jubarte           | nemotron-3.5-lightning-30b-a3b          | 12     | 0.349 / 0.190 | 46.1 / 48.3           | 42.4 / 46.5       | 79 / 87   |
| 0.14.0 Nemotron | jubarte-v3                           | jubarte           | nemotron-3.5-lightning-30b-a3b          | 24     | 0.351 / 0.291 | 42.0 / 46.5           | 37.5 / 40.0       | 83 / 89   |
| 0.14.0 Nemotron | jubarte-v4                           | jubarte           | nemotron-3.5-lightning-30b-a3b          | 12     | 0.308 / 0.305 | 28.6 / 24.3           | 24.6 / 21.2       | 140 / 96  |
| 0.14.0 Nemotron | jubarte-v5                           | jubarte           | nemotron-3.5-lightning-30b-a3b          | 12     | 0.272 / 0.107 | 17.4 / 16.7           | 13.2 / 12.7       | 127 / 66  |
| 0.14.0 Nemotron | jubarte-v6-v3rep                     | jubarte           | nemotron-3.5-lightning-30b-a3b          | 12     | 0.331 / 0.144 | 15.2 / 12.5           | 12.2 / 10.5       | 84 / 58   |
| 0.14.0 Nemotron | jubarte-v7                           | jubarte           | nemotron-3.5-lightning-30b-a3b          | 12     | 0.255 / 0.171 | 16.2 / 15.9           | 13.5 / 12.8       | 89 / 90   |
| 0.14.0 Nemotron | jubarte-v8                           | jubarte           | nemotron-3.5-lightning-30b-a3b          | 12     | 0.303 / 0.180 | 16.3 / 13.4           | 12.9 / 10.5       | 109 / 73  |
| 0.14.0 Nemotron | jubarte-v9                           | jubarte           | nemotron-3.5-lightning-30b-a3b          | 12     | 0.425 / 0.479 | 16.3 / 16.4           | 13.0 / 12.9       | 105 / 97  |
| 0.15.0 DeepSeek | deepseek-full-b                      | benchmark's tools | deepseek-v4.1-flash-1017                | 131    | 0.503 / 0.514 | 18.5 / 15.8           | 17.4 / 14.8       | 70 / 66   |
| 0.15.0 DeepSeek | jubarte-study-v14b-015               | jubarte           | deepseek-v4.1-flash-1017                | 141    | 0.485 / 0.512 | 10.1 / 9.6            | 8.9 / 8.3         | 36 / 32   |
| 0.15.0 DeepSeek | jubarte-study-v14b-015-retry         | jubarte           | deepseek-v4.1-flash-1017                | 6      | 0.644 / 0.656 | 8.1 / 7.1             | 7.7 / 6.8         | 27 / 26   |
| 0.16 Harvey     | harvey-hub-ab                        | benchmark's tools | hf:deepseek-ai/deepseek-v4.1-flash-1017 | 90     | 0.936 / 0.962 | 37.2 / 35.0           | 34.0 / 31.8       | 158 / 153 |
| 0.16 Harvey     | harvey-hub-ab                        | jubarte           | hf:deepseek-ai/deepseek-v4.1-flash-1017 | 90     | 0.941 / 0.962 | 32.4 / 30.6           | 28.1 / 26.8       | 133 / 123 |
| 0.17 Harvey     | harvey-0.17                          | benchmark's tools | deepseek-flash-1017                     | 48     | 0.921 / 0.947 | 28.5 / 27.8           | n/a               | 168 / 158 |
| 0.17 Harvey     | harvey-0.17                          | jubarte           | deepseek-flash-1017                     | 48     | 0.918 / 0.948 | 26.9 / 25.7           | n/a               | 163 / 153 |
| Muse Spark 1.3  | muse-1-3-contributor-total-ooriginal | benchmark's tools | muse-spark-1.3-contributor              | 158    | 0.297 / 0.266 | 48.8 / 60.0           | n/a               | 47 / 40   |
| Muse Spark 1.3  | muse-1-3-contributor-total           | jubarte           | muse-spark-1.3-contributor              | 140    | 0.316 / 0.315 | 36.1 / 35.3           | 35.0 / 34.2       | 34 / 32   |

### A.6 Per run: Tokens

| Cohort          | Run                                  | Arm               | Model                                   | Trials | Input, uncached         | Input, cache read     | Cache write (as reported) | Output            |
|-----------------|--------------------------------------|-------------------|-----------------------------------------|--------|-------------------------|-----------------------|---------------------------|-------------------|
| 0.14.0 DeepSeek | deepseek-full-b                      | benchmark's tools | deepseek-v4.1-flash-1017                | 131    | 113,911 / 112,966       | 2,321,846 / 2,121,519 | 113,911 / 112,966         | 44,509 / 38,152   |
| 0.14.0 DeepSeek | jubarte-ds-v10                       | jubarte           | deepseek-v4.1-flash-1017                | 12     | 119,837 / 121,702       | 1,403,780 / 1,358,346 | 119,837 / 121,702         | 25,495 / 24,626   |
| 0.14.0 DeepSeek | jubarte-ds-v11                       | jubarte           | deepseek-v4.1-flash-1017                | 12     | 91,086 / 86,815         | 1,136,539 / 1,118,630 | 91,086 / 86,815           | 24,040 / 22,438   |
| 0.14.0 DeepSeek | jubarte-ds-v12                       | jubarte           | deepseek-v4.1-flash-1017                | 12     | 69,976 / 56,812         | 1,406,476 / 1,181,506 | 69,976 / 56,812           | 21,047 / 20,530   |
| 0.14.0 DeepSeek | jubarte-ds-v12-rest                  | jubarte           | deepseek-v4.1-flash-1017                | 128    | 81,196 / 78,560         | 1,242,817 / 1,146,944 | 81,196 / 78,560           | 20,895 / 20,428   |
| 0.14.0 DeepSeek | jubarte-ds-v2                        | jubarte           | deepseek-v4.1-flash-1017                | 12     | 167,026 / 136,740       | 1,558,677 / 1,440,351 | 167,026 / 136,740         | 25,826 / 26,314   |
| 0.14.0 DeepSeek | jubarte-ds-v3                        | jubarte           | deepseek-v4.1-flash-1017                | 12     | 134,653 / 123,930       | 1,352,336 / 1,370,042 | 134,653 / 123,930         | 24,966 / 24,004   |
| 0.14.0 DeepSeek | jubarte-ds-v4                        | jubarte           | deepseek-v4.1-flash-1017                | 12     | 103,892 / 111,454       | 919,884 / 741,767     | 103,892 / 111,454         | 19,129 / 18,302   |
| 0.14.0 DeepSeek | jubarte-ds-v4-b                      | jubarte           | deepseek-v4.1-flash-1017                | 6      | 153,251 / 155,851       | 1,568,643 / 1,381,120 | 153,251 / 155,851         | 29,949 / 31,373   |
| 0.14.0 DeepSeek | jubarte-ds-v5                        | jubarte           | deepseek-v4.1-flash-1017                | 12     | 137,671 / 132,712       | 1,441,497 / 1,326,938 | 137,671 / 132,712         | 26,338 / 26,179   |
| 0.14.0 DeepSeek | jubarte-ds-v7                        | jubarte           | deepseek-v4.1-flash-1017                | 12     | 126,481 / 118,509       | 1,392,521 / 1,383,347 | 122,807 / 118,509         | 23,407 / 23,598   |
| 0.14.0 DeepSeek | jubarte-ds-v8                        | jubarte           | deepseek-v4.1-flash-1017                | 12     | 162,263 / 139,994       | 1,437,417 / 1,271,654 | 162,263 / 139,994         | 26,761 / 23,242   |
| 0.14.0 DeepSeek | jubarte-ds-v9                        | jubarte           | deepseek-v4.1-flash-1017                | 12     | 145,061 / 129,852       | 1,221,815 / 1,051,254 | 145,061 / 129,852         | 22,538 / 21,127   |
| 0.14.0 DeepSeek | jubarte-ds-v9-rest                   | jubarte           | deepseek-v4.1-flash-1017                | 128    | 109,401 / 102,497       | 1,296,661 / 1,152,226 | 109,401 / 102,497         | 23,241 / 21,758   |
| 0.14.0 DeepSeek | jubarte-study-v13                    | jubarte           | deepseek-v4.1-flash-1017                | 33     | 89,856 / 92,648         | 911,850 / 904,601     | 89,856 / 92,648           | 18,051 / 17,640   |
| 0.14.0 DeepSeek | jubarte-study-v14                    | jubarte           | deepseek-v4.1-flash-1017                | 33     | 89,526 / 84,876         | 1,154,221 / 896,139   | 89,526 / 84,876           | 19,079 / 17,818   |
| 0.14.0 DeepSeek | jubarte-study-v14-rest               | jubarte           | deepseek-v4.1-flash-1017                | 98     | 124,554 / 120,127       | 1,021,333 / 930,944   | 124,554 / 120,127         | 20,595 / 19,638   |
| 0.14.0 DeepSeek | jubarte-study-v15                    | jubarte           | deepseek-v4.1-flash-1017                | 14     | 105,621 / 104,044       | 1,107,373 / 1,148,592 | 105,621 / 104,044         | 19,432 / 20,038   |
| 0.14.0 Nemotron | nemotron-full-5090                   | benchmark's tools | nemotron-3.5-lightning-30b-a3b          | 160    | 4,490,391 / 3,923,036   | 0 / 0                 | 0 / 0                     | 72,256 / 68,118   |
| 0.14.0 Nemotron | jubarte-v1                           | jubarte           | nemotron-3.5-lightning-30b-a3b          | 12     | 3,458,553 / 3,520,300   | 0 / 0                 | 0 / 0                     | 57,333 / 50,352   |
| 0.14.0 Nemotron | jubarte-v10                          | jubarte           | nemotron-3.5-lightning-30b-a3b          | 12     | 5,925,340 / 3,759,533   | 0 / 0                 | 0 / 0                     | 73,897 / 52,056   |
| 0.14.0 Nemotron | jubarte-v11                          | jubarte           | nemotron-3.5-lightning-30b-a3b          | 12     | 3,219,857 / 2,580,604   | 0 / 0                 | 0 / 0                     | 47,407 / 30,440   |
| 0.14.0 Nemotron | jubarte-v2                           | jubarte           | nemotron-3.5-lightning-30b-a3b          | 12     | 3,692,963 / 3,777,102   | 0 / 0                 | 0 / 0                     | 52,992 / 56,234   |
| 0.14.0 Nemotron | jubarte-v3                           | jubarte           | nemotron-3.5-lightning-30b-a3b          | 24     | 4,007,285 / 4,496,859   | 0 / 0                 | 0 / 0                     | 53,955 / 51,392   |
| 0.14.0 Nemotron | jubarte-v4                           | jubarte           | nemotron-3.5-lightning-30b-a3b          | 12     | 6,964,181 / 4,817,573   | 0 / 0                 | 0 / 0                     | 107,000 / 68,858  |
| 0.14.0 Nemotron | jubarte-v5                           | jubarte           | nemotron-3.5-lightning-30b-a3b          | 12     | 6,034,250 / 3,407,897   | 0 / 0                 | 0 / 0                     | 65,042 / 52,600   |
| 0.14.0 Nemotron | jubarte-v6-v3rep                     | jubarte           | nemotron-3.5-lightning-30b-a3b          | 12     | 3,961,283 / 2,672,285   | 0 / 0                 | 0 / 0                     | 72,152 / 43,512   |
| 0.14.0 Nemotron | jubarte-v7                           | jubarte           | nemotron-3.5-lightning-30b-a3b          | 12     | 4,233,070 / 4,147,826   | 0 / 0                 | 0 / 0                     | 64,562 / 53,342   |
| 0.14.0 Nemotron | jubarte-v8                           | jubarte           | nemotron-3.5-lightning-30b-a3b          | 12     | 5,236,906 / 3,399,830   | 0 / 0                 | 0 / 0                     | 71,182 / 44,939   |
| 0.14.0 Nemotron | jubarte-v9                           | jubarte           | nemotron-3.5-lightning-30b-a3b          | 12     | 4,783,718 / 4,477,614   | 0 / 0                 | 0 / 0                     | 56,638 / 53,068   |
| 0.15.0 DeepSeek | deepseek-full-b                      | benchmark's tools | deepseek-v4.1-flash-1017                | 131    | 113,911 / 112,966       | 2,321,846 / 2,121,519 | 113,911 / 112,966         | 44,509 / 38,152   |
| 0.15.0 DeepSeek | jubarte-study-v14b-015               | jubarte           | deepseek-v4.1-flash-1017                | 141    | 109,934 / 106,946       | 1,061,625 / 889,320   | 109,934 / 106,946         | 20,471 / 19,274   |
| 0.15.0 DeepSeek | jubarte-study-v14b-015-retry         | jubarte           | deepseek-v4.1-flash-1017                | 6      | 62,076 / 52,484         | 818,484 / 852,465     | 62,076 / 52,484           | 18,181 / 15,576   |
| 0.16 Harvey     | harvey-hub-ab                        | benchmark's tools | hf:deepseek-ai/deepseek-v4.1-flash-1017 | 90     | 475,468 / 470,419       | 9,498,302 / 9,113,882 | 473,728 / 452,009         | 53,256 / 50,118   |
| 0.16 Harvey     | harvey-hub-ab                        | jubarte           | hf:deepseek-ai/deepseek-v4.1-flash-1017 | 90     | 451,424 / 429,468       | 8,047,822 / 7,681,576 | 450,269 / 429,468         | 46,492 / 44,134   |
| 0.17 Harvey     | harvey-0.17                          | benchmark's tools | deepseek-flash-1017                     | 48     | 17,268,785 / 16,946,464 | 0 / 0                 | 0 / 0                     | 143,955 / 144,762 |
| 0.17 Harvey     | harvey-0.17                          | jubarte           | deepseek-flash-1017                     | 48     | 16,425,151 / 15,763,987 | 0 / 0                 | 0 / 0                     | 134,683 / 128,898 |
| Muse Spark 1.3  | muse-1-3-contributor-total-ooriginal | benchmark's tools | muse-spark-1.3-contributor              | 158    | 235,601 / 202,738       | 3,744,578 / 3,085,706 | 0 / 0                     | 226,331 / 228,452 |
| Muse Spark 1.3  | muse-1-3-contributor-total           | jubarte           | muse-spark-1.3-contributor              | 140    | 220,239 / 184,727       | 2,714,755 / 2,441,670 | 0 / 0                     | 180,984 / 170,598 |

### A.7 Per run: Estimated cost per trial (USD)

| Cohort          | Run                                  | Arm               | Model                                   | Trials | OpenRouter, agent model | OpenRouter, DeepSeek weekday peak | Claude Opus 5.5 list (hypothetical) |
|-----------------|--------------------------------------|-------------------|-----------------------------------------|--------|-------------------------|-----------------------------------|-------------------------------------|
| 0.14.0 DeepSeek | deepseek-full-b                      | benchmark's tools | deepseek-v4.1-flash-1017                | 131    | 0.051 / 0.046           | 0.102 / 0.092                     | 1.81 / 1.64                         |
| 0.14.0 DeepSeek | jubarte-ds-v10                       | jubarte           | deepseek-v4.1-flash-1017                | 12     | 0.037 / 0.038           | 0.075 / 0.076                     | 1.27 / 1.26                         |
| 0.14.0 DeepSeek | jubarte-ds-v11                       | jubarte           | deepseek-v4.1-flash-1017                | 12     | 0.031 / 0.031           | 0.063 / 0.061                     | 1.07 / 1.09                         |
| 0.14.0 DeepSeek | jubarte-ds-v12                       | jubarte           | deepseek-v4.1-flash-1017                | 12     | 0.027 / 0.027           | 0.055 / 0.054                     | 0.98 / 1.01                         |
| 0.14.0 DeepSeek | jubarte-ds-v12-rest                  | jubarte           | deepseek-v4.1-flash-1017                | 128    | 0.028 / 0.027           | 0.057 / 0.053                     | 0.99 / 0.92                         |
| 0.14.0 DeepSeek | jubarte-ds-v2                        | jubarte           | deepseek-v4.1-flash-1017                | 12     | 0.045 / 0.040           | 0.090 / 0.081                     | 1.50 / 1.36                         |
| 0.14.0 DeepSeek | jubarte-ds-v3                        | jubarte           | deepseek-v4.1-flash-1017                | 12     | 0.039 / 0.039           | 0.078 / 0.077                     | 1.31 / 1.29                         |
| 0.14.0 DeepSeek | jubarte-ds-v4                        | jubarte           | deepseek-v4.1-flash-1017                | 12     | 0.030 / 0.032           | 0.060 / 0.063                     | 0.98 / 1.06                         |
| 0.14.0 DeepSeek | jubarte-ds-v4-b                      | jubarte           | deepseek-v4.1-flash-1017                | 6      | 0.046 / 0.046           | 0.091 / 0.093                     | 1.53 / 1.53                         |
| 0.14.0 DeepSeek | jubarte-ds-v5                        | jubarte           | deepseek-v4.1-flash-1017                | 12     | 0.041 / 0.036           | 0.082 / 0.072                     | 1.37 / 1.29                         |
| 0.14.0 DeepSeek | jubarte-ds-v7                        | jubarte           | deepseek-v4.1-flash-1017                | 12     | 0.037 / 0.036           | 0.074 / 0.073                     | 1.25 / 1.27                         |
| 0.14.0 DeepSeek | jubarte-ds-v8                        | jubarte           | deepseek-v4.1-flash-1017                | 12     | 0.045 / 0.038           | 0.089 / 0.076                     | 1.47 / 1.25                         |
| 0.14.0 DeepSeek | jubarte-ds-v9                        | jubarte           | deepseek-v4.1-flash-1017                | 12     | 0.039 / 0.038           | 0.078 / 0.075                     | 1.28 / 1.20                         |
| 0.14.0 DeepSeek | jubarte-ds-v9-rest                   | jubarte           | deepseek-v4.1-flash-1017                | 128    | 0.034 / 0.032           | 0.068 / 0.064                     | 1.16 / 1.09                         |
| 0.14.0 DeepSeek | jubarte-study-v13                    | jubarte           | deepseek-v4.1-flash-1017                | 33     | 0.027 / 0.028           | 0.054 / 0.056                     | 0.90 / 0.97                         |
| 0.14.0 DeepSeek | jubarte-study-v14                    | jubarte           | deepseek-v4.1-flash-1017                | 33     | 0.028 / 0.026           | 0.057 / 0.052                     | 0.97 / 0.91                         |
| 0.14.0 DeepSeek | jubarte-study-v14-rest               | jubarte           | deepseek-v4.1-flash-1017                | 98     | 0.034 / 0.032           | 0.068 / 0.065                     | 1.11 / 1.06                         |
| 0.14.0 DeepSeek | jubarte-study-v15                    | jubarte           | deepseek-v4.1-flash-1017                | 14     | 0.031 / 0.030           | 0.062 / 0.060                     | 1.03 / 0.98                         |
| 0.14.0 Nemotron | nemotron-full-5090                   | benchmark's tools | nemotron-3.5-lightning-30b-a3b          | 160    | 0.329 / 0.289           | 0.329 / 0.289                     | 19.41 / 17.06                       |
| 0.14.0 Nemotron | jubarte-v1                           | jubarte           | nemotron-3.5-lightning-30b-a3b          | 12     | 0.254 / 0.262           | 0.254 / 0.262                     | 14.98 / 15.61                       |
| 0.14.0 Nemotron | jubarte-v10                          | jubarte           | nemotron-3.5-lightning-30b-a3b          | 12     | 0.430 / 0.271           | 0.430 / 0.271                     | 25.18 / 15.84                       |
| 0.14.0 Nemotron | jubarte-v11                          | jubarte           | nemotron-3.5-lightning-30b-a3b          | 12     | 0.235 / 0.188           | 0.235 / 0.188                     | 13.83 / 11.10                       |
| 0.14.0 Nemotron | jubarte-v2                           | jubarte           | nemotron-3.5-lightning-30b-a3b          | 12     | 0.269 / 0.277           | 0.269 / 0.277                     | 15.83 / 16.42                       |
| 0.14.0 Nemotron | jubarte-v3                           | jubarte           | nemotron-3.5-lightning-30b-a3b          | 24     | 0.291 / 0.329           | 0.291 / 0.329                     | 17.11 / 19.39                       |
| 0.14.0 Nemotron | jubarte-v4                           | jubarte           | nemotron-3.5-lightning-30b-a3b          | 12     | 0.509 / 0.347           | 0.509 / 0.347                     | 30.00 / 20.29                       |
| 0.14.0 Nemotron | jubarte-v5                           | jubarte           | nemotron-3.5-lightning-30b-a3b          | 12     | 0.435 / 0.248           | 0.435 / 0.248                     | 25.44 / 14.62                       |
| 0.14.0 Nemotron | jubarte-v6-v3rep                     | jubarte           | nemotron-3.5-lightning-30b-a3b          | 12     | 0.292 / 0.196           | 0.292 / 0.196                     | 17.29 / 11.62                       |
| 0.14.0 Nemotron | jubarte-v7                           | jubarte           | nemotron-3.5-lightning-30b-a3b          | 12     | 0.309 / 0.302           | 0.309 / 0.302                     | 18.22 / 17.78                       |
| 0.14.0 Nemotron | jubarte-v8                           | jubarte           | nemotron-3.5-lightning-30b-a3b          | 12     | 0.381 / 0.247           | 0.381 / 0.247                     | 22.37 / 14.45                       |
| 0.14.0 Nemotron | jubarte-v9                           | jubarte           | nemotron-3.5-lightning-30b-a3b          | 12     | 0.346 / 0.324           | 0.346 / 0.324                     | 20.27 / 18.93                       |
| 0.15.0 DeepSeek | deepseek-full-b                      | benchmark's tools | deepseek-v4.1-flash-1017                | 131    | 0.051 / 0.046           | 0.102 / 0.092                     | 1.81 / 1.64                         |
| 0.15.0 DeepSeek | jubarte-study-v14b-015               | jubarte           | deepseek-v4.1-flash-1017                | 141    | 0.032 / 0.030           | 0.064 / 0.061                     | 1.06 / 0.98                         |
| 0.15.0 DeepSeek | jubarte-study-v14b-015-retry         | jubarte           | deepseek-v4.1-flash-1017                | 6      | 0.023 / 0.022           | 0.045 / 0.043                     | 0.78 / 0.72                         |
| 0.16 Harvey     | harvey-hub-ab                        | benchmark's tools | hf:deepseek-ai/deepseek-v4.1-flash-1017 | 90     | 0.132 / 0.130           | 0.264 / 0.260                     | 4.87 / 4.71                         |
| 0.16 Harvey     | harvey-hub-ab                        | jubarte           | hf:deepseek-ai/deepseek-v4.1-flash-1017 | 90     | 0.120 / 0.119           | 0.240 / 0.238                     | 4.35 / 4.21                         |
| 0.17 Harvey     | harvey-0.17                          | benchmark's tools | deepseek-flash-1017                     | 48     | 2.677 / 2.630           | 5.353 / 5.260                     | 71.95 / 70.76                       |
| 0.17 Harvey     | harvey-0.17                          | jubarte           | deepseek-flash-1017                     | 48     | 2.545 / 2.442           | 5.089 / 4.884                     | 68.39 / 65.55                       |
| Muse Spark 1.3  | muse-1-3-contributor-total-ooriginal | benchmark's tools | muse-spark-1.3-contributor              | 158    | 0.076 / 0.078           | 0.076 / 0.078                     | 6.22 / 6.52                         |
| Muse Spark 1.3  | muse-1-3-contributor-total           | jubarte           | muse-spark-1.3-contributor              | 140    | 0.064 / 0.064           | 0.064 / 0.064                     | 5.04 / 4.91                         |
