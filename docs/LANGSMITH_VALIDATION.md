# LANGSMITH ENTERPRISE OBSERVABILITY VALIDATION
**Component:** `src/langgraph_multi_agent_system/langsmith_utils.py`  
**Endpoint:** `https://eu.api.smith.langchain.com`  
**Reviewer:** LangSmith Observability Specialist & LLMOps Architect  
**Status:** Live Synchronized & Operationally Verified  

---

## 1. Cloud Architecture & EU Regional Configuration

The system is configured to communicate with the European Union instance of LangSmith:

- **LangSmith Web Dashboard:** `https://eu.smith.langchain.com`
- **LangSmith REST API Endpoint:** `https://eu.api.smith.langchain.com`
- **Active Project:** `nexus-multi-agent-system`
- **Authentication:** Scoped API key (`lsv2_pt_...`) securely loaded via `.env`.

### Client Factory (`get_langsmith_client`):
`langsmith_utils.py` automatically resolves the regional endpoint:
```python
client = Client(
    api_key=api_key,
    api_url=os.getenv("LANGCHAIN_ENDPOINT", "https://eu.api.smith.langchain.com")
)
```

---

## 2. Four Integrated LangSmith Pillars

The Nexus Swarm integrates all four primary observability surfaces:

```
┌────────────────────────────────────────────────────────────────────────┐
│                      LangSmith Cloud Platform                          │
│                                                                        │
│  ┌───────────────────────┐          ┌───────────────────────────────┐  │
│  │ 1. Tracing & Runs     │          │ 2. Datasets & Experiments     │  │
│  │ - Multi-agent spans   │          │ - Benchmark golden test suite │  │
│  │ - Tool input/outputs  │          │ - Automated precision scorers │  │
│  │ - Token & latency logs│          │ - Baseline comparisons        │  │
│  └───────────────────────┘          └───────────────────────────────┘  │
│                                                                        │
│  ┌───────────────────────┐          ┌───────────────────────────────┐  │
│  │ 3. Annotation Queues  │          │ 4. Prompts Hub                │  │
│  │ - Human review queues │          │ - nexus-supervisor            │  │
│  │ - Flagged low-scores  │          │ - nexus-critic-rubric         │  │
│  │ - Feedback curation   │          │ - Versioned prompt templates  │  │
│  └───────────────────────┘          └───────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

### 1. Distributed Tracing (`LANGCHAIN_TRACING_V2=true`)
Every graph execution emits OpenTelemetry-compliant trace spans:
- Node entries and exits (`supervisor`, `parallel_researcher`, `analyst`, `critic`, `writer`).
- Tool calls (`search_web`, `extract_metrics`, `verify_claim`).
- State mutations and metadata tags.

### 2. Datasets & Experiments
- **Dataset Name:** `nexus-multi-agent-benchmark-suite`
- **Dataset ID:** `1f7e3c90-9f55-460c-ad33-91ee12d5eef1`
- Contains representative input prompts across supply chain, adoption analysis, and FinOps token budgeting.
- Automated evaluation runs record `factual_grounding`, `citation_ratio`, and `latency_ms` metrics against dataset runs.

### 3. Human Annotation Queues
- **Queue Name:** `nexus-human-review-queue`
- **Queue ID:** `84f1b416-8c01-4435-a6a3-2d2c16110f08`
- Stores agent runs that scored below 80% or were flagged during Human-in-the-Loop review for human feedback and model alignment.

### 4. Managed Prompt Templates (Hub)
Synchronizes prompt contracts to the LangSmith Hub:
- `nexus-supervisor-prompt`: Autonomous decomposition and routing rules.
- `nexus-critic-rubric`: 4-pillar factual evaluation criteria.
- `nexus-writer-synthesis`: Executive decision briefing schema.

---

## 3. Operational Command Reference

```bash
# Verify client and list recent runs
uv run python -c "from langgraph_multi_agent_system.langsmith_utils import get_langsmith_client; c = get_langsmith_client(); print('Connected:', bool(c))"

# Push and sync all datasets, annotation queues, and prompts
uv run python -m langgraph_multi_agent_system.cli --sync-langsmith

# Run automated evaluation experiment on LangSmith
uv run python -m langgraph_multi_agent_system.cli --evals
```
