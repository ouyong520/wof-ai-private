# Alpha V1.0.0 Current-HEAD Release Gate Preflight Recovery V2 — RESULT

Stage: `ALPHA_V1_0_0_CURRENT_HEAD_RELEASE_GATE_PREFLIGHT_RECOVERY_V2`

Status: **PASS — ALPHA V1.0.0 CURRENT-HEAD RELEASE PREFLIGHT RECOVERY V2 — REPOSITORY GATES RECONCILED / RELEASE REMAINS FAIL-CLOSED ON LISTED OPEN GATES**

Release state: **NOT RELEASED**

Owner action now: **NO** — the one intrinsically Owner-only Browser/WOF proof is deferred until the repository/tooling/package prerequisites below are green.

Browser/WOF launched by this stage: **NO**.

## Canonical recovery ownership

This PM-authorized recovery used canonical dedup v2 without touching the stopped historical claim.

- dedupKey / effectiveDedupKey: `alpha.v1.0.0.current-head-release-gate-preflight-recovery-v2`
- canonical claim: `parallel/PM/DEDUP_CLAIMS/alpha.v1.0.0.current-head-release-gate-preflight-recovery-v2.json`
- stage claim: `parallel/PM/STAGE_CLAIMS/ALPHA_V1_0_0_CURRENT_HEAD_RELEASE_GATE_PREFLIGHT_RECOVERY_V2.json`
- claim token: `f67fc3916f47733c03c179706bc043310272c8d0c2d98a3f`
- claim-start main: `8a6833995c21adb07be64541a2f6de8b65c341f1`
- final audited pre-result main: `0a98a4d468ab0924168d5d57a594b61273dbc52b`

The historical stopped claim `parallel/PM/DEDUP_CLAIMS/alpha.v1.0.0.current-head-release-gate-preflight.json` remains intact and ACTIVE as historical evidence; this recovery does not overwrite, delete, reuse or steal it.

Main advanced during the reconciliation through this recovery's own claim commits, isolated Training Farm R0.1 work, and the newly acquired One-Session Live-Proof Tooling Recovery V2 claim. None of that changed the release-critical player/enemy projection/helper blobs checked below.

## Current release-critical blob drift check

Current `main` at the final audit still has:

- `product/alpha/wof_alpha_player_head_warning.js` -> `af7f2359514dc6f86f74fac0c47858e8a6acf107`
- `product/alpha/wof_alpha_player_head_projection.json` -> `bbed0618b348961580ca805bb93e4d17525f0142` and still `status=UNPROVED`, `activation=DISABLED_UNTIL_BOUNDED_BROWSER_WOF_PROOF`
- `product/alpha/wof_alpha_enemy_target_labels.js` -> `e6e1260559f735b85ce6f69e87803369f125b2de`
- `product/alpha/wof_alpha_enemy_head_projection.json` -> `8de57739818503a0e14702d2fa0bb4eba58228d2` and still `verdict=UNPROVEN`, `status=FAIL_CLOSED_UNTIL_IMPLEMENTATION_READY_PROOF`

These pins equal the current helper/profile contracts covered by the latest player-head QA V2 and enemy-label QA V3. The repository therefore has no basis to reopen those ordinary QA lanes, but it equally has no basis to claim real projection/non-drift proof.

## Gate reconciliation

| Gate | Classification | Durable current-HEAD disposition |
|---|---|---|
| Player-head production integration + strict `warningSampleAt` fix + Fresh QA V2 | **CLOSED** | Production integration completed; strict primitive-finite `warningSampleAt` fix completed; Fresh QA V2 PASS with 74/74 independent cases and 22/22 supportive regression. Current helper/profile blobs remain pinned. Real bounded projection proof is explicitly outside this CLOSED repository QA gate. |
| Enemy-head current-target `1P / 2P / 3P` Fresh QA V3 | **CLOSED** | V3 PASS/COMPLETE cleared the strict-target and cross-epoch drawing-buffer defects, including retarget/clear, stale, bounds and remap regressions. Current helper/profile blobs remain pinned. Real Browser/WOF projection remains outside this CLOSED repository QA gate. |
| Dual-overlay bounded live-proof prep / one-session contract | **CLOSED** | `parallel/ALPHA_V1_ANCHORED_OVERLAYS_LIVE_PROOF_PREP/RESULT.md` is PASS: one-session dynamic proof contract/schema are ready and explicitly state that the old HUDANCHOR proof tool alone is insufficient for final dual-Alpha-surface proof. |
| One-Session Live-Proof Tooling Recovery V2 | **ACTIVE-PENDING** | Recovery V2 is legitimately owned by another worker. Canonical and stage claims are both ACTIVE on current main, start commit `f4f6a7f...`. This preflight must not steal or duplicate the implementation. |
| Fresh repository QA of the recovered one-session tooling | **ACTIVE-PENDING** | Not startable until the tooling recovery produces its durable COMPLETE/RESULT. Required as the immediate successor before the bounded live run; do not substitute synthetic tooling tests for live proof. |
| Real Browser/WOF dual-overlay dynamic non-drift proof / bounded live acceptance | **OWNER ACTION REQUIRED** | No durable real Browser/WOF proof exists. Both production profiles are still UNPROVED/fail-closed. One bounded future session must prove player warning + enemy `1P/2P/3P`, fast L/R, depth, jump, rapid progress/whole-screen scroll, retarget old-label clear, resize/fullscreen/DPR, and invalid-authority no-draw/fixed fallback. Player head-clearance/Y split and enemy type head offsets must come from live observation, never guesses. **Do not request Owner action yet while repository prerequisites remain open.** |
| V1.0.0 player-test release prep | **CLOSED** | `parallel/ALPHA_V1_0_0_USER_TEST_RELEASE_PREP/RESULT.md` PASS. Chinese first-test guide, bug template, release notes and finalization checklist are prepared. The result explicitly remains `NOT RELEASED`. |
| Transport True 5h Endurance Recovery V2 | **ACTIVE-PENDING** | Stage claim remains ACTIVE. Workflow run `33577350728`, run head `de2c86fb...`, has durable repository checkpoints `segment-0` through `segment-8`; latest segment 8 is PASS with `actualElapsedMs=1500055`, zero failures and frozen 67/67 control. Nine 25-minute segments are present, but `parallel/ALPHA_TRANSPORT_TRUE_ENDURANCE_V2/RESULT.md` does not yet exist and the claim is not COMPLETE. This is **not** a 5h PASS. Success still requires all intended 13 checkpoints, genuine >=5h executor/wall-clock evidence, final aggregate/RESULT, unchanged exact SUT pins and durable claim closure. |
| Owner OneClick Current-HEAD Release Refresh V3 / final package snapshot | **ACTIVE-PENDING** | V3 prompt exists and states the committed package manifest is stale against release-consumed runtime. No V3 stage claim is present. It must be generated deterministically from one settled immutable release candidate and pass package/Windows/UTF-8/integrity QA; do not refresh early merely to make hashes current. |
| Acceptance gate-policy reconciliation | **CLOSED** | `ALPHA_ACCEPTANCE_SUPERSEDING_GATE_RECONCILIATION_V2` is PASS: successor-aware repo preflight policy is current and fail-closed rather than mechanically consuming historical BLOCKED results. |
| Final current-HEAD acceptance/release admission | **ACTIVE-PENDING** | Not closed by the policy PASS. Player-head Fresh QA V2 records that a current-head player evidence rebinding/selector successor is still required; later open tooling/5h/package gates also prevent admission. The final bounded Browser/WOF acceptance remains a separate required evidence event. |
| Release Freeze Current-HEAD Recheck V2 | **ACTIVE-PENDING** | The V2 start prompt exists, but no stage claim/result exists. This is correct while upstream release-owned gates are moving. The historical Release Freeze BLOCKED result is preserved as history and is not mechanically reused against current HEAD. |
| `V1.0.0 PLAYER TEST RELEASE` admission | **BLOCKED** | Fail-closed release admission only: mandatory real dual-overlay non-drift evidence is absent and tooling/5h/package/final acceptance/freeze remain open. This is not evidence of a newly discovered production defect. Release state must remain **NOT RELEASED**. |

### Current BLOCKED defect inventory

No new current implementation P0/P1 defect was established by this repository reconciliation. The `BLOCKED` classification above applies to release admission because mandatory evidence/gates are incomplete, not because this PM lane found a fresh product defect.

## Player-head evidence

Durable strict fix result:

- `parallel/ALPHA_V1_PLAYER_HEAD_WARNING_STRICT_SAMPLEAT_FIX/RESULT.md`
- result commit: `3550480392e18f2d38fe0e87cc9d4f587f7a06e8`
- implementation commit: `e1c40b4f6d100a9ed1f2649eae8fee7c610b6acd`
- verdict: `COMPLETE — ALPHA V1 PLAYER-HEAD DANGER WARNING STRICT warningSampleAt FIX — READY FOR FRESH QA V2`

Durable Fresh QA V2:

- `parallel/ALPHA_V1_PLAYER_HEAD_WARNING_QA_V2/RESULT.md`
- result commit: `04ef0bc477fe71c250c6647360f23343b0bf56cd`
- verdict: `PASS — ALPHA V1 PLAYER-HEAD DANGER WARNING FRESH QA V2 — STRICT warningSampleAt FIX VERIFIED / BOUNDED LIVE PROOF STILL REQUIRED`
- canonical/stage claims subsequently closed COMPLETE.

The earlier production integration also has durable COMPLETE result commit `ca12c344d6d67c079356deaa52d475d0880d3413`; the later strict fix + QA V2 supersede its helper-specific freshness evidence without changing danger rules or Transport authority.

## Enemy-label evidence

Latest durable current-product repository QA:

- `parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS_QA_V3/RESULT.md`
- result commit: `c99d50d24f4d487986b8991447e01d51180e22c5`
- verdict: `PASS — ALPHA V1 ENEMY TARGET HEAD LABELS FRESH QA V3 — EPOCH FIX VERIFIED / BOUNDED LIVE PROOF STILL REQUIRED`
- independent matrix: 23/23 PASS
- canonical/stage claims subsequently closed COMPLETE.

The older QA/V2 blockers remain immutable historical evidence but are superseded for current repository decision by V3 and must not be mechanically reopened.

## True 5h durable evidence boundary

Only GitHub-durable evidence is counted here.

Current durable facts:

- stage: `ALPHA_TRANSPORT_TRUE_5H_ENDURANCE_RECOVERY_V2`
- stage claim: ACTIVE
- workflow run: `33577350728`
- run head: `de2c86fb3fe528907aad08cd45d8944e3054f680`
- intended execution: 13 sequential non-overlapping segments x 1,500,000 ms = 19,500,000 ms; no V1 elapsed reuse; no idle padding
- durable repository checkpoints currently present: `segment-0` through `segment-8`
- latest durable checkpoint: segment 8 PASS, `actualElapsedMs=1500055`, `failureCount=0`, frozen control 67/67 PASS
- final `RESULT.md`: absent
- final stage claim state: not COMPLETE

Therefore the only valid classification is **ACTIVE-PENDING**. Do not aggregate the historical V1 25-minute evidence into V2 and do not infer a final PASS from an Actions UI status or from elapsed wall time outside GitHub durable checkpoint/result evidence.

## Acceptance / freeze interpretation

The latest Acceptance successor-policy reconciliation is a CLOSED policy gate, not live acceptance. It correctly preserves historical failures while selecting valid current successors. Since then, the previously open player-head integration was completed, the strict `warningSampleAt` defect was fixed, and Fresh QA V2 passed; however that QA also identified the need for current player evidence rebinding/selector consumption. No later durable final admission result closes the combined release gate.

Release Freeze Current-HEAD Recheck V2 is intentionally not started yet. Its prompt requires current package, current acceptance/preflight and the true 5h robustness gate (while policy requires it) before a freeze-ready verdict. Starting it now would only create avoidable churn.

## Shortest path to `V1.0.0 PLAYER TEST RELEASE`

Two repository branches can advance in parallel, then join into one bounded Owner run:

1. **Tooling branch:** finish the already ACTIVE One-Session Live-Proof Tooling Recovery V2 -> durable COMPLETE/RESULT -> run one fresh repository QA successor on that recovered tooling.
2. **Robustness branch, in parallel:** allow the already-running True 5h V2 workflow to finish its remaining intended segments -> require durable `final-summary.json` + `RESULT.md` -> require stage claim COMPLETE. No non-GitHub elapsed time counts.
3. Once release-consumed runtime/tooling is settled, execute **Owner OneClick Current-HEAD Release Refresh V3** from one immutable candidate and close its Windows/integrity/UTF-8 package QA. Do not package a moving snapshot.
4. Run the final current-HEAD repository acceptance/preflight successor so it consumes the current player-head QA V2 evidence, enemy-label QA V3, completed 5h evidence and current OneClick package. Any required player evidence selector rebinding is handled here; do not reopen ordinary player/enemy implementation QA.
5. **One bounded Owner Browser/WOF session** on that exact candidate: use the recovered/QA'd one-session harness to produce the real dual-overlay dynamic non-drift evidence and bounded acceptance evidence together. This is the only intrinsically Owner-action step: normal gameplay plus the already bounded proof controls, not DevTools/manual constants/input injection.
6. Run **Release Freeze Current-HEAD Recheck V2** against the exact same release snapshot and durable live artifact. If it is freeze-ready and no release-consumed blob drifted, regenerate only if the package snapshot actually needs rebinding.
7. Only after the release freeze/acceptance gates close may the state change from `NOT RELEASED` to **`V1.0.0 PLAYER TEST RELEASE`** and the already-prepared player-facing docs/package be delivered.

There is no justified filler stage between these steps. In particular, do not start another player-head ordinary QA, another enemy-label ordinary QA, another speculative projection-constant task, or a second Browser/WOF session unless the first bounded live artifact objectively reports a failed/incomplete component.

## Scope / safety

This reconciliation changed no `product/alpha/**` file, no danger rule, no `target7E` semantics, no Safe Transport authority, no HUDANCHOR implementation, no input/AI/RAM behavior, and launched no Browser/WOF process.

## Final verdict

**PASS — ALPHA V1.0.0 CURRENT-HEAD RELEASE PREFLIGHT RECOVERY V2 — REPOSITORY GATES RECONCILED / RELEASE REMAINS FAIL-CLOSED ON LISTED OPEN GATES**

**V1.0.0 remains NOT RELEASED.**
