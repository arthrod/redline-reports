# Day 3 · $702 or $9,679 for the same runs

MAIN POST:

The same 1,357 agent runs cost $702 or $9,679. The runs do not change. Only the price list does.

That is the full RedlineBench archive of my jubarte 0.14 study: 140 contract tasks, run many times. 3.29 billion tokens in, 46 million out. Priced at DeepSeek's list: $702. At Claude Sonnet 5.5: $4,839. At Claude Opus 5.5: $9,679.

What I paid looked like none of them. The agent ran on a flat subscription with weekly credits. During the Harvey runs that followed, the queue stopped itself at 4% credit and again at 0%. One judge model was dropped after ten minutes: too expensive. A later study on rented hardware cost $100 for tokens that would list at $6,175.

Three things I did not expect:

In the control arm, 91% of what the agent read was cache hits, billed at a twentieth of the normal rate on Claude. Billed as fresh input, one task at Opus prices would list at $11.33 instead of $2.29.

Grading is a second bill. A model scores every run against a rubric, and every regrade pays again.

The bill moved more than I expected. At Opus prices, one task cost $2.29 with the benchmark's scripts and $1.32 with jubarte, with no score difference detected. In these runs the jubarte arm read 1.40 million tokens, not 2.61 million, and wrote 20.8 thousand, not 44.5 thousand; output was about half the saving. The arms ran on different days, so a provider change is not ruled out.

Disclosure: jubarte is mine, and these are my runs and my bills.

For anyone buying legal AI: ask for tokens and turns per matter and the cache rate, not just the price per seat.

Links in comments. If you have priced an agent deployment, did the cache rate appear in the quote?

COMMENT:

Cost tables and method: https://github.com/arthrod/redline-reports/blob/main/reports/jubarte-0.14-redlinebench.md (section 6)
Raw token counts per trial: https://huggingface.co/datasets/arthrod/redline-bench-deepseek-trajectories

In plain English. A token is roughly three quarters of a word. Input tokens are what the model reads (the contract, the playbook, its own earlier steps), and output tokens are what it writes. A cache hit is text the model already read in this session; providers bill it at a fraction of the normal rate. An agent rereads the same contract dozens of times, which is why cache hits are most of what it reads. They are still a small part of the bill: about 21% of the control's cost at Opus prices, 10% at DeepSeek's.

Nitty-gritty:
- Prices per million tokens:
  - DeepSeek V4.1 Flash, first-party peak: $0.30 in, $0.006 cached, $1.20 out.
  - Sonnet 5.5: $2, $0.10, $10.
  - Opus 5.5: $4, $0.20, $20.
- Cache-write surcharges are excluded, so the Claude figures are a floor.
- Nemotron ran on a local GPU that reports no cache, so its tokens are priced as uncached.
- Claude Code's own estimate in the run files: $9,590 for the archive.
- Per task, 127 held-out: control $2.29 and jubarte $1.32 at Opus prices; $0.137 and $0.081 at DeepSeek's.
- The $100 is the Harvey LAB study on jubarte 0.17, self-hosted, 88 trials, 1.48 billion recorded input tokens.

VISUAL SUGGESTIONS:
14x | SAME RUNS, DIFFERENT PRICE LIST | $702 at DeepSeek list, $9,679 at Claude Opus 5.5
91% | OF WHAT THE AGENT READ WAS CACHED | billed as fresh input, one task would cost about 5x more at Opus prices
$1.32 | PER CONTRACT AT OPUS PRICES | $2.29 with the benchmark's scripts, no score difference detected

OPEN QUESTIONS FOR ARTHUR:
1. What did the Synthetic plan cost? The run logs record credit levels but not the plan. If you want "what I actually paid" to carry a number, give me the plan and months used.
2. The $100 is your figure, recorded in the 0.17 dataset card. Confirm it covers the whole node rental and not only part of it.
