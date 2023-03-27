from abc import ABC, abstractmethod

from pandas import DataFrame


class Cleaner(ABC):
    def clean(self, df: DataFrame, **kwargs):
        pass
