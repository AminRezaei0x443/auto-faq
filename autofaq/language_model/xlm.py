from os import path

import numpy as np
import torch
from onnxruntime import ExecutionMode, InferenceSession, SessionOptions
from transformers import AutoTokenizer

# https://medium.com/microsoftazure/accelerate-your-nlp-pipelines-using-hugging-face-transformers-and-onnx-runtime-2443578f4333
# https://huggingface.co/transformers/serialization.html
# https://huggingface.co/sentence-transformers/paraphrase-xlm-r-multilingual-v1


# Mean Pooling - Take attention mask into account for correct averaging
def mean_pooling(token_embeddings, attention_mask):
    input_mask_expanded = (
        attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    )
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
        input_mask_expanded.sum(1), min=1e-9
    )


def openXLMSession(modelPath):
    tokenizer = AutoTokenizer.from_pretrained(modelPath, use_fast=True)
    options = SessionOptions()
    options.intra_op_num_threads = 1
    options.execution_mode = ExecutionMode.ORT_PARALLEL
    session = InferenceSession(
        path.join(modelPath, "xlm.onnx"),
        options,
        providers=[
            "TensorrtExecutionProvider",
            "CUDAExecutionProvider",
            "CPUExecutionProvider",
        ],
    )
    return {"session": session, "tokenizer": tokenizer}


def embedSentences(xlmSession, sentences):
    encoded_input = xlmSession["tokenizer"](
        sentences, padding=True, truncation=True, return_tensors="pt"
    )
    tokens = {name: np.atleast_2d(val) for name, val in encoded_input.items()}
    out1, out2 = xlmSession["session"].run(None, tokens)
    res = mean_pooling(torch.tensor(out1), encoded_input["attention_mask"])
    return res
