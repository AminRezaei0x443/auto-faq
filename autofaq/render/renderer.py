from abc import ABC, abstractmethod


class BaseRenderer(ABC):
    @abstractmethod
    def render(self, data: list[dict], out: str):
        pass
