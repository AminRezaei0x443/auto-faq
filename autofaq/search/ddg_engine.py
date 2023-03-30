from autofaq.config.configurable import Configurable
from autofaq.search.ddg_search import DDGSearch
from autofaq.search.search_engine import SearchEngine


class DDGEngine(SearchEngine, Configurable):
    def search(self, query_list: list[str]):
        engine = DDGSearch()
        for q in query_list:
            engine.queue_search(q, lang=self.config.lang)
        results = engine.retreive()
        return results

    def settings(self):
        return {
            "namespace": "search.ddg",
            "lang": (str, "fa-IR", False, "Language and region"),
        }
