---
name: azure-task-manager
description: Manage Azure DevOps Tasks through the configured `azure-tasks` MCP server. Use for direct Task lookup, exact import-backed repository reference resolution such as BHC-024, inspection, creation, editing, assignment, estimation, state changes, completion, time logging, bulk updates, and questions about valid states, activities, or iterations. Also use as the Azure read/write protocol for lifecycle workflows such as `azure-task-autoclose`. For automatic post-implementation closure tied to an explicit or exactly resolved Task identity, use `azure-task-autoclose` together with this protocol. Never substitute Azure CLI, shell commands, or direct API calls.
---

# Azure Task Manager

Use only tools exposed by the `azure-tasks` MCP server for Azure operations. Let the MCP host start the configured stdio server; never launch it manually in an interactive terminal. If the server or a required tool is unavailable, report that the current agent session needs the MCP server enabled or restarted, then stop the Azure operation without using a fallback write path.

This skill owns Azure Task lookup and mutation safety. Let `azure-task-autoclose` decide whether completed code work is eligible for automatic closure.

## Read Tasks

1. Call `get_project_context` before choosing or interpreting Azure-specific states, activities, or iterations.
2. Use `resolve_task_reference` for an import-backed repository identifier such as `BHC-024`. Accept it as an exact Task identity only when the result is `resolved` with one match. This lookup intentionally includes completed and differently assigned Tasks.
3. On `not_found`, request an Azure work-item ID or URL. On `ambiguous`, report the conflicting match IDs and make no write until the conflict is resolved.
4. Use `find_tasks` for compact lists and ordinary search. Prefer its defaults for the current user's active Tasks.
5. Use `get_task` for an exact or resolved ID when a full description or complete managed field set is needed, and immediately before a sensitive single-Task update.
6. Treat `completedStates` from project context as authoritative. Never hardcode or invent Task IDs, states, activities, iterations, identities, or field values.
7. Never substitute fuzzy title matching for an explicit or import-backed reference. If supplied identities conflict, ask which exact Task is authoritative.

## Write Tasks

Treat an unambiguous mutation request, including an eligible automatic close, as authorization to preview and commit that mutation. Rely on the MCP host's write approval instead of asking for redundant confirmation. Ask one concise question only when the target or result is ambiguous.

1. Resolve target IDs and required project values with read tools.
2. Prefer `selector: { ids: [...] }` whenever exact IDs are known. Use a query selector only for an intentionally requested bulk operation.
3. Create one preview with the matching tool:
   - `plan_create_task` for a new Task;
   - `plan_update_tasks` for field, assignment, estimate, iteration, activity, or state changes;
   - `plan_log_time` for adding Completed Work and adjusting Remaining Work.
4. For creation, generate one stable `requestKey` if none was supplied. Reuse it for every retry of the same logical request. If the preview returns `existingTask`, report it and do not call `commit_plan`.
5. Inspect `valid`, `planId`, `itemCount`, every target ID, and every field diff. Do not commit an invalid, expired, no-op, over-broad, or otherwise unexpected plan.
6. Briefly state the exact intended changes, then call `commit_plan` with the returned `planId` without requesting another confirmation.
7. Check every returned item status. Report created or updated Task IDs, important resulting fields, and any per-item failures concisely.

Use `discard_plan` when the user cancels a pending change or a valid plan must intentionally be abandoned. Plans expire after 10 minutes. When a plan expires, create and inspect a fresh preview and commit only its new `planId`.

## Complete Tasks

1. Read `completedStates` with `get_project_context`. Use a user-specified valid completed state; otherwise use the sole completed state. If multiple completed states remain plausible and no repository or conversation convention resolves them, ask instead of guessing.
2. Read the exact Task. If its state is already in `completedStates`, report the no-op and do not create a plan.
3. Preview the state change for the exact ID. Completing a Task books Remaining Work into Completed Work and sets Remaining Work to zero by default, so inspect those generated diffs as part of the requested completion.
4. Do not invent time values or disable `bookRemainingTime` merely to bypass validation. Change the default only when the user explicitly requests it or an established workflow rule requires it.

## Handle Failures

- Surface MCP validation errors without attempting Azure CLI, application CLI, shell, or direct API fallbacks.
- If a selector matches unexpected Tasks or a preview contains unexpected diffs, do not commit it.
- If a commit result is uncertain, retry the same `commit_plan` call; completed commits are idempotent.
- Keep responses compact and avoid reproducing full private descriptions unless requested.
