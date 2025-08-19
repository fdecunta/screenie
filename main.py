#!/usr/bin/env python3

import click
import sys

import db
from reader import (
        import_from_bib
)


@click.group()
def cli():
    """LLM-assisted systematic review screening tool"""
    pass


@cli.command()
@click.argument("name")
def init(name):
    """Init a screener in current directory"""
    db_name = name + ".db"
    if db.init_db(db_name):
        click.echo(f"screenie initialized {db_name}")
    else:
        click.echo(f"Error: failed to initialize database '{db_name}'", err=True)
        sys.exit(1)



@cli.command()
@click.option("--model", type=str, prompt="Model name", help="LLM model to use")
def config(model):
    """Configure screener"""
    click.echo("foo")


if __name__ == "__main__":
    cli()
