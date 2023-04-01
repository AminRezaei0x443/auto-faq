import json
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from hashlib import sha256
from os.path import exists as fexists
from os.path import join as pjoin
from urllib.parse import unquote

import click
import pandas as pd
import requests
from tqdm import tqdm
from user_agent import generate_user_agent

from autofaq.cli.entry import entry
from autofaq.extract.better_extractor import BetterExtractor
from autofaq.extract.easy_extractor import EasyExtractor
from autofaq.util.out import sprint

headers = {
    "User-Agent": generate_user_agent(),
    "Accept-Language": "en-US,en;q=0.9,fa-IR;q=0.8,fa;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
}

extractors = {
    "easy": EasyExtractor,
    "better": BetterExtractor,
}


def fetch_content(url, retry=False):
    hash_ = sha256(url.encode("utf-8")).hexdigest()
    tg = f".cache/{hash_}"
    try:
        if fexists(tg):
            with open(tg, "rb") as f:
                c = f.read()
                if c == "|error|" and not retry:
                    return hash_, False
                return hash_, True, c
        response = requests.get(url, timeout=4)
        if response.status_code == 200:
            with open(tg, "wb") as f:
                f.write(response.content)
            return hash_, True, response.content
        else:
            with open(tg, "wb") as f:
                f.write("|error|".encode("utf-8"))
            return hash_, False, None
    except requests.exceptions.RequestException:
        with open(tg, "wb") as f:
            f.write("|error|".encode("utf-8"))
        return hash_, False, None


def download_contents(urls, num_threads=8):
    contents = {}
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = {executor.submit(fetch_content, url): url for url in urls}

        for future in tqdm(as_completed(futures), total=len(urls)):
            hash_, ok, content = future.result()
            contents[hash_] = (ok, content)

    return contents


@entry.command(help="Collects webpages and extracts QA pairs")
@click.option(
    "-e",
    "--extractor",
    default="easy",
    help="extractor engine",
    type=click.Choice(list(extractors.keys())),
)
def extract(extractor):
    sprint("Starting the extraction process ...", fg="cyan")

    pages = pd.read_csv("search.csv")
    r = pages.to_dict(orient="index")
    r = list(r.values())

    sprint("Gathering webpages from web:", fg="black")
    errors = []
    content_map = download_contents(list(map(lambda x: x["link"], r)))
    for d in r:
        hash_ = sha256(d["link"].encode("utf-8")).hexdigest()
        ok, content = content_map[hash_]
        if ok:
            d["state"] = 200
            d["html"] = content
        else:
            errors.append(d["link"])
            d["state"] = -1
            d["html"] = ""

    if len(errors) != 0:
        sprint(
            "Couldn't gather @count webpages! List:",
            fg="red",
            count=(len(errors), "red", "bold"),
        )
        for e in errors:
            sprint(unquote(e), fg="black")

    sprint("Extracting QA pairs ...", fg="black")

    extractor = extractors[extractor]()
    for d in tqdm(r):
        try:
            qa = extractor.extract(d["html"])
            d["qa"] = qa
        except Exception:
            d["qa"] = []

    dataset = []

    for d in tqdm(r):
        src_title = d["title"]
        src_link = d["link"]
        qa = d["qa"]
        for pair in qa:
            dataset.append(
                {
                    "src_title": src_title,
                    "src_link": src_link,
                    **pair,
                }
            )
    data = pd.DataFrame(dataset)
    data["id"] = range(len(data))
    data.to_csv("dataset.csv", index=False)
    sprint("Successfully saved QA pairs to dataset.csv!", fg="green")
