Timestamp: <ISO 8601 UTC, e.g. 2026-04-28T14:32:00Z>
Version: v1.0.0

# Implementation Plan: <Feature Title in Title Case>

## Context

Briefly explain the feature, the source spec, and why this implementation is needed now.

Source spec: `_specs/<same-name>.md`

## Open Question Status

State whether all open questions are answered.

- Answered: ...
- Still blocked: ...

If any high-impact question is still open, mark the plan as blocked and do not proceed to implementation.

## Assumptions

List conservative assumptions used by the plan.

- ...

## Critical Files

List the files expected to be created or modified and why.

- `path/to/file` — reason

## Implementation Sequence

Concrete ordered steps.

1. ...
2. ...
3. ...

## Data, API, or Contract Changes

Describe any data model, API, shared contract, or daemon protocol impact.

If none, write **None**.

## Testing Strategy

Describe which behavior will be covered and at what boundary.

- Unit tests: ...
- Component tests: ...
- Integration tests: ...
- E2E/smoke checks: ...

## Verification Commands

List the commands to run.

```sh
npm --workspace <workspace> run test
npm run lint
npm run build
```

## Documentation Updates

List docs that must be updated, especially authoritative docs.

If none, write **None**.

## Risks and Stop Conditions

List anything that should stop implementation or require user review.

- ...

## Rollback Notes

Explain how to revert the change safely.

## Commit Message Draft

```text
<emoji> <type>[optional scope]: <concise imperative description>
```
