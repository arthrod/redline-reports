# Day 5 · 70,000 characters of thinking, and no answer

MAIN POST:

In one in three of my contract runs, the AI stopped mid-thought, after writing about 70,000 characters of reasoning and not one word of answer.

This week's runs used Claude Code, Anthropic's agent, with models that are not Claude: DeepSeek and NVIDIA's Nemotron. I read the logs of more than 63,000 model responses. Three things surprised me.

First, Claude Code sends Claude's settings to every model: "think adaptively, effort high, stop at 16,384 tokens." The other models accepted them. DeepSeek decided for itself when to think. It skipped thinking on one response in six and thought for over 20,000 characters on one in fourteen. Nemotron thought before every single step.

Second, the ceiling. DeepSeek's reported output never went past 6,897 tokens. 358 responses stopped exactly there, almost all of them still thinking, with no text and usually no action. A third of the runs hit it at least once. The agent then has to try again, with that unfinished thought still in its memory.

Third, the counting. The provider reported zero thinking tokens on every response. Its output counts look about 2.4 times too small next to the text actually written. And it reported the expensive part of the input twice.

Where my tool fits: with jubarte the model took about 40 steps per contract instead of 70, and its typical thought shrank from about 1,800 characters to about 700. A redline that took several steps of hand-written Word markup became one command, so the model had less to reason about. That is where the time and token savings on Monday came from.

Why a lawyer should care: when you buy an agent, you buy the model, the harness around it, and the provider's meter. All three shape the bill and the work, and the meter can be wrong.

Disclosure: jubarte is mine. I have no relationship with Anthropic, DeepSeek or NVIDIA.

Links in comments. Does anyone on your vendor's side read the raw logs?

COMMENT:

The harness article: https://github.com/arthrod/redline-reports/blob/main/harness/report.md
The six cohorts: https://github.com/arthrod/redline-reports/blob/main/reports/jubarte-six-cohorts.md
jubarte: https://github.com/jandira-tech/jubarte

In plain English. A harness is the program that runs the AI model as an agent: it hands the model the files, runs its commands, and feeds back the results. "Thinking" is text the model writes to itself before answering. You pay for it, and you rarely see it. A token limit cuts the model off; if it is cut off mid-thought, it produces nothing usable.

Nitty-gritty:
- Every request carried `thinking: adaptive`, `effort: high`, `max_tokens: 16384`, and `clear_thinking` with `keep: all` (earlier thinking stays in context).
- DeepSeek thought on 82% to 87% of responses. Median thought when thinking: 1,788 characters with the scripts, 698 with jubarte 0.14, 746 with 0.15.
- Stops at the limit: 358 DeepSeek responses, all at exactly 6,897 reported tokens. Median 70.8k thinking characters, no visible text, a tool call in 12% to 15%. Nemotron stopped at the requested 16,384 (66 times).
- DeepSeek reports about 10 characters per output token; Nemotron, about 4. 16,384 ÷ 6,897 = 2.38, which matches the gap. My reading, not proven: the limit works, and the count is on another scale.
- `thinking_tokens` was 0 on all 63,274 responses. DeepSeek's thinking blocks were all unsigned; Nemotron's were signed.

VISUAL SUGGESTIONS:
6,897 | THE CEILING DEEPSEEK NEVER CROSSED | 358 responses stopped there, mid-thought
70→40 | STEPS PER CONTRACT WITH JUBARTE | and the typical thought shrank from 1,788 to 698 characters
0 | THINKING TOKENS THE PROVIDER REPORTED | on 63,274 responses, 91% of which contained thinking

OPEN QUESTIONS FOR ARTHUR:
1. Friday is now the harness article in plain words. The survey of other harnesses' Word skills is out of scope for this week.
2. This post names Anthropic, DeepSeek and NVIDIA. Its tone is factual, but consider sending the harness article to the Claude Code team and to Synthetic before posting.
