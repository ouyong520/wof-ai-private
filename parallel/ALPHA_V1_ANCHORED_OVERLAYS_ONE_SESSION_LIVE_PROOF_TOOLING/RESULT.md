# Alpha V1 Anchored Overlays One-Session Live-Proof Tooling Proof-Authority Fix V1 — RESULT

Status: **COMPLETE — FALSE-PROOF PATHS CLOSED / READY FOR FRESH QA**

Stage: `ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING_PROOF_AUTHORITY_FIX_V1`

Canonical key: `alpha.v1.anchored-overlays.one-session-live-proof-tooling-proof-authority-fix-v1`

Claim token: `9e5f505b-9526-49ba-ad2e-976d12fc2249-f42263e71b13dab610c02dba64a25bed`

## Trigger closed

The independent cross-check blocker was proof-local and has been fixed without changing `product/alpha/**`, danger rules, raw target semantics, Transport authority, gameplay input/AI, or RAM-write policy.

The proof tooling no longer permits declarative/public live fields to self-authorize `IMPLEMENTATION_READY` or proof-only profile binding. Live authority is rooted in a one-session Top/Worker challenge-response: the Worker signs the proof-session challenge with a non-extractable ECDSA P-256 key and binds the witness to the current formal adapter authority tuple. The Core converts a verified witness into an internal branded capability that serialized/replayed repository evidence cannot mint.

## False-proof paths closed

1. **Synthetic masquerade / false `IMPLEMENTATION_READY`** — Session terminal readiness requires the verified live Worker witness. Candidate binders require the internal branded live capability, not caller-provided strings/booleans.
2. **Cross-surface epoch scoring** — both-surface phase closure requires one compatible normalized authority tuple: proof session, runtime/projection/drawing-buffer epochs, drawing-buffer projection epoch, and normalized live mapping authority. Player epoch A + enemy epoch B cannot jointly close a phase.
3. **Enemy lifecycle / same-slot replacement** — proof-local occupant generations are emitted from observable slot presence/type/time/spatial continuity. `liveRetarget` requires one stable occupant generation and continuity; replacement/reappearance cannot score as retarget.
4. **Player lifecycle / respawn calibration** — P1/P2/P3 samples carry proof-local lifecycle generations. P1 body/reference calibration is accepted only when the common head-click timestamp resolves to the same stable P1 lifecycle generation; respawn/replacement requires recapture.
5. **Enemy head-offset ambiguity** — a type offset requires repeated stable captures from one current lifecycle-safe occupant; overlap/replacement or multiple lifecycle identities for the same candidate type fail closed.
6. **Stale-authority exercise** — stale closure is transaction-rooted. The real stop/reinstall path creates a random transaction id and Worker-signed bounded transaction witness. `STALE_*` text/events/timestamps alone cannot satisfy the gate.

## Safety preserved / strengthened

- primitive finite `warningSampleAt` boundary preserved;
- strict raw target `0/4/8` boundary preserved;
- player/marker/projection/drawing-buffer freshness remains fail-closed;
- runtime/projection/drawing-buffer cross-epoch fail-closed is stronger;
- invalid confidence/non-finite/bounds remain fail-closed;
- player fixed-HUD fallback and enemy suppression/no-draw remain required;
- resize/fullscreen/DPR mapping authority remains part of scoring;
- proof Worker remains read-only: `ramWrites=0`;
- `inputInjection=false`;
- no Worker replacement / Blob rewrite;
- repository/synthetic evidence cannot activate production projection profiles.

## Exact implementation and manifest pins

Implementation commit: `e6042741486ed6aae215e282c2f700fd84167811`

Manifest commit: `f2855ed2c554e41b0b8ef6cf2c03a60233c44b64`

Repository regression evidence commit: `b943c58504509e4bc06a45014e7e27e4e75e5309`

Current proof runtime blobs pinned by `RUN_MANIFEST.json`:

- `proof_core.js` — `6fa5b5178dd0dedcad2afe7e53c6cdda98c8a701`
- `wof_alpha_v1_dual_live_proof_top.js` — `e0e686cafc3463ce6041d83c5e0fe1030f7eb444`
- `wof_alpha_v1_dual_live_proof_worker.js` — `2b75092fee63cecafb51e108aa2af8b3d83cc696`
- `wof_alpha_v1_dual_live_proof.js` — `e71a802c8d150cf727345c51c4786512a82abb97`
- `proof_authority_regression.mjs` — `e3697ab88cb36922e717b7a85044e0bfca72a444`
- `tooling_regression.mjs` — `cfd3d15a9adc6d7a532d36026494a76e2c41c4d0`

The selected Alpha product and HUDANCHOR/evidence-schema blobs remain exact-pinned. Production player/enemy projection profiles remain the current unproved/disabled blobs; this stage did not activate or edit either profile.

## Deterministic repository QA

Primary independent adversarial regression:

`node parallel/ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING/proof_authority_regression.mjs`

Result: **PASS — 10 / 10**.

It independently attacks forged public live provenance, forged terminal state, cross-epoch joint scoring, same-slot replacement, valid same-occupant retarget, player respawn between head/body calibration, ambiguous enemy replacement/head offsets, synthetic stale events, strict target/epoch failures, and repository capability forgery.

Supportive Recovery regression:

`node parallel/ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING/tooling_regression.mjs`

Result: **PASS — 19 / 19**.

Core/Top/Worker/loader syntax checks also PASS. `REPOSITORY_TEST_RESULT.json` is explicitly `SYNTHETIC_REPOSITORY_QA_ONLY_NOT_BROWSER_WOF_LIVE_PROOF`; it is repository evidence only and cannot satisfy the real live proof gate.

## Scope / live boundary

Browser/WOF: **NOT RUN by this stage**.

`product/alpha/**`: **NOT MODIFIED by the implementation fix**.

Production profiles: **NOT ACTIVATED; remain UNPROVED**.

This COMPLETE verdict means the repository-level false-proof implementation paths identified by the cross-check are closed and the tooling is ready for a fresh independent QA. It does **not** claim the future Browser/WOF dual-overlay live proof has already run or passed.

Terminal stage text:

`COMPLETE — ALPHA V1 ANCHORED OVERLAYS ONE-SESSION LIVE PROOF TOOLING PROOF-AUTHORITY FIX V1 — FALSE-PROOF PATHS CLOSED / READY FOR FRESH QA`
