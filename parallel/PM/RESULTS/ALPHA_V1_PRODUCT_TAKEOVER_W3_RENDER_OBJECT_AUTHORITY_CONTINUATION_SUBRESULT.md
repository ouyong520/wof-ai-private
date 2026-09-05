# Alpha V1 Product Takeover W3 — Deterministic Exact-Runtime Screen-Space Actor / Head Authority — CONTINUATION SUBRESULT

Status: **SUBCOMPLETE**

Existing logical authority continued (no new recovery / umbrella / equivalent claim):

- dedup key: `alpha.v1.live-acceptance.render-authority-sprite-coordinate-recovery-v2`
- stage: `ALPHA_V1_LIVE_ACCEPTANCE_RENDER_AUTHORITY_SPRITE_COORDINATE_RECOVERY_V2`
- claim token: `d8496ca1-62a2-44a6-85f5-b782a16af2c7`
- claim remains `ACTIVE`
- takeover dispatch baseline: `747c5b09d7a3d510a2df4bb8f9cb480ca8101da4`
- takeover dispatch commit observed before W3 implementation: `077cf8241f511a65fd2c18a269dc8c5c6209e12e`

No Collector, Unified Collector, Training Farm / 10训 source, runtime, claim, result or evidence was read, run, modified, tested or used.

## Verdict

W3 did **not** find repository/exact-runtime evidence sufficient to truthfully identify an already-proven CPS1 renderer/object table used by the displayed frame. The existing V2 structural heap scan only identifies CPS1-like 8-byte regions and therefore remains `UNVERIFIED_CANDIDATE_ONLY`; it is not promoted to production authority and no address/constant is guessed.

Because exact renderer/object source qualification still needs one live exact-World observation, W3 implemented the PM-authorized bounded automatic capture continuation and a fail-closed canonical anchor consumer. The Owner does not need to click a head/foot, calibrate, choose Y/Y-Z/Y+Z, open DevTools or locate JSON. Screenshot evidence is captured automatically and is explicitly verification-only, never per-frame production position authority.

No Owner action is requested by this subresult yet. Per takeover integration order, W1 permanent channel and W2 fixed maintained-production draw smoke should reach their gate first; when PM advances W3 live evidence, the same permanent Owner channel can run this bounded capture during normal play.

## Implementation

### 1. Exact-runtime bounded object-table timeline capture

`parallel/RENDER_AUTHORITY_V2/wof_render_authority_capture_worker.js`

Implementation commit: `5ee09a7230a50c775496c560b91ce200f7d4a7f6`

Changes:

- preserves exact World 921031 SHA binding and read-only safety;
- requires a distinct `rendererEpoch` in addition to runtime epoch / authority key;
- decodes candidate 8-byte `[x,y,tile,attr]` rows only for discovery evidence;
- records bounded per-frame candidate-table timelines instead of only the latest structural region;
- ties each timeline sample to P1 lifecycle/generation evidence and sample sequence;
- preserves every candidate's authority as `UNVERIFIED_CANDIDATE_ONLY`;
- explicitly reports `rendererSourceQualification=UNVERIFIED_CANDIDATE_ONLY`;
- explicitly refuses the canonical `384x224` contract until an exact renderer/object source is proven;
- remains `overlayEnabled=false`, `guessedConstantsAccepted=false`, `ramWrites=0`, `inputInjection=false`.

### 2. Runtime + renderer epoch launcher binding

`parallel/PYLAUNCH/wof_launcher/render_authority_capture.py`

Implementation commit: `2f3c8f85cd0bd93a75590356a62d868521f34172`

Changes:

- generates a fresh renderer epoch for each newly accepted exact runtime capture;
- validates World SHA + authority key + runtime epoch + renderer epoch on every remote status/result;
- rejects stale/mismatched runtime or renderer evidence;
- revokes renderer epoch with runtime authority instead of allowing stale anchor evidence to survive.

### 3. Normal-play-only automatic verification capture

`parallel/RENDER_AUTHORITY_V2/measurement_runner.py`

Implementation commit: `97cb9648913d4318e07d78680ab4a1568d3a410a`

Changes:

- automatically records bounded screenshots with `Page.captureScreenshot` while the Owner simply plays normally;
- each verification frame is linked to sample count, authority key, runtime epoch and renderer epoch;
- every screenshot row is marked `VERIFICATION_ONLY_NOT_POSITION_AUTHORITY`;
- on runtime replacement, old renderer epoch / verification generation is revoked and capture restarts cleanly;
- final evidence includes candidate timeline count + verification-frame index in the automatic result bundle;
- no click/calibration/coordinate-model selection/manual evidence collection is introduced.

### 4. Fail-closed deterministic canonical anchor consumer

`parallel/PYLAUNCH/wof_launcher/render_object_anchor.py`

Implementation commit: `1f634b668339b093961aab8d8b5ad31784ed825d`

Contract:

- canonical native surface is exactly `384x224`;
- accepts only a producer declaring a **proven** source kind of `exact-cps1-buffered-object` or `renderer-side-equivalent`;
- requires exact World SHA, authority key, runtime epoch and renderer epoch match;
- requires exactly one actor/generation association with `proven=true`, `ambiguous=false`, `candidateCount=1`;
- ambiguous/missing association suppresses output; there is no nearest-sprite fallback;
- unsafe frames suppress output;
- supports multi-part actor body union;
- only renderer-qualified body roles participate in body bounds;
- weapon/effect/projectile rows cannot silently enlarge body bounds;
- clips visible body geometry to the native surface;
- derives deterministic above-character anchor from final body bounds;
- stale authority or renderer epoch immediately suppresses output.

This consumer is intentionally not wired into the production HUD while the renderer source is unproven. Doing so would turn a discovery candidate into false production authority.

### 5. Focused tests

`parallel/RENDER_AUTHORITY_V2/selftest.mjs`

Test update commit: `4d170caf04e56ad3cf56ce6a1624d5506d0d811c`

Covers:

- renderer epoch required;
- object-row decode deterministic;
- candidate timeline captured;
- candidates remain unverified;
- canonical contract not falsely accepted;
- wrong/missing authority binding rejected;
- capture remains read-only and completes bounded evidence collection.

`parallel/RENDER_AUTHORITY_V2/render_object_anchor_selftest.py`

Test commit: `ae87cc2e596aa91216a2a339e772ae3c27633f33`

Covers:

- deterministic P1 multi-tile body union and above-character anchor;
- weapon/projectile exclusion;
- clipping;
- unproven renderer source suppression;
- ambiguous actor association suppression;
- stale runtime epoch suppression;
- stale renderer epoch suppression;
- explicit authority revoke suppression.

Implementation-owned focused execution from the exact submitted sources:

- `node parallel/RENDER_AUTHORITY_V2/selftest.mjs` — **PASS**
- `python parallel/RENDER_AUTHORITY_V2/render_object_anchor_selftest.py` — **PASS**
- Python syntax compilation for the modified/new W3 Python modules — **PASS**

No broad QA chain and no real WOF launch was performed for implementation questions that deterministic tests can answer.

## Feasibility proof A-F

### A. exact renderer/object coordinate source identified

**NOT YET PROVEN — precise remaining evidence dependency.**

Current repository runtime exposes exact World Worker/WASM memory and actor lifecycle state, but no existing symbol/export/pointer is proven to be the CPS1 buffered object list or renderer-side equivalent used by the displayed frame. Structural signatures are insufficient and remain untrusted.

### B. exact World 921031 + runtime generation binding

**PASS.**

Existing exact World SHA authority is retained. W3 additionally binds a fresh renderer epoch and rejects stale runtime/renderer generations.

### C. known actor renderer coordinate follows displayed movement

**NOT YET PROVEN — depends on A.**

W3 will not manufacture this proof from actor world X/Y/Z or screenshot-template tracking. The upgraded automatic capture now records time-aligned object-table candidates, actor lifecycle state and verification-only screenshots so the exact source can be qualified from one bounded normal-play run without manual calibration.

### D. ambiguous association suppresses

**PASS at canonical consumer boundary.**

Duplicate/non-unique actor association or `ambiguous=true` produces `SUPPRESSED`; no nearest-sprite guess exists.

### E. stale generation/renderer epoch suppresses

**PASS.**

Runtime/renderer mismatch is rejected by both capture validation and canonical anchor consumer; explicit revoke removes the binding.

### F. canonical native anchor deterministic

**PASS once a proven renderer/object frame is supplied.**

The contract is fixed at native `384x224`; deterministic body bounds / clipping / above-character anchor behavior is covered by focused tests. It cannot become READY while renderer source qualification is false.

## Precise continuation dependency

The remaining non-code evidence is exactly one bounded exact-World renderer/object qualification capture. It must establish which candidate/object structure is actually consumed by the displayed CPS1 frame and show at least one known actor's renderer coordinate changing consistently with displayed movement. Until that evidence exists:

- screenshot/template tracking must not be treated as steady-state production position authority;
- structural object candidates must not be treated as production authority;
- `render_object_anchor.py` remains fail-closed and is not connected to HUD production positioning;
- enemies are not expanded yet because P1 render authority is intentionally first.

When PM reaches the W3 live gate, Owner action is only normal play for a short bounded interval through the same permanent Alpha test channel. No new recovery, package-selection ritual, clicks, calibration, DevTools or manual JSON hunting is required.

## Terminal

**SUBCOMPLETE — W3 fail-closed canonical render/object anchor contract + bounded automatic exact-runtime evidence capture are integration-ready; existing V2 logical claim remains ACTIVE; exact displayed-frame renderer/object source qualification and P1 movement proof remain the one required live evidence dependency.**
