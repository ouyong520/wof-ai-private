# PYLAUNCH parentFrame Authority Fix — Result

Date: 2026-09-01  
Stage: `PYLAUNCH_PARENTFRAME_AUTHORITY_FIX_V1`

## Verdict

**PYLAUNCH PARENTFRAME AUTHORITY FIX READY — READY FOR FRESH QA RETEST**

The P1 from `parallel/PYLAUNCH_QA_DISCOVERY_V2_HARDENING/RESULT.md` is closed repository-side. No Owner Browser run is required for this fix stage.

## Production fix

### Read-only frame introspection

`parallel/PYLAUNCH/wof_launcher/cdp.py`

- Added exactly one CDP introspection method: `Page.getFrameTree`.
- `Input.*` remains outside the allowlist.
- `Runtime.callFunctionOn` remains outside the allowlist.
- Existing `Runtime.evaluate` usage remains probe-only/read-only under the existing policy.

### Production discovery reachability

`parallel/PYLAUNCH/wof_launcher/discovery_v2.py`

- `_probe_page()` now attaches to each page target and executes the existing page probe plus read-only `Page.getFrameTree` on the same page session.
- `_frame_ids_from_tree()` recursively records root and child frame ids into `cdpFrameIds`.
- `_direct_page()` resolves Worker `parentFrameId` against those production-populated frame ids before the unique-WOF-page fallback.
- `parentId` remains the highest direct authority.
- `openerId` remains intentionally non-authoritative for Worker ownership.
- if one `parentFrameId` maps to more than one page, association fails closed.
- diagnostics expose observed `frameIds` and any frame-introspection error for auditability.

This is not an unused helper: the main `discover()` production path calls `_probe_page()` for every page before direct Worker association, so `parentFrameId` authority is now reachable by production discovery.

## Safety invariants preserved

- exact World 921031 SHA-256 authority unchanged;
- `readOnly=true`;
- `ramWrites=0`;
- `inputInjection=false`;
- no Worker replacement/wrapping;
- no Blob/ObjectURL creation;
- no URL rewrite;
- no gameplay `Input.*` capability;
- no arbitrary `Runtime.callFunctionOn` capability.

## Regression coverage

Added production-path regression:

`parallel/PYLAUNCH/tests/test_parentframe_authority.py`

Coverage:

1. two valid WOF pages + direct Worker + unique `parentFrameId` selects the correct page and proves `Page.getFrameTree` was actually called;
2. child-frame id maps to its owning page;
3. duplicated/non-unique frame mapping fails closed;
4. conflicting `parentFrameId` cannot override valid `parentId`;
5. allowlist contains `Page.getFrameTree` while still excluding gameplay input and arbitrary function calls.

## Executed repository-side validation

Synthetic/offline validation was run against the current production discovery logic, without Owner Browser involvement:

- Fresh QA adversarial parentFrame fixture topology: **PASS 1/1**.
  - two WOF pages;
  - direct existing `blob:` Worker;
  - exact World 921031 identity;
  - `parentFrameId=frame-b`;
  - page B uniquely owns `frame-b` through `Page.getFrameTree`;
  - result: page B selected and `Page.getFrameTree` observed on the production path.
- new parentFrame authority regression: **PASS 5/5**.
- existing Discovery V2 compatibility/safety regression set: **PASS 16/16** after matching the production nested auto-attach path.
- syntax/compile checks for the reconstructed current production modules/tests: **PASS**.

No real Browser/game runtime was requested because the blocker is fully repository-side and the Owner Intervention Gate forbids unnecessary Owner debugging.

## Final blobs at result time

- `parallel/PYLAUNCH/wof_launcher/cdp.py` blob: `def308bed2a5609be1da26505a15d621395b66aa`
- `parallel/PYLAUNCH/wof_launcher/discovery_v2.py` blob: `68ada457ba653bba63ec0308f812f1b6b84f3bd6`
- `parallel/PYLAUNCH/tests/test_parentframe_authority.py` blob: `1ed144a003bc54246ff12f75db5f5f886028029a`

Implementation commit sequence:

- `da1943aaf0272b47f2ea17c1cd58c0516e589cff` — add read-only `Page.getFrameTree` allowlist entry;
- `3162bf8470fe247275218b2c1ccb24de381cfe79` — final clean CDP source after immediate annotation correction;
- `233b9bf1b9e7a93d56190b3949b27dd3d79938a1` — production frame-tree mapping and `parentFrameId` consumption;
- `25ecd909905284f3c876abe010c0c0e47d777bf2` — production-path parentFrame regression.

## Owner action

`你现在需要操作：NO`

## Stop condition

> **PYLAUNCH PARENTFRAME AUTHORITY FIX READY — READY FOR FRESH QA RETEST**
