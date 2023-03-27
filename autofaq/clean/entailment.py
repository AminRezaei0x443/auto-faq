import numpy as np
import torch
from pandas import DataFrame

from autofaq.clean.cleaner import Cleaner


class EntailmentCleaner(Cleaner):
    def clean(self, df: DataFrame):
        embeddings = torch.load(".cache/embeddings.bin")
        scores_map = {k: torch.dot(v["q"], v["a"]) for k, v in embeddings.items()}
        self_scores = {k: torch.dot(v["q"], v["q"]) for k, v in embeddings.items()}
        deviation_map = {k: np.abs(scores_map[k] - self_scores[k]) for k in scores_map}
        ids = list(df["id"])
        scores_map = {k: v for k, v in scores_map.items() if k in ids}
        scores = list(scores_map.values())
        m, var = np.mean(scores), np.std(scores)
        print(f"mean: {m}, std: {var}")
        deviations = list(deviation_map.values())
        m_dev, std_dev = np.mean(deviations), np.std(deviations)
        print(f"dev mean: {m_dev}, dev std: {std_dev}")
        r = df.apply(
            lambda x: bool(
                (scores_map[x["id"]] > m) and (deviation_map[x["id"]] < m_dev)
            ),
            axis=1,
        )
        return r
