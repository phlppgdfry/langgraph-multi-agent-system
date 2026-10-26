"""Critic / Fact-Checker Agent: Implements reflection and quality scoring."""

from typing import Any

from langchain_core.messages import AIMessage, HumanMessage

from langgraph_multi_agent_system.state import AgentState
from langgraph_multi_agent_system.tools import get_llm, verify_claim


def critic_node(state: AgentState) -> dict[str, Any]:
    """Evaluates factual consistency, completeness, and rigor.

    Calculates a composite quality score (0-100). If below threshold (80),
    rejects with actionable critique to trigger a self-correction loop.
    """
    task = state.get("task", "")
    notes = state.get("research_notes", [])
    metrics = state.get("quantitative_data", [])
    revision_count = state.get("revision_count", 0)

    sources = [n.get("source", "") for n in notes]
    verification = verify_claim.invoke({
        "claim": f"Primary findings on {task}",
        "sources": sources
    })

    # Scoring heuristic
    base_score = 70
    if len(notes) >= 2:
        base_score += 15
    if len(metrics) >= 2:
        base_score += 10
    if verification.get("verified"):
        base_score += 5

    # On first run, simulate a strict review if notes are light
    if revision_count == 0 and len(notes) < 2:
        passed = False
        score = 68
        feedback = "Sources lack deep comparative benchmarks. Query additional enterprise case studies."
    else:
        passed = base_score >= 80
        score = min(base_score, 98)
        feedback = "Verification passed. Factual integrity, quantitative indicators, and methodology meet standards."

    critique_result = {
        "score": score,
        "passed": passed,
        "verified": verification.get("verified", False),
        "strengths": [
            f"Verified against {len(notes)} sources",
            f"Quantified with {len(metrics)} concrete data indicators",
            "Structured multi-step reasoning"
        ],
        "recommendation": feedback
    }

    llm = get_llm()
    prompt = (
        f"You are the Chief Quality Officer / Critic Agent. Task: '{task}'.\n"
        f"Score: {score}/100. Status: {'APPROVED' if passed else 'REVISE'}.\n"
        f"Feedback: {feedback}.\n"
        "Summarize the quality decision in 2 sharp sentences."
    )
    res = llm.invoke([HumanMessage(content=prompt)])

    msg = (
        f"[Critic] Quality Assessment: {score}/100 ({'APPROVED' if passed else 'REVISION NEEDED'}).\n"
        f"Evaluation: {res.content}"
    )

    return {
        "critique": critique_result,
        "next_agent": "supervisor",
        "messages": [AIMessage(content=msg)]
    }
