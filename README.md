# Multi-Kai Workflow — a starter pack for solo builders using Claude Code

A practical, working system for running specialised Claude instances in parallel with structured
handoffs, encoded discipline, adversarial verification, and durable memory that gets smarter over
time. Developed by Gareth Scott over ~9 months building **SabaiFly**, a travel-planning product;
shared openly for any solo builder who wants to apply the pattern.

**This repo is not a description of the pattern. It is the pattern** — the actual role skills, the
actual playbooks, the actual settings and hook, and a working memory server. Clone it and run it.

> **On the name.** This started as the *three*-Kai workflow: planner, implementer, researcher. A
> fourth role — the adversarial verifier — turned out to be the one that made the difference, so
> the count in the name stopped being useful. It is the **multi-Kai pipeline** now. Where you see
> "three-Kai" below, it is genuinely historical.

> **If you adapt this for your work:** MIT-licensed, no permission needed. A link back to this repo
> when you share your own version is appreciated — it helps other solo builders find the original.
> See [Credit + attribution](#credit--attribution).

---

## Contents

- [What's new (2026-08)](#whats-new-2026-08)
- [What's in this repo](#whats-in-this-repo)
- [Start here](#start-here)
- [The core insight](#the-core-insight)
- [The four roles](#the-four-roles)
- [Why more than one?](#why-more-than-one)
- [The infrastructure layer](#the-infrastructure-layer)
- [The two gates and the two after them](#the-two-gates-and-the-two-after-them)
- [Discipline rules worth encoding from day one](#discipline-rules-worth-encoding-from-day-one)
- [The honest limitations](#the-honest-limitations)
- [Honest disclosure about SabaiFly](#honest-disclosure-about-sabaifly)
- [When this pattern wins / is overkill](#when-this-pattern-wins)
- [Credit + attribution](#credit--attribution)

---

## What's new (2026-08)

The original primer (2026-05) described a way of working. This version ships it, and three things
changed materially in between:

**1. Discipline moved from prose into mechanisms.** The central finding, paid for four separate
times: *a rule that lives only in a document, with no step that forces the read at the moment of
action, will keep failing.* The controlled experiment — an orchestrator banked a rule at 09:00 and
broke it at 10:00, same session, the lesson still in its own context window. Recall was 100%. So
`playbooks/playbook_enforcement_ladder.md` grades every rule by **where it executes** (L0 prose →
L5 impossible-by-construction), and the highest-value rules got wired: a
**harness-enforced dispatch pre-flight hook** (`settings-template/`) that the model cannot skip,
and mandatory template fields that an action cannot complete without.

**2. The learning loop grew receipts.** "I banked that lesson" is a done-claim like any other, and
one audit found it false three times in a row. Every merge now carries a trailer naming the commit
that actually wired each lesson — `Stamped:` / `Promoted:` / `Rung-wired:` — or says `NONE` with a
reason.

**3. The brain became searchable and portable.** `memory-starter/` ships a fully-local semantic
recall MCP server (no cloud, no third party in the read path, ~2s freshness), the conventions that
keep a vault healthy, and an example vault to copy the shapes from.

Also here for the first time: the **brief / handoff / status / `CLAUDE.md` templates**, the
**three-tier permission architecture**, and a **cold-start walk** including the remote-access
recipes.

---

## What's in this repo

| Directory | What it is |
|---|---|
| **[`skills/`](skills)** | The three role skills — `s-kai` (plan), `i-kai` (build), `v-kai` (verify). Copy to `~/.claude/skills/`. **These are the live versions**, not simplified samples. |
| **[`playbooks/`](playbooks)** | Nine domain-free craft playbooks: verification doctrine, the enforcement ladder, the pipeline, model tiering, memory conventions, the failure-mode bank, web engineering, new-project bootstrap, and the operating manual. |
| **[`templates/`](templates)** | The brief contract, the handoff, `BUILD-STATUS` + `DECISIONS-PENDING`, and a `CLAUDE.md` starter. |
| **[`settings-template/`](settings-template)** | The dispatch pre-flight hook and the three-tier permission architecture. |
| **[`memory-starter/`](memory-starter)** | Memory conventions, an example vault with a Lessons-Learned MOC, and the local semantic-recall MCP server. |
| **[`docs/`](docs)** | [Getting started](docs/GETTING-STARTED.md) · [Adapt to your project](docs/ADAPT-TO-YOUR-PROJECT.md) |
| **[`THE-VERIFIER-AND-THE-BRAIN.md`](THE-VERIFIER-AND-THE-BRAIN.md)** | Why the verifier and the learning loop exist, plus the storage architecture. |

> **📎 A note on the links inside these files.** The skills and playbooks are full of
> `[[double-bracket]]` links and backticked `feedback_*` / `project_*` / `reference_*` slugs. **Those
> point into the author's own private memory vault and are expected to be dead for you** — read them
> as "this rule has a receipt somewhere", not as broken links to chase. Cross-references *between*
> shipped playbooks are ordinary working markdown links.
>
> The war stories keep their real dates and nouns on purpose. A rule with a date and a real cost is
> checkable; a sanitised one is a slogan.

---

## Start here

**→ [`docs/GETTING-STARTED.md`](docs/GETTING-STARTED.md)** — clone to running pipeline in about an
hour.

**→ [`docs/ADAPT-TO-YOUR-PROJECT.md`](docs/ADAPT-TO-YOUR-PROJECT.md)** — a full worked example of
deriving *your* domain gates, with a day-by-day first week.

If you only take one idea: **write down the three checks that would hurt most to get wrong silently,
and make a fresh-context agent run them before anything merges.** That is most of the value.

---

## The core insight

Most people use Claude as a single thread: one chat window, ask questions, get answers, lose context
when the session ends. That works for small tasks and breaks down on real projects, for four
reasons:

1. **The context window is finite.** A complex project produces more working state than any single
   session holds.
2. **One model is doing four jobs.** Strategic reasoning, code execution, adversarial review and
   deep research want different capabilities and different mental modes — and they compete for the
   same context.
3. **No durable memory.** Decisions made in one session are lost in the next, so you re-derive them
   every time. A re-derivation is not a neutral cost; it is a process defect.
4. **No quality structure.** Without explicit role discipline, AI trends toward over-confident
   plausibility — and *fluent* is exactly what the best wrong answers look like from the inside.

The multi-Kai pattern addresses all four by **specialising roles, encoding discipline where it
executes, and persisting decisions to durable artifacts.**

---

## The four roles

> **⏱️ DATED EXAMPLE — refresh per deployment.** The model names below are what these seats were
> filled with in **2026-08**. Names and context sizes rot within months; **the seats are the durable
> part.** See [`playbooks/playbook_model_tiering.md`](playbooks/playbook_model_tiering.md) and re-map
> onto whatever your provider ships when you read this.

### S-Kai — strategy / planner
**Job:** briefs, decisions, sequencing, coordination, memory writes, and **merges**.
**Model:** top tier, longest context (Opus 4.8 as of 2026-08).
**Surface:** Claude Code in your IDE.
**Does NOT:** implement beyond one-liners. If it's >15 minutes of building, it writes a brief instead.

### I-Kai — implementation
**Job:** execute ONE brief per session. Ship it, commit at gates, tick the status doc.
**Model:** mid tier is usually enough — the brief carries the reasoning (Sonnet 4.6 as of 2026-08).
**Surface:** a separate Claude Code session, in its own git worktree.
**Does NOT:** drift into planning, or expand scope silently. Unclear → escalate.

### V-Kai — adversarial verifier ⭐ *the one that made the difference*
**Job:** try to break the artifact. Reviews the **brief** before I-Kai builds, and the **build**
before S-Kai merges.
**Model:** match it to the stakes — top tier for anything security, money, or shared plumbing.
**Surface:** a **fresh-context subagent** dispatched from S-Kai's session; independent by
construction. The verdict is its return value.
**Does NOT:** merge. It advises; S-Kai decides.

### R-Kai — research *(optional)*
**Job:** deep autonomous web research, returned as a structured report with citations.
**Surface:** a browser tab, in research mode.
**Does NOT:** touch your codebase or memory. Output flows back to S-Kai for synthesis.

---

## Why more than one?

**Context economy.** Each role spends its context on *its* work. Run three substantial workstreams
in parallel that any one session could only do serially.

**Failure-mode specialisation.** Each role fails differently — S-Kai drifts into implementation,
I-Kai expands scope silently, R-Kai returns generic research. A role contract catches each failure
at the place it happens.

**Coordination via durable artifacts, not chat.** The roles cannot talk to each other directly. They
coordinate through docs commits, memory, and briefs — which forces decisions into durable form,
and that durable form *is* the project memory.

**And the structural one, which is why V-Kai exists at all:** *no author reviews their own work
well.* That includes the planner reviewing its own briefs. It is not a discipline problem — you
cannot fix it by trying harder — so the fix has to be structural: a reviewer with fresh context and
zero investment in the artifact.

---

## The infrastructure layer

Without these, you have several Claude sessions that don't compound.

### 1. The brain — memory that gets smarter
Project-scoped memory at `~/.claude/projects/<encoded-project-path>/memory/`, one fact per file,
typed prefixes (`user_` / `feedback_` / `project_` / `reference_`), backed to a **private** git repo
in the same beat as every write.

On top of it: a **local semantic-recall MCP server** ([`memory-starter/memory-server/`](memory-starter/memory-server))
so recall works by *meaning* rather than by a hand-maintained index — with a file-watcher, so a
memory written this session is findable this session.

And a **learning loop** — capture → consolidate → **apply**, where *apply* means V-Kai reads the
Lessons-Learned checklist before every review. Capture alone changes nothing; the repeat-failure
rate only falls when the verifier reads the lesson first.

Conventions: [`memory-starter/conventions.md`](memory-starter/conventions.md).

### 2. Skills — role discipline that auto-primes
`~/.claude/skills/<name>/SKILL.md`, invoked with `/s-kai`, `/v-kai`, `/i-kai`. **The skill IS the
contract.** New sessions inherit the discipline without re-explanation.

⚠️ Keep them at **user** scope. A project-scoped copy *wins* over the user-scope one and then
silently rots behind it — measured at 37 days behind, in the one repo that mattered most.

### 3. Hooks — the rung where discipline stops depending on memory
[`settings-template/`](settings-template) ships a **harness-enforced dispatch pre-flight**: four
questions injected before every agent launch (writes? concurrent? isolation? watcher?). The harness
executes it, not the model, which is exactly why it works where the same rule in prose did not.

### 4. Templates — where mandatory fields live
[`templates/`](templates). The brief's `Memories to stamp on merge:` field is the clearest example:
it cannot be left blank, and the verifier hard-rejects a brief that blanks it — which is what closed
a vault-rot problem that emphatic prose had not.

### 5. Coordination files
`docs/BUILD-STATUS.md` (what shipped) and `docs/DECISIONS-PENDING.md` (what's waiting on a human
ruling, answerable cold, cleared in batches). Shapes in
[`templates/BUILD-STATUS-and-DECISIONS.md`](templates/BUILD-STATUS-and-DECISIONS.md).

### 6. Handoffs
`docs/HANDOFF-YYYY-MM-DD-<tag>.md` — the connective tissue that dies first in a context exhaustion.
**One rewritten LIVE-QUEUE block at the top**, never append-only sediment. And it is a *save point*,
not a session-end ritual: write it at ~25–30% context remaining, because "the end" is precisely
when it never arrives cleanly.

---

## The two gates and the two after them

1. **Brief gate** — V-Kai reviews the brief on two lenses (right-target, executable). Catches the
   wrong build before a session is spent on it.
2. **Build gate** — V-Kai does its own adversarial diff read against the brief plus your named
   domain gates. Runtime over code-read for anything binary.
3. **Merge gate** — check the **merged tree**, not either parent. `--no-commit --no-ff`, verify,
   then commit or abort. This was the last unwatched step; "sole merge authority" plus "never mark
   your own work" is a contradiction unless the merge itself is checked.
4. **Harvest gate** — stamp the memories the build falsified, promote anything portable, assign each
   new lesson its enforcement rung, and log the gate telemetry **including the zeros**, because that
   is what later licenses you to delete a gate that has stopped catching anything.

Loop cap ~2 rounds per gate. A round-2 failure means the *approach* is wrong → escalate, don't grind.

Full method: [`playbooks/playbook_multi_kai_pipeline.md`](playbooks/playbook_multi_kai_pipeline.md).

---

## Discipline rules worth encoding from day one

- **A gate is theatre unless it is WIRED and FIRES on the branch you push to.** In `package.json`
  but not in CI = theatre. In CI but triggering only on the default branch = also theatre. Prove it
  by mutate → fail → restore, *and* by one clean pass through the same entry point.
- **Grep counts lie.** A hit inside another word (`sha`**`red`**) inflates them. Read each hit's
  context; never trust the number.
- **Verify facts before asserting.** Training data ages faster than any model's window. Label every
  claim *verified* / *recalled* / *inferred* — and let the label travel into documents, because an
  unlabelled guess becomes a "fact" three weeks later.
- **No patches — only working solutions.** Patch debt compounds.
- **Find it, fix it.** Small deferred items compound into perpetual half-done work.
- **"Done" claims need receipts.** A storage or action claim fails *silently and indefinitely* —
  nothing errors and the bill lands months later. Report from an artefact you just observed, and put
  the receipt in the same message.
- **When you narrow an allowlist, verify the COMPLEMENT.** Answer in writing: *what was permitted
  before this change and is not now?*
- **Never force-push** to fix something cosmetic. You trade a real risk for a tidy one.

---

## The honest limitations

- **Cost.** Parallel sessions across tiers use real tokens. Budget for it — and read
  [`playbooks/playbook_model_tiering.md`](playbooks/playbook_model_tiering.md), because the single
  biggest waste is subagents silently inheriting the top tier.
- **Discipline overhead.** The system rewards consistent capture and punishes shortcuts. Skip the
  briefs and you lose the parallelism benefit entirely.
- **Learning curve.** Roughly three weeks to feel comfortable, three months to feel fluent.
- **Not magic.** AI still makes mistakes. This catches more of them than no structure does, and you
  remain the verifier of last resort.
- **Windows-flavoured in places.** It was built on Windows, so some receipts and traps are
  PowerShell-shaped. The doctrine is platform-free; a few commands are not.

---

## Honest disclosure about SabaiFly

**SabaiFly is pre-launch.** It has not launched, no date is being promised here, and there are
currently no users. The workflow in this repo was developed *during* that pre-launch build.

**What that means for you, plainly:**

- **Don't judge the workflow by what is at sabaifly.com.** That address serves an older placeholder
  built before this workflow existed, using earlier and much less disciplined methods. It is not
  this workflow's output.
- **The pattern has not yet been proven in production-at-scale operations.** What it has been proven
  on is sustained, complex pre-launch development.
- **This repo is the honest artifact.** The skills, playbooks and templates here are the real ones,
  in daily use — not a cleaned-up retelling.

**What the pattern has demonstrably done well:**

- Complex multi-week feature work compressed into days via parallel implementer sessions.
- Security audits that found real issues before launch, including several the author's own review
  had passed.
- Adversarial verification catching, in a single day, a false-alarm "leak" that would have wasted a
  fix, a silent merge that had quietly dropped one branch's work, and a flawed design doc — all
  things self-review ships.
- Cross-session continuity: handoffs, memory and skills surviving multi-day and multi-week cycles.
- Measured reduction in repeat failures once lessons were wired to mechanisms rather than written
  down more emphatically.

**What is NOT yet proven** (and will be validated post-launch):

- Production runtime monitoring patterns.
- Long-term knowledge accumulation — the memory base is months old, not years.
- Multi-person team scaling. It has been one human plus AI throughout.
- Stability across major model generation changes, though the model-tiering playbook is the attempt
  to make that survivable.

If you adopt the pattern, you are adopting it on the basis of **development discipline that is
working**, not on a production track record. That is the honest framing.

---

## When this pattern wins

- Solo builders shipping serious products
- Domain experts applying deep expertise to AI-amplified work
- People who hit the same friction repeatedly and want to encode the fix once
- Anyone running several workstreams that compete for cognitive load

## When this pattern is overkill

- Quick one-off scripts
- Prototyping where you haven't decided what you're building
- Pair programming where you want a single conversational thread
- Teams of three or more humans — different coordination patterns fit better

---

## Credit + attribution

**MIT-licensed** — use, adapt and share it without restriction. What's requested but not required:

- **If you publicly share an adaptation** (blog post, video, your own repo, a thread, a talk) → a
  link back to `github.com/GarethScott007/multi-kai-workflow`, so other solo builders can find the
  original.
- **If you build something significantly different** → name what you added or changed, so others can
  compare approaches across implementations.
- **If you adopt it commercially** → same as above. Link back so the pattern compounds across the
  ecosystem.
- **If it saved you meaningful time** → consider opening an issue or PR with what worked, what
  didn't, and what you'd improve. The pattern improves through accumulated practice across many
  builders, not just one.

The point isn't enforcement — MIT means attribution can't be legally enforced, and enforcing it
isn't the goal anyway. The point is **cultural**: patterns spread better when each adaptation knows
its origin.

If you've built something interesting with this, I'd genuinely like to see it. Open an issue, or
reach me at `hello@sabaifly.com`.

---

## Final note

The pattern only works because the human is the orchestrator. Each Kai is bounded; you bridge them.
Your domain expertise, judgment, taste and calibration radar are the load-bearing part — the Kais
multiply your effective output, they don't replace you.

If you find yourself doing *less* thinking rather than more, something is wrong with how you're
using it. The whole point is to free your thinking from mechanical execution so you can spend it on
the decisions that actually matter.

*"Always a little further."*

— Gareth Scott + Kai
2026-05-25 (initial primer) · 2026-05-26 (attribution) · 2026-06-30 (the verifier + the brain) ·
**2026-08 (this starter pack)**
