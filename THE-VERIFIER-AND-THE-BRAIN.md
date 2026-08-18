# The Verifier and the Brain — the 2026-06 evolution

*An update to the [Multi-Kai Workflow](README.md). Two things changed the pattern materially: a **fourth role** (V-Kai, the adversarial verifier) turned the workflow into a **verified pipeline**, and the **durable memory matured into a "brain" that gets smarter over time.** This doc captures both, plus the full storage architecture — how every kind of work is persisted so nothing is ever lost.*

---

## 1. The fourth role: V-Kai, the adversarial verifier

The original pattern had a structural hole: **no author reviews their own work well — and that includes the planner reviewing its own briefs.** The planner (S-Kai) both *wrote* a brief and *checked* the build against it. Two failure modes slipped through:

1. **Flawed briefs** — wrong target, stale premise, under-specification — caught (if at all) only after an implementer (I-Kai) burned a whole session building the wrong thing.
2. **Self-reviewed builds** — the planner is invested in the brief it wrote, so its spot-check is biased toward "it's fine."

**V-Kai closes both.** It is a dedicated, default-skeptical verifier whose only job is to *try to break the artifact in front of it*. It reviews the **brief** before the implementer builds, and the **build** before the planner merges. A review that concludes "looks good" everywhere is a failed review — V-Kai's value is the holes it finds.

With V-Kai, the roles working a task are now **S-Kai (plan) → V-Kai (verify) → I-Kai (implement)**, with R-Kai (research) pulled in as needed. The human stays the principal: the escalation target and the only one who sets product direction.

### How V-Kai runs (the key mechanism)
V-Kai is a **subagent with a fresh context**, dispatched from the planner's session. Fresh context = independent *by construction* — same independence a separate window gives, but cheaper, and (crucially) it actually works: a coding agent can't "wake" a separate idle session, but it *can* spawn a subagent and read its structured verdict back directly. The verdict is the subagent's return value. No second live session to coordinate, no cross-window relay. (For heavy, high-stakes reviews the same role can also be driven by hand in its own window — but the default is the cheap, automatic subagent.)

### The two lenses (brief review)
- **Right-target:** is this the *correct thing to build*? Approach sound, premise current, scope right — or stale/wrong/over-broad?
- **Executable:** can an implementer build it *as written* without flailing? Files anchored, gates defined, "done" crisp, the project's hard constraints called out?

### The build review
V-Kai re-derives findings from the diff itself, **runtime > code-read** for any binary gate (spin the app, check the actually-served output, not just the source), with a **working negative control** so a clean result can't be a false-clean. It *advises*; the planner is still the only one who merges.

### Right-size — don't tax a one-liner, never wave through a landmine
A deterministic predicate, not vibes: **default is "standard"; "trivial" must be affirmatively established** (single file, no user-facing strings, no high-stakes surface, no shared-plumbing); **anything high-stakes/security/shared-plumbing overrides to a full multi-skeptic panel, always.**

### It proved itself on day one
On the day V-Kai shipped, independent verification caught — in a single session — a false-alarm "leak" that would have wasted a fix, a *silent merge graft-drop* (a clean-looking auto-merge that had quietly dropped one branch's work), a flawed design doc (V-Kai reviewed its *own founding charter* and returned "rework" with real holes), a latent caller-mutation bug in shipped-looking code, and a hygiene slip where a verification agent mutated a config file. Every one of those is something self-review ships.

**The rule this earned:** *all non-trivial work is adversarially reviewed before it lands — code, content, and briefs.* It's encoded as law in the project's instructions file, not left to discipline.

---

## 2. The brain — durable memory that gets smarter over time

The original pattern's "durable memory" was a folder of decision notes. It matured into a **brain** with three properties:

1. **Owned semantic recall.** A small, fully-local, owned MCP server indexes the memory folders and serves recall *by meaning*, not just a hand-maintained index — with a file-watcher so a memory written this session is searchable within seconds. Owned end-to-end: no third-party in the read path of the partnership's memory, and it ports to local hardware unchanged. (Sovereignty matters here — the memory is the single most thesis-critical asset; nothing load-bearing should be a dependency someone else can pull.)

2. **A learning loop — the part most people skip.** Capturing notes isn't enough; the brain only gets *smarter* if the lessons are **applied**:
   - **Capture** — every session, new failure-modes are written to the vault as they happen.
   - **Consolidate** — periodically, the lessons are de-duplicated and synthesised into a single **Lessons-Learned map-of-content** (a pre-flight checklist).
   - **Apply** — **V-Kai reads that checklist before *every* review.** The same class of bug can't get through twice, because the verifier reads the lesson first. *Capture → consolidate → apply* is what turns a pile of notes into a measurably falling repeat-failure rate.
   - The read/write split: V-Kai (read-only brain) *finds* a novel lesson and flags it; the planner *writes* it. (This loop fired for real on day one — V-Kai surfaced a new failure-mode, the planner persisted it, and it's now in the checklist.)

3. **Off-machine, can't-be-taken backup.** The live memory folder is its own private git repo, committed + pushed *in the same beat* as every memory write — so the off-machine backup is never more than one write stale. On-machine + backed-up + clone-able = it can't be lost or taken away.

---

## 3. The storage architecture — where every kind of work lives

The discipline that makes the workflow durable: **every kind of knowledge has exactly one home, and it's a durable artifact — never the chat.** When a session ends, nothing of value dies with it.

| Kind of work | Lives in | Why there |
|---|---|---|
| **Code** | git (the trunk branch), pushed | Versioned, reviewable, the source of truth for *what runs* |
| **Strategic decisions + reasoning** | `docs/STRATEGY-*.md` | Long-form, comparison tables, citations — the *why* behind the *what* |
| **Brand / positioning / discipline rules** | the **brain** (memory vault), recalled semantically | Cross-session, evolves slowly, applies broadly |
| **Codebase conventions** | the instructions file (`CLAUDE.md`) + memory | Every code session needs them primed |
| **Role contracts (the workflow itself)** | the **skills** (`s-kai` / `v-kai` / `i-kai`) | Auto-prime the role discipline at session start |
| **In-flight task state** | `docs/HANDOFF-*.md` | Bridges session boundaries — the connective tissue (what's queued / fired / blocked) |
| **Shipped status** | `docs/BUILD-STATUS.md` | Durable record of what merged |
| **The learning library** | the Lessons-Learned map-of-content (in the vault) | V-Kai's pre-flight checklist — the brain's "smarter over time" |
| **Generated content** | gated, published to **checked-in files** | One source of truth; a file exists only if it passed the quality gates ("clean by construction") |

**Two rules keep it honest:**
- **Search the durable layers first.** "What did we decide about X?" → check the strategy docs / brain *before* re-deriving in chat. Chat history is the last resort, not the first.
- **The handoff is a save-point, not just an end-of-session ritual.** When context runs low *mid-task*, the connective tissue (the fire-sequence — what's queued, fired, waiting-on-what) is what dies first in a compaction, so it gets written *early* and refreshed as state changes. A thin handoff beats a dead session.

---

## 4. How this stores work for SabaiFly (the concrete instance)

The same architecture, instantiated:
- **Code** → the product repo on its integration trunk, pushed; every merge is an adversarially-verified "pillar."
- **The brain** → the memory vault, backed off-machine to a private repo, recalled via the owned local server, viewed in Obsidian (where it's simply called *Brain*).
- **Strategy + handoffs + build-status** → `docs/` in the repo.
- **The workflow itself** → the three role skills — which this repo now ships directly in `skills/`, alongside the playbooks, templates, settings/hook and memory server they run on.
- **Content** → an in-repo pipeline that composes on a flat-rate plan, runs it through ported quality gates, and **publishes to checked-in files** — so production renders from versioned files with zero runtime dependency on any external content database, and a published file is "clean by construction" (it exists only because it passed the gates).

Nothing of value lives only in a chat window. That's the whole point: **the work compounds because it's stored, and the brain compounds because it learns.**

---

*Part of the [Multi-Kai Workflow](README.md). MIT-licensed — adapt freely; a link back is appreciated.*
