import numpy as np
import torch
from pandas import DataFrame

from autofaq.clean.cleaner import Cleaner
from autofaq.util.out import sprint


class EntailmentCleaner(Cleaner):
    def clean(self, df: DataFrame, aux: DataFrame = None):
        sprint("Filtering data using entailment cleaner ...", fg="cyan")
        embeddings = torch.load(".cache/embeddings.bin")
        embeddings = {k: v for k, v in embeddings.items() if isinstance(k, int)}
        scores_map = {k: torch.dot(v["q"], v["a"]) for k, v in embeddings.items()}
        self_scores = {k: torch.dot(v["q"], v["q"]) for k, v in embeddings.items()}
        deviation_map = {k: np.abs(scores_map[k] - self_scores[k]) for k in scores_map}
        ids = list(df["id"])
        scores_map = {k: v for k, v in scores_map.items() if k in ids}
        scores = list(scores_map.values())
        m, var = np.mean(scores), np.std(scores)
        sprint(
            "Entailment scores => mean: @m, std: @std",
            fg="black",
            m=(m, "magenta"),
            std=(var, "magenta"),
        )
        deviations = list(deviation_map.values())
        m_dev, std_dev = np.mean(deviations), np.std(deviations)
        sprint(
            "QA Deviation scores => mean: @m, std: @std",
            fg="black",
            m=(m_dev, "magenta"),
            std=(std_dev, "magenta"),
        )
        aux["entailment-score"] = df.apply(lambda x: scores_map[x["id"]], axis=1)
        aux["entailment-deviation"] = df.apply(lambda x: deviation_map[x["id"]], axis=1)
        r = df.apply(
            lambda x: bool(
                (scores_map[x["id"]] > m)
                and (deviation_map[x["id"]] > (m_dev - 2 * std_dev))
                and (deviation_map[x["id"]] < (m_dev + 2 * std_dev))
            ),
            axis=1,
        )
        return r
