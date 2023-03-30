from tomlkit import parse

from autofaq.config.configurable import Configurable


def bind(obj, config: str | dict):
    if isinstance(config, str):
        with open(config, "r") as f:
            config = parse(f.read())
    if isinstance(obj, Configurable):
        return obj.configure(config)
    return True
