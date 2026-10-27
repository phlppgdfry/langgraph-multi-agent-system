"""Supervisor Agent: Orchestrates the multi-agent swarm workflow."""

from typing import Any

from langchain_core.messages import AIMessage, HumanMessage

from langgraph_multi_agent_system.state import AgentState
from langgraph_multi_agent_system.tools import get_llm


def _decompose_objective_into_subtasks(task: str) -> list[str]:
    """Dynamically determine parallel research subtasks tailored to the strategic objective."""
    t_lower = task.lower()
    if any(k in t_lower for k in ["supply chain", "logistics", "freight", "container"]):
        return [
            "Port Congestion, Container Dwell Time & Demurrage Mitigation",
            "Autonomous Route Optimization & Carrier SLA Performance",
            "Customs Clearance, Regulatory Compliance & Border Risk",
        ]
    elif any(k in t_lower for k in ["finops", "token", "cost", "budget"]):
        return [
            "Token Budget Allocation & Multi-Tier Inference Caching",
            "Model Cost-to-Performance Benchmarks & Provider Routing",
            "Autonomous Spend Ceilings & Financial Governance",
        ]
    elif any(k in t_lower for k in ["langgraph", "langchain", "multi-agent", "swarm"]):
        return [
            "StateGraph Architecture, Checkpoint Persistence & HITL",
            "Multi-Agent Synthesis Latency & Token Economics",
            "Enterprise Security, Red-Teaming & Production Guardrails",
        ]
    else:
        # Dynamic decomposition for generic strategic questions
        words = [w for w in task.split() if len(w) > 3][:4]
        topic = " ".join(words) or task
        return [
            f"{topic}: Technical Architecture & Operational Frameworks",
            f"{topic}: Quantitative ROI, Latency & Cost Indicators",
            f"{topic}: Compliance, Risk Matrix & Governance Verification",
        ]


def supervisor_node(state: AgentState) -> dict[str, Any]:
    """Evaluates current progress and decides the next agent to invoke."""
    task = state.get("task", "Analyze technology trends")
    plan = state.get("plan", [])
    research_notes = state.get("research_notes", [])
    quantitative_data = state.get("quantitative_data", [])
    critique = state.get("critique", {})
    revision_count = state.get("revision_count", 0)
    subtasks = state.get("subtasks", [])

    llm = get_llm()

    # Formulate initial plan and tailored subtasks if empty
    if not plan or not subtasks:
        plan_prompt = (
            f"You are the Supervisor of an elite multi-agent system. Task: '{task}'.\n"
            "Break this task into 4 strategic phases:\n"
            "1. Deep factual research and source gathering.\n"
            "2. Quantitative metrics and financial/performance analysis.\n"
            "3. Fact-checking, consistency critique and reflection.\n"
            "4. Executive briefing generation."
        )
        _ = llm.invoke([HumanMessage(content=plan_prompt)])
        new_plan = [
            "1. Deep factual research and parallel source gathering",
            "2. Quantitative metrics and benchmark analysis",
            "3. Fact-checking, consistency critique and reflection",
            "4. Executive briefing generation",
        ]
        dynamic_subtasks = _decompose_objective_into_subtasks(task)
        return {
            "plan": new_plan,
            "subtasks": dynamic_subtasks,
            "next_agent": "researcher",
            "messages": [
                AIMessage(
                    content=(
                        f"[Supervisor] Plan initialized: {len(new_plan)} phases.\n"
                        f"Decomposed objective into {len(dynamic_subtasks)} tailored workstreams:\n"
                        + "\n".join(f"  • {st}" for st in dynamic_subtasks)
                    )
                )
            ],
        }

    # If no research done yet -> researcher
    if not research_notes:
        return {
            "next_agent": "researcher",
            "messages": [
                AIMessage(
                    content="[Supervisor] Routing to Researcher for parallel data collection."
                )
            ],
        }

    # If research done but no quantitative analysis -> analyst
    if not quantitative_data:
        return {
            "next_agent": "analyst",
            "messages": [
                AIMessage(
                    content="[Supervisor] Research complete. Routing to Analyst for quantitative metrics."
                )
            ],
        }

    # If quantitative done but no critique -> critic
    if not critique:
        return {
            "next_agent": "critic",
            "messages": [
                AIMessage(
                    content="[Supervisor] Quantitative analysis complete. Routing to Critic for self-reflection evaluation."
                )
            ],
        }

    # If critique requested revision and within max revisions
    passed = critique.get("passed", False)
    max_revisions = state.get("max_revisions", 2)
    if not passed and revision_count < max_revisions:
        return {
            "next_agent": "researcher",
            "revision_count": revision_count + 1,
            "messages": [
                AIMessage(
                    content=f"[Supervisor] Critique score ({critique.get('score')}/100) below threshold. Initiating revision cycle #{revision_count + 1}."
                )
            ],
        }

    # Check if human approval is required
    requires_approval = state.get("requires_human_approval", False)
    approved = state.get("human_approved", None)
    if requires_approval and approved is None:
        return {
            "next_agent": "human_gate",
            "messages": [
                AIMessage(
                    content="[Supervisor] Quality checks passed. Routing to Human Gatekeeper for executive review."
                )
            ],
        }

    # If human rejected and requested revision
    if approved is False and revision_count < max_revisions + 1:
        feedback = state.get("operator_feedback", "Operator requested revision.")
        return {
            "next_agent": "researcher",
            "revision_count": revision_count + 1,
            "human_approved": None,  # Reset for next human review cycle
            "messages": [
                AIMessage(
                    content=f"[Supervisor] Operator requested revisions: '{feedback}'. Routing back to Researcher."
                )
            ],
        }

    # Ready for final executive writing
    return {
        "next_agent": "writer",
        "messages": [
            AIMessage(
                content="[Supervisor] All verification stages passed. Routing to Executive Writer."
            )
        ],
    }
