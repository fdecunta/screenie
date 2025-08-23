#!/usr/bin/env python3
"""
LLM-assisted systematic review screening tool

A command-line interface for managing research study screening databases.
"""

import os
from pathlib import Path
import platform
import subprocess
import sys

import click

import screenie.config as config
import screenie.db as db
import screenie.llm as llm
import screenie.reader as reader
from screenie.screenie_printer import print_project_dashboard, print_studies_table


# Helper functions
def validate_db_file(ctx, param, value):
    """Validate that the database file has .db extension."""
    if not value.lower().endswith(".db"):
        raise click.BadParameter("File must have .db extension")
    return value


# CLI group definition
@click.group()
def cli():
    """LLM-assisted systematic review screening tool"""
    pass


# Commands
@cli.command(name="init")
@click.argument("name")
def init(name):
    """Initialize a screener database."""
    db_name = Path(name + ".db")

    if db_name.exists():
        click.secho(f"Error: database {db_name} already exists.", err=True, fg="red")
        sys.exit(1)
    
    try:
        db.init_db(db_name)
    except Exception as e:
        click.secho(f"Error: failed to initialize database '{db_name}': {e}", err=True, fg="red")
        sys.exit(1)
    else:
        click.secho(f"Initialized {db_name}", fg="green")



@cli.command(name="config")
def config_edit():
    """Open config file in default text editor."""
    config_file = config.get_config_file()
    
    try:
        click.edit(filename=str(config_file))
    except Exception as e:
        click.secho(f"Failed to open editor: {e}", fg="red")


@cli.command(name="import")
@click.option(
   "--from",
   "input_file",
   type=click.Path(exists=True, file_okay=True, dir_okay=False),
   required=True,
   help="Bibliography file to import from"
)
@click.option(
   "--to",
   "database",
   type=click.Path(file_okay=True, dir_okay=False),
   callback=validate_db_file,
   required=True,
   help="Database file to import to"
)
def import_file(input_file, database):
    """Import studies from bibliography file to database."""
    try:
        studies_list, errors = reader.import_studies(input_file=input_file)
    except ValueError as e:
        click.secho(f"Error: {e}", err=True, fg="red")
    else:
        click.echo(f"Total entries: {len(studies_list) + len(errors)}")
        click.secho(f"Valid studies: {len(studies_list)}", fg="green")
        click.secho(f"Invalid studies: {len(errors)}", fg="red")
    
        # TODO: Better open the connection with the DB here and close only if all goes ok
    
        file_id = db.insert_file(db_path=database, input_file=input_file)
        imported_count = db.insert_studies(db_path=database, file_id=file_id, studies_list=studies_list)
        
        click.secho(f"Done!")



@cli.command(name="criteria")
@click.argument(
    "database",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    callback=validate_db_file,
)
def edit_inclusion_criteria(database: str) -> None:
    """
    Open an editor for defining or updating inclusion criteria.

    Existing criteria are preloaded if available. Lines starting with
    '#' are ignored and serve only as instructions or examples.
    """
    INSTRUCTIONS = """\
# Lines starting with '#' are ignored.
# Write your inclusion criteria below.
# Example:
# 1. The study includes experimental data on LLMs for ecology.
# 2. The study compares LLMs with human performance.
"""

    last_text = db.read_last_criteria(db_path=database)
    buffer = f"{INSTRUCTIONS}\n{last_text or ''}"

    new_text = click.edit(buffer)
    if new_text is None:
        click.echo("No changes made.")
        return

    # Strip instruction lines
    criteria = "\n".join(
        line for line in new_text.splitlines() if not line.strip().startswith("#")
    ).strip()

    if not criteria:
        click.echo("No criteria provided.")
        return

    saved_criteria = db.save_criteria(db_path=database, text=criteria)
    if saved_criteria is None:
        click.echo("The same criteria already exists. No changes made.")
        return

    click.secho("Criteria saved successfully.", fg="green")


@cli.command(name="screen")
@click.argument(
    "database",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    callback=validate_db_file,
)
@click.option("--batch-size", default=1, type=click.IntRange(min=1))
def screen_studies(database, batch_size):
    """Screen studies using LLM assistance."""

    studies_ids = db.fetch_pending_studies_ids(database, batch_size)

    if len(studies_ids) == 0:
        click.echo("All studies have been screened. No pending studies found.")
        return

    if len(studies_ids) < batch_size:
        click.echo(f"Note: Only {len(studies_ids)} studies pending (requested {batch_size})")

    for study_id in studies_ids:
        llm.get_suggestion(database, study_id)


@cli.command(name="status")
@click.argument(
    "database",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    callback=validate_db_file,
)
def show_status(database):
    """Show project overview and statistics."""
    print_project_dashboard(database)


@cli.command(name="list")
@click.argument(
    "database", 
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    callback=validate_db_file,
)
@click.option("--limit", default=20, help="Number of studies to show")
def list_studies(database, limit):
    """List studies in table format."""
    print_studies_table(database, limit)



@cli.command(name="export")
@click.argument("db_path", type=click.Path(exists=True))
@click.option(
    "--format", "-f",
    "output_format",
    type=click.Choice(["csv", "xlsx", "excel"], case_sensitive=False),
    default="csv",
    show_default=True,
    help="Output format."
)
@click.option(
    "--output", "-o",
    "output_file",
    type=click.Path(writable=True),
    help="Path to save the exported file (extension will be added automatically)."
)
def export(db_path, output_format, output_file):
    """Export all studies and screening results"""
    if output_file is None:
        output_file = os.path.splitext(os.path.basename(db_path))[0]

    ext = ".csv" if output_format.lower() == "csv" else ".xlsx"
    if not output_file.lower().endswith(ext):
        output_file += ext

    # TODO: Ask to overwrite if file exists

    db.export_screening_results(db_path, output_format, output_file)
    click.echo(f"Exported results to {output_file} ({output_format})")


# Entry point
if __name__ == "__main__":
    cli()
