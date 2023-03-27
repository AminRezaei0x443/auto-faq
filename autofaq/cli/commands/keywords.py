import subprocess
from os.path import exists as fexists
from os.path import join as pjoin

import click
import pandas as pd

from autofaq.cli.entry import entry
from autofaq.search.google_keywords import GoogleKeywords
from autofaq.util.out import sprint

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
    sprint("Gathering relevant keywords for project ...", fg="cyan")
    if mode == "single":
        data = [keyword]
    elif mode == "google" or mode == "general":
        d_kw = "-nd" if digits else ""
        kw = GoogleKeywords(lang=f"{language}{d_kw}")
        f_word, f_ap = langs[language]
        m_kw = keyword if mode == "google" else ""
        if mode == "google" and keyword is None:
            sprint("Keyword required for google mode!", fg="red")
            return

        df = kw.load(f"{f_word} {f_ap} {m_kw}".replace("  ", " ").strip())
        data = list(df.suggestion)
    if append and fexists("keywords.csv"):
        prev_data = list(pd.read_csv("keywords.csv")["query"])
        data = [*prev_data, *data]
    df = pd.DataFrame()
    df["id"] = range(len(data))
    df["query"] = data
    df["include"] = True
    df.to_csv("keywords.csv", index=False)
    sprint("Successfully saved keywords to keywords.csv!", fg="green")
