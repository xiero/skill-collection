# Commit Message Skill

A lightweight Claude Code / Claude.ai skill that generates a high-quality commit message from staged git changes — and nothing else.

## What it does

When invoked, this skill:

1. Inspects the staged git changes (`git status`, `git diff --staged`).
2. Drafts a commit message following the Conventional Commits format with emoji prefixes.
3. Outputs the message in a code block for the user to copy.

That's it. The skill **does not run `git commit`**, does not stage or unstage files, does not push, and does not modify any source code or git state.

## When to use this vs `git-commit`

If you also have the `git-commit` skill installed, here's when to reach for which:

- **Use `commit-message`** when you just want a message and want to handle the commit yourself (e.g. you're in a different terminal, using a GUI client, or want to copy the message somewhere else).
- **Use `git-commit`** when you want the full workflow: convention detection, split-commit suggestions, approval flow, and the actual `git commit` execution.

## Installation

Copy the entire `commit-message/` directory into one of these locations:

- **Project scope:** `<repo-root>/.claude/skills/commit-message/`
  Available only inside this project. Commit it to share with the team.

- **Personal scope:** `~/.claude/skills/commit-message/`
  Available across all your projects on this machine.

The directory must contain the SKILL.md file:

```
commit-message/
└── SKILL.md
```

## Usage

The skill is configured with `disable-model-invocation: true`, so it triggers only on explicit `/commit-message` calls.

Basic usage:

```
/commit-message
```

With optional context (e.g. ticket ID, reason not visible from the diff):

```
/commit-message fixes PROJ-123
```

```
/commit-message refactor needed for upcoming v2 API
```

The optional argument is appended as extra context that the skill uses when drafting.

## Output format

```
<emoji> <type>[optional scope]: <concise description in present tense>

[optional body explaining WHY, wrapped at 72 chars]

[optional footer: Closes #123, BREAKING CHANGE: ..., etc.]
```

Supported types: `feat`, `fix`, `refactor`, `docs`, `style`, `test`, `perf`, `chore`, `build`, `ci`, `revert`. Breaking changes are marked with `!` after the type and a `BREAKING CHANGE:` footer (per Conventional Commits standard).

Subject line rules: max 50 characters, present tense imperative mood, no trailing period, lowercase description.

## Requirements

- A git repository with staged changes
- The user invoking `/commit-message` explicitly (auto-invocation is disabled)

## Permissions granted

The skill requests these tool permissions in its frontmatter:

- `Bash(git status:*)`, `Bash(git diff:*)` — for inspecting staged changes

No other tools are auto-approved. The skill cannot commit, stage, push, or modify files.

## Behavior on edge cases

- **Nothing staged:** stops immediately, suggests `git add`.
- **Very large diffs:** uses `git diff --staged --stat` first instead of dumping the full diff into context.
- **User wants a revision:** drafts a new version on request.
