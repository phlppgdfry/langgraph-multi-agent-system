# 🔍 LangSmith Full-Stack Observability & Evaluation Guide

This guide details how **Nexus** leverages the complete LangSmith platform ecosystem, mapping directly to every core capability in the LangSmith dashboard.

---

## 🧭 LangSmith Feature Mapping

| LangSmith Feature | Nexus Multi-Agent Swarm Implementation | Dashboard Location |
| :--- | :--- | :--- |
| **Tracing** | Real-time hierarchical DAG tracing of all subagents, state transitions, tool calls, and token spend. | `Tracing` ➔ `nexus-multi-agent-system` |
| **Datasets & Experiments** | Automated benchmark test suite (`nexus-benchmark-dataset`) with regression test runs and side-by-side run comparisons. | `Datasets & Experiments` |
| **Evaluators** | Multi-metric scorers (`topic_coverage`, `meets_quality_bar`, `critic_quality_score`, `quantitative_grounding`). | `Evaluators` / Experiment runs |
| **Annotation Queues** | Human-in-the-Loop review queue (`nexus-human-review-queue`) for human sign-off before executive dissemination. | `Annotation Queues` |
| **Prompts (Prompt Hub)** | Managed, version-controlled agent system prompts published to your private workspace Hub. | `Prompts` |
| **Studio** | Visual inspection and interactive debugging of the `StateGraph` via `langgraph dev` (`langgraph.json`). | `Studio` / Local CLI |
| **Monitoring & Dashboards**| Tag-based filtering (`tags: ["production", "swarm-v2"]`), metadata tracking, and critic feedback scores. | `Monitoring` / `Dashboards` |

---

## ⚡ Quick Start: 1-Click Sync

To populate your entire LangSmith workspace with all assets in seconds:

```bash
cd ~/langgraph-multi-agent-system
uv run python -m langgraph_multi_agent_system.cli --sync-langsmith
```

This single command will:
1. Verify or create the **Benchmark Dataset** (`nexus-benchmark-dataset`).
2. Register and configure the **Annotation Queue** (`nexus-human-review-queue`).
3. Publish all 5 **Agent System Prompts** to your workspace Prompts repository.
4. Execute an automated **Evaluation Experiment** and record metric comparison charts.

---

## 1. Tracing & Distributed Observability

Every time the swarm executes (via CLI, Streamlit, or notebook), LangSmith automatically captures the execution tree:

```
Run: nexus-multi-agent-system [Status: SUCCESS]
├── supervisor (latency: 142ms, tokens: 380)
│   └── Input: "Analyze enterprise multi-agent adoption in 2026..."
│   └── Output: "[Supervisor] Decomposed objective into 4 parallel workstreams"
├── parallel_researcher (ThreadPoolExecutor fan-out)
│   ├── researcher-subtask-1 (Tool: search_web(query="LangGraph 2026 benchmarks"))
│   ├── researcher-subtask-2 (Tool: search_web(query="Multi-agent ROI metrics"))
│   └── researcher-subtask-3 (Tool: search_web(query="StateGraph enterprise case studies"))
├── analyst (latency: 88ms)
│   └── Tool: extract_metrics(...) [4 quantitative KPIs parsed]
├── critic (latency: 165ms)
│   └── Score: 94/100 [Passed reflection loop]
│   └── Feedback: Logged directly to run's 'critic_rigor_score'
└── writer (latency: 520ms, tokens: 1,120)
    └── Output: "# Strategic Intelligence Briefing..."
```

### European vs US Endpoint Configuration
If your LangSmith account was created in the EU data center (as indicated by an `eu.smith.langchain.com` URL), set:

```ini
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT="https://eu.api.smith.langchain.com"
LANGCHAIN_API_KEY="lsv2_pt_your_key_here"
LANGCHAIN_PROJECT="nexus-multi-agent-system"
```

---

## 2. Datasets & Experiments

The repository defines automated benchmark datasets containing realistic strategic questions and required evaluation criteria:

```python
from langgraph_multi_agent_system.langsmith_utils import (
    sync_langsmith_benchmark_dataset,
)

dataset_id = sync_langsmith_benchmark_dataset("nexus-benchmark-dataset")
```

### Running Benchmark Experiments
Run the evaluation suite to benchmark the current swarm against the dataset:

```bash
uv run python -m langgraph_multi_agent_system.cli --evals
```

All runs produce side-by-side diffs and metric distributions under the **Datasets & Experiments** tab.

---

## 3. Human-in-the-Loop Annotation Queues

When high-stakes governance is required (`--human-approval`), runs can be routed directly to a LangSmith Annotation Queue:

```bash
uv run python -m langgraph_multi_agent_system.cli --human-approval
```

In the LangSmith dashboard:
1. Click **Annotation Queues** in the left sidebar.
2. Open `nexus-human-review-queue`.
3. Review agent findings, inspect raw citations, and submit corrections or sign-offs.

---

## 4. Managed Prompt Hub

Nexus decouples prompt management from application code. You can push updated agent prompts to LangSmith:

```bash
uv run python -m langgraph_multi_agent_system.cli --push-prompts
```

Published prompts:
- `nexus-supervisor-prompt`
- `nexus-researcher-prompt`
- `nexus-analyst-prompt`
- `nexus-critic-prompt`
- `nexus-writer-prompt`

---

## 5. LangGraph Studio

Launch visual debugging with zero extra configuration:

```bash
langgraph dev
```

Open the local Studio interface to inspect checkpoint trees, rewind state, edit node parameters, and visually simulate multi-agent message routing.
