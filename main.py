#!/usr/bin/env python3

import click
import os
import platform
import subprocess
import sys

import config
import db
import reader


@click.group()
def cli():
    """LLM-assisted systematic review screening tool"""
    pass


@cli.command(name="init")
@click.argument("name")
def init(name):
    """Init a screener database in current directory"""
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


def validate_db_file(ctx, param, value):
    if not value.lower().endswith(".db"):
        raise click.BadParameter("File must have .db")
    return value

@cli.command(name="import")
@click.argument(
    "database",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    callback=validate_db_file
)
@click.argument(
        'input',
        type=click.File('rb')
)
def import_file(database, input):
    """Import papers from bib to database"""
    reader.import_from_bib(db_path=database, file_path=input.name)


@cli.command(name="config-edit")
def config_edit():
    """Open config file in default text editor"""
    config_dir = config.get_config_dir()
    config_file = config_dir / "config.yaml"

    try:
        click.edit(filename=str(config_file))
    except Exception as e:
        click.secho(f"Failed to open editor: {e}", fg="red")


@cli.command(name="config-help")
def config_help():
    """Show how to configure LLM providers using LiteLLM format"""

    config_dir = config.get_config_dir()
    click.echo("To configure LLM providers, create a config file:")
    click.echo(f"  {config_dir / 'config.yaml'}")
    click.echo("\nExample content:")
    click.echo('''model_list:
  - model_name: "openai-gpt-4"
    litellm_params:
      model: "gpt-4"
      api_key: "sk-your-key-here"

  - model_name: "anthropic-claude"
    litellm_params:
      model: "claude-3-sonnet"
      api_key: "your-anthropic-key"

  - model_name: "ollama-llama3"
    litellm_params:
      model: "ollama/llama3"
      api_base: "http://localhost:11434"''')



if __name__ == "__main__":
    cli()
