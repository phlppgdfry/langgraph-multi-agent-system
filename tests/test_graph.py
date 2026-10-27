"""Unit and integration tests for LangGraph swarm workflow and persistence."""

from langgraph.checkpoint.memory import MemorySaver

from langgraph_multi_agent_system.checkpoint import get_checkpointer
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
    app = create_graph(checkpointer=MemorySaver())
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
        "metadata": {},
    }
    config = {"configurable": {"thread_id": "test-thread-1"}}

    for _ in app.stream(initial_state, config=config):
        pass

    full_state = app.get_state(config).values
    assert full_state is not None
    assert full_state.get("final_report") is not None
    assert len(full_state.get("final_report")) > 100
    assert "Executive Summary" in full_state.get("final_report")


def test_human_gate_checkpoint():
    app = create_graph(checkpointer=MemorySaver(), interrupt_on_human_gate=False)
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
        "metadata": {},
    }
    config = {"configurable": {"thread_id": "test-human-thread"}}

    for _ in app.stream(initial_state, config=config):
        pass

    full_state = app.get_state(config).values
    assert full_state.get("final_report") is not None


def test_sqlite_checkpointer_instance():
    checkpointer = get_checkpointer(backend="sqlite", db_path="data/test_swarm.db")
    assert checkpointer is not None


def test_shared_store_memory():
    from langgraph_multi_agent_system.memory_store import (
        get_shared_store,
        recall_prior_knowledge,
    )

    store = get_shared_store()
    assert store is not None
    store.put(("knowledge", "test_domain"), "insight_1", {"key": "agentic_roi", "val": "+37%"})
    recalled = recall_prior_knowledge(store, "agentic_roi")
    assert isinstance(recalled, list)


def test_time_travel_history():
    from langgraph_multi_agent_system.time_travel import (
        format_history_table,
        get_checkpoint_history,
    )

    app = create_graph(checkpointer=MemorySaver())
    tid = "test-time-travel"
    config = {"configurable": {"thread_id": tid}}
    initial_state = {
        "task": "Test Time Travel History",
        "messages": [],
        "plan": [],
        "current_step": 0,
        "research_notes": [],
        "quantitative_data": [],
        "critique": {},
        "revision_count": 0,
        "max_revisions": 1,
        "next_agent": "",
        "requires_human_approval": False,
        "human_approved": None,
        "final_report": None,
        "metadata": {},
    }
    for _ in app.stream(initial_state, config=config):
        pass

    history = get_checkpoint_history(app, tid)
    assert len(history) > 0
    table_rows = format_history_table(history)
    assert len(table_rows) == len(history)
