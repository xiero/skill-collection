Timestamp: <ISO 8601 UTC, e.g. 2026-04-28T14:32:00Z>
Version: v1.0.0

# Spec: <Feature Title in Title Case>

> Replace every `<...>` placeholder. Delete any optional section that does not apply to this feature, and explain why in the Summary if its absence is non-obvious.

## Summary

A 2–4 sentence plain-language description of the feature. Explain **what** it does and **who** it is for. Avoid implementation details.

## Motivation

Why is this feature needed? What problem does it solve, what user pain does it address, or what capability does it unlock? Keep it short and concrete.

## Affected Layers

List every layer of the system this feature touches. Use the layer names from `architecture.md`. Examples:

- frontend app shell
- frontend core (routing / plugin host / theme / UI primitives / lifecycle)
- frontend plugin: `<plugin-name>` (existing or new)
- backend API / services
- backend Daemon Client Layer
- database / persisted configuration
- shared contracts (`shared/` package)

Mark each entry as **new**, **modified**, or **read-only**.

## Reference Documents

List every authoritative document that was consulted while writing this spec, and the specific sections or requirement IDs that apply. Examples:

- `architecture.md` — sections: ...
- `DAEMON_COMMUNICATION_PROTOCOL.md` — sections: ...
- `system_requirements_daemon_*.csv` — `DMREQ-XXX`, `DMREQ-YYY` (Active only — Superseded and Obsolete must not be referenced)
- `CLAUDE.md` — relevant rules: ...

If no authoritative document applies, write **None** and briefly justify why.

## Functional Requirements

Bulleted list of concrete, observable behaviors the feature must provide. Each item should be testable. No implementation details.

- ...

## In Scope

Bulleted list of what this feature explicitly **includes**. Be concrete.

- ...

## Out of Scope

Bulleted list of what this feature explicitly does **not** include, especially things a reader might assume are included. An empty Out of Scope is a sign of an under-thought spec — fill this in deliberately.

- ...

## Acceptance Criteria

Concrete, verifiable conditions that determine when this feature is considered complete. Prefer "Given / When / Then" style or numbered statements.

- ...

## Edge Cases

List the non-happy-path scenarios the feature must handle. Examples to consider depending on the feature:

- empty / missing / malformed input
- concurrent operations
- daemon connection lost mid-operation
- backend restart while operation is in flight
- permission denied / unauthenticated user
- stale or conflicting persisted state
- large payloads / batch limits
- ...

## Risks and Constraints

Anything that could make this feature dangerous, fragile, or hard to maintain. Cover at minimum:

- **Security:** attack surfaces, input validation, authorization boundaries, secrets handling
- **Performance:** latency targets, throughput expectations, resource constraints
- **Architectural:** boundary risks (e.g. core vs plugin leakage, daemon protocol misuse, shared state pollution)
- **Operational:** failure modes, recovery behavior, observability

If a risk is mitigated by an existing mechanism, name the mechanism.

## Design Reference (optional)

Only fill this in if the feature has a visual design reference (e.g. Figma, mockup, screenshot). Delete this section otherwise.

- Source: ...
- Component / frame name: ...
- Key visual constraints: ...

## Open Questions

List anything that must be clarified before implementation can start. If nothing is open, write **None**.

- ...

## Testing Guidelines

High-level guidance only — not implementation details. Cover:

- which behaviors must be unit-tested (Vitest, per the project's testing rules)
- which boundaries must be tested with mocks (e.g. mocked daemon client, mocked DB, mocked WebSocket transport)
- which integration paths must be exercised end-to-end
- any specific edge cases from the Edge Cases section that require dedicated test coverage

Do not specify file paths, test framework configuration, or test code structure here — those belong in implementation, not in the spec.
