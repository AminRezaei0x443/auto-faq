import numpy as np
import torch
from fuzzywuzzy.fuzz import ratio
from pandas import DataFrame

from autofaq.clean.cleaner import Cleaner


class FuzzCleaner(Cleaner):
    def clean(self, df: DataFrame, aux: DataFrame = None):
        aux["fuzz"] = df.apply(lambda x: ratio(x.q, x.a), axis=1)
        m, var = aux["fuzz"].mean(), aux["fuzz"].std()
        print(f"mean: {m}, std: {var}")
        return df.apply(lambda x: ratio(x.q, x.a) < (m + var), axis=1)
