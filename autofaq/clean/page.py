import numpy as np
import torch
from pandas import DataFrame

from autofaq.clean.cleaner import Cleaner
from autofaq.util.hash import sha256id
from autofaq.util.out import sprint

blacklist = {
    "fa": [
        "نمونه سوال",
    ]
}


def filter_title(filter_map, title):
    title = title.strip()
    q = filter_map[sha256id(title)]
    if q:
        for lang, l_ in blacklist.items():
            for w in l_:
                if w in title:
                    return False
    return q


class PageCleaner(Cleaner):
    def clean(self, df: DataFrame, aux: DataFrame = None):
        sprint("Filtering data using page title cleaner ...", fg="cyan")
        embeddings = torch.load(".cache/embeddings.bin")
        titles = list(set(df.src_title.apply(lambda x: x.strip())))

        title_map = {}
        for t in titles:
            s = sha256id(t)
            title_map[s] = embeddings[f"t-{s}"]

        t_embeds = torch.cat(tuple(v.reshape(1, -1) for v in title_map.values()))
        q_mean = torch.mean(t_embeds, axis=0, keepdim=True)
        distances = torch.cdist(t_embeds, q_mean).reshape(-1)
        m, std = distances.mean(), distances.std()
        m, std = m.item(), std.item()
        sprint(
            "Distance from title centeroid => mean: @m, std: @std",
            fg="black",
            m=(m, "magenta"),
            std=(std, "magenta"),
        )
        threshold = m + std
        filter_ = {k: bool(v < threshold) for k, v in zip(title_map.keys(), distances)}
        return df.apply(lambda x: filter_title(filter_, x["src_title"]), axis=1)
