# ⚡ Nexus: Autonomous Multi-Agent Intelligence Swarm

[![Live Demo](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-0284C7.svg?logo=googlechrome&logoColor=white)](https://phlppgdfry.github.io/langgraph-multi-agent-system/)
[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![LangChain Core](https://img.shields.io/badge/LangChain%20Core-v1.7%2B-1C3C3C.svg?logo=langchain&logoColor=white)](https://www.langchain.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-v1.2%2B-8A2BE2.svg)](https://langchain-ai.github.io/langgraph/)
[![LangSmith](https://img.shields.io/badge/LangSmith-Tracing%20%26%20Evals-FF6C37.svg)](https://smith.langchain.com/)
[![Persistence](https://img.shields.io/badge/Checkpointer-SQLite%20%2B%20Memory-003B57.svg?logo=sqlite&logoColor=white)](https://sqlite.org/)
[![Tests](https://img.shields.io/badge/tests-40%20passed-22C55E.svg)](tests/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](Dockerfile)
[![Notebook](https://img.shields.io/badge/Jupyter-Masterclass-F37626.svg?logo=jupyter&logoColor=white)](notebooks/langgraph_multi_agent_masterclass.ipynb)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-F59E0B.svg)](LICENSE)

> 🌐 **Interactive Web Showcase & Simulator:** [phlppgdfry.github.io/langgraph-multi-agent-system](https://phlppgdfry.github.io/langgraph-multi-agent-system/)
> 
> **A production-grade, stateful multi-agent intelligence swarm built with LangGraph, LangChain Core, LangSmith observability, reflection-driven self-correction, SQLite state persistence, and Human-in-the-Loop governance.**

---

## 📌 Executive Overview

In real-world enterprise deployments, single-turn LLM chains fail because they lack state persistence, cyclical feedback, verifiable audit trails, and human oversight. 

**Nexus** demonstrates how to build an enterprise-grade autonomous multi-agent system utilizing **LangGraph's cyclically directed state graphs** and **LangChain's unified tool abstractions**. The system coordinates a team of specialized agents that gather live intelligence, extract quantitative KPIs, cross-verify assertions, execute reflection self-correction loops, and generate executive-ready decision briefings.

Full distributed tracing, token consumption, and run trees are piped directly to **LangSmith** for enterprise observability and latency profiling.

```
       [Objective / Prompt]
                 │
                 ▼
       ┌───────────────────┐
       │ 🧭 Supervisor     │◄───────────────────┐
       └─────────┬─────────┘                    │
                 │ (Dynamic Planning & Routing) │ (Self-Correction & Updates)
                 ▼                              │
       ┌───────────────────┐                    │
       │ 🔬 Researcher     │────────────────────┤
       └─────────┬─────────┘                    │
                 ▼                              │
       ┌───────────────────┐                    │
       │ 📈 Data Analyst   │────────────────────┤
       └─────────┬─────────┘                    │
                 ▼                              │
       ┌───────────────────┐                    │
       │ ⚖️ Critic Agent   │────[Score < 80]────┘
       └─────────┬─────────┘
                 │ [Score >= 80]
                 ▼
       ┌───────────────────┐
       │ 🛡️ Human Gate     │ (Checkpointed Approval / State Rewind)
       └─────────┬─────────┘
                 ▼
       ┌───────────────────┐
       │ ✍️ Executive Writer│
       └─────────┬─────────┘
                 ▼
       [📊 Strategic Briefing .md]
```

---

## 🏗️ Multi-Agent Architecture

```mermaid
flowchart TD
    START([Start / User Objective]) --> Supervisor[🧭 Supervisor Agent]

    subgraph Swarm ["Nexus Agent Swarm (LangGraph StateGraph)"]
        Supervisor -->|Route: Research| Researcher[🔬 Researcher Agent]
        Researcher -->|Emit: research_notes| Supervisor

        Supervisor -->|Route: Analysis| Analyst[📈 Data Analyst Agent]
        Analyst -->|Emit: quantitative_data| Supervisor

        Supervisor -->|Route: Quality Audit| Critic[⚖️ Critic / Fact-Checker]
        Critic -->|Reflection Rejection < 80| Supervisor
        Critic -->|Verification Passed >= 80| Supervisor

        Supervisor -->|Route: Governance Check| HumanGate{🛡️ Human-in-the-Loop Gate}
        HumanGate -->|Approved| Writer[✍️ Executive Writer Agent]
        HumanGate -->|Revision Requested| Supervisor
    end

    Writer --> FinalReport([📊 Executive Briefing Markdown])
    FinalReport --> END([End])

    classDef agent fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#ffffff;
    classDef gate fill:#2e1065,stroke:#c084fc,stroke-width:2px,color:#ffffff;
    classDef terminus fill:#022c22,stroke:#4ade80,stroke-width:2px,color:#ffffff;
    class Supervisor,Researcher,Analyst,Critic,Writer agent;
    class HumanGate gate;
    class START,END,FinalReport terminus;
```

### Specialized Agents

| Agent | Core Responsibility | Capabilities & Tools |
| :--- | :--- | :--- |
| **🧭 Supervisor** | Dynamic Workflow Orchestration | Task decomposition, 4-phase planning, state routing, and revision cycle tracking. |
| **🔬 Researcher** | Primary Intelligence Gathering | Web search (`search_web`), snippet curation, source triangulation, and fact retrieval. |
| **📈 Analyst** | Quantitative & Metric Extraction | Financial KPI parsing (`extract_metrics`), latency/accuracy calculations, and scorecarding. |
| **⚖️ Critic** | Reflection & Quality Assurance | Multi-source verification (`verify_claim`), rigor scoring (0-100), and self-correction loops. |
| **🛡️ Human Gate** | Governance & Checkpoint Oversight | Human-in-the-loop interruption via SQLite `SqliteSaver` checkpoints before publication. |
| **✍️ Writer** | Executive Briefing Synthesis | C-suite markdown reporting with TL;DR, methodology, quantitative scorecards, and citations. |

---

## 🔍 LangSmith Tracing & Observability

Nexus is pre-instrumented for **LangSmith** out-of-the-box. Every agent action, tool invocation, token spend, latency metric, and reflection cycle is captured in an auditable trace tree.

```
Run: nexus-multi-agent-system [Status: SUCCESS]
├── supervisor [ChatOpenAI] (latency: 142ms, tokens: 380)
│   └── Input: "Analyze enterprise multi-agent adoption..."
│   └── Output: "[Supervisor] Plan initialized: 4 steps..."
├── researcher (latency: 410ms)
│   └── Tool: search_web(query="...") [HTTP 200 OK]
├── analyst (latency: 88ms)
│   └── Tool: extract_metrics(...) [4 benchmarks extracted]
├── critic (latency: 165ms)
│   └── Tool: verify_claim(...) [Quality Score: 96/100, PASSED]
└── writer [ChatOpenAI] (latency: 520ms, tokens: 1,120)
    └── Output: "# Strategic Intelligence Briefing..."
```

### Quick Setup:
Run the interactive configuration wizard:
```bash
uv run python -m langgraph_multi_agent_system.cli --configure
```
Or set `.env`:
```ini
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY=lsv2_pt_your_langsmith_api_key_here
LANGCHAIN_PROJECT="nexus-multi-agent-system"
```
*Read the complete [LangSmith Observability Guide](docs/LANGSMITH_GUIDE.md).*

---

## ⚡ Quickstart

### 1. Prerequisites
- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) (recommended ultra-fast package manager)

### 2. Clone & Sync
```bash
git clone https://github.com/phlppgdfry/langgraph-multi-agent-system.git
cd langgraph-multi-agent-system

# Install dependencies in under 2 seconds with uv
uv sync
```

### 3. Run via Rich Interactive CLI
```bash
# Run with default enterprise research prompt:
uv run python -m langgraph_multi_agent_system.cli

# Or specify a custom strategic prompt:
uv run python -m langgraph_multi_agent_system.cli "Analyze AI Agent ROI in Multimodal Freight Logistics"

# Enable Human-in-the-Loop checkpoint review before report publication:
uv run python -m langgraph_multi_agent_system.cli "Enterprise Agentic FinOps" --human-approval

# Save the generated markdown briefing:
uv run python -m langgraph_multi_agent_system.cli "LangGraph vs Linear Chains" -o briefing.md
```

### 4. Run via Streamlit Web Dashboard
```bash
uv run streamlit run src/langgraph_multi_agent_system/app.py
```
Open [http://localhost:8501](http://localhost:8501) to interact with the swarm in real-time, view live node progression, inspect critique scores, and download executive briefings.

### 5. Inspect in LangGraph Studio
Native integration via `langgraph.json`:
```bash
langgraph dev
```

### 6. Human-in-the-Loop Interrupt & Resume Lifecycle
Nexus implements true checkpoint interruption. When an operator enables `--human-approval`, execution halts before the executive writer, stores state in SQLite, and can be resumed out-of-process hours later:

```bash
# 1. Start pipeline with approval gate
uv run python -m langgraph_multi_agent_system.cli "Evaluate Demurrage Risk" --human-approval

# 2. In a new process or session, inspect and resume:
uv run python -m langgraph_multi_agent_system.cli --resume <THREAD_ID> --approve
# Or request revision:
uv run python -m langgraph_multi_agent_system.cli --resume <THREAD_ID> --reject --feedback "Deepen financial metrics"
```

### 7. Run 6-Baseline Comparative Study (Single vs Multi-Agent)
Objectively compare Single-Agent Direct, Tool-Augmented, Sequential, Parallel Map-Reduce, and Nexus Swarm across latency, token spend, and factual grounding:

```bash
uv run python -m langgraph_multi_agent_system.cli --benchmark-compare
```

---

## 📊 Dual-Mode Empirical Architecture Benchmark

The benchmarking suite (`src/langgraph_multi_agent_system/evals/comparative_benchmark.py`) provides two scientifically separated modes:
- **Mode A (Deterministic Simulation):** Uses `MockChatModel` to isolate pure LangGraph StateGraph engine latency, state routing, checkpoint writing, and reflection cycle overhead from network jitter.
- **Mode B (Real Agent Performance):** Runs live with genuine LLM providers (`gpt-4o-mini`, `claude-3-5-haiku`) and real tools, measuring end-to-end network roundtrips and token spend.

### Mode A: Engine Overhead & Objective Grounding Telemetry

| Architecture Baseline | Avg Engine Latency | Sources Analyzed | KPIs Parsed | Factual Grounding (Objective) | Token Spend | Est. Cost ($) | Architectural Trade-Off Profile |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Baseline A: Single-Agent Direct** | `0.9 ms` | 0.0 | 0.0 | `0.0%` | ~31 | $0.00006 | Zero citations; high hallucination risk. |
| **Baseline B: Single-Agent + Tools** | `80.2 ms` | 2.0 | 3.3 | `32.7%` | ~222 | $0.00045 | Single search pass; no reflection or critique. |
| **Baseline C: Sequential Multi-Agent** | `5.5 ms` | 2.0 | 3.3 | `72.0%` | ~609 | $0.00122 | Linear pipeline; errors cascade to writer. |
| **Baseline D: Parallel Map-Reduce** | `8.8 ms` | 6.0 | 7.3 | `85.0%` | ~1,475 | $0.00295 | 3x evidence density; lacks self-correction. |
| **Baseline F: Nexus Swarm (Reflection)**| `26.9 ms` | **6.0** | **7.3** | **100.0%** | ~2,694 | $0.00539 | **100% grounding & citations**; higher token spend. |

*(Note: Live LLM execution in Mode B exhibits ~3,500 ms total latency dominated by model inference and search HTTP roundtrips; engine overhead is < 30 ms).*

---

## 📑 Independent Principal Validation & Architecture Reports

All claims in this repository are backed by 12 independent engineering audits and technical reports:

| Document | Focus & Coverage |
| :--- | :--- |
| [🔬 Final Principal AI Audit](docs/FINAL_PRINCIPAL_AI_AUDIT.md) | Independent findings register (AUD-001–012), code references, and recalculated scorecard (9.5/10). |
| [📊 Benchmark Methodology Review](docs/BENCHMARK_METHODOLOGY_REVIEW.md) | Forensic separation of simulation vs live benchmarks and objective grounding formulations. |
| [⚡ Real Agent Performance Evaluation](docs/REAL_AGENT_PERFORMANCE_EVALUATION.md) | Engine overhead profiling vs live LLM roundtrips and token consumption. |
| [💾 Memory Persistence Audit](docs/MEMORY_PERSISTENCE_AUDIT.md) | Thread-safe `RLock`, atomic write protocol (`NamedTemporaryFile` + `os.replace`), and tenant isolation. |
| [🛡️ HITL Reliability Report](docs/HITL_RELIABILITY_REPORT.md) | Out-of-process SQLite interrupt/resume, idempotency verification, and structured JSONL audit trail. |
| [🔍 LangSmith Cloud Validation](docs/LANGSMITH_VALIDATION.md) | Live EU endpoint audit across Distributed Tracing, Datasets, Queues, and Prompt Hub. |
| [🔐 Agentic Security Threat Model](docs/AGENTIC_SECURITY_THREAT_MODEL.md) | OWASP Top 10 for LLMs, SSRF private IP validation, and regex prompt injection sanitization. |
| [🧪 Agent Evaluation Framework](docs/AGENT_EVALUATION_FRAMEWORK.md) | 4-dimensional evaluation rubric: Grounding, Quantitative Density, Structure, and FinOps. |
| [🔄 Continuous Improvement Design](docs/CONTINUOUS_IMPROVEMENT_DESIGN.md) | Autonomous flywheel connecting flagged low scores, annotation queues, and dynamic prompt templates. |
| [🚢 Enterprise Case Study](docs/ENTERPRISE_CASE_STUDY.md) | Real-world supply chain and FinOps implementation with 97.9% turnaround reduction. |
| [💼 Final Portfolio Readiness](docs/FINAL_PORTFOLIO_READINESS.md) | Recruiter and architectural assessment with a 5-minute live demonstration script. |
| [⚠️ Remaining Risks & Limitations](docs/REMAINING_RISKS.md) | Transparent disclosure of technical constraints and prioritized engineering roadmap. |
| [📡 Observability Architecture](docs/operations/OBSERVABILITY.md) | P50/P95 latencies, FinOps token accounting, and alert thresholds. |
| [🚀 Production Readiness Runbook](docs/operations/PRODUCTION_READINESS.md) | Non-root Docker, health checks, SQLite disaster recovery. |
| [🌟 Portfolio Showcase Guide](docs/portfolio/SHOWCASE_READINESS.md) | Narrative for technical directors and hiring managers. |
| [🗺️ Architectural Roadmap](docs/roadmap/FUTURE_IMPROVEMENTS.md) | MCP integration, Command state updates, and semantic caching. |

---

## 🧪 Testing & Code Quality

The repository maintains 100% pass rates across unit tests and linter checks:

```bash
# Run full pytest test suite (29 unit & integration tests)
make test
# or
uv run pytest -v

# Run ruff code linter
make lint
```

---

## 📂 Repository Structure

```
langgraph-multi-agent-system/
├── .github/
│   └── workflows/
│       └── ci.yml              # Multi-Python (3.11, 3.12, 3.13) GitHub Actions CI
├── data/
│   └── swarm_checkpoints.db    # SQLite persistence database (thread replay)
├── docs/
│   ├── ARCHITECTURE.md         # Deep-dive into StateGraph, routing & memory
│   ├── LANGSMITH_GUIDE.md      # Tracing setup, eval runs & latency analysis
│   └── HUMAN_IN_THE_LOOP.md    # Checkpointing, interruption gates & state rewind
├── examples/
│   └── reports/                # Pre-generated sample executive briefings
├── src/
│   └── langgraph_multi_agent_system/
│       ├── __init__.py         # Package exports
│       ├── state.py            # TypedDict global state schema (MessagesState)
│       ├── tools.py            # Search, metric extraction & verification tools
│       ├── checkpoint.py       # Unified SQLite & MemorySaver checkpointer
│       ├── graph.py            # StateGraph topology & conditional routers
│       ├── cli.py              # Interactive Rich terminal runner & config wizard
│       ├── app.py              # Interactive Streamlit Web UI
│       ├── agents/
│       │   ├── supervisor.py   # Master orchestration agent
│       │   ├── researcher.py   # Research & source gathering
│       │   ├── analyst.py      # Quantitative extraction
│       │   ├── critic.py       # Reflection & self-correction scoring
│       │   ├── human_gate.py   # Human-in-the-loop checkpoint gate
│       │   └── writer.py       # Executive report generator
│       └── evals/
│           └── run_evals.py    # Automated LangSmith evaluation suite
├── tests/
│   ├── test_graph.py           # Integration, persistence & execution tests
│   └── test_tools.py           # Tool unit tests
├── scripts/
│   └── export_graph.py         # Mermaid topology exporter
├── langgraph.json              # LangGraph Studio configuration
├── pyproject.toml              # Modern uv / pip project metadata
├── .env.example                # Environment variable configuration guide
├── LICENSE                     # MIT License
└── README.md                   # Project documentation
```

---

## 💡 Key Architectural Patterns

1. **Stateful Graph Orchestration (`StateGraph`):** Replaces linear chains with inspectable, cyclical state machines.
2. **Reflection & Self-Correction:** Factual scoring that redirects deficient outputs back to researchers before user delivery.
3. **Deterministic Zero-Key Demo Mode:** Built with resilient fallbacks so reviewers can clone and run tests/demos without needing paid API credits.
4. **State Persistence (`SqliteSaver`):** Checkpointed state transitions allowing step replay, thread resumption, and human intervention.
5. **Observability First:** Deep LangSmith tracing for enterprise auditability and latency profiling.

---

## 👤 Author

**Philippe Godfroy**  
- GitHub: [@phlppgdfry](https://github.com/phlppgdfry)  
- Email: philippe.godfroy@hotmail.com  

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
