import json
import pickle
import subprocess
from hashlib import sha256
from os.path import exists as fexists
from os.path import join as pjoin

import click
import numpy as np
import pandas as pd
import requests
from tqdm import tqdm
from user_agent import generate_user_agent

from autofaq.clean.classic import ClassicCleaner
from autofaq.clean.entailment import EntailmentCleaner
from autofaq.cli.entry import entry

cleaners = {
    "classic": ClassicCleaner,
    "entailment": EntailmentCleaner,
}


@entry.command(help="Cleans the dataset")
@click.option(
    "-c",
    "--cleaner",
    default="classic",
    help="cleaner module",
    type=click.Choice(list(cleaners.keys())),
)
@click.option(
    "-s", "--scratch", default=False, is_flag=True, help="use existing filter"
)
@click.option(
    "-i", "--inplace", default=False, is_flag=True, help="use existing filter"
)
@click.argument("name", required=False)
def clean(name, cleaner, scratch, inplace):
    df = pd.read_csv("dataset.csv")
    if name is None and not inplace:
        click.echo(
            click.style(
                "You must provide a filter name when in not inplace mode!", fg="red"
            )
        )
        return
    filter_p = f"{name}.filter"
    filter_i = {}
    if fexists(filter_p) and not scratch:
        with open(filter_p, "rb") as f:
            filter_i = pickle.load(f)
        selection = df.apply(lambda x: filter_i[x["id"]], axis=1)
        df = df[selection]

    cleaner = cleaners[cleaner]()
    aux = pd.DataFrame()
    aux["id"] = df["id"]
    selection = cleaner.clean(df, aux=aux)
    print(f"Remnants: {selection.sum()}/{len(selection)}")
    if inplace:
        df[selection].to_csv("dataset.csv", index=False)
    else:
        filter_ = pd.DataFrame()
        filter_["id"] = df["id"]
        filter_["selected"] = selection
        filter_d = {x["id"]: x["selected"] for _, x in filter_.iterrows()}
        filter_d = {**filter_i, **filter_d}
        aux.to_pickle(f"{name}.aux")
        with open(filter_p, "wb") as f:
            pickle.dump(filter_d, f)
