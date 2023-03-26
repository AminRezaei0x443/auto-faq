import json
import subprocess
from hashlib import sha256
from os.path import exists as fexists
from os.path import join as pjoin

import click
import pandas as pd
import requests
from tqdm import tqdm
from user_agent import generate_user_agent

from autofaq.cli.entry import entry
from autofaq.extract.extract import retreive_qa

headers = {
    "User-Agent": generate_user_agent(),
    "Accept-Language": "en-US,en;q=0.9,fa-IR;q=0.8,fa;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
}


@entry.command(help="Gathers all webpages and extracts QA pairs from them")
def extract():
    pages = pd.read_csv("search.csv")
    r = pages.to_dict(orient="index")
    r = list(r.values())
    for d in tqdm(r):
        try:
            # TODO: multithread
            # We check cache first
            hash_ = sha256(d["link"].encode("utf-8")).hexdigest()
            tg = f".cache/{hash_}"
            if fexists(tg):
                with open(tg, "rb") as f:
                    d["state"] = 200
                    d["html"] = f.read()
            else:
                rs = requests.get(d["link"], headers=headers, timeout=3)
                if rs.status_code != 200:
                    print("encountered error on dude", d["link"])
                d["state"] = rs.status_code
                d["html"] = rs.content
                with open(tg, "wb") as f:
                    f.write(d["html"])
        except Exception as e:
            print("encountered error on dude", d["link"])
            d["state"] = -1
            d["html"] = e
    for d in tqdm(r):
        try:
            qa = retreive_qa(d["html"])
            d["qa"] = qa
        except Exception as e:
            d["qa"] = []
    dataset = []

    for d in tqdm(r):
        src_title = d["title"]
        src_link = d["link"]
        qa = d["qa"]
        for q, a in qa:
            dataset.append(
                {
                    "src_title": src_title,
                    "src_link": src_link,
                    "q": q,
                    "a": " ".join(a),
                }
            )
    data = pd.DataFrame(dataset)
    data.to_csv("dataset.csv", index=False)
