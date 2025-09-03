#!/usr/bin/env python3
"""
LLM-assisted systematic review screening tool

A command-line interface for managing research study screening databases.
"""

import os
from pathlib import Path
import platform
import sqlite3
import subprocess
import sys

import click

import screenie.config as config
from screenie.db import Database
import screenie.llm as llm
import screenie.studies as studies
import screenie.recipes as recipes


# Helper functions
def validate_db_file(ctx, param, value):
    """Validate that the database file has .db extension."""
    if not value.lower().endswith(".db"):
        raise click.BadParameter("File must have .db extension")
    return value


def validate_toml_file(ctx, param, value):
    """Validate that the database file has .db extension."""
    if not value.lower().endswith(".toml"):
        raise click.BadParameter("File must have .db extension")
    return value


def _read_recipe(recipe):
    try:
        run_recipe = recipes.read_recipe(recipe)
    except KeyError as keyerr:
        click.secho(f"Error in the definition of recipe: {recipe}", err=True, fg="red")
        click.echo(f"Missing field: {keyerr}")
        sys.exit(1)

    return run_recipe


def _register_recipe(project_db, recipe, run_recipe):
    file_id = project_db.fetch_file_id(recipe)
    recipe_id = project_db.fetch_recipe_id(run_recipe)

    if not file_id and project_db.is_filename_used(recipe):
        click.secho(
            "Error: A recipe with the same filename already exists in the database, "
            "but its contents are different. Please use a unique filename or update the existing recipe.",
            err=True,
            fg="red"
        )
        sys.exit(1)
    elif not file_id:
        file_id = project_db.save_file(recipe)
        recipe_id = project_db.save_recipe(run_recipe, file_id)

    return file_id, recipe_id


def _set_env_model_keys(run_recipe):
    # TODO: This may fail because the user put a wrong model name or something else. Check using litellm.models_list()
    try:
        config.load_model_keys(run_recipe.model.model)
    except ValueError as e:
        click.secho(e, err=True, fg="red")
        click.echo("Edit configuration running: \n\tscreenie config")
        sys.exit(1)



def _fetch_pending_studies(project_db, recipe_id, limit):
    studies_ids = project_db.fetch_pending_studies_ids(recipe_id, limit)

    if len(studies_ids) == 0:
        click.echo("All studies have been screened. No pending studies found.")
        sys.exit(0)

    if len(studies_ids) < limit:
        click.echo(f"Note: Only {len(studies_ids)} studies pending (requested {limit})")

    return studies_ids


def _screen_study(project_db, run_recipe, recipe_id, study_id):
    study = project_db.fetch_study(study_id)

    # TODO: Add option to retry a few times or just skip. This can be at this stage or during parsing, which is prone to error
    try:
        response = llm.call_llm(run_recipe, study)
    except Exception as e:
        click.echo(f"Error calling llm: {e}", err=True)
        sys.exit(1)

    llm_output = llm.parse_response(response)

    call_id = project_db.save_llm_call(
            response = response,
            recipe_id = recipe_id,
            study_id = study_id
    )
    suggestion_id = project_db.save_result(
            recipe_id = recipe_id,
            study_id = study_id,
            call_id = call_id,
            verdict = llm_output['verdict'],
            reason = llm_output['reason']
    )
    # Commit at this stage. If things worked, start saving results
    project_db.commit()

    # TODO: mejorar mensajes
    click.echo(f"Study: {study['title']}\n")
    click.echo(f"Verdict: {llm_output['verdict']}")
    click.echo(f"Reason: {llm_output['reason']}\n")



@click.group()
def cli():
    """LLM-assisted systematic review screening tool"""
    pass


@cli.command(name="init")
@click.argument("name")
def init(name):
    """Initialize a screener database."""
    db_name = Path(name + ".db")

    if db_name.exists():
        click.secho(f"Error: database {db_name} already exists.", err=True, fg="red")
        sys.exit(1)
    
    try:
        project_db = Database(db_name)
        project_db.init()
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
   type=click.Path(exists=True, file_okay=True, dir_okay=False),
   callback=validate_db_file,
   required=True,
   help="Database file to import to"
)
def import_file(input_file, database):
    """Import studies from bibliography file to database."""
    try:
        studies_list, errors = studies.import_studies(input_file=input_file)
    except ValueError as e:
        click.secho(f"Error: {e}", err=True, fg="red")
        return

    click.echo(f"Total entries: {len(studies_list) + len(errors)}")
    click.secho(f"Valid studies: {len(studies_list)}", fg="green")
    click.secho(f"Invalid studies: {len(errors)}", fg="red")

    if not studies_list:
        click.secho("No valid studies to import.", fg="yellow")
        return
    
    try:
        project_db = Database(database)
        file_id = project_db.save_file(input_file)
        imported_count = project_db.save_studies(file_id=file_id, studies_list=studies_list)
        project_db.commit()
        project_db.close()
    except Exception as e:
        click.secho(f"Database error: {e}", err=True, fg="red")
        sys.exit(1)
        
    click.secho(f"Done.")


@cli.command(name="run")
@click.argument(
    "recipe",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    required=True,
    callback=validate_toml_file
)
@click.argument(
    "database",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    required=True,
    callback=validate_db_file
)
@click.option(
        "--limit",
        "-l",
        default=1,
        type=click.IntRange(min=1),
        help="Maximum number of studies to process in this run." 
)
@click.option(
        "--dry-run",
        "-d",
        is_flag=True,
        help="Simulate the run without calling the LLM or saving results."
)
def screen_studies(recipe, database , limit, dry_run):
    """Screen studies using LLM assistance."""

    project_db = Database(database)

    # TODO implement dry-run
    if dry_run:
        print("haha dry run")
        sys.exit(1)

    # Read recipe from file. Then register it in the database.
    # If already exists, get its IDs
    run_recipe = _read_recipe(recipe)
    file_id, recipe_id = _register_recipe(project_db, recipe, run_recipe)

    # With model from recipe, set model keys as env variables
    _set_env_model_keys(run_recipe)        

    studies_ids = _fetch_pending_studies(project_db, recipe_id, limit)
    for study_id in studies_ids:
        _screen_study(project_db, run_recipe, recipe_id, study_id)

    # Close before end
    project_db.close()
    return


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

    db.export_results(db_path, output_format, output_file)
    click.echo(f"Exported results to {output_file} ({output_format})")


# TODO: commands to inspect the db


# Entry point
if __name__ == "__main__":
    cli()
