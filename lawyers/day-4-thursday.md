# Day 4 · Which judge graded each side?

MAIN POST:

When a vendor shows you an AI score, ask one question first: which judge graded each side?

I learned this from my own data. The cohort was Muse Spark 1.3 on RedlineBench. Each run is graded by a judge model. Some of the jubarte runs had been graded twice: once by the judge used for both arms, and once by a different model used only on my side. My first pass averaged every grade a run had. That blended two judges into one arm and not the other, and my tool looked 4.6 points ahead.

With one judge per arm, the gap is +0.019, with a 95% range from −0.033 to +0.071. No difference detected.

Two more things about that cohort, said plainly. The jubarte build was not recorded. And the jubarte arm ran a day before the control, not after.

The same discipline changes how the other results read. On RedlineBench the judge sees every insertion, deletion and comment. On Harvey's benchmark the grader reads the contract with every change accepted. One control-arm "redline" there had 39 runs of strikethrough formatting and not a single tracked change, and it scored 0.90.

Then the rounds. RedlineBench tasks are rounds of a negotiation. Across three cohorts, jubarte did slightly better in the middle rounds, answering the other side's markup, and slightly worse in the first and last. Only one round result clears zero, barely. A pattern to test, not a claim.

Disclosure: jubarte is mine, and so was the averaging mistake. I caught it before posting.

If a vendor shows you a score, ask two questions. Which judge graded each side? Does that judge read the tracked changes, or only the accepted text?

Links in comments. Have you ever caught a number of your own that was too good?

COMMENT:

Report, sections 3 and 4: https://github.com/arthrod/redline-reports/blob/main/reports/jubarte-six-cohorts.md
How the grades were filtered: https://github.com/arthrod/redline-reports/blob/main/DATA-AUDIT.md
Harvey LAB: https://github.com/harveyai/harvey-labs
RedlineBench: https://huggingface.co/datasets/crosbylegal/RedlineBench

In plain English. A judge model reads the agent's redline and ticks the lawyers' rubric. Different judge models are stricter or looser, so mixing them inside one comparison moves the number for reasons unrelated to the work. "Accepted text" means the document as it reads after clicking Accept All. A real redline and a clean rewrite look identical that way.

Nitty-gritty:
- Muse Spark 1.3, 140 tasks, gpt-6.1-sol panel in both arms: 0.297 against 0.316, +0.019 (−0.033 to +0.071).
- Mixing in the GLM-5.3-Flash grades on the jubarte side gave +0.046.
- The Muse jubarte arm ran Oct 16 to 17 UTC; the control ran Oct 17 to 18.
- Timeouts: 33 of 140 jubarte trials and 78 of 158 control trials. Timed-out runs are graded on what was saved.
- Rounds, change with jubarte (95% interval):

  | Round | 0.14 DeepSeek | 0.15 DeepSeek | Muse |
  |---|---|---|---|
  | 1 | −0.060 (−0.127 to +0.017) | −0.092 (−0.179 to +0.017) | −0.001 |
  | 2 | +0.017 | +0.040 (+0.001 to +0.082) | +0.017 |
  | 3 | +0.014 | +0.006 | +0.077 (−0.004 to +0.156) |
  | 4 | −0.038 (−0.083 to +0.007) | −0.035 | −0.031 |

- The strikethrough file: the control arm of a Harvey LAB capital-markets indenture task in the 0.16 cohort. It had 39 `w:strike` runs and 0 `w:ins` or `w:del`, and scored 0.900. Harvey's extractor runs `pandoc --track-changes=accept`.

VISUAL SUGGESTIONS:
+0.046 → +0.019 | THE SAME RUNS, ONE JUDGE PER ARM | Muse Spark 1.3, no difference detected
0 | TRACKED CHANGES IN A "REDLINE" | 39 strikethrough runs, scored 0.90 by an accepted-text grader
Rounds 2–3 up, 1 and 4 down | WHERE JUBARTE HELPED AND HURT | the same direction in three cohorts

OPEN QUESTIONS FOR ARTHUR:
1. The hook is now the judge question; the +0.046 blend is the example in the body, not the headline, because +0.046 was never published and the true result is a null. To restore the earlier hook ("The number I almost published"), revert this paragraph.
2. Publish the Muse trials before this goes out (`DATA-AUDIT.md`). The post rests on them.
