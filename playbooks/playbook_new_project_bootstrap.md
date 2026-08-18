---
name: playbook_new_project_bootstrap
aliases:
  - new-project-bootstrap
description: "PORTABLE playbook — the hit-the-ground-running checklist for starting ANY new project on the multi-Kai pipeline: wire memory, skills, pipeline, model tiers, and backups in under an hour."
metadata:
  node_type: memory
  type: reference
---

# New-project bootstrap — hit the ground running

The order matters; each step assumes the previous. Budget: under an hour, mostly waiting on git.

1. **Recall reflex — make it global once.** Your user-scope `~/.claude/CLAUDE.md` tells EVERY session on the machine to search the memory MCP before substantive work — write that instruction once and every future project inherits it. Verify the MCP is registered (`claude mcp list`); re-register per `memory-starter/memory-server/README.md` if it drops.
2. **Memory dir.** The first session in the new repo creates `~/.claude/projects/<encoded-project-path>/memory/`. Immediately: `git init`, a **private** remote (`<project>-vault`), and adopt [playbook_memory_conventions](playbook_memory_conventions.md) from the first memory written (aliases + quoted descriptions + commit-per-write). Seed it from `memory-starter/`.
3. **Index the new vault for recall.** Add the new memory dir as a source in the memory server's `sources.json` so cross-project search covers it, then restart Claude Code once (MCP servers load at session start).
4. **Skills.** The Kai role skills live at **user scope** in `~/.claude/skills` (keep that directory as its own private git repo so skill edits are versioned and backed up). They are project-neutral at the core; project specifics (domain gates, conventions, brief paths) go in the NEW repo's `CLAUDE.md`, which the skills defer to. **Don't fork the skills per project** — a project-scoped copy WINS over the user-scope one and then silently rots behind it (measured at 37 days behind, in the origin project). Extend via `CLAUDE.md`.
5. **Project CLAUDE.md.** Write it session one: codebase conventions, the project's domain gates (the things V-Kai must always check — every project has its own "11-locale / moat" equivalents), escalation rules, port/tooling facts.
6. **Pipeline on.** First real feature: S-Kai brief → V-Kai brief gate → I-Kai worktree build → watcher → V-Kai build gate → merge, exactly per [playbook_multi_kai_pipeline](playbook_multi_kai_pipeline.md). Resist "it's a small project, skip the gates" — the gates are cheapest when habits form.
7. **Model tiers.** Apply [playbook_model_tiering](playbook_model_tiering.md) from day one — including tier-0 local Qwen for bulk drafts and the top-tier-as-oracle rule for whatever the strongest metered model is at the time.
8. **Pre-flight library.** V-Kai pre-flights against BOTH the new project's (initially empty) lessons AND the portable playbooks in this directory — [playbook_verification_doctrine](playbook_verification_doctrine.md) and [playbook_fable_failure_modes](playbook_fable_failure_modes.md) apply from the first review, so the new project inherits every scar without re-earning it.
9. **Backups check (own-the-stack).** Before the first week ends: vault repo pushed · skills repo pushed · playbooks repo pushed · project repo on a private remote · anything else that would hurt to lose, in git. A backup that has never been restored is a hope — clone one of them fresh onto a second machine, once.

The test of a good bootstrap: the first V-Kai verdict in the new project cites lessons learned in the old one.

Related: every other playbook in this directory.
