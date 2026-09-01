# WOF COVERAGE Refresh — PM Bootstrap

Updated: 2026-09-01

## Role

You are continuing the existing `parallel/COVERAGE/**` lane. This is not a new research lane.

Your goal is to refresh coverage accounting from the current GitHub state so PM can make Beta/v1 breadth decisions without asking the owner for unnecessary collection.

## Start by reading

Main repo:
- `WOF_AI_HANDOFF.md`
- `PARALLEL_RESEARCH.md`
- `COLLECTOR_ROUTING.md`
- `parallel/COVERAGE/**`
- `parallel/SWEEPATLAS/**`
- `parallel/SEQMINER/**`
- `parallel/BASECAP/**`
- `parallel/EFIELD/**`
- `parallel/GEO/**`
- `parallel/RAWMINE/**`
- `parallel/PM/PROJECT_DASHBOARD.md`
- `parallel/PM/ACTIVE_PRIORITIES.md`

Bridge, read-only:
- `docs/COLLECTOR_V1_CONTRACT.md`
- `tasks/queue/**`
- `status/by_task/**`
- `results/by_task/**`
- `captures/**`

## Mandatory normalization

Project-wide canonical enemy type notation is:

`T<decimal> (0xHH)`

Do not compare old lane `Txx` labels until their numeric byte identity is normalized.

Important examples:
- Browser T18 = raw byte `0x12`.
- Browser T23 = raw byte `0x17`.
- Browser T16 = raw byte `0x10`.
- Browser T20 = raw byte `0x14`.

Old COVERAGE hex-style labels such as `T17` can therefore refer to Browser decimal T23. Preserve raw-byte identity explicitly.

## Work to do

1. Refresh COVERAGE against current SWEEPATLAS and SEQMINER outputs; the old snapshot that says they are absent is stale.
2. Normalize all enemy type identifiers to decimal + hex form.
3. Materialize as many useful per-type cross-tabs as existing retained data safely supports:
   - sample density;
   - lifecycle episodes;
   - target P1/P2/P3 incidence;
   - target changes / retarget evidence;
   - structural attack/executor episode counts;
   - ordered-sequence evidence availability;
   - provenance/data-quality status.
4. Keep stage/scene/wave/boss labels as UNKNOWN unless an authoritative source exists. Do not infer labels from task names.
5. Distinguish:
   - physical data gap;
   - analysis/materialization gap;
   - label/semantic gap;
   - Browser validation gap.
6. Recompute `COVERAGE_MATRIX.md/json`, `FRONTIER.md`, `GAPS.md`, and `MINIMAL_RECAP_PLAN.md` as appropriate.
7. Determine whether any new physical WinKawaks recap is genuinely necessary.

## Stop / operator policy

Default answer is NO new capture.

Do not create Collector tasks and do not ask the owner to replay the game unless the refreshed matrix proves a specific residual physical gap that:
- matters to Product/Beta/v1;
- cannot be answered from retained raw;
- has a minimal scene/condition target;
- has a bounded expected collection cost.

If no such gap exists, explicitly close with `human recap required: NO`.

## Scope

Write only under `parallel/COVERAGE/**`.
Do not modify MAINLINE, SEQMINER, SWEEPATLAS, EFIELD, GEO, RAWMINE, BASECAP, bridge task/result/capture data, or PM files.

## Deliverable

Continue until the current retained corpus is fully re-accounted with normalized type notation and one of these is true:

A. COVERAGE is refreshed and no human recap is justified; or
B. exactly one minimal, evidence-backed recap request is identified for PM/owner review.

Do not stop merely to report intermediate progress.