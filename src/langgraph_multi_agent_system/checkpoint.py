"""Persistence and checkpointing engine for LangGraph multi-agent swarm."""

import os
import sqlite3
from typing import Any

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver


def get_checkpointer(
    backend: str | None = None,
    db_path: str | None = None,
) -> BaseCheckpointSaver:
    """Instantiate a LangGraph checkpointer.

    Args:
        backend: "sqlite" for persistent storage or "memory" for ephemeral sessions.
        db_path: Path to the SQLite database file if using sqlite backend.

    Returns:
        Configured BaseCheckpointSaver instance.
    """
    selected_backend = backend or os.getenv("PERSISTENCE_BACKEND", "sqlite")
    target_path = db_path or os.getenv("SQLITE_DB_PATH", "data/swarm_checkpoints.db")

    if selected_backend.lower() == "sqlite":
        os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)
        conn = sqlite3.connect(target_path, check_same_thread=False)
        return SqliteSaver(conn)

    return MemorySaver()


def list_saved_threads(db_path: str | None = None) -> list[dict[str, Any]]:
    """List historical checkpoint thread IDs from SQLite persistence store."""
    target_path = db_path or os.getenv("SQLITE_DB_PATH", "data/swarm_checkpoints.db")
    if not os.path.exists(target_path):
        return []

    try:
        conn = sqlite3.connect(target_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT DISTINCT thread_id, checkpoint_ns FROM checkpoints ORDER BY checkpoint_id DESC LIMIT 50"
        )
        rows = cursor.fetchall()
        conn.close()
        return [{"thread_id": r[0], "namespace": r[1]} for r in rows]
    except Exception:  # noqa: BLE001
        return []
