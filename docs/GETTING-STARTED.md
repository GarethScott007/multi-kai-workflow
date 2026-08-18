# Getting started — from a clone to a running multi-Kai pipeline

A cold-start walk. Follow it top to bottom; each step assumes the previous one. Budget **about an
hour**, most of it waiting on downloads.

At the end you will have: the three role skills primed at user scope, a harness-enforced dispatch
gate, a semantic-recall memory server over your own vault, and a first `/s-kai` session that boots
into all of it.

**Contents**
- [0. What you need](#0-what-you-need)
- [1. Claude Code in VS Code](#1-claude-code-in-vs-code)
- [2. Install the role skills — at USER scope](#2-install-the-role-skills--at-user-scope)
- [3. Apply the settings template](#3-apply-the-settings-template)
- [4. Stand up the memory server](#4-stand-up-the-memory-server)
- [5. Seed your vault](#5-seed-your-vault)
- [6. Your first `/s-kai` session](#6-your-first-s-kai-session)
- [7. Your first full pipeline lap](#7-your-first-full-pipeline-lap)
- [8. Working away from the machine](#8-working-away-from-the-machine)
- [9. Where to go next](#9-where-to-go-next)

---

## 0. What you need

- **A Claude subscription.** A plan with room for parallel sessions matters more than raw speed —
  the whole point is running a planner, an implementer and a verifier without rationing.
- **VS Code**, and **git**.
- **Python 3.11+** for the memory server. [`uv`](https://docs.astral.sh/uv/) is recommended.
- **A project.** Not a toy. The pattern's value is proportional to how much context you are
  currently losing between sessions, and a scratch repo loses none.

> **A note on the war stories.** The skills and playbooks are full of dated incidents naming a real
> product (SabaiFly) and a real person (Gareth). **That is deliberate** — a rule with a date, a cost
> and a real noun is checkable; a sanitised one is a slogan. Read them as evidence, not as
> instructions about someone else's project.
>
> You will also see `[[double-bracket]]` links and backticked `feedback_*` / `project_*` /
> `reference_*` slugs. Those point into the author's own **private** memory vault. **They are
> expected to be dead for you.** Read them as "this rule has a receipt somewhere", not as broken
> links to chase.

---

## 1. Claude Code in VS Code

Install the Claude Code extension from the VS Code marketplace and sign in. Open a terminal in your
project root and confirm the CLI is on your path:

```bash
claude --version
```

Standardise on **one dev-server port** for the project now, and write it into your `CLAUDE.md`.
It sounds trivial. It stops a whole class of confusion later, when a verifier attaches to a server
someone else's session started and confidently reports on code it never loaded.

---

## 2. Install the role skills — at USER scope

Copy the three skills into your **user** skills directory, not into the project:

```bash
mkdir -p ~/.claude/skills
cp -r skills/s-kai skills/v-kai skills/i-kai ~/.claude/skills/
```

```powershell
# Windows PowerShell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills" | Out-Null
Copy-Item -Recurse -Force .\skills\s-kai, .\skills\v-kai, .\skills\i-kai "$env:USERPROFILE\.claude\skills\"
```

Restart Claude Code, then confirm `/s-kai`, `/v-kai` and `/i-kai` are offered.

### ⚠️ Why user scope, and the drift trap

A **project-scoped** copy at `<repo>/.claude/skills/` **wins** over the user-scope one. That is
sometimes what you want — and it is a trap, because from then on the project copy is the one that
runs and nothing tells you when it falls behind.

Measured, on the origin project: a project-scoped copy sat **37 days behind** the user-scope
version. Every lesson banked into the skills in those five weeks — new gates, new pre-flights —
was silently not applied in the one repo that mattered most, while the author believed they were.

**So:**
- Keep exactly ONE copy of each skill, at user scope. **Don't fork the skills per project.**
- Project-specific rules go in the project's `CLAUDE.md`, which the skills defer to by design.
- Turn `~/.claude/skills` into its own private git repo. Skill edits are *rule* changes; they
  deserve versioning and an off-machine backup as much as your code does.
- If you ever do need a project-scoped copy, put an expiry date in it, in the file, in bold.

---

## 3. Apply the settings template

Read `settings-template/README-SETTINGS.md` first — it explains the three tiers and why the fourth,
full-autonomy posture is not shipped.

Then merge `settings-template/settings.template.json` into `~/.claude/settings.json`. **Merge, do
not overwrite** — you will lose your model choice, theme and plugin list otherwise. Replace the two
placeholder entries with your project's real schema-mutating commands.

This gives you two things:

1. **The ask-list** — destructive operations still happen, but they stop and ask first.
2. **The dispatch pre-flight hook** — four questions injected before every agent launch. This is the
   only **L4** rung in the pack: it executes without the model's cooperation, which is precisely why
   it is the one gate that stopped producing repeats.

**Verify the hook actually fires.** A hook you have never seen fire is indistinguishable from a typo
in your settings file:

```bash
python -m json.tool < ~/.claude/settings.json > /dev/null && echo "settings.json parses"
```

Then launch any trivial subagent and confirm the four questions appear in the response. If they
don't, check that the matcher covers the tool name your client uses for subagent launches.

---

## 4. Stand up the memory server

Full instructions: `memory-starter/memory-server/README.md`. The short version:

```powershell
cd memory-starter\memory-server
uv venv
uv pip install -e .
copy sources.example.json sources.json
uv run python scripts/smoke_test.py
```

Run installs from **PowerShell** on Windows, not Git Bash/MSYS — a POSIX-emulation shell there can
write package metadata the native runtime cannot resolve while the wrappers still exit 0.

Out of the box `sources.json` points at this repo's example vault, so the smoke test passes before
you have a vault of your own. That is intentional: it separates "did the install work?" from "is my
config right?", and you want those answered one at a time.

Then the runtime proof — the server driven through the real MCP protocol, the way a client does it:

```powershell
uv run python scripts/mcp_client_check.py
```

**Register it at user scope**, so recall spans every project. Use the venv's own interpreter — an
MCP client does not activate a virtualenv, so the interpreter path *is* the environment selection:

```powershell
claude mcp add --scope user sabai-memory -- "<your-clone>\memory-starter\memory-server\.venv\Scripts\python.exe" -m sabai_memory
```

Restart Claude Code, then `claude mcp list`.

**Two gotchas worth knowing before they bite:**
- A user-scope registration lives in **`~/.claude.json`** — not in any repo, not in `settings.json`.
  People look for it in the project, don't find it, and register a duplicate at project scope.
- **Freshness and boot are two different mechanisms.** A file-watcher catches writes while the
  server runs; a boot-time SHA reconcile catches everything that changed while it didn't. So the
  first launch after a long gap does real work — give it a moment before deciding it is broken.

---

## 5. Seed your vault

Find your project's memory directory. It is derived from the project's absolute path:

```
~/.claude/projects/<encoded-project-path>/memory/
```

The reliable way to get it: ask Claude Code, **inside the project**, *"what is the absolute path to
my memory directory?"*

Then:

```bash
mkdir -p ~/.claude/projects/<encoded-project-path>/memory/hubs
cd ~/.claude/projects/<encoded-project-path>/memory
git init            # PRIVATE remote — this is your brain, not a portfolio piece
```

Copy the shapes from `memory-starter/vault/` (the content is invented — copy the form, not the
facts). Write two files on day one:

1. **`user_profile.md`** — who you are, your domain background, how you want to be talked to.
   Every other memory assumes this context.
2. **`hubs/Lessons-Learned.md`** — even nearly empty. **V-Kai dereferences it on every single
   pass**, and a pre-flight pointing at a missing file silently does nothing.

Read `memory-starter/conventions.md` before you write the third. The one convention people skip and
then pay for: **the `description:` field is a query target, not a summary.** It is embedded as its
own chunk and routinely outranks the body, so it must carry the real answer's tokens, in two
registers, with a dated status stamp.

Finally, add the new directory to `sources.json` and restart Claude Code once. Skip this and your
memories get written but are never searchable — the worst of both worlds.

---

## 6. Your first `/s-kai` session

```
/s-kai

Hi S-Kai. I'm setting up <PROJECT> — <one line: what it is and who it's for>.

My background: <your domain + relevant experience>
My situation: <solo / team size> + <stage: pre-launch / live / iterating>

Before we start working:
1. Read CLAUDE.md if it exists — or propose what we'd put in one, using
   templates/CLAUDE-MD-TEMPLATE.md as the shape.
2. Confirm you understand your role: strategy, briefs and decisions — NOT implementation.
3. Propose my three DOMAIN GATES — the checks a verifier must always run for this
   project. Derive them by asking, per surface: "if this is wrong, who finds out,
   and when?" The ones where the answer is "a customer, months later, silently"
   are the gates.
4. Propose the first 2-3 decisions worth capturing as memory.
```

That fourth item is the one that compounds. Capture decisions **as they land**, never batched at
session end — the batch never happens.

**Returning sessions** are much shorter:

```
/s-kai

Read the latest docs/HANDOFF-*.md and skim MEMORY.md.
Check git log --oneline -10.
Acknowledge state + propose the pickup move.
```

---

## 7. Your first full pipeline lap

Do a real one, on something small. The habit forms on the first lap, and the gates are cheapest to
adopt before there is anything to lose.

1. **S-Kai writes a brief** → `docs/BRIEF-I-KAI-<TOPIC>.md`, using `templates/BRIEF-TEMPLATE.md`.
   Existence-probe every symbol it names. Fill in `Memories to stamp on merge:` — never blank.
2. **V-Kai reviews the brief.** Spawn a subagent and **tell it to read
   `~/.claude/skills/v-kai/SKILL.md` first** — a spawned subagent does not auto-load a skill and
   cannot invoke slash commands. Hand it the brief path. Expect findings; a brief review that
   returns "looks good" everywhere is a failed review.
3. **I-Kai builds it** in `/i-kai`, in its own worktree if anything else is running.
4. **V-Kai reviews the build** — hand it `git diff <trunk>...<branch>` plus your domain gates by name.
5. **S-Kai merges**, checking the merged tree (not either parent), then harvests: stamp the memories
   the build falsified, promote anything portable into `playbooks/`, and log the gate telemetry.

Resist *"it's a small project, skip the gates."* Full method: `playbooks/playbook_multi_kai_pipeline.md`.

---

## 8. Working away from the machine

Three independent capabilities. You do not need all of them; they are listed cheapest-first.

### 8a. Connectors on claude.ai

Connectors let a claude.ai conversation reach an external service (issue tracker, error monitor,
hosting platform) directly. Configure them in your claude.ai connector settings.

Two things that cost real time otherwise:

- **Connectors surface at session start.** One added mid-session usually is not visible until you
  start a new one. If a tool you just added is "missing", restart before you debug anything.
- **⛔ "Tools visible" is not "auth works."** A connector can list its tools perfectly while its
  token is expired. So make **one harmless REAL call** — a read, a `whoami` — against every
  connector the session's work depends on, at session start. This is step 0b in the S-Kai skill,
  and it exists because a dead connector that someone had *restarted a session for* went unnoticed.
  Scope it to what you actually need; don't ping everything ritually.

### 8b. Remote sessions on claude.ai/code

Claude Code sessions can be driven from the browser against a connected repository — useful for
reviews, doc work and reading from a phone. It works on the repo, not on your machine: it cannot
see your local dev server, your `.env`, or anything uncommitted. For "check the served bytes of the
thing I'm building right now", you want the tunnel below.

### 8c. The tunnel-as-a-service pattern

The problem: you want the **real dev machine** — its running server, its data, its uncommitted
working tree — from a laptop or phone, without leaving a terminal window open.

The pattern: run the editor's tunnel **as an operating-system service** rather than as a foreground
command. A service survives closed windows, survives sign-out, and restarts at login.

```powershell
# One-time, from an elevated PowerShell. <tunnel-name> is yours; keep it boring and private.
code tunnel service install --accept-server-license-terms --name <tunnel-name>
code tunnel status
```

Then reach it at `https://vscode.dev/tunnel/<tunnel-name>/<path-to-your-project>`. To read a running
dev server on the road: open that URL → **Ports** tab → forward your dev port → the globe icon →
append the path you want.

**⛔ DIAGNOSE FIRST — the most important rule here.** Before running any fix, run:

```powershell
code tunnel status
```

If it reports `Connected`, the service installed, and a **fresh** last-connected timestamp, **the
tunnel is UP — stop.** Do not run the repair recipe. The repair can force a fresh device
authorisation, which needs the machine you are not sitting at, and will strand you mid-trip. A
transient failure reason followed by `Connected` means it already recovered; ignore it.

**Two processes is not automatically a fault — read the command lines.** One process running the
tunnel *service* is the live gateway and owns the registration: **keep it.** A separate
*agent-host* process is a leftover remote-session server from a past connect; harmless, a fresh one
spawns whenever a client connects. **The real fault is multiple *service* processes fighting over
the registration** — that is what produces "gateway is not currently running", and it is caused by
running ad-hoc tunnel commands in terminals alongside the service.

**Repair recipe — only when status is genuinely not connected:**

```powershell
Stop-Process -Name code-tunnel -Force
code tunnel service uninstall
code tunnel service install --accept-server-license-terms --name <tunnel-name>
code tunnel status     # must now show a fresh start time and Connected
```

**Then never start an ad-hoc tunnel in a terminal again** — the service owns it, and ad-hoc runs
recreate the multi-process wedge.

**Residual risks, worth knowing before you rely on it:** the machine sleeping kills the tunnel, and
after a reboot it only returns once your OS user has logged in. If a trip depends on it, check
status before you leave.

---

## 9. Where to go next

- **`docs/ADAPT-TO-YOUR-PROJECT.md`** — a full worked example of mapping the roles, deriving domain
  gates, and a first-week plan. Read this next.
- **`playbooks/playbook_new_project_bootstrap.md`** — the same walk, compressed to a checklist.
- **`playbooks/playbook_operating_manual.md`** — the craft beneath the procedures. Read it when a
  situation no checklist anticipated turns up, which will be soon.
- **`THE-VERIFIER-AND-THE-BRAIN.md`** — why the verifier and the learning loop exist at all.

**The test of a good setup** (from the bootstrap playbook): *the first verifier verdict in your new
project cites a lesson learned somewhere else.* If that happens, the machinery is real — the brain
is not just storing, it is applying.
