"""Unit and integration tests for LangGraph swarm workflow."""

from langgraph_multi_agent_system.graph import create_graph


def test_graph_compilation():
    app = create_graph()
    assert app is not None
    assert "supervisor" in app.nodes
    assert "researcher" in app.nodes
    assert "analyst" in app.nodes
    assert "critic" in app.nodes
    assert "writer" in app.nodes


def test_graph_end_to_end_execution():
    app = create_graph()
    initial_state = {
        "task": "Benchmark LangGraph agent efficiency",
        "messages": [],
        "plan": [],
        "current_step": 0,
        "research_notes": [],
        "quantitative_data": [],
        "critique": {},
        "revision_count": 0,
        "max_revisions": 2,
        "next_agent": "",
        "requires_human_approval": False,
        "human_approved": None,
        "final_report": None,
        "metadata": {}
    }
    config = {"configurable": {"thread_id": "test-thread-1"}}

    final_state = None
    for output in app.stream(initial_state, config=config):
        for state_update in output.values():
            final_state = state_update

    assert final_state is not None
    assert final_state.get("final_report") is not None
    assert len(final_state.get("final_report")) > 100
    assert "Executive Summary" in final_state.get("final_report")


def test_human_gate_checkpoint():
    app = create_graph()
    initial_state = {
        "task": "Test Human Gate Approval",
        "messages": [],
        "plan": [],
        "current_step": 0,
        "research_notes": [],
        "quantitative_data": [],
        "critique": {},
        "revision_count": 0,
        "max_revisions": 1,
        "next_agent": "",
        "requires_human_approval": True,
        "human_approved": None,
        "final_report": None,
        "metadata": {}
    }
    config = {"configurable": {"thread_id": "test-human-thread"}}

    outputs = list(app.stream(initial_state, config=config))
    assert len(outputs) > 0
    last_update = outputs[-1]
    assert "writer" in last_update
    assert last_update["writer"]["final_report"] is not None
