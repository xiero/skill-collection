---
name: azure-task-manager
description: Manage Azure DevOps Tasks through the configured `azure-tasks` MCP server. Use when the user asks to find, inspect, create, edit, assign, estimate, change the state of, complete, or log time against Azure DevOps Tasks. Also use for bulk Task updates and questions about valid Task states, activities, or iterations. Do not use direct Azure CLI or shell commands for these operations.
---

# Azure Task Manager

Use only the tools exposed by the `azure-tasks` MCP server. Do not substitute `az`, shell commands, the application CLI, or direct Azure DevOps API calls. If the server or a required tool is unavailable, report that clearly and stop.

## Read Tasks

1. Call `get_project_context` before choosing or interpreting Azure-specific states, activities, or iterations.
2. Call `find_tasks` for compact task lists and to resolve task IDs. Prefer its defaults when the user asks for their active tasks.
3. Call `get_task` only when a full description or the complete managed field set is needed.
4. Never invent task IDs, state names, activities, iterations, or identities.

## Write Tasks

Treat an unambiguous user request to mutate tasks as authorization to prepare and commit that mutation. Rely on the MCP host's write approval instead of asking for redundant confirmation. Ask a concise question only when the target or requested result is ambiguous.

1. Resolve target IDs and required project values with the read tools.
2. Create exactly one preview with the matching tool:
   - `plan_create_task` for a new task;
   - `plan_update_tasks` for field, assignment, estimate, iteration, activity, or state changes;
   - `plan_log_time` for Completed Work and Remaining Work changes.
3. For creation, generate one stable `requestKey` if the user did not supply one. Keep and reuse that exact value for retries of the same request.
4. Inspect the returned validity, item count, targets, and field diffs. Do not commit an invalid plan or a plan that affects tasks beyond the user's request.
5. Briefly state the intended changes, then call `commit_plan` with the returned `planId`.
6. Report created or updated task IDs and the resulting important fields concisely.

Use `discard_plan` when the user cancels a pending change or when a valid plan must intentionally be abandoned. Plans expire after 10 minutes. If an intended plan expires, create a fresh preview, inspect it again, and commit only the new `planId`.

## Failure Handling

- Surface MCP validation errors without attempting an alternate write path.
- If a selector matches unexpected tasks, do not commit; clarify the intended target.
- On an uncertain commit result, retry the same `commit_plan` call. For task creation, retain the original `requestKey` so retries remain idempotent.
- Keep responses compact: use structured MCP results and avoid reproducing full descriptions unless requested.
