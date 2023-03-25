import json
import subprocess
from os.path import exists as fexists
from os.path import join as pjoin

import click
import pandas as pd

from autofaq.cli.entry import entry
from autofaq.search.ddg_search import DDGSearch

engines = ["ddg"]
langs = {"fa": None, "en": None}


@entry.command(help="Gathers search results for keywords")
@click.option(
    "-e",
    "--engine",
    default="ddg",
    help="engine for searching",
    type=click.Choice(engines),
)
@click.option(
    "-l",
    "--language",
    default="fa",
    help="target language",
    type=click.Choice(list(langs.keys())),
)
def search(engine, language):
    engine = DDGSearch()
    query_list = pd.read_csv("keywords.csv")
    for q in query_list["query"]:
        engine.queue_search(q)
    results = engine.retreive()
    results.to_csv("search.csv", index=False)
