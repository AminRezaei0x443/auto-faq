from functools import reduce
from urllib.parse import urlencode

import bs4
import pandas as pd
import requests
from user_agent import generate_user_agent

from autofaq.search.limit_respecter import LimitRespecter, State


class SearchTask:
    def __init__(self, instance: "XNGSearch", url: str) -> None:
        self._instance = instance
        self._url = url

    def __call__(self):
        resp = requests.get(self._url, headers=self._instance._headers)
        body = resp.content
        page = bs4.BeautifulSoup(body)
        article_count = len(page.select("#urls > article"))
        articles = []
        for i in range(article_count):
            h3 = page.select(f"#urls > article:nth-child({i+1}) > h3")
            h3 = h3[0]
            link = h3.a["href"]
            title = h3.text
            p = page.select(f"#urls > article:nth-child({i+1}) > p")
            content = p[0].text
            articles.append(
                {
                    "title": title,
                    "link": link,
                    "content": content,
                }
            )
        return articles


class XNGSearch:
    def __init__(self, server) -> None:
        self._server = server
        self._respecter = LimitRespecter({1: 2, 20: 15, 600: 150})
        self._headers = {
            "User-Agent": generate_user_agent(),
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9,fa-IR;q=0.8,fa;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        }
        self._reqs = {}

    def create_search_task(self, url):
        return SearchTask(self, url)

    def queue_search(self, q, lang="fa-IR", engine="google", page_no=1):
        params = {
            "q": q,
            "language": lang,
            "engines": engine,
            "pageno": page_no,
        }
        encoded = urlencode(params)
        search_url = self._server + "?" + encoded
        task = self.create_search_task(search_url)
        _id = self._respecter.queue(task)
        self._reqs[_id] = {
            "q": q,
            "params": params,
        }

    def retreive(self):
        r = self._respecter.exec_all()
        for k, v in r.items():
            self._reqs[k]["result"] = v
            if self._respecter._reqs[k]["state"] == State.FAILED:
                self._reqs[k]["err"] = self._respecter._reqs[k]["err"]
        return self._agg(self._reqs)

    def _agg(self, results):
        agg_result = reduce(
            lambda x, y: x + y,
            filter(
                lambda x: x is not None,
                map(
                    lambda v: list(
                        map(
                            lambda r: {**r, "q": v["q"]},
                            [] if v["result"] is None else v["result"],
                        )
                    ),
                    results.values(),
                ),
            ),
        )
        df = pd.DataFrame(agg_result, columns=["title", "link", "content", "q"])
        return df
