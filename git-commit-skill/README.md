# Git Commit Skill

A Claude Code / Claude.ai skill that analyzes staged git changes and drafts a high-quality commit message, with explicit user approval before committing.

## What it does

When invoked, this skill:

1. Inspects the current git state (`git status`, `git diff --staged`).
2. Looks for project-specific commit conventions (CLAUDE.md, CONTRIBUTING.md, commitlint config) and follows them if present.
3. Detects when staged changes look like multiple unrelated commits and suggests splitting.
4. Drafts a commit message following either the project convention or sensible defaults (Conventional Commits + emoji prefix).
5. Presents the message and **waits for explicit user approval** before running `git commit`.

The skill **only inspects git state, drafts a message, and runs the commit after approval**. It does not stage or unstage files, push, rebase, or modify source code.

## Installation

Copy the entire `git-commit/` directory into one of these locations:

- **Project scope:** `<repo-root>/.claude/skills/git-commit/`
  Available only inside this project. Commit it to share with the team.

- **Personal scope:** `~/.claude/skills/git-commit/`
  Available across all your projects on this machine.

The directory must contain the SKILL.md file:

```
git-commit/
└── SKILL.md
```

## Usage

The skill is configured with `disable-model-invocation: true`, so it will **never** trigger automatically — only on explicit `/git-commit` calls. This is intentional: committing is a side effect that shouldn't happen unless the user clearly asks for it.

Basic usage:

```
/git-commit
```

With optional context (e.g. ticket ID, reason not visible from the diff):

```
/git-commit fixes PROJ-123
```

```
/git-commit refactor needed for upcoming v2 API
```

The optional argument is appended as extra context that the skill uses when drafting the message.

## Project conventions

The skill respects project-specific commit conventions if defined. It looks for:

- `CLAUDE.md` at repo root — checks for any commit-related rules
- `CONTRIBUTING.md` — checks for commit guidelines
- `.gitmessage`, `commitlint.config.*` — commit format configurations

If any of these define a convention, the skill follows it exactly. If none are found, it falls back to its built-in defaults (Conventional Commits with emoji prefixes).

For example, if your `CLAUDE.md` says "Commit messages must be in English", the skill will use English even if you're chatting in another language.

## Default commit format

When no project convention is found, the skill uses this format:

```
<emoji> <type>[optional scope]: <concise description in present tense>

[optional body explaining WHY, wrapped at 72 chars]

[optional footer: Closes #123, BREAKING CHANGE: ..., etc.]
```

Supported types: `feat`, `fix`, `refactor`, `docs`, `style`, `test`, `perf`, `chore`, `build`, `ci`, `revert`. Breaking changes are marked with `!` after the type and a `BREAKING CHANGE:` footer (per Conventional Commits standard).

Subject line rules: max 50 characters, present tense imperative mood, no trailing period, lowercase description.

## Approval workflow

The skill follows a strict approval flow:

1. Summarizes the staged changes.
2. Proposes a commit message in a code block.
3. Asks for approval.
4. **Waits.**
5. Commits only after the user explicitly approves with a clear "yes" / "ok" / "go ahead" / "looks good".

Ambiguous responses ("hmm", "not sure") are not treated as approval — the skill asks for clarification.

## Requirements

- A git repository with staged changes
- The user invoking `/git-commit` explicitly (auto-invocation is disabled)

## Permissions granted

The skill requests these tool permissions in its frontmatter:

- `Read`, `Glob` — for reading project convention files (CLAUDE.md, CONTRIBUTING.md, etc.)
- `Bash(git status:*)`, `Bash(git diff:*)`, `Bash(git log:*)` — for inspecting git state
- `Bash(git commit:*)` — for performing the commit after approval

No other tools are auto-approved. Anything else (push, rebase, file modification) would require explicit user approval and is outside the scope of this skill.

## Behavior on edge cases

- **Nothing staged:** stops immediately, suggests `git add`.
- **Staged + unstaged mixed:** mentions it in the summary, only commits the staged subset.
- **Unrelated changes mixed in stage:** suggests splitting, asks which subset to commit now, never auto-unstages.
- **Very large diffs:** uses `git diff --staged --stat` first instead of dumping the full diff into context.
- **Project has its own convention:** follows the project convention, not the skill defaults.
