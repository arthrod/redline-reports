# Day 2 · My twelve-task demo lied to me

MAIN POST:

On twelve contracts, my tool beat the benchmark's own scripts by six points. On the other 127, it did not.

I tuned the agent's instructions for jubarte 0.14 the way most teams tune anything. Pick a dozen tasks, try a draft, keep what scores best, repeat. Ten drafts on DeepSeek. On those twelve tasks the drafts scored up to 0.579 against 0.515 for the plain scripts. I had the post half written.

Then two of the top drafts ran on the 127 tasks they had never seen. One gained 0.004. The other lost 0.024. Neither difference can be told apart from zero.

A small model went the other way entirely. On Nemotron 30B, 11 of 12 drafts scored below the plain scripts on the same twelve tasks, the first one at 0.059 against 0.401. The binary never changed. My instructions did, and for a small model every added option was one more way to get lost.

Why a lawyer should care: a vendor demo is a twelve-task development set. Someone chose the matters, tuned the prompts on them, and showed you the number. The question that separates a result from a demo is short: what did you not tune on?

Disclosure: jubarte is mine. The miss is mine too, and every draft is in the public data, including the ones that lost.

Links in comments. Have you ever seen a legal AI vendor report results on a set they did not tune on?

COMMENT:

The development-set table, all ten DeepSeek drafts against the same control on the same twelve tasks (v4 was graded on six of them): https://github.com/arthrod/redline-reports/blob/main/reports/jubarte-0.14-redlinebench.md (section 4)
Every draft's runs: https://huggingface.co/datasets/arthrod/redline-bench-deepseek-trajectories (jobs `jubarte-ds-v2` to `jubarte-ds-v12`, `jubarte-v1` to `jubarte-v12-boxdown`)

In plain English. A development set is the material you look at while you build. A held-out set is material you lock away until the end. When the score on the first is much better than on the second, you tuned to the first. Every lawyer has seen the same effect in a brief written around three favorable cases.

Nitty-gritty:
- DeepSeek drafts on the 12 tasks: v2 0.579, v9 0.576, v12 0.566, v8 and v10 0.562; control 0.515.
- Held-out 127: v12 0.495 vs 0.491 (−0.026 to +0.034); v9 0.467 vs 0.491 (−0.056 to +0.007). Task bootstrap, 10,000 draws.
- One short study arm lost outright: `jubarte-study-v13`, 33 tasks, 0.455 vs 0.523 (−0.120 to −0.019).
- Nemotron 3.5 Lightning 30B-A3B on one RTX 5090, 12 drafts, control 0.401. Only v9 beat it (0.425).
- Same 0.14.0 binary (`f4c352db…`) in all 22 drafts.
- Judge: GLM-5.3-Flash for every grade above.

VISUAL SUGGESTIONS:
+0.064 | TWELVE TASKS I TUNED ON | best draft 0.579 against 0.515 for the benchmark's scripts
+0.004 | 127 TASKS I DID NOT | the same approach, no difference detected
11 of 12 | DRAFTS THAT LOST ON A SMALL MODEL | Nemotron 30B, same binary, different instructions

OPEN QUESTIONS FOR ARTHUR:
1. "Ten drafts on DeepSeek" counts the ten DeepSeek jobs with results (v2, v3, v4, v5, v7, v8, v9, v10, v11, v12). There is no v6 job; `ds-v4-b` is a rerun of v4. Confirm the count reads right to you.
2. The old Tuesday post was the method and grader post. The grader material moved to Thursday. Say if you want the method post back.
