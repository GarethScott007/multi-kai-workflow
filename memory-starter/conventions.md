# Memory conventions — how the brain stays healthy

Distilled from `playbooks/playbook_memory_conventions.md`. That file is the full doctrine with the
measurements; this is the working subset you need on day one.

The vault is read through **three lenses**, and every convention below exists to keep all three
working at once:

| Lens | Reads by | Breaks when |
|---|---|---|
| The model, directly | file path | files are scattered or the index lies |
| **Semantic search** (the MCP in `memory-server/`) | meaning | the `description:` doesn't carry the answer's words |
| **You**, in a linked-note editor | `[[wikilinks]]` + graph | aliases are missing, so every link is dead |

---

## 1. One fact per file, with a typed prefix

| Prefix | Holds |
|---|---|
| `user_` | who the principal is — background, role, preferences |
| `feedback_` | how-we-work rules and lessons ("from now on…", "never…") |
| `project_` | state and decisions ("X works this way because Y") |
| `reference_` | pointers and mechanics (dashboards, runbooks, platform quirks) |

Resist the urge to write one big file per topic. One fact per file is what makes a search result
*answer* rather than merely *point*, and it is what lets a single fact be superseded without
disturbing its neighbours.

## 2. Frontmatter is not decoration

```yaml
---
name: feedback_verify_before_asserting
aliases:
  - verify-before-asserting          # the kebab concept form
  - how-do-i-know-this-api-still-works   # how someone would actually ask
description: "🔒 STANDING RULE: external facts are VERIFIED live, never recalled …"
metadata:
  node_type: memory
  type: feedback
---
```

- **Quote the `description:`.** An unquoted colon inside one silently dropped four memories from an
  indexer once. Quote it always; the cost is one character.
- **`aliases:` are mandatory**, and they carry the kebab concept form. Without them, wikilinks are
  **dead** in a linked-note editor: you click, get an empty pane, and a 0-byte stray file is
  created behind you.
- **Wikilink by exact filename stem.** Links to memories that don't exist yet are legitimate
  future-markers.

## 3. ⛔ `description:` is a QUERY TARGET, not a summary

This is the highest-leverage convention in the file, and the least obvious.

The semantic index embeds `name + description` as **its own chunk**, and that summary chunk
routinely **outranks** the body. So the description is what actually answers searches. Three parts,
in order:

1. **The load-bearing tokens of the real answer** — actual numbers, names, verdicts. `£6 per trip`,
   `20 LIFETIME`, `SHIPPED`, `REFUSED`, `EU-west`. Not "our pricing decision".
2. **Two registers** — the insider term *and* the lay phrasing someone would actually type.
3. **A dated status stamp** — `✅ SHIPPED 2026-07-25` / `🔒 LOCKED` / `⛔ BLOCKER` /
   `SUPERSEDED 2026-06-09`.

**The corollary that bites:** any status change updates the `description:` **in the same edit** as
the body. A memory whose body says RESOLVED and whose description still says "not yet fixed"
actively misinforms every future search — and because summary chunks outrank body chunks, the wrong
half is the half that gets read. This has caused real, costly errors: an audit filed a blocker
against a module that already existed, because the memory's *body* recorded the fix and its
*description* didn't.

## 4. Body: the fact, then **Why**, then **How to apply**

Five lines beats fifty. Comprehensiveness is the main reason capture doesn't happen at all.

**Never leave a bare heading.** Every `##` needs at least one sentence of prose before any child
heading — a body-free heading becomes a topic-free attractor in the index and will surface against
queries that have nothing to do with it.

## 5. Status claims are dated and exit-conditioned

Anything containing `NOT built` / `queued` / `blocked` / `interim` / `deferred` carries
`(as of YYYY-MM-DD)` **and** a machine-checkable exit condition:

```
EXIT: lib/moderation/ exists
EXIT-COMMIT: <sha>
EXIT-EVENT: the first paying customer outside the EU
```

Without an exit condition, a temporary state becomes permanent by default. In one audit, three
memories had exit conditions that had **already fired** with nobody noticing — including a live
denylist whose removal was overdue.

## 6. Commit + push in the SAME BEAT as every write

The memory dir is its own **private** git repo. Every write is followed immediately by
`git add -A && git commit && git push`, so the off-machine backup is never more than one write
stale.

This is **discipline, not a cron.** A nightly job would be a system to maintain, and solo builders
over-automate. Two commands at the moment of writing costs nothing and never silently stops.

⚠️ The memory repo, the playbooks repo and your app repo are **separate repos**. A memory therefore
*cannot* be stamped in the same **commit** as a code merge — only in the same **beat**. Any process
that says "same commit" across repos has specified something impossible, and will train people to
skip it.

## 7. Nothing is deleted; supersession is a SWEEP

Three tiers, and nothing ever moves out of the tier it was born in:

| Tier | Holds | Target size |
|---|---|---|
| `playbooks/` | **The LAW** — domain-free rules | ≤15 files, ≤25 rules each |
| Project vault | **The STORY** — the incident, date, real numbers, domain nouns. Every lesson is born here. | unbounded |
| Archive | **A status stamp, in place** — not a folder | — |

**The promotion test (~20 seconds):** *delete every proper noun. Is there still a rule?*
Yes, and it reads fine → promote as-is. Yes, but it needs rewriting → write the generic twin, keep
the original. No → it stays project-scoped.

Promotion **preserves progression**: `playbooks/` gains one domain-free rule ending in a
**plain-text** provenance tag — `(first seen: <project> · <file> · 2026-07-25)`, **never a
`[[wikilink]]`**, because cross-vault wikilinks are dead and mint strays. The original gains one
line: `PROMOTED → playbook_x`. The playbook says *where the law came from*; the vault says *what it
cost to learn it*.

**Superseding** is the same shape: the old file **stays**, gains
`⛔ SUPERSEDED by <file> (date) — kept for progression`, gets a `SUPERSEDED <date> —` prefix on its
description, **and then you sweep the old literal string across the whole vault.** That sweep is the
part that actually defends recall. Proof: a pricing memory was stamped perfectly in its own
description and *still* lost rank 1 to an unswept old figure in a neighbouring file.

⚠️ **Read and classify — never find-and-replace.** The same literal is often legitimately correct
elsewhere (a £30/month tier and a £30/review rate are not the same £30).

**Before deleting anything** (and you should almost never delete): grep for inbound `[[links]]` and
repoint them, and transplant any lesson that exists nowhere else.

## 8. Asking well — *"a silly question gets a silly answer"*

Storage discipline is worthless if recall can't find the answer. The index is lexically biased: it
rewards noun-dense, jargon-matched, 6–12 word queries and punishes conversational ones.

1. **Name the artifact, not the intent.** Nouns the vault owns beat verbs describing your need.
2. **Ask twice, in two registers** — your words, then the vault's. Disjoint results mean a
   *description* gap: fix the description, don't fire a third query.
3. **Query symptom and cause separately.** The symptom query is often the only one that lands.
4. **Never accept the top hit on a money / status / decision question.** Open the file and read the
   revision block. **A snippet is a pointer, not a citation.**
5. **Scope craft questions to the playbooks with `k≥8`** — a handful of playbooks are structurally
   outvoted by hundreds of project files, and one long playbook will otherwise eat every slot.
6. **Treat a null result as null.** There is no "I don't know" — a nonsense query still returns
   something with a plausible score. If the snippet doesn't *contain* the answer, the answer isn't
   there. Go to the source, not to a fifth query.

Measured, from a ~370-file vault:

| Typed naturally | Got | Ask instead | Got |
|---|---|---|---|
| *how do I know a fix works before claiming done* | doctrine **absent** | `verification doctrine evidence before assertion` | rank 2 ✅ |
| *how much are we charging* | **stale price at rank 1** | `price per month tier lifetime credits` | correct ✅ |

## 9. Hygiene sweep (run whenever you touch the vault)

- 0-byte `*.md` strays — created whenever a dead wikilink gets clicked.
- Descriptions containing "not yet" / "pending" / "awaiting", diffed against the body's latest update.
- Dead-link scan. Adding the missing `aliases:` fixes most of them.

---

## The example vault in `vault/`

`vault/` is a working example memory dir, and it is what the shipped smoke test searches:

```
vault/
├── MEMORY.md                     # the boot index — auto-loaded every session
├── user_profile.md               # type: user
├── feedback_verify_before_asserting.md   # type: feedback
├── project_deploy_target_ruling.md       # type: project — with a status stamp + EXIT condition
└── hubs/
    └── Lessons-Learned.md        # the MOC V-Kai reads before EVERY review
```

Every file in it is invented. **Copy the shapes, delete the content.** Your real vault lives at
`~/.claude/projects/<encoded-project-path>/memory/` — see `docs/GETTING-STARTED.md` for how to find
that path and how to point the memory server at it.

`hubs/Lessons-Learned.md` is the one file you should create even while it is nearly empty: the
V-Kai pre-flight dereferences it on every pass, and a pre-flight that points at a missing file is a
pre-flight that silently does nothing.
