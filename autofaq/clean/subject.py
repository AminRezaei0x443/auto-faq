import numpy as np
import torch
from pandas import DataFrame

from autofaq.clean.cleaner import Cleaner
from autofaq.config.configurable import Configurable
from autofaq.util.out import sprint


class SubjectCleaner(Cleaner, Configurable):
    def clean(self, df: DataFrame, aux: DataFrame = None):
        sprint("Filtering data using subject cleaner ...", fg="cyan")
        embeddings = torch.load(".cache/embeddings.bin")
        embeddings = {k: v for k, v in embeddings.items() if isinstance(k, int)}
        q_embeds = torch.cat(tuple(v["q"].reshape(1, -1) for v in embeddings.values()))
        q_mean = torch.mean(q_embeds, axis=0, keepdim=True)
        distances = torch.cdist(q_embeds, q_mean).reshape(-1)
        m, std = distances.mean(), distances.std()
        m, std = m.item(), std.item()
        sprint(
            "Distance from subject centeroid => mean: @m, std: @std",
            fg="black",
            m=(m, "magenta"),
            std=(std, "magenta"),
        )
        threshold = m + self.config.distance_std * std
        filter_ = {k: bool(v < threshold) for k, v in zip(embeddings.keys(), distances)}
        return df.apply(lambda x: filter_[x["id"]], axis=1)

    def settings(self):
        return {
            "namespace": "clean.subject",
            "distance_std": (float, 1, False, ""),
        }
