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
from autofaq.util.out import sprint


@entry.command(help="Renders the dataset as human-readable formats")
@click.argument("filter_name", required=False)
def render(filter_name):
    sprint("Rendering QA pairs to markdown ...", fg="cyan")

    df = pd.read_csv("dataset.csv")
    aux = df[["id"]]

    if filter_name is not None:
        filter_p = f"{filter_name}.filter"
        filter_a = f"{filter_name}.aux"
        with open(filter_p, "rb") as f:
            filter_i = pickle.load(f)
        aux = pd.read_pickle(filter_a)
        selection = df.apply(lambda x: filter_i[x["id"]], axis=1)
        selection_aux = aux.apply(lambda x: filter_i[x["id"]], axis=1)

        df = df[selection]
        aux = aux[selection_aux]

    aux = aux.set_index("id")
    df = df.reset_index(drop=True)

    # df -> src_title, src_link, q, a
    pages = {row.src_link: row.src_title for _, row in df.iterrows()}
    grouped = {
        link: list(df[df.src_link == link].apply(lambda x: (x["id"], x.q, x.a), axis=1))
        for link in pages
    }

    document = []
    for group, pairs in grouped.items():
        title = pages[group]
        document.append(f"### {title}")
        for id_, q, a in pairs:
            q = q.replace("\n", "").strip()
            document.append(f"#### {q}")
            document.append(a)
            aux_data = dict(aux.loc[id_])
            aux_data = ", ".join(f"{k}={v:.2f}" for k, v in aux_data.items())
            if aux_data.strip() != "":
                document.append(f"\n```{aux_data}```")

    doc = "\n".join(document)
    with open("out.md", "w") as f:
        f.write(doc)

    sprint("Successfully rendered data to out.md!", fg="green")
