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

from autofaq.config.configurable import Configurable
from autofaq.search.limit_respecter import LimitRespecter, State
from autofaq.search.search_engine import SearchEngine


class SerpEngine(SearchEngine, Configurable):
    def search(self, query_list: list[str]) -> pd.DataFrame:
        num = self.config.num_results
        lang = self.config.lang
        country = self.config.country
        rate = self.config.rate
        return self.serp_search_all(
            query_list, num=num, country=country, lang=lang, max_per_sec=rate
        )

    def settings(self):
        return {
            "namespace": "search.google",
            "api_key": (str, "API_KEY", True, "Serper API Key"),
            "url_filters": (list[str], [], False, "Url filters"),
            "lang": (str, "fa", False, "Language"),
            "country": (str, "ir", False, "Country"),
            "num_results": (int, 10, False, "Number of results"),
            "rate": (int, 50, False, "Rate of req/sec"),
            "use_proxy": (
                bool,
                False,
                False,
                "Use proxy or not [Socks5 supported only]",
            ),
            "proxy_host": (str, "127.0.0.1", False, "Proxy host"),
            "proxy_port": (int, 1089, False, "Proxy port"),
        }

    def search_serp(self, q, num=10, country="ir", lang="fa"):
        q = q.strip()
        url_filters = self.config.url_filters
        filter_q = ""
        if len(url_filters) > 0:
            filter_q = "|".join(f'inurl:"{f}"' for f in url_filters)
            filter_q = f"({filter_q}) "
        qx = f"{filter_q}{q}-{num}-{country}-{lang}"
        sig = sha256(qx.encode("utf-8")).hexdigest()
        cache_file = f".cache/serp.{sig}.cache"

        if fexists(cache_file):
            with open(cache_file, "r") as f:
                res = json.load(f)
                return res

        payload = json.dumps(
            {
                "q": f"{filter_q}{q}",
                "gl": country,
                "hl": lang,
                "num": num,
            }
        )
        headers = {
            "X-API-KEY": self.config.api_key,
            "Content-Type": "application/json",
        }
        proxies = None
        if self.config.use_proxy:
            proxies = {
                "https": f"socks5://{self.config.proxy_host}:{self.config.proxy_port}",
                "http": f"socks5://{self.config.proxy_host}:{self.config.proxy_port}",
            }
        response = requests.request(
            "POST",
            "https://google.serper.dev/search",
            headers=headers,
            data=payload,
            proxies=proxies,
        )
        res = response.json()

        with open(cache_file, "w") as f:
            json.dump(res, f)

        return res

    def serp_search_all(self, queries, num=10, country="ir", lang="fa", max_per_sec=50):
        all_ = []
        # Search all
        for q in tqdm(queries):
            res = self.search_serp(q, num=num, country=country, lang=lang)
            all_.append(res)
            sleep(1 / max_per_sec)

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
