# Redline reports

What happened when AI agents redlined contracts with [jubarte](https://github.com/jandira-tech/jubarte)
instead of the tools two legal benchmarks ship with: Crosby's RedlineBench and the
redline tasks in Harvey's Legal Agent Benchmark.

The short version, for jubarte 0.14 on 120 RedlineBench tasks never used for tuning, against the `deepseek-full-b` control:

- No score difference was detected: 0.500 with the benchmark's scripts, 0.502 with jubarte (difference +0.002, 95% interval −0.029 to +0.032).
- The work halved: 18.3 to 9.1 minutes, 70 to 37 turns, 44.0k to 20.7k output tokens.
- One clean comparison took 716 runs on 0.14 alone. The whole 1,357-run archive lists at $702 to $9,679, depending on whose prices apply.
- Later binaries on Harvey's tasks went the same direction with smaller savings (6% to 14%).

| | |
|---|---|
| [`reports/jubarte-0.14-redlinebench.md`](reports/jubarte-0.14-redlinebench.md) | The 0.14 study: design, scale, held-out results, the development-set trap, cost at three price lists |
| [`reports/jubarte-six-cohorts.md`](reports/jubarte-six-cohorts.md) | Six cohorts side by side (DeepSeek on 0.14.0 and 0.15.0, Nemotron on 0.14.0, Harvey LAB on 0.16 and 0.17, Muse Spark 1.3), each against its own control |
| [`DATA-AUDIT.md`](DATA-AUDIT.md) | Where every run is stored, what the public cards got wrong, and what is in no trial table yet; one section per report |
| [`DATASETS-USED.md`](DATASETS-USED.md) | Which datasets each report read; one section per report |
| [`harness/report.md`](harness/report.md) | For the teams behind agent harnesses and their document skills: every run, the losses, the licence change to Apache-2.0, how to ship it |
| [`lawyers/`](lawyers) | Five short posts for lawyers who follow the technology, Monday to Friday |
| [`artifacts/`](artifacts) | Four single-file pages that run jubarte in the browser. Download one and open it, or paste it into Claude as an artifact |
| [`FACTS.md`](FACTS.md) | Every number used above, with its source, and where the headline claim does not hold |
| [`data/`](data) | Per-job and paired tables behind the 0.14 report |

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
