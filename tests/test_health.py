from src.health import RequestRecord, readiness_gates, summarize, summarize_by_route


def record(**overrides):
    base = dict(
        request_id="r1",
        route="policy",
        latency_ms=1000,
        prompt_tokens=2000,
        retrieved_chunks=4,
        cache_hit=True,
        dependency_error=False,
        retried=False,
        accepted=True,
    )
    base.update(overrides)
    return RequestRecord(**base)


def test_summary_happy_path():
    s = summarize([record(), record(request_id="r2", latency_ms=1200)])
    assert s["requests"] == 2.0
    assert s["cache_hit_rate"] == 1.0
    assert s["acceptance_rate"] == 1.0


def test_route_summary_separates_failure_domains():
    data = [record(route="policy"), record(request_id="r2", route="tool", dependency_error=True)]
    result = summarize_by_route(data)
    assert result["policy"]["dependency_error_rate"] == 0.0
    assert result["tool"]["dependency_error_rate"] == 1.0


def test_readiness_flags_bad_dependency_health():
    s = summarize([record(dependency_error=True, cache_hit=False, retried=True)])
    gates = readiness_gates(s)
    assert gates["dependency_reliability"] is False
    assert gates["retry_stability"] is False


def test_empty_summary():
    assert summarize([])["requests"] == 0
