# WOF Discovery V2 Cross-Component Audit Matrix

Date: 2026-09-01

Status: **DISCOVERY V2 CROSS-COMPONENT AUDIT COMPLETE — exact P0/P1 drift identified; component code was not modified by this audit lane.**

> Concurrency note: while this audit was running, Prospective Validator landed `discovery_v2.py`, `live_validator_v2.py`, its Discovery V2 regression matrix, and switched `RUN_PROSPECTIVE_VALIDATOR.cmd` to the V2 owner path (through commit `456af2a9c7293669d63cd17f0e60140852600127`). The matrix below was re-audited against that newer state; the earlier legacy-Prospective P0 is **not** the final finding.

## Role baseline

| Component | Intended authority |
|---|---|
| `parallel/PYLAUNCH/**` | Authoritative live Worker/WASM/heap + exact World 921031 proof |
| `parallel/BROWSER_FLEET/**` | Cheap discovery indicator only; never World identity authority |
| `parallel/WOF052L_RECORDER/**` | Capture admission authority |
| `parallel/PROSPECTIVE_VALIDATOR/**` | Prospective-session admission authority |

Classification vocabulary:

- `EXPECTED_ROLE_DIFFERENCE`
- `SAFE_COMPATIBILITY_DIFFERENCE`
- `P1_DRIFT_RISK`
- `P0_INTEGRATION_BLOCKER`

## Matrix

| # | Contract point | PYLAUNCH | Browser Fleet | WOF-052L Recorder | Prospective Validator | Classification | Audit conclusion |
|---:|---|---|---|---|---|---|---|
| 1 | localhost endpoint limit | Default is loopback, but generic `--host` is unrestricted and returned `/json/version` websocket is not pinned to requested host/port. | Strong reference: assigned `127.0.0.1:<port>` only and returned websocket must stay on that same loopback port. | Fleet manifest hosts are loopback-filtered, but base `--cdp-host` is unrestricted and returned websocket is not re-pinned. | Endpoint candidates are loopback-only, but the reused core endpoint connector does not pin the returned websocket port. | `P1_DRIFT_RISK` | See `P1-ENDPOINT-CONFINEMENT`. |
| 2 | page identification / multiple-page ambiguity | Related candidates are evaluated globally; more than one exact supported page/Worker pair fails closed. | Per-page cheap indicator; multiple pages/counts are allowed because Fleet is non-authoritative. | Each page fails closed if it has >1 supported Worker, but candidates from different pages are concatenated without a global same-Worker/multi-page uniqueness check. | V2 now does the same per-page uniqueness and global concatenation; no global same-Worker/multi-page uniqueness check. | `P0_INTEGRATION_BLOCKER` | If one exact shared Worker is related to two pages, Recorder/Prospective can keep two page candidates for the same target and later accept one by iteration/order instead of rejecting the association. See `P0-CROSS-PAGE-SHARED-WORKER-AMBIGUITY`. |
| 3 | direct Worker fallback | Yes; worker/shared/service candidates + exact identity + page association. | Yes; cheap module/hint fallback. | Yes; readiness + exact identity + page association. | Yes in V2; exact identity + page association. | `SAFE_COMPATIBILITY_DIFFERENCE` | Backward compatibility exists in all four roles. |
| 4 | `Target.setAutoAttach` / related targets | Preferred page-rooted flattened auto-attach with retained events. | Yes, per page, cheap indicator. | Yes in official V2 entrypoint via `discovery_v2_sync.install(recorder)`. | Yes; V2 installs event-retaining CDP support and page-rooted flattened auto-attach. | `SAFE_COMPATIBILITY_DIFFERENCE` | The former Prospective topology gap closed during this audit. |
| 5 | iframe -> Worker | Yes, bounded recursion. | Yes, bounded recursion. | Yes, bounded recursion. | Yes, bounded recursion; regression includes iframe -> shared Worker with `blob:` URL. | `SAFE_COMPATIBILITY_DIFFERENCE` | Aligned on required topology. |
| 6 | target lifecycle / recreated Worker | Fresh discovery; reconnect clears identity cache; replacement regression exists. | Fresh per-instance recomputation; stale success is cleared. | New target id re-runs identity; page/worker/poll/disconnect paths finalize affected capture; live topology re-audited. | V2 checks direct Worker/page liveness, periodically re-audits live topology, and closes affected rooms on ambiguity/CDP failure. | `SAFE_COMPATIBILITY_DIFFERENCE` | Material lifecycle behavior is fail-safe on implemented surfaces. |
| 7 | Worker URL mismatch tolerance | Worker URL variation is allowed, but existing `blob:`, `data:`, `javascript:` targets are hard-rejected before module/exact identity. | Module-positive existing related/direct worker-like targets may be accepted regardless of URL shape; repository regression includes `blob:`. | Worker URL variation is allowed, but `blob:`, `data:`, `javascript:` are hard-rejected before exact identity. | V2 intentionally makes URL non-authoritative for real worker types; regression accepts `blob:`, hashed/no-extension, and `data:` URLs. | `P1_DRIFT_RISK` | PYLAUNCH/Recorder are now stricter than Fleet + Prospective solely by URL scheme. See `P1-URL-SCHEME-GATE`. |
| 8 | Worker -> page / endpoint association | Preferred path is page-rooted; direct fallback uses `parentId`, then legacy `openerId`, then unique page. | Endpoint/page-rooted advisory discovery; endpoint itself is strongly pinned. | Preferred path is page-rooted; direct fallback uses `parentId`, then `openerId`, then sole page. No global same-target/two-page rejection after related scans. | Preferred path is page-rooted; direct fallback uses `parentId`, then `openerId`, browserContext, then sole page. No global same-target/two-page rejection after related scans. | `P0_INTEGRATION_BLOCKER` | P0 is cross-page shared-Worker ownership. Direct `openerId` use is a separate P1. |
| 9 | multi-room / multi-tab / multi-port strict isolation | Unique authoritative pair inside endpoint; generic endpoint websocket pinning still needs hardening. | Strongest implementation: independent port/profile/process; returned websocket cannot cross room port. | Independent manager per Fleet endpoint, but same Worker observed under multiple pages is not globally rejected; websocket pinning is also weaker than Fleet. | Independent Endpoint objects and V2 page sessions, but same shared Worker observed under multiple pages is not globally rejected; websocket pinning also weaker than Fleet. | `P0_INTEGRATION_BLOCKER` | Evidence/capture authorities must not choose a page for a shared runtime by scan order. Endpoint pin issue remains P1. |
| 10 | stale / reload / disconnect cleanup | Reconnect clears runtime state/cache. | Missing endpoint affects only that instance; refresh clears stale discovery. | Affected room finalizes; other Fleet endpoints continue. | V2 affected room finalizes; other endpoints continue. | `SAFE_COMPATIBILITY_DIFFERENCE` | Aligned sufficiently; cross-page ambiguity must additionally trigger cleanup after P0 fix. |
| 11 | WASM / heap readiness | Light module/heap probe followed by exact World hash authority. | Cheap Emscripten module/heap-shape indicator only. | Requires module + heap + CPS RAM within heap before exact identity/capture admission. | V2 requires module + heap + CPS RAM within heap before exact identity/prospective admission. | `EXPECTED_ROLE_DIFFERENCE` | Fleet is intentionally cheaper; admission/proof roles are stricter. |
| 12 | exact World 921031 SHA-256 authority | Exact full CPU-logical SHA-256 `5c369ce2...8f62`; authoritative proof. | Explicitly not checked; manifest marks Worker status non-authoritative. | Exact same SHA required before capture admission. | Exact same SHA required before prospective probe admission. | `EXPECTED_ROLE_DIFFERENCE` | Correct role split; Fleet must not be promoted to identity authority. |
| 13 | wrong identity fail-closed | Rejected / waiting. | Abstains from identity. | Rejected; capture does not start. | V2 rejects before prospective probe starts. | `SAFE_COMPATIBILITY_DIFFERENCE` | Authorities fail closed; Fleet correctly abstains. |
| 14 | ambiguous Workers fail-closed | Global exact supported pair ambiguity fails closed. | Multiple advisory indicators can remain visible; expected because no evidence admission occurs. | >1 supported Worker on the same page fails closed, but one identical shared Worker related to >1 pages is not globally rejected. | Same: per-page ambiguity fails closed, cross-page same-Worker ambiguity is not globally rejected. | `P0_INTEGRATION_BLOCKER` | Required uniqueness is incomplete at the endpoint relation-graph level. |
| 15 | read-only CDP allowlist | Enumeration/attach/detach/auto-attach/Runtime enable+evaluate only; unsafe methods blocked. | Reuses PYLAUNCH read-only CDP client. | Official V2 adds only `Target.setAutoAttach` to base read-only methods. | V2 explicitly adds only `Target.setAutoAttach`; tests reject `Input.*`, `Runtime.callFunctionOn`, and page injection methods. | `SAFE_COMPATIBILITY_DIFFERENCE` | No unsafe CDP write/input method found. |
| 16 | `Input.*` / gameplay injection forbidden | Explicitly blocked. | None. | None. | V2 regression explicitly asserts no gameplay input method. | `SAFE_COMPATIBILITY_DIFFERENCE` | Aligned. |
| 17 | `ramWrites=0` | Read-only probes; reports 0. | Cheap read-only probes; manifest reports 0. | Capture probes read RAM only; reports 0. | V2 discovery/prospective bootstrap enforces 0. | `SAFE_COMPATIBILITY_DIFFERENCE` | Aligned. |
| 18 | no Worker replacement / Blob rewrite | No replacement/wrap/rewrite. | Observes existing targets only. | No replacement/wrap/rewrite. | V2 observes even existing Blob/Data worker targets read-only, but does not create/rewrite them. | `SAFE_COMPATIBILITY_DIFFERENCE` | Safety invariant aligned. Observing an existing `blob:` target is not a Blob rewrite. |
| 19 | owner-facing Simplified Chinese | Primary launcher flow is Chinese. | `RUN_WOF_FLEET.cmd` + Chinese owner wrapper. | `RUN_WOF052L_RECORDER.cmd` -> `owner_v2_zh_cn.py`. | Owner CMD now explicitly invokes `live_validator_v2.py` and prints Chinese Discovery V2/read-only status. | `SAFE_COMPATIBILITY_DIFFERENCE` | Meets primary owner-path Chinese requirement. |
| 20 | evidence authority: cheap indicator / capture / prospective / authoritative proof | Authoritative Worker/WASM/World proof. | Cheap indicator only; consumers must re-probe. | Exact-identity-gated capture evidence; defaults to discovery when consumed by Prospective adapter. | Candidate/session frozen; discovery diagnostics marked `discovery-only` and V2 write path rejects discovery diagnostics entering prospective corpus. | `EXPECTED_ROLE_DIFFERENCE` | Evidence authority boundaries are correctly distinct. |

## Blocking / drift findings

### `P0-CROSS-PAGE-SHARED-WORKER-AMBIGUITY` — `P0_INTEGRATION_BLOCKER`

**Affected authorities:** WOF-052L Recorder and Prospective Validator.

Both V2 implementations correctly reject *multiple supported Workers on one page*, but both collect per-page candidates and concatenate them without a global relation-graph uniqueness pass. A single `shared_worker` target can therefore be represented as an exact supported candidate under page A and page B. Their later attach logic prevents two live rooms with the same target id, but that is not fail-closed: it keeps whichever page is processed first and silently closes/skips the duplicate candidate.

That violates strict multi-tab evidence ownership. The correct result for `same exact Worker -> multiple pages` is **no admission for those relations**, with explicit ambiguity diagnostics.

Fresh-fix ownership:

- `WOF052L_DISCOVERY_V2_CROSS_PAGE_AMBIGUITY_FIX` -> only `parallel/WOF052L_RECORDER/**`
- `PROSPECTIVE_VALIDATOR_DISCOVERY_V2_CROSS_PAGE_AMBIGUITY_FIX` -> only `parallel/PROSPECTIVE_VALIDATOR/**`

Minimum regression vector for both lanes:

```text
page A ─┐
        ├─ same shared_worker targetId W (module/heap ready, exact World 921031)
page B ─┘
```

Expected: zero admitted candidates/rooms for W; diagnostics say cross-page Worker association ambiguous; if a live relation later becomes cross-page ambiguous, affected room is finalized before more capture/prospective evidence is accepted. One page + one Worker remains PASS. Two independent pages + two distinct Workers remains PASS.

### `P1-ENDPOINT-CONFINEMENT` — `P1_DRIFT_RISK`

Browser Fleet pins request + returned websocket to the assigned loopback port. PYLAUNCH and base Recorder allow arbitrary host CLI values and do not pin the returned websocket. Prospective hosts are loopback-only but its reused core connector likewise does not re-pin the returned websocket port.

Fresh-fix ownership:

- `PYLAUNCH_DISCOVERY_V2_ENDPOINT_GUARD` -> `parallel/PYLAUNCH/**`
- `WOF052L_DISCOVERY_V2_ENDPOINT_GUARD` -> `parallel/WOF052L_RECORDER/**`
- `PROSPECTIVE_VALIDATOR_DISCOVERY_V2_ENDPOINT_GUARD` -> `parallel/PROSPECTIVE_VALIDATOR/**`

Use Browser Fleet's same-loopback/same-port behavior as compatibility reference.

### `P1-URL-SCHEME-GATE` — `P1_DRIFT_RISK`

Fleet and the newly landed Prospective V2 correctly treat URL as diagnostic/hint for an already-existing worker-like target and let module/identity decide. PYLAUNCH and Recorder still reject `blob:/data:/javascript:` before identity can decide.

Fresh-fix ownership:

- `PYLAUNCH_DISCOVERY_V2_URL_GATE` -> `parallel/PYLAUNCH/**`
- `WOF052L_DISCOVERY_V2_URL_GATE` -> `parallel/WOF052L_RECORDER/**`

Do **not** weaken no-Worker-replacement/no-Blob-rewrite safety. Only remove URL scheme as authority over an already-existing attachable target.

### `P1-DIRECT-OPENERID-ASSOCIATION` — `P1_DRIFT_RISK`

WORKER_SURFACE established that Worker `openerId` is not parent authority. PYLAUNCH, Recorder, and the new Prospective V2 direct fallbacks still consult `openerId` after `parentId`.

Fresh-fix ownership:

- `PYLAUNCH_DISCOVERY_V2_DIRECT_ASSOCIATION` -> `parallel/PYLAUNCH/**`
- `WOF052L_DISCOVERY_V2_DIRECT_ASSOCIATION` -> `parallel/WOF052L_RECORDER/**`
- `PROSPECTIVE_VALIDATOR_DISCOVERY_V2_DIRECT_ASSOCIATION` -> `parallel/PROSPECTIVE_VALIDATOR/**`

Prefer actual page-rooted topology / `parentId` / `parentFrameId`; otherwise require a uniquely identified WOF page or fail closed.

### `P1-REGRESSION-GUARD-GAP` — `P1_DRIFT_RISK`

Prospective now has `test_discovery_v2.py`, but `parallel/REGRESSION_ORCH/manifest.json` still lists only `parallel/PROSPECTIVE_VALIDATOR/test_validator.py` for that suite. Recorder's global suite still invokes `owner_zh_cn.py --self-test` rather than the official V2 owner entrypoint `owner_v2_zh_cn.py`, although the helper unit test is separately present.

Fresh-fix ownership:

- `REGRESSION_ORCH_DISCOVERY_V2_INTEGRATION_GUARD` -> only `parallel/REGRESSION_ORCH/**`

Minimum acceptance: require/run the new Prospective Discovery V2 regression; make Recorder's official V2 entrypoint an integration surface; retain existing evidence semantics tests; include component endpoint/cross-page ambiguity regressions once their lanes land.

## Audited implementation anchors

- `parallel/WORKER_SURFACE/AUDIT.md`
- `parallel/PYLAUNCH/wof_launcher/discovery_v2.py`
- `parallel/PYLAUNCH/wof_launcher/cdp.py`
- `parallel/PYLAUNCH/wof_launcher/browser.py`
- `parallel/PYLAUNCH/launcher.py`
- `parallel/PYLAUNCH/wof_launcher/monitor.py`
- `parallel/BROWSER_FLEET/DISCOVERY_CONTRACT.md`
- `parallel/BROWSER_FLEET/fleet_discovery_v2.py`
- `parallel/BROWSER_FLEET/fleet_manager.py`
- `parallel/WOF052L_RECORDER/discovery_v2_sync.py`
- `parallel/WOF052L_RECORDER/recorder.py`
- `parallel/WOF052L_RECORDER/fleet_recorder.py`
- `parallel/PROSPECTIVE_VALIDATOR/discovery_v2.py`
- `parallel/PROSPECTIVE_VALIDATOR/live_validator_v2.py`
- `parallel/PROSPECTIVE_VALIDATOR/test_discovery_v2.py`
- `parallel/PROSPECTIVE_VALIDATOR/start_session.py`
- `parallel/PROSPECTIVE_VALIDATOR/test_validator.py`
- `parallel/REGRESSION_ORCH/manifest.json`
- `parallel/PM/CHINESE_UI_UX_REQUIREMENT.md`

No component implementation was modified by this audit.