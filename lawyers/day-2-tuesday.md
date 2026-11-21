# Day 2 · How we tested it, and what the graders cannot see

Yesterday I gave the result: same scores, half the time, real redlines. Today is
about how much weight those numbers can carry.

## The two benchmarks

**RedlineBench** (Crosby and micro1) is a negotiation. There are three deals. In
each, the agent acts for one party over four turns. Turn 1 is a first markup of a
clean template. Turns 2 to 4 answer the other side's markup. Lawyers wrote a rubric
for every task: "accepts the 30-day cure period", "rejects the uncapped indemnity",
"inserts a mutual confidentiality carve-out". A judge model reads the agent's file
and ticks the rubric. 140 tasks in all.

**Harvey's Legal Agent Benchmark** is broader: 1,200-plus tasks across practice
areas. We used the ones that end in a marked-up document, such as a first-turn
redline of a credit support annex or a counterparty-paper review of an ISDA
schedule. Each has dozens of rubric criteria. We ran 90 of them in pairs.

## What we compared

One thing changed between the two runs of a task: the redlining tool.

- **The benchmark's own tools.** RedlineBench gives the agent Python scripts for
  Word files. Harvey gives it a document skill with a script that builds a redline.
- **jubarte.** One program. The agent reads the contract with a number on every
  paragraph and every tracked change, then says "in paragraph 12, replace *thirty
  days* with *forty-five days*", and jubarte writes that as a tracked change.

The model, the brief, the contract and the grader stayed the same. Most runs used
DeepSeek-V4.1-Flash, a fast and inexpensive model, inside Claude Code. We also ran
Claude Haiku 5.5, GLM-5.3-flash and Nemotron 3.5, and two other agent programs, pi
and Codex. Three more small models, Muse Spark, Muse Glimmer and Qwen, were run with
the benchmark's own tools only, so they tell you how hard the test is and nothing
about jubarte. No run used a top-tier model. That is a limit of this work and I would
rather say so than have you find it.

## What the graders cannot see

This part matters most for a lawyer reading any legal AI benchmark, including ours.

**The grader reads accepted text.** Harvey's grader converts the Word file to plain
text with every tracked change accepted, and the judge reads that. It cannot tell a
redline from a clean rewrite. That is how Monday's file, with strikethrough
formatting and no tracked changes, got through. The struck words were still in the
text, so the judge thought those clauses had not been deleted, and that agent lost
points for it. But it lost them by accident. Nothing checked whether the document
was a redline.

**Comments went missing.** Good markup explains itself in the margin. The first
version of the grader we used dropped Word comments, so an agent that put its
reasoning in comments looked as if it had given none. When we switched to Harvey's
current extractor, which shows comments to the judge, the first 19 pairs moved from
0.890 and 0.876 to 0.936 and 0.938. A tenth of a point came from where the
explanation was written, not from what it said.

**The judge is not steady.** In four of those 19 pairs, identical text in both files
was graded differently. Run the same judge twice and the score moves about 0.02.

**One run per task.** On RedlineBench a single task can swing from 0.77 to 0 between
runs. Only averages over many tasks mean anything.

## What this does to our claim

We do not claim jubarte makes an agent a better lawyer. The scores do not show it,
and the graders could not have seen most of what a redlining tool improves. We
claim what we could measure cleanly: time, tokens, and what is inside the file.

Tomorrow: the part we hoped would go differently.
