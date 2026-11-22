# Day 1 · Six tests, and my tool never made the agent a better lawyer

MAIN POST:

I tested my own redlining tool against the tools two legal benchmarks ship with, in six separate setups. It never raised the score. In five of the six, it halved the work or cut it.

The question was narrow. When an AI agent redlines a contract, does it do better legal work with a real tracked-changes engine than with the benchmark's own scripts?

The engine is jubarte, which I write. The benchmarks are Crosby and micro1's RedlineBench (140 negotiation tasks) and Harvey's Legal Agent Benchmark. Six cohorts: three agent models, four jubarte builds, two benchmarks. Same model, contracts and grader in both arms of each.

The biggest cohort: DeepSeek in Claude Code, jubarte 0.14, 560 runs, 130 tasks paired against the control.

Score: 0.503 with the benchmark's scripts, 0.497 with jubarte. No difference detected.
Minutes per task: 18.3 against 10.3.
Output tokens: 44.2k against 21.5k.

The next build, 0.15, on the same model: 0.503 against 0.501, again in about half the time.

The other four:
Harvey's tasks, two builds: no difference, 6% to 14% less work.
Muse Spark 1.3: no difference, a quarter less time.
Nemotron, a small 30B model: jubarte scored lower, and its interval excludes zero. The one real loss.

Honest reading: the tool did not make any of these agents a better lawyer. With a capable model it made the job shorter. With a small one, my instructions got in the way.

Disclosure: jubarte is mine, and I ran every trial. The control and jubarte arms ran hours to days apart, so a change at the model provider is not ruled out.

Tomorrow: the twelve tasks that fooled me.

Links in comments. If you evaluate legal agents: does your headline number come from one setup or several?

COMMENT:

Report: https://github.com/arthrod/redline-reports/blob/main/reports/jubarte-six-cohorts.md
Every trial, file by file: https://huggingface.co/datasets/arthrod/redline-bench-jubarte-six-cohorts
jubarte: https://github.com/jandira-tech/jubarte
RedlineBench is by Crosby and micro1: https://huggingface.co/datasets/crosbylegal/RedlineBench

In plain English. Score: lawyers wrote a rubric for each task (accept this cure period, reject that uncapped indemnity), and a judge model ticks it, 0 to 1. Tokens are what the model reads and writes, and what you are billed for. "No difference detected" means the 95% range of plausible differences includes zero. It does not prove the two are equal.

Nitty-gritty:
- All six, change in score (95% interval):
  - 0.14 DeepSeek: −0.007 (−0.030 to +0.016), 130 tasks.
  - 0.14 Nemotron: −0.093 (−0.170 to −0.018), 12 tasks.
  - 0.15 DeepSeek: −0.003 (−0.028 to +0.024), 125 tasks.
  - 0.16 Harvey: +0.006 (−0.004 to +0.017), 90 pairs.
  - 0.17 Harvey: −0.002 (−0.026 to +0.022), 16 tasks.
  - Muse Spark 1.3: +0.019 (−0.033 to +0.071), 140 tasks.
- One judge per cohort, the same in both arms: GLM-5.3-Flash for DeepSeek and Nemotron, a gpt-6.1-sol panel for Muse, Harvey's LAB judge for Harvey. Scores compare within a cohort, not across cohorts.
- Bootstrap over tasks, 10,000 draws, seed 20261122.
- 0.14 binary sha256 `f4c352db…`, 0.15 `469c7ff4…`. The Muse build was not recorded.

VISUAL SUGGESTIONS:
0 of 6 | COHORTS WHERE JUBARTE RAISED THE SCORE | five showed no difference, one lost
10.3 min | PER TASK WITH JUBARTE, DEEPSEEK | 18.3 with the benchmark's own scripts
−0.093 | NEMOTRON 30B, THE ONE LOSS | same binary, a small model, a long skill

OPEN QUESTIONS FOR ARTHUR:
1. The lead is the whole 0.14 DeepSeek cohort (0.503 vs 0.497, −0.007), tuning tasks included; Tuesday separates them. Confirm you want the cohort figure as Monday's lead.
2. The Muse row is not in a public dataset yet (`DATA-AUDIT.md`). Publish it before Monday, or drop Muse from the post.
3. The report link resolves only after this branch merges to `main`.
