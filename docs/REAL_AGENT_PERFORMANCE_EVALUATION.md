# REAL AGENT PERFORMANCE EVALUATION & LATENCY PROFILING
**Environment:** Python 3.13.18, LangGraph 1.2.17, LangChain Core 1.7.0  
**Host Architecture:** Apple M-Series Silicon (macOS Darwin 25.1.0)  
**Profile Date:** October 28, 2026  

---

## 1. Experimental Setup & Mode Separation

To provide transparent, reproducible telemetry, performance measurements are partitioned into two profiles:

| Parameter | Mode A: Deterministic Engine Profile | Mode B: Live Provider Profile |
|---|---|---|
| **Model Engine** | `MockChatModel` (Deterministic) | `gpt-4o-mini` / `claude-3-5-haiku` |
| **Search Subsystem** | Deterministic domain knowledge base | Live `duckduckgo_search` / `ddgs` |
| **Persistence Engine** | SQLite Checkpointer (`data/checkpoints.db`) | SQLite Checkpointer (`data/checkpoints.db`) |
| **Cross-Thread Store** | `SqliteMemoryStore` / `PersistentDiskStore` | `SqliteMemoryStore` / `PersistentDiskStore` |
| **Temperature** | 0.0 | 0.2 |
| **Max Revisions** | 1 cycle | 2 cycles |
| **Evaluation Scope** | In-memory graph engine overhead & SQLite I/O | Live network roundtrip & token generation |

---

## 2. Empirical Benchmark Telemetry (Mode A: Engine Overhead)

Collected across 15 automated test executions using the refactored evaluation suite:

| Architectural Baseline | Avg Engine Latency | Sources Analyzed | KPIs Extracted | Objective Grounding | Estimated Tokens | Est. Engine Cost |
|---|---|---|---|---|---|---|
| **Baseline A: Single-Agent Direct** | 0.9 ms | 0.0 | 0.0 | **0.0%** | 31 tokens | $0.00006 |
| **Baseline B: Single-Agent + Tools** | 80.2 ms | 2.0 | 3.3 | **32.7%** | 222 tokens | $0.00045 |
| **Baseline C: Sequential Pipeline** | 5.5 ms | 2.0 | 3.3 | **72.0%** | 609 tokens | $0.00122 |
| **Baseline D: Parallel Map-Reduce** | 8.8 ms | 6.0 | 7.3 | **85.0%** | 1,475 tokens | $0.00295 |
| **Baseline F: Nexus Swarm (Reflection)**| 26.9 ms | 6.0 | 7.3 | **100.0%** | 2,694 tokens | $0.00539 |

### Engine Component Latency Breakdown:
- **Graph State Reducers & Node Transitions:** ~1.2 ms per node hop.
- **SQLite Checkpoint Snapshot Serialization:** ~3.4 ms per checkpoint write.
- **Atomic Disk Store Write:** ~1.8 ms per store mutation.
- **Reflection Cycle & Critic Gate:** ~8.2 ms evaluation overhead.

---

## 3. Analytical Projections for Live Network Execution (Mode B)

> [!NOTE]
> The figures below represent **analytical latency projections** based on standard public cloud API roundtrip profiles for small-to-medium LLMs (`gpt-4o-mini` / `claude-3-5-haiku`). Live performance will vary based on regional network latency, prompt length, and upstream server load.

| Step / Node | Projected Provider Latency (TTFT + Output) | Projected Tool HTTP Latency | Estimated Output Tokens |
|---|---|---|---|
| **1. Supervisor Plan Initialization** | ~400 - 600 ms | 0 ms | ~110 tokens |
| **2. Parallel Researcher (3 concurrent)** | ~800 - 1,200 ms | ~600 - 900 ms (concurrent HTTP) | ~650 tokens |
| **3. Quantitative Data Analyst** | ~450 - 700 ms | 0 ms | ~280 tokens |
| **4. Critic 4-Pillar Reflection** | ~500 - 800 ms | 0 ms | ~240 tokens |
| **5. Executive Writer Briefing** | ~1,000 - 1,800 ms | 0 ms | ~780 tokens |
| **Total Swarm Latency (Single Pass)** | **~3.2 - 5.1 seconds** | **~600 - 900 ms** | **~2,060 tokens** |
| **With 1 Revision Cycle** | **~5.0 - 8.0 seconds** | **~1,200 - 1,800 ms** | **~3,100 tokens** |

### Key Architectural Takeaway:
The local LangGraph state engine contributes **< 30 ms** of latency overhead, representing less than 1% of total execution time in live deployment. The remaining 99% of time is consumed by external LLM provider generation and HTTP network calls.
