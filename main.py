
import asyncio
import logging

from rich.console import Console
from rich.panel import Panel

from researchforge.config import (
    GROQ_MODEL,
    GROQ_MODEL2,
    GEMINI_MODEL,
    print_model_allocation,
    inspect_agent_models,
)
from researchforge.logging_config import configure_logging
from researchforge.workflow import run_research_workflow
from researchforge.utils.output import save_report

console = Console()


async def main():
    configure_logging()

    # Display configured model allocation before execution
    print_model_allocation()

    inspect_agent_models()

    console.print(
        Panel.fit(
            "[bold cyan]ResearchForge AI[/bold cyan]\n"
            f"Research Groq (Key 2): {GROQ_MODEL2}\n"
            f"Analysis Groq (Key 1): {GROQ_MODEL}\n"
            f"Report Gemini: {GEMINI_MODEL}\n"
            f"Reviewer Gemini: {GEMINI_MODEL}"
        )
    )

    topic = input("\nEnter your research topic: ").strip()

    if not topic:
        console.print("[red]Please enter a non-empty topic.[/red]")
        return

    console.print(
        "[cyan]Running Research → Analysis → Report → Review...[/cyan]"
    )

    try:
        report = await run_research_workflow(topic)

        console.print("\n[bold green]Final reviewed report[/bold green]\n")
        console.print(report)

        path = save_report(topic, report)

        console.print(f"\n[green]Saved report to: {path}[/green]")

    except Exception as exc:
        console.print(f"\n[bold red]Workflow failed:[/bold red] {exc}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
