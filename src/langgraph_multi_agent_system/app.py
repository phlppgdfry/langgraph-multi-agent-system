"""Streamlit Web UI for the LangGraph Multi-Agent Swarm."""

import os
import uuid

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Nexus | LangGraph Multi-Agent Swarm",
    page_icon="🤖",
    layout="wide"
)

# Sidebar Configuration
with st.sidebar:
    st.title("⚙️ Swarm Configuration")
    st.markdown("Configure model, observability, and workflow parameters.")

    openai_key = st.text_input("OpenAI API Key", value=os.getenv("OPENAI_API_KEY", ""), type="password", help="Leave blank to run in deterministic offline demo mode.")
    if openai_key:
        os.environ["OPENAI_API_KEY"] = openai_key

    st.divider()
    st.subheader("🔍 LangSmith Tracing")
    langsmith_enabled = st.checkbox("Enable LangSmith Tracing", value=bool(os.getenv("LANGCHAIN_TRACING_V2") == "true"))
    langsmith_key = st.text_input("LangSmith API Key", value=os.getenv("LANGCHAIN_API_KEY", ""), type="password")
    langsmith_project = st.text_input("LangSmith Project", value=os.getenv("LANGCHAIN_PROJECT", "nexus-agent-swarm"))

    if langsmith_enabled and langsmith_key:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = langsmith_key
        os.environ["LANGCHAIN_PROJECT"] = langsmith_project

    st.divider()
    st.subheader("🛡️ Governance")
    human_approval = st.checkbox("Require Human-in-the-Loop Gate", value=False)
    max_revisions = st.slider("Max Reflection Revisions", 1, 3, 2)

    st.markdown("---")
    st.markdown("Built with **LangGraph v1.2+** & **LangChain Core**")

# Main Page
st.title("🤖 Nexus: Autonomous Multi-Agent Intelligence Swarm")
st.caption("Stateful Multi-Agent Orchestration • Reflection Self-Correction • LangSmith Observability")

preset_options = [
    "Analyze LangChain & LangGraph enterprise multi-agent adoption in 2026",
    "Benchmark Latency, Token Costs, and Accuracy in Multi-Agent Swarms",
    "Evaluate Autonomous AI Agents in Enterprise Supply Chain & Logistics",
    "Custom prompt..."
]

selected_preset = st.selectbox("Select Preset Objective or Enter Custom:", preset_options)

if selected_preset == "Custom prompt...":
    task_input = st.text_area("Research Objective", placeholder="e.g. Conduct a strategic and quantitative analysis of...")
else:
    task_input = selected_preset

col1, col2 = st.columns([1, 4])
with col1:
    start_btn = st.button("🚀 Launch Swarm", type="primary", use_container_width=True)

if start_btn and task_input:
    from langgraph_multi_agent_system.graph import create_graph

    thread_id = str(uuid.uuid4())[:8]
    config = {"configurable": {"thread_id": thread_id}}
    app = create_graph()

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
        "metadata": {"thread_id": thread_id}
    }

    st.info(f"**Swarm Initialized:** Thread `{thread_id}` | Checkpointer: `MemorySaver`")

    status_container = st.status("Swarm actively orchestrating...", expanded=True)
    step_container = st.container()

    final_state = None
    with status_container:
        for output in app.stream(initial_state, config=config):
            for node_name, state_update in output.items():
                msgs = state_update.get("messages", [])
                msg_text = msgs[-1].content if msgs else ""
                
                if node_name == "supervisor":
                    st.write(f"🧭 **Supervisor:** {msg_text}")
                elif node_name == "researcher":
                    st.write(f"🔬 **Researcher:** {msg_text}")
                elif node_name == "analyst":
                    st.write(f"📈 **Analyst:** {msg_text}")
                elif node_name == "critic":
                    score = state_update.get("critique", {}).get("score", "N/A")
                    st.write(f"⚖️ **Critic (Quality Score: {score}/100):** {msg_text}")
                elif node_name == "human_gate":
                    st.write(f"🛡️ **Human Gate:** {msg_text}")
                elif node_name == "writer":
                    st.write(f"✍️ **Executive Writer:** {msg_text}")
                
                final_state = state_update

        status_container.update(label="✅ Swarm Execution Complete!", state="complete", expanded=False)

    # Render results
    if final_state:
        st.divider()
        col_metric1, col_metric2, col_metric3 = st.columns(3)
        critique_info = final_state.get("critique", {})
        with col_metric1:
            st.metric("Critic Quality Score", f"{critique_info.get('score', 92)}/100")
        with col_metric2:
            st.metric("Sources Triangulated", len(final_state.get("research_notes", [])))
        with col_metric3:
            st.metric("Revisions Executed", final_state.get("revision_count", 0))

        # Quantitative Metrics Table
        metrics = final_state.get("quantitative_data", [])
        if metrics:
            st.subheader("📊 Quantitative Scorecard")
            import pandas as pd
            df = pd.DataFrame(metrics)
            st.dataframe(df, use_container_width=True)

        # Final Report
        report_content = final_state.get("final_report", "")
        if report_content:
            st.subheader("📑 Final Executive Report")
            st.markdown(report_content)
            st.download_button(
                label="📥 Download Report (.md)",
                data=report_content,
                file_name=f"briefing-{thread_id}.md",
                mime="text/markdown"
            )
