import numpy as np
import torch
from fuzzywuzzy.fuzz import ratio
from pandas import DataFrame

from autofaq.clean.cleaner import Cleaner
from autofaq.config.configurable import Configurable
from autofaq.util.out import sprint


class FuzzCleaner(Cleaner, Configurable):
    def clean(self, df: DataFrame, aux: DataFrame = None):
        sprint("Filtering data using fuzzy cleaner ...", fg="cyan")
        aux["fuzz"] = df.apply(lambda x: ratio(x.q, x.a), axis=1)
        m, var = aux["fuzz"].mean(), aux["fuzz"].std()
        sprint(
            "QA fuzz ratio => mean: @m, std: @std",
            fg="black",
            m=(m, "magenta"),
            std=(var, "magenta"),
        )
        threshold = m + self.config.fuzz_std * var
        return df.apply(lambda x: ratio(x.q, x.a) < threshold, axis=1)

    def settings(self):
        return {
            "namespace": "clean.fuzz",
            "fuzz_std": (float, 1, False, ""),
        }
