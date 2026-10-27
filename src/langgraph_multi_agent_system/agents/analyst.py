"""Data Analyst Agent: Extracts quantitative benchmarks, KPIs, and metrics."""

from typing import Any

from langchain_core.messages import AIMessage, HumanMessage

from langgraph_multi_agent_system.state import AgentState
from langgraph_multi_agent_system.tools import extract_metrics, get_llm


def analyst_node(state: AgentState) -> dict[str, Any]:
    """Extracts numerical indicators, benchmarks, and quantitative trends."""
    task = state.get("task", "")
    notes = state.get("research_notes", [])
    combined_text = " ".join([n.get("snippet", "") for n in notes]) or task

    metrics = extract_metrics.invoke({"text": combined_text})

    llm = get_llm()
    prompt = (
        f"You are the Senior Data Analyst Agent. Task: '{task}'.\n"
        f"Extracted metrics: {metrics}.\n"
        "Provide a high-impact quantitative assessment highlighting ROI, latency, and accuracy gains."
    )
    res = llm.invoke([HumanMessage(content=prompt)])

    msg = (
        f"[Analyst] Formulated quantitative scorecard with {len(metrics)} benchmarks.\n"
        f"Analysis highlight: {res.content[:200]}..."
    )

    return {
        "quantitative_data": metrics,
        "next_agent": "supervisor",
        "messages": [AIMessage(content=msg)],
    }
