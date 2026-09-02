# Alpha V1 Enemy Target Head Labels — Implementation Result

Stage: `ALPHA_ENEMY_TARGET_HEAD_LABELS_V1`

Status: **COMPLETE — ALPHA V1 ENEMY TARGET HEAD LABELS IMPLEMENTED — READY FOR FRESH QA / BOUNDED LIVE PROOF**

## HEAD / scope

- exact stage start HEAD: `3fb7862a59f9203d3f5d8f7f45756d366ec7b148`
- final implementation HEAD before result/claim-only closure commits: `51a2637356033894794ace44055462cad52c923e`
- implementation writes were limited to `product/alpha/**`; result/claim writes remain inside the prompt's allowed evidence paths.
- unrelated concurrent `main` changes between the start HEAD and implementation HEAD are not part of this stage.

## Changed product blobs

| Path | Blob |
|---|---|
| `product/alpha/wof_alpha_enemy_target_labels.js` | `3f6f4410376756e6935a4236e40e76574b289169` |
| `product/alpha/wof_alpha_enemy_head_projection.json` | `8de57739818503a0e14702d2fa0bb4eba58228d2` |
| `product/alpha/wof_alpha_real_worker.js` | `924d02eb575d1031b168b3bb7450c34107447c85` |
| `product/alpha/wof_alpha_hud.js` | `b6f9cbf23ec1c00fe969aa2a2b59ad5e0d5433f4` |
| `product/alpha/wof_alpha_loader.js` | `b1d2bd5cc3f5e4e7a3bed084d6d35ea71489717b` |
| `product/alpha/enemy_target_labels_regression.mjs` | `55b5b1ad08768f78fd536be8995867c9a939e599` |

The existing Alpha core, warning HUD model, bootstrap, and rule manifest were not rewritten by this stage.

## Target authority / current snapshot schema

No target semantic was re-invented. The marker path consumes the existing Alpha target authority:

- `target7E == 0` -> `P1` -> label `1P`
- `target7E == 4` -> `P2` -> label `2P`
- `target7E == 8` -> `P3` -> label `3P`
- any other target field -> no confident player label

The real worker adds only the current read-only enemy state required by the projection contract:

- slot and enemy type;
- `target7E` plus the already-authoritative normalized target;
- enemy world X / floor-depth Y / Z from the existing 16.16 object coordinates at `+0x04/+0x08/+0x0C`;
- current sample time;
- current formal `runtimeEpoch` / projection epoch;
- projection sample metadata only after a durable `IMPLEMENTATION_READY` proof profile validates.

No Browser-proven unique enemy lifecycle ID exists in retained evidence. This implementation therefore does **not** fabricate `slot + type` as an episode identity. The target-label path is deliberately stateless across marker messages: each `enemy-target-markers` message is a complete current snapshot, with `holdMs=0` and smoothing disabled. A retarget, disappearance, unsupported target, or same-slot replacement cannot inherit the prior label state.

## Transport / freshness contract

The decorative marker channel is independent of normal danger warning freshness.

- existing warning publication remains `changed || heartbeat` with the existing `250 ms` heartbeat;
- marker target/presence changes publish immediately after the current 10 ms detector sample completes;
- movement/camera following is bounded to at most 20 Hz (`>= 50 ms` between unchanged-target follow publications);
- maximum scene cardinality remains the existing 20 enemy slots;
- marker payloads are full current snapshots rather than differential held state;
- marker freshness on the HUD is `300 ms`;
- stale marker, stale projection, runtime-epoch mismatch, invalid confidence, non-finite data, unsupported target/type, or invalid/out-of-bounds projection produces no confident label;
- marker delivery never refreshes or authorizes the normal danger warning channel;
- pair/session/generation/nonce/runtime-epoch authority remains the Formal Real-Adapter authority; no weakening was added.

## Projection / rendering contract

`wof_alpha_enemy_target_labels.js` adapts the proven HUDANCHOR fail-closed patterns rather than hard-coding an unproved world-to-screen transform.

A usable projection profile must have schema `wof-alpha-enemy-head-projection-v1`, verdict `IMPLEMENTATION_READY`, the exact supported World 921031 ROM SHA-256, native raster `384x224`, a bounded camera address/read/sign/scale, finite X bias, a proved Y model (`Y-Z`, `Y+Z`, or `Y`), and a finite enemy-head offset for each supported enemy type.

The renderer:

- projects the actual enemy anchor, not a global fixed box;
- rejects an invalid/out-of-native-bounds anchor before any clamping;
- clamps only the final compact `1P/2P/3P` rectangle inside the valid game content rect;
- remeasures the current WebGL `VIEWPORT` / drawing buffer each frame, so resize/fullscreen/DPR mapping changes do not reuse a stale mapping;
- draws on the existing direct game WebGL surface;
- preserves/restores game WebGL state using the existing `snapGL` / `restoreGL` discipline;
- uses a prebuilt three-label texture atlas plus one preallocated vertex buffer for a bounded batched draw of up to 20 labels;
- keeps the existing fixed danger HUD, startup status, and disabled diagnostic path intact.

Because the repository still lacks the bounded real Browser/WOF projection result, `product/alpha/wof_alpha_enemy_head_projection.json` intentionally remains:

- `verdict: UNPROVEN`
- `status: FAIL_CLOSED_UNTIL_IMPLEMENTATION_READY_PROOF`

Therefore this implementation **does not claim production-ready live head placement from synthetic data**. On current `main`, the unproved profile causes the decorative marker path to stay silent while normal warnings continue to operate.

## Exact bounded live-proof requirement

The remaining proof is intentionally narrow and must not be replaced by guessed constants.

Reuse `parallel/HUDANCHOR_REVERSE/MINIMAL_LIVE_PROOF.md` to durably close the shared Browser projection facts:

- current camera address and `u16be` read identity;
- camera sign / scale;
- X bias;
- selected Y model (`Y-Z`, `Y+Z`, or `Y`);
- the existing live WebGL viewport mapping / epoch freshness conditions.

In addition, because a player above-character offset is not evidence for every enemy sprite, perform a bounded enemy-head clearance proof for each enemy type that Alpha V1 chooses to support and populate `enemyHeadOffsetsByType` with only those proved finite offsets. Then set a durable `proofId` and `verdict: IMPLEMENTATION_READY` for the exact World 921031 identity.

Fresh bounded Browser acceptance must visibly confirm, on the supported live enemy types:

- enemy movement, camera movement, depth movement, resize/fullscreen mapping;
- `P1 -> P2 -> P3` retarget changes with no old label remaining;
- simultaneous enemies may show different targets;
- unsupported/ambiguous/stale conditions remain silent.

This is the only remaining live-proof boundary for activation; no broad manual RAM exploration is requested by this implementation stage.

## Focused implementation-side regressions

Command executed against the final implementation content:

`node product/alpha/enemy_target_labels_regression.mjs`

Result:

```json
{
  "schema": "wof-alpha-enemy-target-head-labels-implementation-regression-v1",
  "status": "PASS",
  "testCount": 12,
  "passCount": 12,
  "failCount": 0,
  "fixture": "SYNTHETIC_IMPLEMENTATION_REGRESSION_ONLY_NOT_INDEPENDENT_QA_NOT_BROWSER_PROOF"
}
```

The 12 deterministic cases cover all required implementation-side items: 0/4/8 mapping, unsupported target, P1/P2/P3 retarget, simultaneous enemies, same-slot replacement, stale/epoch fail-closed, invalid confidence/NaN/Infinity, near-edge rectangle-only clamp, invalid anchor suppression, resize/fullscreen remap, danger HUD preservation, read-only safety, and Alpha/Formal transport compatibility.

Fresh post-write syntax checks also passed for the label model, real worker, HUD, loader, and regression file. A focused compatibility check confirmed the existing danger HUD `1500 ms` staleness, exact diagnostic warning revocation, Alpha core identity contract, normal warning `250 ms` heartbeat, and bounded marker `50 ms` follow cadence remain present.

These are implementation-side regressions only. They are **not** independent QA and are **not** Browser/WOF projection proof.

## Safety invariants

Preserved:

- read-only observer path;
- `ramWrites = 0`;
- input injection disabled;
- no game Worker replacement;
- no Blob Worker rewrite;
- no gameplay target selection or enemy AI modification;
- no danger-rule threshold/semantic modification;
- gameplay/warnings are not made dependent on decorative marker activation.

## Freshness / downstream release implications

This stage changes release-consumed Alpha product blobs, so final release must not reuse stale release-gate conclusions mechanically.

Required downstream before Alpha V1 release:

1. fresh independent target-label QA against these settled blobs;
2. freshness-sensitive Formal Real-Adapter QA re-evaluation/rerun wherever its gate pins these changed Alpha blobs;
3. the bounded real Browser/WOF projection + enemy-head clearance proof above;
4. bounded Browser acceptance that visibly verifies enemy-follow and real retarget behavior;
5. Owner OneClick V3 only after these product blobs and the required proof settle;
6. Acceptance reconciliation / Release Freeze must consume the fresh target-label PASS gate.

The independently running Safe Transport 5h endurance is not invalidated merely by unrelated presentation changes; its own exact snapshot-drift policy remains authoritative for the files it pins.

Owner action during this implementation stage: **NO**. The only remaining owner-facing work is the already-bounded real Browser/WOF proof/acceptance path.

## Stop condition

**COMPLETE — ALPHA V1 ENEMY TARGET HEAD LABELS IMPLEMENTED — READY FOR FRESH QA / BOUNDED LIVE PROOF**
