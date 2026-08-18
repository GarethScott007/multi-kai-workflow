"""The engine: walk source dirs, chunk + embed files, keep the store reconciled with disk.

Reconcile is SHA-based: on boot we load the persisted store and re-embed only files whose
content hash changed (or are new), and drop files that vanished. That is what makes restart
fast and what — together with the watcher — keeps recall fresh.
"""
from __future__ import annotations

import hashlib
import logging
from fnmatch import fnmatch
from pathlib import Path

from .chunking import Chunk, chunk_file
from .config import Config
from .embeddings import get_provider
from .store import VectorStore

log = logging.getLogger("sabai_memory")


class Indexer:
    def __init__(self, config: Config):
        self.config = config
        self.provider = get_provider(config)
        model_id = config.model if config.provider == "fastembed" else config.model_ollama
        self.provider_id = f"{config.provider}:{model_id}"
        self.store = VectorStore.load(config.persist_dir, self.provider.dim, self.provider_id)
        self._source_roots = [(Path(s.path).resolve(), s.name) for s in config.sources]

    def _project_for(self, path: Path) -> str:
        p = path.resolve()
        for root, name in self._source_roots:
            try:
                p.relative_to(root)
                return name
            except ValueError:
                continue
        return "unknown"

    def is_excluded(self, path: Path) -> bool:
        return any(fnmatch(part, pat) for part in path.parts for pat in self.config.excludes)

    @staticmethod
    def file_sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def iter_files(self):
        for source_root, name in self._source_roots:
            if not source_root.exists():
                log.warning("source dir missing, skipping: %s", source_root)
                continue
            for f in source_root.rglob("*.md"):
                if f.is_file() and not self.is_excluded(f):
                    yield f, name

    def index_file(self, path: Path, project: str | None = None):
        project = project or self._project_for(path)
        try:
            raw = path.read_text(encoding="utf-8")
        except Exception as exc:  # noqa: BLE001
            log.warning("read failed %s: %s", path, exc)
            return
        chunks = chunk_file(raw)
        if not chunks:  # never silently drop a file — index at least its slug
            chunks = [Chunk("(empty)", path.stem)]
        slug = path.stem
        vecs = self.provider.embed_documents([c.text for c in chunks])
        metas = [
            {
                "file": str(path),
                "project": project,
                "slug": slug,
                "heading": c.heading,
                "snippet": c.text.strip().replace("\n", " ")[:280],
            }
            for c in chunks
        ]
        self.store.add_file(str(path), self.file_sha(path), metas, vecs)

    def reconcile(self):
        """Boot-time + on-demand: re-embed only changed/new files, drop deleted ones."""
        seen: set[str] = set()
        changed = 0
        for f, project in self.iter_files():
            fp = str(f)
            seen.add(fp)
            if self.store.file_hash(fp) == self.file_sha(f):
                continue
            self.index_file(f, project)
            changed += 1
        for known in self.store.known_files():
            if known not in seen:
                self.store.remove_file(known)
        self.store.persist(self.config.persist_dir)
        log.info("reconcile: %d file(s) re-embedded", changed)
        return changed

    def handle_change(self, path: Path):
        """Single-file update fired by the watcher (already debounced)."""
        if path.suffix.lower() != ".md" or self.is_excluded(path):
            return
        if not path.exists():
            self.store.remove_file(str(path))
            log.info("watcher: removed %s", path.name)
        else:
            if self.store.file_hash(str(path)) == self.file_sha(path):
                return  # event fired but content unchanged
            self.index_file(path)
            log.info("watcher: re-embedded %s", path.name)
        self.store.persist(self.config.persist_dir)

    def search(self, query: str, k: int = 8, project: str | None = None) -> list[dict]:
        return self.store.search(self.provider.embed_query(query), k=k, project=project)

    def get_memory(self, name: str) -> dict | None:
        for known in self.store.known_files():
            p = Path(known)
            if p.stem == name:
                return {
                    "name": name,
                    "path": known,
                    "project": self._project_for(p),
                    "content": p.read_text(encoding="utf-8"),
                }
        return None
