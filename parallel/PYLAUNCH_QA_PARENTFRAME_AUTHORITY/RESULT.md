# PYLAUNCH parentFrame Authority — Fresh Independent QA Result

Date: 2026-09-01  
Stage: `PYLAUNCH_PARENTFRAME_AUTHORITY_QA_V1`

## Verdict

**BLOCKED — PYLAUNCH PARENTFRAME AUTHORITY FRESH QA — P1-STALE-TARGETID-IDENTITY-CACHE-AUTHORITY**

Fresh independent QA did not accept the implementation-stage READY verdict as proof. No file under `parallel/PYLAUNCH/**` was modified by this QA lane.

QA snapshot HEAD after the fresh fixture landed and before this result was written:

`b145a6b0db4899cc3e10820a5456dd34895acbbb`

Production blobs re-read at the blocker decision:

- `parallel/PYLAUNCH/wof_launcher/discovery_v2.py` -> `68ada457ba653bba63ec0308f812f1b6b84f3bd6`
- `parallel/PYLAUNCH/wof_launcher/cdp.py` -> `def308bed2a5609be1da26505a15d621395b66aa`
- `parallel/PYLAUNCH/wof_launcher/monitor.py` -> `5ee0ce9a84988d7841799d907ebdfe2a3e68ea56`
- `parallel/PYLAUNCH/wof_launcher/browser.py` -> `e883030fe8a90333b8ed58aae5699118b2c876fe`

## First precise blocker

### P1-STALE-TARGETID-IDENTITY-CACHE-AUTHORITY

The parentFrame production fix itself is reachable, but the QA contract also requires reload/reconnect/stale target/session state to never inherit authority.

Current production code violates that requirement:

1. `_identity_on_session()` looks up `identity_cache[target_id]` and, if present, returns the cached exact World identity **before probing the current CDP session**.
2. `discover()` only removes cached entries whose `targetId` is absent from the current `Target.getTargets` result.
3. `LauncherMonitor._connect()` replaces the CDP client when the browser websocket endpoint changes, but it does **not** clear `_identity_cache`.
4. Therefore a fresh browser/CDP/runtime generation that exposes the same/reused Worker `targetId` can inherit a prior generation's cached `ok=true` exact World 921031 identity without running the current generation's identity probe.
5. The same target-id-only cache key also has no execution-context/session generation discriminator for a runtime generation change that keeps the target alive.

This can make a wrong/new runtime remain authoritative solely because its target id matches a previously accepted runtime. It is fail-open with respect to exact identity freshness, although the launcher remains read-only and performs no game write/input injection. Severity is P1 for authoritative discovery correctness.

## Fresh adversarial fixture

Added:

`parallel/PYLAUNCH_QA_PARENTFRAME_AUTHORITY/test_adversarial_generation_cache.py`

Fixture commit:

`55075ce8749dd34092f9a460d70a3aa1d224cb8c`

The fixture is intentionally not a copy of the implementation tests. It uses two distinct synthetic CDP connection generations:

- two WOF pages;
- unique child-frame ownership of `parentFrameId=frame-b` by page B;
- direct existing `blob:` Worker;
- stable/reused Worker target id `worker-stable`;
- generation 1 returns exact World 921031 identity and seeds the shared monitor-style identity cache;
- generation 2 is a distinct client/session generation with the same target id but returns a wrong SHA identity.

Required behavior: generation 2 must perform a fresh exact identity probe and reject the Worker.

Current deterministic production-path behavior: generation 2 finds `worker-stable` still present, keeps the cache entry, `_identity_on_session()` returns the old `ok=true` identity immediately, and the fresh wrong identity probe is skipped. The fixture therefore expects one identity evaluation in generation 2 and rejection; current HEAD cannot satisfy those assertions.

## QA matrix up to first blocker

1. `Page.getFrameTree` reachable through production page probe path — **PASS**. `_probe_page()` attaches to every page and calls `Page.getFrameTree` on that page session before direct association.
2. two WOF pages + direct Worker + unique `parentFrameId` selects owning page — **PASS** on current production mapping and existing production-path regression.
3. child-frame id maps to correct owning page — **PASS**; frame tree traversal is recursive.
4. duplicate/non-unique frame mapping fails closed — **PASS**; `_direct_page()` returns no page when a frame id maps to more than one page.
5. valid `parentId` remains higher authority than conflicting `parentFrameId` — **PASS**; valid `parentId` is returned before the parent-frame branch.
6. Worker `openerId` never becomes parent authority — **PASS**; direct association does not consult it.
7. multi-page direct fallback without real parent relation rejects — **PASS**; fallback requires one unique positively identified WOF page.
8. reload/reconnect/stale target/session state cannot inherit authority — **FAIL (P1)** due target-id-only exact identity cache reuse described above.

Per the start prompt, QA stops at the first precise P0/P1 blocker. Items 9-12 are not used to manufacture a second blocker after item 8 fails.

## Required fresh fix ownership

Open a new fresh PYLAUNCH implementation stage, suggested stage/lane:

`PYLAUNCH_IDENTITY_CACHE_GENERATION_FIX`

Write scope only:

`parallel/PYLAUNCH/**`

Minimum acceptance:

- exact World identity cache authority must be scoped to a proven current browser/runtime generation, not target id alone;
- changing/replacing the CDP browser connection must invalidate prior exact-identity authority;
- a runtime/execution-context generation change with a stable target id must also force fresh exact identity proof, or the implementation must conservatively stop reusing exact identity across discovery generations;
- add regression using two distinct client/session generations with the same Worker target id: generation 1 exact, generation 2 wrong -> generation 2 must re-probe and reject;
- preserve the new `Page.getFrameTree` / parentFrame authority behavior;
- preserve valid `parentId` priority, non-authoritative `openerId`, and ambiguous-frame fail-closed behavior;
- preserve exact World 921031 SHA-256 authority;
- preserve `readOnly=true`, `ramWrites=0`, `inputInjection=false`;
- preserve no Worker replacement/wrap, no Blob/ObjectURL creation/rewrite, and no gameplay input capability.

No Owner Browser run is required to reproduce or close this repository-side blocker.

## Owner action

`你现在需要操作：NO`

## Stop condition reached

> **BLOCKED — PYLAUNCH PARENTFRAME AUTHORITY FRESH QA — P1-STALE-TARGETID-IDENTITY-CACHE-AUTHORITY**
