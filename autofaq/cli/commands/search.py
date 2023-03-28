import json
import subprocess
from os.path import exists as fexists
from os.path import join as pjoin

import click
import pandas as pd

from autofaq.cli.entry import entry
from autofaq.search.ddg_search import DDGSearch
from autofaq.search.google_serp_search import serp_search_all
from autofaq.search.xng_search import xng_search_all
from autofaq.util.out import sprint

engines = ["ddg", "google", "xng"]
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
    "-n",
    "--results_num",
    default=10,
    help="result count for each search query (just for google currently)",
)
@click.option(
    "-l",
    "--language",
    default="fa",
    help="target language",
    type=click.Choice(list(langs.keys())),
)
def search(engine, results_num, language):
    sprint("Gathering search results for keywords ...", fg="cyan")
    query_list = pd.read_csv("keywords.csv")
    query_list = query_list[query_list["include"]]
    query_list = list(query_list["query"])
    if engine == "ddg":
        engine = DDGSearch()
        for q in query_list:
            engine.queue_search(q)
        results = engine.retreive()
    elif engine == "google":
        results = serp_search_all(query_list, num=results_num)
    elif engine == "xng":
        results = xng_search_all(query_list)
    results.to_csv("search.csv", index=False)
    sprint("Successfully saved results to search.csv!", fg="green")
