"""Export LangGraph swarm topology to Mermaid and Markdown."""

import os

from langgraph_multi_agent_system.graph import create_graph


def export_graph_assets():
    app = create_graph()
    mermaid_code = app.get_graph().draw_mermaid()

    assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../docs/assets"))
    os.makedirs(assets_dir, exist_ok=True)

    mermaid_file = os.path.join(assets_dir, "architecture.mermaid")
    with open(mermaid_file, "w", encoding="utf-8") as f:
        f.write(mermaid_code)

    print(f"✓ Mermaid architecture diagram exported to: {mermaid_file}")
    print("\nMermaid Definition:\n")
    print(mermaid_code)


if __name__ == "__main__":
    export_graph_assets()
