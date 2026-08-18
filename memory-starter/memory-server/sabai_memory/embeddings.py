"""Embedding providers. Both are fully local — no cloud key, nothing leaves the machine.

FastEmbed (default, tested): ONNX bge-small-en-v1.5 — downloads once, then fully offline.
Ollama (optional, less tested): nomic-embed-text over Ollama's local HTTP API.

All vectors are L2-normalized so cosine similarity is a plain dot product.
Retrieval models are asymmetric: queries and documents get different handling
(bge's query instruction / nomic's search_query/search_document prefixes).
"""
from __future__ import annotations

import json
import urllib.request

import numpy as np


def _l2_normalize(mat: np.ndarray) -> np.ndarray:
    mat = np.asarray(mat, dtype=np.float32)
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return (mat / norms).astype(np.float32)


class EmbeddingProvider:
    dim: int

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        raise NotImplementedError

    def embed_query(self, text: str) -> np.ndarray:
        raise NotImplementedError


class FastEmbedProvider(EmbeddingProvider):
    def __init__(self, model_name: str, cache_dir):
        from fastembed import TextEmbedding  # imported lazily so the module loads without it

        self.model_name = model_name
        self._model = TextEmbedding(model_name=model_name, cache_dir=str(cache_dir))
        probe = next(iter(self._model.embed(["dimension probe"])))
        self.dim = int(np.asarray(probe).shape[-1])

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dim), dtype=np.float32)
        vecs = np.asarray(list(self._model.embed(list(texts))), dtype=np.float32)
        return _l2_normalize(vecs)

    def embed_query(self, text: str) -> np.ndarray:
        # query_embed prepends bge's retrieval instruction; fall back to embed if unavailable.
        fn = getattr(self._model, "query_embed", None) or self._model.embed
        vec = np.asarray(list(fn([text]))[0], dtype=np.float32).reshape(1, -1)
        return _l2_normalize(vec)[0]


class OllamaProvider(EmbeddingProvider):
    def __init__(self, model_name: str = "nomic-embed-text", host: str = "http://localhost:11434"):
        self.model_name = model_name
        self.host = host.rstrip("/")
        self.dim = int(self._embed_one("search_document: dimension probe").shape[0])

    def _embed_one(self, prompt: str) -> np.ndarray:
        req = urllib.request.Request(
            self.host + "/api/embeddings",
            data=json.dumps({"model": self.model_name, "prompt": prompt}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        v = np.asarray(data["embedding"], dtype=np.float32)
        n = float(np.linalg.norm(v))
        return (v / n if n else v).astype(np.float32)

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dim), dtype=np.float32)
        return np.vstack([self._embed_one("search_document: " + t) for t in texts]).astype(np.float32)

    def embed_query(self, text: str) -> np.ndarray:
        return self._embed_one("search_query: " + text)


def get_provider(config) -> EmbeddingProvider:
    if config.provider == "ollama":
        return OllamaProvider(config.model_ollama, config.ollama_host)
    return FastEmbedProvider(config.model, config.cache_dir)
