# sabai-memory — an owned, fully-local semantic recall layer over your memory vault

A small MCP (stdio) server that indexes your Claude Code memory directories and serves recall **by
meaning**, not by the hand-maintained `MEMORY.md` index. Every line of it is in this directory:
**no third party sits in the read path of your memory**, no cloud key, nothing leaves the machine.

> **About the name.** It is called `sabai-memory` because it was built for a project called
> SabaiFly. Nothing in it is SabaiFly-specific — the name is just provenance. Rename it if you
> like; if you do, rename the package directory, the `[project] name` in `pyproject.toml`, and
> whatever you pass to `claude mcp add`.

**Read-only by design — there are no write tools.** Memories are written by Claude Code's own
Write/Edit (the audited, visible path); this server only ever reads them.

| Tool | Returns |
|---|---|
| `search_memory(query, k=8, project=None)` | top-k chunks: `{name, path, score, heading, snippet, project}` |
| `get_memory(name)` | the full file, by slug |
| `list_projects()` | indexed sources with file + chunk counts |
| `stats()` | counts, provider/model, dimensions, `semantic_ready` |

---

## Why you want this

`MEMORY.md` is auto-loaded but truncated, and it is an *index* — one line per memory. It tells a
session that something exists; it cannot tell a session what it says. Past roughly thirty memories a
hand-maintained index stops being a recall mechanism and becomes a table of contents nobody reads.

Semantic search fixes that, but only if it is **fresh**: a memory written this session must be
findable this session, or the discipline of "capture as decisions land" quietly buys you nothing
until the next reindex. This server watches the source directories and re-embeds within about two
seconds of a write. That freshness property is the main reason it exists.

---

## Install

Requires **Python 3.11+**. [`uv`](https://docs.astral.sh/uv/) is recommended but optional.

**Windows (PowerShell)** — run installs from PowerShell, not from Git Bash/MSYS. A POSIX-emulation
shell on Windows can write package metadata that the native runtime cannot resolve, while the
wrappers still exit 0 — a failure that only surfaces much later, somewhere unrelated:

```powershell
cd <your-clone>\memory-starter\memory-server
uv venv
uv pip install -e .
```

**macOS / Linux:**

```bash
cd <your-clone>/memory-starter/memory-server
uv venv
uv pip install -e .
```

<details>
<summary>Without <code>uv</code> (stdlib venv + pip)</summary>

```powershell
# Windows
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

```bash
# macOS / Linux
python3 -m venv .venv
./.venv/bin/python -m pip install -e .
```
</details>

The first run downloads the embedding model (~90 MB) into your cache directory. After that the
server is fully offline — the smoke test proves it by searching with all sockets blocked.

---

## Configure: `sources.json`

There are **no baked-in source directories**. Copy the example and edit it:

```powershell
copy sources.example.json sources.json      # Windows
```
```bash
cp sources.example.json sources.json        # macOS / Linux
```

The shipped example points at this repo's **example vault** (`memory-starter/vault`), so it works on
a fresh clone with no edits at all — which is what makes the smoke test below runnable before you
have a vault of your own.

Relative paths resolve against **`sources.json`'s own directory**, not the process working
directory. That matters because an MCP client launches the server from wherever it likes, so `cwd`
is not something you can depend on.

Point it at your real memory dirs when you have them:

```jsonc
{
  "sources": [
    { "name": "my-app",  "path": "~/.claude/projects/<encoded-project-path>/memory" },
    { "name": "_shared", "path": "~/.claude/memory-shared" }
  ],
  "excludes": [".git", ".obsidian", "node_modules", "*-backup-*", ".trash"],
  "provider": "fastembed",
  "persist_dir": "~/.claude/sabai-memory/index",
  "cache_dir": "~/.claude/sabai-memory/fastembed-cache"
}
```

- **`name`** is what you pass as `project=` to scope a search. Keep it short and typeable.
- **Finding `<encoded-project-path>`:** ask Claude Code, inside that project, *"what is the absolute
  path to my memory directory?"* It is derived from the project's absolute path with the separators
  replaced. `docs/GETTING-STARTED.md` has the long version.
- **`sources.json` is gitignored** — it names your machine's directories.
- **Add each new project's memory dir here** as you create it, then restart Claude Code once. This
  is step 3 of `playbooks/playbook_new_project_bootstrap.md`; skip it and the new project's memories
  get written but are never searchable — the worst of both worlds.

If no config file is found the server **fails loudly**, printing every path it looked in. That is
deliberate: a server that silently indexes nothing answers every search with silence, and silence is
indistinguishable from "there is no such memory."

---

## Prove it works, before you register it

Build the index and run every gate:

```powershell
uv run python scripts/smoke_test.py
```

**Part A** runs on throwaway temp dirs and proves the mechanism: frontmatter resilience (bad YAML
never silently drops a file), project scoping, **freshness** (a memory written mid-run surfaces to a
zero-keyword query within seconds), fully-local operation (search with all sockets blocked),
read-only behaviour, and a fast restart with zero re-embeds.

**Part B** runs recall parity over whatever `sources.json` points at — and as a side effect **builds
the index the server loads at boot**. Doing that now means the first MCP launch is fast and never
trips your client's startup timeout.

Then the runtime proof — the server driven through the **real MCP protocol** over stdio, exactly as
a client does:

```powershell
uv run python scripts/mcp_client_check.py
```

These two are not redundant. The in-process smoke test can pass while the thing a client actually
talks to is broken, because it never crosses the stdio boundary. Runtime beats code-read for your
own tooling too.

---

## Register with Claude Code (user scope)

Register at **user** scope so recall spans every project. Use the venv's own interpreter — the MCP
client does not activate a virtualenv, so **the interpreter path IS the environment selection**:

```powershell
# Windows
claude mcp add --scope user sabai-memory -- "<your-clone>\memory-starter\memory-server\.venv\Scripts\python.exe" -m sabai_memory
```
```bash
# macOS / Linux
claude mcp add --scope user sabai-memory -- "<your-clone>/memory-starter/memory-server/.venv/bin/python" -m sabai_memory
```

Verify, then restart Claude Code (MCP servers load at session start):

```bash
claude mcp list
claude mcp get sabai-memory     # expect: Connected
```

`mcp.json.example` carries the equivalent hand-edited block.

### Two gotchas that cost real time

1. **A user-scope registration does not live in any repo.** It lives in **`~/.claude.json`** — not
   in a project `.mcp.json`, not in `settings.json`. People look for it in the project, don't find
   it, and register a second project-scoped copy — then wonder why one window has recall and
   another doesn't. If the server ever seems to vanish: `claude mcp list` first, `~/.claude.json`
   second.
2. **Freshness needs the watcher; boot needs the SHA reconcile. They are two different mechanisms.**
   The watcher catches writes while the server is running. The boot-time reconcile catches
   everything that changed *while it wasn't* — including writes made from another machine, or by you
   in an editor. Both are automatic, but it means the first launch after a long gap does real work:
   give it a moment before concluding it is broken. A restart with nothing changed re-embeds zero
   files and is near-instant — the smoke test asserts exactly that.

---

## How it works

- **Embeddings:** FastEmbed `bge-small-en-v1.5` (ONNX, 384-dim, fully local). The provider is
  swappable: set `"provider": "ollama"` to use `nomic-embed-text` via Ollama's local HTTP API.
- **Store:** a flat numpy + cosine store. At hundreds-to-thousands of chunks a brute-force dot
  product takes microseconds, so there is no reason to take on the native-build risk of a vector
  database. Persisted as `vectors.npy` + `meta.json`, **keyed by source-file SHA**, so a restart
  re-embeds only what actually changed.
- **Freshness:** a `watchdog` observer over every source dir, debounced (~2s), incrementally
  re-embedding changed files and dropping deleted ones — plus the boot-time SHA reconcile.
- **Index-the-parent:** a *list* of source dirs, each tagged with a `project` name. `project=`
  scopes a search; omit it to span all. **Writes stay where Claude Code already puts them** — recall
  is unified without maintaining a second copy of anything.
- **Frontmatter-resilient:** YAML is parsed, but a parse error (e.g. an unquoted colon inside a
  `description:`) **never skips the file.** It logs, salvages the name and description by regex, and
  indexes the body anyway. This is not hypothetical: that exact failure silently lost four memories
  from a previous tool, with no error surfaced anywhere.

The index and the model cache live under `~/.claude/sabai-memory/`, never inside this repo.

---

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `no config file found`, with a list of paths | You haven't copied `sources.example.json` to `sources.json`. |
| Registered but never connects | Claude Code wasn't restarted, or the command isn't the venv's own python. |
| Searches return nothing at all | Call `stats()` — `files: 0` means the source paths don't resolve. Remember relative paths resolve against `sources.json`, not `cwd`. |
| A memory you just wrote isn't found | Give it ~2s (the debounce). If it still isn't there: is it `.md`, inside a configured source, and not caught by `excludes`? |
| Recall finds the file but the wrong part of it | Read `../conventions.md` §3 — the `description:` is a query target, and summary chunks outrank body chunks. |
| Windows: install "succeeded" but imports fail | You installed from Git Bash/MSYS. Re-run the install from PowerShell. |
| Windows: `ModuleNotFoundError` for a file that visibly **exists on disk** | **MAX_PATH.** Some dependency paths under `.venv` are long, and if your clone sits deep the full path crosses 260 characters — the file is there, and Python still cannot open it. Hit for real while testing this pack from a deep temp directory (273 chars). Fix: clone somewhere short (`C:\dev\...`), or enable long paths (`LongPathsEnabled` under `HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem`). Check with `(Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem' -Name LongPathsEnabled).LongPathsEnabled` — `0` means off. |
| `ImportError: No module named 'mcp.server.fastmcp'` | Your `mcp` resolved to 2.x, which removed that module. `pyproject.toml` pins `<2` for exactly this reason — re-create the venv so the pin takes effect. |
