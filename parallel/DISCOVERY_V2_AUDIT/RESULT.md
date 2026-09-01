# WOF Discovery V2 Cross-Component Audit — Result

Date: 2026-09-01

## Verdict

**DISCOVERY V2 CROSS-COMPONENT AUDIT COMPLETE**

There is **blocking drift**. The four components are not yet safe to treat as one fully aligned Discovery V2 stack.

Repository-side audit verdict:

- **1 grouped P0 integration blocker**
- **4 grouped P1 drift risks**
- role differences around Fleet cheap indication vs exact identity/capture/prospective evidence are intentional and correctly documented
- read-only / no gameplay input / `ramWrites=0` / no Worker replacement safety invariants remain aligned in the audited paths
- this audit lane modified only `parallel/DISCOVERY_V2_AUDIT/**`

The blocking issue is not the prospective statistics/evidence framework. Candidate freeze, candidate hash, pre-freeze discovery isolation, prospective labeling, and no-production-auto-promotion boundaries are already present and regression-covered. The P0 is specifically the **Prospective live Worker admission discovery topology**.

## P0 blocker

### P0-PROSPECTIVE-LIVE-DISCOVERY — `P0_INTEGRATION_BLOCKER`

`parallel/PROSPECTIVE_VALIDATOR/live_validator.py` is still on the legacy direct discovery assumption:

```text
Target.getTargets
-> type == worker
-> URL matches gstyphoon*.js
-> light module/RAM probe
-> exact World 921031 SHA-256
-> start prospective probe
```

It does **not** yet implement the Discovery V2 topology already present in PYLAUNCH / Browser Fleet / WOF-052L Recorder:

```text
endpoint
-> page
-> Target.setAutoAttach(flatten=true)
-> related iframe / Worker tree
-> read-only module/heap readiness
-> unique page/Worker association
-> exact World 921031 gate (for an authority component)
```

Consequences:

1. a valid WOF runtime visible only as a page-related Worker can be missed;
2. iframe -> Worker surfaces can be missed;
3. valid Worker URL shape changes can be missed;
4. multiple matching direct Workers are not rejected as an ambiguous admission set — each can be attached independently;
5. page ownership is not established before prospective evidence collection;
6. multi-tab isolation inside one CDP endpoint is therefore not equivalent to Recorder/PYLAUNCH V2 semantics.

This is P0 because Prospective Validator is an **admission authority**. A false negative prevents a real prospective session; an ambiguous false positive can admit evidence without a unique page/Worker ownership proof.

### Exact fresh-fix ownership

Use the already-created lane:

`parallel/PM/PROSPECTIVE_VALIDATOR_DISCOVERY_V2_SYNC_START_PROMPT.md`

Ownership:

- write only `parallel/PROSPECTIVE_VALIDATOR/**`
- do not modify PYLAUNCH, Browser Fleet, Recorder, or Alpha

Minimum PM acceptance for that lane:

- direct Worker backward compatibility;
- page-session `Target.setAutoAttach`;
- related-target-only discovery;
- page -> iframe -> Worker;
- worker/shared_worker/service_worker candidate surfaces;
- URL-shape variation without a gstyphoon URL authority gate;
- WASM/heap readiness;
- exact World 921031 SHA-256 before prospective probe start;
- missing/wrong/ambiguous Worker fail-closed;
- unique page/Worker association;
- reload/recreated Worker cleanup;
- two/ten-room endpoint isolation;
- candidate freeze/hash and discovery-vs-prospective evidence boundary unchanged;
- read-only CDP allowlist only;
- Simplified Chinese owner flow.

The same lane should also add a same-requested-endpoint websocket host/port pin before connecting.

## P1 drift risks

### P1-ENDPOINT-CONFINEMENT — `P1_DRIFT_RISK`

The endpoint contract is not implemented uniformly.

**Browser Fleet reference behavior** is the strongest and should be the compatibility target:

- request only the assigned loopback endpoint;
- require the returned browser websocket to resolve to loopback;
- require the websocket port to equal the assigned Fleet port;
- never fall across to another room/port.

Current drift:

- PYLAUNCH defaults to `127.0.0.1`, but generic CLI `--host` is unrestricted;
- PYLAUNCH `probe_endpoint()` accepts any `ws*` URL returned by `/json/version` without same-host/port verification;
- Recorder base CLI `--cdp-host` is unrestricted;
- Recorder Fleet children filter manifest hosts to loopback but do not verify returned websocket stays on the requested port;
- Prospective constructs loopback endpoints, but also lacks returned websocket port pinning.

This is P1 rather than P0 because official/default owner flows are loopback and Browser Fleet itself is strongly isolated; however, the explicit cross-component contract says localhost + strict room/port isolation and the lower-level clients currently permit bypass/drift.

Fresh-fix ownership:

1. **PYLAUNCH endpoint guard lane** — only `parallel/PYLAUNCH/**`.
   - reject non-loopback `--host`;
   - normalize loopback aliases safely;
   - reject `/json/version` websocket whose host is non-loopback or whose port differs from requested CDP port;
   - regression: remote host, cross-port websocket, valid localhost/127.0.0.1 aliases, Fleet selected endpoint.
2. **WOF-052L endpoint guard lane** — only `parallel/WOF052L_RECORDER/**`.
   - same host/port checks in single-CDP and Fleet child connection paths;
   - prove one Fleet endpoint cannot consume another endpoint's returned websocket.
3. **Prospective side** — fold into the existing P0 Discovery V2 sync lane.

### P1-URL-SCHEME-GATE — `P1_DRIFT_RISK`

Discovery V2 is supposed to make URL shape a hint rather than identity authority.

Current inconsistency:

- Browser Fleet's repository regression accepts an already-existing related `blob:` Worker when the read-only module probe succeeds;
- PYLAUNCH `_worker_compatible()` hard-rejects `blob:`, `data:`, and `javascript:` before module/exact-identity probe;
- WOF-052L `discovery_v2_sync.py` does the same before module/exact-identity probe;
- current Prospective path is even stricter because it still requires `gstyphoon*.js`.

This creates a stitched-stack contradiction: Fleet can legitimately report its **cheap** Worker indicator while the authoritative/capture components refuse to evaluate the same attachable runtime solely because of URL scheme.

Important safety distinction:

> Read-only attachment to an already-existing Blob/Data target is not Worker replacement, Blob creation, ObjectURL creation, or Worker URL rewrite.

The no-replacement/no-rewrite safety invariant must remain unchanged.

Fresh-fix ownership:

- **PYLAUNCH URL-gate lane** — only `parallel/PYLAUNCH/**`;
- **WOF-052L URL-gate lane** — only `parallel/WOF052L_RECORDER/**`;
- existing Prospective V2 lane must not reintroduce URL scheme as an authority gate.

Minimum acceptance: for an already-existing attachable worker-like related target, module/heap + exact World identity decide authority; URL is diagnostic/hint only. Ambiguous exact identities still fail closed.

### P1-DIRECT-OPENERID-ASSOCIATION — `P1_DRIFT_RISK`

`parallel/WORKER_SURFACE/AUDIT.md` already established that Worker `openerId` is not the Worker parent model. The correct association model is based on page-rooted related topology and, for direct/fallback reasoning, `parentId` / `parentFrameId` + frame/context mapping.

Current direct fallback still does:

- PYLAUNCH: `parentId`, then `openerId`, then unique page;
- Recorder: `parentId`, then `openerId`, then sole page.

The preferred page-autoattach path is structurally sound. The drift is limited to the compatibility fallback, so this is P1 rather than P0.

Fresh-fix ownership:

- **PYLAUNCH direct-association hardening** — only `parallel/PYLAUNCH/**`;
- **WOF-052L direct-association hardening** — only `parallel/WOF052L_RECORDER/**`.

Minimum acceptance:

- never treat Worker `openerId` as parent authority;
- prefer `parentId` / `parentFrameId` where actually available;
- otherwise require one uniquely identified WOF page on that endpoint or fail closed;
- preserve old direct Worker support without weakening multi-tab isolation.

### P1-REGRESSION-GUARD-GAP — `P1_DRIFT_RISK`

The global regression orchestrator can currently stay green while important integration drift survives.

Observed in `parallel/REGRESSION_ORCH/manifest.json`:

- Recorder suite runs `owner_zh_cn.py --self-test`, while the official current `RUN_WOF052L_RECORDER.cmd` invokes `owner_v2_zh_cn.py` to install Discovery V2 before entering the Chinese owner flow;
- `test_discovery_v2_sync.py` is separately run, but the official V2 entrypoint/import/install integration is not the suite entry command;
- Prospective suite currently runs `test_validator.py` only, which correctly covers evidence semantics but cannot catch the live Discovery V2 P0.

Fresh-fix ownership:

**REGRESSION_ORCH Discovery V2 integration guard lane** — write only `parallel/REGRESSION_ORCH/**`, after the component fixes land.

Minimum acceptance:

- make the official Recorder V2 entrypoint a required/compiled/self-testable integration surface;
- add the new Prospective Discovery V2 test file as a safety-critical required path/command;
- keep existing evidence/validator regression;
- add endpoint confinement/cross-port tests from the component lanes to the corresponding global suite commands if not already transitively executed.

## Expected / safe role differences that must NOT be "fixed"

### Browser Fleet identity is deliberately non-authoritative

Fleet is correct to avoid the expensive full World hash in ordinary status refresh. Its manifest already says:

- `workerIndicatorOnly: true`
- `world921031Identity: "NOT_CHECKED"`
- consumers must independently re-probe

Do not turn Fleet into a second identity authority.

### Ambiguous Fleet indicators may remain visible

Fleet may expose `workerCount > 1` and still show a cheap Worker indicator. That is acceptable only because it does not admit capture/prospective evidence and does not prove World identity. Admission authorities must still fail closed.

### Readiness strictness may differ by role

- Fleet: cheap module/heap-shape indication;
- PYLAUNCH: exact identity proof authority;
- Recorder: module/heap/CPS RAM readiness + exact identity before capture;
- Prospective: module/heap readiness + exact identity before prospective probe.

These are `EXPECTED_ROLE_DIFFERENCE`, not drift.

### Evidence classes are correctly separated

Prospective session creation freezes the candidate hash/time. Existing regression proves:

- discovery evidence never satisfies the prospective gate;
- Recorder evidence defaults to discovery;
- rooms started after the freeze may be prospective;
- pre-freeze rooms remain discovery;
- manifest mutation after freeze is rejected;
- production auto-promotion is forbidden.

Do not change these semantics while fixing live discovery.

## Safety conclusion

Across the audited primary paths, no cross-component fix is authorized to weaken these invariants:

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

The fixes above are topology/association/endpoint-guard changes only. They do not require game RAM writes, gameplay input, Worker replacement, Alpha changes, attack research expansion, or browser process memory access.

## PM execution order

1. **Close P0 first:** Prospective Validator Discovery V2 Sync lane.
2. In parallel, close PYLAUNCH + Recorder P1 endpoint/URL/direct-association hardening in their own write scopes.
3. Update Regression Orchestrator guard only after those component blobs/tests exist.
4. Re-run this cross-component audit against the new blobs.
5. Only then feed the aligned stack into the **Unified Windows Live Proof Bundle**. This audit does not request any owner Browser operation.

## Stop condition

Satisfied with exact blockers and ownership:

> **DISCOVERY V2 CROSS-COMPONENT AUDIT COMPLETE**

Blocking drift remains:

- `P0-PROSPECTIVE-LIVE-DISCOVERY`
- `P1-ENDPOINT-CONFINEMENT`
- `P1-URL-SCHEME-GATE`
- `P1-DIRECT-OPENERID-ASSOCIATION`
- `P1-REGRESSION-GUARD-GAP`

No component implementation was changed in this lane.