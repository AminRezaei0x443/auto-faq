import json
import pickle
import subprocess
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
from autofaq.config.binder import bind
from autofaq.language_model.xlm_embedder import XLMEmbedder
from autofaq.util.hash import sha256id
from autofaq.util.out import sprint

embedders = {
    "xlm": XLMEmbedder,
}


@entry.command(help="Computes vector embeddings of the dataset")
@click.option(
    "-s", "--scratch", default=False, is_flag=True, help="ignore present embeddings"
)
@click.option(
    "-e",
    "--embedder",
    default="xlm",
    help="embedder module",
    type=click.Choice(list(embedders.keys())),
)
@click.argument("filter_name", required=False)
def embed(filter_name, embedder, scratch):
    sprint("Beginning the embedding process for project ...", fg="cyan")

    df = pd.read_csv("dataset.csv")
    if filter_name is not None:
        filter_p = f"{filter_name}.filter"
        with open(filter_p, "rb") as f:
            filter_i = pickle.load(f)
        selection = df.apply(lambda x: filter_i[x["id"]], axis=1)
        df = df[selection]
    o_df = df.reset_index(drop=True)

    sprint("Initiating ONNX session for language model ...", fg="black")
    embedder = embedders[embedder]()
    ok = bind(embedder, "settings.toml")
    if not ok:
        return

    e_path = ".cache/embeddings.bin"
    if fexists(e_path) and not scratch:
        embeddings = torch.load(e_path)
    else:
        embeddings = {}

    # Filter out existants here
    df = o_df[o_df["id"].apply(lambda x: x not in embeddings)]
    df.reset_index(drop=True)

    sprint("Embedding QA pairs ...", fg="black")
    sentences = list(df.q) + list(df.a)
    batches = batch(sentences)
    s_embeds = embed_batches(embedder, batches)

    n = len(df)

    for i, row in df.iterrows():
        q_e = s_embeds[i]
        a_e = s_embeds[n + i]
        embeddings[row["id"]] = {
            "q": q_e,
            "a": a_e,
        }

    df = o_df[o_df.src_title.apply(lambda x: f"t-{sha256id(x)}" not in embeddings)]
    df.reset_index(drop=True)

    sprint("Embedding page titles ...", fg="black")
    titles = list(set(df.src_title.apply(lambda x: x.strip())))
    batches = batch(titles)
    t_embeds = embed_batches(embedder, batches)
    for title, embedding in zip(titles, t_embeds):
        embeddings[f"t-{sha256id(title)}"] = embedding

    torch.save(embeddings, e_path)
    sprint("Successfully calculated and saved the embeddings!", fg="green")


def batch(items, size=16):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def embed_batches(embedder, batches):
    embeddings = ()
    batches = list(batches)  # To track progress
    for b in tqdm(batches):
        res = embedder.embed(b)
        if len(embeddings) == 0:
            embeddings = res
        else:
            embeddings = torch.cat((embeddings, res))
    return embeddings
