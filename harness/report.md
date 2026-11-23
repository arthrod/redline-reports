# jubarte inside an agent harness: what two legal benchmarks measured

For the people who maintain Claude Code, Codex, pi, Cline, Gemini CLI and the Word
skills that ship with them, and for the teams behind RedlineBench and Harvey LAB.

**In one paragraph.** We replaced each benchmark's own Word tooling with jubarte, one
36 MB binary that writes Word tracked changes directly, and re-ran the tasks with the
same model, brief and grader. Scores stayed inside the noise. Output tokens fell by
about half and wall-clock time by 13% to 51%, across four models and two harnesses.
jubarte 0.19.0 is Apache-2.0 as of 2026-11-21, so it can ship inside a proprietary
skill or container.

## 1. What was run

| Benchmark | Tasks | Harness | Model | jubarte | Control arm |
|---|---|---|---|---|---|
| RedlineBench (Crosby, micro1) | 134 common | Claude Code | DeepSeek-V4.1-Flash | 0.15.0 | the benchmark's Python docx scripts |
| RedlineBench | 134 common | pi | DeepSeek-V4.1-Flash | 0.15.0 | Claude Code with the Python scripts |
| RedlineBench | 41, hardest first | Codex | DeepSeek-V4.1-Flash | 0.15.0 | none (see §4) |
| RedlineBench | 69 and 33 | Claude Code | Claude Haiku 5.5 | 0.12.0 | Python scripts |
| RedlineBench | 40 paired | Claude Code | GLM-5.3-flash | 0.12.0 | Python scripts |
| Harvey LAB, redline deliverables | 90 pairs | Claude Code | DeepSeek-V4.1-Flash | 0.16.0 | LAB's docx skill and its `redline.py` |
| Harvey LAB, document editing | 44 pairs, 16 tasks, up to 3 repeats | Claude Code | DeepSeek-V4.1-Flash, self-hosted | 0.17.0 | LAB's standard workflow |

Runs went through Harbor. The jubarte arm got the binary on `PATH`, the repository's
`SKILL.md` and the `--help` pages. For Harvey LAB both arms kept LAB's docx skill; the
jubarte arm lost `redline.py`, `comments_add.py` and `accept_changes.py` and gained a
six-step how-to.

## 2. Results

### Score

| Run | Tasks | Control | jubarte |
|---|---|---|---|
| RedlineBench, DeepSeek, Claude Code | 134 | 0.494 | 0.492 |
| RedlineBench, DeepSeek, Claude Code, held-out set | 127 | 0.489 | 0.493 |
| RedlineBench, DeepSeek, pi | 134 | 0.494 | 0.486 |
| RedlineBench, Haiku 5.5, first 69 | 69 | 0.394 | 0.427 |
| RedlineBench, Haiku 5.5, second block | 33 | 0.430 | 0.412 |
| RedlineBench, GLM-5.3-flash | 40 | 0.350 | 0.364 |
| Harvey LAB redline tasks | 90 pairs | 0.936 | 0.941 (paired difference +0.006, SE 0.005) |
| Harvey LAB, jubarte 0.17, task-balanced | 44 pairs | 0.925 | 0.923 (difference −0.002, 95% interval −0.026 to +0.022) |

We wanted a score gain and did not get one. Per-task noise on RedlineBench is about
±0.04. Read every row as a tie except Haiku's first 69 (35 wins, 24 losses, 10 ties).

### Tokens and time

| Run | Measure | Control | jubarte | Change |
|---|---|---|---|---|
| RedlineBench, DeepSeek, Claude Code, 134 tasks | output tokens per trial | 44.8k | 20.4k | −54% |
| | input tokens per trial | 2.60M | 1.27M | −51% |
| | uncached input per trial | 234k | 217k | −7% |
| RedlineBench, DeepSeek, pi, 134 tasks | output tokens per trial | 44.8k | 15.0k | −67% |
| | input tokens per trial | 2.60M | 1.42M | −45% |
| RedlineBench, DeepSeek, Claude Code, 127 held-out | agent minutes per trial | 18.6 | 9.2 | −51% |
| RedlineBench, GLM-5.3-flash | minutes per attempt | 102 | 68 | −33% |
| | output tokens per attempt | 0.24M | 0.18M | −25% |
| | tasks finished with a valid score, of 69 | 42 | 59 | |
| Harvey LAB, 90 pairs | tokens per task | 10.4M | 8.9M | −14% |
| | minutes per task | 37.2 | 32.4 | −13% |
| Harvey LAB, jubarte 0.17, 44 pairs | minutes per trial | 28.4 | 26.6 | −6% |
| | input tokens per trial | 17.2M | 16.2M | −6% |
| | output tokens per trial | 143k | 133k | −7% |
| Harvey LAB, first 10 pairs | agent steps | 1,463 | 1,311 | −10% |
| | hard tool failures | 38 | 5 | |

The saving is in output tokens and cache reads. Uncached input barely moves: the
agent still has to read the contract once.

The 0.17 study is the smallest saving of any DeepSeek run. Its trials ran sixteen at a
time on one rented node, and its own write-up says the scheduling prevents a causal
efficiency claim. Read it as the same direction, not as a measured 6%.

**Other models.** Muse Glimmer 30B (44 graded, 0.269) and Qwen 3.8 27B (21 graded,
0.106) were run on RedlineBench with the benchmark's own scripts only. They have no
jubarte arm, so they say how hard the benchmark is for small models and nothing about
jubarte.

Updated 2026-11-23: this paragraph used to say the same of Muse Spark 1.3, and that its
jubarte arm failed at authentication on every trial. Muse has a jubarte arm. Its run
with the benchmark's scripts (52 valid trials, mean 0.385 as first graded) is the
control for 140 jubarte trials run on 16–17 October; regraded by the gpt-6.1-sol panel,
the two score 0.297 and 0.316. Only the first of two jubarte launches on 18 October
failed at authentication. The relaunch ran all 140 tasks, but two judge panels graded
it. FACTS.md has the numbers.

**The exception.** Haiku 5.5 on jubarte 0.12.0 took 26 minutes per attempt against 24
and cost $0.98 per scored task against $0.91. Cached input fell 14%; output did not
move. That was the first skill version. Every run since 0.14 is cheaper and faster.

### Where the tokens go in the control arm

An agent without a redline tool writes one. In Harvey's first ten pairs the control
arm spent about 190 of 335 minutes rebuilding a redline pipeline in Python: unzip,
parse `document.xml`, wrap runs in `w:ins` and `w:del` in schema order, zip, render,
retry. With jubarte the edit is one call that names a paragraph id and an anchor:

```sh
jubarte edit contract.docx -p p12 --anchor "thirty days" --content "forty-five days" --author "Maria Souza"
```

A refusal exits 3, writes nothing, and names the cause: `ANCHOR_NOT_FOUND`,
`AMBIGUOUS_ANCHOR` with the count, `STALE_SOURCE`, `EXISTING_REVISIONS`.

## 3. What the redlines contained

Neither grader looks at tracked-change structure, so these do not show in the score.

- A control-arm "redline" with 39 `w:strike` formatting runs and no `w:ins` or
  `w:del`. The jubarte file for the same task had 38 insertions and 39 deletions.
- A control-arm counter-turn that accepted the other side's markup and re-issued its
  own: 182 insertions, one author. jubarte's kept 191 of theirs and added 89 of ours.
- A control-arm rebuild that left "and Mexico" in a Territory definition it meant to
  narrow. jubarte edited in place.

## 4. By harness

### Codex

What we have: 41 jubarte trials through a LiteLLM proxy, hardest tasks first, no
plain-Codex control. Mean 0.160, against 0.202 for plain Claude Code and 0.199 for pi
with jubarte on the same tasks. Before we added a "continue" nudge, 6 of 23 trials
failed the validity gate, 4 of them by stopping on a message with no tool call. After
it, 18 trials: mean 0.259, 0 gate failures, against 0.285 for plain Claude Code on
the same tasks. Codex wrote 40k to
126k output tokens per trial, more than plain Claude Code.

So we cannot show a Codex gain yet. What we can show for Codex is narrower:

- OpenAI's curated `doc` skill does not cover tracked changes at all. python-docx
  writes no `w:ins` or `w:del`.
- Its install line, `apt-get install -y libreoffice poppler-utils`, adds 1,753 MB to
  a fresh Ubuntu 24.04 container. With python-docx the replaced set is 1,793 MB;
  jubarte is 36 MB.
- Codex issue #38313 asks for page-range rendering and a render timeout.
  `jubarte convert file.docx -o file.png --pages 1-3,7 --timeout 60` does both.
- The token halving above came from the tool, not the harness: it showed in Claude
  Code and in pi with the same model.

Install: `codex mcp add jubarte -- uvx --from 'jubarte-docx[mcp]' jubarte-mcp --root .`

Step-by-step replacement of the `doc` skill:
https://github.com/jandira-tech/jubarte/blob/main/docs/adoption/openai-doc-skill.md

The run we would like to do with you: plain Codex against Codex with jubarte, on the
140 RedlineBench tasks, with a current GPT model.

### Claude Code

All paired runs used Claude Code. With DeepSeek: same score, 54% fewer output tokens,
51% less time. Anthropic's `docx` skill installs LibreOffice, Poppler, pandoc and
Node with docx-js, 850 MB together; the model hand-writes `w:ins` and `w:del` and
pastes comment range markers itself.

Install: `claude mcp add --transport stdio jubarte --scope project -- uvx --from 'jubarte-docx[mcp]' jubarte-mcp --root .`

Script-by-script replacement of the `docx` skill:
https://github.com/jandira-tech/jubarte/blob/main/docs/adoption/anthropic-docx-skill.md

### pi

pi with jubarte matched plain Claude Code on score (0.486 against 0.494) with a third
of the output tokens (15.0k against 44.8k). On the 12 tasks where plain pi also ran:
0.312 plain, 0.406 with jubarte, 43.6k against 19.6k output tokens. A small sample.

One finding for pi itself: the route mattered more than the tool. On the
OpenAI-compatible route with `reasoning_effort: high`, the same model wrote about
169k output tokens per trial, 12 times the Anthropic route, for the same number of
turns.

### Cline

One smoke trial: 0.091. Cline did not read the instruction file on its own. Not a
result, and listed so that nobody thinks we hid it.

### Gemini CLI

Not benchmarked. The extension installs with
`gemini extensions install https://github.com/jandira-tech/jubarte`.

### Harvey LAB's harness and RedlineBench's tooling

For benchmark owners: your control tooling is where the agent's budget goes. On LAB
the agent rebuilds a redline engine per task; on RedlineBench it wrote twice the
output tokens to reach the same rubric score. A task set that ships a real redline
tool measures legal judgment and not OOXML authoring. Both graders also read accepted
text, so neither can fail a deliverable for not being a redline. `jubarte changes
FILE --json` lists every tracked change with its author and kind, if you want that
check.

## 5. Where jubarte costs more, or loses

- **Documents that already carry the other side's tracked changes.** On Harvey LAB
  several such pairs cost more with jubarte (one: 8.9M tokens against 3.2M, 22.6
  minutes against 13.6). Agents learned the existing-revision rules by experiment.
- **First-turn rewrites.** On RedlineBench turn 1, 0.258 against 0.280. A paragraph
  rewrite on the `existing_revisions: keep` path was marked word by word: 254 spans
  per trial against 73.
- **Over-striking.** With a one-flag strike, agents rejected more. "Rejects" rubric
  items: 47 won, 12 lost. "Accepts" items: 9 won, 62 lost.
- **Atomic plans.** A 30 to 100 operation plan is refused whole for one bad anchor.
  `--skip-failed` exists; agents rarely found it.
- **Version.** Runs used 0.12.0 to 0.16.0. 0.19.0 has not been benchmarked.
- **Models.** No frontier model was run. The judge for the DeepSeek RedlineBench
  runs was one model (GLM-5.3-Flash), not Crosby's panel, so those scores are
  comparable to each other and not to Crosby's leaderboard.

We also ran 180 reviews written to be biased against jubarte, by non-Claude models
with the binary and the trial documents. Their verified findings are in the list
above.

## 6. Licence

jubarte is **Apache-2.0 from 0.19.0**. Releases up to 0.18.0 remain AGPL-3.0-only.
Every crate, wheel, npm package and release archive carries `LICENSE` and `NOTICE`.
Bundled fonts keep their own licences (OFL 1.1, Apache-2.0). You can vendor the
binary into a skill, a container image or a closed product.

## 7. What you would ship

| Channel | Package | Size |
|---|---|---|
| Binary | GitHub release, Linux glibc and musl (x86_64, aarch64), macOS, Windows x86_64 | 36 MB installed, 14 MB download |
| Python | `jubarte-docx` (import `jubarte`), abi3 wheels, Python 3.10+ | 22 MB |
| Rust | `cargo install jubarte` | |
| Node and browser | `jubarte-wasm` | |
| MCP | `uvx --from 'jubarte-docx[mcp]' jubarte-mcp --root .` | every path confined to `--root` |
| Skill | `skills/jubarte-documents/SKILL.md` | one file |

It reads a document as Markdown with an id on every paragraph, change and comment;
edits as tracked changes; replies to and resolves comments; accepts or rejects by id,
author or kind; compares two files into a redline; renders PDF and PNG with its own
layout engine; validates that Word will open the file and that every edit is
tracked; and scrubs authors and metadata. No Word, LibreOffice, pandoc or Node.

## 8. Check it without trusting us

```sh
uvx --from jubarte-docx jubarte read your.docx
uvx --from jubarte-docx jubarte convert your.docx -o your.png --dpi 100
git clone https://github.com/jandira-tech/jubarte && ls jubarte/examples/adoption
```

`examples/adoption/` has one folder per replaced script: the old tool's output beside
jubarte's, a `run.sh` that regenerates both, and a verdict that says where jubarte is
worse. Rendering is scored page by page against Microsoft Word on 808 documents:
https://jandira-tech.github.io/neurotic_docx_bench/

Agent transcripts for the Haiku and GLM runs (785 trials, with the delivered
contracts): https://huggingface.co/datasets/arthrod/redline-bench-jubarte-trajectories

Full trial directories for the DeepSeek runs on both benchmarks, including the 90 Harvey
pairs and the 0.17 study (trajectories, session logs, delivered files, grades): https://huggingface.co/datasets/arthrod/redline-bench-deepseek-trajectories

## 9. What we are asking for

1. **Try it as the redline route in your Word skill**, on your own evaluation, and
   tell us the result either way.
2. **Run the missing control with us.** Codex first: plain against jubarte, 140
   tasks, a current model.
3. **If it holds up, say so.** A line in your skills catalogue or docs is how other
   teams will find it.

Repository and issues: https://github.com/jandira-tech/jubarte
