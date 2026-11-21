# Redline reports

What happened when AI agents redlined contracts with [jubarte](https://github.com/jandira-tech/jubarte)
instead of the tools two legal benchmarks ship with: Crosby's RedlineBench and the
redline tasks in Harvey's Legal Agent Benchmark.

The short version: the score stayed the same, and the work took fewer tokens and
less time. On RedlineBench that was about half. On Harvey's tasks it was 6% to 14%.
One early run, Claude Haiku 5.5 on jubarte 0.12, was slower and dearer.

| | |
|---|---|
| [`harness/report.md`](harness/report.md) | For the teams behind agent harnesses and their document skills: every run, the losses, the licence change to Apache-2.0, how to ship it |
| [`lawyers/`](lawyers) | Five short posts for lawyers who follow the technology, Monday to Friday |
| [`artifacts/`](artifacts) | Four single-file pages that run jubarte in the browser. Download one and open it, or paste it into Claude as an artifact |
| [`FACTS.md`](FACTS.md) | Every number used above, with its source, and where the headline claim does not hold |

## The artifacts

| File | What it does |
|---|---|
| `is-it-really-a-redline.html` | Drop a Word file and see whether its markup is real tracked changes or only formatting |
| `word-to-pdf.html` | Word to PDF with tracked changes and comments printed as Word prints them |
| `redline-two-drafts.html` | Compare two drafts into a Word file with real tracked changes |
| `jubarte-desk.html` | Review changes one by one, compare, scrub names, validate, and print to PDF |

The last three fetch the jubarte 0.19.0 WebAssembly build from cdn.jsdelivr.net.
Documents stay in the browser tab.

## Data

Agent transcripts for the Haiku and GLM runs are public at
<https://huggingface.co/datasets/arthrod/redline-bench-jubarte-trajectories>.
Full trial directories for the DeepSeek runs on both benchmarks are public at
<https://huggingface.co/datasets/arthrod/redline-bench-deepseek-trajectories>.

jubarte is Apache-2.0 from 0.19.0. The benchmarks belong to their authors: RedlineBench
is MIT (code) and CC-BY-4.0 (data), Harvey's LAB is MIT.
