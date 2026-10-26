# 🏗️ Nexus Multi-Agent Swarm Architecture Deep Dive

## Overview

Nexus is an enterprise-grade autonomous intelligence system engineered with **LangGraph v1.2+** and **LangChain Core v1.7+**. It replaces brittle, linear prompt chains with a resilient, cyclical, stateful agent graph.

---

## 🧩 Architectural Topology

```mermaid
flowchart TD
    START([START]) --> Supervisor[🧭 Supervisor Node]

    subgraph Orchestration ["Stateful Agent Swarm (LangGraph StateGraph)"]
        Supervisor -->|Route: researcher| Researcher[🔬 Researcher Agent]
        Researcher -->|Emit: research_notes| Supervisor

        Supervisor -->|Route: analyst| Analyst[📈 Data Analyst Agent]
        Analyst -->|Emit: quantitative_data| Supervisor

        Supervisor -->|Route: critic| Critic[⚖️ Critic / Fact-Checker]
        Critic -->|Emit: critique (Score < 80)| Supervisor
        Critic -->|Emit: critique (Score >= 80)| Supervisor

        Supervisor -->|Route: human_gate| HumanGate{🛡️ Human Gatekeeper}
        HumanGate -->|Approved| Writer[✍️ Executive Writer Agent]
        HumanGate -->|Revision Request| Supervisor
    end

    Writer --> FinalReport([📊 Executive Briefing .md])
    FinalReport --> END([END])

    classDef agent fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#ffffff;
    classDef gate fill:#2e1065,stroke:#c084fc,stroke-width:2px,color:#ffffff;
    classDef terminus fill:#022c22,stroke:#4ade80,stroke-width:2px,color:#ffffff;
    class Supervisor,Researcher,Analyst,Critic,Writer agent;
    class HumanGate gate;
    class START,END,FinalReport terminus;
```

---

## 🧬 Global State Schema (`AgentState`)

The graph communicates through a typed dictionary (`AgentState`) that maintains chronological message histories and structured task deliverables:

```python
class AgentState(TypedDict):
    task: str                                           # Primary objective
    messages: Annotated[list[BaseMessage], add_messages] # Cumulative conversation trace
    plan: list[str]                                     # Phased execution steps
    current_step: int                                   # Execution pointer
    research_notes: list[dict[str, Any]]                # Sourced intelligence & URLs
    quantitative_data: list[dict[str, Any]]             # Benchmarks, KPIs, and metrics
    critique: dict[str, Any]                            # Reflection score (0-100) & feedback
    revision_count: int                                 # Active revision iterations
    max_revisions: int                                  # Maximum self-correction ceiling
    next_agent: str                                     # Target router node
    requires_human_approval: bool                       # HITL governance trigger
    human_approved: Optional[bool]                      # Operator decision
    final_report: Optional[str]                         # Generated markdown briefing
    metadata: dict[str, Any]                            # Thread, model, and trace IDs
```

---

## 🔄 The Self-Correction Reflection Cycle

Traditional LLM workflows fail silently when assertions are unsubstantiated. Nexus implements a self-correction loop:

1. **Researcher** collects external sources and populates `research_notes`.
2. **Analyst** calculates quantitative benchmarks from findings.
3. **Critic** performs multi-source triangulation:
   - Validates whether numbers and claims match source snippets.
   - Computes an aggregate quality score (0-100).
   - If score `< 80` and `revision_count < max_revisions`: The critic issues targeted recommendations and routes back to **Researcher** with a revised search scope.
   - If score `>= 80`: The critic approves progression to the **Human Gate** or **Executive Writer**.

---

## 💾 Checkpointing & State Persistence

Nexus supports both ephemeral and persistent checkpointers:
- **`MemorySaver`**: In-memory session tracking for unit testing and interactive demos.
- **`SqliteSaver`**: ACID-compliant SQLite persistence (`data/swarm_checkpoints.db`) allowing long-running threads to be paused, rewound, and resumed across CLI sessions.
