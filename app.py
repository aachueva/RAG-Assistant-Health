from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd
import streamlit as st

from src.health import RequestRecord, readiness_gates, summarize, summarize_by_route

DATA = Path("data/sample_requests.csv")


def load_records(path: Path = DATA) -> list[RequestRecord]:
    rows = []
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            rows.append(
                RequestRecord(
                    request_id=row["request_id"],
                    route=row["route"],
                    latency_ms=float(row["latency_ms"]),
                    prompt_tokens=int(row["prompt_tokens"]),
                    retrieved_chunks=int(row["retrieved_chunks"]),
                    cache_hit=row["cache_hit"].lower() == "true",
                    dependency_error=row["dependency_error"].lower() == "true",
                    retried=row["retried"].lower() == "true",
                    accepted=row["accepted"].lower() == "true",
                )
            )
    return rows


st.set_page_config(page_title="RAG Assistant Health Monitor", layout="wide")
st.title("Enterprise RAG Assistant Health Monitor")
st.caption("Synthetic telemetry • vendor-neutral • route-aware diagnostics")

records = load_records()
overall = summarize(records)
by_route = summarize_by_route(records)
gates = readiness_gates(overall)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Requests", int(overall["requests"]))
c2.metric("p95 latency", f'{overall["p95_latency_ms"]:.0f} ms')
c3.metric("Cache hit rate", f'{overall["cache_hit_rate"]:.0%}')
c4.metric("Acceptance rate", f'{overall["acceptance_rate"]:.0%}')

st.subheader("Scale-readiness gates")
gate_cols = st.columns(len(gates))
for col, (name, passed) in zip(gate_cols, gates.items()):
    col.metric(name.replace("_", " ").title(), "PASS" if passed else "FAIL")

st.subheader("Route-level health")
route_df = pd.DataFrame(by_route).T.reset_index().rename(columns={"index": "route"})
st.dataframe(route_df, use_container_width=True, hide_index=True)

st.subheader("Latency by route")
raw = pd.DataFrame([r.__dict__ for r in records])
st.bar_chart(raw.groupby("route")["latency_ms"].mean())

left, right = st.columns(2)
with left:
    st.subheader("Prompt size")
    st.line_chart(raw[["prompt_tokens"]])
with right:
    st.subheader("Failure signals")
    failure = raw.groupby("route")[["dependency_error", "retried"]].mean()
    st.bar_chart(failure)

st.subheader("Diagnostic interpretation")
if not gates["dependency_reliability"]:
    st.warning("Tool/dependency failures are high enough to block scale-up.")
if not gates["cache_efficiency"]:
    st.warning("Cache hit rate is below the example readiness target; repeated traffic may be reprocessing unnecessarily.")
if not gates["context_size"]:
    st.warning("Average prompt/context size is above the example target; inspect retrieval chunk count and prompt construction.")
if all(gates.values()):
    st.success("All example readiness gates pass.")

st.caption("This dashboard is an operational portfolio prototype. Thresholds are examples and should be tuned to real product SLOs and risk tolerance.")
