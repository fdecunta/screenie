#!/usr/bin/env python3

import click
import os
import sys

import db
from reader import (
        import_from_bib
)


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
    import_from_bib(db_path=database, file_path=input.name)



@cli.command()
@click.option("--model", type=str, prompt="Model name", help="LLM model to use")
def config(model):
    """Configure screener"""
    click.echo("foo")


if __name__ == "__main__":
    cli()
