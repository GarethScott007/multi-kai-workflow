"""Smoke test — proves every gate this server claims, especially FRESHNESS.

Run:  uv run python scripts/smoke_test.py
Exits non-zero if any gate fails.

Part A runs entirely on throwaway temp dirs — deterministic, and it never touches your vault.
Part B runs recall parity against whatever `sources.json` points at, and as a side effect builds
the index the server will load at boot. Out of the box `sources.json` points at the shipped
example vault (memory-starter/vault), so Part B passes on a fresh clone with no vault of your
own; once you repoint it at your real memory dirs, swap the PARITY_CASES below for two queries
whose answers you know.
"""
from __future__ import annotations

import socket
import sys
import tempfile
import time
from pathlib import Path

# make the package importable when run as a script
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Windows consoles default to cp1252; force UTF-8 so output never crashes on a stray glyph.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

from sabai_memory.config import Config, Source, load_config  # noqa: E402
from sabai_memory.indexer import Indexer  # noqa: E402
from sabai_memory.watcher import MemoryWatcher  # noqa: E402

RESULTS: list[tuple[bool, str]] = []


def check(ok: bool, label: str, detail: str = ""):
    RESULTS.append((ok, label))
    mark = "PASS" if ok else "FAIL"
    line = f"  [{mark}] {label}"
    if detail:
        line += f"  ::  {detail}"
    print(line, flush=True)


def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def slugs(results: list[dict]) -> list[str]:
    return [r["slug"] for r in results]


# --------------------------------------------------------------------------------------
# PART A — isolated mechanism tests on temp dirs
# --------------------------------------------------------------------------------------
def part_a(cache_dir: Path):
    print("\n=== PART A — mechanism (temp dirs) ===", flush=True)
    root = Path(tempfile.mkdtemp(prefix="sabai-smoke-"))
    a_dir = root / "alpha"
    b_dir = root / "beta"
    persist = root / "index"

    write(a_dir / "alpha_flights.md", (
        "---\nname: alpha_flights\ndescription: Flight filter chips and sort order\n---\n"
        "# Flights\nUsers narrow airline results with departure-time chips and sort by price.\n"
    ))
    # Frontmatter resilience: UNQUOTED colon-space in description breaks YAML.
    write(a_dir / "alpha_currency_note.md", (
        "---\nname: alpha_currency_note\ndescription: Critical constraint: never hardcode FX rates\n---\n"
        "# Currency\nExchange rates are fetched from a live source every session, never hardcoded.\n"
    ))
    write(b_dir / "beta_hotels.md", (
        "---\nname: beta_hotels\ndescription: Hotel affiliate booking links\n---\n"
        "# Hotels\nAccommodation deep links route through the affiliate partner with the locale param.\n"
    ))

    cfg = Config(
        sources=[Source("alpha", str(a_dir)), Source("beta", str(b_dir))],
        excludes=[".git", ".obsidian"],
        persist_dir=persist,
        cache_dir=cache_dir,
    )
    ix = Indexer(cfg)
    ix.reconcile()

    # Gate: frontmatter resilience (no silent skip on bad YAML)
    known = {Path(f).stem for f in ix.store.known_files()}
    check("alpha_currency_note" in known, "frontmatter resilience: bad-YAML file still indexed",
          f"indexed files include alpha_currency_note: {'alpha_currency_note' in known}")

    # Gate: scoping
    res_all = ix.search("airline departure time filtering controls", k=5)
    res_alpha = ix.search("airline departure time filtering controls", k=5, project="alpha")
    res_beta = ix.search("airline departure time filtering controls", k=5, project="beta")
    check("alpha_flights" in slugs(res_all), "scoping: unscoped search spans all", str(slugs(res_all)[:3]))
    check("alpha_flights" in slugs(res_alpha), "scoping: project=alpha includes alpha hit", str(slugs(res_alpha)[:3]))
    check(all(r["project"] == "beta" for r in res_beta) and "alpha_flights" not in slugs(res_beta),
          "scoping: project=beta excludes alpha", str(slugs(res_beta)[:3]))

    # Gate: FRESHNESS — write a NEW memory live, query with ZERO keyword overlap, expect <5s surfacing
    watcher = MemoryWatcher(ix, debounce_seconds=2.0)
    watcher.start()
    fresh_query = "coffee maker limescale maintenance schedule"
    pre = slugs(ix.search(fresh_query, k=3))
    write(a_dir / "alpha_fresh.md", (
        "---\nname: alpha_fresh\ndescription: Studio espresso machine upkeep cadence\n---\n"
        "# Espresso upkeep\nWe agreed the Chiang Mai studio espresso machine should be descaled "
        "every fortnight to keep its boiler healthy.\n"
    ))
    deadline = time.time() + 8.0
    found_at = None
    while time.time() < deadline:
        if "alpha_fresh" in slugs(ix.search(fresh_query, k=3)):
            found_at = round(time.time() - (deadline - 8.0), 2)
            break
        time.sleep(0.25)
    check(found_at is not None,
          "FRESHNESS: live-written memory semantically searchable within seconds (the markdown-vault-mcp gap)",
          f"pre={pre} surfaced_after~{found_at}s (zero-keyword query)")
    watcher.stop()

    # Gate: fully-local read path — block all sockets, search must still work
    real_socket = socket.socket

    def _blocked(*a, **k):  # noqa: ANN002, ANN003
        raise OSError("network blocked by smoke test")

    socket.socket = _blocked  # type: ignore[assignment]
    try:
        offline = slugs(ix.search("airline departure time filtering controls", k=3))
        check("alpha_flights" in offline, "fully local: search works with sockets blocked (no cloud in read path)",
              str(offline))
    finally:
        socket.socket = real_socket  # type: ignore[assignment]

    # Gate: read-only — searches/gets must not mutate files on disk
    target = a_dir / "alpha_flights.md"
    before = target.read_bytes()
    ix.search("airline departure time filtering controls", k=3)
    ix.get_memory("alpha_flights")
    check(target.read_bytes() == before, "read-only: file bytes unchanged after search + get")

    # Gate: read-only — server exposes only the 4 read tools, nothing that mutates
    try:
        from sabai_memory.server import mcp
        tool_names = {t.name for t in mcp._tool_manager.list_tools()}  # type: ignore[attr-defined]
        mutating = {"create", "write", "update", "delete", "set", "put", "add", "remove"}
        no_writers = not any(any(v in n.lower() for v in mutating) for n in tool_names)
        check(tool_names == {"search_memory", "get_memory", "list_projects", "stats"} and no_writers,
              "read-only: only 4 read tools registered, none mutate", str(sorted(tool_names)))
    except Exception as exc:  # noqa: BLE001
        check(False, "read-only: tool introspection", f"could not introspect: {exc}")

    # Gate: restart — persisted index loads + reconciles with 0 re-embeds
    watcher = None
    ix2 = Indexer(cfg)
    t0 = time.time()
    changed = ix2.reconcile()
    load_secs = round(time.time() - t0, 2)
    files2, chunks2 = ix2.store.counts()
    check(changed == 0 and chunks2 > 0,
          "restart: persisted index reloads with 0 re-embeds (no full rebuild)",
          f"re-embedded={changed}, files={files2}, chunks={chunks2}, reconcile={load_secs}s")


# --------------------------------------------------------------------------------------
# PART B — recall parity over YOUR configured sources (also builds the boot index)
# --------------------------------------------------------------------------------------
#
# Each case is (query typed the way a human would, slug that MUST come back in the top k).
# These two are answerable from the shipped example vault. When you repoint sources.json at
# your own memory dirs, replace them with two of your own — a parity case is the cheapest
# possible regression test on the thing that actually matters: can recall find the answer?
#
# Note the queries deliberately share almost no literal words with their target files. That is
# the point: a lexical match would prove nothing about semantic recall.
PARITY_CASES = [
    ("which cloud region do we deploy to and why only one", "project_deploy_target_ruling"),
    ("is it safe to trust what the model remembers about a third party API",
     "feedback_verify_before_asserting"),
]


def part_b():
    print("\n=== PART B — recall parity (your configured sources) ===", flush=True)
    cfg = load_config()
    print(f"  sources: {[(s.name, s.path) for s in cfg.sources]}", flush=True)
    ix = Indexer(cfg)
    t0 = time.time()
    changed = ix.reconcile()
    files, chunks = ix.store.counts()
    print(f"  built boot index: {files} files / {chunks} chunks, re-embedded {changed} "
          f"in {round(time.time() - t0, 1)}s", flush=True)

    # Non-vacuity: parity cases over an empty index would all "fail" for the wrong reason,
    # and a green run over 0 files would be meaningless. Assert there is something to search.
    check(files > 0 and chunks > 0,
          "index non-vacuity: configured sources contain at least one indexable memory",
          f"files={files}, chunks={chunks}")

    for query, expected in PARITY_CASES:
        top = ix.search(query, k=8)
        names = slugs(top)
        rank = names.index(expected) + 1 if expected in names else None
        check(expected in names, f"recall parity: '{query[:38]}...' -> {expected}",
              f"rank={rank}, top3={names[:3]}")


def main():
    try:
        cfg = load_config()
    except Exception as exc:  # noqa: BLE001 - the config error message IS the instruction
        print(f"\nCONFIG ERROR\n{exc}\n", flush=True)
        sys.exit(2)
    part_a(cfg.cache_dir)
    part_b()

    print("\n=== SUMMARY ===", flush=True)
    passed = sum(1 for ok, _ in RESULTS if ok)
    total = len(RESULTS)
    for ok, label in RESULTS:
        if not ok:
            print(f"  FAILED: {label}", flush=True)
    print(f"  {passed}/{total} gates passed", flush=True)
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
