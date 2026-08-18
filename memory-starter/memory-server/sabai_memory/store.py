"""Flat numpy + cosine vector store. Every line ours, no native DB, trivially portable.

At hundreds-to-thousands of chunks a brute-force dot product is microseconds, so there is no
reason to take on LanceDB/Chroma native-build risk (which bites hardest on Windows). Persisted
as vectors.npy + meta.json, keyed by source-file SHA so a restart re-embeds only what changed.

Thread-safe: the watcher thread mutates while the server thread searches.
"""
from __future__ import annotations

import json
import threading
from pathlib import Path

import numpy as np


class VectorStore:
    def __init__(self, dim: int, provider_id: str):
        self.dim = dim
        self.provider_id = provider_id  # e.g. "fastembed:BAAI/bge-small-en-v1.5"
        self._lock = threading.RLock()
        self._metas: list[dict] = []          # per-chunk metadata
        self._vecs: list[np.ndarray] = []      # per-chunk vector [dim]
        self._file_hashes: dict[str, str] = {}  # file -> content SHA (for reconcile)
        self._matrix: np.ndarray | None = None
        self._matrix_dirty = True

    def _invalidate(self):
        self._matrix = None
        self._matrix_dirty = True

    def file_hash(self, file: str) -> str | None:
        with self._lock:
            return self._file_hashes.get(file)

    def known_files(self) -> set[str]:
        with self._lock:
            return set(self._file_hashes.keys())

    def remove_file(self, file: str):
        with self._lock:
            if file not in self._file_hashes and not any(m["file"] == file for m in self._metas):
                return
            keep_m, keep_v = [], []
            for m, v in zip(self._metas, self._vecs):
                if m["file"] != file:
                    keep_m.append(m)
                    keep_v.append(v)
            self._metas, self._vecs = keep_m, keep_v
            self._file_hashes.pop(file, None)
            self._invalidate()

    def add_file(self, file: str, file_hash: str, metas: list[dict], vecs):
        with self._lock:
            self.remove_file(file)  # idempotent upsert
            for m, v in zip(metas, vecs):
                self._metas.append(m)
                self._vecs.append(np.asarray(v, dtype=np.float32))
            self._file_hashes[file] = file_hash
            self._invalidate()

    def _ensure_matrix(self):
        if self._matrix is None or self._matrix_dirty:
            self._matrix = (
                np.vstack(self._vecs).astype(np.float32)
                if self._vecs
                else np.zeros((0, self.dim), dtype=np.float32)
            )
            self._matrix_dirty = False

    def search(self, qvec, k: int = 8, project: str | None = None) -> list[dict]:
        with self._lock:
            self._ensure_matrix()
            if self._matrix.shape[0] == 0:
                return []
            sims = self._matrix @ np.asarray(qvec, dtype=np.float32)
            if project:
                cand = [i for i, m in enumerate(self._metas) if m["project"] == project]
            else:
                cand = list(range(len(self._metas)))
            if not cand:
                return []
            cand.sort(key=lambda i: sims[i], reverse=True)
            return [{**self._metas[i], "score": round(float(sims[i]), 4)} for i in cand[:k]]

    def counts(self) -> tuple[int, int]:
        with self._lock:
            return len(self._file_hashes), len(self._metas)

    def projects(self) -> list[dict]:
        with self._lock:
            agg: dict[str, dict] = {}
            for m in self._metas:
                d = agg.setdefault(m["project"], {"files": set(), "chunks": 0})
                d["files"].add(m["file"])
                d["chunks"] += 1
            return [
                {"project": k, "files": len(v["files"]), "chunks": v["chunks"]}
                for k, v in sorted(agg.items())
            ]

    def persist(self, dirpath):
        with self._lock:
            self._ensure_matrix()
            dirpath = Path(dirpath)
            dirpath.mkdir(parents=True, exist_ok=True)
            # write to temp then replace, so a crash mid-write can't corrupt the index
            tmp_vec = dirpath / "vectors.npy.tmp"
            tmp_meta = dirpath / "meta.json.tmp"
            np.save(tmp_vec, self._matrix)
            payload = {
                "dim": self.dim,
                "provider_id": self.provider_id,
                "metas": self._metas,
                "file_hashes": self._file_hashes,
            }
            tmp_meta.write_text(json.dumps(payload), encoding="utf-8")
            # np.save appends .npy to the temp name
            (dirpath / "vectors.npy.tmp.npy").replace(dirpath / "vectors.npy")
            tmp_meta.replace(dirpath / "meta.json")

    @classmethod
    def load(cls, dirpath, dim: int, provider_id: str) -> "VectorStore":
        dirpath = Path(dirpath)
        mp, vp = dirpath / "meta.json", dirpath / "vectors.npy"
        if not mp.exists() or not vp.exists():
            return cls(dim, provider_id)
        payload = json.loads(mp.read_text(encoding="utf-8"))
        # provider/model/dim changed -> discard, force a clean rebuild
        if payload.get("dim") != dim or payload.get("provider_id") != provider_id:
            return cls(dim, provider_id)
        store = cls(dim, provider_id)
        mat = np.load(vp)
        store._metas = payload["metas"]
        store._file_hashes = payload["file_hashes"]
        store._vecs = [mat[i] for i in range(mat.shape[0])]
        store._invalidate()
        return store
