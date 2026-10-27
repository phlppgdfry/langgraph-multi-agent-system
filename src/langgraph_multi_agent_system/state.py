"""State schema definition for the multi-agent system."""

from typing import Annotated, Any

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class AgentState(TypedDict):
    """Global state passed across nodes in the LangGraph multi-agent pipeline."""

    task: str
    messages: Annotated[list[BaseMessage], add_messages]
    plan: list[str]
    current_step: int
    research_notes: list[dict[str, Any]]
    quantitative_data: list[dict[str, Any]]
    critique: dict[str, Any]
    revision_count: int
    max_revisions: int
    next_agent: str
    requires_human_approval: bool
    human_approved: bool | None
    operator_feedback: str | None
    final_report: str | None
    subtasks: list[str]
    metadata: dict[str, Any]
