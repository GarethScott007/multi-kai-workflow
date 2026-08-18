# MEMORY — boot index

> This file is auto-loaded into **every** session in this project (truncated to roughly the first
> 200 lines), so it is the one memory artefact you can rely on being read. Treat it as an **INDEX,
> not the content**: one line per memory, each a hook that helps a session decide whether to open
> the file. **Never answer from an index line alone** — the reasoning lives in the file, and index
> lines go stale faster than bodies do.
>
> Everything below is an **EXAMPLE**. Delete it and write your own on day one.

## ⛔ NON-NEGOTIABLE
<!-- The two or three rules you never want re-litigated. Keep this section brutally short —
     if everything is non-negotiable, nothing is. -->
- [Verify before asserting](feedback_verify_before_asserting.md) — external facts get checked live, never recalled; label every claim verified / recalled / inferred.

## Who / how we work
- [User profile](user_profile.md) — who the principal is, what they're building, how they want to be talked to.

## Live state / decisions
- [Deploy target ruling 🔒](project_deploy_target_ruling.md) — 🔒 LOCKED 2026-08-12: single region, EU-west. EXIT-EVENT: first paying customer outside the EU.

## Lessons
> Once you pass ~20 lessons, stop listing them here individually and point at the MOC instead.
- **[hubs/Lessons-Learned](hubs/Lessons-Learned.md)** — the failure-mode library. **V-Kai reads this before every review.** 2 lessons.

---

### How to keep this file useful

- **One line per memory, under ~150 characters.** The hook is what a session sees at boot.
- **Compact it when it grows heavy.** Mature lesson-tier pointers move into topic MOCs under
  `hubs/`; this index keeps identity, working rules, live state, and anything post-MOC.
- **Status belongs in the line.** `🔒 LOCKED`, `⛔ BLOCKER`, `✅ SHIPPED 2026-08-12`,
  `SUPERSEDED` — a session should be able to triage without opening anything.
- **When a status changes, fix the line AND the file's `description:` in the same edit.** A stale
  description outranks an updated body in semantic recall, so a memory whose body says RESOLVED and
  whose description still says "not yet fixed" actively misinforms every future search.
