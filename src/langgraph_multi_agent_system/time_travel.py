"""Time-Travel & State Replay Engine for LangGraph checkpoints."""

from typing import Any

from langgraph.graph.state import CompiledStateGraph


def get_checkpoint_history(
    app: CompiledStateGraph, thread_id: str
) -> list[dict[str, Any]]:
    """Retrieve full chronological checkpoint history for a thread."""
    config = {"configurable": {"thread_id": thread_id}}
    history_entries = []

    try:
        for state_snapshot in app.get_state_history(config):
            history_entries.append(
                {
                    "checkpoint_id": state_snapshot.config.get("configurable", {}).get(
                        "checkpoint_id"
                    ),
                    "checkpoint_ns": state_snapshot.config.get("configurable", {}).get(
                        "checkpoint_ns", ""
                    ),
                    "next_nodes": state_snapshot.next,
                    "values": state_snapshot.values,
                    "created_at": state_snapshot.created_at,
                }
            )
    except Exception:  # noqa: BLE001, S110
        pass

    return history_entries


def format_history_table(history: list[dict[str, Any]]) -> list[list[str]]:
    """Format history entries for Rich terminal or UI tables."""
    table_rows = []
    for h in history:
        cid = str(h.get("checkpoint_id", "-"))[:12]
        next_n = ", ".join(h.get("next_nodes", [])) or "END"
        task_snippet = str(h.get("values", {}).get("task", ""))[:35]
        next_agent = str(h.get("values", {}).get("next_agent", "-"))
        table_rows.append([cid, next_n, next_agent, task_snippet])
    return table_rows
