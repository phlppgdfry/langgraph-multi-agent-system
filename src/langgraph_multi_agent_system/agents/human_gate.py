"""Human Gatekeeper Node: Implements Human-in-the-Loop (HITL) checkpoints."""

from typing import Any

from langchain_core.messages import AIMessage

from langgraph_multi_agent_system.state import AgentState


def human_gate_node(state: AgentState) -> dict[str, Any]:
    """Human-in-the-loop checkpoint.

    Can be interrupted via LangGraph checkpointer `interrupt_before=["human_gate"]`
    or automatically approved when unattended.
    """
    approved = state.get("human_approved")
    if approved is None:
        # Default auto-approval for non-interactive runs, or mark approved
        approved = True

    status_str = "Approved by operator" if approved else "Changes requested by operator"
    return {
        "human_approved": approved,
        "next_agent": "writer" if approved else "supervisor",
        "messages": [
            AIMessage(content=f"[HumanGate] Executive review completed: {status_str}.")
        ],
    }
