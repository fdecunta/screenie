from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.padding import Padding
from rich.table import Table
from rich.layout import Layout
from rich.live import Live
import sqlite3

console = Console()


def print_project_dashboard(db_path: str):
    """Display project overview dashboard"""
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        
        # Get statistics
        total_studies = cur.execute("SELECT COUNT(*) FROM studies").fetchone()[0]
        screened_studies = cur.execute("SELECT COUNT(*) FROM screening_results").fetchone()[0]
        included_studies = cur.execute("SELECT COUNT(*) FROM screening_results WHERE verdict = 1").fetchone()[0]
        excluded_studies = cur.execute("SELECT COUNT(*) FROM screening_results WHERE verdict = 0").fetchone()[0]
        
        # Create dashboard table
        table = Table(title="Project Overview", show_header=False, box=None)
        table.add_column("Metric")
        table.add_column("Value")
        
        table.add_row("Total Studies", str(total_studies))
        table.add_row("Screened", f"{screened_studies} ({screened_studies/total_studies*100:.1f}%)" if total_studies > 0 else "0")
        table.add_row("Included", f"[green]{included_studies}[/green]")
        table.add_row("Excluded", f"[red]{excluded_studies}[/red]")
        table.add_row("Remaining", f"[yellow]{total_studies - screened_studies}[/yellow]")
        
        console.print(table)


def print_studies_table(db_path: str, limit: int = 10):
    """Display studies in a table format"""
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()

        # Get studies with screening status
        query = """
        SELECT s.study_id, s.title, s.authors, s.year,
               sr.verdict, sr.human_validated
        FROM studies s
        LEFT JOIN screening_results sr ON s.study_id = sr.study_id
        ORDER BY s.study_id
        LIMIT ?
        """

        results = cur.execute(query, (limit,)).fetchall()

        # Create table
        table = Table()
        table.add_column("ID", style="dim")
        table.add_column("Title", max_width=40)
        table.add_column("Authors", max_width=20)
        table.add_column("Year")
        table.add_column("LLM", justify="center")
        table.add_column("Status", justify="center")

        for row in results:
            study_id, title, authors, year, verdict, validated = row

            # Truncate long titles
            display_title = title[:37] + "..." if len(title) > 40 else title
            display_authors = authors[:17] + "..." if len(authors) > 20 else authors

            # Format LLM verdict
            if verdict is None:
                llm_status = "[dim]—[/dim]"
                status = "[yellow]Pending[/yellow]"
            elif verdict == 1:
                llm_status = "[green]✓[/green]"
                status = "[green]Include[/green]" if validated else "[yellow]Review[/yellow]"
            else:
                llm_status = "[red]✗[/red]"
                status = "[red]Exclude[/red]" if validated else "[yellow]Review[/yellow]"

            table.add_row(
                str(study_id),
                display_title,
                display_authors,
                str(year),
                llm_status,
                status
            )

        console.print(table)


def print_study(title, authors, abstract):
    title_text = Text(title, style="bold underline")
    authors_text = Text(authors, style="italic")
    abstract_text = Text(abstract)
    content = Padding(Text.assemble(authors_text, "\n\n", abstract_text), (1, 4))
    panel = Panel(content, title=title_text, expand=False)
    console.print(panel)


def print_llm_suggestion(verdict: str, reason: str):
    """
    Prints the LLM verdict and reasoning in a panel with a simple 'Verdict/Reason' format.
    """
    # Combine verdict and reason in the panel content
    if verdict == "1":
        verdict_msg = "Relevant"
        verdict_color = "bold green"
    else:
        verdict_msg = "Not relevant"
        verdict_color= "bold red"

    content = Text.assemble(
        ("Verdict: ", "bold"),
        (f"{verdict_msg}\n", verdict_color),
        ("Reason: ", "bold"),
        (reason, "")
    )
    
    padded_content = Padding(content, (1, 2))
    panel = Panel(padded_content, expand=False)
    console.print(panel)

