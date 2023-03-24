import subprocess
from os.path import join as pjoin

import click

from autofaq.cli.entry import entry
from autofaq.cli.commands.util import create_directories_and_settings


@entry.command(help="Initiates a new mining project")
@click.option("-p", "--path", default=".", help="base path")
@click.option("-f", "--force", default=False, is_flag=True, help="overwrite project if exists")
@click.argument("name")
def init(name, path, force):
    click.echo("Initializing new mining project ...")

    structure = {
        ".cache": None,
    }

    settings = {
        "name": name,
        "search_engine": "duck-duck-go"
    }

    ok = create_directories_and_settings(structure, settings, pjoin(path, name), force)
    if ok:
        click.echo(click.style("Successfully created project!", fg="green"))
    else:
        click.echo(
            click.style("Error creating project!", fg="red"),
        )
