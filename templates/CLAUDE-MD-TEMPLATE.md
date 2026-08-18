# `CLAUDE.md` STARTER TEMPLATE — your project's always-in-context instructions

Copy this to `CLAUDE.md` in your repo root. **Write it in week one** — it is step 5 of the
bootstrap, and every later piece of the pattern defers to it.

`CLAUDE.md` is loaded into **every** session in this repo, so it is the **L1 rung** of the
enforcement ladder (`playbooks/playbook_enforcement_ladder.md`): it survives context assembly, but
it loses to the task when salience is low. That has a sharp consequence you should design around:

> **`CLAUDE.md` is the right home for FACTS.** For *behaviours*, it is the wrong home on its own —
> a behaviour needs a gate at the moment it happens (a checklist in a role skill, a mandatory
> template field, or a hook). The measured proof: one project had a rule in a **dedicated
> `CLAUDE.md` section AND as its own memory**, and still broke it at the decision-framing moment,
> because nothing at that moment asked the question.
>
> So: put the fact here, and put the *behaviour derived from the fact* into the skill/template/hook
> that fires when it matters. Cross-reference the two.

Keep it under ~300 lines. A `CLAUDE.md` nobody finishes reading is an unloaded gun.

---

```markdown
# <PROJECT> — Claude Code Instructions

**Last updated:** YYYY-MM-DD
**What this is:** <one line — what the product does and for whom>
**Current stage:** <pre-launch / private beta / live>
**Operative plan:** `docs/HANDOFF-<latest>.md` — boot from it.

---

## ⚠️ SEVERITY FRAMING — read before writing "critical" anywhere

<Delete this whole section once it stops being true — and it WILL stop being true, so put an
exit condition on it.>

**<PROJECT> is not live. There are zero users.** Therefore:

- NEVER frame a finding as "users at risk" / "serving users now" / "emergency".
- Ask BEFORE any severity language: **(1) has it shipped to real users? (2) is the surface
  actually reachable?** Both NO → pre-launch framing: quality work, done right, zero fires.
- **External reports inherit no urgency.** A subagent or third-party scan claiming "live
  exposure" gets re-based against this section before it is relayed.

**EXIT: delete this section on the day <the launch event> happens.**

> **Why this section exists as a pattern, not just a fact.** Every project has a class of
> constraint it has not reached yet, and models reliably borrow urgency the situation does not
> have — inventing risk from a world that doesn't exist yet, because the *shape* of the finding
> matches a real production incident. Naming your not-yet class in writing, once, kills a whole
> family of wasted work. If your product IS live, invert the section: state what genuinely is at
> stake, so severity language is calibrated rather than absent.

---

## MANDATORY READING

Before writing ANY code, read:
1. `<this file>`
2. `docs/<your spec / architecture doc>`
3. `docs/HANDOFF-<latest>.md`

---

## ADVERSARIAL REVIEW (MANDATORY)

All non-trivial work is independently reviewed before it lands — **code, content, AND briefs.**
A separate, default-skeptical agent re-derives each finding from source and must reproduce it.

- **"Trivial" is exempt but must be AFFIRMATIVELY established**: single file · no user-facing
  strings · no high-stakes surface · no shared-plumbing import.
- **Any high-stakes touch overrides to a full multi-skeptic panel, always** (see DOMAIN GATES).
- **Runtime > code-read** for any binary gate: check the served bytes, not the source.
- The pipeline: S-Kai briefs → V-Kai reviews the brief → I-Kai builds → V-Kai reviews the build →
  S-Kai merges. Skills: `/s-kai` · `/v-kai` · `/i-kai`.

---

## ⚙️ DOMAIN GATES — the things V-Kai must ALWAYS check

<This is the most valuable section in the file, and the one only you can write. Every project
has 3-6 of these: the checks that are cheap to run, expensive to miss, and invisible to a
generic reviewer. Derive them by asking, per surface: **"if this is wrong, who finds out, and
when?"** — the ones where the answer is "a customer, months later, silently" go here.>

| Gate | What it checks | How to check it | Auto-escalates to full panel? |
|---|---|---|---|
| <e.g. Payment idempotency> | replaying a webhook changes state once | replay the same test event twice; assert one state change | YES |
| <e.g. Tenant isolation> | no query crosses a tenant boundary | grep every query for the tenant predicate; runtime probe with two seeded tenants | YES |
| <e.g. PII in logs> | no user-typed text or email in log output | run the flow, grep the log sink for seeded canaries | YES |
| <e.g. Locale parity> | every user-facing string exists in all N locales | `pnpm check-translations` | no |

⚠️ **A gate is theatre unless it is WIRED and FIRES on the branch you push to.** In `package.json`
but not in CI = theatre. In CI but the workflow only triggers on the default branch = also theatre.
Prove each one by mutate → fail → restore, and record the receipt.

---

## TECH STACK

| Layer | Technology | Version |
|---|---|---|
| Framework | | |
| Language | | |
| Database | | |
| Deployment | | |
| Package manager | | |
| Testing | | |

## QUICK START

```bash
<install>
<dev>          # note the PORT you standardise on
<build>
<typecheck>
<lint>
<test>
```

## PROJECT STRUCTURE

<A shallow tree, annotated. Only the parts a newcomer would get wrong. Not `find .` output —
a directory listing nobody curated is worse than none, because it rots invisibly.>

## KEY CONVENTIONS

<The rules that would otherwise be re-litigated every session. Each one: the rule, plus a
WRONG/CORRECT pair. Examples are load-bearing — a rule with an example gets followed.>

### <Convention name>
```
// WRONG
<the tempting thing>

// CORRECT
<the required thing>
```

## ENVIRONMENT VARIABLES

<Names and purposes ONLY. Never values.>
<If you have multiple environments/branches that are easy to confuse, put the disambiguation
here in bold with a one-line verification command — that confusion is destructive, not merely
annoying.>

## COMMON MISTAKES TO AVOID

| Mistake | Correct approach |
|---|---|
| | |

<Grow this table from real incidents. Every row should be traceable to a day something broke.>

## ESCALATION

Stop and ask the principal when: scope is unclear or self-contradicting · a fix needs a
destructive or irreversible action · a "trivial fix" turns out to need >30 min · you find a bug
adjacent to the task that is worse than the task.

---
*This file is the source of truth for development context. Update it when completing significant
work — a stale `CLAUDE.md` misinforms every session in the repo, which is the most expensive kind
of stale document you can own.*
```

---

## How to fill in the DOMAIN GATES section (worked example)

Say you are building a **contractor-on-the-road assistant** — it answers calls, lines up jobs, and
tracks vehicles. Ask *"if this is wrong, who finds out, and when?"* of each surface:

| Surface | If wrong, who finds out and when | → Gate |
|---|---|---|
| Telephony + payment webhooks | The contractor, at the bank, weeks later. **Silent, compounding, discovered late.** | **Money surface → full panel, always.** Replay every webhook twice; assert one state change. Verify the signature before parsing. |
| Vehicle tracking display | The contractor, mid-job, immediately — but only in the real app | **Runtime > code-read.** The gate is a probe of the served/rendered position, never a source read. |
| Missed-call handling | Nobody, until a job is lost | **A fail-open/fail-closed decision, made explicitly and written down.** Then a forced-failure test that exercises the chosen branch. |
| Job-status copy | The contractor, on first read | Standard review. Not a domain gate. |

That third row is the pattern worth internalising: **the failure path is code too.** Every
`try/catch`, fallback and default in a diff gets one forced-failure exercise, because fallbacks are
exactly where fail-open bugs and silent data loss live. *"It would catch"* is not evidence — name
the test or the manual probe that exercised it.
