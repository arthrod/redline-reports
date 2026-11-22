# What Claude Code asks of models that are not Claude

An investigation of 63,274 model responses. They come from the three RedlineBench cohorts that ran Claude Code with non-Claude models (0.14.0 DeepSeek, 0.15.0 DeepSeek, 0.14.0 Nemotron) and from those cohorts' two controls.

For harness maintainers, inference providers, and anyone who prices or benchmarks agents from usage numbers.

Data: [`arthrod/redline-bench-jubarte-six-cohorts`](https://huggingface.co/datasets/arthrod/redline-bench-jubarte-six-cohorts) holds every trial, session logs included.

Disclosure: Arthur Souza Rodrigues writes jubarte, the Word tool under test in the cohorts, and ran every trial. No one at Anthropic, DeepSeek, NVIDIA or Synthetic reviewed this article.

**In short.**

- Claude Code sent Claude's thinking settings on every request, to every model: adaptive thinking, effort high, a 16,384-token output limit, and a rule to keep earlier thinking in context. The non-Claude backends accepted all of it.
- Thinking was dynamic. DeepSeek skipped thinking on one response in six and thought for over 20,000 characters on one in fourteen. Nemotron thought on every response.
- DeepSeek's reported output never exceeded 6,897 tokens. Every one of its 358 responses that stopped for length stopped at exactly 6,897, nearly all of them mid-thought, with no visible text.
- The provider's usage numbers do not add up. DeepSeek's output tokens look about 2.4 times too small, `thinking_tokens` is always 0, and uncached input is reported a second time as cache writes, which inflates Harbor's input totals.
- jubarte cut DeepSeek's thinking in two ways at once: half as many responses, and a shorter median thought per response (698 characters against 1,788). On Nemotron it cut neither.

Every number here comes from `uv run python scripts/harness.py`, which reads `data/harness_requests.csv` and `data/harness_responses.parquet`. Both were extracted from the Claude Code session logs (`agent/sessions/projects/-app/*.jsonl`) in the public trial dataset. A response is one API message. Claude Code writes a response as several log lines, one per content block, and lines that share a message id are merged here.

## 1. The request is Claude's, whatever the model

Claude Code 2.1.310 talks to every model through the Anthropic Messages API (`/v1/messages`).

- DeepSeek-V4.1-Flash-1017 was served by Synthetic.
- Nemotron 3.5 Lightning 30B-A3B was served by a local server on one RTX 5090.

Each of the 63,380 logged requests carried the same parameters:

| Parameter | Value sent |
|---|---|
| `thinking` | `{"type": "adaptive", "display": "updates"}` |
| `output_config.effort` | `high` |
| `max_tokens` | `16384` |
| `context_management` | `{"edits": [{"type": "clear_thinking_20251015", "keep": "all"}]}` |

The beta header included interleaved thinking, the effort control and thinking-token counting. None of these settings is DeepSeek's or NVIDIA's own vocabulary. They are Claude's settings, and both backends accepted them without an error.

What each backend did with them:

- **Adaptive thinking** leaves it to the model whether to think on a turn, and for how long. DeepSeek behaved that way: thinking varied from none to tens of thousands of characters (section 2). Nemotron thought on every response.
- **`keep: "all"`** tells the API to keep earlier thinking blocks in the context. Claude Code sent each trial's earlier thinking back to the model on every request, so a long thought early in a trial is paid for again, as input, on every later turn.
- **Effort** has no published meaning for these models. Whether either backend acted on `high` cannot be told from the logs.

## 2. Thinking was dynamic, and large

Per response:

| Arm | Responses | With thinking | Median characters, when thinking | 90th percentile | Longest |
|---|---:|---:|---:|---:|---:|
| 0.14.0 DeepSeek | 22,105 | 83.8% | 698 | 15,367 | 78,130 |
| 0.15.0 DeepSeek | 4,943 | 86.5% | 746 | 16,020 | 75,983 |
| DeepSeek control | 9,145 | 82.4% | 1,788 | 17,842 | 77,775 |
| 0.14.0 Nemotron | 12,906 | 100% | 356 | 4,945 | 71,653 |
| Nemotron control | 14,175 | 100% | 275 | 4,675 | 73,648 |

How long DeepSeek thought, across all three DeepSeek arms:

| Thinking length (characters) | Share of responses |
|---|---:|
| none | 16.2% |
| 1 to 200 | 20.6% |
| 201 to 1,000 | 23.4% |
| 1,001 to 5,000 | 21.9% |
| 5,001 to 20,000 | 10.8% |
| over 20,000 | 7.2% |

**The trial's opening is cheap; the middle is not.** DeepSeek thought on only 22% to 54% of first responses, usually for under 200 characters. The long thinking clusters in responses 7 to 21, when the agent is reading the contract and planning edits. There the 90th percentile reaches 30,578 characters in the 0.14.0 jubarte arm and 15,212 in the control. Later in the trial the control keeps thinking hard: its median is 1,746 characters in responses 22 to 51, against 691 with jubarte.

**Thinking is most of what the model writes.** Per trial, thinking was 86% to 89% of DeepSeek's characters and 75% to 83% of Nemotron's. The rest, the visible text and tool inputs, is what the agent acts on.

| Arm | Trials | Responses per trial | Thinking per trial | Visible text and tool input per trial | Thinking share |
|---|---:|---:|---:|---:|---:|
| DeepSeek control | 131 | 69.8 | 366.8k characters | 51.4k | 87.7% |
| 0.14.0 DeepSeek | 560 | 39.5 | 180.2k | 29.4k | 86.0% |
| 0.15.0 DeepSeek | 138 | 35.8 | 173.9k | 21.9k | 88.8% |
| Nemotron control (140 tasks) | 140 | 101.2 | 205.9k | 69.9k | 74.7% |
| 0.14.0 Nemotron (12 tasks) | 131 | 98.5 | 198.9k | 40.6k | 83.1% |

## 3. How a Word tool reduced thinking

With DeepSeek, jubarte halved thinking per trial (366.8k to 180.2k characters) through two effects that multiply:

1. **Fewer responses.** 69.8 per trial fell to 39.5. A tracked change that took the control several steps (unzip, edit XML, rezip, check) is one jubarte command.
2. **Shorter thoughts per response.** The median thought fell from 1,788 to 698 characters. The model spent less time reasoning about Word's XML because it no longer wrote it.

The share of output that is thinking did not change (about 87%). So the saving came from removing work, not from the model thinking less about the same work.

With Nemotron, neither effect appeared. Responses stayed near 100 per trial and thinking near 200k characters. Visible output fell, so the thinking share rose from 75% to 83%. Nemotron thinks on every response regardless, and the jubarte skill is long. This is the cohort where jubarte lost on score (see `reports/jubarte-six-cohorts.md`).

One caveat: the Nemotron arms cover different task sets (12 tasks against 140), so this comparison is not paired.

## 4. A fixed output ceiling at 6,897 tokens

Responses that stopped because they reached the output limit:

| Arm | Stopped at the limit | Reported output tokens on those | Median thinking characters | Median visible characters | With a tool call | Trials with at least one | Share of the arm's reported output |
|---|---:|---|---:|---:|---:|---:|---:|
| 0.14.0 DeepSeek | 240 | exactly 6,897 | 70,802 | 0 | 15% | 33.9% | 13.5% |
| 0.15.0 DeepSeek | 52 | exactly 6,897 | 70,917 | 0 | 12% | 31.9% | 12.8% |
| DeepSeek control | 66 | exactly 6,897 | 70,456 | 0 | 14% | 30.5% | 7.8% |
| 0.14.0 Nemotron | 24 | exactly 16,384 | 61,579 | 0 | 17% | 10.7% | 4.6% |
| Nemotron control | 42 | exactly 16,384 | 64,942 | 0 | 5% | 21.4% | 6.8% |

Nemotron stops where Claude Code asked: 16,384. DeepSeek reports 6,897 every time. Its largest output on a response that did not stop for length was 6,892, so nothing in 36,193 responses crossed 6,897.

The likely explanation is in section 5. If DeepSeek's reported output tokens are about 2.4 times smaller than the tokens actually generated, then 16,384 real tokens show up as about 6,900. The capped responses hold about 70,800 characters of thinking, which fits 16,384 tokens at about 4.3 characters each. So the provider probably applies the requested limit correctly and reports the count on a different scale.

Either way, the effect on the agent is the same:

- **Wasted turns.** A capped response is almost always an unfinished thought: no visible text, and a tool call in only 12% to 17% of them. The agent then has to try again.
- **They are common.** About a third of DeepSeek trials hit the limit at least once.
- **They cost more than their count suggests.** With `keep: "all"`, the 70,000 characters of unfinished thinking stay in the context and are re-read on every later turn.

jubarte did not reduce how often a trial hits the limit with DeepSeek (31.9% to 33.9% of trials, against 30.5% in the control). It concentrates more of the arm's output there (13.5% against 7.8%), because everything else shrank.

## 5. The usage numbers do not add up

Three anomalies, each checked across every response.

**Thinking is never counted separately.** `usage.output_tokens_details.thinking_tokens` is 0 on all 63,274 responses, for both models, although 91% of the responses contain thinking. Thinking is included in `output_tokens`, so anyone reading the field would conclude these agents never think.

**DeepSeek's output tokens look about 2.4 times too small.** Characters per reported output token:

| | Fitted tokens per thinking character | Fitted tokens per visible character | Implied characters per token |
|---|---:|---:|---:|
| DeepSeek (35,835 responses) | 0.0989 | 0.0871 | about 10 to 11 |
| Nemotron (27,015 responses) | 0.2537 | 0.2522 | about 4 |

On plain responses with no thinking and more than 2,000 visible characters, DeepSeek's median is 9.92 characters per reported token. English text and JSON run about 3 to 4.5 characters per token for any modern tokenizer. Nemotron's 4 is in range; DeepSeek's 10 is not. The ratio between the two, about 2.5, matches the 16,384 / 6,897 = 2.38 ceiling ratio in section 4.

So DeepSeek's `output_tokens` is either undercounted or counted on a different basis. These logs cannot tell which. Any per-token price, budget or "tokens saved" figure built on that field inherits the scale, the DeepSeek figures in the cohort report included. The comparisons between arms still hold, because both arms are measured the same way.

**Uncached input is reported twice.** On 36,192 of 36,193 DeepSeek responses, `cache_creation_input_tokens` equals `input_tokens` exactly. Nemotron reports no caching at all. Harbor's trial total adds input, cache creation and cache reads. For DeepSeek it therefore counts the uncached part twice: about 110k extra tokens per trial, 4% to 8% of the total.

The cohort report prices DeepSeek from the logs, counting uncached input once:

| Per trial | Cached input | Uncached input | Cached share |
|---|---:|---:|---:|
| DeepSeek control | 2.32M | 114k | 95.3% |
| 0.14.0 DeepSeek | 1.21M | 107k | 91.9% |
| 0.15.0 DeepSeek | 1.05M | 108k | 90.7% |

Two consequences:

- **The bill falls less than the tokens.** jubarte removed re-reads of the conversation, which are cache hits. The uncached input, billed at full price, barely moved. At OpenRouter's price for this model ($0.15 in, $0.003 cached, $0.60 out per million, fetched 2026-11-22) a trial fell from $0.051 to $0.033 (−35%; $0.102 to $0.066 at the weekday peak rate), while total input fell by about half.
- **Harbor's totals overstate the cache miss rate.** Read naively, they put the DeepSeek control's cache share at 91% instead of 95%.

## 6. Thinking blocks without signatures

Anthropic signs each thinking block. The API checks the signature when the block comes back in a later request, so the model cannot be fed altered reasoning.

- All 32,208 DeepSeek thinking blocks carry an empty `signature`.
- All 27,081 Nemotron thinking blocks carry one.
- There were no `redacted_thinking` blocks.

With `keep: "all"`, Claude Code returned these unsigned blocks to the provider on every request, and Synthetic accepted them. Two things follow, neither of them tested here:

- A session that starts on such a provider and is switched to Claude mid-conversation would send unsigned thinking to an API that checks signatures.
- Nothing upstream verifies that the reasoning in the context is the reasoning the model produced.

## 7. What to take from this

For harness maintainers:

- **Settings meant for Claude reach every model.** Claude Code does not adapt `thinking`, `effort` or `max_tokens` to the backend. For a model that always thinks, adaptive thinking is a no-op. For a model with a different token scale, the 16,384 limit is not what it seems.
- **Watch for length-limited thoughts.** A response with 70,000 characters of thinking and no visible text is a lost turn that stays in context. A harness could detect a `max_tokens` stop with no text or tool call and drop that thinking before the next request, instead of keeping all of it.
- **Tools cut thinking.** The largest saving in these runs came from giving the model a tool that turned a multi-step job into one step. The model then had less to reason about on each turn, as well as fewer turns.

For providers that implement the Messages API:

- Report `thinking_tokens`.
- State the tokenizer behind `output_tokens`.
- Do not report uncached input as cache creation unless it was written to a cache.
- Sign thinking blocks, or document that they are unsigned.

For anyone who benchmarks or prices agents:

- **Count from the response logs**, not from harness totals.
- **Check a provider's characters per token** before converting its usage into money.
- **Compare arms on the same provider and the same scale.** The DeepSeek arms here are comparable with each other. Their absolute token counts are not comparable with Nemotron's or Claude's.

## 8. Limits

- Two backends, one harness version (Claude Code 2.1.310), one benchmark.
- The Muse Spark 1.3 and Harvey cohorts are not covered. Muse's control arm has no session logs (trajectories only), so it cannot be compared response by response, and the Harvey runs were not extracted for this article.
- The 2.4× output scale is inferred from character counts, not from the provider's tokenizer.
- "Stopped at the limit" is the `stop_reason` the provider returned. Whether DeepSeek truncates at 16,384 real tokens is an inference.

## 9. Reproduce

```sh
uv run python scripts/harness.py
uv run pytest tests/test_harness.py   # pins the ceiling, the zero thinking_tokens, the unsigned blocks and the double count
```

Raw session logs are in [`hf://datasets/arthrod/redline-bench-jubarte-six-cohorts`](https://huggingface.co/datasets/arthrod/redline-bench-jubarte-six-cohorts) (`files/redlinebench.parquet`, `path_in_trial` matching `agent/sessions/projects/-app/*.jsonl`), for jobs `jubarte-ds-*`, `jubarte-study-*`, `jubarte-v1` to `jubarte-v11`, `deepseek-full-b` and `nemotron-full-5090`.
