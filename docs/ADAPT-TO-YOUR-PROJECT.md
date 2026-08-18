# Adapt this to your project — a worked example

The pattern is domain-free. What is **not** domain-free is the part that makes it earn its keep:
your **domain gates**, the checks a verifier must always run because they are cheap to run and
expensive to miss. Nobody can write those for you. This document shows how one person would derive
theirs.

The running example is deliberately not a web product: **an assistant for a contractor on the road**
— it answers inbound calls when the crew is on a job, lines up work, and tracks the vans. One
person building it, alongside running the business.

**Contents**
- [1. Map the roles onto how you actually work](#1-map-the-roles-onto-how-you-actually-work)
- [2. Derive your domain gates](#2-derive-your-domain-gates)
- [3. The first week](#3-the-first-week)
- [4. The success test](#4-the-success-test)
- [5. Things that will feel wrong at first](#5-things-that-will-feel-wrong-at-first)

---

## 1. Map the roles onto how you actually work

You are the **principal**. Not a role in the pipeline — the person the pipeline reports to. You set
direction, rule on scope, and are the escalation target. Everything below serves that.

| Role | What it is for you | When you open it |
|---|---|---|
| **S-Kai** — planner | Holds the plan. Writes briefs. Decides sequencing. Merges. | Start of a work block; any "what should we do about X" |
| **I-Kai** — implementer | Executes ONE brief per session, in its own worktree | When a brief is V-Kai-approved and ready |
| **V-Kai** — verifier | A fresh-context subagent that tries to break the artifact | Twice per lap: on the brief, and on the build |
| **R-Kai** — researcher *(optional)* | Deep autonomous web research on a browser tab | When a decision waits on facts about the outside world |

**The one that feels redundant and isn't: V-Kai on the *brief*.** Reviewing a build is intuitive.
Reviewing the *instructions* feels like bureaucracy — until the first time it comes back with
*"this builds the wrong thing"* and saves a whole session. On the origin project, roughly a third of
REWORK verdicts landed on briefs, not builds. Catching a wrong brief costs minutes; catching it
after an implementer has worked from it for three hours costs the afternoon.

**Working solo does not exempt you — it is the reason.** A solo builder has no colleague who will
say *"are you sure?"* The verifier is that colleague, and it is the only role you cannot play
yourself, because no author reviews their own work well.

### The context economy, concretely

This is why the roles are separate windows rather than one long conversation. If a single session
holds the plan, reads the code, writes the code, and reviews it, then by hour three the plan is
competing for space with a stack trace — and the plan is what loses. Separate windows mean the
planner's context stays full of *plan*.

---

## 2. Derive your domain gates

Go surface by surface and ask **one question**:

> **If this is wrong, who finds out, and when?**

Then spend your review budget where failure is **silent, compounding, and discovered late.** Loud
failures protect themselves — a build break is found in seconds by a machine and needs almost no
review. A wrong bank transfer is found in six weeks by an accountant.

Here is that applied:

| Surface | If it's wrong, who finds out, and when? | Verdict |
|---|---|---|
| Payment + telephony webhooks | The contractor, at the bank, weeks later | **MONEY SURFACE → full panel, always** |
| Vehicle tracking display | The contractor, mid-job — but only in the real app | **Runtime > code-read** |
| Missed-call handling | Nobody, until a job is quietly lost | **Needs an explicit fail-open/fail-closed ruling** |
| Job-status wording | Read immediately | Standard review. Not a gate. |
| Marketing page copy | Whenever someone reads it | Standard review. Not a gate. |

Three of five surfaces get a real gate. **That ratio is healthy.** If everything is a gate, nothing
is — thoroughness theatre is a real failure mode, and forty findings where three matter is worse
than three findings, because it teaches everyone to skim.

### Gate 1 — money surfaces override to a full panel, always

**Rule:** any diff touching payment or telephony webhooks gets a multi-skeptic panel regardless of
how small it looks. A one-line change to a signature check is not a one-line change.

**What the panel checks:**
- **Signature verified BEFORE the payload is parsed.** Parsing untrusted input is already trusting it.
- **Idempotency.** Providers *will* redeliver. Record the event id; a replay must be a no-op.
  **Prove it by replaying the same test event twice and asserting the state changed once** — not by
  reading the code and agreeing that it looks idempotent.
- **Return 2xx fast, queue the slow work.** A timeout looks like a failure and triggers a redelivery,
  which is how one payment becomes three.
- **Uniqueness lives in the database constraint, not in an application check.** Concurrent
  invocations make check-then-write races a certainty rather than a risk. The app-level check is UX;
  the constraint is integrity.

### Gate 2 — vehicle tracking is runtime, never code-read

**Rule:** no claim about what a van's position *looks like* is accepted from reading the source. The
gate is a probe of the actually-rendered output.

**Why this specific surface:** it is a chain — device → API → store → transform → map. Every link
can be individually correct while the composition is wrong, and every one of those bugs reads as
correct code. On the origin project, **two of three code-read UI findings in one panel were refuted
by the runtime lens.** Structural facts survive a code read; rendered-experience claims do not.

**What the gate looks like:** serve the real thing, put a van at a known coordinate, and assert the
rendered marker. Include a **negative control** — move the van and watch the marker move. A probe
that cannot fail is not a probe, and a clean result from a broken probe is indistinguishable from a
clean result from a working one.

### Gate 3 — missed calls need a ruling, not a default

This one is different in kind, and it is the most valuable of the three. It is not a check — it is a
**decision you must make explicitly, in writing, before any code exists.**

The system will sometimes be unable to handle an inbound call: the model is down, the calendar API
times out, confidence is too low. There are exactly two designs:

| | **Fail OPEN** | **Fail CLOSED** |
|---|---|---|
| Behaviour | Answer anyway, degrade gracefully — take a message, promise a callback | Don't answer; fall through to voicemail or a human |
| Wins when | A partial answer beats silence | A wrong answer is worse than no answer |
| Fails as | Books a job on a day you're not free | Loses a lead you'd have won |

**Neither is correct in general. One is correct for this business** — and only the principal can say
which, because it is a values-and-money question, not an engineering one.

Given the stated goal *"never drop a paid job because of a missed call"*, the ruling is probably
**fail open with a loud degradation** — take the message, never touch the calendar, flag it for
human follow-up within the hour. But **write the ruling down** as a `project_*` memory with the
reasoning, because six months later someone will "clean up" the degraded path without knowing it was
load-bearing.

**Then test the failure path.** The failure path is code too. Every `try/catch`, every fallback,
every default gets one *forced-failure* exercise — fallbacks are exactly where fail-open bugs and
silent data loss live. *"It would catch"* is not evidence; name the test that exercised it.

### Write them down where they execute

Your three gates go in **`CLAUDE.md`** (see `templates/CLAUDE-MD-TEMPLATE.md`), and S-Kai passes
them **by name** in every V-Kai dispatch. A gate that lives only in your head is not a gate; a gate
named in a document nobody is required to read is barely better.

---

## 3. The first week

Five days, in this order, because each one assumes the last. The aim is not to have built much by
Friday — it is to have gone round the loop **once**, end to end, so the habit exists before there is
anything expensive to lose.

### Day 1 — write your `CLAUDE.md`

Start here, before any pipeline work. It is the always-in-context file, so it is the cheapest place
to put facts — and getting it written is what makes every later session start warm.

From `templates/CLAUDE-MD-TEMPLATE.md`: project facts, quick-start commands, the conventions worth
never re-litigating, your three domain gates, and the severity-framing section.

**Do not skip the severity section.** Right now nothing is live and there are no users, so *nothing*
is an emergency. Say so in writing, with an exit condition. Otherwise you will get findings framed
as *"users at risk"* about a system no user has ever touched — and once you have learned to discount
that framing, you will discount it on the day it is finally true.

**And know the file's limit.** `CLAUDE.md` is always in context, which makes it perfect for **facts**
and unreliable for **behaviours**. A rule sitting only in prose loses to the task at the moment it
matters — measured, repeatedly, even with the rule in the context window. Put the fact here; put the
*behaviour derived from it* into the skill, template or hook that fires at the moment it applies.

### Day 2 — seed the vault

`~/.claude/projects/<encoded-project-path>/memory/`, its own **private** git repo. Two files:

1. **`user_profile.md`** — who you are, your domain background, how you want to be talked to.
2. **`hubs/Lessons-Learned.md`** — even nearly empty. **V-Kai reads it before every pass.**

Then the discipline that makes all of it work: **capture decisions as they land, and commit+push in
the same beat.** Not batched at session end — the batch never happens.

### Day 3 — first brief, first brief review

Pick something small and real. *"Log every inbound call with its outcome"* is a good first brief:
one clear surface, a real gate, no ambiguity about done.

Write it from `templates/BRIEF-TEMPLATE.md`. Existence-probe every file it names. Fill in
`Memories to stamp on merge:` — never blank.

Then dispatch V-Kai on the **brief**. **Expect findings.** A brief review that returns "looks good"
everywhere is a failed review, and your first brief will not be good — nobody's is.

### Day 4 — first build, first build review

`/i-kai` in its own worktree. Then V-Kai on the diff, with your gates named in the dispatch.

**The dispatch detail that trips everyone up:** a spawned subagent does **not** auto-load a skill and
**cannot** invoke slash commands. You must tell it, in the prompt, to read
`~/.claude/skills/v-kai/SKILL.md` first — or paste that file in as its framing. Skip this and you get
a generic code review wearing V-Kai's name.

### Day 5 — merge, and harvest

Merge with `--no-commit --no-ff` so you can inspect the **merged tree** before committing. Gates run
on the merge result, not on either parent — a merge is where two individually-fine branches produce
something neither intended.

Then **harvest**, in the same beat:
- Stamp the memories the build falsified (the brief's field told you which).
- Promote anything portable into `playbooks/`. **The test: delete every proper noun — is there still
  a rule?** If yes, it belongs in the portable tier, with a plain-text provenance tag.
- Log the gate telemetry in `BUILD-STATUS.md`, **including the zeros.** That is the data that later
  licenses you to *delete* a gate that has stopped catching anything.

**Harvest is the step everyone skips, and it is the step that makes the loop return smarter rather
than merely finished.** Capturing notes changes nothing on its own; the repeat-failure rate only
falls when the verifier reads the lesson *before* the next review.

---

## 4. The success test

From `playbooks/playbook_new_project_bootstrap.md`:

> **The test of a good bootstrap: the first verifier verdict in the new project cites a lesson
> learned somewhere else.**

That is the whole thesis in one sentence. When V-Kai's first verdict on your contractor assistant
says *"checked against the portable rule that a negative control sharing a short-circuit with an
earlier predicate proves nothing"* — a rule earned on a completely unrelated product, in a different
industry, months earlier — then the machinery is real. The brain is not storing; it is **applying**.

Until that happens, you have a filing system. After it, you have a system that compounds.

---

## 5. Things that will feel wrong at first

- **"The gates are slower than just doing it."** For the first fortnight, yes. The gates pay off
  when you stop re-deriving decisions you already made and stop shipping the same class of bug
  twice — which is a curve, not an event.
- **"I'm the only person here, why write briefs?"** The brief is not for a colleague. It is for the
  *implementer session*, which has no memory of your reasoning, and for the verifier, which needs
  something falsifiable to check against. It is also the artifact that survives the week you spend
  on a job site.
- **"The verifier is being pedantic."** Sometimes. But a review that finds nothing is
  indistinguishable from a lazy one, which is exactly why V-Kai is required to state **what it
  attacked** when it finds nothing. Read the attack, not just the verdict.
- **"This is a lot of documents."** It is five: `CLAUDE.md`, a brief, a handoff, `BUILD-STATUS.md`,
  and a decisions queue. Each replaces something you are currently keeping in your head, badly,
  while driving between jobs.
- **"Do I need all of it on day one?"** No. `CLAUDE.md` + the vault + the brief template gets you
  most of the value. Add the verifier on your second real feature, and the memory server when
  `MEMORY.md` stops fitting on a screen.
