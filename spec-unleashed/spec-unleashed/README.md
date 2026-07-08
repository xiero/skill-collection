# SpecUnleashed

SpecUnleashed is an orchestrator skill for the New GUI spec-driven workflow.

It chains:

```text
feature idea or existing _specs/*.md
→ _specs/<name>.md
→ _plans/<same-name>.md
→ implementation
→ verification
→ commit-ready summary
```

## Files

- `SKILL.md` — the skill definition.
- `template.md` — bundled spec template, aligned with the existing `spec` skill.
- `plan-template.md` — implementation plan template for `_plans/<same-name>.md`.

## Suggested install location

```text
skills/
  spec/
    SKILL.md
    template.md
  git-commit/
    SKILL.md
  spec-unleashed/
    SKILL.md
    template.md
    plan-template.md
```

## Key conventions

- Specs go to `_specs/`.
- Plans go to `_plans/`.
- Plan filename must match the spec filename exactly.
- Final commit still requires explicit approval unless the user gave approval in the same request.
