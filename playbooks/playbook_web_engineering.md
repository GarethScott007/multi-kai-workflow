---
name: playbook_web_engineering
aliases:
  - web-engineering-portable
description: "PORTABLE playbook — Fable 5's parting web-engineering lessons for S-Kai briefs and I-Kai/V-Kai checks: verify the shipped artifact not the dev server, cache-boundary and hydration bug classes, expand-migrate-contract deploys, DB-constraint-not-app-check, webhook idempotency, env schema at build time, test the failure path, restore drills."
metadata:
  node_type: memory
  type: reference
---

# Web engineering — Fable's parting lessons (2026-07-12)

Written for a Next.js/Vercel/Postgres stack but portable. Each entry: the bug class → the check that catches it. S-Kai bakes these into briefs; I-Kai runs them as gates; V-Kai attacks with them.

## The master rule

**Verify the artifact that SHIPS, not the artifact that's convenient.** `next dev` has no minifier (the Lightning-CSS prefix bug proved it), different caching, different error surfaces. Every binary gate runs against `next build && next start` or a preview deploy. Three environments — dev, prod build, deployed edge — and a pass in the wrong one is not a pass.

## Bug classes for briefs and reviews

1. **Cache-boundary leaks (App Router).** Server-component data cached across users or locales; a `cookies()`/`headers()` call silently flipping a route dynamic; ISR serving stale after deploy. *Check: two requests differing ONLY in locale/user → diff the served bytes; assert the varying field actually varies.*
2. **Hydration mismatch.** Server and client render differently — `Intl`/timezone formatting, `Date.now()`, random IDs, `window` guards. *Check: build output console clean of hydration warnings on the key templates; format dates/numbers in ONE place with an explicit locale+TZ.*
3. **Expand → migrate → contract.** Never deploy code that requires a schema the DB doesn't have yet, or drop a column code still reads. Order: additive migration ships first, code second, destructive cleanup third — each independently deployable and revertible. *Check in review: does this diff read/write any column/table the CURRENT production schema lacks?*
4. **Uniqueness lives in the constraint, not the check.** Serverless means concurrent invocations; check-then-write races are guaranteed eventually (pairs with the write-time-backstop-races lesson). *Rule: every "only one X per Y" claim maps to a DB unique constraint or an atomic upsert; the app-level check is UX, not integrity.*
5. **Webhooks: verify, dedupe, return fast.** Signature verified before parsing; an idempotency key (event id) recorded so replays are no-ops; 2xx returned before slow work (queue the rest). Stripe WILL redeliver. *Check: replay the same test event twice — state must change once.*
6. **Env vars fail at build, not at runtime.** A var present locally but missing in prod crashes only on the untested path, in front of a user. *Rule: one zod/valibot env schema validated at boot/build — a missing var fails the DEPLOY. Grep every `process.env.` outside that schema.*
7. **The failure path is code too.** Every try/catch, fallback, and `??` default in a diff gets one forced-failure exercise — fallbacks are where fail-open bugs and silent data loss live. *Check: for each new catch block, name the test or manual probe that exercised it. "It would catch" is not evidence.*
8. **Type-level lies.** In TS diffs, `as X`, non-null `!`, and `any` are where runtime bugs hide behind a green typecheck. *Check: grep the diff for `as ` / `!.` / `: any` — each one either justified in a comment-of-constraint or removed.*
9. **Dead exports still ship.** Removing a UI element without sweeping its derivation chain (known lesson) generalizes: unused API routes still SERVE, unused exports still bundle, orphaned flags still branch. *Check: after any removal, sweep route handlers + exports + flags that only that feature consumed.*
10. **Third-party scripts are guests, not owners.** Affiliate/analytics tags load after interaction or idle, never render-blocking; measure LCP/INP with them ON — the widget that pays pennies must not cost the ranking that pays rent.
11. **SEO parity is a sweep, not a vibe.** Per-locale canonical + hreflang reciprocity, OG tags, structured-data validity, and NO noindex leak from staging — asserted in served bytes for EVERY locale by script, pre-launch and after any head/-metadata refactor.
12. **Accessibility: the keyboard is the test.** Automated axe catches ~a third. The gate that matters: full keyboard-only pass on each key template — visible focus everywhere, icon buttons labelled, focus not trapped/lost on modals. For an accessibility-wedge brand this is brand integrity, not polish.
13. **Longest-locale layout test.** Whatever breaks a layout, German or Thai finds it first: test key templates in the longest and tallest locales, not just EN.
14. **A backup that's never been restored is a hope.** One restore drill (Neon branch → point-in-time restore → app boots against it) before launch. Same for the vault repos: clone-fresh onto a second machine once.
15. **An alert that's never fired is decoration.** Wire error reporting, then deliberately throw in preview and confirm the alert ARRIVES. Test the pipeline, not the config. Unhandled rejections in API routes vanish silently otherwise.
16. **Re-diff after rebase.** The diff you reviewed is not automatically the diff you merge — a rebase shifts the merge-base. V-Kai's verdict pins the SHA it reviewed; S-Kai re-diffs if the SHA moved.

Related: [playbook_verification_doctrine](playbook_verification_doctrine.md) · [playbook_fable_failure_modes](playbook_fable_failure_modes.md) · [playbook_multi_kai_pipeline](playbook_multi_kai_pipeline.md)

## Windows build ops (promoted 2026-08-09, first seen sabaifly voice-arc)

- **A package install run from a POSIX-emulation shell on Windows (Git Bash/MSYS) can write
  symlink targets the native runtime cannot resolve, while wrappers still exit 0.** Install from
  the native shell (PowerShell); never take a build's exit code over its final log lines; confirm
  with a served-bytes probe.
