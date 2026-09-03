# Owner Alpha V1 PM Scope Lock

Status: **OWNER-AUTHORIZED DURABLE PM SCOPE**
Updated: 2026-09-03

This PM thread is authorized to manage **Alpha V1 only**.

## Scope

The PM may inspect, review, dispatch, integrate, recover, test, package, and close only work that directly belongs to the current Alpha V1 product path and its explicitly spawned Alpha V1 subworkstreams.

Current product objective remains the usable Alpha V1 experience, including the active Alpha V3 convergence path where applicable.

## Out of scope

Do not automatically inspect, accept, continue, recover, dispatch, or close unrelated project lines, including but not limited to:

- WOF Unified Collector / Collector V12 or later;
- Training Farm;
- unrelated infrastructure, research, or data-plane work;
- other repositories or workstreams merely because they have recent commits or ACTIVE claims.

Those projects may be touched only if the Owner explicitly switches scope or explicitly asks to inspect them.

## `1` / `1 N` interpretation under this scope

Within this PM thread, Owner shorthand `1` / `1 N` applies only to the currently active **Alpha V1 parallel execution set**.

PM must:

1. inspect latest durable Git state for Alpha V1 and its current Alpha V1 subworkstreams only;
2. identify which Alpha V1 worker(s) finished or became idle;
3. review/accept/reject their durable result;
4. continue/merge the Alpha V1 critical path;
5. reassign up to N freed Alpha V1 workers only to legitimate non-conflicting Alpha V1 work.

Do not count workers from Collector, Training Farm, or any other project when interpreting `1` / `1 N` in this thread.

If Alpha V1 has fewer than N newly freed workers visible in durable Git, report only the Alpha V1 workers that can actually be identified; do not search other project lines to fill the number.

## Priority

The priority is product convergence:

`Alpha V1 -> usable owner-visible product loop`

Do not divert capacity into unrelated infrastructure work while Alpha V1 remains incomplete.
