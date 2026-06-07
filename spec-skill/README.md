# Spec Skill

A skill that turns a short feature idea into a structured spec file and a feature branch, aligned with the project's authoritative specification documents.

## What it does

When invoked with a short feature description, this skill:

1. Verifies the working directory is clean.
2. Parses the input into a feature title, slug, and branch name.
3. Identifies which architectural layers the feature touches and which authoritative documents must be consulted.
4. Resolves any branch-name collision and creates a new feature branch.
5. Drafts a spec file in `_specs/<feature-slug>.md` using the bundled `template.md`.
6. Prints a short summary of what was created.

The skill **only writes a spec file and creates a branch**. It does not modify source code, install dependencies, or perform any other side effects.

## Installation

Copy the entire `spec/` directory into your skills location. The directory must contain both files:

```
spec/
├── SKILL.md
└── template.md
```

## Usage

Invoke the skill explicitly with `/spec` followed by a feature description:

```
/spec add a dark mode toggle to the settings page
```

```
/spec backend endpoint to list all connected MCU devices, with pagination
```

## Project assumptions

This skill expects the project to follow conventions defined in:

- `AGENTS.md` or `CLAUDE.md` (at repo root) — project-wide rules
- `architecture.md` — architectural layers and boundaries
- `DAEMON_COMMUNICATION_PROTOCOL.md` — backend ↔ daemon contract (if applicable)
- `system_requirements_daemon_*.csv` — system-level requirements (if applicable)

If your project does not have these files, the skill still works — it will simply not consult them. For best results, make sure your project rules file lists the authoritative documents the skill should reference.

## Output

Specs are written to `_specs/<feature-slug>.md` at the repo root. The directory is created if it does not exist.

The created branch follows the convention `feature/<feature-slug>`, e.g. `feature/dark-mode-toggle`.

## Customizing the template

Edit `template.md` in this skill directory to adjust the spec structure. The skill always uses the bundled template as the structural source of truth.

## Requirements

- Git repository (the skill creates branches via `git switch -c`)
- Clean working directory at invocation time

## Permissions granted

The skill requests these tool permissions in its frontmatter:

- `Read`, `Write`, `Glob` — for reading reference docs and writing the spec file
- `Bash(git status:*)`, `Bash(git branch:*)`, `Bash(git switch:*)`, `Bash(git rev-parse:*)` — for git state checks and branch creation

No other tools are auto-approved. Anything else (e.g. running tests, modifying source) would require explicit user approval and is outside the scope of this skill.
