"""Critic / Fact-Checker Agent: Implements multi-criteria reflection and quality scoring."""

from typing import Any

from langchain_core.messages import AIMessage, HumanMessage

from langgraph_multi_agent_system.schemas import CriticVerdict
from langgraph_multi_agent_system.state import AgentState
from langgraph_multi_agent_system.tools import get_llm, verify_claim


def critic_node(state: AgentState) -> dict[str, Any]:
    """Evaluates factual consistency, completeness, and rigor.

    Calculates a multi-criteria quality score (0-100) across:
    1. Citation Diversity & Source Credibility (0-25)
    2. Quantitative Indicator Density (0-25)
    3. Factual Verification & Claim Grounding (0-25)
    4. Subtask & Domain Coverage (0-25)

    If below threshold (80), rejects with actionable critique to trigger
    a self-correction loop in the StateGraph.
    """
    task = state.get("task", "")
    notes = state.get("research_notes", [])
    metrics = state.get("quantitative_data", [])
    subtasks = state.get("subtasks", [])
    revision_count = state.get("revision_count", 0)

    sources = [n.get("source", "") for n in notes if n.get("source")]
    verification = verify_claim.invoke(
        {"claim": f"Primary findings on {task}", "sources": sources}
    )

    # 1. Citation Diversity Score (0-25)
    unique_domains = {s.split("/")[2] if "://" in s else s for s in sources}
    citation_score = min(len(unique_domains) * 8 + (5 if len(sources) >= 3 else 0), 25)

    # 2. Quantitative Density Score (0-25)
    metric_categories = {m.get("type", "") for m in metrics}
    quant_score = min(len(metrics) * 5 + len(metric_categories) * 3, 25)

    # 3. Factual Verification Score (0-25)
    grounding_score = 25 if verification.get("verified") and sources else 10

    # 4. Subtask Coverage Score (0-25)
    covered_subtasks = 0
    notes_text = " ".join(
        [n.get("title", "") + " " + n.get("snippet", "") for n in notes]
    ).lower()
    for st in subtasks:
        key_terms = [w.lower() for w in st.split() if len(w) > 4]
        if any(kt in notes_text for kt in key_terms):
            covered_subtasks += 1
    subtask_score = int((covered_subtasks / max(len(subtasks), 1)) * 25)

    composite_score = citation_score + quant_score + grounding_score + subtask_score

    # On first revision cycle, demand rigorous coverage if evidence is sparse
    if revision_count == 0 and (len(notes) < 3 or len(metrics) < 2):
        passed = False
        score = min(composite_score, 74)
        feedback = (
            "Evidence base lacks breadth. Expand parallel worker research to address "
            "missing quantitative indicators and verify primary citations."
        )
    else:
        passed = composite_score >= 80
        score = min(composite_score, 98)
        feedback = (
            "Verification passed. Composite evidence meets enterprise accuracy, "
            "quantitative grounding, and domain coverage thresholds."
            if passed
            else "Quality threshold not met. Additional cross-source corroboration required."
        )

    strengths = [
        f"Corroborated across {len(sources)} source citations ({len(unique_domains)} distinct domains)",
        f"Quantified with {len(metrics)} indicators across {len(metric_categories)} categories",
        f"Addressed {covered_subtasks} of {len(subtasks)} strategic subtasks",
    ]

    verdict_model = CriticVerdict(
        score=score,
        passed=passed,
        verified=verification.get("verified", False),
        strengths=strengths,
        recommendation=feedback,
    )
    critique_result = verdict_model.model_dump()

    llm = get_llm()
    prompt = (
        f"You are the Chief Quality Officer / Critic Agent. Task: '{task}'.\n"
        f"Composite Score: {score}/100. Status: {'APPROVED' if passed else 'REVISE'}.\n"
        f"Citation score: {citation_score}/25 | Quant score: {quant_score}/25 | "
        f"Grounding score: {grounding_score}/25 | Subtask score: {subtask_score}/25.\n"
        f"Feedback: {feedback}.\n"
        "Provide a concise quality assessment justification."
    )
    res = llm.invoke([HumanMessage(content=prompt)])

    msg = (
        f"[Critic] Quality Assessment: {score}/100 ({'APPROVED' if passed else 'REVISION NEEDED'}).\n"
        f"Rubric Breakdown: Citations={citation_score}/25, Metrics={quant_score}/25, "
        f"Grounding={grounding_score}/25, Coverage={subtask_score}/25.\n"
        f"Justification: {res.content}"
    )

    return {
        "critique": critique_result,
        "next_agent": "supervisor",
        "messages": [AIMessage(content=msg)],
    }
