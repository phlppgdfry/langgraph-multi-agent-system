"""Unit tests for tool functions."""

from langgraph_multi_agent_system.tools import (
    extract_metrics,
    get_llm,
    search_web,
    verify_claim,
)


def test_search_web_returns_results():
    results = search_web.invoke({"query": "LangChain architecture"})
    assert isinstance(results, list)
    assert len(results) > 0
    assert "title" in results[0]
    assert "snippet" in results[0]


def test_extract_metrics_parses_kpis():
    sample_text = (
        "The system achieved 42% accuracy gain and saved $12 million in cloud costs."
    )
    metrics = extract_metrics.invoke({"text": sample_text})
    assert isinstance(metrics, list)
    assert len(metrics) >= 2


def test_verify_claim_with_sources():
    verdict = verify_claim.invoke(
        {
            "claim": "Multi-agent systems improve accuracy.",
            "sources": ["https://example.com/study"],
        }
    )
    assert verdict["verified"] is True
    assert verdict["confidence"] > 0.8


def test_mock_llm_fallback():
    llm = get_llm()
    assert llm is not None
