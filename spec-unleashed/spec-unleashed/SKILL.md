---
name: spec-unleashed
description: "Orchestrate the full New GUI spec-driven coding workflow from feature idea or existing _specs/*.md file to _plans/*.md, implementation, verification, and commit-ready summary. Use when the user wants to unleash the agent and avoid manual review after every phase, while still keeping safety gates for high-risk changes and final commits."
argument-hint: "A feature idea or existing _specs/<name>.md path. Optionally include mode: guided|fast|autopilot and commit: no_commit|prepare_commit|commit."
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, LS, TodoWrite, Bash(git status:*), Bash(git branch:*), Bash(git switch:*), Bash(git rev-parse:*), Bash(git diff:*), Bash(git log:*), Bash(git add:*), Bash(git commit:*), Bash(npm:*), Bash(node:*), Bash(mkdir:*), Bash(pwd:*), Bash(ls:*), Bash(find:*), Bash(test:*)
---

# SpecUnleashed

Spec first. Agent unleashed. Brakes still installed.

SpecUnleashed chains the project's spec-driven coding workflow:

```text
feature idea or existing spec
→ _specs/<name>.md
→ answer low-risk open questions
→ _plans/<same-name>.md
→ implementation
→ verification
→ commit-ready summary
```

This skill is an orchestrator. It must preserve the quality and safety rules of the existing `spec` and `git-commit` skills while reducing manual checkpoint friction.

---

## When to use this skill

Use this skill when the user asks to automate or run the full spec-driven workflow, for example:

- "Use SpecUnleashed for this feature."
- "Take this spec and implement it."
- "Create the spec, plan it, implement it, test it."
- "Autopilot this task from spec to commit-ready."
- "No need to stop after every step."
- "Run the spec → plan → implementation → tests flow."

Do not use this skill for:

- Tiny edits where a full spec/plan would be wasteful.
- Pure commit-message drafting only; use the `git-commit` workflow instead.
- Production deployments.
- Remote git operations.
- Secret rotation or credential handling.
- Destructive database/data operations without an explicit user decision.

---

## Core repository conventions

Default paths:

```text
_specs/<feature-slug>.md
_plans/<feature-slug>.md
```

The implementation plan must always use the exact same base filename as the spec.

Examples:

```text
_specs/unsaved-changes-guard.md
_plans/unsaved-changes-guard.md
```

If the user provides an existing spec path, preserve its basename exactly:

```text
_specs/rack-rear-view-and-cabling.md
→ _plans/rack-rear-view-and-cabling.md
```

Do not write implementation plans next to specs. Plans belong in `_plans/`.

---

## New GUI repository profile

When the repository matches the New GUI project structure, use these conventions:

```text
CLAUDE.md
architecture.md
plugin_spec.md
requirements.md
docs/DAEMON_COMMUNICATION_PROTOCOL.md
docs/DAEMON_COMMUNICATION_PROTOCOL_v1.0.4_IMPLEMENTED_MIRROR.md
docs/system_requirements_daemon_latest.csv
_specs/
_plans/
frontend/
backend/
shared/
```

Expected stack:

- Root npm workspace project.
- Frontend: Vite + React.
- Backend: Node.js + Express.
- Shared contracts in `shared/`.
- Daemon communication owned by the backend daemon client layer.
- Tests use Vitest.

Useful verification commands in this repo:

```sh
npm --workspace frontend run test
npm --workspace backend run test
npm --workspace shared run test
npm run test:ci
npm run lint
npm run build
```

For backend daemon protocol work, also consider:

```sh
npm --workspace backend run protocol:check-drift
npm --workspace backend run protocol:generate-fixtures
npm --workspace backend run protocol:export-jsonschema
```

Only run fixture/schema generation when the implementation intentionally changes protocol registrations, protocol schemas, or generated protocol artifacts.

---

## Operating modes

### `guided`

Use when the user wants checkpoints.

Stop after:

1. Spec creation/update.
2. Open question resolution.
3. Implementation plan creation.
4. Implementation.
5. Verification.
6. Commit-message proposal.

### `fast`

Default mode when the user asks for automation but does not explicitly request full autopilot.

Continue automatically through low- and medium-risk decisions.

Stop before:

- High-impact unanswered open questions.
- Destructive operations.
- Security/auth/data model changes that are not clearly specified.
- Final commit.

### `autopilot`

Use only when the user explicitly asks for full automation.

Continue automatically through safe phases, but still stop before:

- Data deletion or irreversible data migration.
- Dropping columns/tables.
- Rewriting migration history.
- Changing authentication/authorization semantics beyond the spec.
- Modifying secrets.
- Adding paid/external services.
- `git push`, force-push, rebase, reset, clean.
- Final `git commit`, unless the user already gave explicit commit approval in the same request.

Even in autopilot mode, do not guess on decisions that could cause meaningful rework, data loss, security exposure, or architectural drift.

---

## Commit modes

### `no_commit`

Default.

Do not stage. Do not commit. Return a suggested commit message.

### `prepare_commit`

Do not commit.

Return:

- Changed files.
- Recommended staging set.
- Verification result.
- Proposed commit message using the repository's commit conventions.

Do not auto-stage unless the user explicitly asked for staging.

### `commit`

Only commit after explicit approval.

A valid approval can be part of the original request, such as:

```text
Run SpecUnleashed and commit automatically if all checks pass.
```

If explicit approval is not present, stop with a commit proposal and wait.

Never push.

---

## Phase 0 — Preflight

Before changing anything:

1. Identify the repository root.
2. Read `CLAUDE.md` at the root if present.
3. Check for nested `CLAUDE.md` files in affected areas before editing those areas.
4. Run `git status --porcelain` or `git status --short`.
5. Detect whether the input is:
   - a new feature idea, or
   - an existing `_specs/<name>.md` file.
6. Detect package manager, workspaces, and relevant scripts.
7. Locate `_specs/` and `_plans/`; create them only when needed.

Working tree policy:

- For a new feature idea that requires spec creation and branch creation, the working tree must be clean before the branch/spec phase.
- For an existing spec, continue only if existing uncommitted changes are clearly related to the same task.
- If unrelated changes exist, stop and ask the user to commit/stash them.
- Do not overwrite unrelated user changes.

---

## Phase 1 — Determine feature identity

If the input is a feature idea, derive:

- `feature_title`: Title Case.
- `feature_slug`: git-safe kebab-case.
- `branch_name`: `feature/<feature_slug>`.

Slug rules:

- lowercase
- kebab-case
- only `a-z`, `0-9`, `-`
- replace spaces and punctuation with `-`
- collapse repeated `-`
- trim leading/trailing `-`
- maximum length 40 characters

If the input is an existing spec path:

- `spec_path` is the provided path.
- `feature_slug` is the spec basename without `.md`.
- `plan_path` is `_plans/<same-basename>.md`.
- Do not create a new branch unless explicitly requested.

If a feature identity cannot be derived safely, stop and ask for clarification.

---

## Phase 2 — Spec creation or update

Follow the same quality rules as the existing `spec` skill.

If creating a new spec:

1. Require a clean working tree.
2. Resolve branch name collision.
3. Create a feature branch with `git switch -c <branch_name>`.
4. Read the bundled `template.md` from this skill folder.
5. Write the spec to `_specs/<feature_slug>.md`.

If updating an existing spec:

1. Read the existing spec.
2. Preserve its filename.
3. Preserve already-answered open questions unless the user explicitly asks to change them.
4. Append or refine answers where needed.

Spec rules:

- The spec describes what and why, not how.
- Avoid implementation details, file paths, function names, and library choices unless dictated by authoritative architecture.
- Use plain language.
- Do not invent user-facing requirements beyond the user's request.
- Always fill `Out of Scope` deliberately.
- Use the template structure exactly where practical.
- Keep `Timestamp` and `Version: v1.0.0` headers.

---

## Phase 3 — Authoritative document review

Before writing or modifying a spec, plan, or code, identify affected layers and consult the relevant authoritative documents.

Typical affected layers:

- frontend app shell
- frontend core: routing / plugin host / theme / UI primitives / lifecycle
- frontend plugin: existing or new plugin name
- backend API / services
- backend Daemon Client Layer
- database / persisted configuration
- shared contracts (`shared/` package)

Rules:

- For architectural boundaries, core/plugin separation, lifecycle, manifest contracts, slot system, shell composition, or shared state: consult `architecture.md` and `CLAUDE.md`.
- For plugin manifest or plugin behavior: consult `plugin_spec.md` if present, plus `architecture.md`.
- For backend ↔ daemon communication: consult `docs/DAEMON_COMMUNICATION_PROTOCOL.md`, `docs/system_requirements_daemon_latest.csv`, and `docs/DAEMON_COMMUNICATION_PROTOCOL_v1.0.4_IMPLEMENTED_MIRROR.md`.
- Use only Active `DMREQ-*` requirements. Ignore Superseded and Obsolete requirements.
- If the daemon protocol spec and implemented mirror disagree, stop and surface the discrepancy instead of silently choosing one side.
- If a change alters behavior described in an authoritative document, update the relevant document in the same task or stop and report that the doc update is required.
- If a required document is missing, stop and ask the user to provide it.

---

## Phase 4 — Open questions handling

Before planning implementation, inspect `## Open Questions`.

For each question:

1. If the answer is already present, respect it.
2. If repository conventions clearly answer it, add an answer.
3. If the answer is low-risk and reversible, choose a conservative answer and add rationale.
4. If the answer affects security, auth, authorization, data loss, database migrations, public API behavior, daemon protocol contract, privacy, billing, or irreversible behavior, stop and ask.

Use this format when answering inside the spec:

```md
- **Question:** <question text>
  **Answer:** <decision>
  **Rationale:** <short rationale>
```

If the existing file has another established style, preserve that style. In this project it is acceptable to append `**Answer:**` directly under each open question when that matches the current spec style.

If high-impact open questions remain unanswered, do not create an implementation plan except as a partial exploratory plan clearly marked as blocked.

---

## Phase 5 — Implementation plan

Write the implementation plan to:

```text
_plans/<same-basename-as-spec>.md
```

The plan may include implementation details. Unlike the spec, the plan should describe how the change will be made.

Before writing a plan, inspect existing `_plans/*.md` files for local style and level of detail. Prefer the repository's observed plan style over generic formatting when it is clear and consistent.

If `_plans/<same-basename>.md` already exists, update it instead of creating a duplicate. Preserve valuable existing content, but refresh stale sections that conflict with the current spec.

Use the bundled `plan-template.md` as the fallback structure where practical.

Minimum plan sections:

- Timestamp and version.
- Title.
- Context.
- Source spec path.
- Open question status.
- Assumptions.
- Critical files.
- Step-by-step implementation sequence.
- Testing strategy.
- Verification commands.
- Documentation updates.
- Risks and stop conditions.
- Rollback notes.
- Commit-message draft.

Planning rules:

- Keep the plan specific enough for implementation.
- Prefer existing project patterns over new abstractions.
- Avoid speculative architecture.
- Identify exact affected files where possible.
- Call out generated files separately.
- For daemon protocol changes, include drift check and fixture/schema handling.
- For frontend work, include component and CSS boundaries.
- For backend work, include route/controller/service/middleware boundaries where applicable.
- For shared contract work, include frontend/backend consumer updates.

In `guided` mode, stop after writing the plan.

In `fast` or `autopilot` mode, continue only when the plan is bounded and no high-impact open question remains.

---

## Phase 6 — Implementation

Implement exactly the accepted or safely inferred plan.

Rules:

1. Keep changes focused.
2. Prefer existing patterns and naming.
3. Do not broaden scope opportunistically.
4. Do not add runtime dependencies unless the plan explicitly justifies them.
5. Do not modify generated artifacts unless the related generation command is also part of the plan.
6. Do not perform broad formatting-only rewrites.
7. Do not move code across architectural boundaries without explicit spec/plan support.
8. Do not let plugins import other plugins or core internals.
9. Keep daemon communication behind the daemon client/service layer.
10. Validate incoming backend data before use.
11. Use plain CSS in frontend work unless the project explicitly says otherwise.
12. Add or update tests close to the changed behavior.

If implementation reveals that the plan is wrong, update the plan with a short "Deviation" note before continuing, unless the deviation is high-risk. For high-risk deviations, stop.

---

## Phase 7 — Verification

Run the narrowest meaningful checks first, then broaden if needed.

Suggested order:

1. Targeted tests for changed behavior.
2. Workspace tests for affected package.
3. Protocol drift checks if daemon protocol artifacts changed.
4. Lint.
5. Build.
6. Full workspace CI tests if reasonable.

New GUI command guidance:

Frontend-only change:

```sh
npm --workspace frontend run test
npm run lint
npm run build
```

Backend-only change:

```sh
npm --workspace backend run test
npm run lint
```

Shared contract change:

```sh
npm --workspace shared run test
npm --workspace frontend run test
npm --workspace backend run test
npm run lint
```

Broad change:

```sh
npm run test:ci
npm run lint
npm run build
```

Daemon protocol change:

```sh
npm --workspace backend run test
npm --workspace backend run protocol:check-drift
```

If `protocol:check-drift` reports intentional drift, run the appropriate generation commands and re-run the drift check.

If a command fails:

- Diagnose whether the failure is caused by current changes.
- Fix current-change failures.
- Do not fix unrelated pre-existing failures unless needed for the task.
- Report likely pre-existing failures clearly.
- Re-run relevant checks after fixes.

If no automated verification is available, perform static inspection and report that automated verification was unavailable.

---

## Phase 8 — Self-review

Before final output or commit proposal, review:

- Spec exists in `_specs/`.
- Plan exists in `_plans/` with the same basename as the spec.
- Accepted open questions are reflected in the plan and implementation.
- No high-impact open question was silently guessed.
- Implementation matches the spec and plan.
- Diff is focused.
- Tests cover changed behavior and edge cases.
- No secrets, credentials, local machine paths, or debug leftovers are present.
- Architecture boundaries are respected.
- Authoritative docs were updated if behavior described there changed.
- Generated artifacts were regenerated only when appropriate.

If self-review finds issues, fix them before proceeding.

---

## Phase 9 — Commit preparation and optional commit

This phase must align with the `git-commit` skill behavior.

Before proposing a commit message:

1. Run `git status --short`.
2. Inspect `git diff --stat`.
3. Inspect detailed diff where useful.
4. Check recent commit style with `git log -n 5 --oneline`.
5. Check commit conventions in `CLAUDE.md`, `CONTRIBUTING.md`, `.gitmessage`, or `commitlint.config.*` if present.
6. Detect whether the diff should be split into multiple commits.

Do not auto-stage in `no_commit` or `prepare_commit` mode.

If the user requested `commit` and gave explicit approval:

1. Stage only files belonging to the current task.
2. Re-run `git diff --staged --stat`.
3. Draft the commit message.
4. Commit using the approved message.
5. Report the commit hash.

If explicit approval is missing:

- Present the proposed commit message.
- Ask the user to approve, request changes, or cancel.
- Stop.

Default commit-message format when the repo has no stronger convention:

```text
<emoji> <type>[optional scope]: <concise imperative description>

[optional body explaining why/context]

[optional footer]
```

Use the same default type vocabulary as the `git-commit` skill:

- ✨ `feat`
- 🪲 `fix`
- 🔨 `refactor`
- 📝 `docs`
- 🎨 `style`
- ✅ `test`
- ⚡ `perf`
- 🧹 `chore`
- 📦 `build`
- 👷 `ci`
- ⏪ `revert`

Never push.

---

## Stop conditions

Stop immediately before:

- Deleting user data.
- Dropping database tables or columns.
- Rewriting migration history.
- Running irreversible migrations.
- Changing auth/authz semantics outside the spec.
- Introducing paid services or external infrastructure.
- Modifying secrets.
- Running `git push`.
- Running `git reset --hard`.
- Running `git clean`.
- Running force-push or rebase.
- Deleting large parts of the repository.
- Modifying files outside the repository.
- Making production deployments.

Stop before implementation when:

- High-impact open questions remain unanswered.
- Required authoritative docs are missing.
- The plan conflicts with project architecture.
- The working tree contains unrelated changes.
- Verification is impossible and the task is high-risk.

---

## Final response format

Successful run:

```text
Done.

Branch:
- <branch or current branch>

Spec:
- _specs/<name>.md

Plan:
- _plans/<name>.md

Implemented:
- <short bullet>
- <short bullet>

Checks:
- <command> — passed/failed/not run

Commit:
- Not created / Created <hash>
- Suggested message: <message>

Notes:
- <remaining risk or follow-up, if any>
```

Stopped run:

```text
Stopped before <phase>.

Reason:
- <reason>

Completed:
- <what was completed>

Next decision needed:
- <clear question or action>
```

---

## Example invocations

```text
Use SpecUnleashed for the floorplan upload API. Fast mode, no commit.
```

```text
Run SpecUnleashed on _specs/unsaved-changes-guard.md and prepare it commit-ready.
```

```text
Autopilot this from feature idea to tested implementation, but stop before commit.
```

```text
SpecUnleashed _specs/rate-limiting-per-user-and-per-ip.md, answer low-risk open questions, create _plans/rate-limiting-per-user-and-per-ip.md, implement, and run checks.
```
