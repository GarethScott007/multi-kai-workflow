"""The owned FastMCP stdio server. Read-only by design — NO write/mutate tools.

Memories are written by Claude Code's native Write/Edit (the audited, visible path), same as
today. This server only ever reads them. Logs go to stderr so they never corrupt the stdio
JSON-RPC channel.
"""
from __future__ import annotations

import logging
import sys

from mcp.server.fastmcp import FastMCP

from .config import load_config
from .indexer import Indexer
from .watcher import MemoryWatcher

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="%(asctime)s sabai-memory %(levelname)s %(message)s",
)
log = logging.getLogger("sabai_memory")

mcp = FastMCP("sabai-memory")
_state: dict = {"indexer": None}


def _indexer() -> Indexer:
    ix = _state["indexer"]
    if ix is None:
        raise RuntimeError("sabai-memory index not initialised")
    return ix


@mcp.tool()
def search_memory(query: str, k: int = 8, project: str | None = None) -> list[dict]:
    """Semantic search over the partnership memory vault(s) by meaning, not keywords.

    Returns up to k chunks, each: {name, path, score, heading, snippet, project}.
    `project` scopes the search to ONE configured source by its name in sources.json
    (e.g. "my-app" or "_shared"); omit it to search across every indexed source.
    """
    results = _indexer().search(query, k=k, project=project)
    return [
        {
            "name": r["slug"],
            "path": r["file"],
            "score": r["score"],
            "heading": r["heading"],
            "snippet": r["snippet"],
            "project": r["project"],
        }
        for r in results
    ]


@mcp.tool()
def get_memory(name: str) -> dict:
    """Fetch a full memory file by its slug/name (e.g. "reference_agoda_verification")."""
    res = _indexer().get_memory(name)
    if res is None:
        return {"found": False, "name": name}
    return {"found": True, **res}


@mcp.tool()
def list_projects() -> list[dict]:
    """List indexed memory sources with file + chunk counts."""
    return _indexer().store.projects()


@mcp.tool()
def stats() -> dict:
    """Index stats: files, chunks, embedding provider/model, dim, and semantic_ready."""
    ix = _indexer()
    files, chunks = ix.store.counts()
    return {
        "files": files,
        "chunks": chunks,
        "semantic_ready": chunks > 0,
        "provider": ix.config.provider,
        "model": ix.provider_id,
        "dim": ix.provider.dim,
        "sources": [s.name for s in ix.config.sources],
    }


def main():
    cfg = load_config()
    log.info("booting: provider=%s, %d source(s)", cfg.provider, len(cfg.sources))
    ix = Indexer(cfg)
    ix.reconcile()  # load persisted index + re-embed only what changed since last run
    _state["indexer"] = ix
    MemoryWatcher(ix, cfg.debounce_seconds).start()
    files, chunks = ix.store.counts()
    log.info("ready: %d file(s) / %d chunk(s) indexed", files, chunks)
    mcp.run()


if __name__ == "__main__":
    main()
