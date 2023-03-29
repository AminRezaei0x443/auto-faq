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
from autofaq.clean.fuzzy_match import FuzzCleaner
from autofaq.clean.page import PageCleaner
from autofaq.clean.subject import SubjectCleaner
from autofaq.cli.entry import entry
from autofaq.util.out import sprint

cleaners = {
    "classic": ClassicCleaner,
    "entailment": EntailmentCleaner,
    "subject": SubjectCleaner,
    "fuzz": FuzzCleaner,
    "page": PageCleaner,
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
        sprint("You must provide a filter name when in not inplace mode!", fg="red")
        return
    filter_p = f"{name}.filter"
    filter_a = f"{name}.aux"
    filter_i = {}
    if fexists(filter_p) and not scratch:
        with open(filter_p, "rb") as f:
            filter_i = pickle.load(f)
        selection = df.apply(lambda x: filter_i[x["id"]], axis=1)
        df = df[selection]

    aux = pd.DataFrame()
    aux["id"] = df["id"]
    if fexists(filter_a) and not scratch:
        aux = pd.read_pickle(filter_a)

    cleaner = cleaners[cleaner]()
    selection = cleaner.clean(df, aux=aux)
    sprint(
        "Survivors: @s @sep @all",
        fg="white",
        s=(selection.sum(), "green", "bold"),
        all=(len(selection), "black"),
        sep=("/", "black"),
    )
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
