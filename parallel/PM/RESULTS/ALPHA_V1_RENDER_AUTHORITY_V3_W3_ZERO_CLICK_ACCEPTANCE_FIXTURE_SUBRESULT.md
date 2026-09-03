# Alpha V3 W3 — Zero-Click Acceptance Fixture / Package-Readiness SUBRESULT

## Verdict

**SUBCOMPLETE — W3 deterministic acceptance fixture and package-readiness gate are ready for V3 umbrella integration.**

W3 changed only subworkstream claims plus tests/fixtures/this SUBRESULT. W3 did **not** edit production runtime, package manifest/generator, immutable package content, or the V3 umbrella claim, and did not launch Browser/WOF.

## Authority

- stageId: `ALPHA_V1_RENDER_AUTHORITY_V3_W3_ZERO_CLICK_ACCEPTANCE_FIXTURE`
- dedupKey: `alpha.v1.render-authority-v3.w3-zero-click-acceptance-fixture`
- claimToken: `w3-4e9d7c2a-0b31-4a66-96f8-01a3e5d9247b`
- startCommit: `78335c095af09f20af05e13e959d445d5c0017e5`
- canonical claim: `parallel/PM/DEDUP_CLAIMS/alpha.v1.render-authority-v3.w3-zero-click-acceptance-fixture.json`
- stage claim: `parallel/PM/STAGE_CLAIMS/ALPHA_V1_RENDER_AUTHORITY_V3_W3_ZERO_CLICK_ACCEPTANCE_FIXTURE.json`

## W3 artifacts

1. Deterministic owner-path fixture:
   - `parallel/PYLAUNCH/tests/fixtures/alpha_v3_w3_zero_click_acceptance.json`
   - final W3 fixture commit: `dff737ff222b79e88fb92d02a6af61d9c82b5d3a`
   - final blob: `c35fa1a6c5ec15bb07803a790ebeff418d42902e`

2. Focused acceptance/package-readiness gate:
   - `parallel/PYLAUNCH/tests/test_zero_click_acceptance_fixture_w3.py`
   - final W3 gate commit: `622f1fdab260957b6c51dd8fcc19ce2752e59ee6`
   - final blob: `358a7d84852503171c6e2664db706dd099fff5af`

The gate can be used as a cheap self-check or against a generated candidate:

```text
python parallel/PYLAUNCH/tests/test_zero_click_acceptance_fixture_w3.py
python parallel/PYLAUNCH/tests/test_zero_click_acceptance_fixture_w3.py --candidate-root . --manifest parallel/OWNER_ONECLICK/package_manifest.json --immutable parallel/OWNER_ONECLICK_IMMUTABLE/<candidate>/IMMUTABLE_PACKAGE.json
```

The second form intentionally requires a local Git checkout because it verifies each critical manifest `gitBlobSha` against `<sourceCommit>:<path>`.

## Deterministic acceptance coverage

The fixture/gate proves the required path-level invariants without Owner input:

| Contract | W3 deterministic oracle |
| --- | --- |
| automatic zero-click before click fallback | any click arming before an automatic acquisition attempt is rejected |
| safe unique -> `HEAD_TRACKING`, `ownerClickCount=0` | `safe_unique_zero_click` requires P1 binding, visible marker, no click arming |
| ambiguity cannot silently bind wrong actor/head | `ambiguous_auto_fails_closed` and `wrong_actor_candidate_rejected` forbid `HEAD_TRACKING`, actor binding, or visible marker |
| fallback only after automatic failure, max one click | `auto_failure_then_single_click` requires automatic failure first, exactly one arm, final click count 1 |
| tray/status remains visible | every path step requires `trayVisible=true` |
| correct/reused WOF, never blank browser | every scenario requires WOF intent, accepted reuse/configured/restore path, `aboutBlank=false`; existing V3 browser test already covers last-session restore without `about:blank` and was reused rather than rerun |
| confidence loss hides; recovery restores | `confidence_loss_hide_and_recover` requires marker `true -> false -> true` without another Owner click |
| runtime/lifecycle/layout change revokes stale authority | three invalidation scenarios require generation/layout change, `authorityRevoked=true`, marker hidden |
| final package contains corrected runtime | candidate gate requires critical runtime selection, current source-commit pins, per-file blob pins, a zero-click-first contract, and at least one corrected integration blob relative to the known pre-zero-click baseline |
| read-only safety | fixture + manifest/immutable gate require `readOnly=true`, `ramWrites=0`, `inputInjection=false`; owner click maximum may not exceed 1 |

## Focused self-check

Only W3-owned deterministic logic was exercised; no unrelated historical PASS suite was rerun.

Final focused replay: **6/6 checks PASS**:

- committed fixture scenarios self-consistent;
- click-before-auto mutation rejected;
- ambiguous wrong-P1 binding mutation rejected;
- marker-visible-during-loss mutation rejected;
- structured corrected zero-click package contract accepted;
- pre-integration one-click/stale-runtime package shape rejected.

An earlier focused run exposed one W3 fixture defect only: the three invalidation start states omitted `boundActor=P1`. W3 fixed the fixture and reran the focused checks successfully. No production change was made for that issue.

## Concurrent V3 integration observed, but not authored by W3

During W3, the umbrella worker advanced production independently:

- commit `2ae9757ab69a6aa595d8c581afe7c534fa8bfd2c` changed `head_visual_tracker.py` to zero-click-first auto seed / fail-closed / revoke behavior;
- current `head_visual_tracker.py` blob observed by W3: `061925e2aef9a45efbc3bc09f15d6371953c0433`, different from the pre-zero-click package pin `c58b2805b8dc5ac248702ef69bcfb998d6cd10dc`;
- commit `663b0cde64de344e84d605706c7cf89f3722871d` updated `parallel/OWNER_ONECLICK/refresh_manifest.py` to emit structured zero-click-first package metadata including normal expected clicks 0 and automatic-before-fallback.

W3 deliberately accepts either an inline umbrella implementation or a separately selected W2 zero-click module; it does not require a particular production filename.

## Current package-readiness state at W3 handoff

The checked-in `parallel/OWNER_ONECLICK/package_manifest.json` is still the older candidate `2026.09.03.renderauthv3.7f8f1ff5b7a5`. It still says `camera prepare -> one P1 head click maximum` and pins the old `head_visual_tracker.py` blob `c58b2805b8dc5ac248702ef69bcfb998d6cd10dc` plus old `measurement_runner.py` blob `1f7292345529a8d5ee2b948f16d9adb030abf20e`.

Therefore **that existing manifest is correctly NOT READY under W3**. This is not a W3 blocker: package publication/repin belongs to the umbrella worker. The umbrella worker should generate the successor manifest/package from the corrected source commit and run W3 candidate mode before publication/closeout. W3 must not publish that package itself.

## Exact umbrella handoff

Before V3 package publication, W1 should:

1. integrate/settle the final zero-click production candidate (including any accepted W2 output);
2. run its one coherent focused V3 regression;
3. generate/repin `package_manifest.json` from the final corrected source commit;
4. run W3 candidate mode against the generated manifest and immutable descriptor;
5. require `W3 CANDIDATE READY` before final immutable package/RESULT closeout.

A failure from W3 candidate mode is package/integration evidence, not a request for another QA chain.

## Remaining live-only assertions

After W1 has a W3-green corrected immutable package, the only facts that still intrinsically require the bounded Owner/real-WOF run are:

1. Windows tray/status is actually visible while the real browser/WOF owns focus and remains visible through normal play.
2. Menu 6 actually reconnects to/reuses or opens the intended WOF flow on the Owner machine, rather than presenting an empty browser.
3. On exact World 921031 imagery, when the automatic P1 identity/head candidate is safely unique, real status reaches `HEAD_TRACKING` with `ownerClickCount=0`; when it is not safe/unique, no wrong marker appears and only then may the one-click fallback surface.
4. If real visual confidence is lost during the bounded run, the on-screen marker actually disappears and reappears after recovery; runtime/room/layout changes must not leave a stale marker visible.

No DevTools, manual calibration, RAM write, or input injection is part of those assertions.

## Safety / scope integrity

- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`
- W3 production edits: **0**
- W3 package publications: **0**
- W3 umbrella-claim mutations: **0**
- unrelated historical PASS reruns: **0**

## Terminal

`SUBCOMPLETE — ALPHA V3 W3 ZERO-CLICK ACCEPTANCE FIXTURE / PACKAGE-READINESS GATE READY — HAND OFF TO V3 UMBRELLA WORKER`
