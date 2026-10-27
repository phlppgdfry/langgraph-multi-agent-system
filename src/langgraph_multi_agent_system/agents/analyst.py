"""Data Analyst Agent: Extracts quantitative benchmarks, KPIs, and metrics."""

from typing import Any

from langchain_core.messages import AIMessage, HumanMessage

from langgraph_multi_agent_system.schemas import MetricItem
from langgraph_multi_agent_system.state import AgentState
from langgraph_multi_agent_system.tools import extract_metrics, get_llm


def analyst_node(state: AgentState) -> dict[str, Any]:
    """Extracts numerical indicators, benchmarks, and quantitative trends.

    Performs structural validation using Pydantic V2 MetricItem schemas,
    groups indicators by economic category, and synthesizes an analytical scorecard.
    """
    task = state.get("task", "")
    notes = state.get("research_notes", [])
    combined_text = " ".join([n.get("snippet", "") for n in notes]) or task

    raw_metrics = extract_metrics.invoke({"text": combined_text})

    validated_metrics: list[dict[str, Any]] = []
    for rm in raw_metrics:
        try:
            m_type = rm.get("type", "performance")
            if m_type not in [
                "percentage",
                "financial",
                "performance",
                "accuracy",
                "roi",
                "observability",
            ]:
                m_type = "performance"
            item = MetricItem(
                metric=str(rm.get("metric", "Indicator")),
                value=str(rm.get("value", "-")),
                type=m_type,
                context=rm.get("context", ""),
            )
            validated_metrics.append(item.model_dump())
        except Exception:  # noqa: BLE001
            validated_metrics.append(rm)

    # Calculate analytical groupings
    category_counts: dict[str, int] = {}
    for vm in validated_metrics:
        cat = vm.get("type", "general")
        category_counts[cat] = category_counts.get(cat, 0) + 1

    llm = get_llm()
    prompt = (
        f"You are the Senior Data Analyst Agent. Task: '{task}'.\n"
        f"Extracted metrics ({len(validated_metrics)} indicators): {validated_metrics}.\n"
        f"Category distribution: {category_counts}.\n"
        "Provide a concise analytical synthesis highlighting ROI, efficiency gains, and risk mitigation."
    )
    res = llm.invoke([HumanMessage(content=prompt)])

    msg = (
        f"[Analyst] Formulated quantitative scorecard with {len(validated_metrics)} benchmarks "
        f"across {len(category_counts)} categories ({', '.join(f'{k}:{v}' for k, v in category_counts.items())}).\n"
        f"Analysis highlight: {res.content[:200]}..."
    )

    return {
        "quantitative_data": validated_metrics,
        "next_agent": "supervisor",
        "messages": [AIMessage(content=msg)],
    }
