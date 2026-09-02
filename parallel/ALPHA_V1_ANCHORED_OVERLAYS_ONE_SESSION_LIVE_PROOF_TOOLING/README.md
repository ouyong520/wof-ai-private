# Alpha V1 Anchored Overlays — One-Session Live-Proof Tooling Recovery V2

Status: repository tooling only. This folder does **not** contain Browser/WOF evidence and does not activate either production projection profile.

## Purpose

This proof-only lane extends the existing `parallel/HUDANCHOR_PROOF/**` one-session camera/X/Y/WebGL proof so a future **single uninterrupted real Browser/WOF runtime** can also retain evidence for the two Alpha V1 production surfaces:

- player-head danger warning, including actual anchored draw versus fixed-HUD fallback;
- enemy-head current-target labels `1P / 2P / 3P`, including actual draw/suppress and live retarget clearing.

The observer records the same authority inputs used by the current product helpers: live actor/slot/type/target identity, `warningSampleAt`, sample ages, confidence, runtime/projection/drawing-buffer epochs, mapping keys, projected anchors and helper decision/reason.

## Hard boundaries

- no ROM/game RAM writes;
- no input injection or AI/control path;
- no danger-rule or `target7E` semantic changes;
- no Safe Transport authority changes;
- no synthetic target/warning/coordinate injection;
- no repository write to `product/alpha/**`;
- candidate projection profiles are tagged `PROOF_ONLY_RUNTIME_BINDING` and exist only in the current runtime;
- repository/synthetic tests can never become `REAL_BROWSER_WOF_BOUNDED_DYNAMIC_LIVE_PROOF` evidence.

## Loader

The future bounded live run uses the same line in the active game Worker Console and Top page Console, after normal Alpha V1 is already running:

```js
fetch('https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/parallel/ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING/wof_alpha_v1_dual_live_proof.js?'+Date.now()).then(r=>r.text()).then(t=>(0,eval)(t))
```

The loader first starts the existing HUDANCHOR common proof in that same context, then starts the recovery-v2 observer. No second calibration runtime is created.

## Live-only profile facts

The existing common calibration click proves the desired above-character anchor, but it does not mathematically separate player body `yBias` from `headClearanceNative`. Recovery V2 therefore adds one bounded **P1 body/reference click** in the same runtime. The tool maps that click to the current native viewport and combines it with the already-frozen live head click and current P1 world Y/Z sample. No coordinate is copied or typed by the Owner.

Enemy `enemyHeadOffsetsByType` is likewise never guessed. For each supported type to be enabled in the candidate profile, the Owner clicks the head center of a currently non-overlapping live enemy. The tool binds the click to the nearest current live enemy X/slot/type, records its world Y/Z, and derives the offset. Ambiguous overlap fails closed; unobserved types are omitted and remain unsupported. Repeated captures with spread greater than 4 native pixels are rejected as unstable.

## Proof-only runtime binding

After common proof + live clearance observations are ready, the Worker side validates the two candidate profiles with the current Alpha helper validators. It then calls the **existing official** `WOFAlphaTransportAuthority.install` with the existing session binding while intercepting only the two projection-profile fetches for that single install. The fetch shim is restored in `finally` and the candidate profiles are never written to the repository.

This lets the normal Alpha worker/HUD render the actual two surfaces with the candidate live facts while keeping existing transport, detector, target and rendering semantics intact. The Top observer wraps the existing helper objects' `buildPlan` methods only to record their returned plan; the original plan is delegated unchanged and is what the HUD draws.

## Required live coverage before `IMPLEMENTATION_READY`

The terminal result stays `INCOMPLETE_OBSERVATION:*` unless all required live gates are observed in the same proof session:

- common HUDANCHOR objective proof and resize/fullscreen recovery;
- real player warning anchored draw;
- real enemy label anchored draw;
- fast horizontal movement with both surfaces observed;
- player depth movement and complete jump;
- rapid camera/stage scroll with both surfaces;
- simultaneous player + camera motion with both surfaces;
- moving enemy label follow;
- live enemy retarget with old target no longer drawn;
- resize/fullscreen mapping change with both surfaces observed on current mapping;
- one real stale-authority window showing **enemy no-draw and player fixed-HUD fallback** rather than stale anchored rendering;
- final visual classification `VISUAL_OK` and no recorded P0 drift/wrong identity/wrong target/stale cue.

Multiple-enemy isolation is recorded when naturally exposed but remains `NOT_OBSERVED` rather than fabricated if the encounter does not expose it.

The `450ms authority gap` control is a bounded real-authority exercise: it stops the current official Alpha observer long enough for normal HUD freshness gates to expire, observes real no-draw/fallback, then reinstalls the same live candidates and transport binding. It does not inject fake warnings, targets or coordinates.

## Terminal artifact

`WOFAlphaDualProof.result()` emits one JSON using the committed `parallel/ALPHA_V1_ANCHORED_OVERLAYS_LIVE_PROOF_PREP/LIVE_PROOF_EVIDENCE_SCHEMA.json` root/event structure and only these verdict families:

- `IMPLEMENTATION_READY`
- `FAILED_COMPONENT:<component>`
- `INCOMPLETE_OBSERVATION:<component>`

The artifact also adds an allowed `proofOnly` block containing the runtime-only candidate profiles and the live observations from which they were derived, plus `productionProfilesWritten:false`.

## Repository test

```text
node parallel/ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING/tooling_regression.mjs
```

This is deterministic repository evidence only. It validates binder fail-closed rules, observer correlation, invalid/no-draw classification, success terminal generation, required-phase gating, current HUDANCHOR compatibility and source boundaries. It is not Browser/WOF live proof.
