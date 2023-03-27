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


def batch(items, size=16):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def embed_batches(session, batches):
    embeddings = None
    batches = list(batches)  # To track progress
    for b in tqdm(batches):
        res = embedSentences(session, b)
        if embeddings is None:
            embeddings = res
        else:
            embeddings = torch.cat((embeddings, res))
    return embeddings


@entry.command(help="Calculates the vector embeddings of the dataset")
@click.argument("filter_name", required=False)
def embed(filter_name):
    sprint("Beginning the embedding process for project ...", fg="cyan")

    df = pd.read_csv("dataset.csv")
    if filter_name is not None:
        filter_p = f"{filter_name}.filter"
        with open(filter_p, "rb") as f:
            filter_i = pickle.load(f)
        selection = df.apply(lambda x: filter_i[x["id"]], axis=1)
        df = df[selection]
    df = df.reset_index(drop=True)

    sprint("Initiating ONNX session for language model ...", fg="black")
    session = openXLMSession(
        "/Volumes/WorkSpace/AutoFAQ/models/quantized-xlm-paraphrase"
    )

    embeddings = {}
    sentences = list(df.q) + list(df.a)
    batches = batch(sentences)
    s_embeds = embed_batches(session, batches)

    n = len(df)

    for i, row in df.iterrows():
        q_e = s_embeds[i]
        a_e = s_embeds[n + i]
        embeddings[row["id"]] = {
            "q": q_e,
            "a": a_e,
        }

    torch.save(embeddings, ".cache/embeddings.bin")
    sprint("Successfully calculated and saved the embeddings!", fg="green")
