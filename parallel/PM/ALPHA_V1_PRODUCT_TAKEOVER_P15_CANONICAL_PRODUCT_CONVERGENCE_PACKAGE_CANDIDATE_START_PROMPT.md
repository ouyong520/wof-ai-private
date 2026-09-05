stageId: `ALPHA_V1_PRODUCT_TAKEOVER_P15_CANONICAL_PRODUCT_CONVERGENCE_PACKAGE_CANDIDATE`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.canonical-product-convergence-package-candidate-v1`
dedupMode: `exclusive`
resultProtocol: `wof-alpha-worker-result-v1`
resultJsonPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P15_CANONICAL_PRODUCT_CONVERGENCE_PACKAGE_CANDIDATE_RESULT.json`
resultMdPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P15_CANONICAL_PRODUCT_CONVERGENCE_PACKAGE_CANDIDATE_RESULT.md`
terminalCommitPrefix: `WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P15_CANONICAL_PRODUCT_CONVERGENCE_PACKAGE_CANDIDATE`

# Alpha V1 Product Takeover P15 — Canonical Product Convergence + Package Candidate

Repository: `ouyong520/wof-ai-private`

This is intentionally a larger convergence task. Do not split it into micro-stages unless a genuine external blocker makes one coherent implementation impossible.

Read latest `main` first, then at minimum:
- `AGENTS.md`
- `parallel/PM/TESTING_CADENCE_POLICY.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/ALPHA_V1_P14_SUPERSEDED_BY_P15_LONG_CONVERGENCE_DECISION.md`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P10_CANONICAL_ANCHOR_RUNTIME_TRANSPORT_BRIDGE_RESULT.json`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P12_CANONICAL_ACTOR_GENERATION_REGISTRY_RESULT.json`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P13_ALPHA_RUNTIME_CANONICAL_BOOTSTRAP_PARITY_RESULT.json`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P11_MAINTAINED_HUD_CANONICAL_OVERLAY_WIRING_RESULT.json`
- `parallel/PYLAUNCH/wof_launcher/alpha_runtime.py`
- `parallel/PYLAUNCH/wof_launcher/canonical_overlay_runtime_bridge.py`
- `parallel/PYLAUNCH/wof_launcher/canonical_actor_generation_registry.py`
- `product/alpha/wof_alpha_field_adapter.js`
- `product/alpha/wof_alpha_hud.js`
- `parallel/OWNER_ONECLICK/refresh_manifest.py`
- `parallel/OWNER_ONECLICK/package_manifest.json`
- package/pin tooling actually used by current Owner one-click path.

## Ownership

Perform normal dedup-v2 create-only canonical claim + exact-token re-read + create-only stage claim + exact-token re-read before implementation. Fail closed on any ownership failure. Do not invent recovery.

Do **not** create or modify the superseded P14 claim. P14 never acquired ownership and its work is now part of P15.

## Product goal

Turn the already-complete canonical components into one normal package-selected Alpha runtime candidate instead of a collection of isolated modules.

Required product chain:

`accepted exact World authority`
`-> current W3-format frame identity snapshot`
`-> P12 actor/generation registry`
`-> P10 DeterministicRenderObjectAnchor transport bridge`
`-> P9 envelope normalization`
`-> P8 unified overlay plan`
`-> P11 maintained WebGL HUD`

while preserving target/danger semantics and removing old projection coordinates as a prerequisite for canonical semantic publication.

The candidate must remain fail-closed until W3 renderer/object source is actually qualified in real WOF. This stage does not fabricate that proof.

## Workstream A — semantic/spatial decoupling (absorbed P14)

In the maintained runtime semantic producer path, separate **what** should be shown from **where** it should be drawn.

1. Enemy target semantics (`slot`, `target7E`, mapped target `P1/P2/P3`, and other non-spatial fields actually needed by the canonical planner) must be publishable from exact read-only game semantics even when the old enemy projection profile is unavailable/unproved.
2. Player danger/warning semantics must likewise remain semantic-only for canonical composition; do not require old player projection merely to decide that a warning exists.
3. Canonical mode position authority must come only from P9/P10 canonical anchors.
4. Old projection-derived x/y/head coordinates may remain only for explicitly legacy/non-canonical paths if still required for compatibility, but they must not gate canonical semantic publication and must never become fallback once canonical authority is bound.
5. Preserve `0 -> P1`, `4 -> P2`, `8 -> P3` semantics.
6. Preserve read-only safety and current warning policy; do not expand danger rules.

Prefer a minimal, explicit schema distinction such as semantic-only message fields rather than overloading old spatial payloads.

## Workstream B — normal AlphaRuntime canonical lifecycle integration

Wire P12 + P10 + P13 into the normal `AlphaRuntimeManager` lifecycle.

1. Reuse `CanonicalActorGenerationRegistry` and `CanonicalOverlayRuntimeBridge`; do not duplicate their logic.
2. Establish one explicit lifecycle object/coordinator per accepted authority/page target. A new authority/runtime/renderer/page must clear/revoke old canonical state before rebinding.
3. When a current W3-format frame is available, resolve descriptors through P12, then pass only READY registry descriptors to P10 with the exact binding/frame/sample time.
4. Registry suppression/invalid identity must clear or suppress canonical overlay for that sample; never reuse old descriptors.
5. P10 suppression must remain suppression; never fill coordinates from projection/screenshot/old points.
6. Ensure page bootstrap capability from P13 is positively verified before canonical bind/ingest.
7. Surface canonical lifecycle status through normal runtime status, including at least: capability present, bound/unbound, latest ingest state/reason, authority/runtime/renderer identity, and whether current frame resolved READY or SUPPRESSED. Do not label API availability as visible draw proof.
8. Preserve fixed TEST and P5 direct P1 behavior independently.
9. Revoke canonical overlay explicitly on runtime stop, target replacement, authority change, page loss, renderer epoch change, or fatal bridge/CDP error.
10. Avoid introducing background polling that competes with an existing canonical W3 producer. If no stable W3 producer callback exists yet, define a narrow explicit ingest seam in AlphaRuntime and keep the runtime SUPPRESSED/WAITING rather than inventing a source.

## Workstream C — package-selected candidate pinning

Create one coherent package candidate that actually pins the integrated canonical stack.

1. Use the repository's existing package/manifest refresh mechanism; do not hand-wave package selection and do not weaken `_verified_text` integrity.
2. The candidate must pin every runtime file needed by the normal canonical path, including the current versions of:
   - `parallel/PYLAUNCH/wof_launcher/alpha_runtime.py`
   - P10 bridge module
   - P12 registry module
   - P9 canonical anchor envelope JS
   - P8 canonical overlay plan JS
   - P11 maintained HUD JS
   - any semantic producer file changed by P15
   - any narrow coordinator module added by P15.
3. Update manifest/tooling only through the canonical package refresh flow already used by Owner one-click. If the current refresh script has an explicit allowlist, update it narrowly and deterministically.
4. Produce a new candidate package version/pin metadata as required by existing tooling.
5. **Do not move `alpha-live`** and do not change the permanent Owner launcher to select this candidate yet. PM will promote after integration review/final gate.
6. Do not weaken blob SHA verification or load arbitrary `main` files at runtime.

## Workstream D — product status coherence

Make the normal status truthful and useful for PM/Owner-facing integration later.

At minimum distinguish:
- canonical stack installed/capable;
- canonical authority bound/unbound;
- waiting for W3 frame/source qualification;
- identity/generation suppressed;
- renderer source unproven;
- canonical anchors READY;
- HUD ingest accepted/suppressed;
- fatal canonical runtime error.

Do not report `READY`, `VISIBLE`, or equivalent product success solely because modules loaded or fake fixtures passed.

## Write boundaries

Expected files may include, as genuinely needed:
- `parallel/PYLAUNCH/wof_launcher/alpha_runtime.py`
- a new narrow canonical runtime coordinator beside it
- `product/alpha/wof_alpha_field_adapter.js`
- package refresh/pin/manifest files under `parallel/OWNER_ONECLICK/`
- narrow focused self-check fixtures.

Do not modify W3 capture/producer/qualification ownership or its claims. Do not move `alpha-live`. Do not broaden target/danger policy. Do not add screenshot/template/world-projection fallback. Do not modify unrelated Collector / Training Farm code.

## Acceptance invariants

A correct implementation must satisfy all of these:

1. Canonical semantic publication no longer depends on legacy projection proof.
2. Canonical spatial draw never receives legacy projection/screenshot coordinates as fallback.
3. Actor identity/generation reaches P10 only through P12 or an exactly equivalent imported registry result, not ad-hoc construction.
4. P10 bind/ingest/revoke is owned by one normal runtime lifecycle and clears on authority changes.
5. Package-selected AlphaRuntime can actually verify/load the integrated P9/P8/P11/P10/P12/P15 stack from pinned blobs.
6. Missing W3 proof yields truthful WAITING/SUPPRESSED behavior, not a visible guessed overlay.
7. Fixed TEST and existing accepted direct P1 path remain intact.
8. Safety remains `readOnly=true`, `ramWrites=0`, `inputInjection=false`.

## Implementation cadence

Implementation first. This is a coherent convergence module, so finish the whole bounded scope before declaring terminal unless a real external blocker exists.

Run only focused checks needed to avoid shipping obvious breakage:
- Python parse/compile for touched Python;
- JS parse/syntax for touched JS;
- one controlled lifecycle fixture proving authority bind -> P12 descriptors -> P10 ingest -> revoke;
- one suppression fixture proving invalid/stale/unproven input clears/hides with no fallback coordinates;
- one semantic-only fixture proving target semantics still publish with projection unproved;
- one package candidate/manifest integrity check proving all required canonical files are pinned and blob-verifiable;
- one narrow preservation check for fixed TEST / P5 API presence.

Do not run broad Fresh QA, full historical regression, real-WOF acceptance, or unrelated package matrices. Final concentrated acceptance happens after the integrated candidate is reviewed.

## Terminal result

Write exactly:
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P15_CANONICAL_PRODUCT_CONVERGENCE_PACKAGE_CANDIDATE_RESULT.json`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P15_CANONICAL_PRODUCT_CONVERGENCE_PACKAGE_CANDIDATE_RESULT.md`

Record:
- implementation commits;
- changed files;
- package candidate version/pin evidence;
- focused tests;
- integrationReady;
- exact remaining W3/Owner gate boundary;
- safety;
- nextAction.

Expected successful terminal state is implementation/package **integration-ready**, not real-WOF visible PASS.

Final commit begins:
`WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P15_CANONICAL_PRODUCT_CONVERGENCE_PACKAGE_CANDIDATE <STATE>`

Chat terminal only: `COMPLETE`, `SUBCOMPLETE`, or precise `BLOCKED`.
