# REMAINING RISKS, LIMITATIONS & FUTURE ROADMAP
**Repository:** `phlppgdfry/langgraph-multi-agent-system`  
**Reviewer:** Principal Agentic AI Engineer & SRE Architect  
**Status:** Transparent Risk Disclosure & Mitigation Strategy  

---

## 1. Technical Limitations & Known Constraints

In the spirit of uncompromising engineering honesty, this register outlines current technical boundaries and operational risks:

### 1. SQLite Concurrency under High Distributed Load
- **Current State:** The SQLite checkpointer (`data/checkpoints.db`) uses standard SQLite file locking.
- **Risk:** In multi-node Kubernetes clusters with dozens of distributed agent workers writing simultaneously, SQLite may encounter `sqlite3.OperationalError: database is locked`.
- **Mitigation / Next Step:** For horizontal multi-pod deployments, migrate the checkpointer backend to Postgres (`langgraph.checkpoint.postgres` / Neon Postgres).

### 2. File-Backed Disk Store Scalability
- **Current State:** `PersistentDiskStore` serializes memory to an atomic JSON file.
- **Risk:** While safe up to thousands of records with `RLock` and atomic file swapping, scaling beyond 100,000 memories will increase JSON serialization overhead.
- **Mitigation / Next Step:** Add an optional Redis or PostgreSQL pgvector store backend for vector embeddings and sub-millisecond similarity recall at scale.

### 3. Public Web Search Rate Limiting
- **Current State:** The free DuckDuckGo search integration (`ddgs`) relies on scraping endpoints without an API key.
- **Risk:** Aggressive concurrent queries during intensive parallel research can trigger upstream HTTP 429 rate limiting or bot challenge blocks.
- **Mitigation / Next Step:** In production, wire an enterprise search provider with authenticated API keys (e.g. Tavily Search, Google Custom Search API, or Firecrawl).

### 4. Dynamic Token Context Budgets
- **Current State:** Intermediate agent notes are accumulated into the typed state list.
- **Risk:** In extensive reflection loops with many revisions, state size can grow, consuming increasing context window tokens on successive agent passes.
- **Mitigation / Next Step:** Implement automatic state compression / summarization nodes when intermediate research notes exceed 4,000 tokens.

---

## 2. Prioritized Engineering Roadmap

| Milestone | Target | Description | Expected Impact |
|---|---|---|---|
| **v1.3** | PostgreSQL Checkpointing | Add `PostgresSaver` option for distributed multi-pod Kubernetes deployments. | Eliminates SQLite locking bottlenecks. |
| **v1.4** | Vector BaseStore Embeddings | Integrate pgvector / Chroma for semantic memory recall with embedding distances. | Sub-millisecond similarity search across 1M+ memories. |
| **v1.5** | Streaming WebSocket API | Add FastAPI WebSocket streaming endpoint for token-by-token frontend rendering. | Drastically reduces perceived time-to-first-token in web apps. |
| **v1.6** | Multi-Modal Evaluation | Extend Analyst agent to parse PDFs, charts, and image screenshots. | Expands ingestion capabilities to corporate financial decks. |
