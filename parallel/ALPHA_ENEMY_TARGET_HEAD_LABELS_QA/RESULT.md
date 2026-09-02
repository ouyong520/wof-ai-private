# Alpha V1 Enemy Target Head Labels — Fresh Independent QA Result

Stage: `ALPHA_ENEMY_TARGET_HEAD_LABELS_QA_V1`

Status: **BLOCKED — ALPHA V1 ENEMY TARGET HEAD LABELS FRESH QA — malformed numeric-string `target7E` values are coerced into valid player targets and can render false `1P` / `2P` / `3P` labels**

Owner action during this repository QA: **NO**.

## Exact QA start / claim

- exact QA start HEAD: `26fe29f442193246bf3d131a8c57d5a4cde39dea`
- atomic claim commit: `25b664fea50a593cd46a8aca1ae7259351b8687c`
- dedicated independent fixture commit: `97a9a3dd99cfdcdb05980ffe995d9983a7bd1351`
- durable independent execution result commit: `82ecd257c9aca7e7f83d2c997c10b982a9c8911c`
- production scope modified by this QA: **none**

Audited product blobs stayed pinned to the implementation result:

| Path | Blob |
|---|---|
| `product/alpha/wof_alpha_enemy_target_labels.js` | `3f6f4410376756e6935a4236e40e76574b289169` |
| `product/alpha/wof_alpha_enemy_head_projection.json` | `8de57739818503a0e14702d2fa0bb4eba58228d2` |
| `product/alpha/wof_alpha_real_worker.js` | `924d02eb575d1031b168b3bb7450c34107447c85` |
| `product/alpha/wof_alpha_hud.js` | `b6f9cbf23ec1c00fe969aa2a2b59ad5e0d5433f4` |
| `product/alpha/wof_alpha_loader.js` | `b1d2bd5cc3f5e4e7a3bed084d6d35ea71489717b` |
| `product/alpha/enemy_target_labels_regression.mjs` | `55b5b1ad08768f78fd536be8995867c9a939e599` |

## Independent defect

The production helper currently defines its raw target mapping through ordinary JavaScript object indexing:

`TARGETS_BY_FIELD[target7E]`

without first requiring `target7E` to be an exact numeric/integer value.

JavaScript property-key coercion therefore turns numeric strings into the same object keys as numbers:

- `target7E: "0"` -> `P1` -> `1P`
- `target7E: "4"` -> `P2` -> `2P`
- `target7E: "8"` -> `P3` -> `3P`

The independent fixture proves this reaches the render plan, not merely the mapper helper. With a synthetically valid projection fixture, a marker whose raw field is the string `"0"` produces one confident `1P` label instead of being suppressed. A direct follow-up probe confirmed `"4"` and `"8"` similarly produce `2P` / `3P`.

Expected fail-closed behavior for the QA prompt's malformed/ambiguous-target attack is **no confident label**.

Normal current `wof_alpha_real_worker.js` obtains `target7E` from `U16(...)`, so the ordinary worker producer emits a number. That does not close this QA gate: the HUD accepts a transport-matched `enemy-target-markers` envelope, stores `m.markers`, and passes those marker objects directly to `TARGET_LABELS.buildPlan(...)`; there is no independent exact-type guard at that consumer boundary. The repository fail-closed contract explicitly requires malformed target values to be attacked and rejected rather than normalized by coercion.

This is a real implementation defect and triggers the stage's `BLOCKED` stop condition. This QA does not modify the implementation.

## Independent fixture

Added:

`parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS_QA/independent_enemy_target_labels_qa.mjs`

Durable output:

`parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS_QA/independent_qa_result.json`

Result:

- schema: `wof-alpha-enemy-target-head-labels-independent-repository-qa-v1`
- evidence class: `SYNTHETIC_REPOSITORY_QA_ONLY_NOT_BROWSER_WOF_PROJECTION_PROOF`
- tests: **16**
- PASS: **15**
- FAIL: **1**
- failing case: `malformed numeric-string raw targets must fail closed`
- observed first failure: `string 0 must not render a label; got 1P`

The other 15 independent checks were green:

- exact numeric `0/4/8 -> P1/P2/P3 -> 1P/2P/3P` mapping;
- unsupported numeric target and raw/normalized-target mismatch suppression;
- same-enemy `P1 -> P2 -> P3` retarget with no stale hold;
- simultaneous enemies with independent different targets;
- disappearance / same-slot replacement with no inherited label;
- marker freshness: `300 ms` accepted, `301 ms` suppressed;
- projection freshness: `300 ms` accepted, `301 ms` suppressed;
- marker/projection/drawing-buffer epoch mismatch suppression;
- invalid confidence and NaN/Infinity/non-finite XYZ/projection values suppression;
- unsupported enemy type and invalid slot suppression;
- near-edge valid anchor clamps only the label rectangle;
- invalid/out-of-bounds anchor suppression before clamp;
- malformed/stale drawing-buffer suppression;
- resize/fullscreen mapping-key and coordinate recomputation;
- current repository `UNPROVEN` projection profile is rejected and keeps labels silent;
- invalid proof/profile facts remain fail closed.

## Execution mode / limitations

The QA environment could not perform a native repository clone because the container has no external DNS/network access (`Could not resolve host: github.com`). The stage prompt explicitly permits source-exact reconstruction when a native private checkout cannot execute.

For the independently executed SUT, the current production helper and current projection profile were reconstructed directly from the claimed GitHub blobs and verified byte-for-byte through Git blob hashing before execution:

- `git hash-object product/alpha/wof_alpha_enemy_target_labels.js` -> `3f6f4410376756e6935a4236e40e76574b289169`
- `git hash-object product/alpha/wof_alpha_enemy_head_projection.json` -> `8de57739818503a0e14702d2fa0bb4eba58228d2`

Executed successfully before the intentional failing assertion:

- `node --check product/alpha/wof_alpha_enemy_target_labels.js`
- `node --check parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS_QA/independent_enemy_target_labels_qa.mjs`
- `node parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS_QA/independent_enemy_target_labels_qa.mjs` -> **FAIL, 15/16 PASS**

The unchanged implementation-owned `product/alpha/enemy_target_labels_regression.mjs` was re-read and its historical implementation result remains 12/12 synthetic PASS, but it was **not falsely reported as natively re-executed** in this network-isolated environment. It does not contain the malformed numeric-string target attack found by this independent QA and is not used to override the independent failure.

## Wiring / regression observations

Repository inspection confirmed the intended surrounding design remains structurally present:

- page loader order loads `wof_alpha_hud_model.js`, then `wof_alpha_enemy_target_labels.js`, then `wof_alpha_hud.js`;
- HUD requires `WOFAlphaEnemyTargetLabels.buildPlan` before takeover;
- HUD marker receive path requires schema/session/transport-pair match;
- marker messages update marker state only; normal warning `state` messages separately refresh the danger-warning state;
- normal danger warning publication remains `changed || heartbeat` with `>= 250 ms` heartbeat;
- target-marker retarget/presence change publishes immediately and unchanged follow publication remains bounded by `>= 50 ms`;
- marker HUD staleness remains `300 ms`, separate from the normal danger HUD's `1500 ms` freshness;
- current profile remains `verdict: UNPROVEN` / `FAIL_CLOSED_UNTIL_IMPLEMENTATION_READY_PROOF`, so current live target-head rendering remains silent rather than guessing projection constants;
- current HUD retains GL state snapshot/restore around its draw paths;
- current worker continues to declare read-only / `ramWrites=0` / input injection false / Worker replacement false / Blob rewrite false.

These green surrounding checks do not excuse the malformed-target fail-closed defect.

## Formal / Acceptance / Release implications

The historical Formal Real-Adapter Recovery V2 fresh QA pinned older Alpha worker/HUD blobs and cannot be mechanically reused for this candidate. Current `main` already contains the dedicated `ALPHA_FORMAL_REAL_ADAPTER_CURRENT_BLOB_REVALIDATION_V1` start prompt for the changed worker/HUD blobs. That freshness gate remains correctly identified as a separate downstream/currentness requirement.

Acceptance and Release Freeze current prompts now explicitly require this target-head-label implementation plus a fresh independent QA PASS. Because this stage is **BLOCKED**, those consumers must remain fail closed; they must not consume the implementation-owned 12-case synthetic PASS as a substitute.

## Browser/WOF proof boundary

No Browser/WOF was launched by this repository QA, and no synthetic evidence here is a live projection proof.

Even after the malformed-target defect is fixed and fresh repository QA passes, the already-declared bounded live proof remains required for:

- current camera/projection facts under the HUDANCHOR minimal live-proof contract;
- proved `enemyHeadOffsetsByType` only for supported enemy types;
- real movement/camera/depth/resize following;
- a real `1P -> 2P -> 3P` retarget with no stale prior label;
- unsupported/ambiguous/stale live state remaining silent.

That pending bounded live proof is **not** the blocker reported here. The repository blocker is the numeric-string raw-target coercion defect.

## Minimal implementation follow-up required

Independent QA does not apply the fix. The implementation owner should make raw target acceptance exact-type / exact-value fail closed before lookup (for example, require a finite integer/number and exact membership in numeric `0/4/8`, without coercive property lookup), and add regression coverage that strings `"0"`, `"4"`, `"8"` and other malformed target values produce no label.

After that implementation settles, this stage requires a **fresh independent QA rerun on the new blobs**; this BLOCKED result must not be rewritten into PASS without new evidence.

## Stop condition

**BLOCKED — ALPHA V1 ENEMY TARGET HEAD LABELS FRESH QA — malformed numeric-string `target7E` values `"0"` / `"4"` / `"8"` are coerced to valid targets and can render false `1P` / `2P` / `3P` labels instead of failing closed.**
