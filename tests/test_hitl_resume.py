"""Unit and integration test for out-of-process Human-in-the-Loop interrupt and resume."""

import json
import os

from langgraph_multi_agent_system.checkpoint import get_checkpointer
from langgraph_multi_agent_system.cli import log_hitl_audit_event
from langgraph_multi_agent_system.graph import create_graph


def test_hitl_interrupt_and_resume_lifecycle(tmp_path):
    """Verify that an interrupted Human-in-the-Loop graph pauses cleanly before human_gate,

    saves state in SQLite checkpointer, and can be resumed with approval.
    """
    db_file = str(tmp_path / "hitl_test.db")
    checkpointer = get_checkpointer(backend="sqlite", db_path=db_file)

    # 1. Compile graph with interrupt_on_human_gate=True
    app = create_graph(checkpointer=checkpointer, interrupt_on_human_gate=True)

    thread_id = "test-hitl-lifecycle-1"
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "task": "Evaluate Global Supply Chain Container Dwell Time",
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
        "operator_feedback": None,
        "final_report": None,
        "subtasks": [],
        "metadata": {"thread_id": thread_id},
    }

    # 2. Run graph until it pauses at the human approval boundary
    for _ in app.stream(initial_state, config=config):
        pass

    # 3. Verify state paused exactly before human_gate
    snapshot = app.get_state(config)
    assert snapshot is not None
    assert "human_gate" in snapshot.next
    assert snapshot.values.get("human_approved") is None
    assert snapshot.values.get("final_report") is None

    # 4. Simulate process restart / new graph instance loading the same SQLite DB
    new_app = create_graph(
        checkpointer=get_checkpointer(backend="sqlite", db_path=db_file)
    )
    reloaded_snapshot = new_app.get_state(config)
    assert "human_gate" in reloaded_snapshot.next

    # 5. Operator approves execution
    new_app.update_state(
        config,
        {
            "human_approved": True,
            "next_agent": "writer",
        },
    )

    # 6. Resume execution from checkpoint
    for _ in new_app.stream(None, config=config):
        pass

    final_snapshot = new_app.get_state(config)
    assert final_snapshot.values.get("final_report") is not None
    assert "Executive Summary" in final_snapshot.values["final_report"]
    assert final_snapshot.values.get("human_approved") is True


def test_hitl_rejection_and_revision_loop(tmp_path):
    """Verify that operator rejection with feedback triggers an active revision cycle."""
    db_file = str(tmp_path / "hitl_reject.db")
    checkpointer = get_checkpointer(backend="sqlite", db_path=db_file)
    app = create_graph(checkpointer=checkpointer, interrupt_on_human_gate=True)

    thread_id = "test-hitl-reject-1"
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "task": "FinOps Cloud Cost Optimization Strategy",
        "messages": [],
        "plan": [],
        "current_step": 0,
        "research_notes": [],
        "quantitative_data": [],
        "critique": {},
        "revision_count": 0,
        "max_revisions": 2,
        "next_agent": "",
        "requires_human_approval": True,
        "human_approved": None,
        "operator_feedback": None,
        "final_report": None,
        "subtasks": [],
        "metadata": {"thread_id": thread_id},
    }

    for _ in app.stream(initial_state, config=config):
        pass

    snapshot = app.get_state(config)
    assert "human_gate" in snapshot.next

    # Operator rejects and provides actionable feedback
    app.update_state(
        config,
        {
            "human_approved": False,
            "operator_feedback": "Please add breakdown of GPU cluster reserve pricing.",
            "next_agent": "researcher",
        },
    )

    # Stream again: supervisor processes rejection and initiates cycle #1
    for _ in app.stream(None, config=config):
        pass

    post_reject_snapshot = app.get_state(config)
    assert post_reject_snapshot.values.get("revision_count") >= 1


def test_hitl_audit_logging(tmp_path):
    """Verify that operator audit events are written cleanly as structured JSONL."""
    audit_file = str(tmp_path / "test_hitl_audit.log")

    log_hitl_audit_event(
        thread_id="test-thread-audit-1",
        action="operator_review",
        approved=True,
        feedback="Looks solid",
        status="success",
        details={"reviewer": "Philippe"},
        audit_file=audit_file,
    )

    assert os.path.exists(audit_file)
    with open(audit_file, encoding="utf-8") as f:
        lines = f.readlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["thread_id"] == "test-thread-audit-1"
    assert record["approved"] is True
    assert record["status"] == "success"
    assert record["details"]["reviewer"] == "Philippe"
