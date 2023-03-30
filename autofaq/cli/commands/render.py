import json
import pickle
import re
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
from autofaq.render.json_renderer import JSONRenderer
from autofaq.render.md_renderer import MarkdownRenderer
from autofaq.util.out import sprint

# This matches languages characters of persian and english (no digits)
# Aim: Easy clearance of numbered lists and questions
alpha_L = r"[^\u0041-\u005A\u0061-\u007A\u0622\u0626-\u0628\u062a-\u063a\u0641\u0642\u0644-\u0648\u067e\u0686\u0698\u06a9\u06af\u06cc\u200f\u0020]+"

renderers = {
    "md": MarkdownRenderer,
    "markdown": MarkdownRenderer,
    "json": JSONRenderer,
}


def replace_prefix_pattern(target, pattern):
    r = re.search(pattern, target, re.UNICODE)
    if r is None:
        return target
    begin_i, end_i = r.span()
    if begin_i == 0:
        return target[end_i:]
    return target


@entry.command(help="Transforms the dataset into human-readable formats")
@click.option(
    "-r",
    "--renderer",
    default="md",
    help="renderer engine",
    type=click.Choice(list(renderers.keys())),
)
@click.argument("filter_name", required=False)
def render(filter_name, renderer):
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

    query_df = pd.read_csv("search.csv")
    query_df = query_df.set_index("link", drop=True)

    data = []
    for group, pairs in grouped.items():
        title = pages[group]
        query = query_df.loc[group]["q"]
        if not isinstance(query, str):
            query = query.iloc[0]
        page = {
            "title": title,
            "query": query,
            "pairs": [],
        }
        for id_, q, a in pairs:
            q = q.replace("\n", "").strip()
            q = replace_prefix_pattern(q, alpha_L)

            aux_data = dict(aux.loc[id_])
            page["pairs"].append(
                {
                    "q": q,
                    "a": a,
                    "aux": aux_data,
                }
            )
        data.append(page)

    renderer = renderers[renderer]()
    o = renderer.render(data, "out")

    sprint("Successfully rendered data to @o!", fg="green", o=(o, "green", "bold"))
