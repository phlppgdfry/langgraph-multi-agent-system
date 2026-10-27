# 📡 Operational Observability & LLMOps Architecture

**System:** Nexus Multi-Agent Swarm  
**Platform:** LangSmith EU / Distributed OpenTelemetry Spans  
**Lead:** MLOps & LLMOps Architect, DevOps & SRE Engineer  

---

## 1. Observability Architecture Overview

In distributed multi-agent systems, failure modes are non-linear: an agent might not throw an exception, but instead enter an unhelpful looping pattern, hallucinate unsupported figures, or consume excessive tokens.

Nexus instruments every state transition with **hierarchical distributed tracing** via LangSmith:

```
[Swarm Root Trace: nexus-multi-agent-system]
 │
 ├── [Node Span: supervisor] ────────► Duration, Model, Tokens, Routing Decision
 ├── [Parallel Span: researcher] ────► Worker Concurrency, Search HTTP Status Codes
 │    ├── [Subtask Worker 1] ────────► Query Latency, Result Count
 │    ├── [Subtask Worker 2] ────────► Query Latency, Result Count
 │    └── [Subtask Worker 3] ────────► Query Latency, Result Count
 ├── [Node Span: analyst] ───────────► Parsing Regex Duration, Validated Metric Count
 ├── [Node Span: critic] ────────────► 4-Pillar Score, Pass/Fail Verdict
 └── [Node Span: writer] ────────────► Synthesis Duration, Output Token Count
```

---

## 2. Key Telemetry Metrics & KPIs

| Telemetry Metric | Target / SLA | Measurement Mechanism | Alert Threshold |
| :--- | :---: | :--- | :--- |
| **P50 Run Latency** | `< 2.5s` (API) | LangSmith Run Tree Duration | `> 5.0s` |
| **P95 Run Latency** | `< 6.0s` (API) | LangSmith Run Tree Duration | `> 10.0s` |
| **Token Cost per Run** | `< $0.01` | LangSmith FinOps Accounting | `> $0.03` |
| **Reflection Cycle Rate** | `1.2 avg` | `revision_count` in Checkpoint State | `> 2.5 avg` |
| **Tool Error Rate** | `< 1.0%` | HTTP Status on Search & Extraction | `> 5.0%` |
| **HITL Approval Time** | Operator Driven | Delta between `human_gate` and resume | `> 24 hours` |

---

## 3. Metadata & Tagging Strategy

Every execution run automatically includes standardized audit tags:
- `tags`: `["production", "swarm-v2", "reflection", "provider:openai"]`
- `metadata`:
  - `thread_id`: UUID tracking checkpoint session in SQLite.
  - `provider`: Active model backend (`openai`, `anthropic`, `google`, `mock`).
  - `human_in_the_loop`: Boolean indicator whether approval gates were enforced.
  - `revision_count`: Number of reflection cycles executed.

This enables instant filtering, latency heatmaps, and cost attribution in the LangSmith dashboard.

---

## 4. Privacy & Data Governance

1. **Secret Scrubbing:** Environment variables, API keys, and authorization tokens are strictly filtered out of trace payloads.
2. **Data Residency:** Configured to target the LangSmith EU cloud (`https://eu.api.smith.langchain.com`), ensuring telemetry data complies with European data sovereignty and GDPR principles.
3. **Trace Retention:** Retention policies can be configured in LangSmith to automatically prune development traces after 14 days while retaining benchmark datasets indefinitely.
