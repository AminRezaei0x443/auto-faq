from autofaq.config.configurable import Configurable
from autofaq.language_model.embedder import BaseEmbedder
from autofaq.language_model.xlm import embedSentences, openXLMSession


class XLMEmbedder(BaseEmbedder, Configurable):
    def settings(self):
        return {
            "namespace": "embed.xlm",
            "model_path": (str, "MODEL_PATH", True, "xlm-r model path (onnx)"),
        }

    def on_bound(self):
        self.session = openXLMSession(self.config.model_path)

    def embed(self, sentences: list[str]):
        res = embedSentences(self.session, sentences)
        return res
