"""Human Gatekeeper Node: Implements Human-in-the-Loop (HITL) checkpoints."""

from typing import Any

from langchain_core.messages import AIMessage

from langgraph_multi_agent_system.state import AgentState


def human_gate_node(state: AgentState) -> dict[str, Any]:
    """Human-in-the-loop checkpoint.

    Can be interrupted via LangGraph checkpointer `interrupt_before=["human_gate"]`
    or automatically approved when running unattended.
    """
    approved = state.get("human_approved")
    feedback = state.get("operator_feedback")

    if approved is None:
        # Default auto-approval for unattended runs
        approved = True

    if approved:
        status_str = "Approved by operator — proceeding to final report synthesis."
        next_agent = "writer"
    else:
        status_str = (
            f"Revision requested by operator: '{feedback or 'Deepen analysis'}' — "
            "routing back to research."
        )
        next_agent = "supervisor"

    return {
        "human_approved": approved,
        "next_agent": next_agent,
        "messages": [AIMessage(content=f"[HumanGate] {status_str}")],
    }
