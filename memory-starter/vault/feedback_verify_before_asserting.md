---
name: feedback_verify_before_asserting
aliases:
  - verify-before-asserting
  - dont-recall-external-facts
  - training-data-is-stale
  - how-do-i-know-this-api-still-works-that-way
description: "EXAMPLE MEMORY (invented — replace with your own). 🔒 STANDING RULE: external facts (APIs, pricing, SDK behaviour, regulations) are VERIFIED live before assertion, never recalled from training data; every claim carries a verified / recalled / inferred label. Cost of the miss that created it: a whole afternoon on an endpoint that had been retired."
metadata:
  node_type: memory
  type: feedback
---

> ⚠️ **This is a shipped EXAMPLE** — invented incident, real rule. It is here to show the SHAPE of
> a `feedback_` memory: the rule, the incident that bought it, **Why**, and **How to apply**.

## The rule

**Anything about the outside world gets verified before it is asserted. Anything about our own
decisions gets recalled from this vault — and the FILE gets re-read before it is quoted.**

Every claim carries one of three labels, spoken rather than implied:

| Label | Means | Evidence it carries |
|---|---|---|
| **verified** | I ran the command / read the file / hit the endpoint | the output, pasted |
| **recalled** | from memory or training — may have aged | where it came from + "verify before acting" |
| **inferred** | follows from X and Y *if both hold* | the joint, stated |

## The incident that bought it (2026-06-04)

A session confidently described the telephony provider's call-recording webhook payload from
training data, including a field that had been renamed eight months earlier. Roughly four hours
went into a handler for a shape that no longer existed. The provider's changelog said so on page
one. **One fetch would have cost thirty seconds.**

The tell, in hindsight: the claim arrived with no hedge and no source. Confidence is not a
correctness signal — it is a fluency signal, and fluent-and-wrong is exactly what recall produces.

## Verify vs recall

| Topic | Default |
|---|---|
| Third-party APIs, webhook payloads, SDK behaviour | **Verify** — fetch the current docs |
| Pricing and plan limits | **Verify**, every time |
| Regulations cited specifically (article, date, enforcement) | **Verify** |
| Our own conventions, our architecture, past rulings | **Recall** from this vault — it IS the source of truth |
| A memory's contents | **Re-read the file.** Memories age too; the index line ages faster |

## Why

The failure is asymmetric. A verified claim that turns out wrong is a bug with a trail you can
follow. A **recalled** claim that turns out wrong is indistinguishable from a correct one until
something downstream breaks — and by then it has usually been copied into a brief or a doc, where
it becomes a premise nobody re-checks.

## How to apply

- Prefix external-service assertions with the label: *"Verified via fetch, 2026-08-18: …"*
- If the principal pushes back on a fact, **go and check** — never double down from training data.
- If the topic is fast-moving (model APIs, pricing, anything under a year old), check *without*
  being pushed.
- The label **travels with the claim into documents and memories.** An unlabelled guess written
  into a brief becomes a "fact" three weeks later. That is how premise rot breeds.

**Related:** `playbooks/playbook_verification_doctrine.md` (rules 8, 9) ·
`playbooks/playbook_fable_failure_modes.md` (Class 3 — premise rot).
