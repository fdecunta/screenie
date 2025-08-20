from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.padding import Padding

console = Console()

def print_paper(title, authors, abstract):
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

