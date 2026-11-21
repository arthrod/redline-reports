# Day 3 · The disappointment

We built a better pen and expected better drafting. That is not what happened.

| Test | Tasks | Their tools | jubarte |
|---|---|---|---|
| Harvey redline tasks, DeepSeek | 90 pairs | 0.936 | 0.941 |
| Harvey editing tasks, DeepSeek, later version | 44 pairs | 0.925 | 0.923 |
| RedlineBench, DeepSeek | 134 | 0.494 | 0.492 |
| RedlineBench, Claude Haiku 5.5, first set | 69 | 0.394 | 0.427 |
| RedlineBench, Claude Haiku 5.5, second set | 33 | 0.430 | 0.412 |
| RedlineBench, GLM-5.3-flash | 40 | 0.350 | 0.364 |
| RedlineBench, Nemotron 3.5 | 12 | 0.401 | 0.425 |

Four small wins and three small losses. Only one of them, Haiku's first set, is larger
than the noise in the measurement. The fair reading is a tie. It took us a few days
to say that sentence without adding "but".

Looking at where the points went was more useful than the totals.

## Where jubarte lost

**First drafts came out unreadable.** On turn 1, marking up a clean template,
jubarte scored 0.258 against 0.280. When the agent rewrote a paragraph, the tool
compared old and new one word at a time and marked each difference. A paragraph that
a lawyer would strike and replace came out as 254 little insertions and deletions
per document, against 73 for the other arm. Half of the insertions were nine
characters or shorter. You have seen this redline. It is the one where "are" is struck and
"apply to" inserted, then "provided" struck and "with" inserted, and by the third
line you give up and ask for a clean copy. The judge gave up too.

**Agents struck too much.** This one is about lawyering, not software. On the
response turns, jubarte lets an agent reject the other side's insertion with one
short command. Agents used it. They won 47 rubric items that say "rejects X" and
lost 12. But they lost 62 items that say "accepts X" and won 9. By turn 4, when a
deal should be closing, they were still re-opening settled points.

A junior with a red pen marks more than a junior without one. The tool made
rejection cheap, and the agent's judgment about when to concede did not improve to
match. A playbook that says what to concede matters more than any tool.

## Where jubarte won

**It kept the other side's markup.** On a securities-lending first turn, the control
arm accepted the counterparty's changes and re-issued only its own. All 182
insertions carried one name. A reader could no longer see what the other side had
proposed. jubarte's file kept 191 changes under their name and added 89 under ours.
On Harvey's ISDA first turn, editing in place kept a party-identification preamble
that the rebuilt file lost. Those were real points, and they are the difference
between a turn of a negotiation and a new document.

**It did what the memo asked.** When each edit is one short instruction, agents
carried out every item in the issues memo. When each edit means writing a script,
they ran out of patience or budget and skipped some.

**It failed less.** In the first ten Harvey pairs the control arm hit 38 hard tool
failures and jubarte hit 5. Across those ten tasks the control arm spent about 190
of its 335 minutes rebuilding a redline engine from scratch.

## What I take from it

The score measures legal judgment, and a redlining tool does not supply judgment.
The same model with the same brief makes the same calls. What the tool changes is
what the work costs and what state the file is in when you open it. That is
tomorrow's post, and it turned out to be the better story.
