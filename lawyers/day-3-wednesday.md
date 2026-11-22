# Day 3 · Half the tokens, a third off the bill

MAIN POST:

My tool cut the agent's tokens roughly in half. The bill fell by about a third. The gap between those two numbers is worth understanding before you sign an AI contract.

Same runs as Monday: DeepSeek in Claude Code, redlining RedlineBench contracts, with the benchmark's scripts or with jubarte. I read the logs of every model response, over 36,000 of them, and priced each trial at OpenRouter's public rates.

Per contract, at OpenRouter's price for this DeepSeek model: about 5 cents with the scripts, about 3 cents with jubarte. 35% less.
Priced as if Claude Opus 5.5 had done the work: $1.81 against $1.11. 39% less.

So why not 50%?

An agent rereads the whole conversation on every step: the contract, the instructions, everything it has written so far. Providers cache that reread and bill it at a small fraction of the normal rate. In these runs, 92% to 95% of what the agent read was cached.

jubarte halved the number of steps, from about 70 per contract to about 40, so it halved the cheap rereads. The expensive part, the new text the model reads for the first time, hardly moved: 114 thousand tokens with the scripts, 107 thousand with jubarte.

Then I checked the provider's numbers. Its usage figures counted that expensive part twice, and its output counts look about 2.4 times too small next to the text actually produced. A tokens-saved claim built on those numbers would have been wrong in both directions. More on that Friday.

Disclosure: jubarte is mine, and these are my runs. The real bill was a flat subscription, so these are estimates at OpenRouter's prices.

For anyone buying legal AI: ask for tokens per matter split into cached and uncached, and ask how the vendor counted them.

Links in comments. If you have priced an agent deployment, did the quote say how much of the input was cached?

COMMENT:

Report, section 6: https://github.com/arthrod/redline-reports/blob/main/reports/jubarte-six-cohorts.md
How the provider's usage numbers go wrong: https://github.com/arthrod/redline-reports/blob/main/harness/report.md (section 5)

In plain English. A token is roughly three quarters of a word. Input tokens are what the model reads, and output tokens are what it writes. A cache hit is text the model has already read in this session; providers bill it at a fraction of the normal rate. An agent rereads the same contract dozens of times, which is why cached reads are most of what it reads but a small part of the bill.

Nitty-gritty:
- Per trial, from the session logs:

  | | Cached input | Uncached input | Output (reported) |
  |---|---:|---:|---:|
  | Scripts | 2.32M | 114k | 44.5k |
  | jubarte 0.14 | 1.21M | 107k | 21.8k |
  | jubarte 0.15 | 1.05M | 108k | 20.4k |

- Prices per million tokens:
  - DeepSeek V4.1 Flash 1017 on OpenRouter (2026-11-22): $0.15 in, $0.003 cached, $0.60 out. Doubled on weekdays 01:00–04:00 and 06:00–10:00 UTC.
  - Opus 5.5 list: $4, $0.20, $20.
- Per contract at OpenRouter's base rate: $0.051 with the scripts, $0.033 with jubarte 0.14. At the weekday peak: $0.102 and $0.066.
- Cache-write surcharges are excluded, so the Claude figures are a floor. No Claude model was the agent; that column is a what-if.
- jubarte 0.15 on the same model: $0.032 on OpenRouter ($0.063 at the peak), $1.05 at Opus prices.
- Agent minutes per contract: 18.3 with the scripts, 10.3 with jubarte 0.14.

VISUAL SUGGESTIONS:
−51% | OUTPUT TOKENS WITH JUBARTE | 44.2k → 21.5k per contract
−35% | THE BILL, AT OPENROUTER'S PRICE | $0.051 → $0.033 per contract
107k vs 114k | THE EXPENSIVE INPUT BARELY MOVED | the savings came from cheap cached rereads

OPEN QUESTIONS FOR ARTHUR:
1. Prices are now OpenRouter's (fetched 2026-11-22). The earlier $0.102 → $0.066 was DeepSeek's weekday peak rate, which is double the base rate. Report Appendix A has OpenRouter prices for all six cohorts, including Nemotron and Muse.
2. The Opus figures dropped from $2.29 → $1.32 to $1.81 → $1.11. The old figures counted DeepSeek's uncached input twice, as Harbor's totals do.
