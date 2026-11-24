# jubarte inside an agent harness: what the runs measured, what they cost, and what each harness ships today

For the people who maintain Codex, Grok Build, Qwen Code, Trae, MiniMax Code, DeepSeek's terminal agents, Z Code and Claude Code, and the Word skills that ship with them. Also for the teams behind RedlineBench and Harvey LAB.

Disclosure: Arthur Souza Rodrigues writes jubarte and ran every trial below.

**In one paragraph.**
- We replaced RedlineBench's own Word tooling with jubarte 0.14 and re-ran the tasks with the same model, brief and grader.
- On 120 tasks never used to tune the skill, no score difference was detected: 0.500 vs 0.502.
- Agent time halved (18.3 to 9.1 minutes), turns fell from 70 to 37, and output tokens from 44.0k to 20.7k.
- Getting one clean comparison took 716 runs on 0.14 alone. The whole archive (1,357 runs) would list at $702 on DeepSeek's prices and $9,679 on Claude Opus 5.5.
- Later binaries on Harvey's benchmark went the same direction, with smaller savings.
- jubarte 0.19.0 is Apache-2.0, so it can ship inside a proprietary skill or container.

## 1. What each harness ships for Word today

Checked 2026-11-22 against each project's default branch.

| Harness | Word skill it ships | What the skill uses | Writes tracked changes? |
|---|---|---|---|
| Codex | none in `openai/codex` (skill samples) or `openai/plugins` | none | no tool |
| OpenAI's skills catalog | the curated `doc` skill is no longer in `openai/skills/.curated` (commit 49f948f); the repository says it is deprecated in favour of `openai/plugins` | n/a | n/a |
| Qwen Code | none among the bundled skills (`packages/core/src/skills/bundled`) | none | no tool |
| DeepSeek TUI (`Hmbown/DeepSeek-TUI`) | `docx` (19 lines), with `document` and `documents` as aliases | "use python-docx/pandoc when available" | no: python-docx writes no `w:ins` or `w:del` |
| MiniMax Code (`mcode`) | `packages/local-runtime/assets/skills/docx` (261 lines) | .NET OpenXML SDK scripts, LibreOffice and pandoc for some routes | only if the model writes `w:ins` and `w:del` through the SDK |
| MiniMax skills catalog | `skills/minimax-docx` (274 lines) | .NET OpenXML SDK, with `TrackChangesSamples.cs` | same |
| Trae (community skills) | `docx-diff-comment` | pandoc, python-docx, unpack/comment/pack scripts | no: adds comments only |
| Grok | built-in "Word Documents" skill (described at x.ai/news/grok-skills) | not published | unknown |
| Grok Build marketplace (`xai-org/plugin-marketplace`) | no Word plugin | n/a | n/a |
| Z Code | supports skills and plugins (zcode.z.ai/docs); built-in list not checked from here | unknown | unknown |
| Claude Code | Anthropic's `docx` skill | LibreOffice, Poppler, pandoc, docx-js; the model hand-writes `w:ins`, `w:del` and comment ranges | only by hand-written XML |

In every open skill above, a tracked change exists only if the model writes the markup. That is where the control arm's extra turns go: on Harvey's first ten pairs the control arm spent about 190 of 335 minutes rebuilding a redline pipeline in Python.

With jubarte the edit is one command that names a paragraph and an anchor:

```sh
jubarte edit contract.docx -p p12 --anchor "thirty days" --content "forty-five days" --author "Maria Souza"
```

A refusal exits 3, writes nothing, and names the cause (`ANCHOR_NOT_FOUND`, `AMBIGUOUS_ANCHOR` with the count, `STALE_SOURCE`, `EXISTING_REVISIONS`).

## 2. The 0.14 result (RedlineBench, Claude Code, DeepSeek-V4.1-Flash)

| Per task, 120 held-out tasks | Benchmark's scripts | jubarte 0.14 | Change |
|---|---:|---:|---:|
| Score | 0.500 | 0.502 | +0.002 (95% CI −0.029 to +0.032) |
| Agent minutes | 18.3 | 9.1 | −50% |
| Turns | 70 | 37 | −47% |
| Input tokens | 2.58 M | 1.39 M | −46% |
| Uncached input | 228 k | 158 k | −31% |
| Output tokens | 44.0 k | 20.7 k | −53% |
| At Claude Opus 5.5 list | $2.26 | $1.29 | −43% |

The control is one job, `deepseek-full-b`. It never ran 9 of the 140 tasks and one more has only a panel grade, so the full set is 130 tasks and the held-out set 120.

Other full-length arms on the same control:

| Arm (binary) | Tasks | Score difference | Input tokens per task, jubarte vs control | Minutes per task, jubarte vs control |
|---|---:|---|---:|---:|
| ds-v12, all 130 tasks (0.14.0) | 130 | +0.004 (−0.025 to +0.032) | 1.39 M vs 2.54 M | 9.2 vs 18.3 |
| ds-v9, held-out (0.14.0) | 120 | −0.024 (−0.058 to +0.008) | 1.50 M vs 2.58 M | 11.0 vs 18.3 |
| study-v14, held-out (0.14.0) | 106 | −0.002 (−0.028 to +0.025) | 1.28 M vs 2.63 M | 10.9 vs 18.4 |
| study-v14b (0.15.0) | 125 | −0.003 (−0.028 to +0.023) | 1.24 M vs 2.57 M | 10.1 vs 18.4 |

No full-length arm showed a score difference whose interval excluded zero (no equivalence margin was tested). One short arm did: `jubarte-study-v13`, 27 tasks, −0.090 (−0.149 to −0.035). The efficiency held in every arm, that one included.

**The development set overstated the gain.** On the 10 tuning tasks the control ran (of 12), DeepSeek drafts scored up to 0.618 against 0.552; on the 120 held-out tasks the gain was gone. On Nemotron 30B-A3B, 10 of 11 drafts scored below the control on all 12 tuning tasks (from 0.059 against 0.401; one v3 trial has no grade, so v3's mean covers 11). The binary was the same in every draft and one draft (v9, 0.425) beat the control. The skill text is what changed by design, but each draft ran once per task and a regrade moves a trial's score by 0.108 on average, so part of the spread among drafts may be run and grading variation. The control used the benchmark's own scripts, so the gap to it also reflects a different tool path. My read: keep a Word skill short for small models.

## 3. What it took, and what it cost

| | jubarte 0.14 arms | Whole RedlineBench archive |
|---|---:|---:|
| Runs with a result | 716 | 1,357 |
| Jobs | 30 | 49 |
| Run time, summed | 157.8 hours | 414.5 hours |
| Input tokens | 1.43 B | 3.29 B |
| Output tokens | 21.1 M | 46.2 M |
| Agent turns | 35,496 | 78,524 |
| Tool calls | 38,811 | 82,572 |
| Calendar | Oct 26 to 30 | Oct 25 to 31 |

Each arm in section 2 is one run per task. The 716 were needed to build the skill (22 drafts across two models), run the held-out arms, and recover from a full disk, a killed process and a Docker image deleted mid-run.

The same archive at today's list prices:

| Price list | Archive | Per task, control | Per task, jubarte 0.14 |
|---|---:|---:|---:|
| DeepSeek V4.1 Flash, first-party peak | $702 | $0.135 | $0.079 |
| Claude Sonnet 5.5 | $4,839 | $1.13 | $0.64 |
| Claude Opus 5.5 | $9,679 | $2.26 | $1.29 |

Cache reads are priced at the cache rate and cache writes are excluded, so the Claude rows are floors. 91% of the control's input was cache reads; they are about 21% of its bill at Opus prices. Billed as ordinary input, the same task would list at about $11.20, five times more. Grading is a second bill on top, one LLM call per rubric pass per trial.

What actually happened to the budget: runs on a flat Synthetic subscription paused at 4% and 0% credit. OpenRouter returned 402. A DevPass allowance ran out. A judge model (gpt-5.6-luna) was dropped after ten minutes on cost. The one study with a confirmed bill (Harvey LAB on 0.17, 88 trials, self-hosted MI355X) cost $100; its 1.48 B recorded input tokens would list at $6,175 on Opus 5.5.

For a harness team: one 140-task sweep with a frontier model at list price is about $317 with the benchmark's scripts and $181 with jubarte. The missing controls below are each one or two sweeps.

## 4. By harness

### Codex

What we have: 41 trials with jubarte 0.15 through a LiteLLM proxy, hardest tasks first, and no plain-Codex control. Mean 0.160, against 0.202 for plain Claude Code and 0.199 for pi with jubarte on the same tasks. After a "continue" nudge (18 trials): mean 0.259, no gate failures, against 0.285 for plain Claude Code. Codex wrote 40k to 126k output tokens per trial, more than plain Claude Code.

These 41 trials are in `redline-bench-tree-2026-11-02` of the private local archive (`DATA-AUDIT.md`, section 2). They can be read through its public copy in the six-cohorts dataset since Nov. 23, but they are in no documented trial table. The plain Claude Code figures beside them were not re-derived on the `deepseek-full-b` control alone.

What we can say without a control: Codex has no Word skill today, `codex mcp add jubarte -- uvx --from 'jubarte-docx[mcp]' jubarte-mcp --root .` adds one, and the token halving in section 2 was measured in Claude Code, against plain Claude Code as the control. The pi result compares a different harness with plain Claude Code, so it does not isolate the tool.

The run we would like to do with you: plain Codex against Codex with jubarte, 140 tasks, a current GPT model. About two sweeps.

### Claude Code

Every paired run used Claude Code. Anthropic's `docx` skill installs LibreOffice, Poppler, pandoc and Node with docx-js, about 850 MB together, against 36 MB for jubarte (measured 2026-10-04 on Ubuntu 24.04, by the jubarte author). Script-by-script replacement: `docs/adoption/anthropic-docx-skill.md` in the jubarte repository.

Install: `claude mcp add --transport stdio jubarte --scope project -- uvx --from 'jubarte-docx[mcp]' jubarte-mcp --root .`

### pi

jubarte 0.15 in pi: 0.486 against 0.494 for plain Claude Code on 134 tasks (the earlier control, which took 9 of those tasks from `deepseek-full`; not re-derived), with 15.0k output tokens against 44.8k. On the OpenAI-compatible route with `reasoning_effort: high`, the same model wrote about 169k output tokens per trial, 12 times the Anthropic route, for the same number of turns. The route mattered more than the tool. These trials are in `redline-bench-tree-2026-11-02` of the private local archive, which has had a public copy in the six-cohorts dataset's `archive/` since Nov. 23. They are in no documented public trial table.

### Cline

One smoke trial on 0.15: 0.091. Cline did not read the instruction file on its own. Listed so that nobody thinks it was hidden.

### DeepSeek TUI, Qwen Code, MiniMax Code, Trae, Grok Build, Z Code

Not benchmarked. Each loads an Agent Skills `SKILL.md`. The drop-in skill is `skills/jubarte-documents/SKILL.md` in the jubarte repository (a 120-line cut for small models is prepared with the pull requests). Where to put it, as each project documents:

| Harness | Skill location |
|---|---|
| Qwen Code | `~/.qwen/skills/<name>/SKILL.md` (personal) or `.qwen/skills/<name>/SKILL.md` (project); `QwenLM/qwen-code` `docs/users/features/skills.md` |
| Trae | `~/.trae/skills/<name>/SKILL.md` or `.trae/skills/<name>/SKILL.md`; `trae-community/trae-skills` README |
| Grok Build | `~/.grok/skills/` or a plugin's `skills/` directory; docs.x.ai, "Skills, plugins and marketplaces" |
| Codex | `.agents/skills/` in the working directory and each parent up to the repository root; developers.openai.com/codex/skills |
| DeepSeek TUI (Codewhale) | `~/.codewhale/skills/` by default, or `~/.agents/skills/`; `crates/skills/src/lib.rs` |
| MiniMax Code | workspace `.minimax/skills/`, `.agents/skills/` or `.claude/skills/`; `packages/tui/CHANGELOG.md` and the bundled `skill-creator` skill |
| Z Code | `~/.zcode/skills/<name>/SKILL.md` (user level), as reported by third-party install guides, which also list `.zcode/skills/` and `~/.agents/skills/`; ZCode's own page is zcode.z.ai/en/docs/skill, not fetched from here. Its built-in Word support was not checked |

Qwen Code also converts Gemini CLI extensions, so `qwen extensions install https://github.com/jandira-tech/jubarte` should load jubarte's MCP server (not yet tested).

## 5. What the graders can and cannot see

- **Harvey LAB reads accepted text.** Its extractor runs `pandoc --track-changes=accept`, so a redline and a clean rewrite look the same to the judge. One control-arm "redline" had 39 strikethrough formatting runs and no `w:ins` or `w:del`, and scored 0.900.
- **RedlineBench reads the markup.** Its judge gets an annotated view with deletions, insertions and comment markers. An earlier version of this report said both graders read accepted text; that was wrong for RedlineBench. So the result cannot be blamed on a grader that never sees the markup. Whether this judge rewards better markup has not been tested, so grading insensitivity is not ruled out.
- **Judges are noisy.** 47 RedlineBench trials were graded twice by GLM-5.3-Flash; the two grades differ by 0.108 on average (median 0.062). List: `data/judge_regrades.csv`. Harvey's judge moves about 0.02 between runs.
- **The RedlineBench judge was one model.** GLM-5.3-Flash, not Crosby's panel, so these scores compare with each other and not with Crosby's leaderboard.

## 6. Where jubarte costs more, or loses

- **Documents that already carry the other side's tracked changes.** On Harvey LAB (jubarte 0.16) several such pairs cost more. In one, 8.9 M tokens against 3.2 M and 22.6 minutes against 13.6. Agents learned the existing-revision rules by experiment.
- **First-turn rewrites.** On RedlineBench turn 1, 0.248 against 0.275 (7 held-out tasks). A paragraph rewrite was marked word by word: 254 spans per trial against 73.
- **Over-striking.** With a one-flag strike, agents rejected more. "Rejects" rubric items: 37 won, 12 lost. "Accepts" items: 8 won, 54 lost (120 held-out tasks).
- **Small models.** On Nemotron 30B, 10 of 11 drafts scored below the control, which used the benchmark's own scripts.
- **Atomic plans.** A 30 to 100 operation plan is refused whole for one bad anchor. `--skip-failed` exists; agents rarely found it.
- **Version.** Runs used 0.14.0 to 0.17.0. 0.19.0 has not been benchmarked.
- **Models.** No frontier model was the agent.

180 reviews written to be biased against jubarte, by non-Claude models with the binary and the trial documents, are in the Harvey archive. Their verified findings are in this list.

## 7. What you would ship

| Channel | Package | Size |
|---|---|---|
| Binary | GitHub release, Linux glibc and musl (x86_64, aarch64), macOS, Windows x86_64 | 36 MB installed, 14 MB download |
| Python | `jubarte-docx` (import `jubarte`), abi3 wheels, Python 3.10+ | |
| Rust | `cargo install jubarte` | |
| Node and browser | `jubarte-wasm` | |
| MCP | `uvx --from 'jubarte-docx[mcp]' jubarte-mcp --root .` | every path confined to `--root` |
| Skill | `skills/jubarte-documents/SKILL.md` | one file |

Licence: Apache-2.0 from 0.19.0. Releases up to 0.18.0 remain AGPL-3.0-only. Every package carries `LICENSE` and `NOTICE`. Bundled fonts keep their own licences (OFL 1.1, Apache-2.0).

## 8. Check it without trusting us

```sh
uvx --from jubarte-docx jubarte read your.docx
uvx --from jubarte-docx jubarte convert your.docx -o your.png --dpi 100
git clone https://github.com/jandira-tech/jubarte && ls jubarte/examples/adoption
```

Data:
- Every RedlineBench and Harvey trial behind sections 2, 3 and 5: https://huggingface.co/datasets/arthrod/redline-bench-deepseek-trajectories
- The 0.14 report with every table above: `reports/jubarte-0.14-redlinebench.md`
- The data audit: `DATA-AUDIT.md`

## 9. What we are asking for

1. Try jubarte as the redline route in your Word skill, on your own evaluation, and tell us the result either way.
2. Run the missing control with us. Codex first: plain against jubarte, 140 tasks, a current model.
3. If it holds up, say so in your skills catalogue or docs. That is how other teams will find it.

Repository and issues: https://github.com/jandira-tech/jubarte
