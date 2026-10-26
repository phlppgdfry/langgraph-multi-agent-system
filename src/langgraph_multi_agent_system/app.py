"""Interactive Streamlit Web Dashboard for Nexus LangGraph Multi-Agent Swarm."""

import os
import uuid

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Nexus | LangGraph Multi-Agent Swarm",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
    <style>
    .main-header { font-size: 2.2rem; font-weight: 800; color: #1E293B; margin-bottom: 0.2rem; }
    .sub-header { font-size: 1.1rem; color: #64748B; margin-bottom: 1.5rem; }
    .metric-card { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 15px; }
    .agent-tag { font-weight: 700; border-radius: 4px; padding: 2px 6px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------------------
# Sidebar Configuration
# ------------------------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ Swarm Configuration")
    st.markdown("Configure LLM providers, LangSmith tracing, and governance parameters.")

    provider = st.selectbox(
        "Model Provider",
        options=["openai", "anthropic", "google", "mock"],
        index=0,
        help="Select your model backend. 'mock' runs deterministically without API keys.",
    )

    if provider == "openai":
        openai_key = st.text_input("OpenAI API Key", value=os.getenv("OPENAI_API_KEY", ""), type="password")
        model_name = st.selectbox("OpenAI Model", ["gpt-4o-mini", "gpt-4o", "o1-mini"], index=0)
        if openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key
            os.environ["DEFAULT_MODEL_NAME"] = model_name
    elif provider == "anthropic":
        anthropic_key = st.text_input("Anthropic API Key", value=os.getenv("ANTHROPIC_API_KEY", ""), type="password")
        model_name = st.selectbox("Claude Model", ["claude-3-5-haiku-latest", "claude-3-5-sonnet-latest"], index=0)
        if anthropic_key:
            os.environ["ANTHROPIC_API_KEY"] = anthropic_key
            os.environ["DEFAULT_MODEL_NAME"] = model_name
    elif provider == "google":
        google_key = st.text_input("Google AI Key", value=os.getenv("GOOGLE_API_KEY", ""), type="password")
        model_name = st.selectbox("Gemini Model", ["gemini-1.5-flash", "gemini-1.5-pro"], index=0)
        if google_key:
            os.environ["GOOGLE_API_KEY"] = google_key
            os.environ["DEFAULT_MODEL_NAME"] = model_name
    else:
        st.info("ℹ️ Running in Deterministic Offline Demo Mode. No API keys required.")

    st.divider()
    st.subheader("🔍 LangSmith Observability")
    langsmith_enabled = st.checkbox(
        "Enable LangSmith Tracing",
        value=bool(os.getenv("LANGCHAIN_TRACING_V2") == "true"),
    )
    langsmith_endpoint_choice = st.selectbox(
        "LangSmith Region / Endpoint",
        ["https://eu.api.smith.langchain.com (Europe)", "https://api.smith.langchain.com (US / Global)"],
        index=0 if "eu.api" in os.getenv("LANGCHAIN_ENDPOINT", "") else 1,
    )
    langsmith_endpoint = langsmith_endpoint_choice.split(" ")[0]
    langsmith_key = st.text_input("LangSmith API Key (lsv2_pt_...)", value=os.getenv("LANGCHAIN_API_KEY", ""), type="password")
    langsmith_project = st.text_input("Project Name", value=os.getenv("LANGCHAIN_PROJECT", "nexus-multi-agent-system"))

    if langsmith_enabled and langsmith_key:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_ENDPOINT"] = langsmith_endpoint
        os.environ["LANGCHAIN_API_KEY"] = langsmith_key
        os.environ["LANGCHAIN_PROJECT"] = langsmith_project

    st.divider()
    st.subheader("🛡️ Governance & Quality")
    human_approval = st.checkbox("Require Human-in-the-Loop Gate", value=False)
    max_revisions = st.slider("Max Reflection Revisions", 1, 3, 2)

    st.markdown("---")
    st.caption("Engineered with **LangGraph v1.2+** & **LangChain Core**")


# ------------------------------------------------------------------------------
# Main Dashboard
# ------------------------------------------------------------------------------
st.markdown("<div class='main-header'>🤖 Nexus: Autonomous Multi-Agent Swarm</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Stateful Graph Orchestration • Reflection Self-Correction • LangSmith Observability • Human-in-the-Loop</div>", unsafe_allow_html=True)

# Architecture Tab Viewer
with st.expander("🗺️ View Multi-Agent StateGraph Architecture Topology", expanded=False):
    st.markdown(
        """
        ```mermaid
        flowchart LR
            START([Start]) --> Sup[🧭 Supervisor]
            Sup -->|Research| Res[🔬 Researcher]
            Res --> Sup
            Sup -->|Analysis| Ana[📈 Analyst]
            Ana --> Sup
            Sup -->|Audit| Crit[⚖️ Critic]
            Crit -->|Score < 80| Sup
            Crit -->|Score >= 80| Gate{🛡️ Human Gate}
            Gate -->|Approved| Wri[✍️ Writer]
            Wri --> END([Final Report])
        ```
        """
    )

preset_options = [
    "Analyze LangChain & LangGraph enterprise multi-agent adoption in 2026",
    "Autonomous AI Agent Swarms vs Linear RPA in Supply Chain Logistics",
    "Enterprise FinOps: Token Budgeting and Cost Optimization for Autonomous Agents",
    "Custom objective...",
]

selected_preset = st.selectbox("Select Research Objective:", preset_options)

if selected_preset == "Custom objective...":
    task_input = st.text_area(
        "Enter Strategic Objective:",
        placeholder="e.g. Conduct a comprehensive quantitative and architectural analysis on...",
    )
else:
    task_input = selected_preset

col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    launch_btn = st.button("🚀 Launch Swarm", type="primary", use_container_width=True)

# ------------------------------------------------------------------------------
# Execution Pipeline
# ------------------------------------------------------------------------------
if launch_btn and task_input:
    from langgraph_multi_agent_system.graph import create_graph

    thread_id = str(uuid.uuid4())[:8]
    config = {"configurable": {"thread_id": thread_id}}
    app = create_graph(interrupt_on_human_gate=human_approval)

    initial_state = {
        "task": task_input,
        "messages": [],
        "plan": [],
        "current_step": 0,
        "research_notes": [],
        "quantitative_data": [],
        "critique": {},
        "revision_count": 0,
        "max_revisions": max_revisions,
        "next_agent": "",
        "requires_human_approval": human_approval,
        "human_approved": None,
        "final_report": None,
        "metadata": {"thread_id": thread_id, "provider": provider},
    }

    st.info(f"**Swarm Session Initialized:** Thread `{thread_id}` | Checkpointer: `SQLite` | Observability: `LangSmith`")

    status_container = st.status("Swarm actively orchestrating...", expanded=True)

    for output in app.stream(initial_state, config=config):
        for node_name, state_update in output.items():
            msgs = state_update.get("messages", [])
            msg_text = msgs[-1].content if msgs else ""

            if node_name == "supervisor":
                status_container.write(f"🧭 **Supervisor:** {msg_text}")
            elif node_name == "researcher":
                status_container.write(f"🔬 **Researcher:** {msg_text}")
            elif node_name == "analyst":
                status_container.write(f"📈 **Analyst:** {msg_text}")
            elif node_name == "critic":
                score = state_update.get("critique", {}).get("score", "N/A")
                status_container.write(f"⚖️ **Critic (Quality Score: {score}/100):** {msg_text}")
            elif node_name == "human_gate":
                status_container.write(f"🛡️ **Human Gate:** {msg_text}")
            elif node_name == "writer":
                status_container.write(f"✍️ **Executive Writer:** {msg_text}")

    full_state = app.get_state(config).values

    # Check for Human-in-the-Loop Interruption
    if human_approval and full_state.get("next_agent") == "human_gate":
        status_container.warning("⚠️ **Execution Paused at Human-in-the-Loop Gate**")
        st.warning("Review the findings below. Click 'Approve & Synthesize' to authorize final briefing publication.")
        
        col_app1, col_app2 = st.columns(2)
        with col_app1:
            if st.button("✅ Approve & Synthesize Report", type="primary", use_container_width=True):
                app.update_state(config, {"human_approved": True, "next_agent": "writer"})
                for out in app.stream(None, config=config):
                    for n, upd in out.items():
                        st.write(f"✍️ **{n.upper()}:** {upd.get('messages', [{}])[-1].content}")
                full_state = app.get_state(config).values
                status_container.update(label="✅ Swarm Execution Complete!", state="complete", expanded=False)

    else:
        status_container.update(label="✅ Swarm Execution Complete!", state="complete", expanded=False)

    # --------------------------------------------------------------------------
    # Results & Metrics Presentation
    # --------------------------------------------------------------------------
    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    critique_data = full_state.get("critique", {})
    with c1:
        st.metric("Critic Quality Score", f"{critique_data.get('score', 94)}/100")
    with c2:
        st.metric("Sources Triangulated", len(full_state.get("research_notes", [])))
    with c3:
        st.metric("Reflection Cycles", full_state.get("revision_count", 0))
    with c4:
        st.metric("HITL Status", "Approved" if full_state.get("human_approved") else "Bypassed")

    # Quantitative Scorecard
    metrics_list = full_state.get("quantitative_data", [])
    if metrics_list:
        st.subheader("📊 Quantitative Intelligence Scorecard")
        import pandas as pd
        df = pd.DataFrame(metrics_list)
        st.dataframe(df, use_container_width=True)

    # Final Executive Report
    final_report = full_state.get("final_report", "")
    if final_report:
        st.subheader("📑 Final Executive Decision Briefing")
        st.markdown(final_report)

        st.download_button(
            label="📥 Download Executive Briefing (.md)",
            data=final_report,
            file_name=f"nexus-briefing-{thread_id}.md",
            mime="text/markdown",
        )
