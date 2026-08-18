---
name: Lessons-Learned
aliases:
  - lessons-learned
  - hub-lessons-learned
  - failure-mode-library
  - what-has-bitten-us-before
  - v-kai-pre-flight-checklist
description: "EXAMPLE MOC (invented lessons — replace with your own). The failure-mode library and V-Kai's mandatory pre-flight checklist: every lesson the project has paid for, consolidated. READ THIS BEFORE EVERY REVIEW. 2 lessons as of 2026-08-18."
metadata:
  node_type: moc
  type: reference
---

> ⚠️ **This is a shipped EXAMPLE with two invented lessons.** The file exists because **V-Kai
> dereferences it on every single pass** — a pre-flight that points at a missing file is a
> pre-flight that silently does nothing. Keep the file; replace the lessons with yours as you
> earn them.

# Lessons-Learned — the failure-mode library

**⛔ V-Kai reads this before EVERY review, and NAMES in its verdict which lessons it checked
against.** That naming is not ceremony: it is how dead lessons get pruned and hot ones get
reinforced. A library nobody cites is a library nobody is using.

**Capture → consolidate → apply.** Capture happens in the moment (a `feedback_*` memory as the
failure lands). Consolidation happens here, roughly every 20 lessons. **Apply is this file being
read before the review** — and apply is the step everyone skips, which is why a pile of notes
usually doesn't reduce the repeat-failure rate at all.

---

## L1 — A gate is theatre unless it is WIRED *and* FIRES on the branch you push to

*(2026-07-02 · found by V-Kai on the call-routing build · PORTABLE: yes)*

**What happened.** A validation script was written, tested by hand, and reported as "the gate is
in." It was in `package.json` and never referenced by CI. Three weeks later a malformed config
shipped to the beta. The gate had never run once outside the author's terminal.

**The sharper edge, found the same day.** A *second* gate WAS in CI — but the workflow triggered
only on the default branch, and all work happens on `feature/*`. It had never fired on a single
pull request. Both states look identical in a review: a file exists, it has assertions, someone
says "that's covered."

**Apply:**
- "The gate is in" is a done-claim and needs a receipt: a link to a CI run where it **executed**.
- Read the workflow's `on:` triggers, not just its steps.
- Prove it can catch: **mutate → watch it fail → restore → watch it pass.** Read the explicit
  failed-count and the failing check's NAME — a check that was filtered out or skipped is
  indistinguishable from one that ran and passed.
- Prove it can clear: one clean run through the same entry point CI uses, exit 0. A gate proven
  only to fail is not proven to work; an unpassable gate gets overridden rather than fixed.

**Rung:** L4 — the gate itself is the mechanism. The lesson is wired by the CI config, not by
anyone remembering this paragraph.

---

## L2 — A "no results" answer from a search is not evidence of absence

*(2026-07-29 · found on the missed-call audit · PORTABLE: yes)*

**What happened.** An audit concluded that no code path could drop an inbound call without logging
it. The evidence was a repo-wide search for `drop` that returned nothing outside the tests. The
real path used the word `abandon`, in a module the search's path filter excluded. A dropped call
had already happened twice in staging, silently.

**Why it is nasty.** An absence check returns empty on success **and** on total blindness. Nothing
distinguishes the two from the output. It is strictly worse than running no check at all, because
it converts an unverified claim into a *documented* one — and documented claims stop getting
re-checked.

**Apply:**
- Before writing "X appears nowhere", **prove the probe can find X where it legitimately exists.**
  Plant it, watch the search fire, remove it. Without that positive control, the zero means nothing.
- Enumerate the legitimate variants first — spelling, casing, synonyms, the term-of-art
  (`drop` / `abandon` / `miss` / `timeout`), and the localised forms if the product is translated.
- Write the claim **from the query**: paste the exact predicate beside the sentence, including its
  scope and its exclusions. "Nothing in the repo" and "nothing matching this regex under `src/`"
  are different claims, and only one of them is true.
- Ask of any absence claim: *what would this command have printed if it HAD happened?*

**Rung:** L2 — it lives as a named step in the V-Kai review checklist, because it is a judgement
about probe quality and cannot be fully mechanised. What *can* be mechanised — requiring a positive
control alongside every deny-probe — is written into the brief template's gates section (L3).

---

## How to add to this file

1. The lesson is **born** as its own `feedback_*` memory the day it happens, with the date, the
   real cost, and the actual nouns. That file is the STORY and it never gets deleted.
2. It is **consolidated** into this MOC at the next round-up (~every 20 lessons), compressed to
   what a reviewer needs at pre-flight.
3. If it survives the portability test — *delete every proper noun; is there still a rule?* — its
   domain-free form is **promoted** into `playbooks/`, with a plain-text provenance tag. Never a
   cross-vault wikilink: those are dead in a linked-note editor and mint 0-byte strays.
4. It is assigned an **enforcement rung** (`playbooks/playbook_enforcement_ladder.md`). Ask *"what
   EXECUTES this?"*, not *"where do we write it?"* **A lesson is not banked when it is written; it
   is banked when it reaches the rung where recall is no longer required.** A rule implicated in a
   REPEAT while sitting at L0–L2 gets promoted to a mechanism the same day — the repeat is a defect
   in the mechanism, not in the memory.
