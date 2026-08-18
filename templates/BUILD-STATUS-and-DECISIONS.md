# The two coordination files — `BUILD-STATUS.md` and `DECISIONS-PENDING.md`

These are the cheapest pieces of infrastructure in the whole pattern, and the two that make
**coordination without chat** actually work. Both live in `docs/`. Copy the shapes below.

They solve different problems and must not be merged into one file:

| File | Answers | Written by | Read by |
|---|---|---|---|
| `BUILD-STATUS.md` | *"what has shipped, and what is in flight?"* | I-Kai (ticks its own work); S-Kai if I-Kai slips | Everyone, every session |
| `DECISIONS-PENDING.md` | *"what is waiting on a human ruling?"* | S-Kai | The principal, in one batched pass |

---

## 1. `docs/BUILD-STATUS.md`

A table I-Kai ticks as work ships. It lets S-Kai see progress **without a chat relay** — the tick
commit IS the signal. It is also where gate telemetry accumulates, which is what eventually
justifies deleting a gate that has stopped catching things.

```markdown
# BUILD STATUS

Legend: 🟢 shipped · 🟡 in progress · ⛔ blocked · ⚪ not started
I-Kai ticks its own rows. If I-Kai slips, S-Kai ticks on its behalf.

## Current milestone: <name>

| Item | Brief | Branch | State | Commit | Notes |
|---|---|---|---|---|---|
| Retire `/pricing-old` | `BRIEF-I-KAI-PRICING-RETIRE.md` | `feature/retire-pricing-old` | 🟢 shipped 2026-08-18 | `abc1234` | merged; redirect asserted in e2e |
| Webhook idempotency | `BRIEF-I-KAI-WEBHOOKS.md` | `feature/webhooks` | 🟡 in progress — steps 1-3 of 5 | — | see progress note at brief bottom |
| Tenant-isolation audit | — | — | ⛔ blocked | — | needs ruling D2 |
| Restore drill | — | — | ⚪ not started | — | before launch |

## Gate telemetry
> A gate that stops catching things gets DELETED. Record the zeros too — that is the data
> that licenses removal.

| Date | Gate | Wall-clock | Findings |
|---|---|---|---|
| 2026-08-18 | brief review (pricing-retire) | 12 min | 2 MAJOR, 1 MINOR |
| 2026-08-18 | build review (pricing-retire) | 40 min | 1 BLOCKER |
```

**Three rules that keep it honest:**

- **Tick from an artefact you just observed, never from intention.** A status claim fails silently
  and indefinitely: nothing errors, nothing regresses, and the bill lands months later. Put the
  commit sha in the row.
- **A partial state is a legitimate state.** `🟡 in progress — steps 1-3 of 5, see brief note` is
  worth more than a blank row, and it is what makes a low-context handoff recoverable in minutes.
- **Never round a suite to N/N.** If 20 tests failed and they are identical on trunk, write
  *"1439/1459 — the 20 failures are identical on trunk"*. That is a **stronger** claim than "all
  green" and costs one extra command. A rounded-up number is indistinguishable from one hiding a
  real regression.

---

## 2. `docs/DECISIONS-PENDING.md`

The principal cannot take interrupts all day. Anything needing a ruling accumulates here **with
enough context to answer cold**, and gets cleared several at a time instead of one round-trip each.
Only genuinely blocking items interrupt.

```markdown
# DECISIONS PENDING

Answer these cold — each entry carries its own context. Reply inline (a line under the entry is
enough) and S-Kai will action + close it.

---

## D4 — Should the alert scanner run 1× or 2× daily? — ⏳ OPEN (raised 2026-08-14)

**The question:** how often should the price-alert cron scan?

**Options**
| | Frequency | Cost | User value |
|---|---|---|---|
| A | 1×/day, 06:00 UTC | ~£0.60/mo at 20 watched routes | catches daily moves only |
| B | 2×/day, 06:00 + 18:00 | ~£1.20/mo | catches AM/PM swings |
| C | adaptive: 1×/day, 3× when within 10% of target | variable, ~£0.90/mo | highest |

**Recommendation:** B. C is better in theory but adds a state machine we would have to verify,
and the delta over B is unmeasured.

**Blocked on this:** the scanner brief cannot be written; 2 items in BUILD-STATUS are ⛔.

**Ruling:** _<principal writes here>_

---

## D3 — Locale coverage at launch — ✅ CLOSED 2026-08-05

**Ruling (principal):** English-first launch; the locale gate is WAIVED for v1.
**Actioned:** captured as `project_launch_language_ruling`; gate marked advisory in CI.
```

**Four rules that make it work:**

- **Answerable cold.** Question + options + recommendation + what is blocked. If the principal has
  to open three files to answer, the entry is not finished.
- **Recommend.** A queue of open questions with no recommendation is a to-do list handed upward.
  Deference dressed as rigor is still deference — make the call you can make and mark it.
- **⛔ Before adding an entry, check for a CLOSED one on the same ground.** A re-ask of settled
  ground is a process defect. This file plus a `search_memory` is the two-second check.
- **Close in place, stamped and dated.** Never delete a ruling — the progression is the record.
  And when a ruling lands, capture it as a memory in the **same beat**; this file is the queue, the
  vault is the memory.
