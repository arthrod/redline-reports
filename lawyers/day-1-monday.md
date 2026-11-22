# Day 1 · 716 runs for one sentence

MAIN POST:

It took 716 agent runs, 158 hours of run time and 1.43 billion input tokens to earn one sentence I can defend: half the work, no detectable change in the score.

The question was narrow. When an AI agent redlines a contract, does it do better legal work if it gets a real tracked-changes engine instead of the Python scripts the benchmark ships with?

The test was Crosby and micro1's RedlineBench: 140 negotiation tasks, four rounds of markup each. DeepSeek-V4.1-Flash ran inside Claude Code. One arm used the benchmark's own scripts. The other used jubarte 0.14, the Word engine I write. Model, brief, contracts and grader stayed the same.

On the 127 tasks I never used to tune anything:

Score: 0.491 with their tools, 0.495 with mine. No difference detected.
Minutes per task: 18.5 against 9.2.
Turns: 71 against 37.
Output tokens: 44.5k against 20.8k.

Disclosure: jubarte is mine, and I ran every trial. One model grades every file but one, which went to a three-judge panel. Graded twice, the same file's score moves by 0.108 on average, so only the 127-task average means anything.

Honest reading: the tool did not make the agent a better lawyer. With jubarte it took half the time and stopped writing Word's XML by hand. The arms ran on different days, so a provider change is not ruled out.

Why 716 runs for one comparison? It took a dozen drafts of the agent's instructions, a control arm, and reruns after a full disk, a killed process and a Docker image deleted mid-run. Tomorrow: what those drafts taught me about every vendor demo.

Links in comments. If you evaluate legal agents: how many runs sit behind your last headline number?

COMMENT:

Report: https://github.com/arthrod/redline-reports/blob/main/reports/jubarte-0.14-redlinebench.md
Every trial, file by file: https://huggingface.co/datasets/arthrod/redline-bench-deepseek-trajectories
The 140 tasks as configured: https://huggingface.co/datasets/arthrod/redline-bench-jubarte-tasks
jubarte: https://github.com/jandira-tech/jubarte
RedlineBench is by Crosby and micro1: https://huggingface.co/datasets/crosbylegal/RedlineBench

In plain English. Score: lawyers wrote a rubric for each task (accept this cure period, reject that uncapped indemnity), and a judge model ticks it, 0 to 1. A turn is one step the agent takes: read a file, run a command, write an edit. Tokens are what the model reads and writes, and what you are billed for. "Never used to tune" means I wrote the agent's instructions while watching 12 tasks and kept the other 127 out of sight; those 127 are the fair test.

Nitty-gritty:
- 0.14.0 linux-aarch64 binary, sha256 `f4c352db…`, in every trial of the arm.
- Control: jobs `deepseek-full` and `deepseek-full-b`, one run per task. jubarte: `jubarte-ds-v12-rest`.
- Judge: GLM-5.3-Flash with the benchmark's rubric.
- Difference +0.004, 95% bootstrap interval −0.026 to +0.034.
- 48 tasks better, 40 worse, 39 equal.
- The 716 runs cover 30 jobs from 26 to 30 October.
- The arms were not interleaved: the control ran 27 to 28 October, the jubarte arm 28 to 30 October. Model, harness and grader were pinned, but a provider-side change between those days cannot be ruled out.
- Later versions on Harvey's benchmark went the same direction with smaller savings. They are in the report and stay out of this post on purpose.

VISUAL SUGGESTIONS:
716 | RUNS ON JUBARTE 0.14 | to reach one clean comparison on 127 held-out contracts
9.2 min | PER TASK WITH JUBARTE | 18.5 with the benchmark's own scripts, no score difference detected
0.495 | SCORE, 127 HELD-OUT TASKS | 0.491 with the benchmark's scripts, no difference detected

OPEN QUESTIONS FOR ARTHUR:
1. The old Day 1 led with 134 tasks (0.494 vs 0.492), which is the 0.15.0 run. This version leads with the 0.14.0 held-out set. Confirm you want 0.14 as the headline.
2. The report links point to `main` and resolve only after PR #1 merges. Merge before posting, or swap in the benchmarks.law URL if you publish it there.
3. The old Monday opened with the strikethrough "redline". It is now Thursday's hook, where it fits the grader story. Say if you want it back on Monday.
