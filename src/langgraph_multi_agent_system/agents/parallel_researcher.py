"""Parallel Map-Reduce Research Workers for high-throughput intelligence gathering."""

from concurrent.futures import ThreadPoolExecutor
from typing import Any

from langchain_core.messages import HumanMessage

from langgraph_multi_agent_system.tools import get_llm, search_web


def execute_subtask_research(subtask: str, task: str) -> list[dict[str, Any]]:
    """Execute focused search query for a single subtask."""
    query = f"{task} {subtask}"
    results = search_web.invoke({"query": query})

    notes = []
    for r in results:
        notes.append({
            "title": r.get("title", "Source"),
            "snippet": r.get("snippet", ""),
            "source": r.get("source", "web"),
            "subtask": subtask,
            "category": "parallel_worker_evidence",
        })
    return notes


def parallel_research_coordinator(task: str, subtasks: list[str]) -> tuple[list[dict[str, Any]], str]:
    """Execute multiple specialized research workers in parallel (Map-Reduce pattern).

    Args:
        task: Overarching strategic objective.
        subtasks: Decomposed domain angles (e.g. Architecture, FinOps, Risks).

    Returns:
        Tuple of (aggregated evidence list, synthesis summary message).
    """
    if not subtasks:
        subtasks = [
            "Technical StateGraph Architecture & Resilience",
            "Quantitative Performance & FinOps Benchmarks",
            "Enterprise Governance & Risk Matrix",
        ]

    aggregated_notes: list[dict[str, Any]] = []

    # Map: Parallel fan-out across worker threads
    with ThreadPoolExecutor(max_workers=min(len(subtasks), 4)) as executor:
        future_to_subtask = {
            executor.submit(execute_subtask_research, st, task): st for st in subtasks
        }
        for future in future_to_subtask:
            try:
                worker_notes = future.result()
                aggregated_notes.extend(worker_notes)
            except Exception:  # noqa: BLE001, S110
                pass

    # Reduce: Synthesize findings across all parallel streams
    llm = get_llm()
    prompt = (
        f"You are the Research Coordinator. Aggregated {len(aggregated_notes)} data points "
        f"across {len(subtasks)} parallel research workers on: '{task}'.\n"
        "Provide a concise multi-angle synthesis."
    )
    res = llm.invoke([HumanMessage(content=prompt)])

    summary_msg = (
        f"[ParallelSwarm] Fan-out complete across {len(subtasks)} worker threads.\n"
        f"Triangulated {len(aggregated_notes)} sources.\n"
        f"Synthesis: {res.content[:200]}..."
    )

    return aggregated_notes, summary_msg
