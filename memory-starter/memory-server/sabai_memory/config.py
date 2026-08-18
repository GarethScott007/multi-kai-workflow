"""Configuration: which dirs to index, where to persist, which embedding provider.

Everything comes from a JSON config file — there are NO baked-in source directories, because
the directories worth indexing are yours, not this package's. Resolution order:

  1. the path in the SABAI_MEMORY_CONFIG environment variable, if set;
  2. `sources.json` beside this package (i.e. the directory you cloned);
  3. `~/.claude/sabai-memory/sources.json`.

Copy `sources.example.json` to `sources.json` and edit it. Relative source paths resolve
against the config file's own directory, so the shipped example works from a fresh clone
with no edits at all.

Portable by construction: the same code runs against a different machine's directory layout —
or a different box entirely — by pointing it at a different config file.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

HOME = Path(os.path.expanduser("~"))
CLAUDE_DIR = HOME / ".claude"
PROJECTS_DIR = CLAUDE_DIR / "projects"
PACKAGE_ROOT = Path(__file__).resolve().parents[1]   # the dir containing sabai_memory/


class ConfigError(RuntimeError):
    """Raised when no usable config file can be found. Loud beats an index of nothing."""


@dataclass
class Source:
    """One indexed memory dir, tagged with a project name used for `project=` scoping."""
    name: str
    path: str


@dataclass
class Config:
    sources: list[Source]
    excludes: list[str]
    persist_dir: Path
    cache_dir: Path
    provider: str = "fastembed"
    model: str = "BAAI/bge-small-en-v1.5"
    model_ollama: str = "nomic-embed-text"
    ollama_host: str = "http://localhost:11434"
    debounce_seconds: float = 2.0


DEFAULT_EXCLUDES = [".git", ".obsidian", "node_modules", "*-backup-*", ".trash"]


def candidate_config_paths() -> list[Path]:
    """Every place a config file is looked for, in priority order."""
    paths: list[Path] = []
    env = os.environ.get("SABAI_MEMORY_CONFIG")
    if env:
        paths.append(Path(os.path.expanduser(env)))
    paths.append(PACKAGE_ROOT / "sources.json")
    paths.append(CLAUDE_DIR / "sabai-memory" / "sources.json")
    return paths


def find_config() -> Path:
    for p in candidate_config_paths():
        if p.is_file():
            return p
    looked = "\n  ".join(str(p) for p in candidate_config_paths())
    raise ConfigError(
        "sabai-memory: no config file found. Looked in:\n  " + looked +
        "\n\nCopy sources.example.json to sources.json (in the same directory as the "
        "sabai_memory package) and edit it, or point SABAI_MEMORY_CONFIG at your own file. "
        "See README.md -> 'Configure: sources.json'."
    )


def _resolve(path_str: str, base: Path) -> str:
    """Expand ~ and env vars; resolve a relative path against the CONFIG FILE's directory.

    Resolving against the config file rather than the process working directory is what lets
    the shipped example point at `../vault` and keep working regardless of where the server
    is launched from — and an MCP server is launched from wherever the client feels like.
    """
    expanded = os.path.expandvars(os.path.expanduser(path_str))
    p = Path(expanded)
    if not p.is_absolute():
        p = base / p
    return str(p.resolve())


def load_config() -> Config:
    cfg_path = find_config()
    base = cfg_path.parent
    data = json.loads(cfg_path.read_text(encoding="utf-8"))

    raw_sources = data.get("sources")
    if not raw_sources:
        raise ConfigError(
            f"sabai-memory: {cfg_path} has no non-empty 'sources' array. A server with nothing "
            "to index answers every search with silence, which is indistinguishable from a "
            "broken index — so this fails loudly instead of quietly."
        )
    sources = [Source(s["name"], _resolve(s["path"], base)) for s in raw_sources]

    excludes = data.get("excludes", list(DEFAULT_EXCLUDES))
    persist_dir = Path(_resolve(
        data.get("persist_dir", str(CLAUDE_DIR / "sabai-memory" / "index")), base))
    cache_dir = Path(_resolve(
        data.get("cache_dir", str(CLAUDE_DIR / "sabai-memory" / "fastembed-cache")), base))
    provider = data.get("provider", "fastembed")
    model = data.get("model", "BAAI/bge-small-en-v1.5")
    model_ollama = data.get("model_ollama", "nomic-embed-text")
    ollama_host = data.get("ollama_host", "http://localhost:11434")
    debounce = float(data.get("debounce_seconds", 2.0))

    # Make every source dir real so the watcher attaches from boot and is ready for the first
    # write — a project may not have written a memory yet, but recall there must be live the
    # moment it does. These are exactly the dirs Claude Code writes memories into.
    for s in sources:
        Path(s.path).mkdir(parents=True, exist_ok=True)
    persist_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    return Config(
        sources=sources,
        excludes=excludes,
        persist_dir=persist_dir,
        cache_dir=cache_dir,
        provider=provider,
        model=model,
        model_ollama=model_ollama,
        ollama_host=ollama_host,
        debounce_seconds=debounce,
    )
