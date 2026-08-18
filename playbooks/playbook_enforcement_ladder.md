# THE ENFORCEMENT LADDER — a lesson is banked at a RUNG, not in prose

*Domain-free craft law. First seen: sabaifly · the worktree-exclusivity repeat · 2026-08-03.
Provoked by Gareth's direct question: "Learning a lesson and then making the same mistake an hour
later is what we need to eradicate — is it a model thing or something we can improve in the
skills/CLAUDE.md files?"*

## The finding that forces this doctrine

Four dated incidents, one shape:

| Date | Rule | Where it was written | Failed anyway at |
|---|---|---|---|
| 2026-07-25 | brain-is-source-of-truth | vault mandate, CLAUDE.md | brief-writing (2× REWORK, TDAC unactioned 2 months) |
| 2026-08-01 | site-not-live | **CLAUDE.md dedicated section AND its own memory** | decision-framing ("linked from an indexed hub?" — no hub is indexed) |
| 2026-08-02 | standing law outranks a permission default | written, indexed, AND recalled | dispatch (brief shipped unreviewed, gap disclosed as a footnote) |
| 2026-08-03 | mutating agents get an EXCLUSIVE worktree | banked **~1 hour earlier, still in the context window, self-written** | dispatch (second writer fanned into an occupied tree → a FALSE finding against a correct brief) |

The 08-03 case is the controlled experiment: **recall was 100%** — the rule was not merely in the
vault, it was in working context, an hour old, written by the same agent that then violated it.
So *"search the brain harder"* and *"write it more emphatically"* target a layer that did not fail.

**The counter-evidence is just as clean.** Every moment that got wrapped in a MECHANISM stopped
producing repeats: V-Kai's mandated pre-flight (the role that "reliably catches things"), the brief
template's required fields, the merge gate, the 08-01 DECISION PRE-FLIGHT (zero framing repeats
since). Same model on both sides of that line. **The discriminating variable is never the model,
the wording, or the recall — it is whether the MOMENT OF ACTION has a mechanism.**

## Why prose fails at the action moment (the honest mechanics)

1. **Attention is task-shaped, not rule-shaped.** At the moment of dispatching "clear gate-fares",
   working attention holds token classes, fences, the complement rule. "Is another agent writing to
   this tree?" is not part of that task's surface form, so nothing summons it. Checking is itself an
   action, and actions need triggers.
2. **Prose encodes WHAT; expertise is WHEN.** "Exclusive worktree for mutators" does not lexically
   match "dispatch a workflow to clear a gate." The applicability inference only fires if something
   forces it. This is the condition-action gap, and it is why knowing a rule and applying it are
   different capabilities.
3. **Flow is the enemy.** The violation moments are always high-throughput, multi-task,
   autonomous-mode moments — exactly when per-action deliberation is lowest. This is not a silicon
   defect: it is why aviation and surgery use checklists *on experts specifically*. Experts under
   flow skip steps they know cold.
4. **Model choice modulates, mechanism eliminates.** A stronger model lowers the base rate but keeps
   the class; a faster, more confident model raises exposure per hour. And the platform's own
   engineering docs state the conclusion: automated always/never behaviours must be hooks because
   *"the harness executes these, not Claude — memory/preferences cannot fulfil them."*

## The ladder

A rule climbs DOWN this ladder as soon as its class has been paid for once. Each rung reduces how
much the moment depends on recall; the bottom rungs need none.

| Rung | Lives in | Survives | Fails when |
|---|---|---|---|
| **L0** | a vault memory | sessions | recall doesn't happen |
| **L1** | always-in-context prose (CLAUDE.md, skill preamble) | context assembly | salience loses to the task (proven 08-01) |
| **L2** | a checklist bound to a NAMED MOMENT in a role skill | flow — *if* the moment is structured | the ritual is skipped or decays |
| **L3** | a MANDATORY field in the action's own template | skipping — the action can't complete unfilled | the template isn't used |
| **L4** | a harness-executed interlock (hook, CI gate, lint, test) | everything — executes WITHOUT the model's cooperation | the interlock itself is theatre (so it gets the mutate→fail→restore proof like any gate) |
| **L5** | a safe DEFAULT / impossible-by-construction (isolation-by-default, quoted-heredoc-only, generated code, types) | everything — the rule is no longer needed | — |

**Terminal rung by rule type:**
- **FACTS** (site-not-live, branch topology, endpoints) → L1 is correct and sufficient *as reference*;
  any BEHAVIOUR derived from a fact still needs its own L2+ at the moment that behaviour happens.
- **JUDGMENT/FRAMING rules** (severity framing, decision pre-flight, tone) → **L2 is the floor and
  usually the ceiling** — they cannot be mechanised, so they live IN the moment's own instruction,
  ≤3 questions, in the role skill. The 08-01 decision pre-flight is the proven template.
- **ACTION-SHAPE rules** (worktree isolation, git hygiene, commit format, allowlist edits) →
  **L3–L5. These should leave prose entirely.** Every action-shape rule still sitting at L0–L2 is
  scheduled to fail again.

## Operating rules

1. **At harvest, every NEW-LESSON gets a rung assigned** — the question is "what EXECUTES this?",
   not "where do we write it?" A lesson without a rung is a note, not a defence.
2. **A repeat while at L0–L2 forces same-day promotion to L3+.** The repeat is a mechanism defect,
   not a memory defect — respond by moving the rule down the ladder, never by rewriting it louder.
3. **Prefer converting silent failures to LOUD ones over adding rules.** A quoted heredoc that
   errors immediately needs no discipline; a backtick that silently eats a phrase needs a rule
   forever. Loud failures self-correct.
4. **≤3 questions per L2 gate.** Checklists longer than a breath decay into pattern-matched ritual —
   which is itself the L2 failure mode. If a moment needs more than 3, split the moment.
5. **External challenge beats self-attestation.** The reliable rule-appliers in this system are the
   ones whose ENTIRE TASK is rule application (V-Kai; a hook; a template validator). When a rule
   matters, make its checking someone's whole job at that moment — a separate agent, the harness, or
   a field that must be filled — never a background intention.
6. **Every mutation receipt carries an environment disclosure** (start/exit `git status` + "files I
   did not create"). Detection is the layer that already works — keep it working.

## The one-sentence answer

**You do not stop an intelligence — silicon or carbon — from making a known mistake by helping it
remember; you stop it by changing the environment so the moment of action either asks the question
itself or cannot express the error at all.** The smart human Gareth describes is not the one with
the better memory; it is the one who installs the interlock.
