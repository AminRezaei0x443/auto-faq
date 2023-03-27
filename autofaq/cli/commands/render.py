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
import torch
from tqdm import tqdm
from user_agent import generate_user_agent

from autofaq.cli.entry import entry
from autofaq.language_model.xlm import embedSentences, openXLMSession


@entry.command(help="Renders the dataset as human-readable formats")
@click.argument("filter_name", required=False)
def render(filter_name):
    df = pd.read_csv("dataset.csv")

    filter_p = f"{filter_name}.filter"
    with open(filter_p, "rb") as f:
        filter_i = pickle.load(f)
    selection = df.apply(lambda x: filter_i[x["id"]], axis=1)
    df = df[selection]
    df = df.reset_index(drop=True)

    # df -> src_title, src_link, q, a
    pages = {row.src_link: row.src_title for _, row in df.iterrows()}
    grouped = {
        link: list(df[df.src_link == link].apply(lambda x: (x.q, x.a), axis=1))
        for link in pages
    }

    document = []
    for group, pairs in grouped.items():
        title = pages[group]
        document.append(f"### {title}")
        for q, a in pairs:
            document.append(f"#### {q}")
            document.append(a)

    doc = "\n".join(document)
    with open("out.md", "w") as f:
        f.write(doc)