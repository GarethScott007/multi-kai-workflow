# BRIEF TEMPLATE — the S-Kai → I-Kai contract

Copy this to `docs/BRIEF-I-KAI-<TOPIC>.md`. S-Kai writes it, **V-Kai reviews it**, I-Kai executes it.

The brief is a contract. A good one means I-Kai needs zero clarification mid-execution — and, just
as important, means V-Kai can tell whether it targets the right thing at all. **Roughly a third of
the origin project's REWORK verdicts landed on briefs, not builds** — catching a wrong brief costs
minutes; catching it after an implementer has burned a session costs hours.

---

## ⛔ Before you write a word — the two pre-flight laws

These sit ABOVE the numbered sections because they govern the whole document. Skipping either is
the single most expensive brief-writing mistake in the record.

### 1. Existence-probe every symbol, module path and file the brief names

Grep the export; note `module:line`. **A brief that names a symbol it never probed is not
review-ready.** Promoted to a template law 2026-08-08 after the class fired *inside* a brief: it
anchored a helper to the wrong module, put a constant in a module where it is actually derived
elsewhere, and anchored a dead map entry to a third wrong file — three wrong-module builds V-Kai
had to catch.

**⚠️ The probe covers files the brief claims to CREATE.** An existing file at the creation target —
especially one with early-return guards — silently converts "create" into "extend before the
guards," and the natural append placement can no-op the feature exactly where it must fire.
Probe the creation path too.

### 2. Any change-every-occurrence task carries its FRESH sweep predicate

If the brief says "update every X", it must (a) include the exact search command that produced the
occurrence list, (b) instruct the build to **RE-RUN it**, and (c) say *read each hit* — because grep
counts lie. **A list recalled from a prior audit under-enumerates**, and re-creates the
surviving-instance defect the task exists to fix.

V-Kai's counterpart: it re-runs your predicate independently and set-diffs your enumeration
(changed ∪ deliberately-untouched) against its own hit list. A hit in neither column is an
undispositioned miss, by construction — dead code included.

### 3. GATE 0 — sweep the brain first

`search_memory` for the subsystem, the established convention, and any prior decision on the topic.
Fold what you find into the brief with links. **V-Kai hard-rejects a brief with no sweep evidence**
— a brief is where a re-derivation gets *institutionalised*, because it then directs an implementer
for hours.

---

## The template

```markdown
# BRIEF — I-Kai — <TOPIC>

**Status:** DRAFT → V-Kai brief review → I-Kai
**Date:** YYYY-MM-DD · **Author:** S-Kai · **Principal:** <name>
**Working copy:** <repo path / worktree path — this MUST also appear in the first chat message,
not only here>
**Branch:** <branch to build on>
**Vault sweep consulted:** <memory slugs / playbooks found, or "nothing relevant existed">

## 1. Goal
One paragraph. What does success look like, in the world, when this is merged?

## 2. Why
The strategic motivation — so I-Kai can make judgement calls when something is ambiguous
rather than guessing or stalling.

## 3. Scope — IN
Numbered, explicit. Each item existence-probed (see pre-flight law 1) with `module:symbol`
anchors. If an item is "change every occurrence of X", paste the sweep predicate here.

## 4. Scope — OUT
Explicit. The things a reasonable implementer might otherwise pull in.
⚠️ Cross-check IN against OUT **by data flow, not by filename**: if anything IN changes a value
an OUT item reads, the OUT declaration is void. Convert each surviving OUT item into a stated
frozen-contract invariant ("shape X is FROZEN; verify by <grep>") or pull the reader in.

## 5. Files to touch
Anchor paths so I-Kai doesn't go hunting.
⛔ **Standing entry — always include:** `docs/BUILD-STATUS.md` (the I-Kai status-tick protocol).
Without it, any conformance gate of the form `diff ⊆ allowlist` structurally fails on every build.

## 6. Gates
Typecheck / lint / tests / smoke / manual checks. For each **binary** gate, state:
  - the command,
  - the expected output,
  - its **negative control** (mutate → must FAIL → restore → must pass again),
  - and its **positive/pass path** (a clean run through the same entry point CI uses, exit 0,
    with the all-clear output asserted).
A gate proven only to fail is not proven to work; a gate proven only to pass is not proven to
catch. One limb without the other carries no information in that direction.

## 7. Done definition
What "shipped" means: commits on <branch>, gates green with receipts pasted, BUILD-STATUS ticked,
completion note at the bottom of this file, pushed.

## 8. Estimated effort / recommended model
<e.g. 2-3h · top tier — judgement-heavy> — see playbooks/playbook_model_tiering.md

## 9. Memories to stamp on merge:
⛔ MANDATORY, NEVER BLANK. List the memory files whose blocked / queued / NOT-built / pending
claims this build will falsify — or write `NONE — <reason>`.
V-Kai hard-rejects a brief that is missing this field or leaves it blank.

## 10. Negative limbs
Every unblock / acceptance condition states its NEGATIVE limb IN ADVANCE:
not "find X", but "find X, **OR** record with apparatus that X is absent — and here is what that
absence licenses." A pre-authorised null is a decision. An unanticipated null is an item stuck at
held-forever, and retro-fitting the limb after a disappointing result invites the result to shape
the standard.

## 11. Completion note (I-Kai writes this section)
Per-item disposition · each gate's ACTUAL output · what was NOT tested · every shortcut taken ·
environment disclosure (start/exit `git status` + "files I did not create").
Write it for a skeptic who will try to break it.
```

---

## The 11 conventions, and why each one exists

| # | Convention | The failure it prevents |
|---|---|---|
| 1 | **Goal** — one paragraph | A brief with no stated outcome gets built to the letter and misses the point |
| 2 | **Why** | Without it, ambiguity becomes a stall or a guess instead of a judgement call |
| 3 | **Scope IN**, existence-probed | Wrong-module builds; "create" silently becoming "extend before a guard" |
| 4 | **Scope OUT**, data-flow-checked | A brief that freezes a reader while mandating a change at its writer is unbuildable — and whichever instruction the builder picks, a gate silently dies |
| 5 | **Files to touch** + the standing BUILD-STATUS entry | I-Kai hunting; and a conformance gate that fails on every build for a bookkeeping reason |
| 6 | **Gates** with both control limbs | An unfalsifiable absence-check is *worse* than none — it converts an unverified claim into a documented one |
| 7 | **Done definition** | "Done" quietly meaning "the parts that went well" |
| 8 | **Effort + model** | Context exhaustion mid-session, or top-tier tokens on mechanical work |
| 9 | **`Memories to stamp on merge:`** | Vault rot. Writing a memory is part of a workflow; *stamping* one was part of no workflow at all — median lag 1–6 days, some closed the same day they were written |
| 10 | **Negative limbs** | Items stuck at held-forever, and standards that get shaped by disappointing results |
| 11 | **Completion note for a skeptic** | "I checked, it's clean" is not evidence; the pasted output is |

---

## Worked mini-example

A real-shaped small brief. Note that every anchor carries a probe receipt, the sweep predicate is
literal, the gate has both control limbs, and section 9 is answered rather than left blank.

```markdown
# BRIEF — I-Kai — RETIRE THE LEGACY `/pricing-old` ROUTE

**Status:** DRAFT → V-Kai brief review → I-Kai
**Date:** 2026-08-18 · **Author:** S-Kai · **Principal:** <name>
**Working copy:** <repo>/../wt-pricing-retire  (dedicated worktree — mutating build)
**Branch:** feature/retire-pricing-old
**Vault sweep consulted:** `project_pricing_locked` (prices are ruled, do NOT restate them here);
`feedback_dead_exports_still_ship` (removal = sweep the derivation chain, not just the page).

## 1. Goal
`/pricing-old` stops serving and 301s to `/pricing`. No surface anywhere still links to it, and
the redirect is asserted by a test, so the route cannot quietly come back.

## 2. Why
Two live pricing pages disagree on the tier names since the pricing ruling. The old one is the
wrong one. It is reachable from the footer on 3 locales, so it is not dead code — it is a live
contradiction.

## 3. Scope — IN
1. Delete `app/(marketing)/pricing-old/page.tsx`  (PROBED: exists, 141 lines, default export
   `PricingOldPage`).
2. Add the 301 in `next.config.mjs::redirects` (PROBED: `redirects()` exists at :52, currently
   returns 4 entries).
3. Remove every inbound link. **Fresh sweep predicate — RE-RUN IT, read each hit:**
   `rg -n --hidden -g '!node_modules' -g '!.git' "pricing-old"`
   At write time this returned 7 hits across 5 files (3 locale message files, the footer
   component, one e2e spec). **Re-run before you start: the list may have moved.**
4. Add an e2e assertion that `/pricing-old` responds 301 with `location: /pricing`.

## 4. Scope — OUT
- The prices themselves. They are 🔒 ruled — see the vault. Do not restate, reformat or "tidy" them.
- `/pricing` layout or copy. Read-only.
  ⚠️ Data-flow check: nothing IN writes a value `/pricing` reads. The two pages share only the
  `tiers` constant, which this brief does not touch. FROZEN — verify with
  `git diff -- lib/pricing.ts` returning empty.

## 5. Files to touch
`app/(marketing)/pricing-old/page.tsx` (delete) · `next.config.mjs` · `components/Footer.tsx` ·
`messages/{en,de,fr}.json` · `e2e/redirects.spec.ts` · `docs/BUILD-STATUS.md` (standing entry)

## 6. Gates
- `pnpm typecheck && pnpm lint` — clean.
- `pnpm test:e2e -- redirects` — the new assertion passes.
  **Negative control:** comment out the redirect entry in `next.config.mjs` → the spec MUST fail,
  and you must read the explicit failed-count and the failing test NAME (a filter that skipped it
  is indistinguishable from a pass). Restore → green again.
  **Pass path:** the same `pnpm test:e2e -- redirects` invocation CI runs, exit 0.
- Re-run the sweep predicate from §3.3: **zero** hits outside `next.config.mjs` and the e2e spec.
  Paste the command and its output.

## 7. Done definition
Commits on `feature/retire-pricing-old`; all gates green with output pasted; BUILD-STATUS ticked;
completion note written; branch pushed.

## 8. Estimated effort / recommended model
~45 min · mid tier — mechanical, the reasoning is in this brief.

## 9. Memories to stamp on merge:
`project_pricing_locked` — its description still says "two pricing pages live, old one pending
retirement (as of 2026-07-30)". This build falsifies that clause.

## 10. Negative limbs
§3.3: if the sweep finds an inbound link in a file this brief does NOT list, **do not silently
fix it and do not silently skip it** — record the path, fix it, and name it in the completion note
as an out-of-allowlist edit. If it finds a link in generated output, STOP and escalate: the
generator is the real target and this brief is aimed at the wrong layer.
```

---

## Reviewer's checklist (what V-Kai will do to this document)

1. **Right-target lens** — is this the correct thing to build? Premise current? Scope right, or stale/over-broad?
2. **Executable lens** — could a fresh implementer build it AS WRITTEN without flailing?
3. **Hard reject** if there is no vault-sweep evidence.
4. **Hard reject** if `Memories to stamp on merge:` is missing or blank. Blank is not an answer.
5. Re-run every existence probe and every sweep predicate independently.
6. Check that each binary gate has BOTH control limbs, and that the negative control varies only
   the property under test (a control that shares a short-circuit with an earlier predicate proves
   nothing).
7. Cross-check §3 against §4 by data flow, and each requirement's true file-set against §5's
   allowlist — in both directions.

Loop cap ~2 rounds. A round-2 failure, or trading one failure for its opposite, means the
*approach* is wrong → escalate to the principal, don't grind.
