---
name: commit-message
description: Generate a high-quality commit message from staged git changes. Use this skill when the user asks for a commit message, asks "what should my commit say", or invokes /commit-message. This skill ONLY drafts a message — it does not run git commit or modify any state.
argument-hint: Optional extra context for the commit message — e.g. a ticket ID, a reason that's not visible from the diff, or a hint about scope. Leave empty to let the skill infer everything from the staged diff.
disable-model-invocation: true
allowed-tools: Bash(git status:*), Bash(git diff:*)
---

# Commit Message Skill

You are helping the user draft a commit message for the currently staged git changes.

This skill **only inspects the staged diff and outputs a commit message**. It does not run `git commit`, does not stage or unstage files, does not push, and does not modify any source code or git state. The user takes the generated message and uses it however they like.

User input (optional extra context): $ARGUMENTS

---

## Step 1. Inspect staged changes

Run `git status --short` to confirm something is staged.

- If **nothing is staged**, stop immediately. Tell the user there is nothing to draft a message for, and suggest they `git add` their changes first.
- Otherwise, continue.

Run `git diff --staged --stat` for an overview, then `git diff --staged` (or per-file `git diff --staged -- <file>` for very large diffs) to understand the actual changes.

## Step 2. Draft the commit message

Use this format:

```
<emoji> <type>[optional scope]: <concise description in present tense>

[optional body: explain WHY this change was needed and any non-obvious context.
Wrap at 72 characters per line.]

[optional footer: Closes #123, BREAKING CHANGE: <description>, etc.]
```

### Subject line rules

- **Maximum 50 characters** (soft limit 72 — never exceed).
- **Present tense, imperative mood** ("add", "fix", "remove" — not "added", "fixes").
- **No trailing period.**
- **English** by default.
- **Lowercase description** after the colon.

### Commit types

| Emoji | Type       | When to use                                                  |
| ----- | ---------- | ------------------------------------------------------------ |
| ✨    | `feat`     | New feature or capability                                    |
| 🪲    | `fix`      | Bug fix                                                      |
| 🔨    | `refactor` | Code restructuring without behavior change                   |
| 📝    | `docs`     | Documentation only                                           |
| 🎨    | `style`    | Formatting, whitespace, linting (no logic change)            |
| ✅    | `test`     | Adding or updating tests                                     |
| ⚡    | `perf`     | Performance improvement                                      |
| 🧹    | `chore`    | Routine maintenance (deps, configs not affecting build/CI)   |
| 📦    | `build`    | Build system, bundler, package manifest changes              |
| 👷    | `ci`       | CI/CD pipeline changes                                       |
| ⏪    | `revert`   | Reverting a previous commit                                  |

### Breaking changes

Mark any type as breaking with `!` after the type/scope, **and** add a `BREAKING CHANGE:` footer:

```
💥 feat(api)!: remove deprecated v1 endpoints

BREAKING CHANGE: /api/v1/* endpoints have been removed.
```

### Body guidance

- Include a body only when the subject line doesn't fully convey the change (e.g. for non-trivial bug fixes, refactors, or context-dependent changes). Skip the body for self-evident changes like typo fixes.
- The body explains **why** and **what context matters**, not what changed line-by-line.
- Wrap at 72 characters.

### Scope guidance

Use a scope to identify the area affected (e.g. `auth`, `api`, `frontend`). If the changes span unrelated areas, omit the scope rather than listing several — and consider whether the commit should actually be split (but do not act on this; the skill only drafts messages).

## Step 3. Output the message

Output exactly two things, in this order:

1. **A 1–2 sentence summary** of what the staged changes do.
2. **The commit message** in a fenced code block, formatted exactly as it should appear.

Do not ask for approval. Do not run `git commit`. Do not suggest next steps. The user will copy the message and use it themselves.

If the user requests a revision, draft a new version following the same output format. Loop until the user is satisfied or moves on.
