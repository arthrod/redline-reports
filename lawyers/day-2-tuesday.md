# Day 2 · The twelve tasks that fooled me

MAIN POST:

On the twelve contracts I tuned on, my tool was ahead. On the 120 I did not, it was slightly behind.

I wrote the agent's instructions for jubarte 0.14 the way most teams tune anything: pick a dozen tasks, try a draft, keep what scores best, repeat. Eleven drafts on DeepSeek, all on the same twelve.

Pooling every run of every draft:

On the twelve tuning tasks: +0.030 against the benchmark's own scripts.
On the 120 tasks never used for tuning: −0.010.

Neither can be told apart from zero. But the sign flipped, and the draft that looked best on the twelve (0.576) lost 0.025 when it met the other 128.

A small model went the other way entirely. On Nemotron 30B, 10 of 11 drafts scored below the plain scripts on the same twelve tasks. The first draft scored 0.059 against 0.401. Pooled, jubarte lost 0.093, and that loss is real: its interval excludes zero. The binary never changed; my instructions did. For a model that thinks on every step, every extra option was one more thing to think about.

Why a lawyer should care: a vendor demo is a twelve-task development set. Someone chose the matters, tuned the prompts on them, and showed you the number. The question that separates a result from a demo is short: what did you not tune on?

Disclosure: jubarte is mine. So is the miss, and every draft is in the public data, the losers included.

Links in comments. Have you seen a legal AI vendor report results on matters it did not tune on?

COMMENT:

Report, section 3: https://github.com/arthrod/redline-reports/blob/main/reports/jubarte-six-cohorts.md
Every draft's runs: https://huggingface.co/datasets/arthrod/redline-bench-jubarte-six-cohorts (jobs `jubarte-ds-v2` to `jubarte-ds-v12`, `jubarte-v1` to `jubarte-v11`)

In plain English. A development set is the material you look at while you build. A held-out set is material you lock away until the end. When the first scores better than the second, you tuned to the first. Every lawyer has seen the same effect in a brief written around three favorable cases.

Nitty-gritty:
- DeepSeek, 0.14 cohort, 95% intervals:
  - Tuning tasks: +0.030 (−0.017 to +0.080), 10 tasks with a control grade.
  - Every other task: −0.010 (−0.034 to +0.014), 120 tasks.
- Draft means on the tuning tasks: 0.510 (`ds-v3`) to 0.576 (`ds-v9`).
- `ds-v9` on the rest: −0.025 (−0.060 to +0.008). `ds-v12` on the rest: +0.002 (−0.029 to +0.032).
- One study job lost outright: `study-v13`, 27 tasks, −0.090 (−0.150 to −0.035). It still cut the time from 18.7 to 8.0 minutes.
- Nemotron 3.5 Lightning 30B-A3B on one RTX 5090. 11 drafts, control 0.401 on the twelve tasks. Only v9 beat it (0.425). Pooled: −0.093 (−0.170 to −0.018).
- Judge: GLM-5.3-Flash for every grade above.

VISUAL SUGGESTIONS:
+0.030 | ON THE TWELVE TASKS I TUNED ON | pooled across every DeepSeek draft
−0.010 | ON THE 120 I DID NOT | same drafts, same control, no difference detected
10 of 11 | DRAFTS THAT LOST ON A SMALL MODEL | Nemotron 30B, same binary, different instructions

OPEN QUESTIONS FOR ARTHUR:
1. The tuning-task figure is single-judge and pooled across drafts: +0.030, with the best draft at 0.576. Any larger figure you remember averaged more than one judge.
2. "Eleven drafts on DeepSeek" counts the jobs `ds-v2` to `ds-v12`, with no v6 and `ds-v4-b` as a half rerun of v4. Recount if you think of them differently.
