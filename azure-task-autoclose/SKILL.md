---
name: azure-task-autoclose
description: Automatically close a verified Azure DevOps Task through the configured `azure-tasks` MCP server after completing its associated code work. Use when an implementation or fix is tied to an explicit Azure Task ID, Azure work-item URL, a `task/123` or `azdo/123` branch pattern, or when the user expects Azure state to follow successful implementation. Do not use when Task identity is ambiguous or for analysis-, planning-, review-, or diagnosis-only work.
---

# Azure Task Auto-close

Apply the `azure-task-manager` read/write protocol for every Azure operation. Use this skill to decide when code work is complete enough to trigger that protocol automatically.

## Retain Exact Task Identity

At the start of implementation, retain the exact Task ID from one of these sources:

- the user request or an Azure DevOps work-item URL;
- established conversation context;
- a branch segment beginning with `task/<id>` or `azdo/<id>`.

Treat all other numbers as ambiguous. Never infer an Azure Task from an issue number, version, port, fuzzy title match, or repository name. If authoritative sources provide conflicting IDs, resolve the conflict before any Azure write. If no exact ID is available, finish the code work without closing a Task and report that Azure synchronization still needs the ID.

## Decide Whether to Close

Close only when all conditions hold:

1. The requested implementation or fix for that Task is genuinely complete.
2. Relevant repository tests, type checks, linters, builds, or the strongest available verification have passed.
3. No known relevant failure or requested work remains.
4. The user has not asked to keep the Task open.

Do not close after partial work or when the request was only for analysis, planning, review, diagnosis, or status reporting. Unrelated pre-existing working-tree changes do not block closure when the requested work itself is isolated and verified.

## Close the Task

1. Call `get_project_context` and inspect `completedStates`. Use an explicitly requested valid completed state, an already established repository convention, or the sole completed state. If several completed states remain plausible, ask rather than guess.
2. Call `get_task` with the exact retained ID. If its current state is already in `completedStates`, report that no Azure write was needed.
3. Call `plan_update_tasks` with `selector: { ids: [<id>] }` and a change containing the selected completed state. Leave `bookRemainingTime` at its default unless the user or an established workflow explicitly says otherwise.
4. Inspect plan validity, expiration, item count, exact target ID, and every diff. Expect default completion to add Remaining Work to Completed Work and set Remaining Work to zero; treat these as part of the completion and report them when material.
5. Commit only a valid one-Task plan that matches the verified implementation. Do not invent time values or weaken validation to force closure.
6. Check the committed item status and report the Task ID, resulting state, material time-booking changes, and code verification outcome.

Do not ask for redundant confirmation before `commit_plan`; successful implementation tied to the exact Task is the authorization for automatic closure, while the MCP host remains the write-approval boundary.

For multiple explicit Task IDs, evaluate and close each Task independently. Never close one merely because another Task's implementation passed.

## Handle Unavailable MCP

If `azure-tasks` or a required tool is unavailable, leave Azure unchanged. Do not start the stdio server manually and do not fall back to Azure CLI, shell commands, the application CLI, or direct APIs. Report code completion and Azure synchronization as separate statuses, and state that the agent host must enable the MCP server or start a fresh session after configuration changes.
