"""Per-trial API calls, token usage and inference time for the six cohorts, both arms.

Writes data/trial_metrics.csv: one row per trial in data/cohort_trials.csv,
with the per-trial fields of that file plus:

  source            "session log" (Claude Code JSONL) or "trajectory" (ATIF steps)
  api_calls         model responses (session log: unique message ids, synthetic ones excluded;
                    trajectory: sum of llm_call_count over agent steps)
  in_uncached, cache_read, cache_write, out   summed from per-response usage
  inference_min     session log only: for each response, time from the last event before it
                    (prompt or tool result) to its last streamed line, summed. Null for
                    trajectory sources, which carry no tool-result timestamps.
  call_gap_min      trajectory and session log: time from the first to the last response,
                    an upper bound on inference time (it includes tool execution).

Sources: the public redline-bench-deepseek-trajectories (DeepSeek, Nemotron, both Harvey cohorts),
the public redline-bench-jubarte-trajectories (Muse control trajectories) and the private
redline-bench-local-archive (Muse jubarte session logs). Without access to the private archive the
Muse jubarte rows come out empty.

Run from the repository root: uv run --with huggingface_hub python tools/extract_trial_metrics.py
"""

import json
import sys
from datetime import datetime

import polars as pl
from huggingface_hub import HfApi

CSV = "data/cohort_trials.csv"
DS = "hf://datasets/arthrod/redline-bench-deepseek-trajectories/"
LA = "hf://datasets/arthrod/redline-bench-local-archive/"
JT = "hf://datasets/arthrod/redline-bench-jubarte-trajectories/data/redline_bench_extra_trials.parquet"
SESSION = r"^agent/sessions/projects/-app/[^/]+\.jsonl$"

C = pl.read_csv(CSV, infer_schema_length=10000)
rows: list[dict] = []


def ts(s: str | None) -> datetime | None:
    return datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None


def from_session(key: tuple[str, str], texts: list[str]) -> None:
    calls = 0
    tok = dict(in_uncached=0, cache_read=0, cache_write=0, out=0)
    inference = 0.0
    first = last = None
    for text in texts:
        events = []
        for line in text.splitlines():
            if not line.strip():
                continue
            try:
                o = json.loads(line)
            except Exception:
                continue
            if o.get("type") in ("assistant", "user", "system") and o.get("timestamp"):
                events.append(o)
        msgs: dict[str, dict] = {}
        prev_other = None
        for o in events:
            t = ts(o["timestamp"])
            if o["type"] != "assistant":
                prev_other = t
                continue
            m = o.get("message") or {}
            if m.get("model") == "<synthetic>":
                continue
            mid = m.get("id") or o.get("uuid")
            r = msgs.setdefault(mid, dict(start=prev_other, end=t, usage={}))
            r["end"] = max(r["end"], t)
            if m.get("usage"):
                r["usage"] = m["usage"]
        for r in msgs.values():
            calls += 1
            u = r["usage"]
            tok["in_uncached"] += u.get("input_tokens") or 0
            tok["cache_read"] += u.get("cache_read_input_tokens") or 0
            tok["cache_write"] += u.get("cache_creation_input_tokens") or 0
            tok["out"] += u.get("output_tokens") or 0
            if r["start"] is not None:
                inference += max(0.0, (r["end"] - r["start"]).total_seconds())
            first = r["end"] if first is None else min(first, r["end"])
            last = r["end"] if last is None else max(last, r["end"])
    if calls == 0:
        return
    rows.append(
        dict(
            job=key[0],
            trial_name=key[1],
            source="session log",
            api_calls=calls,
            **tok,
            inference_min=inference / 60,
            call_gap_min=(last - first).total_seconds() / 60 if first else None,
        )
    )


def from_atif(key: tuple[str, str], steps: list[dict]) -> None:
    calls = 0
    tok = dict(in_uncached=0, cache_read=0, cache_write=0, out=0)
    stamps = []
    for s in steps:
        if s.get("source") != "agent" or not s.get("metrics"):
            continue
        mt = s["metrics"]
        ex = mt.get("extra") or {}
        cr = ex.get("cache_read_input_tokens") or mt.get("cached_tokens") or 0
        cw = ex.get("cache_creation_input_tokens") or 0
        calls += s.get("llm_call_count") or 1
        tok["cache_read"] += cr
        tok["cache_write"] += cw
        tok["in_uncached"] += max(0, (mt.get("prompt_tokens") or 0) - cr - cw)
        tok["out"] += mt.get("completion_tokens") or 0
        if s.get("timestamp"):
            stamps.append(ts(s["timestamp"]))
    if calls == 0:
        return
    rows.append(
        dict(
            job=key[0],
            trial_name=key[1],
            source="trajectory",
            api_calls=calls,
            **tok,
            inference_min=None,
            call_gap_min=(max(stamps) - min(stamps)).total_seconds() / 60 if stamps else None,
        )
    )


def log(*a: object) -> None:
    print(*a, file=sys.stderr, flush=True)


# 1. RedlineBench DeepSeek and Nemotron cohorts, both arms: public session logs
rb_jobs = C.filter(~pl.col("cohort").str.contains("Harvey|Muse"))["job"].unique().to_list()
for job in rb_jobs:
    d = (
        pl.scan_parquet(DS + "redlinebench/files-*.parquet")
        .filter((pl.col("job") == job) & pl.col("path_in_trial").str.contains(SESSION))
        .select("trial_name", "text")
        .collect()
    )
    for (trial,), g in d.group_by("trial_name"):
        from_session((job, trial), [t for t in g["text"] if t])
    log("redlinebench", job, d["trial_name"].n_unique())

# 2. Harvey 0.16: public session logs, keyed by trial name
h = (
    pl.scan_parquet(DS + "harvey_lab/files-*.parquet")
    .filter(pl.col("path_in_trial").str.contains(SESSION))
    .select("trial_name", "text")
    .collect()
)
for (trial,), g in h.group_by("trial_name"):
    from_session(("harvey-hub-ab", trial), [t for t in g["text"] if t])
log("harvey 0.16", h["trial_name"].n_unique())

# 3. Muse jubarte arm: session logs in the private local archive
api = HfApi()
for f in [f for f in api.list_repo_files("arthrod/redline-bench-local-archive", repo_type="dataset") if "/files-" in f]:
    lf = pl.scan_parquet(LA + f)
    if "path" not in lf.collect_schema().names():
        continue
    d = (
        lf.filter(
            pl.col("path").str.contains("/muse-1-3-contributor-total/") & pl.col("path_in_trial").str.contains(SESSION)
        )
        .select("trial_name", "text")
        .collect()
    )
    for (trial,), g in d.group_by("trial_name"):
        from_session(("muse-1-3-contributor-total", trial), [t for t in g["text"] if t])
    if d.height:
        log("muse jubarte", f, d["trial_name"].n_unique())

# 4. Muse control: only ATIF trajectories survive
m = (
    pl.scan_parquet(JT)
    .filter(pl.col("job") == "muse-1-3-contributor-total-ooriginal")
    .select("trial_name", "trajectory_json")
    .collect()
)
for trial, tj in m.iter_rows():
    if tj:
        st = json.loads(tj)
        from_atif(("muse-1-3-contributor-total-ooriginal", trial), st if isinstance(st, list) else st.get("steps", []))
log("muse control", m.height)

# 5. Harvey 0.17: ATIF steps
tr = pl.read_parquet(DS + "harvey_lab_017/trials/part-00000.parquet").select("uuid", "trial")
st = (
    pl.scan_parquet(DS + "harvey_lab_017/steps/part-*.parquet")
    .select("trial_uuid", "step_index", "step_json")
    .collect()
    .join(tr, left_on="trial_uuid", right_on="uuid")
    .sort("trial", "step_index")
)
for (trial,), g in st.group_by("trial"):
    from_atif(("harvey-0.17", trial), [json.loads(x) for x in g["step_json"]])
log("harvey 0.17", st["trial"].n_unique())

M = pl.DataFrame(rows).unique(["job", "trial_name"], keep="first")
out = C.join(M, on=["job", "trial_name"], how="left")
out.write_csv("data/trial_metrics.csv")
log(
    out.group_by("cohort", "arm")
    .agg(
        pl.len(),
        pl.col("api_calls").is_not_null().sum().alias("with_calls"),
        pl.col("inference_min").is_not_null().sum().alias("with_inf"),
    )
    .sort("cohort", "arm")
)
