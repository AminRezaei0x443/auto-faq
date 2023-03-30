from autofaq.config.configurable import Configurable
from autofaq.search.search_engine import SearchEngine
from autofaq.search.xng_search import XNGSearch


class XNGEngine(SearchEngine, Configurable):
    def search(self, query_list: list[str]):
        # TODO: Gather servers
        # TODO: Run queries
        # TODO: Return aggregated and deduplicated results
        raise NotImplementedError("XNG engine is not complete yet!")

    def settings(self):
        return {
            "namespace": "search.xng",
            "lang": (str, "fa-IR", False, "Language and region"),
        }
