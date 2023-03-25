import subprocess
from os.path import join as pjoin, exists as fexists

import click
import pandas as pd

from autofaq.cli.entry import entry
from autofaq.cli.commands.util import create_directories_and_settings
from autofaq.search.google_keywords import GoogleKeywords

modes = ["single", "google", "general"]

langs = {"fa": ("سوالات متداول", ""), "en": ("frequently asked questions", "in")}


@entry.command(help="Creates a list of keywords")
@click.option(
    "-a", "--append", default=True, is_flag=True, help="append if keyword list exists"
)
@click.option("-d", "--digits", default=False, is_flag=True, help="use digits in hints")
@click.option(
    "-m",
    "--mode",
    default="google",
    help="mode for creating keywords",
    type=click.Choice(modes),
)
@click.option(
    "-l",
    "--language",
    default="fa",
    help="target language",
    type=click.Choice(list(langs.keys())),
)
@click.argument("keyword", required=False)
def keywords(keyword, append, digits, mode, language):
    if mode == "single":
        data = [keyword]
    elif mode == "google" or mode == "general":
        d_kw = "-nd" if digits else ""
        kw = GoogleKeywords(lang=f"{language}{d_kw}")
        f_word, f_ap = langs[language]
        m_kw = keyword if mode == "google" else ""
        if mode == "google" and keyword is None:
            click.echo(click.style("Keyword required for google mode!", fg="red"))
            return
        df = kw.load(f"{f_word} {f_ap} {m_kw}".strip())
        data = list(df.suggestion)
    if append and fexists("keywords.csv"):
        prev_data = list(pd.read_csv("keywords.csv")["query"])
        data = [*prev_data, *data]
    df = pd.DataFrame()
    df["id"] = range(len(data))
    df["query"] = data
    df["include"] = True
    df.to_csv("keywords.csv", index=False)
