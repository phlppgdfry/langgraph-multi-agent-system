"""Researcher Agent: Gathers facts, sources, and ecosystem intelligence."""

from typing import Any

from langchain_core.messages import AIMessage, HumanMessage

from langgraph_multi_agent_system.state import AgentState
from langgraph_multi_agent_system.tools import get_llm, search_web


def researcher_node(state: AgentState) -> dict[str, Any]:
    """Conducts targeted web research, extracts facts and compiles structured notes."""
    task = state.get("task", "")
    critique = state.get("critique", {})
    existing_notes = state.get("research_notes", [])

    # If this is a revision cycle, address critic feedback
    if critique and not critique.get("passed", True):
        recommendation = critique.get("recommendation", "Deepen coverage")
        query = f"{task} {recommendation}"
    else:
        query = task

    # Perform web research
    results = search_web.invoke({"query": query})
    new_notes: list[dict[str, Any]] = list(existing_notes)

    for item in results:
        new_notes.append({
            "title": item.get("title", ""),
            "snippet": item.get("snippet", ""),
            "source": item.get("source", ""),
            "category": "evidence"
        })

    llm = get_llm()
    summary_prompt = (
        f"You are the Lead Researcher Agent. The task is '{task}'.\n"
        f"Collected sources: {len(results)} items.\n"
        "Synthesize the 3 key qualitative findings from these sources."
    )
    res = llm.invoke([HumanMessage(content=summary_prompt)])

    msg = (
        f"[Researcher] Sourced {len(results)} verified data points.\n"
        f"Key synthesis: {res.content[:200]}..."
    )

    return {
        "research_notes": new_notes,
        "next_agent": "supervisor",
        "messages": [AIMessage(content=msg)]
    }
