# RESULT — Alpha V1 Anchored Overlays Bounded Dynamic Live Proof Prep

Stage: `ALPHA_V1_ANCHORED_OVERLAYS_BOUNDED_LIVE_PROOF_PREP_V1`

Status: **PASS — ALPHA V1 ANCHORED OVERLAYS BOUNDED LIVE PROOF PREP — ONE-SESSION DYNAMIC PROOF CONTRACT READY**

Browser/WOF launched by this stage: **NO**

Live proof executed: **NO**

Repository/synthetic evidence accepted as live proof: **NO**

## Deliverables

- `ONE_SESSION_DYNAMIC_PROOF_CONTRACT.md` — complete one-session operator/evidence/failure contract;
- `LIVE_PROOF_EVIDENCE_SCHEMA.json` — machine-readable terminal evidence schema for the future real Browser/WOF run.

## Current-head reconciliation

The preparation began from `fd850d27d32b90efa5a96b1456c6244a1ecdf7da`; during concurrent Alpha work, `main` advanced through the completed Player-Head Integration result. The current product facts used by this prep include:

- Enemy Target Head Labels Fresh QA V3: PASS/COMPLETE, with bounded live proof still required;
- Player-Head Danger Warning Production Integration result: COMPLETE and ready for fresh QA / bounded dynamic live proof;
- player production projection profile: still `UNPROVED` / disabled until bounded Browser/WOF proof;
- enemy production projection profile: still `UNPROVEN` / fail-closed until `IMPLEMENTATION_READY` proof.

No product file was modified by this stage.

## Reuse conclusion

One uninterrupted Browser/WOF session can reuse the existing HUDANCHOR machinery to prove the facts common to both anchored surfaces:

- native 384x224 projection plane;
- bounded camera identity and common X transform;
- selection of `Y-Z`, `Y+Z` or `Y`;
- direct-WebGL drawing-buffer/viewport mapping;
- resize/fullscreen/DPR remap and recovery;
- horizontal, depth, jump and camera-scroll coverage;
- optional P2/P3 common reuse when live.

The existing objective thresholds and exact Worker/Top loader command are retained rather than replaced with a new manual workflow.

## Dynamic proof matrix prepared

The future live run is explicitly required to attack and retain evidence for:

1. fast left/right movement;
2. depth/lane movement;
3. complete jump ascent -> apex -> descent -> landing;
4. rapid forward progression with stage/camera scrolling;
5. simultaneous player + camera movement;
6. real player-head danger warning follow;
7. moving enemy label follow;
8. live current-target retarget with old-label clearing;
9. multiple supported enemies where practical;
10. resize/fullscreen/drawing-buffer remap;
11. stale, identity, runtime/projection/drawing-buffer epoch, confidence, non-finite and bounds fail-closed windows.

Visible/repeatable drift, wrong identity, wrong target, stale old target/coordinate, or anchored rendering under known invalid authority are P0 failures.

## Important tooling finding

**The contract is ready, but the current committed HUDANCHOR proof tool cannot by itself execute the final dual-Alpha-surface end-to-end proof in one run.**

Current `parallel/HUDANCHOR_PROOF/**` proves the common transform by drawing its own `Y-Z / Y+Z / Y` candidate markers. It does not currently:

- observe/score actual Alpha player-head warning draws;
- observe/score actual Alpha enemy target-label draws;
- bind the current two `UNPROVED` production profiles in-session;
- convert the common proof result into the complete player production profile without an ambiguous Y-bias/head-clearance split;
- collect the enemy `enemyHeadOffsetsByType` live clearance facts.

Pretending otherwise would turn candidate/synthetic evidence into a false product live proof, so this prep fails closed on that distinction.

## Exact minimal follow-up

The next minimal stage is documented as:

- stageId: `ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING_V1`
- dedupKey: `alpha.v1.anchored-overlays.one-session-live-proof-tooling`

Its scope should be limited to extending the existing proof harness so the already-bounded common proof can hand its frozen live facts to dual Alpha surface observers/profile binders in the **same uninterrupted runtime**, collect enemy-type clearance, correlate live draw/no-draw decisions with identity/target/epoch/confidence/mapping authority, and emit one JSON conforming to `LIVE_PROOF_EVIDENCE_SCHEMA.json`.

It must not alter danger rules, target semantics, Transport authority, game AI/input, or invent constants. Owner interaction must remain normal gameplay plus the existing bounded proof controls.

## Stress/confidence history classification

The historical HUDANCHOR long-stress result found the invalid-confidence fail-open defect. That exact confidence defect was subsequently fixed and independently verified by Confidence Fail-Closed Fresh QA (12/12 adversarial matrix plus unchanged regressions). The current Alpha player helper independently implements strict finite/admissible confidence validation and fixed-HUD fallback. Therefore the old long-stress BLOCKED verdict is retained as history, not treated as current proof of live projection readiness.

Real Browser/WOF projection/non-drift remains unproven until the bounded live run actually occurs.

## Evidence semantics

The future terminal artifact may emit:

- `IMPLEMENTATION_READY` only from real bounded Browser/WOF evidence satisfying required observable gates;
- `FAILED_COMPONENT:<component>` for objective/visual failures;
- `INCOMPLETE_OBSERVATION:<component>` when a release-required live case was not exposed.

A repository PASS, synthetic fixture PASS, or the present prep PASS can never be promoted to `IMPLEMENTATION_READY`.

## Owner action

Owner action during this prep stage: **NO**.

Future live proof Owner actions are bounded to normal movement/gameplay, one calibration click, one resize/fullscreen transition, any normal gameplay needed to expose warning/retarget/moving enemies, one final visual classification when necessary, and returning the generated JSON. No manual address selection or coordinate transcription is part of the contract.

## Final verdict

**PASS — ALPHA V1 ANCHORED OVERLAYS BOUNDED LIVE PROOF PREP — ONE-SESSION DYNAMIC PROOF CONTRACT READY**
