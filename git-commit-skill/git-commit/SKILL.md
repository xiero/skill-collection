---
name: git-commit
description: Analyze staged git changes and generate a well-crafted commit message. Use this skill when the user explicitly asks for help writing a commit message, asks "what should my commit say", asks Claude to draft a commit, or invokes /git-commit. Do not auto-trigger on unrelated git activity.
argument-hint: Optional extra context for the commit message — e.g. a ticket ID, a reason that's not visible from the diff, or a hint about scope. Leave empty to let the skill infer everything from the staged diff.
disable-model-invocation: true
allowed-tools: Read, Glob, Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git commit:*)
---

# Git Commit Skill

You are helping the user craft a high-quality git commit message for the currently staged changes, and (after explicit approval) running the commit.

This skill **only inspects git state, drafts a commit message, and — after the user confirms — runs `git commit`**. It must not modify source code, stage or unstage files, push, rebase, or perform any other git operation.

User input (optional extra context): $ARGUMENTS

---

## Step 1. Gather context

Run `git status --short` to see what is staged and unstaged.

- If **nothing is staged**, stop immediately. Tell the user that there is nothing to commit and suggest `git add <files>` first. Do not proceed.
- If there are **unstaged changes alongside staged ones**, mention this in your summary so the user is aware that the commit will only cover the staged subset. Do not auto-stage anything.

Then inspect the staged changes:

- Run `git diff --staged --stat` first to get a high-level overview (file list + line counts).
- Run `git diff --staged` only if the stat output is small enough to be useful in full, or if you need to look at specific files in detail. For very large diffs, prefer per-file inspection (`git diff --staged -- <file>`) over dumping the entire diff.

Optionally consult `git log -n 5 --oneline` to see the recent commit message style in this repo, in case the project follows a non-default convention.

## Step 2. Consult project conventions

Look for project-specific commit conventions before applying the defaults below.

- Check the repo root for `CLAUDE.md`. If present, look for any commit-related rules (commit format, language, ticket reference requirements, scope rules, etc.).
- Also check for a `CONTRIBUTING.md`, `.gitmessage`, `commitlint.config.*`, or similar config files at the repo root.

**Precedence rules:**

- If the project defines its own commit convention (in CLAUDE.md, CONTRIBUTING.md, or a commitlint config), **follow that convention exactly** and ignore the defaults in this skill.
- If the project's CLAUDE.md says commit messages must be in a specific language (e.g. English), use that language even if the user is communicating in a different one.
- If no project convention is found, use the defaults defined below.

## Step 3. Detect "this should be multiple commits"

Inspect the staged diff. If it contains **clearly unrelated changes** (e.g. a feature change in one module + an unrelated bugfix in another + a docs typo fix), do not draft a single mega-commit.

Instead:

- Briefly explain why the changes look unrelated.
- Suggest a logical split (which files / hunks belong together).
- Recommend the user run `git reset HEAD <file>` (or `git restore --staged <file>`) to unstage the parts they want to commit separately.
- Ask which subset they want to commit **now**, and draft a message only for that subset.

Do not run any unstaging commands yourself.

## Step 4. Draft the commit message

If the project has its own convention (Step 2), follow it. Otherwise, use the defaults below.

### Default format

```
<emoji> <type>[optional scope]: <concise description in present tense>

[optional body: explain WHY this change was needed and any non-obvious context.
Wrap at 72 characters per line.]

[optional footer: Closes #123, Refs #456, BREAKING CHANGE: <description>, etc.]
```

### Subject line rules

- **Maximum 50 characters** for the subject (soft limit 72 — never exceed).
- **Present tense, imperative mood** ("add", "fix", "remove" — not "added", "fixes", "removing").
- **No trailing period.**
- **English by default**, unless the project's CLAUDE.md says otherwise.
- **Lowercase description** after the colon (the type and scope are already structured; the description reads as a sentence fragment).

### Default commit types

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

A breaking change is **not** a separate type. Mark any type as breaking with a `!` after the type/scope, **and** add a `BREAKING CHANGE:` footer explaining the impact:

```
💥 feat(api)!: remove deprecated v1 endpoints

Clients still calling /api/v1/* will receive 404 responses.
Migration guide: docs/migration-v2.md.

BREAKING CHANGE: /api/v1/* endpoints have been removed.
```

The 💥 emoji is optional and stacks with the type (e.g. `💥 feat(api)!: ...`).

### Body guidance

- Include a body for any commit that is **not self-evidently described by the subject line**. For example, a one-line typo fix may not need a body, but a refactor or a fix for a non-obvious bug usually does.
- The body explains **why** and **what context matters**, not what changed line-by-line. The diff already shows what changed.
- Wrap at 72 characters per line. Use blank lines to separate paragraphs.

### Scope guidance

- Use the scope to identify the area of the codebase affected (e.g. `auth`, `api`, `frontend`, `daemon-client`, a plugin name, etc.).
- For multi-area changes that genuinely belong in one commit (rare — usually means it should be split per Step 3), omit the scope rather than listing multiple.

### Examples

Good:

- ✨ feat(auth): add OAuth2 login flow
- 🪲 fix(api): prevent crash when config file is missing
- 🔨 refactor(daemon-client): extract envelope construction into helper
- 📝 docs: clarify daemon reconnect behavior in architecture.md
- 💥 feat(api)!: remove deprecated v1 endpoints

Avoid:

- "fixed stuff" / "various changes" / "updates" (no information)
- "added oauth login" (past tense)
- "Add OAuth login." (trailing period, capital letter, no type)
- "feat: add stuff and fix things and update docs" (multiple unrelated changes — should be split)

## Step 5. Present and wait for approval

Output your work in this order:

1. **A 2–3 sentence summary** of what the staged changes do. Focus on intent, not file lists.
2. **The proposed commit message** in a fenced code block, exactly as it would appear when committed (including blank lines between subject, body, and footer).
3. **A confirmation prompt**: ask the user to approve the message as-is, request changes, or cancel.

Then **stop and wait** for the user's response. Do not run `git commit` yet.

## Step 6. Commit on approval

Only after the user **explicitly approves** the message:

- Run `git commit -m "<subject>" -m "<body>" -m "<footer>"` — using separate `-m` flags for each paragraph so newlines are preserved correctly. Alternatively, write the message to a temporary file and use `git commit -F <file>` for messages with complex formatting.
- After the commit succeeds, print the resulting commit hash and subject line as confirmation.

If the user requests changes, revise the message and present it again. Loop until they either approve or cancel.

If the user cancels, do nothing further. Do not commit.

**Never commit without explicit approval.** "Looks good", "ok", "yes", "go ahead", "commit it" are valid approvals. Anything ambiguous ("hmm", "not sure", "maybe") is **not** approval — ask for clarification.
