# Settings + hooks — the three-tier permission architecture

Two things live here, and they do very different jobs:

1. **A harness-enforced hook** — the dispatch pre-flight. This is the pattern's only **L4** rung:
   it executes *without the model's cooperation*, which is why it is the one gate that stopped
   producing repeats. Ship it as-is.
2. **A permission architecture in three tiers** — so the prompts you see are the ones that
   actually deserve a human decision, and everything else either flows or is blocked.

---

## Part 1 — the dispatch pre-flight hook

`settings.template.json` carries it verbatim. It fires on **every** agent/workflow/task launch and
injects four questions the model must answer in writing, in its visible response, before it can
proceed:

1. **WRITES?** — does any agent in this launch write to a repo? (Docs and fixtures count. Running a
   gate counts until proven write-free. **A mutate-control — break-then-restore — counts as a
   WRITE.**)
2. **CONCURRENT?** — is any already-running task writing to the same tree? Enumerate your running
   background tasks. *Only the dispatcher can see both sides.*
3. **ISOLATION?** — if writes overlap: isolate (one worktree per writer) or serialise. Sharing a
   tree requires a one-line written justification, and then every other writer waits or isolates.
4. **WATCHER?** — if this launch starts a build whose completion must trigger a review, arm the
   completion watcher NOW, at dispatch.

If the launch is read-only and nothing else is running, the model says exactly that in one line and
continues. **Cost: one sentence per dispatch.**

### Why a hook and not a rule

This is the whole thesis of `playbooks/playbook_enforcement_ladder.md`, and it was paid for:

> An orchestrator **banked** the rule *"mutating agents get an exclusive worktree"* at ~09:00 and
> **violated it at ~10:00** — same session, same agent, the lesson still in its context window.
> Recall was 100%. It failed anyway.
>
> The cost: a second writing agent fanned into a tree where a long-running one was mid-flight. The
> running agent watched a tracked file go clean→dirty across its own gate run and filed a finding
> that the brief's *"this gate is write-free"* claim was false. **It wasn't false** — the write was
> the sibling's. So the output was a **false finding against a correct brief, carrying evidence**,
> which would have been folded into the next revision had nobody tested it. The agent was blameless:
> an agent structurally *cannot* see its siblings.

*"Search the brain harder"* and *"write it more emphatically"* both target a layer that did not
fail. The moment of action needed a mechanism, so the check lives at the dispatch moment, in the
harness. The platform's own guidance says the same thing: automated always/never behaviours must be
hooks, because **the harness executes these, not the model — memory and preferences cannot fulfil
them.**

### Keep it at four questions

A checklist longer than a breath decays into pattern-matched ritual — which is itself the failure
mode of the rung below. If a moment needs more than four, split the moment.

### Verify it actually fires

A hook you have never seen fire is indistinguishable from a typo in your settings file. After
installing: launch any trivial subagent and confirm the four questions appear in the response. If
they don't, check that `~/.claude/settings.json` parses (`python -m json.tool < ~/.claude/settings.json`)
and that the matcher covers the tool name your client actually uses for subagent launches.

---

## Part 2 — the three tiers

| Tier | File | Scope | Contains | Ships? |
|---|---|---|---|---|
| **1. User** | `~/.claude/settings.json` | Every project on the machine | The **ask-list** of destructive operations + the hook | ✅ `settings.template.json` |
| **2. Project** | `<repo>/.claude/settings.json` | This repo, all contributors | A **read-only-plus-verify allowlist** — the safe, high-frequency commands | ✅ block below (checked in) |
| **3. Session** | `<repo>/.claude/settings.local.json` | You, this machine, right now | Whatever accreted during real sessions | ❌ **gitignored, never** |

The tiers exist because permission decisions have three completely different lifetimes. Mixing them
is what produces the two failure states everyone ends up in: prompt fatigue (so you approve
everything on autopilot) or a blanket allow (so nothing is ever checked).

### Tier 1 — user scope: the ask-list

This is the **deny-ish** tier: operations that are destructive, irreversible, or push to somewhere
public. They are always allowed to *happen* — they just require you to say yes, once, in the moment.

Copy `settings.template.json` into `~/.claude/settings.json` (merge with what is already there —
don't blindly overwrite; you will lose your model choice, theme and plugin list).

Replace the two placeholder entries with your project's real schema-mutating commands:

```jsonc
"Bash(<your db-mutating commands, e.g. the migrate/push/seed scripts>*)",
"PowerShell(<your db-mutating commands, e.g. the migrate/push/seed scripts>*)"
```

⚠️ **The ask-list is duplicated per shell for a reason.** If you use both a POSIX shell and
PowerShell, an entry in one does **not** cover the other, and the gap is silent — you find out when
a `git push --force` sails through the shell you forgot. The template ships both halves; keep them
in sync when you add entries.

⚠️ **A Windows note that generalises:** the patterns are prefix-matched against the command string.
`rm -rf ~*` does not catch `rm -rf "$HOME"`. Treat the ask-list as a speed bump against accidents,
not as a security boundary against a determined process.

### Tier 2 — project scope: the read-only-plus-verify allowlist

This is the tier that buys back your attention. It goes in `<repo>/.claude/settings.json` and gets
**checked in**, so every contributor gets the same low-friction floor. Everything in it must be
either read-only or trivially reversible.

```jsonc
// <repo>/.claude/settings.json  — checked in
{
  "permissions": {
    "allow": [
      // --- read-only inspection ---
      "Read(*)",
      "Glob(*)",
      "Grep(*)",
      "Bash(git status*)",
      "Bash(git log*)",
      "Bash(git diff*)",
      "Bash(git show*)",
      "Bash(git branch --list*)",

      // --- verification: your gates, by name ---
      "Bash(<your typecheck command>*)",      // e.g. pnpm typecheck
      "Bash(<your lint command>*)",           // e.g. pnpm lint
      "Bash(<your unit test command>*)",      // e.g. pnpm test
      "Bash(<your e2e test command>*)",       // e.g. pnpm test:e2e
      "Bash(<your build command>*)",          // e.g. pnpm build

      // --- research ---
      "WebSearch",
      "WebFetch",

      // --- your memory MCP: read tools only ---
      "mcp__<your-memory-server>__search_memory",
      "mcp__<your-memory-server>__get_memory",
      "mcp__<your-memory-server>__stats",
      "mcp__<your-memory-server>__list_projects"
    ]
  }
}
```

Two things to notice, because both are load-bearing:

- **The memory server's tools are listed individually, not with a wildcard.** The server ships
  read-only by design (there are no write tools), and enumerating them keeps that property visible
  in your own config rather than trusting it silently. If a future version ever gained a write tool,
  a wildcard would have granted it in advance.
- **`Write` and `Edit` are deliberately absent.** Editing is the thing you actually want to see
  happening. If you find yourself approving edits constantly, that is a signal to give the agent an
  isolated worktree, not a signal to widen the allowlist.

### Tier 3 — `settings.local.json`: the accretion sink

Real sessions generate one-off permission needs. Those land in
`<repo>/.claude/settings.local.json`, which **your `.gitignore` must exclude and which must never
ship.** Two reasons, and the second is the one people miss:

1. It is machine-specific — absolute paths, local ports, personal tool choices.
2. **It is an audit surface.** Reading someone's accreted local allowlist tells you which commands
   they run, against which hosts, with which flags. That is reconnaissance, published by accident.

Sweep it occasionally: anything in there that has proven safe and is genuinely repo-wide should be
*promoted* into tier 2 deliberately, and the rest deleted. An allowlist that only ever grows is
a blanket allow with extra steps.

Confirm the exclusion is real:

```bash
git check-ignore -v .claude/settings.local.json   # must print a matching .gitignore rule
```

---

## ⛔ Part 3 — the full-autonomy posture (explicit opt-in, with the warning)

There is a fourth configuration, and this pack **does not ship it**: a blanket allow for
`Bash(*)` / `PowerShell(*)` / `Edit(*)` / `Write(*)`, which turns off approval prompts for
essentially everything.

**It is a real and sometimes correct choice.** Long autonomous runs — an overnight build, a
multi-hour audit fleet — are impossible if every file write blocks on a human who is asleep. The
original author runs this posture, deliberately.

**But it is a posture, not a default, and it must be chosen with the trade understood:**

- **The ask-list still applies.** `ask` beats `allow`, so the destructive operations in tier 1 keep
  prompting. That is what makes the posture survivable — do not remove them at the same time.
- **The blast radius becomes "everything the process can reach."** Not just the repo: your home
  directory, your other repos, your credentials, any host you can reach. Agents make mistakes with
  paths, and a wrong path plus a recursive delete is not recoverable by `git`.
- **Pair it with isolation, always.** Any writing agent gets its own worktree (that is what the
  dispatch hook's question 3 is for). Full autonomy in a *shared* tree is how you get a false
  finding against a correct brief — or worse, one agent committing onto another's branch and a
  recovery `reset` destroying both. That has happened; it is in the doctrine.
- **Pair it with a working backup.** Vault pushed, skills pushed, repo pushed to a private remote.
  And a backup that has never been restored is a hope — do one restore drill.
- **Never combine it with a shell that swallows errors.** Read the last lines of a log, not the
  exit code.

If you want it, add it to **tier 1** consciously and write a line in your `CLAUDE.md` saying you
run this posture and why — so a future session (and a future you) knows it was a decision, not
an accident.

If you are new to the pattern: **run tiers 1–3 for a few weeks first.** The prompts you get are
data. They tell you which commands you actually run often enough to promote, and that is a much
better allowlist than one you guessed at on day one.
