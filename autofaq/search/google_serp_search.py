import json
import pickle
from functools import reduce
from hashlib import sha256
from os.path import exists as fexists
from time import sleep
from urllib.parse import urlencode

import pandas as pd
import requests
from tqdm import tqdm

from autofaq.search.limit_respecter import LimitRespecter, State


def search_serp(q, num=10, country="ir", lang="fa"):
    payload = json.dumps(
        {
            "q": q,
            "gl": country,
            "hl": lang,
            "num": num,
        }
    )
    headers = {
        "X-API-KEY": "709299a5526db140c9b2b58b7b6d4136417f4193",  # TODO: better key read, will reset though
        "Content-Type": "application/json",
    }
    proxies = {
        "https": "socks5://127.0.0.1:1089",
        "http": "socks5://127.0.0.1:1089",
    }
    response = requests.request(
        "POST",
        "https://google.serper.dev/search",
        headers=headers,
        data=payload,
        proxies=proxies,
    )
    res = response.json()
    return res


def serp_search_all(queries, num=10, country="ir", lang="fa", max_per_sec=50):
    qx = "-".join(sorted(queries)) + f"-{num}-{country}-{lang}"
    sig = sha256(qx.encode("utf-8")).hexdigest()
    cache_file = f".cache/serp.{sig}.cache"
    all_ = []

    if fexists(cache_file):
        # Check cache first
        with open(cache_file, "rb") as f:
            all_ = pickle.load(f)
    else:
        # Search all
        for q in tqdm(queries):
            res = search_serp(q, num=num, country=country, lang=lang)
            all_.append(res)
            sleep(1 / max_per_sec)
        # Cache Results
        with open(cache_file, "wb") as f:
            pickle.dump(all_, f)

    results = []
    for r in all_:
        for o in r["organic"]:
            results.append(
                {
                    "title": o["title"],
                    "link": o["link"],
                    "content": o["snippet"],
                    "q": r["searchParameters"]["q"],
                }
            )
    df = pd.DataFrame(results, columns=["title", "link", "content", "q"])
    return df
