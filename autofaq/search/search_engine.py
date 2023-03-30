from abc import ABC, abstractmethod

from pandas import DataFrame


class SearchEngine(ABC):
    @abstractmethod
    def search(self, query_list: list[str], **kwargs) -> DataFrame:
        pass
