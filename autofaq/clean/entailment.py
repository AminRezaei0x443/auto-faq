import numpy as np
import torch
from pandas import DataFrame

from autofaq.clean.cleaner import Cleaner


class EntailmentCleaner(Cleaner):
    def clean(self, df: DataFrame):
        embeddings = torch.load(".cache/embeddings.bin")
        scores_map = {k: torch.dot(v["q"], v["a"]) for k, v in embeddings.items()}
        ids = list(df["id"])
        scores_map = {k: v for k, v in scores_map.items() if k in ids}
        scores = list(scores_map.values())
        m = np.mean(scores)
        var = np.std(scores)
        print(f"mean: {m}, std: {var}")
        r = df.apply(lambda x: bool(scores_map[x["id"]] > m), axis=1)
        return r
