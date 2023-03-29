import json
from json import JSONEncoder

import torch

from autofaq.render.renderer import BaseRenderer


class TEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, torch.Tensor):
            return o.item()
        return o.__dict__


class JSONRenderer(BaseRenderer):
    def render(self, data: list[dict], out: str):
        pt = f"{out}.json"
        with open(pt, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=4, cls=TEncoder)
        return pt
