stageId: `ALPHA_V1_PRODUCT_TAKEOVER_P18_MAINTAINED_HUD_CANONICAL_DRAW_ACKNOWLEDGEMENT`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.maintained-hud-canonical-draw-acknowledgement-v1`
dedupMode: `exclusive`
resultProtocol: `wof-alpha-worker-result-v1`
resultJsonPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P18_MAINTAINED_HUD_CANONICAL_DRAW_ACKNOWLEDGEMENT_RESULT.json`
resultMdPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P18_MAINTAINED_HUD_CANONICAL_DRAW_ACKNOWLEDGEMENT_RESULT.md`
terminalCommitPrefix: `WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P18_MAINTAINED_HUD_CANONICAL_DRAW_ACKNOWLEDGEMENT`
dispatchManifestPath: `parallel/PM/DISPATCH_MANIFESTS/ALPHA_V1_CANONICAL_FINALIZATION_P15_P17_P18_LONG_3_WORKER_V1.json`

# Alpha V1 P18 — Maintained HUD Canonical Draw Acknowledgement

Repository: `ouyong520/wof-ai-private`

This is a larger finalization task. Implement the whole bounded draw-evidence module rather than splitting it into micro-stages.

Read latest `main` first, then at minimum:
- `AGENTS.md`
- `parallel/PM/TESTING_CADENCE_POLICY.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/ALPHA_V1_CANONICAL_FINALIZATION_P15_P17_P18_LONG_3_WORKER_DISPATCH.md`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P11_MAINTAINED_HUD_CANONICAL_OVERLAY_WIRING_RESULT.json`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P16_OWNER_CANONICAL_STATUS_ACCEPTANCE_EVIDENCE_RESULT.json`
- current P15 implementation/candidate metadata if present, only to understand runtime contract; do not edit P15-owned files.
- `product/alpha/wof_alpha_hud.js`
- `product/alpha/wof_alpha_canonical_overlay_plan.js`
- `product/alpha/wof_alpha_canonical_anchor_envelope.js`
- `parallel/PYLAUNCH/wof_launcher/cdp.py`

## Ownership

Perform normal dedup-v2 create-only canonical claim + exact-token re-read + create-only stage claim + exact-token re-read before implementation. Fail closed on ownership failure. Do not invent recovery.

## Goal

Close the evidence gap between **HUD ingest accepted** and **maintained WebGL draw primitive actually executed**.

P18 must add bounded, read-only acknowledgement/evidence for canonical enemy labels and player danger warnings that actually traverse the maintained HUD's real draw path. This evidence is for final acceptance diagnostics only. It is **not** production coordinate authority and is **not** sufficient by itself to claim that the Owner visually saw the overlay.

Target proof chain:

`P9/P8 canonical plan accepted`
`-> maintained HUD canonical draw intent selected`
`-> existing maintained WebGL label/warning draw primitive invoked`
`-> bounded draw acknowledgement recorded`
`-> read-only collector writes verification snapshot`

## Workstream A — HUD draw acknowledgement ledger

Modify the maintained `product/alpha/wof_alpha_hud.js` narrowly.

1. Add a bounded ring buffer/ledger for canonical draw acknowledgements only.
2. Record an acknowledgement **at the actual maintained primitive invocation boundary**, not merely at envelope ingest or plan creation.
3. Record only deterministic, non-sensitive fields needed for proof, for example:
   - monotonic draw sequence;
   - sample/draw timestamp;
   - canonical intent kind (`enemy-target-label`, `player-danger-warning`);
   - actor/source id when present;
   - label/warning identity when present;
   - native x/y actually passed to the maintained primitive;
   - authority/runtime/renderer identity currently bound by the canonical HUD state;
   - canonical plan/envelope sequence or sample identity when available;
   - whether the primitive call completed without local exception.
4. Keep the ledger bounded (for example last 64/128 entries). Do not create unbounded memory growth.
5. Do not record screenshot pixels, world projection, guessed coordinates, DOM geometry, or legacy tracker points as canonical evidence.
6. Canonical suppression/hide must not fabricate draw entries.
7. Authority clear/rebind must make stale evidence distinguishable from the new authority generation; either reset the current ledger or retain bounded history with explicit generation identity. Never merge incompatible epochs as one current proof.

## Workstream B — read-only HUD evidence API

Expose a stable read-only API on `window.WOFALPHAHUD`, preferably:

`canonicalDrawEvidence()`

or an equivalently clear name.

The snapshot must include:
- schema/version;
- bounded entries;
- current canonical bound/unbound state;
- exact authority/runtime/renderer identity if bound;
- latest acknowledgement state/reason;
- safety metadata;
- `visibleProof: "NOT_PROVEN"`.

Do not expose a mutator that lets external code invent acknowledgement rows.

Do not change existing P11 bind/ingest/clear APIs except as narrowly needed to hook evidence lifecycle.

## Workstream C — Python/CDP evidence collector

Add a narrow read-only collector, preferably:

`parallel/PYLAUNCH/wof_launcher/canonical_draw_evidence.py`

or a similarly scoped new file.

Responsibilities:
1. Attach to the explicit accepted page target through existing CDP abstractions.
2. Read only `window.WOFALPHAHUD.canonicalDrawEvidence()`.
3. Validate snapshot schema and exact current authority identity supplied by the caller.
4. Reject stale/mixed runtime/renderer/page evidence.
5. Atomically write the default verification snapshot:

`~/Documents/WOF_RESULTS/ALPHA_CANONICAL_DRAW_EVIDENCE.json`

6. Include deterministic metadata needed by P17:
   - evidence schema;
   - collectedAt;
   - page target;
   - authority/runtime/renderer identity;
   - bounded acknowledgement rows;
   - draw evidence state such as `NO_CANONICAL_DRAW`, `CANONICAL_DRAW_ACKNOWLEDGED`, `STALE_OR_MISMATCH`, `HUD_API_MISSING`;
   - safety;
   - `visibleProof: "NOT_PROVEN"`.
7. Never turn draw acknowledgement into position authority or visible PASS.

If useful, add a small CLI wrapper or pure function so P17 can invoke collection later without importing P15 runtime internals.

## Workstream D — evidence semantics

Distinguish these clearly:
- `HUD_INGEST_ACCEPTED`: P11 accepted canonical envelope/plan;
- `CANONICAL_DRAW_ACKNOWLEDGED`: a maintained WebGL label/warning draw primitive was actually invoked for a canonical intent;
- `VISIBLE_PROOF`: still not established automatically.

The final Owner visual gate remains the only source of actual visual confirmation.

## Preserve behavior

Must preserve:
- fixed TEST path;
- P5 direct P1 path;
- P6/P7 semantics;
- P9/P8/P11 fail-closed canonical behavior;
- no canonical legacy spatial fallback;
- existing drawing appearance/placement semantics;
- read-only safety.

Do not broaden warning/target policy.

## File boundaries

Expected writes:
- `product/alpha/wof_alpha_hud.js`
- new narrow collector/helper under `parallel/PYLAUNCH/wof_launcher/` that is not `alpha_runtime.py` or P15 coordinator
- focused P18 self-check files
- P18 RESULT files.

Do not modify:
- `parallel/PYLAUNCH/wof_launcher/alpha_runtime.py`
- P15 canonical runtime coordinator
- `product/alpha/wof_alpha_field_adapter.js`
- package refresh/manifest/candidate files
- W3 producer/analyzer files or claim
- P16 `state.py`/`tray.py`
- alpha-live.

## Focused self-check only

Implementation first. Then run only narrow checks:
- JS syntax/parse;
- canonical enemy label draw fixture records one acknowledgement only when the maintained primitive is invoked;
- canonical player warning draw fixture records one acknowledgement only when the maintained primitive is invoked;
- suppressed canonical intent records no draw acknowledgement;
- authority rebind/revoke does not let stale evidence appear current;
- ledger bound is enforced;
- fake-CDP collector accepts exact identity, rejects stale renderer/runtime/page mismatch, and atomically writes the expected JSON;
- fixed TEST/P5 APIs still exist and are not included as canonical draw acknowledgement.

No broad QA. No real WOF. No package refresh. No alpha-live movement.

## Terminal

Write exact RESULT.json + RESULT.md declared above. Record implementation commits, changed files, focused checks, productProof boundary, safety, integrationReady, blocker, and nextAction.

A successful result proves repository/runtime draw acknowledgement behavior only. It must explicitly state that Owner-visible screen proof is still NOT_RUN/NOT_PROVEN.

Final commit begins:
`WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P18_MAINTAINED_HUD_CANONICAL_DRAW_ACKNOWLEDGEMENT <STATE>`

Chat only COMPLETE / SUBCOMPLETE / precise BLOCKED.
