"""End-to-end MCP check: launch the server the way Claude Code will (stdio) and drive it
through the real protocol — initialize, list_tools, stats, search, and a LIVE freshness probe.

This is the fresh-eyes RUNTIME proof. The in-process smoke test can pass while the thing a
client actually talks to is broken, because the smoke test never crosses the stdio boundary —
the two checks are not redundant. Runtime > code-read applies to your own tooling too.

Run:  uv run python scripts/mcp_client_check.py
Exits non-zero on any failure.

The freshness probe writes ONE throwaway file into your FIRST configured source dir and deletes
it again in a finally-block. Out of the box that is the shipped example vault. If you have
repointed sources.json at your real memory dirs, know that this touches the first one.
"""
from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sabai_memory.config import load_config  # noqa: E402

# The MCP client does not activate a virtualenv — the interpreter path IS the environment.
# Prefer this project's venv; fall back to the interpreter running this script.
_VENV_CANDIDATES = [
    ROOT / ".venv" / "Scripts" / "python.exe",   # Windows
    ROOT / ".venv" / "bin" / "python",           # macOS / Linux
]
PY = next((p for p in _VENV_CANDIDATES if p.exists()), Path(sys.executable))

# The parity case must be answerable from whatever sources.json points at. Keep this in step
# with PARITY_CASES in scripts/smoke_test.py when you repoint at your own vault.
PARITY_QUERY = "which cloud region do we deploy to and why only one"
PARITY_EXPECT = "project_deploy_target_ruling"

RESULTS: list[tuple[bool, str]] = []


def check(ok: bool, label: str, detail: str = ""):
    RESULTS.append((ok, label))
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f"  ::  {detail}" if detail else ""), flush=True)


def extract(result):
    sc = getattr(result, "structuredContent", None)
    if isinstance(sc, dict):
        return sc.get("result", sc)
    for c in result.content:
        text = getattr(c, "text", None)
        if text:
            try:
                return json.loads(text)
            except Exception:
                return text
    return None


async def run(probe_dir: Path):
    params = StdioServerParameters(command=str(PY), args=["-m", "sabai_memory"], cwd=str(ROOT))
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await asyncio.wait_for(session.initialize(), timeout=120)

            tools = await session.list_tools()
            names = sorted(t.name for t in tools.tools)
            check(names == ["get_memory", "list_projects", "search_memory", "stats"],
                  "MCP: server connects + exposes exactly the 4 read tools", str(names))

            st = extract(await session.call_tool("stats", {}))
            # A green run over an EMPTY index would prove nothing, so the floor is a real one.
            check(bool(st.get("semantic_ready")) and st.get("files", 0) >= 1,
                  "MCP: stats reports semantic_ready over a non-empty index",
                  f"files={st.get('files')}, chunks={st.get('chunks')}, model={st.get('model')}")

            res = extract(await session.call_tool(
                "search_memory", {"query": PARITY_QUERY, "k": 5}))
            top = [r["name"] for r in res]
            check(PARITY_EXPECT in top,
                  "MCP: search_memory recall parity through the tool surface", f"top3={top[:3]}")

            # LIVE freshness through the real watcher (deliberately zero keyword overlap with
            # the query, so a lexical fallback could not produce a false pass).
            probe = probe_dir / "zz_mcp_freshness_probe.md"
            probe.write_text(
                "---\nname: zz_mcp_freshness_probe\ndescription: throwaway MCP freshness probe\n---\n"
                "# Probe\nThe team agreed the rooftop herb garden should be watered at dawn so the "
                "basil survives the dry season.\n",
                encoding="utf-8",
            )
            q = "morning irrigation for kitchen plants during drought"
            found_at = None
            deadline = time.time() + 12.0
            try:
                while time.time() < deadline:
                    hit = extract(await session.call_tool("search_memory", {"query": q, "k": 3}))
                    if any(r["name"] == "zz_mcp_freshness_probe" for r in hit):
                        found_at = round(12.0 - (deadline - time.time()), 2)
                        break
                    await asyncio.sleep(0.3)
                check(found_at is not None,
                      "MCP: LIVE freshness — a memory written right now surfaces via the tool in seconds",
                      f"surfaced_after~{found_at}s (zero-keyword query through MCP)")
            finally:
                # Always clean up: leaving the probe behind would pollute the vault it was
                # written into, and the next run's "deletion propagates" gate would be vacuous.
                if probe.exists():
                    probe.unlink()
                    await asyncio.sleep(3.0)
                    gone = extract(await session.call_tool("search_memory", {"query": q, "k": 3}))
                    check(not any(r["name"] == "zz_mcp_freshness_probe" for r in gone),
                          "MCP: deletion propagates — a removed memory drops out of recall",
                          f"top3_after_delete={[r['name'] for r in gone][:3]}")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    try:
        cfg = load_config()
    except Exception as exc:  # noqa: BLE001 - the config error message IS the instruction
        print(f"\nCONFIG ERROR\n{exc}\n", flush=True)
        sys.exit(2)

    probe_dir = Path(cfg.sources[0].path)
    print(f"  interpreter: {PY}", flush=True)
    print(f"  freshness probe will be written to: {probe_dir}", flush=True)

    asyncio.run(run(probe_dir))
    print("\n=== SUMMARY ===", flush=True)
    passed = sum(1 for ok, _ in RESULTS if ok)
    total = len(RESULTS)
    for ok, label in RESULTS:
        if not ok:
            print(f"  FAILED: {label}", flush=True)
    print(f"  {passed}/{total} MCP checks passed", flush=True)
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
