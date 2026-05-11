# Three-Point Estimation Methodology

This file defines a deterministic-as-possible methodology for assigning **Optimistic / Realistic / Pessimistic** hour estimates to software development tasks. Following this methodology consistently is the difference between estimates that vary wildly between runs and estimates that a team can actually plan against.

## Core principle

Each task gets a **size class** based on its scope and risk profile. The size class maps to a fixed `(Opt, Real, Pess)` tuple. You pick the size class; the hours follow.

This avoids the "pick a number that feels right" trap, which is the main reason different runs produce wildly different totals.

## Step 1 — Assign a size class

Walk through the size classes top-to-bottom and pick the **first** one that fits. When in doubt between two adjacent classes, pick the larger one (developers consistently underestimate).

| Class   | Opt | Real | Pess | When to use                                                                                              |
| ------- | ---:| ----:| ----:| -------------------------------------------------------------------------------------------------------- |
| **XS**  | 2   | 4    | 8    | Trivial config, single-file change, one small dependency added, simple text/copy update                  |
| **S**   | 4   | 8    | 16   | Single well-defined component or endpoint with no external integration; standard CRUD; baseline tooling  |
| **M**   | 6   | 12   | 24   | A feature touching 2–3 modules; one external integration; needs basic tests; moderate UI work            |
| **L**   | 8   | 16   | 32   | A non-trivial subsystem; touches FE+BE; needs schema work; needs meaningful test coverage                |
| **XL**  | 12  | 24   | 48   | Complex feature with multiple moving parts, validation, error states, edge cases; cross-cutting concerns |
| **XXL** | 16  | 32   | 64   | Foundational architecture decision, schema design, complex stateful flow, large refactor                 |

If a task feels bigger than XXL, **split it**. Tasks over 32 realistic hours are bad planning units — they hide complexity and are impossible to estimate accurately. Decompose into 2+ smaller tasks.

## Step 2 — Apply size-class modifiers

After picking the base class, check these modifiers and **bump up by one class per modifier that applies** (cap at XXL, then split):

- **Auth / security / GDPR / audit involvement**: +1 class. Security work always takes longer than it looks.
- **Stateful protocol / async / WebSocket / event-driven**: +1 class. Race conditions and reconnect logic are a tar pit.
- **Cross-cutting (touches >3 modules)**: +1 class.
- **Migration / backwards compat / data conversion**: +1 class.
- **First-of-its-kind in this codebase** (new framework, new pattern, no prior art): +1 class.
- **Performance-critical / load-tested**: +1 class.

Modifiers stack additively. A task that involves *both* auth *and* WebSocket starts at M but ends up at XL.

## Step 3 — Sanity-check the spread

The pessimistic estimate should be roughly **2× the realistic** estimate, and realistic should be roughly **2× the optimistic**. The size-class table above already enforces this — if you find yourself wanting to manually set an estimate that breaks this ratio, you're either picking the wrong class or the task needs splitting.

The 2x spread reflects software estimation reality: things go wrong in ways that double the time, not in ways that add 10%.

## What gets a task of its own

When decomposing a requirement into tasks, **explicitly include** these categories of work — they are the most commonly forgotten and the most commonly underestimated:

- **Tooling baseline**: lint, formatter, pre-commit hooks, CI pipeline, build configuration. Each is its own S/M task.
- **Schema & migrations**: every database change is its own task. Don't fold migrations into "implement feature X".
- **Auth & permissions**: separate task per concern (login flow, permission model, route guards, session invalidation, password reset).
- **Validation & sanitization**: input validation as a cross-cutting task, not bundled into endpoints.
- **Security headers / CSRF / rate limiting**: each is its own S/M task.
- **Observability**: logging setup, traceId propagation, metrics — each its own task.
- **Tests**: a baseline test setup task PER layer (FE unit, BE unit, E2E). Don't assume tests come "for free" with each feature.
- **Docker / deployment / runtime hardening**: separate from feature work.
- **Performance pass**: separate task for FE bundle/lazy-route work and another for BE indexes/timing.
- **Documentation** that the requirement explicitly calls for: README, API docs, runbooks. Skip if not requested.

## What does NOT get its own task

- Code review time (assume it's bundled into the realistic estimate)
- Rubber-ducking and "thinking" time (already in the optimistic→realistic spread)
- Meetings about the task (out of scope of dev estimates)
- "Nice-to-have" polish that the spec doesn't call for — don't pad

## Worked examples

These calibrate the methodology against real tasks. Refer back when uncertain.

| Task                                                       | Class + modifiers                          | Hours        |
| ---------------------------------------------------------- | ------------------------------------------ | ------------ |
| Add `ESLint + Prettier + scripts + git hooks`              | S (baseline tooling)                       | 4 / 8 / 16   |
| Add `CI pipeline (lint + unit + build)`                    | M (touches multiple jobs)                  | 6 / 12 / 24  |
| `App Shell layout (header/sidebar/slot)`                   | L (FE structural)                          | 8 / 16 / 32  |
| `Plugin registry + manifest validation`                    | XL (first-of-its-kind +1)                  | 12 / 20 / 36 |
| `Theme engine (light/dark + custom hooks)`                 | L                                          | 8 / 16 / 32  |
| `Auth: login/logout/me (JWT cookie) + session policy`      | XL (auth +1 from L)                        | 12 / 24 / 44 |
| `DB schema v1 (users/roles/perms/.../audit)`               | XXL (foundational, schema)                 | 16 / 32 / 64 |
| `Users CRUD + roles + validation`                          | XL (auth-adjacent +1 from L)               | 12 / 24 / 48 |
| `WebSocket server + project channel + auth cookie`         | XL (stateful protocol +1, auth +1, from M) | 12 / 24 / 48 |
| `CSP header + helmet config`                               | M (security work)                          | 6 / 12 / 24  |
| `Rate limiting (per user + per IP)`                        | M                                          | 6 / 12 / 24  |
| `Audit log middleware + critical events`                   | XL                                         | 12 / 24 / 48 |
| `FE unit test baseline (registry, contexts, plugin state)` | XXL (baseline + many subsystems)           | 16 / 32 / 64 |
| `Docker compose (frontend+backend+db+redis)`               | XL                                         | 12 / 24 / 48 |
| `Daemon protocol package (Zod schemas + fixtures)`         | XL (first-of-its-kind, complex)            | 12 / 24 / 48 |

Notice the consistency: same class → same hours, every time. That is the goal.

## Final checklist before returning estimates

- [ ] Every task has integer hours (no decimals)
- [ ] Every task fits one of the size-class tuples (or a documented stack of modifier bumps)
- [ ] No task exceeds XXL — bigger ones are split
- [ ] Pess ≈ 2× Real; Real ≈ 2× Opt for each row
- [ ] The commonly-forgotten categories above were considered and included where relevant
- [ ] TOTAL row is generated by the script, not hand-summed
