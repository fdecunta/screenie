#!/usr/bin/env python3

import click


@click.group()
def cli():
    """LLM-assisted systematic review screening tool"""
    pass

@cli.command()
@click.argument("input", type=click.File("rb"), nargs=1)
def init(input):
    """Init a screener in current directory"""
    click.echo(f"screenie initialized with {input.name}")

@cli.command()
@click.option("--model", type=str, prompt="Model name", help="LLM model to use")
def config(model):
    """Configure screener"""
    click.echo("foo")

if __name__ == "__main__":
    cli()
