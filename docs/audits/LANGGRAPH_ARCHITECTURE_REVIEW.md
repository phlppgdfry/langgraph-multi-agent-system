# 🏗️ LangGraph Architecture Review & Formal Specification

**System:** Nexus Multi-Agent Swarm  
**Architecture Specification:** StateGraph Cyclical Directed Graph  
**Review Lead:** Staff Agentic Systems Engineer & Senior LangGraph Engineer  

---

## 1. Graph Topology & State Machine Formalism

The Nexus Multi-Agent System is modeled as an extended finite state machine implemented via LangGraph's `StateGraph(AgentState)`.

```
                    ┌─────────────────────────┐
                    │          START          │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
        ┌──────────►│       Supervisor        │◄──────────┐
        │           └────────────┬────────────┘           │
        │                        │ (Conditional Edge)     │
        │                        ▼                        │
        │     ┌─────────────────────────────────────┐     │
        │     │         supervisor_router           │     │
        │     └──────┬───────┬───────┬───────┬──────┘     │
        │            │       │       │       │            │
        │ "research" │       │       │       │ "critic"   │
        │            ▼       │       │       ▼            │
        │     ┌────────────┐ │       │ ┌────────────┐     │
        ├─────┤ Researcher │ │       │ │   Critic   │─────┤
        │     └────────────┘ │       │ └────────────┘     │
        │                    │       │                    │
        │        "analyst"   ▼       ▼  "human_gate"      │
        │             ┌────────────┐ ┌────────────┐       │
        ├─────────────┤  Analyst   │ │ Human Gate │───────┤
        │             └────────────┘ └─────┬──────┘       │
        │                                  │              │
        │                                  │ "writer"     │
        │                                  ▼              │
        │                            ┌────────────┐       │
        │                            │   Writer   │       │
        │                            └─────┬──────┘       │
        │                                  │              │
        │                                  ▼              │
        │                            ┌────────────┐       │
        │                            │    END     │       │
        │                            └────────────┘       │
```

---

## 2. State Schema & Reducers

```python
class AgentState(TypedDict):
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
```

### Reducer Analysis
- `messages`: Utilizes LangGraph's built-in `add_messages` reducer. Ensures message appending semantics rather than destructive overwrite, preserving the full conversational transcript across agent turns.
- All other keys follow standard dictionary replacement semantics, allowing agents to emit surgical delta updates without mutating state in-place.

---

## 3. Checkpointing & Human-in-the-Loop Lifecycle

### Checkpointer Boundaries
- **Transient Memory:** `MemorySaver` (used for fast in-process unit tests).
- **Durable Persistence:** `SqliteSaver(sqlite3.connect("data/swarm_checkpoints.db"))`.

### Interrupt & Resume Workflow
When compiled with `interrupt_before=["human_gate"]`:
1. Swarm executes `supervisor -> researcher -> analyst -> critic -> supervisor`.
2. Upon routing to `human_gate`, LangGraph captures an ACID checkpoint to SQLite and halts execution.
3. State inspection via `app.get_state(config)` confirms `next == ('human_gate',)` and `human_approved == None`.
4. The system can safely terminate, restart, or wait indefinitely for operator governance.
5. Resumption occurs out-of-process via:
   ```bash
   uv run python -m langgraph_multi_agent_system.cli --resume <thread_id> --approve
   ```
6. The state update sets `human_approved = True` and resumes `app.stream(None, config=config)`, executing `writer -> END`.

---

## 4. Node Role & Capability Audit

### 🧭 Supervisor Agent
- **Decomposition:** Dynamically translates complex strategic questions into 3 distinct workstreams (Operational, Quantitative, and Risk/Governance).
- **Routing:** Evaluates state progression indicators (`research_notes`, `quantitative_data`, `critique`).
- **Loop Bounding:** Strict exit condition enforced via `revision_count < max_revisions` (default 2), preventing infinite graph recursion.

### 🔬 Researcher Agent
- **Tool Triangulation:** Executes `search_web` via `ddgs` (DuckDuckGo Search) with zero-key fallback domain intelligence.
- **Concurrency:** Dispatches subtask research queries concurrently using `ThreadPoolExecutor`.

### 📈 Data Analyst Agent
- **Schema Validation:** Enforces Pydantic V2 `MetricItem` validation on all extracted numerical data points.
- **Taxonomy:** Groups benchmarks across financial, percentage, latency, accuracy, and ROI categories.

### ⚖️ Critic Agent (Self-Correction Reflection)
- **Calibrated 4-Pillar Rubric:**
  1. *Citation Diversity (0-25):* Audits unique domains and non-empty URLs.
  2. *Quantitative Density (0-25):* Measures presence of structured KPI indicators.
  3. *Grounding Integrity (0-25):* Cross-verifies assertions against snippet evidence.
  4. *Subtask Coverage (0-25):* Evaluates coverage of decomposed research angles.
- **Threshold:** Score `< 80` forces a rejection verdict, incrementing `revision_count` and returning control to the researcher with targeted critique.

### ✍️ Executive Writer Agent
- **Structure:** Synthesizes Executive Summary, Quantitative Scorecard, Strategic Workstream Findings, Critic Quality Breakdown, and Source Citations.
- **Validation:** Produces structured Markdown and printable C-level HTML reports via `export_report.py`.
