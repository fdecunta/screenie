#!/usr/bin/env python3
"""
LLM-assisted systematic review screening tool

A command-line interface for managing research paper screening databases.
"""

import os
import platform
import subprocess
import sys

import click

import config
import db
import reader


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
    """Initialize a screener database in current directory."""
    db_name = name + ".db"
    
    if os.path.exists(db_name):
        click.secho(f"Error: database {db_name} already exists.", err=True, fg="red")
        sys.exit(1)
    
    fmt_db_name = click.format_filename(db_name)
    
    if db.init_db(db_name):
        click.secho(f"Initialized {fmt_db_name}", fg="green")
    else:
        click.echo(f"Error: failed to initialize database '{fmt_db_name}'", err=True, fg="red")
        sys.exit(1)


@cli.command(name="import")
@click.argument(
    "database",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    callback=validate_db_file
)
@click.argument(
    "input",
    type=click.File("rb")
)
def import_file(database, input):
    """Import papers from bibliography file to database."""
    reader.import_from_bib(db_path=database, file_path=input.name)


@cli.command(name="criteria-edit")
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


@cli.command(name="criteria-show")
@click.argument(
    "database",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    callback=validate_db_file
)
def show_criteria(database):
    last_text = db.read_last_criteria(db_path=database)
    click.echo(last_text)


@cli.command(name="config-edit")
def config_edit():
    """Open config file in default text editor."""
    config_dir = config.get_config_dir()
    config_file = config_dir / "config.yaml"
    
    try:
        click.edit(filename=str(config_file))
    except Exception as e:
        click.secho(f"Failed to open editor: {e}", fg="red")


@cli.command(name="screen")
@click.argument(
    "database",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    callback=validate_db_file,
)
def screen_papers(database):
    import llm
    llm.get_suggestion(database, 1, 1)


# Entry point
if __name__ == "__main__":
    cli()
