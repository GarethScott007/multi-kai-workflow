"""Markdown -> chunks. Split by heading (H1-H4), plus a summary chunk from frontmatter.

Frontmatter-resilient by design: a parse error (e.g. an unquoted colon in a `description:`)
NEVER drops the file. We log, salvage name/description by regex, and index the body anyway.
This is the exact failure that made markdown-vault-mcp silently lose 4 memories.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass

log = logging.getLogger("sabai_memory")

_HEADING = re.compile(r"^(#{1,4})\s+(.*\S)\s*$")
_FM_FENCE = re.compile(r"^﻿?---\s*\n.*?\n---\s*\n", re.DOTALL)
_NAME_LINE = re.compile(r"^\s*name:\s*(.+?)\s*$", re.MULTILINE)
_DESC_LINE = re.compile(r"^\s*description:\s*(.+?)\s*$", re.MULTILINE)


@dataclass
class Chunk:
    heading: str
    text: str


def parse_frontmatter(raw: str) -> tuple[dict, str, bool]:
    """Return (meta, body, ok). Never raises. On bad YAML, ok=False, meta={}, body=raw minus fence."""
    try:
        import frontmatter

        post = frontmatter.loads(raw)
        meta = dict(post.metadata) if post.metadata else {}
        return meta, post.content, True
    except Exception as exc:  # noqa: BLE001 - resilience is the whole point
        log.warning("frontmatter parse failed (indexing body anyway): %s", exc)
        body = _FM_FENCE.sub("", raw, count=1)
        return {}, body, False


def _salvage_field(raw: str, pattern: re.Pattern) -> str:
    m = pattern.search(raw)
    if not m:
        return ""
    return m.group(1).strip().strip("\"'")


def split_sections(body: str) -> list[Chunk]:
    chunks: list[Chunk] = []
    stack: list[tuple[int, str]] = []
    cur_heading = ""
    buf: list[str] = []

    def flush():
        text = "\n".join(buf).strip()
        if text:
            chunks.append(Chunk(cur_heading or "(body)", text))

    for line in body.splitlines():
        m = _HEADING.match(line)
        if m:
            flush()
            buf = []
            level = len(m.group(1))
            title = m.group(2).strip()
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, title))
            cur_heading = " > ".join(t for _, t in stack)
        buf.append(line)
    flush()
    return chunks


def chunk_file(raw: str) -> list[Chunk]:
    meta, body, _ok = parse_frontmatter(raw)
    name = str(meta.get("name") or _salvage_field(raw, _NAME_LINE))
    desc = str(meta.get("description") or _salvage_field(raw, _DESC_LINE))

    chunks: list[Chunk] = []
    summary = "\n".join(p for p in (name, desc) if p).strip()
    if summary:
        chunks.append(Chunk("(summary)", summary))
    chunks.extend(split_sections(body))
    return chunks
