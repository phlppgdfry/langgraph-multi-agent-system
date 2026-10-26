"""Rich Interactive Terminal CLI for the Nexus LangGraph Multi-Agent Swarm."""

import argparse
import os
import uuid

from dotenv import load_dotenv, set_key
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich.table import Table

from langgraph_multi_agent_system.checkpoint import list_saved_threads
from langgraph_multi_agent_system.graph import create_graph

console = Console()


def print_banner():
    banner_text = """[bold cyan]
 _   _                     _                                  
| \\ | |                   | |                                 
|  \\| | _____  ___   _ ___| |     __ _ _ __   __ _ _ __ __ _  
| . ` |/ _ \\ \\/ / | | / __| |    / _` | '_ \\ / _` | '__/ _` | 
| |\\  |  __/>  <| |_| \\__ \\ |___| (_| | | | | (_| | | | (_| | 
|_| \\_|\\___/_/\\_\\\\__,_|___/\\_____/\\__,_|_| |_|\\__, |_|  \\__,_| 
                                               __/ |          
   Autonomous Multi-Agent Intelligence Engine |___/ (LangGraph)
[/bold cyan]"""
    console.print(banner_text)
    console.print(
        "[dim]LangChain Core v1.7+ | LangGraph v1.2+ | LangSmith Observability | Human-in-the-Loop[/dim]\n"
    )


def interactive_configure():
    """Interactive wizard to configure LangSmith and LLM keys in .env."""
    print_banner()
    console.print(Panel("[bold green]Nexus Swarm Configuration Wizard[/bold green]\nConfigure your LangSmith and LLM API keys.", border_style="cyan"))

    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.env"))
    if not os.path.exists(env_path):
        with open(env_path, "w", encoding="utf-8") as f:
            f.write("# Nexus Multi-Agent Configuration\n")

    current_smith_key = os.getenv("LANGCHAIN_API_KEY", "")
    smith_prompt = "LangSmith API Key (starts with lsv2_pt_)"
    smith_key = Prompt.ask(smith_prompt, default=current_smith_key or None, password=True)
    if smith_key:
        endpoint = "https://eu.api.smith.langchain.com"
        try:
            from langsmith import Client
            c = Client(api_url="https://api.smith.langchain.com", api_key=smith_key.strip())
            c.list_projects(limit=1)
            endpoint = "https://api.smith.langchain.com"
        except Exception:  # noqa: BLE001
            pass

        set_key(env_path, "LANGCHAIN_TRACING_V2", "true")
        set_key(env_path, "LANGCHAIN_ENDPOINT", endpoint)
        set_key(env_path, "LANGCHAIN_API_KEY", smith_key.strip())
        set_key(env_path, "LANGCHAIN_PROJECT", os.getenv("LANGCHAIN_PROJECT", "nexus-multi-agent-system"))
        console.print(f"[green]✓ LangSmith tracing credentials saved to .env (Endpoint: {endpoint})[/green]")

    current_openai = os.getenv("OPENAI_API_KEY", "")
    openai_key = Prompt.ask("OpenAI API Key (optional, leave blank for offline demo mode)", default=current_openai or None, password=True)
    if openai_key:
        set_key(env_path, "OPENAI_API_KEY", openai_key.strip())
        console.print("[green]✓ OpenAI API key saved to .env[/green]")

    console.print(Panel(f"[bold green]Configuration successfully updated![/bold green]\nSaved in: {env_path}", border_style="green"))


def run_pipeline(
    task: str,
    thread_id: str | None = None,
    human_approval: bool = False,
    provider: str | None = None,
    output_file: str | None = None,
):
    load_dotenv()

    if provider:
        os.environ["DEFAULT_MODEL_PROVIDER"] = provider

    if not thread_id:
        thread_id = str(uuid.uuid4())[:8]

    config = {"configurable": {"thread_id": thread_id}}
    app = create_graph(interrupt_on_human_gate=human_approval)

    initial_state = {
        "task": task,
        "messages": [],
        "plan": [],
        "current_step": 0,
        "research_notes": [],
        "quantitative_data": [],
        "critique": {},
        "revision_count": 0,
        "max_revisions": 2,
        "next_agent": "",
        "requires_human_approval": human_approval,
        "human_approved": None,
        "final_report": None,
        "metadata": {"thread_id": thread_id, "provider": provider or "default"},
    }

    console.print(
        Panel(
            f"[bold green]Objective:[/bold green] {task}\n"
            f"[dim]Thread: {thread_id} | Checkpoint: SQLite | LangSmith Tracing: {os.getenv('LANGCHAIN_TRACING_V2', 'false')}[/dim]",
            title="Swarm Initialized",
            border_style="cyan",
        )
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        step_task = progress.add_task("[yellow]Swarm executing...", total=None)

        for output in app.stream(initial_state, config=config):
            for node_name, state_update in output.items():
                progress.update(
                    step_task,
                    description=f"[cyan]Agent active: [bold]{node_name}[/bold]",
                )

                msgs = state_update.get("messages", [])
                if msgs:
                    last_msg = msgs[-1].content
                    color = (
                        "magenta"
                        if node_name == "supervisor"
                        else "blue"
                        if node_name == "researcher"
                        else "green"
                        if node_name == "analyst"
                        else "yellow"
                        if node_name == "critic"
                        else "cyan"
                    )
                    console.print(f"[{color}]● [{node_name.upper()}][/{color}] {last_msg}")

    # Read complete cumulative checkpoint state
    full_state = app.get_state(config).values

    # Check if human approval is pending
    if human_approval and full_state.get("next_agent") == "human_gate":
        console.print(Panel("[bold yellow]Human-in-the-Loop Gate Triggered[/bold yellow]\nReview agent findings and approve final report synthesis.", border_style="yellow"))
        approved = Prompt.ask("Approve executive report generation? (y/n)", choices=["y", "n"], default="y") == "y"
        
        # Resume graph execution with operator decision
        app.update_state(config, {"human_approved": approved, "next_agent": "writer" if approved else "researcher"})
        for output in app.stream(None, config=config):
            for node_name, state_update in output.items():
                msgs = state_update.get("messages", [])
                if msgs:
                    console.print(f"[cyan]● [{node_name.upper()}][/cyan] {msgs[-1].content}")
        full_state = app.get_state(config).values

    # Display quantitative table
    metrics = full_state.get("quantitative_data", [])
    if metrics:
        table = Table(title="📊 Quantitative Intelligence Scorecard", border_style="cyan")
        table.add_column("Indicator / Benchmark", style="bold white")
        table.add_column("Observed Value", style="bold green")
        table.add_column("Category", style="dim")
        for m in metrics:
            table.add_row(m.get("metric", "-"), m.get("value", "-"), m.get("type", "-"))
        console.print("\n", table, "\n")

    # Display final report
    report = full_state.get("final_report")
    if report:
        console.print(
            Panel(
                Markdown(report),
                title="[bold green]Final Executive Briefing[/bold green]",
                border_style="green",
            )
        )
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report)
            console.print(f"[green]✓ Report saved to: {output_file}[/green]")
    else:
        console.print("[red]Execution completed without generating final report.[/red]")


def main():
    parser = argparse.ArgumentParser(description="Run Nexus LangGraph Multi-Agent Swarm")
    parser.add_argument(
        "task",
        nargs="?",
        default="Analyze LangChain & LangGraph enterprise multi-agent adoption in 2026",
        help="Strategic research question or task",
    )
    parser.add_argument("--thread-id", type=str, default=None, help="LangGraph checkpoint thread ID")
    parser.add_argument("--human-approval", action="store_true", help="Enable human-in-the-loop gate")
    parser.add_argument("--provider", type=str, choices=["openai", "anthropic", "google", "mock"], help="LLM model provider")
    parser.add_argument("--output", "-o", type=str, help="Save final markdown report to file")
    parser.add_argument("--configure", action="store_true", help="Launch interactive configuration wizard for LangSmith and API keys")
    parser.add_argument("--list-threads", action="store_true", help="List saved checkpoint thread sessions from SQLite store")
    parser.add_argument("--evals", action="store_true", help="Run automated LangSmith benchmark evaluation suite")

    args = parser.parse_args()

    if args.configure:
        interactive_configure()
        return

    if args.list_threads:
        threads = list_saved_threads()
        if not threads:
            console.print("[yellow]No saved checkpoint threads found in SQLite database.[/yellow]")
        else:
            table = Table(title="📜 Saved LangGraph Checkpoint Threads", border_style="cyan")
            table.add_column("Thread ID", style="bold green")
            table.add_column("Namespace", style="dim")
            for t in threads:
                table.add_row(t["thread_id"], t["namespace"])
            console.print(table)
        return

    if args.evals:
        from langgraph_multi_agent_system.evals.run_evals import run_benchmark_evals
        run_benchmark_evals()
        return

    print_banner()
    run_pipeline(args.task, args.thread_id, args.human_approval, args.provider, args.output)


if __name__ == "__main__":
    main()
