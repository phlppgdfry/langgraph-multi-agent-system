"""Rich Interactive Terminal CLI for the Multi-Agent System."""

import argparse
import uuid

from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

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
    console.print("[dim]LangChain Core v1.7+ | LangGraph v1.2+ | LangSmith Observability | Human-in-the-Loop[/dim]\n")


def run_pipeline(task: str, thread_id: str | None = None, human_approval: bool = False):
    load_dotenv()

    if not thread_id:
        thread_id = str(uuid.uuid4())[:8]

    config = {"configurable": {"thread_id": thread_id}}
    app = create_graph()

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
        "metadata": {"thread_id": thread_id}
    }

    console.print(Panel(f"[bold green]Starting Objective:[/bold green] {task}\n[dim]Thread ID: {thread_id} | Checkpoint: MemorySaver[/dim]", title="Task Initialized"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        step_task = progress.add_task("[yellow]Swarm executing...", total=None)

        final_state = None
        for output in app.stream(initial_state, config=config):
            for node_name, state_update in output.items():
                progress.update(step_task, description=f"[cyan]Agent active: [bold]{node_name}[/bold]")
                
                # Print agent message
                msgs = state_update.get("messages", [])
                if msgs:
                    last_msg = msgs[-1].content
                    color = "magenta" if node_name == "supervisor" else "blue" if node_name == "researcher" else "green" if node_name == "analyst" else "yellow" if node_name == "critic" else "cyan"
                    console.print(f"[{color}]● [{node_name.upper()}][/{color}] {last_msg}")

                final_state = state_update

    # Display quantitative table if available
    metrics = final_state.get("quantitative_data", []) if final_state else []
    if metrics:
        table = Table(title="📊 Quantitative Intelligence Scorecard", border_style="cyan")
        table.add_column("Benchmark / KPI", style="bold white")
        table.add_column("Observed Value", style="bold green")
        table.add_column("Category", style="dim")
        for m in metrics:
            table.add_row(m.get("metric", "-"), m.get("value", "-"), m.get("type", "-"))
        console.print("\n", table, "\n")

    # Display final report
    report = final_state.get("final_report") if final_state else None
    if report:
        console.print(Panel(Markdown(report), title="[bold green]Final Executive Briefing[/bold green]", border_style="green"))
    else:
        console.print("[red]Execution completed without generating final report.[/red]")


def main():
    print_banner()
    parser = argparse.ArgumentParser(description="Run Nexus LangGraph Multi-Agent Swarm")
    parser.add_argument("task", nargs="?", default="Analyze LangChain & LangGraph enterprise multi-agent adoption in 2026", help="Strategic research question or task")
    parser.add_argument("--thread-id", type=str, default=None, help="LangGraph checkpoint thread ID")
    parser.add_argument("--human-approval", action="store_true", help="Enable human-in-the-loop gate before report publication")

    args = parser.parse_args()
    run_pipeline(args.task, args.thread_id, args.human_approval)


if __name__ == "__main__":
    main()
