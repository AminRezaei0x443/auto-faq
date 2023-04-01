import subprocess
from os.path import join as pjoin

import click
import tomlkit
from tomlkit import boolean, document, nl, table

from autofaq.clean.entailment import EntailmentCleaner
from autofaq.clean.fuzzy_match import FuzzCleaner
from autofaq.clean.page import PageCleaner
from autofaq.clean.subject import SubjectCleaner
from autofaq.cli.entry import entry
from autofaq.language_model.xlm_embedder import XLMEmbedder
from autofaq.search.ddg_engine import DDGEngine
from autofaq.search.google_serp_search import SerpEngine
from autofaq.search.xng_engine import XNGEngine
from autofaq.util.dir import create_directories_and_settings
from autofaq.util.out import sprint

configurables = [
    EntailmentCleaner,
    FuzzCleaner,
    SubjectCleaner,
    PageCleaner,
    DDGEngine,
    SerpEngine,
    XNGEngine,
    XLMEmbedder,
]


@entry.command(help="Initiates a new mining project")
@click.option("-p", "--path", default=".", help="base path")
@click.option(
    "-f", "--force", default=False, is_flag=True, help="overwrite project if exists"
)
@click.argument("name")
def init(name, path, force):
    sprint("Initializing new mining project ...", fg="cyan")

    structure = {
        ".cache": None,
    }

    doc = document()
    doc.add("name", name)
    doc.add(nl())
    configs = gather_configs(doc)

    ok = create_directories_and_settings(structure, configs, pjoin(path, name), force)
    if ok:
        sprint("Successfully created project!", fg="green")
    else:
        sprint("Error creating project!", fg="red")


def gather_configs(d=None):
    all_ = {}
    for c in configurables:
        o = c()
        s = o.settings()
        namespace = s.pop("namespace", None)
        for k, v in s.items():
            if namespace:
                k = f"{namespace}.{k}"
            all_[k] = v
    if d is None:
        d = document()
    for k, v in all_.items():
        path = k.split(".")
        *trail, last = path
        cur = d
        for t in trail:
            if t not in cur:
                cur.add(t, table())
            cur = cur[t]
        type_, def_, req_, hint = v
        cm = f"{hint} (type: {type_.__name__})".strip()
        if type_ == bool:
            item = boolean("true" if def_ else "")
            item = item.comment(cm)
            cur.add(last, item)
        else:
            cur.add(last, def_)
            cur[last].comment(cm)
    return d
