# AGENT EVALUATION FRAMEWORK & METRIC TAXONOMY
**Component:** `src/langgraph_multi_agent_system/evals/` & LangSmith Evaluators  
**Reviewer:** LLM Evaluation Researcher  
**Status:** Multi-Dimensional & Statistically Grounded  

---

## 1. Evaluation Architecture & Philosophy

Evaluating autonomous multi-agent systems requires moving beyond simple string-matching or BLEU/ROUGE metrics. The Nexus Swarm evaluation framework assesses four discrete dimensions:

```
                  ┌───────────────────────────────────────────────┐
                  │          Multi-Agent Evaluation Rubric        │
                  └───────┬──────────────┬──────────────┬─────────┘
                          │              │              │
        ┌─────────────────┴─┐   ┌────────┴────────┐   ┌─┴────────────────┐
        ▼                   ▼   ▼                 ▼   ▼                  ▼
┌───────────────┐   ┌───────────────┐     ┌───────────────┐   ┌────────────────┐
│ 1. Grounding  │   │ 2. Quantitative│    │ 3. Structural │   │ 4. Operational │
│ - Citations   │   │ - Metric count│     │ - Plan check  │   │ - Latency (ms) │
│ - Evidence    │   │ - KPI density │     │ - Reducers    │   │ - Token spend  │
│ - Overlap %   │   │ - Pydantic    │     │ - Revision lim│   │ - Checkpoints  │
└───────────────┘   └───────────────┘     └───────────────┘   └────────────────┘
```

---

## 2. Metric Taxonomy & Scoring Formulations

### Dimension 1: Factual Grounding & Corroboration ($M_{grounding}$)
Evaluates whether synthesized statements originate from retrieved research snippets rather than model hallucination.
- **Citation Density:** Ratio of validated source citations to total generated paragraphs.
- **Lexical Overlap:** Computed via `verify_claim` token comparison ($R_{overlap} > 0.25$).
- **Scoring Range:** 0.0 to 1.0 (Target: $\ge 0.90$).

### Dimension 2: Quantitative Density & Rigor ($M_{quantitative}$)
Evaluates whether findings contain measurable data rather than generic marketing prose.
- Evaluated via `extract_metrics` tool and Pydantic schema validation.
- Requires at least 3 distinct quantitative metrics (percentages, financials, throughput multipliers).
- Scoring: $M_{quant} = \min(1.0, N_{metrics} / 4.0)$.

### Dimension 3: Structural Integrity & Task Decomposition ($M_{structure}$)
Evaluates whether the agent swarm executed all planned workstreams.
- Dynamically decomposed into subtasks by supervisor (`_decompose_objective_into_subtasks`).
- Evaluated by the Critic node across 4 pillars:
  1. *Citations Pillar* (25 pts)
  2. *Quantitative Metrics Pillar* (25 pts)
  3. *Factual Grounding Pillar* (25 pts)
  4. *Subtask Completion Pillar* (25 pts)
- Threshold: 80 / 100 required to pass to writer without triggering a revision loop.

### Dimension 4: Operational FinOps & Efficiency ($M_{finops}$)
- **Token Efficiency Ratio:** $\text{Grounding Gain} / \text{Token Overhead}$.
- **Latency Budget:** Ensure total multi-agent latency remains within the target SLA (< 30 ms engine overhead; < 5.0 s live LLM execution).

---

## 3. LangSmith Continuous Evaluators

When syncing evaluations to LangSmith via `langsmith_utils.py`:
1. `evaluate_factual_grounding`: Computes automated score based on citation counts.
2. `evaluate_quantitative_density`: Checks Pydantic metric extraction count.
3. `evaluate_latency`: Logs millisecond response times against SLA thresholds.
All evaluator results are visualized in the LangSmith **Datasets & Experiments** tab with side-by-side baseline diffs.
