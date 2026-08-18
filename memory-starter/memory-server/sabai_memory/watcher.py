"""THE freshness fix. A watchdog Observer over the source dirs, debounced, re-embeds on change.

This is the property markdown-vault-mcp lacked: a memory written this session is semantically
searchable within seconds, no manual reindex. Events coalesce over a short debounce window
(rapid editor saves -> one flush); the indexer's SHA check then skips no-op events.
"""
from __future__ import annotations

import logging
import threading
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

log = logging.getLogger("sabai_memory")


class _Handler(FileSystemEventHandler):
    def __init__(self, watcher: "MemoryWatcher"):
        self._w = watcher

    def on_any_event(self, event):
        if event.is_directory:
            return
        for attr in ("src_path", "dest_path"):
            p = getattr(event, attr, None)
            if p and str(p).lower().endswith(".md"):
                self._w.schedule(str(p))


class MemoryWatcher:
    def __init__(self, indexer, debounce_seconds: float = 2.0):
        self.indexer = indexer
        self.debounce = debounce_seconds
        self._observer = Observer()
        self._pending: set[str] = set()
        self._lock = threading.Lock()
        self._timer: threading.Timer | None = None

    def schedule(self, path: str):
        with self._lock:
            self._pending.add(path)
            if self._timer:
                self._timer.cancel()
            self._timer = threading.Timer(self.debounce, self._flush)
            self._timer.daemon = True
            self._timer.start()

    def _flush(self):
        with self._lock:
            batch = list(self._pending)
            self._pending.clear()
            self._timer = None
        for p in batch:
            try:
                self.indexer.handle_change(Path(p))
            except Exception as exc:  # noqa: BLE001 - one bad file must not kill the watcher
                log.warning("watcher reindex failed for %s: %s", p, exc)

    def start(self):
        watched = 0
        for source in self.indexer.config.sources:
            root = Path(source.path)
            if not root.exists():
                continue
            self._observer.schedule(_Handler(self), str(root), recursive=True)
            watched += 1
        self._observer.daemon = True
        self._observer.start()
        log.info("watcher started over %d dir(s), debounce=%.1fs", watched, self.debounce)

    def stop(self):
        if self._timer:
            self._timer.cancel()
        self._observer.stop()
        self._observer.join(timeout=5)
