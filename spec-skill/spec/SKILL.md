---
name: spec
description: Create a feature spec file and feature branch from a short idea. Use when the user wants to draft a new feature specification, plan out a feature before implementation, or scaffold a new branch with a structured spec document. Aligns the spec with the project's authoritative specification documents (CLAUDE.md, architecture.md, DAEMON_COMMUNICATION_PROTOCOL.md, system_requirements_daemon_*.csv).
argument-hint: A one-sentence to one-paragraph feature description. Include enough context for the spec to be written without guessing.
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Bash(git status:*), Bash(git branch:*), Bash(git switch:*), Bash(git rev-parse:*)
---

# Spec Skill

You are helping to create a new feature spec for this project, based on a short idea provided in the user input below.

This skill **only writes a spec file and creates a branch**. It must not modify source code, install dependencies, or perform any other side effects beyond the steps described here.

Always adhere to all rules and requirements defined in any `CLAUDE.md` file at the repo root or in subdirectories. The CLAUDE.md files reference authoritative specification documents (e.g. `architecture.md`, `DAEMON_COMMUNICATION_PROTOCOL.md`, system requirements CSV). When the feature touches a domain owned by one of those documents, you must consult the relevant document before drafting the spec.

User input: $ARGUMENTS

---

## Step 1. Validate working directory state

Run `git status --porcelain` to verify the working directory is clean.

- If there are **any** uncommitted, unstaged, or untracked changes, **abort immediately**. Print a clear message asking the user to commit or stash their changes, then **stop**. Do not continue with any further step.
- If the directory is clean, continue.

## Step 2. Validate input and parse arguments

Read `$ARGUMENTS`. If it is empty, too vague, or does not describe a concrete feature (e.g. just "make it better", "add stuff"), **stop and ask the user to provide a clearer description**. Do not guess.

Otherwise, derive three values:

1. **`feature_title`** — a short, human-readable title in **Title Case**.
   
   - Example: `Card Component For Dashboard Stats`

2. **`feature_slug`** — a git-safe slug derived from the title.
   
   - Rules:
     - lowercase
     - kebab-case
     - only `a-z`, `0-9`, `-`
     - replace spaces and punctuation with `-`
     - collapse multiple `-` into one
     - trim leading/trailing `-`
     - maximum length 40 characters
   - Example: `card-component-for-dashboard-stats`

3. **`branch_name`** — `claude/feature/<feature_slug>`
   
   - Example: `claude/feature/card-component-for-dashboard-stats`

If you cannot derive a sensible `feature_title` and `feature_slug` from the input, **stop and ask the user** to clarify. Do not invent a feature scope that was not described.

## Step 3. Identify affected layers and required reference documents

Before writing anything, decide which parts of the system this feature touches. Use the layers defined in `architecture.md` and the project's `CLAUDE.md`. Typical layers include:

- frontend app shell
- frontend core (routing, plugin host, theme, UI primitives, lifecycle)
- frontend plugin (existing or new)
- backend API / services
- backend Daemon Client Layer (anything touching the daemon protocol)
- database / persisted configuration
- shared contracts (`shared/` package)

For each affected layer, identify which authoritative documents must be consulted while drafting the spec. Apply at minimum these rules:

- If the feature touches **backend ↔ daemon communication**, the spec must reference `DAEMON_COMMUNICATION_PROTOCOL.md` and any relevant **Active** `DMREQ-*` requirements from `system_requirements_daemon_*.csv`. Ignore `Superseded` and `Obsolete` requirements.
- If the feature touches **architectural boundaries** (core vs plugin, plugin manifest, lifecycle, slot system, shell composition), the spec must reference `architecture.md`.
- If the feature is purely additive inside an existing plugin and does not touch core or backend, only `architecture.md`'s plugin boundary rules need to be referenced.

Read the relevant sections of these documents before writing the spec. Do not draft the spec from memory.

If a referenced document is not available in the working tree, **stop and ask the user to attach it** rather than guessing its contents.

## Step 4. Resolve branch name collision

Check whether `branch_name` already exists locally or remotely (`git branch --list`, `git rev-parse --verify`).

- If free, use it as-is.
- If taken, append `-01`, `-02`, ... and re-check, until you find a free name. Stop at `-999`; if everything is taken, abort and ask the user.

## Step 5. Create the feature branch

Switch to the new branch using `git switch -c <branch_name>`.

Do not push the branch. Do not stage or commit anything yet.

## Step 6. Draft the spec content

Use the spec template located in this skill's directory at `./template.md` as the structural source of truth for the spec.

- Read `./template.md` from the skill directory.
- Follow its structure exactly.
- If for any reason the template cannot be read, fall back to the default structure listed below, and inform the user in the final summary that the bundled template was missing so they can investigate.

**Default spec structure (fallback only — prefer the bundled `./template.md`):**

- **Title** — `feature_title`
- **Summary** — 2–4 sentences explaining the feature in plain language
- **Motivation** — why this feature is needed
- **Affected layers** — the layers identified in Step 3
- **Reference documents** — the authoritative documents identified in Step 3, with the specific sections or `DMREQ-*` IDs that apply
- **Functional requirements** — concrete, observable, testable behaviors
- **In scope** — what this feature includes
- **Out of scope** — what this feature explicitly does **not** include
- **Acceptance criteria** — concrete, verifiable conditions
- **Edge cases** — non-happy-path scenarios that must be handled
- **Risks and constraints** — security, performance, architectural, operational
- **Design reference (optional)** — only if a visual design exists
- **Open questions** — anything that must be clarified before implementation
- **Testing guidelines** — high-level guidance only, no implementation details

**Drafting rules:**

- Write the spec in plain language. No code examples, no implementation details (no file paths, no function signatures, no library names unless they are dictated by the architecture).
- The spec describes **what** and **why**, not **how**.
- Do not invent requirements or scope that the user did not describe. If something is unclear, list it under **Open questions** instead of assuming.
- Always fill in **Out of scope** explicitly. An empty Out of scope is a sign of an under-thought spec.
- Include the header from the template at the very top of the file:
  - ISO 8601 timestamp (e.g. `2026-04-28T14:32:00Z`)
  - Version: `v1.0.0`

Save the file as `_specs/<feature_slug>.md`. Create the `_specs/` directory if it does not exist.

## Step 7. Final output to the user

Print a short summary in this exact format, inside a fenced code block:

```
Branch:    <branch_name>
Spec file: _specs/<feature_slug>.md
Title:     <feature_title>
```

If the bundled template was missing in Step 6, add one extra line below the block:

> Note: The bundled `./template.md` could not be read. Default structure was used. Investigate the skill installation.

If any **Open questions** were added to the spec, also add:

> Note: The spec contains open questions that should be answered before implementation.

Do not print the full spec content unless the user explicitly asks for it. Do not stage, commit, or push anything.
