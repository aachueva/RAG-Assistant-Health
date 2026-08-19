"""Vendor-neutral health metrics for an enterprise RAG assistant."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import median
from typing import Iterable


@dataclass(frozen=True)
class RequestRecord:
    request_id: str
    route: str
    latency_ms: float
    prompt_tokens: int
    retrieved_chunks: int
    cache_hit: bool
    dependency_error: bool
    retried: bool
    accepted: bool


def percentile(values: Iterable[float], pct: float) -> float:
    ordered = sorted(float(v) for v in values)
    if not ordered:
        return 0.0
    if len(ordered) == 1:
        return ordered[0]
    pos = (len(ordered) - 1) * pct
    low = int(pos)
    high = min(low + 1, len(ordered) - 1)
    weight = pos - low
    return ordered[low] * (1 - weight) + ordered[high] * weight


def summarize(records: list[RequestRecord]) -> dict[str, float]:
    if not records:
        return {
            "requests": 0,
            "p50_latency_ms": 0.0,
            "p95_latency_ms": 0.0,
            "avg_prompt_tokens": 0.0,
            "avg_retrieved_chunks": 0.0,
            "cache_hit_rate": 0.0,
            "dependency_error_rate": 0.0,
            "retry_rate": 0.0,
            "acceptance_rate": 0.0,
        }

    n = len(records)
    return {
        "requests": float(n),
        "p50_latency_ms": round(median(r.latency_ms for r in records), 1),
        "p95_latency_ms": round(percentile((r.latency_ms for r in records), 0.95), 1),
        "avg_prompt_tokens": round(sum(r.prompt_tokens for r in records) / n, 1),
        "avg_retrieved_chunks": round(sum(r.retrieved_chunks for r in records) / n, 2),
        "cache_hit_rate": round(sum(r.cache_hit for r in records) / n, 4),
        "dependency_error_rate": round(sum(r.dependency_error for r in records) / n, 4),
        "retry_rate": round(sum(r.retried for r in records) / n, 4),
        "acceptance_rate": round(sum(r.accepted for r in records) / n, 4),
    }


def summarize_by_route(records: list[RequestRecord]) -> dict[str, dict[str, float]]:
    routes = sorted({r.route for r in records})
    return {route: summarize([r for r in records if r.route == route]) for route in routes}


def readiness_gates(summary: dict[str, float]) -> dict[str, bool]:
    """Example scale-readiness gates; tune per product/SLO."""
    return {
        "latency": summary["p95_latency_ms"] <= 2500,
        "context_size": summary["avg_prompt_tokens"] <= 4500,
        "dependency_reliability": summary["dependency_error_rate"] <= 0.03,
        "retry_stability": summary["retry_rate"] <= 0.05,
        "cache_efficiency": summary["cache_hit_rate"] >= 0.15,
        "quality": summary["acceptance_rate"] >= 0.90,
    }
