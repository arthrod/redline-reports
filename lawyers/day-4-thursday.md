# Day 4 · The redline that wasn't one

MAIN POST:

One "redline" in a benchmark I ran had no tracked changes in it, and it scored 0.90.

It looked right: old words struck through, new words beside them. Inside the file, Word had recorded 39 runs of strikethrough formatting and zero insertions or deletions. The agent drew a redline instead of making one. Accept All does nothing to that file.

It passed because Harvey's grader reads the contract with every tracked change accepted, as plain text. It cannot tell a redline from a clean rewrite. On that benchmark, a tool built for real tracked changes can move the score only through the words.

RedlineBench is different, and that matters for this week's tie. Its judge sees every insertion, deletion and comment. jubarte still tied there. So the tie is not the grader hiding the tool's work. It is legal judgment, which a tool does not supply.

The judges are noisy, though. I graded 47 RedlineBench runs twice with the same model, and the two grades differ by about 0.08 per task.

Then I audited my own write-up. My dataset card headlined a 0.15 result inside a 0.14 study. A trial table counted a folder named "analysis" as a run. And the card described Codex runs that the public data does not contain. All of it is listed in the audit, with the fixes.

Disclosure: jubarte is mine.

If a vendor says its redlines score well, ask one question: does the grader open the tracked changes, or read the accepted text?

Links in comments. Who here checks a redline's markup before trusting its score?

COMMENT:

The audit: [link to DATA-AUDIT.md]
Harvey LAB, the benchmark with the accepted-text grader: https://github.com/harveyai/harvey-labs
RedlineBench: https://huggingface.co/datasets/crosbylegal/RedlineBench

In plain English. "Accepted text" means the document as it reads after clicking Accept All. A real redline and a clean rewrite look identical that way. A grader that reads the markup sees who changed what, as a lawyer does in the Reviewing Pane.

Nitty-gritty:
- The strikethrough file was the control arm of Harvey LAB's capital-markets indenture markup: 39 `w:strike` runs, 0 `w:ins`, 0 `w:del`, scored 0.900. The jubarte file for the same task had 38 insertions and 39 deletions.
- Harvey's extractor runs `pandoc --track-changes=accept`. Under the upstream extractor, which also shows Word comments, the first 19 pairs moved from 0.890 / 0.876 to 0.936 / 0.938.
- RedlineBench's judge reads an annotated view with deletions as `~~…~~`, insertions as `++…++` and comment markers.
- Judge repeatability: 47 trials with two GLM-5.3-Flash grades, mean per-trial standard deviation 0.077.
- The Harvey runs used jubarte 0.16; the RedlineBench runs used 0.14.

VISUAL SUGGESTIONS:
0 | TRACKED CHANGES IN A "REDLINE" | 39 strikethrough runs, scored 0.90 by an accepted-text grader
0.08 | SAME FILE, GRADED TWICE | per-task swing from one judge model
7 | ERRORS IN MY OWN DATASET CARDS | found in this week's audit, fixed before this post

OPEN QUESTIONS FOR ARTHUR:
1. Post this only after the card fixes in DATA-AUDIT.md are live. The post says they are fixed.
2. The old harness report says both graders read accepted text. That is wrong for RedlineBench (checked in the judges' annotated views), and the new harness report corrects it. Confirm nothing published elsewhere repeats the old claim.
