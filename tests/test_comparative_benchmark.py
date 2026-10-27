"""Unit tests for the comparative evaluation benchmarks."""

from langgraph_multi_agent_system.evals.comparative_benchmark import (
    run_baseline_a_single_agent,
    run_baseline_b_single_agent_with_tools,
    run_baseline_c_sequential_agents,
    run_baseline_d_parallel_workflow,
    run_baseline_f_nexus_swarm,
    run_comparative_benchmarks,
)


def test_baseline_a_execution():
    res = run_baseline_a_single_agent("Test task")
    assert res["baseline"] == "Baseline A: Single-Agent Direct"
    assert res["sources_count"] == 0
    assert res["latency_ms"] >= 0


def test_baseline_b_execution():
    res = run_baseline_b_single_agent_with_tools("Test task")
    assert res["baseline"] == "Baseline B: Single-Agent + Tools"
    assert res["sources_count"] > 0


def test_baseline_c_execution():
    res = run_baseline_c_sequential_agents("Test task")
    assert res["baseline"] == "Baseline C: Sequential Agents"
    assert res["grounding_ratio"] > 0.70


def test_baseline_d_execution():
    res = run_baseline_d_parallel_workflow("Test task")
    assert res["baseline"] == "Baseline D: Parallel Map-Reduce"
    assert res["sources_count"] >= 4


def test_baseline_f_execution():
    res = run_baseline_f_nexus_swarm("Test task")
    assert res["baseline"] == "Baseline F: Nexus Swarm (Reflection)"
    assert res["grounding_ratio"] >= 0.90
    assert "critic_score" in res


def test_run_comparative_benchmarks_subset(tmp_path):
    output_json = str(tmp_path / "benchmarks_test.json")
    summary = run_comparative_benchmarks(
        tasks=["Supply chain test"],
        output_json=output_json,
        sync_to_langsmith=False,
    )
    assert len(summary) == 5
    assert any(s["baseline"] == "Baseline F: Nexus Swarm (Reflection)" for s in summary)
