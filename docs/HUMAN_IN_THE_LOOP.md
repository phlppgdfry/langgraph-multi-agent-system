# 🛡️ Human-in-the-Loop (HITL) Governance Guide

## Why Human-in-the-Loop Matters

Fully autonomous agents are powerful, but high-stakes strategic, legal, or financial decisions require human verification before release or distribution. 

LangGraph provides native **Human-in-the-Loop** capabilities through persistent checkpoints and interruption gates.

---

## ⚙️ How It Works in Nexus

1. **Interruption Declaration:**  
   The graph is compiled with `interrupt_before=["human_gate"]`.
2. **Execution Halt:**  
   When the Supervisor routes execution toward final synthesis, LangGraph automatically halts right before `human_gate` and persists state to SQLite.
3. **Operator Inspection:**  
   The human operator reviews:
   - Sourced intelligence notes.
   - Extracted metrics and benchmarks.
   - Critic evaluation score and feedback.
4. **Resumption:**  
   The operator either approves (`human_approved = True`) or requests revisions (`human_approved = False`). The graph is resumed with `app.invoke(None, config=config)`.

---

## 💻 CLI Usage

To run with human-in-the-loop enabled:

```bash
uv run python -m langgraph_multi_agent_system.cli "Analyze Enterprise AI Budgets" --human-approval
```

When the checkpoint is reached, the terminal pauses:
```
╭──────────────── Human-in-the-Loop Gate Triggered ────────────────╮
│ Review agent findings and approve final report synthesis.         │
╰──────────────────────────────────────────────────────────────────╯
Approve executive report generation? (y/n) [y]:
```

---

## 🌐 Streamlit UI Usage

In the Streamlit Web Dashboard:
1. Check **"Require Human-in-the-Loop Gate"** in the left sidebar.
2. Launch the swarm.
3. The UI pauses at the governance step, presenting **"Approve & Finalize"** and **"Request Revisions"** buttons with custom feedback inputs.
