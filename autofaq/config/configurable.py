from abc import ABC, abstractmethod
from types import SimpleNamespace

from autofaq.util.out import sprint


class Configurable(ABC):
    def __init__(self):
        self.config = SimpleNamespace()

    @abstractmethod
    def settings(self) -> dict:
        """
        This method should return a dict showing the config of this object
        {
            "namespace": "namespace",
            "var": (type, default, required, hint)
        }
        """
        pass

    def configure(self, config: dict):
        settings = self.settings()
        namespace = settings.pop("namespace", "")
        for k, v in settings.items():
            if namespace:
                k = f"{namespace}.{k}"
            type_, def_, req_, hint_ = v
            ok = self.read_key(config, k, default=def_, required=req_, type_=type_)
            if not ok:
                return False
        return True

    @classmethod
    def _nested_get(cls, d: dict, path: list):
        r = d
        path = path.copy()
        while len(path) != 0:
            k = path.pop(0)
            if k in r:
                r = r[k]
            else:
                return None
        return r

    def read_key(
        self, config: dict, key: str, default=None, required=False, type_=None
    ):
        path = key.split(".")
        value = self._nested_get(config, path)
        if value is None and required:
            sprint(
                "You must provide a value for @key key in your config!",
                fg="red",
                key=(key, "white", "bold"),
            )
            return False
        if value is None:
            value = default
        else:
            if type_:
                value = type_(value)
        setattr(self.config, path[-1], value)
        return True
