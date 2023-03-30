import json
import subprocess
from os.path import exists as fexists
from os.path import join as pjoin

import click
import pandas as pd

from autofaq.cli.entry import entry
from autofaq.config.binder import bind
from autofaq.search.ddg_engine import DDGEngine
from autofaq.search.google_serp_search import SerpEngine
from autofaq.search.xng_engine import XNGEngine
from autofaq.util.out import sprint

engines = {"ddg": DDGEngine, "google": SerpEngine, "xng": XNGEngine}
langs = {"fa": None, "en": None}


@entry.command(help="Gathers search results for keywords")
@click.option(
    "-e",
    "--engine",
    default="ddg",
    help="Search Engine",
    type=click.Choice(engines.keys()),
)
def search(engine):
    sprint("Gathering search results for keywords ...", fg="cyan")
    query_list = pd.read_csv("keywords.csv")
    query_list = query_list[query_list["include"]]
    query_list = list(query_list["query"])

    engine = engines[engine]()
    ok = bind(engine, "settings.toml")
    if not ok:
        return

    results = engine.search(query_list)
    results.to_csv("search.csv", index=False)
    sprint("Successfully saved results to search.csv!", fg="green")
