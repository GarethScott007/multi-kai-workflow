---
name: playbook_multi_kai_pipeline
aliases:
  - multi-kai-pipeline-portable
description: "PORTABLE playbook — the multi-Kai pipeline pattern (S-Kai plan / I-Kai build / V-Kai verify, S-Kai merges), distilled project-neutral from the SabaiFly engine 2026-07-12. Start any new project from this."
metadata:
  node_type: memory
  type: reference
---

# The multi-Kai pipeline — portable core

Distilled 2026-07-12 from the SabaiFly engine after ~3 months of live operation. Project specifics (domain gates, file conventions) live in each project's `CLAUDE.md`; THIS is the part that transfers.

**"The principal" throughout means the human** — the person who sets direction, approves, and is the escalation target. In the origin project that was Gareth; in yours it is you.

## Roles

- **S-Kai (strategist)** — briefs, decisions, sequencing, coordination, memory writes, MERGES. Never implements beyond one-liners. Context economy is the point: S-Kai holds the plan; burning its context on code degrades both halves.
- **I-Kai (implementer)** — executes ONE brief per session, in its own window and its own git worktree. The brief is the contract: in scope, not beyond; unclear → escalate, never silently expand.
- **V-Kai (adversarial verifier)** — a FRESH-context subagent (not a standing window) dispatched at two gates: BRIEF review (before I-Kai burns a session) and BUILD review (before S-Kai merges). Default-skeptical: "not proven" until its own evidence says otherwise. Advises; never merges.
- **The principal (the human)** — approval, escalation authority, direction. Post-escalation their re-scope is authoritative (V-Kai gets ONE confirmatory pass, not a fresh loop).

## The two gates

1. **Brief gate** — two lenses, both must pass: *right-target* (is this the correct thing to build — premise current, scope right?) and *executable* (can a fresh implementer build it AS WRITTEN — files anchored, gates defined, done-definition crisp?).
2. **Build gate** — V-Kai does its own adversarial diff read (`git diff <trunk>...<branch>`) against the brief + the project's domain gates. Then S-Kai final-checks and merges. V-Kai approval is necessary, never sufficient.

Loop cap ~2 rounds per gate; round-2 failure (or trading a failure for its opposite) means the APPROACH is wrong → escalate, don't grind.

## Right-sizing (deterministic predicate, not vibes)

Default = STANDARD review. "Trivial" must be AFFIRMATIVELY established (single file · no user-facing strings · no high-stakes domain surface · no shared-plumbing import). Any high-stakes touch (security, money, health/legal claims, shared plumbing) overrides to FULL multi-skeptic panel, always. Don't tax a one-liner; never wave through a landmine.

## Coordination: git as the bus

- S-Kai ↔ I-Kai coordinate via **docs commits**, not chat. The completion commit IS the signal.
- S-Kai arms a HEAD-watcher over active `feature/*` branches (background loop, ~45s poll, exits + re-invokes on movement). Watcher stays armed across the V-Kai↔I-Kai fix loop; tear down only after merge/escalation.
- **ROBUST-BASELINE rule** (bit twice): arm from the last-PROCESSED heads, never a fresh `rev-parse` at arm time — a commit landing in the re-arm gap gets silently absorbed.
- **SCAN-AT-ARM-TIME rule** (bit once, 20h loss): watchers only see FUTURE movement. At session start, scan every in-flight branch for already-done-but-unmerged work (`git log <trunk>..<branch>` + completion note + clean worktree). Don't trust the handoff's "in-flight" list.

## Dispatch contract (load-bearing)

A spawned subagent does NOT auto-load a skill and CANNOT invoke slash commands. Frame the role inline: tell it to read the role's SKILL.md first (or paste it), then hand it the concrete inputs (brief path, or diff range + named gates). The verdict is the subagent's structured RETURN VALUE, read in the dispatcher's context — no blackboard, no cross-session relay.

## Session lifecycle failsafes

- **Early handoff**: at <25-30% context remaining, STOP and write/refresh the handoff doc — fire-sequence, decisions + where captured, single next move. A thin handoff beats a dead session. The handoff is a save point, not a session-end artifact.
- **I-Kai partial**: commit whatever is green, progress note at the bottom of the brief (done hashes / not done / next step / landmines), tick status to partial, tell the principal.

## The learning loop (what makes the engine improve)

- V-Kai pre-flights every pass against the Lessons library (semantic search) and NAMES the lessons it checked — so dead lessons get pruned, hot ones reinforced.
- Novel failure-mode → `NEW-LESSON:` heading in the verdict → S-Kai persists it to the vault (verifier reads, strategist writes). The same class of bug must not pass twice.
- **Post-merge coroner** (added 2026-07-12): after each merge, a cheap subagent diffs brief vs build vs verdict and proposes 0-2 lessons. No lesson escapes because nobody remembered to harvest.
- Consolidate lessons into topic MOCs every ~20; keep frontmatter descriptions tracking status ([playbook_memory_conventions](playbook_memory_conventions.md)).

Related: [playbook_model_tiering](playbook_model_tiering.md) · [playbook_verification_doctrine](playbook_verification_doctrine.md) · [playbook_fable_failure_modes](playbook_fable_failure_modes.md) · [playbook_new_project_bootstrap](playbook_new_project_bootstrap.md)
