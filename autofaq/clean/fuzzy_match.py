import numpy as np
import torch
from fuzzywuzzy.fuzz import ratio
from pandas import DataFrame

from autofaq.clean.cleaner import Cleaner
from autofaq.util.out import sprint


class FuzzCleaner(Cleaner):
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
        return df.apply(lambda x: ratio(x.q, x.a) < (m + var), axis=1)
