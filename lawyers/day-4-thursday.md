# Day 4 · Half the time, half the tokens

If the score is a tie, the question becomes what each side paid for it.

| Test | Measure | Their tools | jubarte | Change |
|---|---|---|---|---|
| RedlineBench, 127 tasks | minutes per round of markup | 18.6 | 9.2 | −51% |
| | words the model wrote (output tokens) | 44,500 | 20,800 | −53% |
| | text the model read (input tokens) | 2.61M | 1.40M | −46% |
| Harvey redline tasks, 90 pairs | minutes per task | 37.2 | 32.4 | −13% |
| | tokens per task | 10.4M | 8.9M | −14% |
| Harvey editing tasks, 44 pairs, later version | minutes per task | 28.4 | 26.6 | −6% |
| | text the model read | 17.2M | 16.2M | −6% |
| RedlineBench, GLM-5.3-flash | minutes per attempt | 102 | 68 | −33% |
| | tasks finished, of 69 | 42 | 59 | +17 |

Same model, same brief, same quality of legal answer.

One run went the other way, and you should know about it. Claude Haiku 5.5, on an
early version of jubarte, took 26 minutes where the other arm took 24, and cost
about 7 cents more per task. Every run since then has been faster and cheaper. And
inside the Harvey average there are single tasks where jubarte cost more: the ones
where the document already carried the other side's tracked changes and the agent
had to learn how to work around them.

## Where the time went

Watch an agent redline with general-purpose tools and you see it do what nobody
would ask of an associate. It unzips the Word file. It reads raw XML. It writes a
small program to find a sentence, then another to wrap the old words in a deletion
and the new ones in an insertion, in the order the file format demands. It runs the
program, gets an error, and rewrites it. Then it renders the page to check.

With jubarte the same edit is one line: paragraph 12, replace *thirty days* with
*forty-five days*, author *Maria Souza*. The tool refuses if the words are not
there, or appear twice, or sit inside someone else's change, and says which.

Tokens are the unit AI is billed in, so half the tokens is close to half the bill.
But the other effects matter more in practice.

## Why this matters to a practice

**Waiting.** Nine minutes is a coffee. Nineteen is a meeting you start instead, and
then the redline sits unread. The speed at which a draft comes back decides whether
a lawyer stays in the document or leaves it.

**Memory.** An agent can hold only so much text at once. When that fills up, it
summarises what it has done and carries on from the summary, and things get lost.
On the weaker models we saw agents, with either set of tools, finish with a summary
instead of a contract. An agent that reads half as much has more room left for the
contract and the playbook.

**Finishing at all.** The slowest model finished 59 of 69 tasks with jubarte and 42
with the other tools. The work it did not finish scored nothing.

**The file.** The easiest part to overlook. On RedlineBench with DeepSeek, no jubarte
file failed the benchmark's validity check, and jubarte's own check that every edit
is tracked came back clean on 122 of 128. Their changes stayed theirs. Ours carried
our author's name. That is a file you can send to the other side.

For the people who build legal AI products, the same numbers read as margin: the
same answer for half the compute, with a 36 MB tool in place of 850 MB or more of
other software. Friday's post has the links for them, and for you.
