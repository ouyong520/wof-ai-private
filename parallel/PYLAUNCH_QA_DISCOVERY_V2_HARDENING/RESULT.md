# PYLAUNCH Discovery V2 Hardening — Fresh Independent QA Result

Date: 2026-09-01  
Stage: `PYLAUNCH_DISCOVERY_V2_HARDENING_QA_V1`

## Verdict

**BLOCKED — PYLAUNCH DISCOVERY V2 HARDENING QA — P1-DIRECT-PARENTFRAMEID-AUTHORITY-NOT-REACHABLE**

This is a fresh independent QA result. The implementation-stage PASS was not accepted as proof. No `parallel/PYLAUNCH/**` implementation file was modified by this QA lane.

## Exact blocker

The hardening contract requires direct Worker association to preserve real `parentId` and a uniquely mapped `parentFrameId`, while never using Worker `openerId` as parent authority.

Current `parallel/PYLAUNCH/wof_launcher/discovery_v2.py` does correctly:

- honor `parentId`;
- ignore `openerId` as Worker parent authority;
- fall back only to one unique WOF page;
- fail closed when two WOF pages remain ambiguous.

However, its `parentFrameId` branch can only compare the Worker frame id against:

- `page["frameId"]`; or
- `page["wofPageProbe"]["frameId"]`.

Neither source is populated by the current production discovery path:

- normal page `TargetInfo` does not provide the page's own root frame id as `frameId` to this code path;
- current `PAGE_PROBE` returns `href`, `title`, `gameSurface`, `alphaBootstrap`, and `readOnly`, but no CDP frame id;
- current CDP allowlist has no `Page.getFrameTree` and discovery performs no equivalent execution-context `auxData.frameId` mapping.

Therefore a real direct Worker topology can be unambiguously attributable by `parentFrameId`, yet PYLAUNCH cannot consume that authority. With two valid WOF pages it falls through to the unique-WOF-page rule and rejects the Worker as page-ambiguous.

That is a P1 compatibility/association defect relative to the explicit hardening QA requirement. It is fail-closed, so it is not a safety bypass, but it still blocks PASS.

## Independent adversarial fixture

Added:

`parallel/PYLAUNCH_QA_DISCOVERY_V2_HARDENING/test_adversarial_parent_frame.py`

The synthetic endpoint contains:

- two positively identified WOF pages;
- one direct existing `blob:` Worker;
- exact World 921031 identity;
- `Worker.parentFrameId = frame-b`;
- a synthetic `Page.getFrameTree` surface that maps `frame-b` uniquely to page B.

The contract expectation is page B association. Current production discovery never asks for the available frame map, so the topology remains direct-worker-page ambiguous.

Fixture commit: `2d1d9db04204abae93ad827a4c2dc43f69578b23`.

## QA matrix

1. remote HTTP/CDP host fail closed — **PASS**
2. returned websocket remote/cross-port fail closed — **PASS**
3. localhost / 127.0.0.1 / ::1 loopback normalization — **PASS**
4. existing blob/data/hashed/extensionless Worker URL not rejected by shape — **PASS**
5. wrong World 921031 identity fails closed independent of URL shape — **PASS**
6. `openerId` cannot become direct Worker parent authority — **PASS**
7. real `parentId` / uniquely mapped `parentFrameId` valid — **FAIL (P1)**; `parentId` works, production `parentFrameId` mapping is not reachable
8. direct fallback only with one unique WOF page; two WOF pages reject — **PASS**
9. cross-page exact pair ambiguity rejects — **PASS**
10. vanished/recreated Worker target ids do not inherit stale identity cache — **PASS**
11. disconnect/reconnect clears old runtime authority — **PASS**
12. exact World 921031 SHA-256 authority preserved — **PASS**
13. `readOnly=true / ramWrites=0 / inputInjection=false` — **PASS**
14. no Worker replacement/wrap / Blob creation / URL rewrite — **PASS**
15. CDP allowlist contains no gameplay `Input.*` or `Runtime.callFunctionOn` — **PASS**

Machine-readable result:

`parallel/PYLAUNCH_QA_DISCOVERY_V2_HARDENING/RESULT.json`

## Required fresh fix ownership

Open a new fresh PYLAUNCH fix stage with write scope only under `parallel/PYLAUNCH/**`.

Minimum fix:

- surface a read-only frame-to-page identity map, preferably `Page.getFrameTree` and/or equivalent Runtime execution-context `auxData.frameId` mapping;
- add only the required read-only CDP introspection method(s) to the allowlist;
- resolve `parentFrameId` through that map before the unique-WOF-page fallback;
- keep `openerId` non-authoritative;
- keep multiple mappings fail closed;
- keep exact World 921031 SHA authority;
- keep `readOnly=true`, `ramWrites=0`, `inputInjection=false`;
- keep no Worker replacement, no Blob/ObjectURL creation, no URL rewrite.

No Owner Browser run is needed to close this repository-side blocker.

## External observations — recorded only, not fixed here

### Owner OneClick package manifest

**Still stale at this QA snapshot.**

Current manifest pins:

- `parallel/PYLAUNCH/wof_launcher/browser.py` -> `92838cef8584d16c865de7ab2ffd7fc5ff6921d2`
- `parallel/PYLAUNCH/wof_launcher/discovery_v2.py` -> `cee0bdef0fe461ab0cb003e6ae198db8c19a5ec2`

Current default-branch blobs are:

- `browser.py` -> `e883030fe8a90333b8ed58aae5699118b2c876fe`
- `discovery_v2.py` -> `5e3d8f27bcd044366bc402811f638c5569240b9b`

This remains package/integration ownership and is not the PYLAUNCH core blocker.

### Windows CP1252 / Chinese stdout

**Risk still present in the direct Python CLI path.**

`parallel/PYLAUNCH/launcher.py` still prints Chinese `ensure_ascii=False` JSON via ordinary `print()` without forcing/reconfiguring stdout to UTF-8. The owner CMD sets `chcp 65001`, which protects that console path, but redirected or CP1252 Python stdout can still hit the previously observed encoding failure.

This is recorded only. It is not used to manufacture the PYLAUNCH core QA blocker above.

## Owner action

`你现在需要操作：NO`

## Stop condition

> **BLOCKED — PYLAUNCH DISCOVERY V2 HARDENING QA — P1-DIRECT-PARENTFRAMEID-AUTHORITY-NOT-REACHABLE**
