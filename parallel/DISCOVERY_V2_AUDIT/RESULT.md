# WOF Discovery V2 Cross-Component Audit — Result

Date: 2026-09-01

## Verdict

**DISCOVERY V2 CROSS-COMPONENT AUDIT COMPLETE**

There is still **blocking drift**, but the blocker changed while this audit was in progress.

During the audit, the Prospective Validator parallel lane landed:

- `parallel/PROSPECTIVE_VALIDATOR/discovery_v2.py`
- `parallel/PROSPECTIVE_VALIDATOR/live_validator_v2.py`
- `parallel/PROSPECTIVE_VALIDATOR/test_discovery_v2.py`
- owner CMD switch to `live_validator_v2.py`

through commit `456af2a9c7293669d63cd17f0e60140852600127`.

Therefore the earlier finding “Prospective owner live path is still legacy direct gstyphoon discovery” is **closed and superseded**. This result was re-audited against the newer V2 owner path.

Final repository-side verdict:

- **1 grouped P0 integration blocker**
- **4 grouped P1 drift risks**
- no component implementation was modified by this audit lane
- intentional Fleet/capture/prospective/authoritative-proof role differences remain correctly separated
- read-only / no gameplay input / `ramWrites=0` / no Worker replacement safety invariants remain aligned

## Final P0 blocker

### P0-CROSS-PAGE-SHARED-WORKER-AMBIGUITY — `P0_INTEGRATION_BLOCKER`

**Affected admission authorities:**

- `parallel/WOF052L_RECORDER/**`
- `parallel/PROSPECTIVE_VALIDATOR/**`

Both implementations correctly fail closed when **one page has multiple exact supported Workers**. However, both perform that check inside each page scan and then concatenate successful per-page candidates.

They do not perform a final endpoint-level relation-graph uniqueness check for this case:

```text
page A ─┐
        ├── same shared_worker target W
page B ─┘

W:
- WASM/heap ready
- exact World 921031 SHA-256
- same targetId/runtime surface observed as related to both pages
```

Current outcome can be:

1. page A scan yields candidate `(A, W)`;
2. page B scan yields candidate `(B, W)`;
3. both candidates survive discovery because each page locally saw exactly one supported Worker;
4. later attach/live bookkeeping notices the same Worker target id is already live and closes/skips the second candidate;
5. whichever page was processed first wins.

That is **not fail-closed ambiguity handling**. It is scan-order selection of evidence ownership.

This is P0 because Recorder and Prospective Validator are evidence admission authorities. Multi-tab/shared-worker ambiguity must never decide capture/prospective room ownership by iteration order.

PYLAUNCH is stricter here: its related exact supported page/Worker pairs are judged globally, so more than one exact supported pair fails closed. Browser Fleet may remain advisory/non-authoritative.

### Fresh-fix ownership

#### WOF-052L

Lane: `WOF052L_DISCOVERY_V2_CROSS_PAGE_AMBIGUITY_FIX`

Write scope only:

`parallel/WOF052L_RECORDER/**`

Minimum PM task:

- after related/direct candidate collection, build an endpoint-level Worker<->page relation graph;
- group exact supported candidates by Worker target identity (`targetId` at minimum within current endpoint/session generation);
- if one Worker is associated with >1 page, admit none of those relations;
- emit explicit Chinese/diagnostic reason such as `cross-page-worker-association-ambiguous`;
- if a live capture later re-audits into that ambiguous relation, finalize the affected room before accepting further evidence;
- add regression for one shared Worker under two pages;
- preserve PASS for one page/one Worker and two pages/two distinct Workers.

#### Prospective Validator

Lane: `PROSPECTIVE_VALIDATOR_DISCOVERY_V2_CROSS_PAGE_AMBIGUITY_FIX`

Write scope only:

`parallel/PROSPECTIVE_VALIDATOR/**`

Minimum PM task is the same relation-graph/fail-closed rule, plus:

- ambiguity diagnostics remain `discovery-only`;
- no ambiguity diagnostic may enter prospective corpus;
- any live prospective room that becomes cross-page ambiguous is censored/finalized before more prospective evidence is accepted;
- candidate freeze/hash semantics remain unchanged.

No owner Browser operation is required to close this repository-side P0; use synthetic CDP topology regression first.

## P1 drift risks

### P1-ENDPOINT-CONFINEMENT — `P1_DRIFT_RISK`

Browser Fleet implements the strongest endpoint invariant and should be the compatibility reference:

- assigned endpoint is loopback;
- returned browser websocket must also be loopback;
- returned websocket port must equal the requested/assigned port;
- no silent fallover to another room/port.

Current drift:

- PYLAUNCH generic CLI accepts arbitrary `--host`;
- PYLAUNCH `/json/version` probe accepts a returned `ws*` URL without same-host/port pinning;
- Recorder generic `--cdp-host` accepts arbitrary host;
- Recorder Fleet children filter manifest hosts to loopback but do not pin the returned websocket back to that exact requested port;
- Prospective endpoint candidates are loopback-only, but V2 reuses the same base Recorder endpoint connector and therefore also lacks returned websocket same-port pinning.

This remains P1 because normal owner/Fleet defaults are loopback and Browser Fleet itself is strongly isolated, but the explicit cross-component contract is stricter than the lower-level consumers.

Fresh-fix ownership:

- `PYLAUNCH_DISCOVERY_V2_ENDPOINT_GUARD` -> only `parallel/PYLAUNCH/**`
- `WOF052L_DISCOVERY_V2_ENDPOINT_GUARD` -> only `parallel/WOF052L_RECORDER/**`
- `PROSPECTIVE_VALIDATOR_DISCOVERY_V2_ENDPOINT_GUARD` -> only `parallel/PROSPECTIVE_VALIDATOR/**`

Minimum regression: reject remote host, reject cross-port returned websocket, accept normalized loopback aliases, preserve correct Fleet endpoint.

### P1-URL-SCHEME-GATE — `P1_DRIFT_RISK`

The newly landed Prospective V2 joins Browser Fleet in using the correct Discovery V2 principle:

> for an already-existing attachable worker-like target, URL shape is diagnostic/hint only; runtime readiness + exact identity decide admission authority.

Prospective regression now explicitly accepts existing Worker URLs such as:

- `blob:...`
- hashed/no-extension URLs
- `data:...`

PYLAUNCH and Recorder still hard-reject `blob:`, `data:`, and `javascript:` targets before module/exact identity can decide.

This can produce:

```text
Fleet cheap indicator = found
Prospective V2 = exact supported
PYLAUNCH / Recorder = rejected only because URL scheme
```

That is a stitched-stack semantic drift.

Fresh-fix ownership:

- `PYLAUNCH_DISCOVERY_V2_URL_GATE` -> only `parallel/PYLAUNCH/**`
- `WOF052L_DISCOVERY_V2_URL_GATE` -> only `parallel/WOF052L_RECORDER/**`

Safety must remain unchanged: observing an already-existing Blob/Data worker read-only does **not** authorize Worker replacement, wrapping, Blob creation, ObjectURL creation, or URL rewriting.

### P1-DIRECT-OPENERID-ASSOCIATION — `P1_DRIFT_RISK`

`parallel/WORKER_SURFACE/AUDIT.md` established that Worker `openerId` is not the Worker parent model.

Current direct fallback still consults it in:

- PYLAUNCH
- WOF-052L Recorder
- newly landed Prospective V2

The preferred page-autoattach topology is structurally sound; this risk is limited to the compatibility fallback, so it remains P1.

Fresh-fix ownership:

- `PYLAUNCH_DISCOVERY_V2_DIRECT_ASSOCIATION` -> only `parallel/PYLAUNCH/**`
- `WOF052L_DISCOVERY_V2_DIRECT_ASSOCIATION` -> only `parallel/WOF052L_RECORDER/**`
- `PROSPECTIVE_VALIDATOR_DISCOVERY_V2_DIRECT_ASSOCIATION` -> only `parallel/PROSPECTIVE_VALIDATOR/**`

Minimum acceptance:

- never use Worker `openerId` as parent authority;
- prefer page-rooted topology and actual `parentId` / `parentFrameId` mapping;
- otherwise require one uniquely identified WOF page on the endpoint or fail closed;
- preserve direct Worker backward compatibility.

### P1-REGRESSION-GUARD-GAP — `P1_DRIFT_RISK`

The Prospective lane has now added `parallel/PROSPECTIVE_VALIDATOR/test_discovery_v2.py`, but the global `parallel/REGRESSION_ORCH/manifest.json` still requires/runs only `parallel/PROSPECTIVE_VALIDATOR/test_validator.py` for the Prospective suite.

Recorder global coverage also still invokes:

`owner_zh_cn.py --self-test`

while the official current owner CMD uses:

`owner_v2_zh_cn.py`

which is the integration point that installs Recorder Discovery V2 before entering the owner flow. The helper V2 unit test is separately present, but the official V2 entrypoint/import/install composition is not the suite entry command.

Fresh-fix ownership:

`REGRESSION_ORCH_DISCOVERY_V2_INTEGRATION_GUARD`

Write scope only:

`parallel/REGRESSION_ORCH/**`

Minimum acceptance:

- add Prospective `test_discovery_v2.py` as safety-critical required path/command;
- make Recorder official V2 owner entrypoint a required compile/self-test integration surface;
- preserve existing Prospective evidence semantics regression;
- after P0/P1 component lanes land, include their cross-page/endpoint tests in the global component suites.

## Differences that are expected and must not be "fixed"

### Fleet remains cheap-indicator-only

Browser Fleet should not become a second full World identity authority. Its ordinary status remains advisory and consumers must independently re-probe.

### Fleet ambiguity display is allowed

Fleet may show multiple Worker indicators/counts because it does not admit evidence. Recorder and Prospective must fail closed at the full relation-graph level.

### Readiness strictness differs by role

- Fleet: cheap module/heap-shape indicator
- PYLAUNCH: authoritative exact World proof
- Recorder: readiness + exact identity before capture
- Prospective: readiness + exact identity before prospective probe

This is `EXPECTED_ROLE_DIFFERENCE`.

### Evidence classes remain correctly separated

Prospective V2 keeps Discovery diagnostics explicitly `discovery-only`, validates frozen candidate/session state, and rejects discovery diagnostics entering prospective corpus. Existing validator regression still proves pre-freeze evidence remains discovery and manifest mutation after freeze is rejected.

## Safety conclusion

No required fix changes these invariants:

```json
{
  "readOnly": true,
  "ramWrites": 0,
  "inputInjection": false,
  "windowWorkerReplacement": false,
  "blobWorkerRewrite": false,
  "productionAutoPromotion": false
}
```

No Alpha modification, game RAM write, gameplay input injection, Worker replacement, attack automation, or production rule promotion is needed.

## PM execution order

1. Close **P0 cross-page shared-Worker ambiguity** in Recorder and Prospective with separate write scopes.
2. In parallel, close endpoint confinement, URL-gate drift, and direct-fallback association P1s in their owning components.
3. Update Regression Orchestrator only after the component tests/blobs land.
4. Re-run this cross-component audit against those new blobs.
5. Hand the aligned stack to **Unified Windows Live Proof Bundle**. This audit does not ask the owner to perform Browser operations.

## Stop condition

Satisfied with exact blockers and fresh-fix ownership:

> **DISCOVERY V2 CROSS-COMPONENT AUDIT COMPLETE**

Final blocker set:

- `P0-CROSS-PAGE-SHARED-WORKER-AMBIGUITY`
- `P1-ENDPOINT-CONFINEMENT`
- `P1-URL-SCHEME-GATE`
- `P1-DIRECT-OPENERID-ASSOCIATION`
- `P1-REGRESSION-GUARD-GAP`

No component implementation was changed in this lane.