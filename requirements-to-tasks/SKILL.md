---
name: requirements-to-tasks
description: Convert a requirements list, specification document, or feature description into a structured task breakdown with three-point time estimates (optimistic / realistic / pessimistic hours per task). Always produces BOTH a CSV and a Markdown file in a fixed schema (ID, Epic, Task, Opt (h), Real (h), Pess (h)) plus a TOTAL row. Trigger this skill whenever the user provides any kind of requirements, spec, scope document, feature list, brief, or product description AND asks for tasks, a task list, a task breakdown, work items, a backlog, estimates, hour estimates, or effort planning. Also trigger for phrasings like "bontsd taskokra", "csinálj task listát", "becsülj időt", "task breakdown", "estimate this", "plan the work for this". Use even when the user does not explicitly say "CSV" — the dual CSV+MD output is the default deliverable of this skill.
---

# Requirements → Tasks

This skill turns a requirements document (in any format — markdown, plain text, bullet list, prose spec) into a structured task breakdown with three-point hour estimates. The output is **always** two files with identical content but different formats: a CSV and a Markdown table.

## When to use

Trigger this skill whenever the user supplies a requirement-like input (spec, feature list, scope doc, user stories, PRD, brief) and asks for any of: tasks, a task list, a backlog, work breakdown, estimates, planning hours. Also trigger on Hungarian phrasings like "bontsd taskokra", "csinálj task listát ehhez", "ezt becsüld meg", "tervezzük meg".

Do NOT use this skill if the user just wants a free-form summary, a roadmap with calendar dates (use a project-planning approach instead), or a single-task estimate with no decomposition.

## Output contract (strict)

Two files, same data, both saved to `/mnt/user-data/outputs/`:

1. **`tasks.csv`** — UTF-8, comma-separated, with header row.
2. **`tasks.md`** — A markdown file with a metadata header and a single table.

### Column schema (exactly these columns, in this order)

| Column     | Type   | Notes                                                                |
| ---------- | ------ | -------------------------------------------------------------------- |
| `ID`       | int    | 1-based, sequential. Empty string for the TOTAL row.                 |
| `Epic`     | string | The category/section the task belongs to. Empty for TOTAL row.       |
| `Task`     | string | Short, action-oriented description. The TOTAL row uses "TOTAL" here. |
| `Opt (h)`  | int    | Optimistic estimate in hours.                                        |
| `Real (h)` | int    | Realistic estimate in hours.                                         |
| `Pess (h)` | int    | Pessimistic estimate in hours.                                       |

**TOTAL row**: The very last row must sum each of the three hour columns. Leave `ID` and `Epic` empty, set `Task` to `TOTAL`.

### Markdown file format

The `.md` file must look like the example below. Date is today's date in ISO 8601 (YYYY-MM-DD) form. The title comes from the project/feature name the user provided — if none, use `Task Estimates`.

```markdown
Timestamp: 2026-05-05T00:00:00Z
Version: 1.0.0

# <Project Name> Task Estimates

This file is a direct Markdown export of `tasks.csv`.
**Content is identical; only the format differs.**

| ID  | Epic           | Task                                         | Opt (h) | Real (h) | Pess (h) |
| ---:|:-------------- |:-------------------------------------------- | -------:| --------:| --------:|
| 1   | Repo/Setup     | Monorepo struktúra + alap build              | 4       | 8        | 16       |
| ... | ...            | ...                                          | ...     | ...      | ...      |
|     |                | TOTAL                                        | 670     | 1326     | 2632     |
```

Note the column alignment: `ID` right-aligned, `Epic` and `Task` left-aligned, the three hour columns right-aligned. Do NOT include any "Progress Update" or "Current Status" sections — those belong in a separate, manually-maintained progress file, not in the generated task table.

## Workflow

1. **Read the requirements input.** It may be a file (any format — md, txt, pdf, docx) or inline text. If it is a file the user uploaded, read it from `/mnt/user-data/uploads/`. For non-text files use the appropriate skill (pdf-reading, file-reading) to extract the content first.

2. **Detect epics/categories.** Look for explicit structure first:
   
   - Markdown headers (`#`, `##`, `###`)
   - Numbered sections (`1. Backend`, `2. Frontend`)
   - Bold section labels
   - Bullet groupings
   
   Use those as epics directly. If the document is unstructured prose with no clear sections, fall back to grouping tasks by functional area (Backend, Frontend, DB, Auth, Security, Testing, Ops, etc.) — but only if there is enough material; for short specs a flat single-epic list is fine.

3. **Decompose into tasks.** Each task must be:
   
   - **Atomic-ish** — a developer should be able to pick it up and finish it without further decomposition. If a task feels like 40+ realistic hours, split it.
   - **Action-oriented** — phrased as a deliverable, not a question. ("Implement JWT auth flow" not "Authentication?")
   - **Specific** — name the concrete thing being built. Avoid vague tasks like "Setup" or "Misc work".
   - **Self-contained** — readable without context from neighbouring tasks.
   
   Match the language of the input: if the requirements are in Hungarian, write the tasks in Hungarian; if English, write in English. Mixing is OK if the source mixes (the sample uses Hungarian task names with English column headers — keep that pattern).

4. **Estimate hours.** Apply the three-point estimation methodology in `references/estimation_methodology.md`. **Read that file before producing any estimate** — consistency across runs and across models depends on following the same heuristics. Round all hours to whole integers.

5. **Generate both files** using `scripts/generate.py` — this guarantees the CSV and MD stay in sync and the formatting is correct. Do not hand-write the markdown table; the script handles column padding and the TOTAL row.

6. **Save outputs to `/mnt/user-data/outputs/`** and present them to the user with `present_files`.

## Using the generation script

The script takes a JSON file describing the tasks and writes both outputs:

```bash
python /path/to/skill/scripts/generate.py \
    --input tasks.json \
    --output-dir /mnt/user-data/outputs \
    --project-name "GUI"
```

Input JSON shape:

```json
{
  "tasks": [
    {"epic": "Repo/Alap", "task": "Monorepo struktúra...", "opt": 4, "real": 8, "pess": 16},
    {"epic": "Repo/Alap", "task": "Env/config rendszer...", "opt": 4, "real": 8, "pess": 16}
  ]
}
```

The script auto-numbers IDs starting at 1, computes the TOTAL row, writes `tasks.csv` and `tasks.md` to the output directory, and prints the final paths. It does NOT need the ID or TOTAL row in the input — those are generated.

## Important constraints

- **Always produce both files**, even if the user only asks for one. The dual output is the contract of this skill — having both at hand is consistently useful (CSV for spreadsheet import, MD for review/PRs/wikis).
- **Never invent a TOTAL — let the script compute it.** Hand-summed totals are a common source of off-by-one errors.
- **Estimates must be integers.** No `4.5h` — round to 4 or 5.
- **Do not pad with filler tasks** to make the list look longer. If the requirement only justifies 8 tasks, deliver 8.
- **Do not omit obvious cross-cutting work**: testing, CI, documentation, security review, observability are real tasks and should appear when the scope warrants them. The estimation methodology reference covers what's typically missed.

## Reference files

- `references/estimation_methodology.md` — How to assign Opt/Real/Pess hours consistently. **Read before estimating.**
- `scripts/generate.py` — Generates `tasks.csv` and `tasks.md` from a tasks JSON.
