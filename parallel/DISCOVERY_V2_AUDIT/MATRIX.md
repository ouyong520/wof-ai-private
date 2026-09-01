# WOF Discovery V2 Cross-Component Audit Matrix

Date: 2026-09-01

Status: **DISCOVERY V2 CROSS-COMPONENT AUDIT COMPLETE — exact P0/P1 drift identified; component code was not modified by this audit lane.**

## Role baseline

| Component | Intended authority |
|---|---|
| `parallel/PYLAUNCH/**` | Authoritative live Worker/WASM/heap + exact World 921031 proof |
| `parallel/BROWSER_FLEET/**` | Cheap discovery indicator only; never World identity authority |
| `parallel/WOF052L_RECORDER/**` | Capture admission authority |
| `parallel/PROSPECTIVE_VALIDATOR/**` | Prospective-session admission authority |

Classification vocabulary is fixed to the audit prompt:

- `EXPECTED_ROLE_DIFFERENCE`
- `SAFE_COMPATIBILITY_DIFFERENCE`
- `P1_DRIFT_RISK`
- `P0_INTEGRATION_BLOCKER`

## Matrix

| # | Contract point | PYLAUNCH | Browser Fleet | WOF-052L Recorder | Prospective Validator | Classification | Audit conclusion |
|---:|---|---|---|---|---|---|---|
| 1 | localhost endpoint limit | Defaults to `127.0.0.1`, but CLI `--host` is unrestricted and `/json/version` websocket host/port is not pinned back to the requested endpoint. | Strong: manager probes only `127.0.0.1:<assigned port>` and rejects websocket cross-port/cross-host boundary. | Fleet manifest hosts are filtered to loopback, but base `--cdp-host` is unrestricted and returned websocket is not pinned to requested host/port. | Endpoint candidates are loopback-only, but returned websocket is not pinned to the requested port. | `P1_DRIFT_RISK` | Endpoint confinement semantics are not uniform. See `P1-ENDPOINT-CONFINEMENT` in `RESULT.md`. |
| 2 | page identification / multiple-page ambiguity | Probes pages independently; scored WOF page selection; authoritative pair requires a unique supported page/Worker pair. | Page probe + WOF hints; multiple pages/counts are acceptable because Fleet is advisory only. | Related discovery is rooted per page; direct fallback requires a unique page relation/sole page. | Current live path does not identify or bind a Worker to a page at all. | `P0_INTEGRATION_BLOCKER` | Prospective admission can neither prove page ownership nor fail closed on page ambiguity. Part of `P0-PROSPECTIVE-LIVE-DISCOVERY`. |
| 3 | direct Worker fallback | Yes; worker/shared/service worker candidates, module + exact identity, then page association. | Yes; cheap module/hint fallback. | Yes; module/heap/RAM readiness + exact identity + page association. | Yes, but it is currently the *only* live discovery path and requires `type=worker + gstyphoon URL`. | `SAFE_COMPATIBILITY_DIFFERENCE` | Direct fallback itself is compatible; Prospective's lack of a preferred related-target path is handled by rows 4-9/P0. |
| 4 | `Target.setAutoAttach` / related targets | Preferred path: attach page, flattened auto-attach, event queue. | Yes, per page, cheap indicator. | Yes in official V2 entrypoint via `discovery_v2_sync.install(recorder)`. | No in current live validator. | `P0_INTEGRATION_BLOCKER` | Known real-Chrome surface risk is not covered by Prospective admission. |
| 5 | iframe -> Worker | Yes, bounded recursion. | Yes, bounded recursion. | Yes, bounded recursion. | No. | `P0_INTEGRATION_BLOCKER` | Prospective can miss a valid runtime visible only below a related iframe target. |
| 6 | target lifecycle / recreated Worker | Fresh discovery each monitor cycle; identity cache keyed by target id and reset on reconnect; tests cover replacement. | Fresh per-instance status recomputation; no stale success retention. | Replacement gets a new target id and a new identity preflight; live topology is periodically re-audited. | Current direct-target loop can reattach a recreated *direct gstyphoon worker*, but has no related-target lifecycle model. | `P0_INTEGRATION_BLOCKER` | Lifecycle behavior is only complete for Prospective's legacy direct surface; it is not Discovery V2 complete. |
| 7 | Worker URL mismatch tolerance | Worker-type URL variation is allowed, but existing `blob:`, `data:`, `javascript:` targets are hard-rejected before module/identity probe. | Module-positive related/direct worker-like targets are accepted even when URL shape changes; tests include an existing `blob:` related target. | Worker-type URL variation is allowed, but `blob:`, `data:`, `javascript:` are hard-rejected before exact identity. | Current live path requires `gstyphoon*.js`, so general URL mismatch is unsupported. | `P0_INTEGRATION_BLOCKER` | P0 for Prospective; additionally PYLAUNCH/Recorder vs Fleet have a P1 URL-scheme gate drift. See `P1-URL-SCHEME-GATE`. |
| 8 | Worker -> page / endpoint association | Related path is structurally rooted at a page. Direct path tries `parentId`, then legacy `openerId`, then unique page. | Per-instance endpoint is pinned; related discovery is rooted at each page. | Related path is structurally rooted at a page. Direct path tries `parentId`, then legacy `openerId`, then sole page. | No page binding in current live path; every matching direct Worker at an endpoint is independently admitted if identity passes. | `P0_INTEGRATION_BLOCKER` | Prospective is P0. Separately, use of Worker `openerId` as a direct-fallback parent surrogate in PYLAUNCH/Recorder is a P1 association drift. |
| 9 | multi-room / multi-tab / multi-port strict isolation | Fleet selection pins one endpoint, but generic CLI endpoint/websocket pinning is incomplete. Within an endpoint, unique page/Worker acceptance is fail-closed. | Strongest implementation: unique port/profile per room; websocket must remain on assigned port; one-room errors contained. | One manager/client/session set per Fleet endpoint; ambiguity per page is fail-closed, but websocket endpoint is not re-pinned to the requested port. | Separate Endpoint objects exist, but current live discovery has no page ownership or ambiguous-worker gate within the endpoint and websocket port is not re-pinned. | `P0_INTEGRATION_BLOCKER` | Prospective multi-tab isolation is not admission-safe. Endpoint pin hardening is separately P1 for PYLAUNCH/Recorder/Prospective. |
| 10 | stale / reload / disconnect cleanup | Reconnect clears runtime status and identity cache; stale/replaced Worker regression exists. | Every refresh clears per-instance discovery before re-probe; missing endpoint affects only that instance. | Disconnect/reload/poll failure finalizes affected room; replacement revalidates; other Fleet endpoints continue. | Direct-target disappearance finalizes the room; browser disconnect finalizes endpoint rooms. | `SAFE_COMPATIBILITY_DIFFERENCE` | Cleanup is materially fail-safe on implemented surfaces. Prospective's missing related surface is already captured by the P0 discovery blocker. |
| 11 | WASM / heap readiness | Light module/heap probe followed by exact ROM identity; waits when module is not ready. | Cheap Emscripten module/heap-shape indicator only; no full identity hash. | Requires module + heap + CPS RAM within heap before exact identity/capture admission. | Current direct path requires module + RAM-within-heap before exact identity. | `EXPECTED_ROLE_DIFFERENCE` | Fleet is intentionally cheaper; capture/prospective admission is stricter. PYLAUNCH exact identity remains authoritative proof. |
| 12 | exact World 921031 SHA-256 authority | Exact full CPU-logical SHA-256 `5c369ce2...8f62`; authoritative proof. | Explicitly `NOT_CHECKED`; manifest marks `workerIndicatorOnly=true` and identity non-authoritative. | Exact same SHA required before capture admission. | Exact same SHA required before prospective probe admission. | `EXPECTED_ROLE_DIFFERENCE` | Correct role split. Fleet status must never be promoted to identity evidence. |
| 13 | wrong identity fail-closed | Rejected / remains waiting. | Does not claim identity at all. | Rejected; no capture room starts. | Rejected before prospective probe starts. | `SAFE_COMPATIBILITY_DIFFERENCE` | Authorities are fail-closed; Fleet correctly abstains. |
| 14 | ambiguous Workers fail-closed | Multiple exact supported pairs/workers are rejected. | May report multiple Worker indicators as OK because it is advisory and exposes counts/non-authoritative status. | More than one supported Worker per page is rejected; live ambiguity ends affected capture. | Current live path admits every matching direct Worker independently; no uniqueness gate. | `P0_INTEGRATION_BLOCKER` | Fleet behavior is an expected role exception; Prospective ambiguity handling is a P0 admission blocker. |
| 15 | read-only CDP allowlist | `Target.getTargets`, attach/detach, `Target.setAutoAttach`, `Runtime.enable/evaluate`; unsafe methods blocked. | Reuses PYLAUNCH CDP client/read-only allowlist. | Official V2 installs only `Target.setAutoAttach` on top of base read-only methods. | Current path uses base read-only methods only; future V2 needs auto-attach added without broadening unsafe methods. | `SAFE_COMPATIBILITY_DIFFERENCE` | No unsafe CDP write/input surface found in the audited paths. |
| 16 | `Input.*` / gameplay injection forbidden | Explicit tests block `Input.dispatchKeyEvent`; `inputInjection=false`. | No input injection; manifest states false. | No `Input.*`; self-test/V2 tests enforce; `inputInjection=false`. | Live corpus safety reports `inputInjection=false`; no gameplay Input method is used. | `SAFE_COMPATIBILITY_DIFFERENCE` | Aligned. |
| 17 | `ramWrites=0` | Identity/light probes report `ramWrites=0`; read-only Runtime evaluation. | Manifest/status declares `ramWrites=0`; cheap probe only reads. | Capture safety declares `ramWrites=0`; probe reads RAM but does not write it. | Prospective probe reads RAM state and declares `ramWrites=0`; no game-memory write path found. | `SAFE_COMPATIBILITY_DIFFERENCE` | Aligned. |
| 18 | no Worker replacement / Blob rewrite | No `window.Worker` replacement/wrap and no Blob/ObjectURL worker creation/rewrite in V2 path. | No Worker replacement/rewrite; only observes existing targets. | No Worker replacement/wrap/rewrite. | No Worker replacement/wrap/rewrite. | `SAFE_COMPATIBILITY_DIFFERENCE` | Safety invariant is aligned. Note: *observing an already-existing `blob:` target read-only is not a rewrite*; the separate discovery gate drift is row 7. |
| 19 | owner-facing Simplified Chinese | Launcher CLI/tray/proof paths are Chinese by default. | Primary `RUN_WOF_FLEET.cmd` + `fleet_owner_zh_cn.py` are Chinese; internal manager strings may remain English. | Primary `RUN_WOF052L_RECORDER.cmd` invokes `owner_v2_zh_cn.py`; normal owner flow is Chinese. | Primary CMD and current live-validator owner messages are Chinese. | `SAFE_COMPATIBILITY_DIFFERENCE` | Meets project UX rule on primary owner paths; internal/machine-facing English remains an allowed compatibility exception. |
| 20 | evidence authority: cheap indicator / capture / prospective / authoritative proof | Proof/status is authoritative for Worker/WASM/exact World identity. | Contract explicitly says cheap indicator only and requires consumers to re-probe. | Exact identity is an admission gate to *capture evidence*; output is not prospective by default. | Session freeze + candidate hash separate new prospective evidence from pre-freeze discovery evidence; production auto-promotion remains forbidden. | `EXPECTED_ROLE_DIFFERENCE` | Authority boundaries are correctly distinct. Prospective's P0 is discovery/admission topology, not evidence labeling. |

## Cross-component blockers referenced by the matrix

### `P0-PROSPECTIVE-LIVE-DISCOVERY` — `P0_INTEGRATION_BLOCKER`

Current `parallel/PROSPECTIVE_VALIDATOR/live_validator.py` still discovers only browser-level targets satisfying `type == "worker"` plus `gstyphoon*.js` URL, then admits each matching Worker independently after module/identity checks. It does not use page-rooted auto-attach, iframe-related topology, URL-shape-tolerant Worker discovery, or unique page/Worker association.

**Ownership:** existing fresh lane defined by `parallel/PM/PROSPECTIVE_VALIDATOR_DISCOVERY_V2_SYNC_START_PROMPT.md`; write scope `parallel/PROSPECTIVE_VALIDATOR/**` only.

### `P1-ENDPOINT-CONFINEMENT` — `P1_DRIFT_RISK`

Browser Fleet enforces the strongest invariant: request and websocket must remain on the same assigned loopback port. PYLAUNCH and base Recorder accept arbitrary CLI hosts and do not validate the `/json/version` websocket host/port against the requested endpoint. Prospective constructs loopback hosts but also does not re-pin the returned websocket port.

**Ownership:** separate fresh fixes in `parallel/PYLAUNCH/**` and `parallel/WOF052L_RECORDER/**`; fold the Prospective side into `P0-PROSPECTIVE-LIVE-DISCOVERY`. Use Browser Fleet's `endpoint_matches_runtime()` semantics as the compatibility reference.

### `P1-URL-SCHEME-GATE` — `P1_DRIFT_RISK`

Browser Fleet proves that an already-existing related Worker with a nontraditional URL (including the repository regression's `blob:` case) can be observed and read-only module-probed. PYLAUNCH and Recorder reject `blob:/data:/javascript:` *before* module/identity authority can decide. This can yield `Fleet Worker OK` while authoritative/capture consumers remain WAIT solely because of URL scheme.

**Ownership:** fresh fixes in `parallel/PYLAUNCH/**` and `parallel/WOF052L_RECORDER/**`; the Prospective V2 lane must follow the same rule. Keep the safety prohibition on *creating/replacing/rewriting* Blob workers; only remove URL scheme as an admission authority for an already-existing attachable target.

### `P1-DIRECT-OPENERID-ASSOCIATION` — `P1_DRIFT_RISK`

Worker-surface audit established that `openerId` is not the Worker parent model; `parentId` / `parentFrameId` and page/frame topology are the correct association primitives. Current PYLAUNCH and Recorder direct fallbacks still try `openerId` after `parentId`.

**Ownership:** fresh direct-fallback association hardening in `parallel/PYLAUNCH/**` and `parallel/WOF052L_RECORDER/**`. Do not change the preferred page-autoattach path.

### `P1-REGRESSION-GUARD-GAP` — `P1_DRIFT_RISK`

`parallel/REGRESSION_ORCH/manifest.json` runs Recorder's `owner_zh_cn.py --self-test` even though the official V2 CMD invokes `owner_v2_zh_cn.py`; the V2 helper has a separate unit test, but the official integration entrypoint is not the suite command. The Prospective suite currently runs only `test_validator.py`, so the live Discovery V2 P0 cannot make the global orchestrator red.

**Ownership:** fresh `parallel/REGRESSION_ORCH/**` guard lane after component fixes land: exercise/compile the official Recorder V2 entrypoint and add Prospective Discovery V2 regression as a safety-critical required path/command.

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
- `parallel/PROSPECTIVE_VALIDATOR/live_validator.py`
- `parallel/PROSPECTIVE_VALIDATOR/start_session.py`
- `parallel/PROSPECTIVE_VALIDATOR/test_validator.py`
- `parallel/REGRESSION_ORCH/manifest.json`
- `parallel/PM/CHINESE_UI_UX_REQUIREMENT.md`

No component implementation was modified by this audit.