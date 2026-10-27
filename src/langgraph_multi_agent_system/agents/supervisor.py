"""Supervisor Agent: Orchestrates the multi-agent swarm workflow."""

from typing import Any

from langchain_core.messages import AIMessage, HumanMessage

from langgraph_multi_agent_system.state import AgentState
from langgraph_multi_agent_system.tools import get_llm


def supervisor_node(state: AgentState) -> dict[str, Any]:
    """Evaluates current progress and decides the next agent to invoke."""
    task = state.get("task", "Analyze technology trends")
    plan = state.get("plan", [])
    research_notes = state.get("research_notes", [])
    quantitative_data = state.get("quantitative_data", [])
    critique = state.get("critique", {})
    revision_count = state.get("revision_count", 0)

    llm = get_llm()

    # Formulate initial plan if empty
    if not plan:
        plan_prompt = (
            f"You are the Supervisor of an elite multi-agent system. Task: '{task}'.\n"
            "Break this task into 4 strategic phases:\n"
            "1. Deep factual research and source gathering.\n"
            "2. Quantitative metrics and financial/performance analysis.\n"
            "3. Fact-checking, consistency critique and reflection.\n"
            "4. Executive briefing generation."
        )
        _ = llm.invoke([HumanMessage(content=plan_prompt)])
        new_plan = [
            "1. Deep factual research and parallel source gathering",
            "2. Quantitative metrics and benchmark analysis",
            "3. Fact-checking, consistency critique and reflection",
            "4. Executive briefing generation",
        ]
        subtasks = [
            "Technical Architecture & StateGraph Patterns",
            "Quantitative Performance & FinOps Metrics",
            "Enterprise Risk & Governance Controls",
        ]
        return {
            "plan": new_plan,
            "subtasks": subtasks,
            "next_agent": "researcher",
            "messages": [
                AIMessage(
                    content=f"[Supervisor] Plan initialized: {len(new_plan)} steps. Decomposed into {len(subtasks)} parallel research streams."
                )
            ],
        }

    # If no research done yet -> researcher
    if not research_notes:
        return {
            "next_agent": "researcher",
            "messages": [
                AIMessage(
                    content="[Supervisor] Routing to Researcher for primary data collection."
                )
            ],
        }

    # If research done but no quantitative analysis -> analyst
    if not quantitative_data:
        return {
            "next_agent": "analyst",
            "messages": [
                AIMessage(
                    content="[Supervisor] Research complete. Routing to Analyst for quantitative metrics."
                )
            ],
        }

    # If quantitative done but no critique -> critic
    if not critique:
        return {
            "next_agent": "critic",
            "messages": [
                AIMessage(
                    content="[Supervisor] Quantitative analysis complete. Routing to Critic for self-reflection evaluation."
                )
            ],
        }

    # If critique requested revision and within max revisions
    passed = critique.get("passed", False)
    max_revisions = state.get("max_revisions", 2)
    if not passed and revision_count < max_revisions:
        return {
            "next_agent": "researcher",
            "revision_count": revision_count + 1,
            "messages": [
                AIMessage(
                    content=f"[Supervisor] Critique score ({critique.get('score')}/100) below threshold. Initiating revision cycle #{revision_count + 1}."
                )
            ],
        }

    # Check if human approval is required
    requires_approval = state.get("requires_human_approval", False)
    approved = state.get("human_approved", None)
    if requires_approval and approved is None:
        return {
            "next_agent": "human_gate",
            "messages": [
                AIMessage(
                    content="[Supervisor] Quality checks passed. Routing to Human Gatekeeper for executive review."
                )
            ],
        }

    # Ready for final executive writing
    return {
        "next_agent": "writer",
        "messages": [
            AIMessage(
                content="[Supervisor] All verification stages passed. Routing to Executive Writer."
            )
        ],
    }
