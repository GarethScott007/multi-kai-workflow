---
name: playbook_fable_failure_modes
aliases:
  - fable-failure-modes-portable
  - fable-only-catches
description: "PORTABLE playbook — the failure-mode bank of what Fable-tier review caught that Opus-tier missed (entailment drift, authority-padding, unenumerated egress, premise rot). Written BY Fable 5 on its last subscription day (2026-07-12) so cheaper models can hunt these by name."
metadata:
  node_type: memory
  type: reference
---

# The Fable failure-mode bank

Written 2026-07-12 by the top-tier model the partnership was then running, distilling what its adversarial review seats caught in June–July that cheaper-tier panels demonstrably missed. The pattern behind every entry: **Opus verifies surface form; these bugs live one level down, in entailment, enumeration, or premise.** Prompt any review panel with these BY NAME — a named failure mode gets hunted; an unnamed one needs instincts.

## Class 1 — Entailment drift (content integrity)

The claim passes every mechanical check but is not actually LICENSED by its source.

- **1a. Unentailed superlatives/rankings.** Composed prose asserts centrality or rank ("the most important temple", "the city's premier market") where the source only establishes existence or popularity. *Check: for every superlative/comparative/ranking word, demand the exact source sentence that licenses THAT strength of claim. Derive from the QUOTE only, never from the sign-off shorthand around it.* (Phuket red-team: 3 BLOCKERs of this class.)
- **1b. Authority-padding.** Unearned credentials, invented institutional weight, or borrowed authority inserted during composition — including by the strategist itself while editing (one confirmed S-Kai-introduced instance). *Check: every authority claim ("experts say", "officially designated", credential mentions) traced to a verified fact card; no card → cut.*
- **1c. Hedge-stripping via quotation.** A substring quote drops the source's hedge ("possibly the oldest…" → "the oldest…"). *Check: inspect the LEFT boundary of every quoted fragment against the full source sentence; the hedge is part of the claim.*
- **1d. Promotion laundering.** Sign-off shorthand ("approve the temple batch") launders words into Facts that no individual decision covered; items silently drop when the id list isn't diffed in full. *Check: diff the FULL id list per decision group; promote from quotes, not from decision labels.*

## Class 2 — Unenumerated egress (coverage integrity)

A gate is verified on the channels someone THOUGHT OF; the leak ships through the channel nobody listed.

- **2a. The forgotten channel.** Gating verified on pages/payloads while the same data egresses via the AI prompt channel and a secondary content route (the 2 live egresses Fable found 07-01/02 that prior Opus review passed). *Check: FIRST enumerate every egress channel for the datum (pages, API routes, RSC payloads, prompts sent to models, feeds, sitemaps, structured data, emails) — THEN verify the gate on each. Coverage of an unenumerated set is not coverage.*
- **2b. Adjacent-surface leak.** The fix is verified on the surface named in the brief while the identical datum sits ungated on a sibling surface (country hub vs city hub vs pricing). *Check: grep the DATUM repo-wide, not the fixed FILE.*
- **2c. Narrative field rides the whitelist.** A field-level projection/strip nulls the structured fields but RETAINS a composed narrative field — which carries the very claim classes the strip exists to remove (2026-07-12: `toJourneyOnlyRoute` nulled `keyFacts.priceRange` yet kept `quickAnswer` prose asserting prices, visa figures, seasons and carrier ownership, on three egress channels at once; the docstring said volatile facts weren't kept — true of the fields, false of the prose). *Check: classify every KEPT field structured-vs-narrative; run the banned-pattern greps (visa \d+ days, currency figures, month-ranges, ownership/superlatives, carrier names) over the narrative ones; a strip is verified against the prose it keeps, not the fields it nulls.*

## Class 3 — Premise rot (mechanism integrity)

The reasoning is sound; the ground it stands on has moved.

- **3a. Stale-premise briefs.** A brief inherits a fact from an earlier session that is no longer true (a ten-field schema premise, five dead redirect targets — both caught at the brief gate before an implementer burned a session on them). *Check: re-derive every load-bearing premise from CURRENT source at review time; a brief is only as good as its freshest grep.*
- **3b. Count-right, mechanism-wrong.** The reported number matches, so the explanation is accepted — but the attributed mechanism is false, and the next change breaks it invisibly. *Check: verify the MECHANISM independently of the count; make the code path show itself (trace one instance end-to-end).*
- **3c. Dormant-assumption revival.** A conclusion cached from an earlier state ("that prop is unused") is applied after the state changed. *Check: re-grep the current line before acting on any remembered property of the code.*

## How to deploy this bank (post-Fable era)

1. Every review panel's prompt includes the class names relevant to the artifact (content artifact → Class 1+2; code/brief → Class 2+3).
2. Verifiers report per-class: attacked / found / clean-with-evidence.
3. When the top tier is available as a bounded oracle ([playbook_model_tiering](playbook_model_tiering.md)), spend it ONLY on items these mechanical hunts flag as ambiguous — the bank narrows the oracle's docket.
4. A new top-tier-only catch → a new entry HERE, the same day. This bank is the model's judgment surviving the model's access.

Related: [playbook_verification_doctrine](playbook_verification_doctrine.md) · [playbook_model_tiering](playbook_model_tiering.md)
