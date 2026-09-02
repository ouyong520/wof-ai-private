# Alpha V1 Anchored Overlays One-Session Live-Proof Tooling — Independent Cross-Check V1 RESULT

## Subject

Stage: `ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING_CROSSCHECK_V1`

Mode: canonical dedup v2 `independent-validation`

Effective key: `alpha.v1.anchored-overlays.one-session-live-proof-tooling-recovery-v2-crosscheck--iv--alpha-v1-dual-overlay-tooling-recovery-v2--second-opinion-adversarial-v1`

Claim token: `9b0e5be2-9a39-4415-9019-25e08a518c8b-df5d7dda5f0385407fb84d31ec6b38af`

This was a repository-only independent second-opinion cross-check. No Browser/WOF session was started. No tooling implementation and no `product/alpha/**` file was modified. Fresh QA verdicts/fixtures were not used as proof.

## Fixture under review

Recovery V2 durable completion was re-verified from:

- `parallel/PM/STAGE_CLAIMS/ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING_RECOVERY_V2.json` — COMPLETE, result path points to the durable Recovery V2 result.
- `parallel/ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING/RESULT.md` — COMPLETE / ready for fresh QA or bounded live run.
- current `RUN_MANIFEST.json` plus all pinned product/proof/HUDANCHOR/schema blobs.

Current blobs independently inspected include:

- `proof_core.js` `fbfa665daa624b7a81b6b75d488af504194bd378`
- `wof_alpha_v1_dual_live_proof_top.js` `3f2ffdfc2947387518e593445306f8803132345c`
- `wof_alpha_v1_dual_live_proof_worker.js` `5cc30f3a3b32ee0ef3dfe1b9ac2937dbabc774f3`
- `wof_alpha_v1_dual_live_proof.js` `30c965bb8b16466810781e2741f2d2eb86a0533d`
- player helper `af7f2359514dc6f86f74fac0c47858e8a6acf107`
- enemy helper `e6e1260559f735b85ce6f69e87803369f125b2de`
- real Worker `b7f4506fc90b681ede059df5ad3316e665c6f15e`
- player profile `bbed0618b348961580ca805bb93e4d17525f0142`
- enemy profile `8de57739818503a0e14702d2fa0bb4eba58228d2`
- live evidence schema `f9213012502b4a307e6cab0df23fbe9f5812f769`
- HUDANCHOR proof loader/top/worker/GL blobs exactly matching `RUN_MANIFEST.json`.

An independent scratch adversarial matrix was built and executed outside the repository. It did not invoke the Recovery regression fixture and did not consume any Fresh QA fixture/verdict.

## Checks

### Current-manifest drift

PASS for the current checked tree: every product/proof/HUDANCHOR/schema SHA listed by `parallel/ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING/RUN_MANIFEST.json` matched the current blob SHA observed on `main`. No release-relevant implementation drift was found in those pinned blobs.

### Product helper raw-authority fail-closed checks

PASS:

- player `warningSampleAt` requires primitive finite `number`; missing/null/string/boxed/coercible/NaN/Infinity fail closed to fixed HUD.
- player runtime/projection/drawing-buffer authority requires strict valid epoch strings and all authority epochs equal.
- enemy drawing-buffer authority requires `state.epoch === state.projectionEpoch === projection.epoch`; internally consistent stale-old drawing-buffer epoch cannot be mixed with current projection epoch.
- enemy raw target is strict primitive integer `0/4/8 -> P1/P2/P3 -> 1P/2P/3P`.

### Read-only / execution boundary

PASS for static repository boundary:

- proof Worker reads CPS RAM but does not write game RAM;
- no gameplay input injection was introduced;
- no Worker replacement was introduced;
- stale-authority exercise uses the existing real transport `stop` / official `WOFAlphaTransportAuthority.install` re-install path;
- current production projection profiles remain `UNPROVED` / fail-closed and were not repository-activated.

## Adversarial semantic results

### 1. False `IMPLEMENTATION_READY` / synthetic promotion — BLOCKER

`proof_core.js` defines live provenance with a purely declarative predicate:

`evidenceClass === REAL_BROWSER_WOF_BOUNDED_DYNAMIC_LIVE_PROOF`, `source === LIVE_OBSERVATION`, `synthetic !== true`, and `browserWofActuallyRun === true`.

There is no independently rooted witness/token tying those fields to the actual one-session Top/Worker runtime. `Session` also initializes `boundaries.browserWofActuallyRun:true` and `syntheticEvidenceUsedAsLiveProof:false` by construction.

Independent scratch attack: a repository-generated object self-declaring those four fields was accepted by the same `real()` semantics and accepted by the player profile binder; a synthetic `Session` whose public gate state was populated to the required PASS values returned `IMPLEMENTATION_READY` while still self-reporting the live boundaries.

Therefore repository/synthetic/candidate evidence can semantically masquerade as real-live evidence inside the proof core. The current core does not make `IMPLEMENTATION_READY` cryptographically or structurally impossible for synthetic construction.

This violates the explicit cross-check requirement that synthetic/candidate/replay evidence must never produce `IMPLEMENTATION_READY` or masquerade as Browser/WOF live evidence.

### 2. Player/enemy observer isolation — BLOCKER

Top phase scoring uses time-window presence of any `ANCHORED_DRAW` player event and any `ANCHORED_DRAW` enemy event. It does not require the two events to share the same runtime/projection/drawing-buffer epoch tuple.

Independent scratch attack: one player anchored event from epoch A plus one enemy anchored event from epoch B in the same phase window produced player PASS + enemy PASS under the current `mark()` semantics.

The individual product helpers are strict, but the cross-surface live-proof phase gate is not independently epoch-correlated. This allows observer authority to be combined across different authority epochs at the proof-scoring layer.

### 3. P1 -> P2 -> P3 retarget vs same-slot replacement — BLOCKER

Normal strict target mapping itself is correct, but the live-proof identity is not replacement-safe.

Both the Recovery Worker and current production real Worker construct enemy identity as:

`sourceId: 'enemy-slot-' + slot`.

No lifecycle/generation/object discriminator is retained. Top retarget scoring groups events by that `actorIdentity` and marks `liveRetarget` PASS when the target changes.

Independent scratch attack:

- physical enemy A in slot 3 -> `actorIdentity=enemy-slot-3`, target P1;
- A disappears and physical enemy B reuses slot 3 -> same `actorIdentity=enemy-slot-3`, target P2.

The current retarget scorer marks this as a valid retarget even though it is an enemy replacement, not a same-enemy target transition. The same defect can false-close a required live retarget gate.

### 4. Player respawn / player head-body authority — BLOCKER

Recovery Worker player snapshots are keyed only as P1/P2/P3 and contain present/x/y/z/sampleAt/epoch fields; they carry no player lifecycle/generation identity. Production player spatial snapshots likewise do not expose a replacement generation.

The P1 body/reference click combines the current P1 snapshot with the frozen common head click, but no lifecycle identity proves that the frozen head click and current body click belong to the same P1 object lifetime. A respawn/object replacement inside the same runtime epoch is therefore indistinguishable to the proof model.

Old player head/body calibration authority can survive a player replacement without an identity barrier.

### 5. Enemy type head-offset ambiguity — NOT SUFFICIENTLY AUTHORITATIVE

Enemy head capture selects the nearest live enemy by horizontal X distance and rejects only a narrow second-nearest X ambiguity. The capture does not carry a lifecycle-safe enemy identity, and the same-slot replacement issue applies to the captured observation. A single capture also has zero spread by definition and can be marked stable.

This is not by itself needed for the terminal BLOCKED verdict, but it means current type-head evidence cannot repair the replacement defect by itself.

### 6. Stale-authority exercise — LIVE PATH PRESENT, PROVENANCE GAP REMAINS

The bounded 450 ms real transport stop/reinstall path is present and uses the official install API. The Top HUD observer requires player fixed fallback and enemy suppression before the stale gate can close in the normal live path.

However `Session.record()` classifies stale authority from event/reason content and the core has no independent live provenance root. A synthetic/replayed stale event can therefore populate the same stale evidence structure. The exercise is correctly wired, but its terminal proof authority inherits the false-live provenance blocker above.

### 7. RUN_MANIFEST blob drift — CURRENT TREE PASS

No mismatch was found between the manifest-pinned blobs and current `main` for the checked product/proof/HUDANCHOR/schema files. Preflight code hashes every listed blob and fails closed on mismatch.

This check does not cure the semantic false-live/lifecycle defects because the defective current blobs are themselves exactly the pinned blobs.

## Gate result

The current tooling cannot receive the requested independent PASS because at least two required invariants are false:

1. synthetic/self-declared evidence can satisfy the proof core's live-provenance predicate and can construct an `IMPLEMENTATION_READY` terminal state;
2. same-slot enemy replacement and player respawn/object replacement lack lifecycle identity, allowing old authority to survive or a replacement to masquerade as a valid retarget.

A third proof-scoring defect allows player/enemy events from different epochs to jointly close a phase because cross-surface phase scoring does not require a shared epoch tuple.

## Residual blockers

A future implementation fix needs, at minimum:

- non-forgeable/session-rooted provenance for terminal live evidence rather than self-declared booleans/strings;
- lifecycle/generation identity for enemy slot occupants and player objects, propagated through head-fact capture, draw events and retarget scoring;
- explicit cross-surface epoch correlation when a phase claims both surfaces passed;
- stale-authority evidence tied to the actual bounded stop/reinstall transaction rather than reason text alone.

No Owner action is required for this repository defect. Browser/WOF should not be used to waive these repository-level false-pass paths.

## Final verdict

`BLOCKED — ALPHA V1 ANCHORED OVERLAYS ONE-SESSION LIVE PROOF TOOLING INDEPENDENT CROSS-CHECK — false-live provenance and lifecycle identity leaks can produce false proof gates / false IMPLEMENTATION_READY`

## STATUS
STAGE_STATUS: COMPLETE
VERDICT: BLOCKED
