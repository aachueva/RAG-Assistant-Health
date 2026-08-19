# Enterprise RAG Assistant Health Monitor

A vendor-neutral portfolio project for diagnosing the health of an enterprise retrieval-augmented assistant before reliability, latency, cost, or dependency issues become production incidents.

The project focuses on a common operational problem: **an assistant may appear healthy at the model layer while retrieval quality, prompt growth, caching, tool dependencies, or retry behavior are quietly degrading the user experience.**

## Product preview

![Enterprise RAG Assistant Health Monitor dashboard](ChatGPT%20Image%20Aug%2018%2C%202026%2C%2005_58_08%20PM.png)

*Concept preview of the Streamlit monitoring experience. The runnable app in this repository uses synthetic telemetry and exposes the same core operational signals: traffic, latency, retrieval/context health, cache efficiency, dependency failures, quality signals, and readiness gates.*

## What this project demonstrates

- RAG system observability beyond basic model latency
- Route-aware analysis for retrieval-only, tool-backed, and mixed requests
- Prompt/context growth monitoring
- Cache-efficiency analysis
- Dependency and tool-failure diagnosis
- Readiness gates for scaling traffic
- Separating retrieval, generation, and dependency failures during incident analysis

## Scenario

A large internal assistant answers employee questions using two kinds of context:

1. policy and knowledge-base retrieval
2. live operational data from an external inventory-style service

As usage grows, latency and error rates begin to increase. The goal is to determine whether the bottleneck comes from retrieval configuration, prompt growth, cache misses, dependency degradation, retries, or traffic mix.

All data in this repository is synthetic.

## Architecture

```text
User request
    |
    v
Route classifier
  |         |
  |         +--------------------+
  v                              v
Knowledge retrieval         Live data tool
  |                              |
  +-------------+----------------+
                v
          Context builder
                |
                v
            LLM / agent
                |
                v
             Response

Telemetry collected across:
route • retrieved chunks • prompt size • cache • latency • retries • dependency errors
```

## Health signals

The dashboard tracks:

- request volume and route mix
- p50 / p95 latency
- prompt token growth
- retrieved chunk count
- cache hit rate
- tool/dependency error rate
- retry rate
- answer acceptance / quality proxy

The key idea is to **segment by route**. A blended average can hide the fact that policy-only traffic is healthy while tool-backed traffic is degrading.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Run tests:

```bash
python -m pytest -q
```

## Repository structure

```text
app.py                    Streamlit health dashboard
src/health.py             Metric aggregation and readiness logic
data/sample_requests.csv  Synthetic telemetry
tests/test_health.py      Offline unit tests
.github/workflows/ci.yml  CI validation
```

## Readiness framework

A production assistant should not be declared ready to scale based only on average latency or demo quality. This project uses explicit gates across four areas:

- **Quality:** answer acceptance and retrieval behavior remain stable
- **Performance:** p95 latency and context size remain within target
- **Reliability:** dependency and retry rates remain controlled
- **Efficiency:** cache utilization improves rather than forcing every repeated request through the full stack

## Production extensions

A production implementation would add:

- distributed tracing across retrieval, model, and tool calls
- semantic and exact-match cache layers
- retrieval precision / recall eval sets
- dependency circuit breakers and dead-letter handling
- cost-per-successful-answer tracking
- authorization-aware cache keys
- alerting on route-specific SLOs
- prompt/context regression detection
- release comparisons and rollback dashboards

## Why I built it

Enterprise AI systems often fail at the seams between components rather than inside the model itself. I built this project to make that operational reasoning visible: isolate failure domains, segment traffic, measure the right signals, and define objective readiness gates before scaling.

— Anastasia Chueva
