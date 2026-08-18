---
name: playbook_memory_conventions
aliases:
  - memory-conventions-portable
description: "PORTABLE playbook — how the partnership brain stays healthy: one fact per file, aliases for Obsidian, descriptions track status, commit+push same beat, MOC consolidation, hygiene sweeps. Apply in EVERY project's memory dir."
metadata:
  node_type: memory
  type: reference
---

# Memory conventions — portable doctrine (consolidated 2026-07-12)

The vault is read through three lenses — the model (direct file reads), semantic search (the memory MCP in `memory-starter/memory-server/`), and the human (a linked-note editor such as Obsidian: wikilinks + graph view). Every convention below keeps all three lenses working.

> **A note on directory names.** This doctrine splits durable knowledge into **the LAW** (domain-free
> craft rules, portable across every project) and **the STORY** (the incident, date, real numbers,
> domain nouns — project-scoped). In this repo the LAW tier is the `playbooks/` directory you are
> reading; the author's own machine calls that same directory `~/.claude/memory-shared` and refers
> to it below as `_shared`. Read `_shared` as "wherever your portable playbooks live."

## Writing a memory

- **One fact per file**, typed filename prefix: `feedback_` (how-we-work rules + lessons), `project_` (state/decisions), `reference_` (pointers/mechanics), `user_` (who the human is).
- **Frontmatter**: `name:` + quoted `description:` (unquoted colons in a description once silently dropped 4 memories from an indexer) + `aliases:` carrying the kebab concept form (`feedback_new_lesson.md` → alias `new-lesson`). Without the alias, wikilinks are DEAD in Obsidian — the human clicks and sees an empty pane, and a 0-byte stray gets created.
- **Body**: the fact, then **Why:** and **How to apply:**. 5 lines beats 50 — don't let comprehensiveness kill capture.
- **Wikilinks by exact filename stem** (`sabaifly · feedback_test_dont_assume`); links to not-yet-written memories are allowed future-markers.

## Keeping it true

- **Descriptions track status** (the recall-poisoning bug, found 2026-07-12): the semantic index embeds `name + description` as its own summary chunk, and summary chunks routinely OUTRANK body chunks. A memory whose body says RESOLVED but whose description says "not yet fixed" actively misinforms every future recall. Any status change (resolved / superseded / extended / shipped) updates the `description:` line IN THE SAME EDIT, leading with the status word and date. Living logs say "LIVING LOG … read the latest UPDATE block, not the top."
- **Capture in-session as decisions land** (~2-5k tokens each), session-end sweep only as backstop. Cost of not capturing = re-derivation forever.
- **Commit+push the memory dir in the same beat as every write** — the off-machine backup is never more than one write stale. Discipline, not cron (solo founders over-automate).

## Structure at scale

- `MEMORY.md` = boot index, one line per memory. When it grows heavy, compact: mature lesson-tier pointers move into topic **MOCs** (`hubs/`), index keeps identity + working rules + live state + post-MOC lessons. Re-consolidate every ~20 new lessons.
- **Hygiene sweep** (run whenever touching the vault): 0-byte `*.md` strays (Obsidian creates one when a dead link is clicked); descriptions containing "not yet"/"pending"/"awaiting" diffed against their body's latest update; dead-link scan (aliases fix most).
- **Cross-project**: recall is user-scoped — the whole brain is searchable from any repo. New projects boot with an empty memory dir; the global `~/.claude/CLAUDE.md` carries the search-first reflex. Portable doctrine lives in the shared playbooks dir (`_shared`); project lessons stay in their project vault (still searchable everywhere).

### The tier model + promotion path (added 2026-07-25)

**Measured problem:** ~370 project memories vs **8** portable ones. Triage put **~32% portable as-is** and **~21% portable after generalisation** — class A alone is ~15× the entire `_shared` corpus. Root cause is structural, not lazy: the learning loop says *"S-Kai persists it to the vault"* and contains **no portability triage step** — the same shape as the stamping failure (*writing is in a workflow; promoting is in none*).

**Three tiers, nothing ever deleted, nothing ever moved out of the project vault:**

| Tier | Holds | Target |
|---|---|---|
| `_shared` (this repo's `playbooks/`) | **The LAW** — domain-free numbered rules | ≤15 files, ≤25 rules each |
| Project vault | **The STORY** — the incident, date, real bug, numbers, domain nouns. Every lesson is born here. | unbounded |
| Archive | **A status stamp, in place** — not a folder. Only dated session logs ever move. | — |

**The decision test (~20 seconds):** *delete every proper noun. Is there still a rule?* Yes and it reads fine → promote as-is. Yes but needs rewriting → write the generic twin, keep the original. No → stays project-scoped.

**Promotion preserves progression** (Gareth's requirement — *"good to see how we arrived at a certain point"*): `_shared` gains ONE numbered domain-free rule ending in a **plain-text** provenance tag — `(first seen: sabaifly · feedback_x · 2026-07-25)`, **never a `[[wikilink]]`**, because cross-vault wikilinks are dead in Obsidian and mint 0-byte strays. The vault original is untouched in substance and gains one line: `PROMOTED → playbook_x #12`. Shared says *where the law came from*; the vault says *what it cost to learn it*.

**Supersession is the same shape** — the old file **stays**, gains `⛔ SUPERSEDED by <file> (date) — kept for progression`, a `SUPERSEDED <date> —` description prefix, **plus the R7 string sweep**, which is the part that actually defends recall.

**The trigger (must be a workflow step, or it never happens):** V-Kai's `NEW-LESSON` block gains a mandatory `PORTABLE: yes | generalise | no` field with a one-line domain-free form; S-Kai's stamp-on-merge appends it to `_shared` **in the same commit as the vault write**. Split commits = the 370-vs-8 pile. **Backstop:** if a `search_memory` before writing a lesson returns its closest hit from a *different project*, that lesson has now been learnt twice independently → promote it.

## Retrieval — the half nobody designs for (added 2026-07-25, Gareth: *"asking the right question or search is just as important — silly question equals silly answer"*)

Storage discipline is worthless if recall can't find the answer. Measured against a 370-file vault; the index is **lexically biased** (bge-small, 384-dim) — it rewards noun-dense, jargon-matched, 6–12 word queries and punishes conversational ones.

### Writing so it can be found

- **R5 — `description:` is a QUERY TARGET, not a summary.** It is embedded as its own chunk and routinely outranks the body. Three parts, in order: (1) the load-bearing tokens of the actual answer — real numbers, names, verdicts (`£6 Trip Pass`, `20 LIFETIME`, `SHIPPED`, `REFUSED`); (2) **two registers** — the insider term AND the lay phrasing someone would actually type; (3) a dated status stamp (`✅ SHIPPED 2026-07-25` / `🔒 LOCKED` / `⛔ BLOCKER` / `SUPERSEDED 2026-06-09`).
- **R6 — never leave a bare heading.** Every `##`/`###` needs at least one prose sentence before any child heading. A body-free heading becomes a topic-free attractor: `## Why this is the decision` scored 0.7488 against a query about a podcast that does not exist. Check: `rg -U '^##+ .*\n\n?(?=##)' *.md`.
- **R7 — sweep the superseded STRING, not the file.** ⚠️ *The load-bearing one.* When a value changes, `rg` the old literal across **every indexed source**, then read each hit and correct or stamp it. Proof: a pricing memory was stamped perfectly in its own description and **still** lost rank 1 to an unswept old figure in a neighbour file. **Read and classify — never find-and-replace**; the same literal is often legitimately correct elsewhere (a £30/mo tier vs a £30/chunk review rate).
- **R8 — portability = promotion, not annotation.** Writing "applies beyond this project" in a description creates **zero** portability — 35 domain nouns beat a 3-word clause every time. If the generic form doesn't live in `_shared`, the lesson is not cross-project.
- **R9 — filename and aliases are retrieval surface.** Name the file after *the question that will be asked*, not the incident. A name carrying **cause + symptom** hit rank 1 on a pure symptom query; a diary-style title never surfaced at all. Jargon name → add a lay-phrasing alias.

### Asking — six rules

1. **Name the artifact, not the intent.** Nouns the vault owns beat verbs describing your need.
2. **Ask twice, in two registers** — your words, then the vault's. Disjoint results = a *description* gap: fix the description (R5), don't fire a third query.
3. **Query symptom and cause separately.** The symptom query is often the only one that lands.
4. **Never accept the top hit on a money / status / decision question.** Open the `🔒` or dated file with `get_memory` and read the revision block. **A snippet is a pointer, not a citation.**
5. **Scope your search to the shared playbooks (`_shared`) with `k≥8` for craft/process questions** — a handful of playbooks are structurally outvoted by hundreds of project files, and one long playbook will otherwise eat every slot.
6. **Treat a null result as null.** There is no "I don't know" — a nonsense query still scored 0.7488. If the snippet text doesn't *contain* the answer, the answer isn't there. Go to the source, not to a fifth query.

### Measured failures (what a "silly question" actually costs)

| Typed naturally | Got | Ask instead | Got |
|---|---|---|---|
| *how do I know a fix works before claiming done* | doctrine **absent** | `verification doctrine scar rules evidence before assertion` | rank 2 ✅ |
| *how much are we charging* | **stale price at rank 1** | `Trip Pass price per month Pro tier lifetime credits` | correct ✅ |
| *what is still blocking launch* | neither blocker ranked | `launch blocker legal GDPR publication privacy Stripe live flip` | ✅ |

Related: [playbook_multi_kai_pipeline](playbook_multi_kai_pipeline.md) · [playbook_new_project_bootstrap](playbook_new_project_bootstrap.md)
