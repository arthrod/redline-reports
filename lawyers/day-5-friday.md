# Day 5 · Seven agents, one missing tool

MAIN POST:

I checked what seven AI coding agents, plus MiniMax's skills catalog, ship for Word documents. None of the open ones gives the model a command that makes a tracked change. The model writes the markup itself.

Here is what each one does today, when you ask it to redline a contract.

Codex: no Word skill in OpenAI's open repositories. The old curated one is gone.
Qwen Code: none bundled.
DeepSeek's terminal agent: a 19-line skill that says use python-docx or pandoc if available. Neither writes tracked changes.
MiniMax Code and MiniMax's skills: Microsoft's .NET OpenXML SDK. Tracked changes, if the model writes them.
Trae's community skill: compares two files and adds comments. No tracked changes.
Grok: a built-in Word skill whose source is not public.
Z.ai's Z Code: supports skills; I found no Word skill to check.

Monday's numbers sit next to that gap: 18.5 minutes a task without a redline engine, 9.2 with one. Those arms ran on different days, so I report the gap, not its cause.

jubarte 0.19 is out under Apache-2.0, so a lab can ship it inside a closed product. I drafted a drop-in skill for each harness that accepts contributions.

Honest reading: the benchmarks ran on 0.14 to 0.16, not 0.19. No frontier model was the agent. Codex never ran without jubarte, so I have no Codex control.

Disclosure: jubarte is mine.

Links in comments. If you maintain one of these agents: would you run the missing Codex control with me?

COMMENT:

jubarte: https://github.com/jandira-tech/jubarte
The harness report, with every skill's source and what it calls: https://github.com/arthrod/redline-reports/blob/main/harness/report.md
The drop-in skills: [links to the pull requests, once open]

The audit, by repository and commit:
- `openai/codex` (codex-rs skill samples) and `openai/plugins`: no docx skill.
- `openai/skills` `.curated/`: no `doc` skill at commit 49f948f.
- `QwenLM/qwen-code`: no docx skill among the bundled skills.
- `Hmbown/DeepSeek-TUI` `crates/skills/assets/skills/docx/SKILL.md`: 19 lines, python-docx or pandoc.
- `MiniMax-AI/minimax-code` `packages/local-runtime/assets/skills/docx` and `MiniMax-AI/skills` `skills/minimax-docx`: .NET OpenXML SDK with tracked-change samples.
- `trae-community/trae-skills` `skills/docx-diff-comment`: pandoc, python-docx and comment scripts.
- `xai-org/plugin-marketplace`: no Word plugin. Grok's built-in "Word Documents" skill is described on x.ai; its source is not published.
- Anthropic's `docx` skill for Claude Code: LibreOffice, Poppler, pandoc and docx-js, about 850 MB together, against 36 MB for jubarte, measured 4 October on Ubuntu 24.04.

In plain English. A skill is a set of instructions and tools an agent loads when a task needs them. When the skill has no redline tool, the model writes the file format itself. That was the arm with more time and tokens on Monday; the arms ran on different days, so the comparison does not prove the file format was the cause.

VISUAL SUGGESTIONS:
7 | AGENTS CHECKED FOR A WORD SKILL | none of the open ones has a command that makes a tracked change
36 MB | JUBARTE, INSTALLED | about 850 MB for the tools Anthropic's docx skill installs
Apache-2.0 | JUBARTE 0.19 | free to ship inside a commercial product

OPEN QUESTIONS FOR ARTHUR:
1. Post only after the pull requests are open, or reword "I drafted" to match what is live. The PR drafts are in `outreach/prs/` in your local folder, not in this public repo.
2. You listed "mcode" and "minimax code" separately. I read both as MiniMax Code (its CLI is `mcode`) and count MiniMax's skills catalog as a source, not an agent, so the count is seven. If mcode is another product, it becomes eight once checked.
3. Z Code: zcode.z.ai documents skills and plugins, but its built-in skills could not be fetched from here. Check its built-in list before posting the line.
4. Claude Code is the eighth harness and the one every paired run used. It is in the comment and stays out of the headline count, because it was not on your list.
