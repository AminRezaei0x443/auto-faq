from abc import ABC, abstractmethod

from torch import Tensor


class BaseEmbedder(ABC):
    @abstractmethod
    def embed(sentences: list[str]) -> Tensor:
        pass
