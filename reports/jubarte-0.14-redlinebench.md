# jubarte 0.14 on RedlineBench: no score difference detected, about half the work

Report date: 2026-11-22. Scope: every RedlineBench run made with the jubarte 0.14.0 binary, against the benchmark's own Python document scripts, plus the runs needed to read them (the controls, and the one 0.15.0 job that the public dataset card currently uses as its headline).

Disclosure: Arthur Souza Rodrigues writes jubarte (Jandira Technologies) and ran every trial in this report. RedlineBench is by Crosby Legal and micro1; no one at Crosby, micro1, DeepSeek or Synthetic reviewed this report.

## 1. The answer, in one table

The setup:

- **Agent:** DeepSeek-V4.1-Flash-1017 inside Claude Code 2.1.310, effort high.
- **Control:** the benchmark's bundled `contract-redliner` skill and Python docx scripts.
- **jubarte arm:** the jubarte 0.14.0 binary with skill iteration v12.
- **Tasks:** the 127 RedlineBench tasks that were never used to tune the skill (the held-out set; the other 12 were the development set, section 4).
- **Grading:** paired by task, each task graded by GLM-5.3-Flash with the benchmark's rubric.

| Per task, 127 held-out tasks | Control | jubarte 0.14 | Change |
|---|---:|---:|---:|
| Score (0 to 1) | 0.491 | 0.495 | +0.004 (95% CI −0.026 to +0.034) |
| Tasks better / worse / equal | | 48 / 40 / 39 | |
| Input tokens | 2.61 M | 1.40 M | −46% |
| of which not cached | 232 k | 163 k | −30% |
| Output tokens | 44.5 k | 20.8 k | −53% |
| Agent minutes | 18.5 | 9.2 | −50% |
| Agent turns | 71 | 37 | −48% |
| Price at Claude Opus 5.5 list | $2.29 | $1.32 | −43% |
| Price at DeepSeek list (peak) | $0.137 | $0.081 | −41% |

Reading: no score difference was detected; the interval runs from 0.026 below to 0.034 above the control. The agent did the same job with about half the turns, half the time and half the output. Nothing here shows jubarte improving the legal quality of a redline.

Notes on the table:

- The interval is a task bootstrap (10,000 draws, seed 20261122) of the per-task differences.
- Prices apply today's list rates to the recorded tokens, with cache reads at the cache rate (section 6).
- All 139 graded tasks, development set included: 0.493 vs 0.501 (+0.008, −0.020 to +0.035), with the same token and time ratios.
- `FACTS.md` in `redline-reports` reports this run as 0.489 vs 0.493. The 0.002 gap is how the 47 trials that were graded twice are combined: this report averages both grades.

## 2. It was not one run

The table above compares one run per task per arm. Getting there took 30 jobs and 716 trials on the 0.14.0 binary alone.

| | 0.14 arms | DeepSeek control | Nemotron control | Whole RedlineBench archive |
|---|---:|---:|---:|---:|
| Trial directories with a result | 716 | 178 | 170 | 1,357 |
| Jobs | 30 | 3 | 4 | 49 |
| Tasks covered | 140 | 140 | 140 | 140 |
| First start to last finish (UTC) | Oct 26 12:33 to Oct 30 15:46 | Oct 27 21:16 to Oct 28 05:13 | Oct 25 07:52 to Oct 26 12:32 | Oct 25 05:25 to Oct 31 02:05 |
| Summed trial hours | 157.8 | 45.5 | 86.5 | 414.5 |
| Input tokens | 1.43 B | 368 M | 794 M | 3.29 B |
| of which cache reads | 677 M | 334 M | 0 reported | 1.16 B |
| Output tokens | 21.1 M | 6.41 M | 12.5 M | 46.2 M |
| Agent turns | 35,496 | 10,100 | 18,049 | 78,524 |
| Tool calls | 38,811 | 10,107 | 18,275 | 82,572 |
| Trials graded | 688 | 139 | 140 | 1,212 |

Runs per task on 0.14 ranged from 2 to 27 (median 3); across the whole archive, 4 to 42 (median 7.5). The 12 tasks used to develop the skill carry most of the repeats.

What the 716 were:

- 12 skill iterations on Nemotron 3.5 Lightning 30B-A3B (`jubarte-v1` to `jubarte-v12-boxdown`), 12 tasks each, on an RTX 5090.
- 10 iterations on DeepSeek-V4.1-Flash (`jubarte-ds-v2` to `jubarte-ds-v12`), 12 tasks each.
- Two of those carried to the other 128 tasks (`ds-v9-rest`, `ds-v12-rest`).
- A study pass (`jubarte-study-v13`, `v14`, `v14-rest`, `v15`).
- Failures kept on purpose: a full disk (`jubarte-v3-diskfull`), a memory kill (`_aborted-jubarte-ds-v9-memkill`), a Docker image deleted mid-run (`_failed-deepseek-full-dockerprune`, control side).

## 3. Three full-length 0.14 arms, one 0.15 arm

| Arm (binary) | Paired tasks | Control | jubarte | Difference (95% CI) | Input / task | Minutes / task | Turns / task |
|---|---:|---:|---:|---|---:|---:|---:|
| ds-v9 (0.14.0) | 139 | 0.493 | 0.476 | −0.017 (−0.047 to +0.012) | 1.51 M vs 2.57 M | 11.2 vs 18.6 | 42 vs 70 |
| ds-v12 (0.14.0) | 139 | 0.493 | 0.501 | +0.008 (−0.020 to +0.035) | 1.41 M vs 2.57 M | 9.3 vs 18.6 | 38 vs 70 |
| study-v14 (0.14.0) | 125 | 0.474 | 0.477 | +0.003 (−0.021 to +0.027) | 1.34 M vs 2.62 M | 10.8 vs 18.6 | 38 vs 72 |
| study-v14b (0.15.0) | 134 | 0.493 | 0.492 | −0.000 (−0.025 to +0.024) | 1.28 M vs 2.60 M | 10.4 vs 18.6 | 36 vs 71 |

On the held-out tasks alone:

- ds-v12: +0.004 (−0.026 to +0.034), 127 tasks.
- ds-v9: −0.024 (−0.056 to +0.007), 127 tasks.
- study-v14: +0.002 (−0.025 to +0.028), 113 tasks (`jubarte-study-v14` and `v14-rest` together, minus the 12 development tasks; the earlier figure of +0.020 on 92 tasks counted `v14-rest` alone).

Two short study arms are not in the table. `jubarte-study-v13` (0.14.0, 33 tasks, 12 of them development tasks) scored lower: 0.455 against 0.523, −0.068 (−0.120 to −0.019), 7 wins and 16 losses, while still cutting time (8.4 against 19.6 minutes) and input (1.09 M against 2.65 M). It is the one arm whose interval excludes zero. `jubarte-study-v15` (14 tasks) came in at −0.044 (−0.107 to +0.029).

Per-task scores for every arm in this section, the table rows included, are in `data/task_pairs.csv`; `uv run scripts/paired_bootstrap.py` recomputes each score, difference, interval and win/loss count above. The token, time and turn figures in sections 1 and 3 come from `data/deepseek_pairs.csv`, which has a row for each arm above, the held-out ones included. The interval bounds are Monte Carlo estimates and move by up to about 0.003 with the seed; no conclusion changes.

No full-length arm showed a score difference whose interval excluded zero. No equivalence margin was set or tested, so the claim is "no difference detected", not "equal". Every arm cut input tokens by 41% to 51% and agent time by 40% to 50%. The efficiency result repeats across three skill versions and two binaries.

The arms were not interleaved. The control ran from 27 October 21:16 to 28 October 05:13 UTC; the jubarte arms ran from 28 to 31 October (ds-v12-rest on 30 October). Model, harness, brief and grader were pinned, but a provider-side change between those days cannot be ruled out, so the time and token savings are an observed difference between arms run days apart, not a controlled causal estimate.

The public dataset card's headline (0.494 vs 0.492 on 134 tasks) is the 0.15.0 row. Its 0.494 takes the later grade for the five control trials graded twice; averaging both grades, as this table does, gives 0.493 (the first grades alone give 0.491). This report's headline is the ds-v12 row, the best-documented 0.14.0 arm.

## 4. The development set overstated the gain

The skill was tuned on 12 tasks. All ten DeepSeek iterations with results, against the same control on those tasks (there is no v6 job; `ds-v4-b` reran half of v4, and v4 itself graded only 6):

| DeepSeek iteration (0.14.0) | Tasks graded | Control on the same tasks | jubarte |
|---|---:|---:|---:|
| ds-v2 | 12 | 0.515 | 0.579 |
| ds-v3 | 12 | 0.515 | 0.513 |
| ds-v4 | 6 | 0.583 | 0.580 |
| ds-v5 | 12 | 0.515 | 0.527 |
| ds-v7 | 12 | 0.515 | 0.528 |
| ds-v8 | 12 | 0.515 | 0.562 |
| ds-v9 | 12 | 0.515 | 0.576 |
| ds-v10 | 12 | 0.515 | 0.562 |
| ds-v11 | 12 | 0.515 | 0.548 |
| ds-v12 | 12 | 0.515 | 0.566 |

On the full set, ds-v9 lost 0.017 and ds-v12 gained 0.008. A +0.05 to +0.06 gain on 12 hand-picked tasks did not survive 139. Any claim built on a small development set, ours included, should be read with this in mind.

The small model went the other way. On Nemotron 30B-A3B, 11 of 12 skill iterations scored below the plain control on the same 12 tasks (0.059 to 0.381, against 0.401). Only v9 beat it (0.425). The 0.14.0 binary was the same throughout; the instructions were what changed. With a small model, a document skill that adds options can cost more than it saves.

## 5. How the grade can move

- **One judge, one grade per trial, mostly.** GLM-5.3-Flash graded every trial with the benchmark's rubric. 47 trials were graded twice; the two grades differ by 0.108 on average (median 0.062, largest 0.5). These 47 are the trials that happened to be regraded, not a random sample. Per-task differences of that size are judge noise. The 139-task mean averages much of it out, which is why the intervals above are about ±0.03.
- **One control run per task.** The control ran once per task (`deepseek-full` 9 tasks, `deepseek-full-b` 131, with one task, `redline-s1-t4-g11a`, graded only by the 3-judge panel). Control run-to-run variance is not measured here.
- **Not simultaneous.** The control ran Oct 27 to 28; the 0.14 arms ran Oct 28 to 30. Same model ID, same provider, same harness version. Provider-side changes in between cannot be ruled out.
- **No frontier model as the agent.** DeepSeek-V4.1-Flash and Nemotron are cost choices. A frontier agent may use fewer turns on its own, which would shrink the efficiency gap.

## 6. What it cost, and what it would have cost

Cost is the part most benchmark write-ups leave out. Section 2 is the work; this is the bill.

The tokens, priced at today's list rates:

| Recorded tokens priced at | RedlineBench archive (1,357 trials) | Per task, control (127 held-out) | Per task, jubarte 0.14 (127 held-out) |
|---|---:|---:|---:|
| DeepSeek V4.1 Flash, first-party peak ($0.30 in, $0.006 cache read, $1.20 out per M) | $702 | $0.137 | $0.081 |
| Claude Sonnet 5.5 ($2 in, $0.10 cache hit, $10 out) | $4,839 | $1.15 | $0.66 |
| Claude Opus 5.5 ($4 in, $0.20 cache hit, $20 out) | $9,679 | $2.29 | $1.32 |
| Claude Code's own estimate in `result.json` | $9,590 | $3.67 | $2.13 |

One full 140-task sweep at Opus 5.5 list: about $321 with the benchmark's tools, $184 with jubarte. The study that produced one clean comparison ran the equivalent of nearly ten sweeps (1,357 trials).

Notes on the table:

- Cache-write surcharges are not included, so the Claude rows are a floor.
- Nemotron ran on a local GPU that reports no cache, so its tokens are priced as uncached input.
- 91% of the control's input tokens were cache reads, billed at a twentieth of the input price on Claude and a fiftieth on DeepSeek. They are about 21% of the control's bill at Opus prices and 10% at DeepSeek's. The discount is what matters: billed as ordinary input, the same task would list at about $11.33 at Opus prices, five times the $2.29 above.

What was actually paid differs from every row above:

- The DeepSeek runs went through a flat Synthetic subscription with weekly credits. The work paused whenever credit ran low: the run logs record credit at 1.2% on Oct 30, a queue stop at 4% on Nov 1 and a stop at 0% on Nov 4.
- Grading went through several routes. OpenRouter returned 402 when its credit ran out; a DevPass weekly allowance was used up on Nov 2; a judge model was dropped after ten minutes as too expensive.
- The one study with a confirmed bill (Harvey LAB on jubarte 0.17, 88 trials, self-hosted MI355X) cost $100. The same 1.48 B recorded input tokens would list at $6,175 on Opus 5.5.

The judge is a second bill. Each RedlineBench trial is graded against a multi-criterion rubric by an LLM. Re-grading a run, which this study did several times, costs about as many judge calls again.

For a buyer: the same 1,357 trials span a 14x price range depending on which model's list price applies. Ask a vendor for tokens per task and its cache rate, not price per seat. Here, halving the turns cut the per-task bill by 41% at DeepSeek prices and 43% at Sonnet and Opus prices.

## 7. Later versions, for context only

These used newer binaries and a different benchmark. They are here to show the pattern held, not as 0.14 results.

| Study | Binary | Trials | Score, control vs jubarte | Tokens and time |
|---|---|---:|---|---|
| Harvey LAB redline tasks, Harbor Hub, Nov 1 to 4 | 0.16.0 + 39 commits (`e5e0838d9`) | 180 (90 pairs) | 0.936 vs 0.941 (judge noise about 0.02) | input 10.4 M vs 8.9 M, minutes 37.2 vs 32.4 |
| Harvey LAB editing tasks, MI355X, Nov 4 to 5 | 0.17.0 | 88 (44 pairs, 16 tasks) | −0.002 task-balanced (−0.026 to +0.022) | about 6% fewer tokens and minutes; the study's own write-up declines a causal efficiency claim |

The Harvey savings are smaller than RedlineBench's. They also grow or reverse by task: jubarte cost more when the input already carried the counterparty's tracked changes, where agents probed existing-revision rules by trial and error (Harvey `FINDINGS.md`).

## 8. Reproduce

Raw data (public):
- `hf://datasets/arthrod/redline-bench-deepseek-trajectories`: `redlinebench/` for this report (1,409 rows, 39,611 files), `harvey_lab/`, `harvey_lab_017/`.
- `hf://datasets/arthrod/redline-bench-jubarte-tasks`: the 140 task definitions.

Each grade sits at `runs/rejudge-synthetic/GLM-5.3-Flash/<job>/<trial>/grade.json` in the `files` table. The binary for each trial is in `trials.jubarte_sha256`: `f4c352db…` is 0.14.0 linux-aarch64, `469c7ff4…` is 0.15.0.

The tables in this report come from `data/per_job.csv`, `data/deepseek_pairs.csv`, `data/costs.json` and `data/scale.json` at the root of this repository, built by reading `result.json`, `grade.json` and `agent/trajectory.json` for every trial.

## 9. Rights

RedlineBench tasks and documents: Crosby Legal and micro1, code MIT, data CC-BY-4.0. Harvey LAB material: Harvey AI, MIT. Trajectories, deliverables and grades from these runs: CC-BY-4.0. Not affiliated with or endorsed by Crosby, micro1, Harvey, DeepSeek, Synthetic or Anthropic. The contracts are synthetic benchmark material; nothing here is legal advice.
