# Day 5 · What you can do with it on Monday

This week in one paragraph: we gave AI agents a real redlining tool and tested it on
Crosby's and Harvey's benchmarks. The legal quality of the work did not change. The
time and cost fell by about half on one benchmark and about an eighth on the other.
And the files were actual redlines, with each side's changes under its own name.

## It is free, including for commercial use

jubarte 0.19.0 came out on 21 November under the **Apache 2.0** licence. Earlier
versions used a licence (AGPL) that many companies' legal departments will not
allow near their products. If that was the reason your team could not try it, the
reason is gone. You can run it inside a firm, ship it inside a product, and change
it, without paying anyone or publishing your own code.

## Three ways to try it

**If you use an AI coding agent** (Claude Code, Codex, Gemini CLI), one line adds
it:

```
claude mcp add --transport stdio jubarte --scope project -- uvx --from 'jubarte-docx[mcp]' jubarte-mcp --root .
codex mcp add jubarte -- uvx --from 'jubarte-docx[mcp]' jubarte-mcp --root .
gemini extensions install https://github.com/jandira-tech/jubarte
```

Then ask in plain words: "Compare these two drafts and give me a redline." "Reject
their change to the indemnity cap and say why in a comment."

**If you are comfortable with a terminal:**

```
cargo install jubarte
jubarte original.docx revised.docx -o redline.docx --author "Your Name"
jubarte changes redline.docx
jubarte scrub final.docx -o clean-to-send.docx
```

The last line removes authors, editing history, metadata and comments before a
document leaves the building.

**If you are neither**, send this post to whoever runs your firm's AI tools. The
question to put to them: when our assistant marks up a contract, is the output a
tracked-changes file with each side's edits preserved, and how do we know?

## What it still gets wrong

- **Rewritten paragraphs.** When an agent rewrites a paragraph in a document that
  already carries the other side's changes, the markup can come out word by word and
  hard to read. This cost us points on first drafts.
- **Documents full of the other side's changes.** The tool is strict about not
  touching their markup. That is correct, and it makes those tasks slower.
- **Judgment.** It will strike whatever the agent tells it to strike. Our agents
  rejected too much. Give the agent your playbook, and tell it what you concede.
- **Old `.doc` files.** It reads the text, headings, lists and tables. For anything
  where the exact layout of an old file matters, convert it in Word first.
- **We have not re-run the benchmarks on 0.19.0.** The numbers this week come from
  versions 0.12 to 0.16.

## The test I would run

Take the worst document in your drawer: the one with four rounds of markup from
three authors, a table that breaks, and numbering that restarts. Ask your current
AI tool for a counter-markup. Then open the result in Word and check three things.

1. Review → Reviewing Pane. Are the other side's changes still there, under their
   name?
2. Accept All on a copy. Does the text become what you meant?
3. Does Word open the file without offering to repair it?

Then do the same with jubarte. If it fails where the other passes, tell us. The
issue tracker is public, and a document that breaks the tool is the most useful
thing anyone can send.

Code, releases and the issue tracker: https://github.com/jandira-tech/jubarte
Every page of 808 documents rendered beside Word: https://jandira-tech.github.io/neurotic_docx_bench/
The agent transcripts for the Haiku and GLM runs: https://huggingface.co/datasets/arthrod/redline-bench-jubarte-trajectories
Every DeepSeek run on both benchmarks, file by file: https://huggingface.co/datasets/arthrod/redline-bench-deepseek-trajectories
