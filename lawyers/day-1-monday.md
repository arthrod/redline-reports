# Day 1 · The redline that wasn't one

One of the redlines in our test had no tracked changes in it.

It looked right. Old words were struck through and new words sat beside them. But
when we opened the file's XML, Word had recorded 39 runs of strikethrough
*formatting* and zero insertions or deletions. The AI agent had drawn a redline
instead of making one. Press "Accept All" on that file and nothing happens. The
struck words stay in your contract, struck.

No lawyer caught this, because no lawyer was looking. The file came out of an
automated benchmark, and the grader that scored it reads only the document's text.
It scored 0.90 out of 1.

I have spent this year building **jubarte**, an open-source engine that makes real
Word redlines without Word: tracked insertions, deletions and moves, comments,
replies, accept and reject, all in the file format Word itself writes. This week it
went out under the Apache 2.0 licence, which means anyone can use it, including
inside a commercial product, at no cost.

Before releasing it, we wanted an answer to one question: **if you give an AI agent
a proper redlining tool, does it do better legal work?**

So we tested it on two public benchmarks built by legal AI companies:

- **RedlineBench**, from Crosby and micro1. 140 negotiation tasks. An agent
  represents one party to a commercial contract across four rounds of markup,
  and lawyers' rubrics say which changes it should have accepted, rejected or made.
- **Harvey's Legal Agent Benchmark**. We took the tasks whose deliverable is a
  marked-up document, ran 90 of them twice, and compared.

In each one the agent did the same task two ways: once with the tools the
benchmark ships, and once with jubarte in their place. Same model, same
instructions, same documents.

Here is the whole result in three lines, so that nobody has to wait until Friday:

1. **The scores barely moved.** On Harvey's tasks, 0.936 with their tools and 0.941
   with ours. On RedlineBench, 0.494 and 0.492. We hoped for more. Wednesday's post
   is about that.
2. **The work took about half the time.** On RedlineBench the agent finished a
   round of markup in 9.2 minutes instead of 18.6, and used about half the tokens,
   which is what you pay for.
3. **The files were real redlines.** Their changes stayed under their name and ours
   went in under ours, the way a negotiated draft is supposed to look.

A lawyer reading that list might shrug at number 2 and care most about number 3. An
engineer would do the reverse. This series is written for the people who are a bit
of both.

**The week:**

- **Tuesday** · How the test worked, and the things the graders cannot see.
- **Wednesday** · The disappointment: why a better tool did not buy a better score.
- **Thursday** · Half the time and half the tokens, and why that matters to a
  practice more than it sounds.
- **Friday** · What is free to use today, what it still gets wrong, and how to try
  it on your own worst document.

Try it now if you would rather not wait: https://github.com/jandira-tech/jubarte
