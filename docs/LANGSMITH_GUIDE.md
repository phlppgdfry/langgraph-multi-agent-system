# 🔍 LangSmith Observability & Evaluation Guide

## 1. Why LangSmith?

In multi-agent systems, debugging silent failures, unexpected routing loops, or runaway token spend is nearly impossible without distributed tracing. 

**LangSmith** provides full visibility into:
- Individual agent execution latencies (P50, P95, P99).
- Exact prompt inputs and generated outputs at each node.
- Tool invocation arguments, returns, and HTTP status codes.
- Total token consumption and estimated inference cost per run.
- Automated regression benchmarks.

---

## 2. Configuration Setup

### Step 1: Create an API Key
1. Sign in to your LangSmith account at [smith.langchain.com](https://smith.langchain.com).
2. Navigate to **Settings** (gear icon in the bottom left) ➔ **API Keys**.
3. Click **Create API Key** and copy the generated token (`lsv2_pt_...`).

### Step 2: Configure Environment
You can either run the interactive CLI wizard:
```bash
uv run python -m langgraph_multi_agent_system.cli --configure
```
Or directly edit `.env`:
```ini
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY="lsv2_pt_your_actual_key_here"
LANGCHAIN_PROJECT="nexus-multi-agent-system"
```

---

## 3. Real-Time Trace Visualization

Once configured, every run through the CLI or Streamlit app generates an auditable trace in LangSmith:

```
Run: nexus-multi-agent-system [Status: SUCCESS]
├── supervisor (latency: 142ms, tokens: 380)
│   └── Input: "Analyze enterprise multi-agent adoption..."
│   └── Output: "[Supervisor] Plan initialized: 4 steps..."
├── researcher (latency: 410ms)
│   └── Tool: search_web(query="...") [HTTP 200 OK]
├── analyst (latency: 88ms)
│   └── Tool: extract_metrics(...) [4 metrics parsed]
├── critic (latency: 165ms)
│   └── Score: 94/100 [Approved]
└── writer (latency: 520ms, tokens: 1,120)
    └── Output: "# Strategic Intelligence Briefing..."
```

---

## 4. Running Automated Evaluations

Nexus includes an automated evaluation suite that tests topic completeness, critic rigor, and quantitative grounding:

```bash
uv run python -m langgraph_multi_agent_system.evals.run_evals
```

All evaluation results and metric distributions are automatically logged to the **Experiments** tab inside your LangSmith project.
