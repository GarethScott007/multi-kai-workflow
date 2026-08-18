# HANDOFF TEMPLATE — the session-boundary save point

Copy to `docs/HANDOFF-YYYY-MM-DD-<session-tag>.md`. S-Kai writes it; the next session boots from it.

The handoff carries the **connective tissue** — what's queued, fired, and waiting on what. Decisions
themselves live in the brain (captured as they land); the handoff carries the thing the brain
cannot: the *shape of the moment*. That is what dies first in a context exhaustion.

---

## ⛔ The live-queue law (2026-08-18)

**The boot doc carries exactly ONE live-queue block, at the top, and superseding it means REWRITING
that block — never appending a new section beneath it.**

This law was written after one boot doc accreted eight sub-sections over eight days, with duplicate
item numbers and the live queue split across four places. Nothing was *wrong* in it; every line had
been true when written. But the next reader had to reconstruct current state by mentally cancelling
superseded lines against later ones — which is vigilance-dependent, and had already produced errors.

**How to supersede correctly:**
1. Rewrite the LIVE QUEUE block in place, so it states current reality and nothing else.
2. Stamp the section it replaced — `⛔ SUPERSEDED 2026-08-18 — see LIVE QUEUE above` — and leave it
   where it is. Progression has value; ambiguity does not.
3. Never renumber old items. Never leave two blocks that both look current.

An append-only handoff is sediment. A rewritten one is a save point.

---

## ⛔ The early-handoff trigger

**The handoff is not only a session-end artifact.** When your remaining context drops below ~25–30%
— or the moment a long task starts eating context faster than expected — STOP and write or refresh
the handoff BEFORE anything else. **A thin handoff beats a dead session.**

Written after a session ran its context to exhaustion mid-flow and could not emit a handoff at all;
the next session had to reconstruct it from git artifacts and a pasted chat log. The decisions
survived (they'd been captured to memory in-flight). The fire-sequence nearly didn't.

A minimal handoff MUST carry three things; everything else is nice-to-have:
1. **The fire-sequence** — queued / fired / waiting-on-what.
2. **Decisions made this session + where each is captured** — memory slug, commit hash, or doc path.
3. **The single next move.**

---

## The template

```markdown
# HANDOFF — YYYY-MM-DD — <session tag>

## 🔴 LIVE QUEUE  (⛔ ONE block. Rewrite it to supersede. Never append a rival.)

**Next move:** <the single next action, concrete enough to start on>

| # | Item | State | Waiting on | Where |
|---|------|-------|-----------|-------|
| 1 | <task> | 🔥 fired | V-Kai build review | `feature/<branch>` |
| 2 | <task> | 🟡 queued | item 1 merging | `docs/BRIEF-I-KAI-<x>.md` |
| 3 | <task> | ⛔ blocked | principal's ruling on D4 | `docs/DECISIONS-PENDING.md` |

**In-flight agents / watchers:** <what is running right now, and what fires when it finishes.
If a HEAD-watcher is armed, say over which branches — an unarmed watcher means the principal
has to relay completions by hand, which is the recurring lapse this line exists to prevent.>

---

## 0. Role discipline
<Only if you slipped this session. Lead with it — it is the first thing the next S-Kai reads,
and an honest one-line self-report is worth more than a clean-looking omission.>

## 1. Today's commits (chronological)
| sha | branch | what |
|-----|--------|------|
| `abc1234` | main | ... |

## 2. Decisions made + where each is captured
| Decision | Captured in | Verifiable by |
|---|---|---|
| <decision> | `project_<slug>` memory | `git -C <vault> log -1 -- <file>.md` |
| <decision> | `docs/STRATEGY-<x>.md` | commit `abc1234` |

⚠️ A decision that exists only in this handoff is not captured. Name the durable home or say
plainly that it has none yet.

## 3. Gate telemetry (feeds the harvest gate)
| Gate | Wall-clock | Findings |
|---|---|---|
| brief review | 12 min | 2 MAJOR, 1 MINOR |
| build review | 40 min | 1 BLOCKER |

Purpose: **a gate that stops catching things gets DELETED.** Telemetry justifies removal, not
only addition — so record it even when the answer is zero.

## 4. Battle plan / milestone state
<done vs in-progress vs not-started against whatever the current milestone is>

## 5. Strategic work pending (planner-shaped, for the next S-Kai)
<things that need thinking, not building>

## 6. Brief-able tasks NOT yet written
<things that need a brief, with a one-line scope sketch each — so the next session can dispatch
without re-deriving the scope>

## 7. Landmines
<anything that will bite the next session: a wedged process, a stale cache, a flaky gate, a
platform quirk you just paid to learn. Name it here AND capture it as a memory — this section
is the fast path, the memory is the durable one.>

---
*Signed: Kai*
```

---

## Boot sequence (what the next session does with this)

1. `/s-kai`
2. **Search the brain first** on the session's topic — mechanical, not optional.
3. Verify the session's tooling: one harmless REAL call to each MCP/CLI the queue depends on.
   "Tools visible" is not "auth works."
4. Read this handoff top-to-bottom. The LIVE QUEUE is the state; everything below it is context.
5. `git status` + recent commits, to ground the branch picture against what the doc claims.
6. **Scan every in-flight branch for already-done-but-unmerged work** (`git log <trunk>..<branch>`
   plus a completion note plus a clean worktree). Watchers only see FUTURE movement — a build that
   finished while nobody was watching is invisible to them. This rule cost 20 hours once.
7. Acknowledge state and propose the pickup move. Don't dump everything.
