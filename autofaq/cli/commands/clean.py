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


@entry.command(help="Cleans the dataset")
def clean():
    df = pd.read_csv("dataset.csv")
    df = df.fillna("")
    selection = df.a.apply(lambda x: type(x) == str and x.strip() != "")
    df = df[selection]
    print(selection.sum(), len(selection))
    df.to_csv("dataset-cleaned.csv", index=False)
