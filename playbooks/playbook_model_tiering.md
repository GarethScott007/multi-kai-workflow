---
name: playbook_model_tiering
aliases:
  - model-tiering-portable
description: "PORTABLE playbook — which model runs which seat (local Qwen tier-0 → Haiku → Sonnet → Opus default → Fable as bounded ORACLE for adversarial adjudication only); explicit model overrides on every workflow agent, never inherit."
metadata:
  node_type: memory
  type: reference
---

# Model tiering — portable doctrine (updated 2026-07-12)

Hard-won across a June/July window with a top-tier model on metered access. The principle: **the top model buys judgment, not throughput** — burning it on mechanical work starves the seats only it can fill.

> **⏱️ DATED EXAMPLE — REFRESH PER DEPLOYMENT.** The model names below are the ones this
> partnership ran in **2026-07**, recorded so the tier assignments stay concrete. Names,
> versions and context sizes rot within months. **The five TIERS and the six rules under them
> are the durable part** — re-map the names onto whatever your provider ships when you read
> this, and leave the seats alone.

| Tier | Model (as of 2026-07) | Seats | Cost posture |
|---|---|---|---|
| 0 | **A small local open-weights model on your own hardware** (an ~8B-class model behind a local OpenAI-compatible endpoint) | Bulk mechanical drafts: translation first-passes, summarisation, tag/format extraction, high-volume classification. Output ALWAYS verified by a higher tier before it ships. | Free, private, can't be taken away |
| 1 | **Haiku 4.5** | Structured passes with zero judgment: lint sweeps, renames, format conversions, list transforms | Cheapest API tier |
| 2 | **Sonnet (5 / 4.6)** | Mechanical-with-a-tight-brief: finder fleets, coverage sweeps, coroner harvests, <90-min builds where the brief carries the reasoning | Cheap; DEFAULT for workflow finder/mechanical agents |
| 3 | **Opus (4.8)** | DEFAULT driver: builds, fix loops, synthesis, routine verification, S-Kai sessions when tier 4 is unavailable | Plan allowance |
| 4 | **Fable 5** (or whatever the current top model is) | **ORACLE ONLY**: adversarial adjudication of compounding-if-wrong artifacts — brief red-teams, template-defining reviews, hardest content-integrity panels. Bounded single questions, never open-ended fleets, never a default driver on metered credits. | Metered — every call deliberate |

## The rules (each one paid for in real money)

1. **Every workflow agent gets an EXPLICIT `model:`** — subagents inherit the session model by default; a 92-agent fleet inheriting the top tier ate ~10-15% of a weekly allowance in one run (2026-06-12).
2. **Fable-as-oracle** (formalised 2026-07-12): when the top model is metered, don't buy sessions — Opus runs everything and dispatches ONE bounded top-tier subagent to adjudicate a single flagged hard-judgment item. The unit of spend is a question, not a session. (The API's "advisor tool" is this exact pattern, productized.)
3. **Distill before the window closes**: top-model access is volatile — 2026-06-12 proved a frontier tier can vanish overnight on a decision nobody in the partnership controls. While you have it, have it WRITE durable artifacts — rubrics, lens prompts, failure-mode banks — that cheaper models execute later. Judgment captured as a checklist survives the model that produced it.
4. **Hard multi-round adversarial reviews burn pots fast** (a 4-round template review consumed £75). First artifact of a class gets the expensive review; its lessons become the pre-flight for the rest of the class — expect FEWER rounds each time.
5. **Brief sizing**: >2h / 8+ items / judgment-heavy → Opus. <90min mechanical with reasoning in the brief → Sonnet. <30min structured → Haiku (or tier 0 + verification). Estimated burn > ~85% of the model's context → upgrade or split. When in doubt, Opus.
6. **Tier-0 discipline**: the local model is free but unverified — it drafts, it never decides. Pair every tier-0 bulk pass with a spot-check ritual from tier 2+.
7. **Every tier assignment is re-checked when your provider ships a new generation.** A tier is a job description; a model name is this quarter's answer to it.

Related: [playbook_multi_kai_pipeline](playbook_multi_kai_pipeline.md) · [playbook_fable_failure_modes](playbook_fable_failure_modes.md)
