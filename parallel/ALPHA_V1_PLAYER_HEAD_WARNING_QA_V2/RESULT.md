# Alpha V1 Player-Head Danger Warning Fresh Independent QA V2 — RESULT

## Verdict

**PASS — ALPHA V1 PLAYER-HEAD DANGER WARNING FRESH QA V2 — STRICT warningSampleAt FIX VERIFIED / BOUNDED LIVE PROOF STILL REQUIRED**

This is fresh independent **repository-only QA**. Browser/WOF was not launched. No `product/alpha/**` file was modified by this QA stage.

## Dedup / ownership

- protocol: canonical dedup v2
- stageId: `ALPHA_V1_PLAYER_HEAD_WARNING_QA_V2`
- dedupKey / effectiveDedupKey: `alpha.v1.player-head-danger-warning.post-strict-sampleat-fix-fresh-qa`
- canonical claim: `parallel/PM/DEDUP_CLAIMS/alpha.v1.player-head-danger-warning.post-strict-sampleat-fix-fresh-qa.json`
- stage claim: `parallel/PM/STAGE_CLAIMS/ALPHA_V1_PLAYER_HEAD_WARNING_QA_V2.json`
- claimToken: `a9c0f7c8-4d6a-4f91-8ee4-7c93b20b5a13-6f22e8c91fd54f5f`
- startCommit: `a974621875150031e3c1dbc16f49aa502d2bd87b`

The canonical claim was create-only claimed first, then re-read from current `main` and the token/schema/key/stage/prompt/state were verified before the stage claim and substantive QA work.

## Current product evidence pinned at final drift check

| Path | Current Git blob |
|---|---|
| `product/alpha/wof_alpha_player_head_warning.js` | `af7f2359514dc6f86f74fac0c47858e8a6acf107` |
| `product/alpha/player_head_warning_regression.mjs` | `5cdda2c738d02e91f5b77a8c3a2b016abed14102` |
| `product/alpha/wof_alpha_player_head_projection.json` | `bbed0618b348961580ca805bb93e4d17525f0142` |
| `product/alpha/wof_alpha_real_worker.js` | `b7f4506fc90b681ede059df5ad3316e665c6f15e` |
| `product/alpha/wof_alpha_hud.js` | `50d944c451ac94b114e4f86441aeae8ad6b25c78` |
| `product/alpha/wof_alpha_loader.js` | `66aee09fc2dd009c2f295d2092f3129548605efb` |
| `product/alpha/wof_alpha_core.js` | `267a44190744b6848b0685712c3d5572627d3a8a` |

The player-head helper history was also checked: the strict-sampleAt implementation commit is `e1c40b4f6d100a9ed1f2649eae8fee7c610b6acd`; no later helper production change was present during this QA.

## Independent executable fixture

Durable fixture:

- `parallel/ALPHA_V1_PLAYER_HEAD_WARNING_QA_V2/independent_warning_sampleat_qa.mjs`
- Git blob: `4ed92983d399a879ec0db5a1ddef6dd3887c3ada`
- durable machine result: `parallel/ALPHA_V1_PLAYER_HEAD_WARNING_QA_V2/independent_qa_result.json`

Commands executed:

```text
node --check parallel/ALPHA_V1_PLAYER_HEAD_WARNING_QA_V2/independent_warning_sampleat_qa.mjs
node parallel/ALPHA_V1_PLAYER_HEAD_WARNING_QA_V2/independent_warning_sampleat_qa.mjs
```

Result: **74 / 74 PASS**.

The executable fixture used a byte-exact reconstruction of the current helper and current production projection blobs. The executed fixture itself was subsequently committed and re-read with the same Git blob hash.

### Strict `warningSampleAt` attacks

PASS for all required malformed classes:

- missing
- `null`
- numeric string
- boxed `Number`
- `valueOf`-coercible object
- `toString`-coercible object
- empty / numeric arrays
- booleans
- `NaN`
- `Infinity` / `-Infinity`
- additional adversarial `Date`, `bigint`, and function forms

Every invalid form produced `INVALID_WARNING_SAMPLE_TIME`, fixed-HUD routing, zero anchored items, and no usable anchored coordinate. Direct `resolveAnchor` verification also confirmed `xDb`, `yDb`, `bodyXDb`, and `bodyYDb` remain `null` on this failure.

Valid primitive finite numbers retained the existing anchored behavior, including primitive `0`.

## Retarget / freshness / lifecycle regression

PASS:

- P1 -> P2 -> P3 retarget sequence
- a player spatial sample older than the warning sample cannot authorize the new warning
- a projection sample older than the warning sample cannot authorize the new warning
- newer unrelated semantic/drawing-buffer activity does not repair an old player/projection freshness barrier
- simultaneous P1/P2/P3 warnings do not cross-use player coordinates
- death (`present:false`) fails closed
- disappearance / missing player state fails closed
- respawn uses the fresh position and does not retain the old anchor
- same-slot replacement uses the replacement object's fresh coordinates
- player freshness boundary: exactly 80 ms accepted, >80 ms fails closed
- projection freshness boundary: exactly 80 ms accepted, >80 ms fails closed
- `holdMs=0`, `smoothing=false`

Static production inspection confirms the worker player-spatial publish cadence remains **20 ms**, while the helper player/projection freshness ceiling remains **80 ms**.

## Epoch / confidence / nonfinite / bounds

PASS fail-closed attacks for:

- missing, malformed, coercible, and mismatched warning/player/projection/drawing-buffer epochs
- mismatched `projectionEpoch`
- malformed/nonfinite/out-of-range confidence
- nonfinite player XYZ and projection state
- body/anchor projection outside bounded native validation area
- malformed and stale drawing-buffer state
- left/right edge draw-rect clamping

## Resize / fullscreen / DPR

PASS:

- resize recomputes the drawing-buffer mapping and anchor instead of retaining an old coordinate
- fullscreen changes the mapping key and recomputes the anchor
- DPR-like drawing-buffer/content-rect scaling recomputes current coordinates without stale-coordinate reuse

## Fixed-HUD fallback

PASS. Any anchoring failure remains in `plan.fixed`; the original warning payload is retained for fixed-HUD rendering. The HUD passes semantic `lastMsg.sampleAt` into the helper as `warningSampleAt`, and consumes `plan.fixed` through the fixed warning path.

## Supportive committed regression replay

Commands executed:

```text
node --check product/alpha/player_head_warning_regression.mjs
node product/alpha/player_head_warning_regression.mjs
```

Result: **22 / 22 PASS** (`SYNTHETIC_PLAYER_HEAD_WARNING_ONLY_NOT_BROWSER_PROOF`).

Durable replay metadata: `parallel/ALPHA_V1_PLAYER_HEAD_WARNING_QA_V2/supportive_regression_replay.json`.

Execution-boundary note: a native private-repository checkout was not available in the local runner. The helper, committed regression, and projection used for the replay were byte-exact to the current Git blobs. The committed regression's worker/HUD/loader regex-only integration checks were supplied with minimal mirrors of the exact current source excerpts, and those same required facts were independently re-verified against current GitHub source. This replay is supportive evidence; the 74-case independent fixture is the primary fresh QA evidence.

## Frozen semantics / authority regression

No evidence of scope drift was found:

- strict-sampleAt implementation commit changed only the player-head warning helper, not core danger rules, worker transport logic, or HUD authority semantics
- `target7E` mapping in core remains `0 -> P1`, `4 -> P2`, `8 -> P3`
- current production danger-rule selection remains the existing frozen production rules
- worker safety/transport remains read-only/no-input-injection and HUD inbound messages remain filtered by the existing transport/session authority
- this QA made **no `product/alpha/**` changes**

## Projection / live-proof boundary

The production player-head projection remains:

- `status: UNPROVED`
- `activation: DISABLED_UNTIL_BOUNDED_BROWSER_WOF_PROOF`

Therefore this repository QA PASS does **not** constitute Browser/WOF non-drift proof and does not release the anchored production path. The bounded Browser/WOF proof gate remains required.

## Acceptance/current-HEAD evidence classification

**YES — a separate current-HEAD evidence rebinding / selector successor is required in addition to the still-open bounded live-proof gate.**

Reason: the current Acceptance preflight player-head selector consumes the original `ALPHA_V1_PLAYER_HEAD_WARNING_PRODUCTION_INTEGRATION_V1` stage claim and expects machine-readable product blob pins. That original integration claim does not contain those pins, and the helper/regression blobs were subsequently changed by the strict-sampleAt fix. This repository QA verifies the fix but is not authorized to rewrite Acceptance selector/evidence plumbing.

This downstream admission issue does **not** invalidate this QA verdict; it prevents treating the repository QA PASS as release admission by itself.

## Owner action

**NO.** No product decision is required from Owner for this QA result. Remaining release work is an execution/gate matter: bounded Browser/WOF proof plus the current-HEAD evidence rebinding/selector successor described above.

---

**PASS — ALPHA V1 PLAYER-HEAD DANGER WARNING FRESH QA V2 — STRICT warningSampleAt FIX VERIFIED / BOUNDED LIVE PROOF STILL REQUIRED**
