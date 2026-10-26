"""Graph assembly and state compilation for the LangGraph multi-agent system."""

from typing import Any, Literal

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph

from langgraph_multi_agent_system.agents.analyst import analyst_node
from langgraph_multi_agent_system.agents.critic import critic_node
from langgraph_multi_agent_system.agents.human_gate import human_gate_node
from langgraph_multi_agent_system.agents.researcher import researcher_node
from langgraph_multi_agent_system.agents.supervisor import supervisor_node
from langgraph_multi_agent_system.agents.writer import writer_node
from langgraph_multi_agent_system.checkpoint import get_checkpointer
from langgraph_multi_agent_system.state import AgentState


def supervisor_router(
    state: AgentState,
) -> Literal["researcher", "analyst", "critic", "human_gate", "writer", "__end__"]:
    """Routes execution based on the supervisor's decision."""
    target = state.get("next_agent", "writer")
    if target == "researcher":
        return "researcher"
    elif target == "analyst":
        return "analyst"
    elif target == "critic":
        return "critic"
    elif target == "human_gate":
        return "human_gate"
    elif target == "writer":
        return "writer"
    return "__end__"


def create_graph(
    checkpointer: BaseCheckpointSaver | None = None,
    interrupt_on_human_gate: bool = False,
    **compile_kwargs: Any,
):
    """Builds and compiles the multi-agent StateGraph.

    Args:
        checkpointer: Custom checkpointer (SqliteSaver, MemorySaver) or None to use default.
        interrupt_on_human_gate: If True, halts execution right before human_gate for HITL approval.
        compile_kwargs: Additional arguments passed to StateGraph.compile().

    Returns:
        Compiled StateGraph application.
    """
    workflow = StateGraph(AgentState)

    # Register agent nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("human_gate", human_gate_node)
    workflow.add_node("writer", writer_node)

    # Define edges
    workflow.add_edge(START, "supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        supervisor_router,
        {
            "researcher": "researcher",
            "analyst": "analyst",
            "critic": "critic",
            "human_gate": "human_gate",
            "writer": "writer",
            "__end__": END,
        },
    )

    # Return cycles back to supervisor
    workflow.add_edge("researcher", "supervisor")
    workflow.add_edge("analyst", "supervisor")
    workflow.add_edge("critic", "supervisor")
    workflow.add_edge("human_gate", "supervisor")
    workflow.add_edge("writer", END)

    if checkpointer is None:
        checkpointer = get_checkpointer()

    interrupt_before = ["human_gate"] if interrupt_on_human_gate else None

    return workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=interrupt_before,
        **compile_kwargs,
    )


# Top-level export for LangGraph Studio (`langgraph dev`)
graph = create_graph()
