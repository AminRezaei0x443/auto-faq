import json
import subprocess
from hashlib import sha256
from os.path import exists as fexists
from os.path import join as pjoin

import click
import numpy as np
import pandas as pd
import requests
from tqdm import tqdm
from user_agent import generate_user_agent

from autofaq.cli.entry import entry
from autofaq.language_model.xlm import embedSentences, openXLMSession


def entailment(session, x, y):
    res = embedSentences(session, [x, y])
    x_features, y_features = res[0], res[1]
    return np.dot(x_features, y_features)


@entry.command(help="Assigns QA entailment scores to the dataset")
def entail():
    session = openXLMSession(
        "/Volumes/WorkSpace/AutoFAQ/models/quantized-xlm-paraphrase"
    )
    df = pd.read_csv("dataset-cleaned.csv")
    tqdm.pandas()
    df["entailment"] = df.progress_apply(
        lambda row: entailment(session, row.q, row.a), axis=1
    )
    df.to_csv("dataset-scored.csv", index=False)
