"""Researcher Agent: Gathers facts, sources, and ecosystem intelligence."""

from typing import Any

from langchain_core.messages import AIMessage

from langgraph_multi_agent_system.agents.parallel_researcher import (
    parallel_research_coordinator,
)
from langgraph_multi_agent_system.state import AgentState
from langgraph_multi_agent_system.tools import search_web


def researcher_node(state: AgentState) -> dict[str, Any]:
    """Conducts targeted web research, extracts facts and compiles structured notes."""
    task = state.get("task", "")
    critique = state.get("critique", {})
    existing_notes = state.get("research_notes", [])
    subtasks = state.get("subtasks", [])

    # If this is a revision cycle, address critic feedback
    if critique and not critique.get("passed", True):
        recommendation = critique.get("recommendation", "Deepen coverage")
        query = f"{task} {recommendation}"
        results = search_web.invoke({"query": query})
        new_notes = list(existing_notes)
        for item in results:
            new_notes.append(
                {
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "source": item.get("source", ""),
                    "category": "evidence",
                }
            )
        msg = f"[Researcher] Sourced {len(results)} additional data points addressing critic recommendations."
    elif subtasks:
        # Parallel Map-Reduce Fan-out
        parallel_notes, msg = parallel_research_coordinator(task, subtasks)
        new_notes = list(existing_notes) + parallel_notes
    else:
        # Standard intelligent research
        results = search_web.invoke({"query": task})
        new_notes = list(existing_notes)
        for item in results:
            new_notes.append(
                {
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "source": item.get("source", ""),
                    "category": "evidence",
                }
            )
        msg = f"[Researcher] Sourced {len(results)} verified data points across primary repositories."

    return {
        "research_notes": new_notes,
        "next_agent": "supervisor",
        "messages": [AIMessage(content=msg)],
    }
