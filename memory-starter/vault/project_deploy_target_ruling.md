---
name: project_deploy_target_ruling
aliases:
  - deploy-target-ruling
  - which-region-do-we-deploy-to
  - single-region-eu-west
  - multi-region-decision
description: "EXAMPLE MEMORY (invented — replace with your own). 🔒 LOCKED 2026-08-12: single-region deploy, EU-west, one primary database, no read replicas. Multi-region is REJECTED for now — not on cost, on the solo-maintainability constraint. EXIT-EVENT: the first paying customer outside the EU. Do not re-ask; read this file first."
metadata:
  node_type: memory
  type: project
---

> ⚠️ **This is a shipped EXAMPLE** — invented ruling, real shape. It demonstrates the two things a
> `project_` memory must carry that a `feedback_` one need not: a **dated status stamp** and a
> **machine-checkable exit condition**.

## The ruling (2026-08-12, principal)

**Single region: EU-west. One primary database. No read replicas. No multi-region anything.**

> *"I can't be woken up by a replication lag alert in a region I've never visited. If it can't be
> fixed from a phone in a van, we don't run it."*

## Why — and note that it is NOT the reason you'd expect

The rejection is **not** about cost; the multi-region bill would have been about £40/month, which is
affordable. It is about the **solo-maintainability constraint** in `user_profile`: every piece of
infrastructure has to be one that a single non-specialist can reason about at 7am. Cross-region
replication fails in ways that require a second engineer to diagnose, and there is no second
engineer.

Recording the *real* reason matters more than recording the decision. A future session reading only
*"multi-region: no"* will happily re-propose it the moment the cost argument changes — and the cost
argument was never the argument.

## How to apply

- Anything that assumes a second region is out of scope until the exit condition fires.
- Latency work goes to caching and payload size, never to moving compute closer.
- If an external service offers a "multi-region by default" tier, that is a **downgrade** against
  this constraint, not an upgrade. Say so explicitly rather than treating it as free.

## Status

**🔒 LOCKED (as of 2026-08-12.)**

**EXIT-EVENT:** the first paying customer whose users are outside the EU.
**EXIT-CHECK:** `SELECT count(*) FROM customers WHERE billing_country NOT IN (<EU set>)` returns > 0.

When that fires, this file gets **re-opened and re-ruled** — it does not get deleted, and it does
not silently lapse. The description line above gets its status word changed **in the same edit** as
the body, because a stale description outranks an updated body in semantic recall and will keep
answering the question with the old ruling.

**Superseding, if it ever comes:** keep this file, add `⛔ SUPERSEDED by <file> (date) — kept for
progression` at the top, prefix the description with `SUPERSEDED <date> —`, and then sweep the vault
for the old literal (`single-region`, `EU-west`) and correct or stamp every hit. The sweep is the
part that actually defends recall; the stamp on its own does not.
