import itertools
import json
import string
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import reduce

import pandas as pd
from httpx import Client


class GoogleKeywords:
    config = {"wait_time": 0.1, "max_workers": 20}
    lang_chars = {
        "fa": {"digits": "۰۱۲۳۴۵۶۷۸۹", "chars": "یهونملگکقفغعظطضصشسژزرذدخحچجثتپباء"},
        "en": {"digits": string.digits, "chars": string.ascii_lowercase},
        "fa-nd": {"chars": "یهونملگکقفغعظطضصشسژزرذدخحچجثتپباء"},
        "en-nd": {"chars": string.ascii_lowercase},
    }

    @staticmethod
    def register_chars(lang_code: str, chars: str = "", digits: str = ""):
        GoogleKeywords.lang_chars[lang_code] = {"digits": digits, "chars": chars}
        GoogleKeywords.lang_chars[f"{lang_code}-nd"] = {"chars": chars}

    def __init__(self, lang="fa", wait_time=0, max_workers=0) -> None:
        if wait_time == 0:
            self.wait_time = GoogleKeywords.config["wait_time"]
        if max_workers == 0:
            self.max_workers = GoogleKeywords.config["max_workers"]
        self.lang = lang
        self.client = Client()
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)

    def make_google_request(self, query):
        url = "http://suggestqueries.google.com/complete/search"
        params = {"client": "firefox", "hl": self.lang, "q": query}
        headers = {"User-agent": "Mozilla/5.0"}

        time.sleep(self.wait_time)
        response = self.client.get(url, params=params, headers=headers)

        if response.status_code == 200:
            suggestions = json.loads(response.content.decode("utf-8"))[1]
            return suggestions
        else:
            raise RuntimeError("failed response")

    def get_google_suggests(self, keyword):
        char_list = (
            reduce(lambda x, y: x + y, GoogleKeywords.lang_chars[self.lang].values())
            + " "
        )
        query_list = [keyword + " " + char for char in char_list]

        suggestions = []
        for query in query_list:
            try:
                res = self.make_google_request(query)
                suggestions.append(res)
            except RuntimeError as e:
                print(e)

        # Remove empty suggestions
        suggestions = set(itertools.chain(*suggestions))
        if "" in suggestions:
            suggestions.remove("")

        return suggestions

    def load(
        self,
        *keywords: tuple[str],
    ):
        tasks = {}
        for kw in keywords:
            task = self.executor.submit(self.get_google_suggests, kw)
            tasks[task] = kw
        result = []
        for future in as_completed(tasks):
            kw = tasks[future]
            for suggestion in future.result():
                result.append([kw, suggestion])
        return pd.DataFrame(result, columns=["keyword", "suggestion"])
