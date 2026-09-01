# PYLAUNCH Identity Cache Generation Fix — Result

Date: 2026-09-01
Stage: `PYLAUNCH_IDENTITY_CACHE_GENERATION_FIX_V1`

## Verdict

**PYLAUNCH IDENTITY CACHE GENERATION FIX READY — READY FOR FRESH QA**

The repository-side P1 identity-cache generation authority defect is closed within the allowed `parallel/PYLAUNCH/**` scope. No Owner Browser/WOF run is required for this stage.

## Closed P1 defect

Fresh independent QA demonstrated that a browser/runtime generation could reuse a prior accepted exact World identity when the replacement Worker reused the same `targetId`. The previous cache key was only `targetId`, and stale cleanup only removed IDs absent from the current `Target.getTargets` set.

### 1. Discovery-generation-scoped exact identity authority

`parallel/PYLAUNCH/wof_launcher/discovery_v2.py`

- every `discover()` call now invalidates the caller-provided identity cache before any target is admitted;
- exact World identity may therefore be reused only inside the current discovery generation, where auto-attach and direct-worker paths may encounter the same Worker;
- a stable/reused `targetId` cannot carry accepted authority into a later discovery generation;
- generation 2 must execute a fresh exact identity probe and a wrong World identity fails closed.

This intentionally chooses the conservative option required by the stage prompt: **no cross-discovery-generation identity authority reuse**.

### 2. Browser-level CDP replacement invalidates authority

`parallel/PYLAUNCH/wof_launcher/monitor.py`

`LauncherMonitor._connect()` now clears:

- the prior browser-level client/endpoint references;
- `_last_worker_id`;
- `_last_identity`;
- `_identity_cache`;

before the replacement browser-level CDP client becomes observable. Explicit `reconnect()` and connection-error handling already had equivalent invalidation and remain intact.

### 3. Fresh QA adversarial case absorbed into implementation regression

Added:

`parallel/PYLAUNCH/tests/test_identity_cache_generation.py`

It covers both required authority boundaries:

1. generation 1 exact World 921031 -> accepted and cached; generation 2 wrong World, same `worker-stable` target ID -> exact identity probe executes again, authority is rejected, Worker is not admitted;
2. replacing the browser-level CDP connection clears prior cached/last identity authority before the new connection is installed.

## Regression

Targeted deterministic regression matrix executed after the fix:

- `test_identity_cache_generation.py`: **2/2 PASS**
- `test_parentframe_authority.py`: **5/5 PASS**
- `test_discovery_v2.py`: **16/16 PASS**
- `test_endpoint_hardening.py`: **5/5 PASS**
- total: **28/28 PASS**, **0 failures**, **0 errors**

Preserved behaviors include:

- `Page.getFrameTree` / `parentFrameId` production association;
- child-frame-to-owning-page mapping;
- `parentId` remains higher authority than `parentFrameId`;
- Worker `openerId` remains non-authoritative;
- duplicate/ambiguous parent-frame or multi-page associations fail closed;
- page-rooted auto-attach and nested iframe/Worker discovery remain supported;
- blob/data/hashed existing Worker URLs remain diagnostic only, never identity authority;
- exact World mismatch fails closed;
- endpoint confinement remains loopback + exact-port constrained;
- read-only CDP allowlist continues to reject gameplay input and arbitrary function calls.

## Final blobs

Production:

- `parallel/PYLAUNCH/wof_launcher/discovery_v2.py` -> `ec9d27bfe26557a11187a23853893b898a3366d1`
- `parallel/PYLAUNCH/wof_launcher/monitor.py` -> `4430f7e927265cd3366fd70ce560c375aa878993`
- `parallel/PYLAUNCH/wof_launcher/cdp.py` -> `def308bed2a5609be1da26505a15d621395b66aa`
- `parallel/PYLAUNCH/wof_launcher/browser.py` -> `e883030fe8a90333b8ed58aae5699118b2c876fe`
- `parallel/PYLAUNCH/wof_launcher/probe.py` -> `789a6849b826b35542b22d56a4d2ca3628d285a1`

Regression:

- `parallel/PYLAUNCH/tests/test_identity_cache_generation.py` -> `ed7a7af17060ae234687b6ef546ac50a0c0dcfef`
- `parallel/PYLAUNCH/tests/test_parentframe_authority.py` -> `1ed144a003bc54246ff12f75db5f5f886028029a`
- `parallel/PYLAUNCH/tests/test_discovery_v2.py` -> `8262c3310b97bab9fd30d7fe2cd8fb3aabd7ade9`
- `parallel/PYLAUNCH/tests/test_endpoint_hardening.py` -> `242a76e8c9cddf28ba60bc3e5aee93060bd6d1ae`

Exact World authority remains the existing World 921031 SHA-256:

`5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`

## Safety invariants

Unchanged and regression-covered:

```json
{
  "readOnly": true,
  "ramWrites": 0,
  "inputInjection": false,
  "workerReplacement": false,
  "urlRewrite": false
}
```

No Worker replacement, Blob/ObjectURL rewrite, gameplay input injection, or RAM write was introduced.

## External Owner One-Click observation — outside this stage's write ownership

The push-triggered `Owner One-Click Package` run for commit `46a045809ee25584a759190204ea8dd9b03314e2` completed with:

- `windows-oneclick`: **SUCCESS**;
- `integrity`: **FAILURE** only in `test_current_pylaunch_runtime_cannot_outgrow_package`, because `parallel/OWNER_ONECLICK/package_manifest.json` pins older PYLAUNCH blobs for `browser.py`, `cdp.py`, `discovery_v2.py`, and `monitor.py`.

That manifest is under `parallel/OWNER_ONECLICK/**`, which this stage explicitly forbids modifying. The same class of package-manifest drift was already documented by the prior PYLAUNCH hardening stage. It is an integration ownership handoff, not a blocker to the repository-side identity-cache authority fix.

## Owner action

**NO** — no Owner Browser/WOF run is required.

## Stop condition

> **PYLAUNCH IDENTITY CACHE GENERATION FIX READY — READY FOR FRESH QA**
