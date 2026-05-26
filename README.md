# Three-Kai Workflow — A Primer for Solo Builders Using Claude Code

A practical guide to running specialised Claude instances in parallel with structured handoffs, encoded discipline, and durable memory. Developed by Gareth Scott over ~8 months building SabaiFly; shared with permission for any solo builder who wants to apply the pattern.

**What you'll get from this:** ~5-10x throughput vs single-thread "AI helps me code" workflows, with quality guardrails that catch the failure modes solo builders typically miss.

**What this is NOT:** A replacement for understanding what you're building. The pattern works because you bring domain expertise + judgment; the Kais bring breadth + execution + memory.

---

## The core insight

Most people use Claude as a single thread: one chat window, ask questions, get answers, lose context when the session ends. This works for small tasks but breaks down on real projects because:

1. **Context window is finite.** A complex project produces conversations that exceed any single session's working memory.
2. **One model does everything.** Strategic reasoning, code execution, and deep research want different model capabilities and different mental modes.
3. **No durable memory.** Decisions made in one session are lost in the next; you re-derive them every time.
4. **No quality structure.** Without explicit role discipline, AI tends toward over-confident plausibility — the failure modes are subtle.

The three-Kai pattern solves all four by **specialising roles, encoding discipline, and persisting decisions to durable artifacts.**

---

## The three roles

### S-Kai (Strategic / Planner)

**Job:** Strategy, briefs, decisions, sequencing, coordination.
**Model:** Claude Opus 4.7 (best reasoning + longest context).
**Surface:** Claude Code in your IDE (VS Code recommended).
**What it does:** Holds the project's bigger picture in working memory. Writes briefs for I-Kai to execute. Reviews I-Kai's output. Synthesises research from R-Kai into strategic decisions. Maintains the discipline contracts.
**What it does NOT do:** Execute code at scale. Run mechanical refactors. Implement entire features end-to-end.

### I-Kai (Implementation / Code-cutter)

**Job:** Execute briefs. Ship working code. Update status docs.
**Model:** Claude Sonnet 4.6 (sufficient capability, faster + cheaper).
**Surface:** Separate Claude Code session in your IDE (run multiple in parallel windows).
**What it does:** Reads the brief end-to-end, executes it, commits at gates, pushes to the branch, updates status documentation. Asks for help when scope is unclear.
**What it does NOT do:** Drift into planning. Expand scope silently. Refactor adjacent code unless the brief asks.

### R-Kai (Research)

**Job:** Deep autonomous web research.
**Model:** Claude with Research mode (on claude.ai web — different surface from Claude Code).
**Surface:** claude.ai in a browser tab.
**What it does:** Multi-hour autonomous research across many sources, returns structured reports with citations.
**What it does NOT do:** Access your codebase or memory. Make strategic synthesis decisions. (Output flows back to S-Kai for synthesis.)

---

## Why three, not one?

**Context economy.** Each Kai uses its context window for ITS work. If S-Kai is reasoning about strategy, it doesn't waste tokens on code execution. If I-Kai is implementing, it doesn't waste tokens on strategic re-derivation. If R-Kai is researching, neither of the others has to allocate tokens to fact-gathering.

Result: you can run three substantial workstreams in parallel that any one Kai could only do serially.

**Discipline specialisation.** Each role has different failure modes. S-Kai's failure mode is drifting into implementation when it should be writing briefs. I-Kai's failure mode is expanding scope silently. R-Kai's failure mode is generic research that doesn't reflect your brand context. Specialised role contracts catch each failure mode at the right place.

**Coordination via durable artifacts, not real-time chat.** The three Kais cannot directly talk to each other (different surfaces). They coordinate via docs commits + memory + briefs. This forces decisions to land in durable form, which IS the project memory.

---

## The infrastructure layer

This is what makes the pattern work. Without these, you have three Kais that don't compound.

### 1. Memory system (project-scoped)

Claude Code can persist memory across sessions. You add memory files at:
- `~/.claude/projects/<encoded-project-path>/memory/`
- One file per memory, with YAML frontmatter (`name`, `description`, `metadata.type`)
- An index file `MEMORY.md` lists them all (auto-loaded each session)

Memory types worth distinguishing:
- **`user`** — facts about you (background, preferences, role)
- **`feedback`** — discipline rules learned from past sessions ("don't suggest sleep unprompted"; "verify facts before asserting"; "never use 'no refunds' as policy")
- **`project`** — strategic decisions + product state ("X feature works this way because of Y reason")
- **`reference`** — pointers to external systems (registrar dashboards, API docs, etc.)

Pattern: capture decisions as they're made, not at session end. Each memo has a **Why** + **How to apply** block — captures reasoning so future-you can judge edge cases.

### 2. Skills (auto-priming role discipline)

Claude Code supports skills — markdown files that prime the session with role-specific instructions.

Project-level skills at `.claude/skills/<name>/SKILL.md`. Invoke at session start with `/skill-name`.

Recommended setup:
- `/s-kai` skill — encodes Strategic-Kai role discipline (briefs not builds, decision-capture sweep at session end, brief sizing by model, verify facts before asserting)
- `/i-kai` skill — encodes Implementation-Kai role discipline (read brief end-to-end first, codebase conventions, gate-driven commits, git sync discipline for parallel sessions, escalate to user when scope is unclear)

The skill IS the contract. When you type `/s-kai`, the role primes automatically. New sessions inherit the discipline without you having to re-explain.

### 3. Brief format (the I-Kai contract)

Briefs live at `docs/BRIEF-I-KAI-<TOPIC>.md`. Standard sections:

1. **Goal** — one paragraph, what success looks like
2. **Why** — strategic motivation (so I-Kai can make judgment calls if scope is ambiguous)
3. **Scope** — explicit IN and OUT-OF-SCOPE bullets
4. **Files to touch** — anchor file paths so I-Kai doesn't go searching
5. **Gates** — typecheck/lint/test/manual-check expectations
6. **Done definition** — what "shipped" means (commit + status tick, etc.)
7. **Estimated effort** + **Recommended model** — for parallel-window planning

The brief is the contract between S-Kai (writer) and I-Kai (executor). A good brief means I-Kai needs zero clarification mid-execution.

### 4. Handoff doc convention

At session end, S-Kai writes `docs/HANDOFF-YYYY-MM-DD-<tag>.md` capturing:
- Today's commits (chronological)
- What's currently in-flight (I-Kai sessions running, drafts pending review)
- Pre-launch state (or whatever the milestone is) — done vs in-progress vs not-started
- Strategic work pending (decisions still to make)
- Brief-able tasks not yet written

Next session — yours or a future Kai — opens the handoff and picks up cleanly. Continuity becomes structural rather than memory-dependent.

### 5. BUILD-STATUS.md (your project's status tracker)

A markdown table that I-Kai ticks as work ships. Lets S-Kai see I-Kai's progress without direct chat. Coordination via git commits.

---

## Discipline rules worth encoding from day one

These compound over time. Encode them in the skill files so they auto-apply.

### "Verify facts before asserting"

For external services (APIs, MCP servers, SDK versions, pricing, regulations), DEFAULT to WebSearch / WebFetch rather than recalling from training data. Training data ages; the world changes faster than any model's training window. When in doubt, search.

### "Don't suggest sleep/rest unprompted"

Trust user autonomy. The user knows when they're tired. Becoming a Claude-trope ("get some rest!") is condescending and a Claude-pattern users have publicly flagged.

### "No patches — only working solutions"

When something's broken, fix the root cause. Don't apply a quick patch that ships now and breaks later. The patch debt compounds.

### "Find it, fix it"

Don't defer small accessibility/polish items to "a later session". Small deferred items compound into perpetual half-done work.

### "Decision capture sweep at session end"

Before closing a session, scan for decisions worth keeping. Capture as memory files (with **Why** + **How to apply**) or docs commits. Anything that lived in chat history alone is lost; anything in durable artifacts survives.

### "Git sync discipline for parallel sessions"

When multiple I-Kai sessions run in parallel on the same branch:
- `git fetch + pull --rebase` at session start
- `git pull --rebase` before each commit if time has passed
- `git pull --rebase` before each push
- On non-fast-forward push: rebase, resolve, retry
- Never force-push without explicit approval

### "Brief sizing by model"

- Briefs >2h or judgment-heavy → Opus 4.7 (1M context)
- Briefs <90 min mechanical → Sonnet 4.6 (200k context, cheaper)
- Briefs <30 min structured passes → Haiku 4.5 (fastest, cheapest)

When in doubt: Opus. Tiny cost differential vs cost of mid-session context exhaustion.

---

## Practical setup (~30 min one-time)

1. **Install Claude Code** in VS Code (Extensions marketplace, search "Claude")
2. **Subscribe to a Claude Pro or Max plan** (Max recommended for parallel sessions — higher rate limits)
3. **Create `.claude/skills/` in your project root**
4. **Add the two skill files** (s-kai + i-kai) — see Appendix A below for starter templates
5. **Set up the memory directory** — see Memory Setup section below
6. **Open a Claude Code session, type `/s-kai`** and use the S-Kai bootstrap prompt below
7. **As decisions land, capture them as memories.** As patterns emerge, encode them in skills.

The system compounds. Month 1 you have basic discipline. Month 3 you have a workflow that meaningfully outperforms most solo builders. Month 6 you have infrastructure that survives team growth without rewrites.

---

## Bootstrap prompts (copy-paste to start each Kai)

### S-Kai (first session on a new project)

Open Claude Code in VS Code at your project root. Type:

```
/s-kai

Hi S-Kai. I'm setting up [PROJECT NAME] — a [ONE-LINE DESCRIPTION OF WHAT YOU'RE BUILDING, e.g. "a SaaS app for X" / "a mobile-first marketplace for Y"].

My background: [YOUR ROLE + RELEVANT EXPERIENCE — paramedic, finance, designer, etc.]
My situation: [SOLO / TEAM SIZE] + [WHAT STAGE — pre-launch / live / iterating]

Before we start working:
1. Read CLAUDE.md if it exists, or propose what we'd put in one
2. Confirm you understand your role (strategy + briefs + decisions, NOT implementation)
3. Propose how we'd structure the first 2-3 strategic decisions to capture as memory

I'll work with you to capture decisions to memory as we go.
```

### S-Kai (returning session on existing project)

```
/s-kai

Read the latest docs/HANDOFF-*.md and skim MEMORY.md.
Check git log --oneline -10 for recent commits.
Acknowledge state + propose pickup move.
```

### I-Kai (execute a brief from S-Kai)

```
/i-kai

Today is [YYYY-MM-DD]. Read `docs/BRIEF-I-KAI-[TOPIC].md` and execute per the done-definition.

Push commits to [branch-name] when shipped. If scope is unclear or you hit something unexpected, escalate to me — don't expand scope silently.
```

### R-Kai (deep research on claude.ai Research mode — separate browser tab)

Copy the entire primer block below + your research question to claude.ai Research mode:

```
I'm researching for [PROJECT NAME] — [ONE-LINE BRAND + POSITIONING].

### Brand positioning
- [3-5 bullets about what you stand for + tagline + what makes you different]

### Research style preferences
- Operational, not lecturing: deliver locale/situation-specific actionable intel, not abstract overviews
- Evidence rule: every factual claim citable to authoritative source. If not citable, flag as folklore.
- [Country-specific OR comparative analysis preferences — whichever fits your domain]
- Primary sources preferred over user-reported forum evidence (label clearly when forum-derived)

### Hard constraints
- [Geographic constraints — sanctioned jurisdictions, compliance requirements]
- [Terminology rules — professional credentials, scope of practice]
- [Anything you specifically do NOT want included]

### Output format
- Structured report with sections + tables for comparisons
- Citations to primary sources at each major claim
- Explicit "what we found vs couldn't verify" honesty
- 3-5 actionable takeaways the brand could ship as customer-facing content
- Flag findings that contradict common industry assumptions

### Research question

[YOUR SPECIFIC RESEARCH QUESTION HERE]
```

R-Kai then runs autonomously for 15-40 min. Output report goes back to S-Kai for strategic synthesis.

---

## Memory setup — specific steps with example

### Where memory lives

Claude Code stores per-project memory at:
- **Windows**: `C:\Users\<you>\.claude\projects\<encoded-project-path>\memory\`
- **macOS/Linux**: `~/.claude/projects/<encoded-project-path>/memory/`

The `<encoded-project-path>` is automatically computed by Claude Code from your project's absolute path. To find yours:
1. Open Claude Code in your project
2. Type: `Get-Location` (Windows PowerShell) or `pwd` (macOS/Linux)
3. Replace `/` and `\` with `-` and prefix with `c--` (Windows) or just `-` (Unix)
4. OR just ask S-Kai in the first session: "What's the absolute path to my memory directory?"

### The index file

Create `MEMORY.md` in that directory. This is auto-loaded into every session's context (truncated to ~200 lines). Format:

```markdown
- [Short title](file-name.md) — one-line hook explaining what's in this memory
- [Another memory](other-file.md) — one-line hook
```

Each entry is one line under ~150 chars. The hook is what S-Kai sees at session start to decide whether to deep-read the file.

### Memory file format

Each memory file has YAML frontmatter + markdown body:

```markdown
---
name: short-kebab-case-slug
description: One-line summary used to decide relevance in future sessions. Be specific.
metadata:
  type: feedback
---

## The rule / decision / fact

(Memory body in markdown. For feedback + project memories, lead with the rule then add **Why:** and **How to apply:** lines — captures reasoning so future-you can judge edge cases.)
```

### Memory types

| Type | When to use |
|---|---|
| `user` | Facts about you (background, role, preferences) |
| `feedback` | Discipline rules from past sessions ("don't suggest X unprompted", "always verify Y", "X is the wrong approach because Z") |
| `project` | Strategic decisions + product state (architectural calls, why-we-built-it-this-way, current scope) |
| `reference` | Pointers to external systems (dashboards, API docs, registrar accounts) |

### Example first memory (copy + adapt)

Create `user_profile.md`:

```markdown
---
name: User profile
description: [Your name], [your role/experience], building [project]. Key context for tailoring future work.
metadata:
  type: user
---

[Your name] is a [role + experience]. Building [project] — [what it is + who it's for].

**Background that shapes how I work:**
- [Domain expertise — e.g. paramedic, finance, design]
- [Years experience]
- [Specific operating mode preferences]

**Project goals:**
- [Primary goal, e.g. ship MVP by X date]
- [Secondary goals]

**Communication preferences:**
- [Tight + honest / detailed + explanatory / etc.]
- [Specific Claude-tropes to avoid]
```

Then add to `MEMORY.md`:
```
- [User profile](user_profile.md) — [your name + role + project one-liner]
```

That's the minimal viable memory. S-Kai will read it at session start and have context about who you are + what you're building.

### When to add memories

Capture as decisions/insights/rules land. Don't batch at session end (you'll forget). Common triggers:
- User explicitly says "remember this" / "from now on" / "always"
- User corrects a Claude pattern ("don't do X")
- User confirms a non-obvious approach worked ("yes exactly, keep doing that")
- Strategic decision made in conversation that affects future work
- Pattern emerges across 2-3 incidents

---

## Appendix A — Starter skill file templates

These are intentionally generic; adapt to your domain. The SabaiFly versions are more SabaiFly-specific (HCPC compliance, locale rules, etc.) — yours will be different.

### `.claude/skills/s-kai/SKILL.md`

```markdown
---
name: s-kai
description: Activate S-Kai (planner/strategic) role discipline. Use when starting a strategic session — writing briefs, making decisions, sequencing work, coordinating parallel I-Kai sessions. DO NOT use for direct implementation — use /i-kai instead.
---

# S-Kai — planner/strategic role

You are **S-Kai**. Your job is **strategy, briefs, decisions, sequencing, coordination** — NOT implementation. The pattern exists for context-window economy: S-Kai holds the strategic plan; I-Kai holds implementation context.

## What S-Kai SHOULD do
- Write briefs to `docs/BRIEF-I-KAI-*.md` for I-Kai to execute
- Make architectural / scope / sequencing decisions with the user
- Maintain handoff docs at session boundaries
- Spot-check I-Kai's output AFTER it ships
- Update memories when patterns emerge

## What S-Kai should AVOID
- Editing code directly (except trivial one-liners or urgent bug-fixes)
- Refactoring at scale — those are I-Kai jobs from a brief
- Building features end-to-end inline

## The decision tree
1. 30-second tweak? → Just do it.
2. 5-minute decision? → Discuss + decide + log. No code.
3. >15 min of implementation? → STOP. Write a brief. Don't build.

## Verify facts before asserting
For external services, APIs, SDKs, pricing, regulations — DEFAULT to WebSearch rather than recalling from training data. Training data ages.

## Session-end decision capture
Before ending a session, sweep for decisions/insights worth keeping. Capture as memory or docs commits. Anything in chat history alone is lost.

(Expand with your project-specific conventions.)
```

### `.claude/skills/i-kai/SKILL.md`

```markdown
---
name: i-kai
description: Activate I-Kai (implementation/code) role discipline. Use when executing a specific brief from S-Kai. DO NOT use for planning/decisions — use /s-kai.
---

# I-Kai — implementation role

You are **I-Kai**. Your job is to **execute the brief, ship working code, commit cleanly, escalate when scope is unclear**.

## Session-start protocol
1. `git fetch origin && git pull origin <branch> --rebase` — sync with remote BEFORE work (critical when parallel I-Kai sessions exist)
2. Read the brief end-to-end
3. Read CLAUDE.md if not in context
4. Check git status + recent commits
5. Begin implementation

## What I-Kai should AVOID
- Drifting into planning or scope expansion
- Patching around problems (only complete fixes)
- Deferring small items to "later sessions"
- Shipping with red typecheck / lint / tests

## Git sync for parallel sessions
- `git pull --rebase` before each commit if time has passed
- `git pull --rebase` before each push
- On non-fast-forward push: rebase, resolve, retry
- Never force-push without explicit user approval

## When to escalate
- Brief scope unclear or contradicts itself
- Implementation reveals unflagged dependency
- "Trivial fix" turns out to need >30 min unplanned work

(Expand with your project-specific conventions.)
```

---

## Appendix B — Safety + privacy note

Before sharing your own version of this primer publicly:

- **Scrub credentials, API keys, env var VALUES** (mentioning env var NAMES is fine)
- **Don't include actual code from proprietary projects** — describe patterns abstractly
- **Don't include private business metrics** (revenue, customer count, churn) unless you want them public
- **Workflow patterns ARE shareable** — the discipline is generic; only the project-specific application is proprietary
- **Credit appropriately** — pattern originators deserve attribution if you're building on their work

---

## The honest limitations

- **Cost.** Three parallel Claude sessions on Opus + Sonnet uses real tokens. Budget for it.
- **Discipline overhead.** The system rewards consistent capture; it punishes shortcuts. If you skip writing briefs and just chat with Claude, you lose the parallelism benefit.
- **Learning curve.** Three weeks to feel comfortable. Three months to feel fluent. Six months for it to feel like second nature.
- **Not magic.** AI still makes mistakes. The discipline catches more of them than no discipline does, but you remain the verifier-of-last-resort.

---

## When this pattern wins

- Solo builders shipping serious products
- Domain experts (paramedics, finance professionals, lawyers, etc.) applying their expertise to AI-amplified work
- People who experience friction in their workflow and want to encode the fix once
- Anyone running multiple workstreams that compete for cognitive load

## When this pattern is overkill

- Quick one-off scripts
- Prototyping where you haven't decided what you're building
- Pair programming where you want a single conversational thread
- Teams of 3+ humans (different coordination patterns work better)

---

## Final note

The pattern only works because the human is the orchestrator. Each Kai is bounded; you bridge them. Your domain expertise, judgment, taste, and calibration radar are the load-bearing part — the Kais multiply your effective output but don't replace you.

If you find yourself doing less thinking, not more, something's wrong with how you're using the system. The whole point is to FREE your thinking from mechanical execution so you can apply it to the decisions that actually matter.

— Gareth Scott + Kai (S-Kai mode, partnership across sessions)
2026-05-25
