# PM Addendum — Vision-Assisted Automatic Head Localization / Calibration

Applies to:
`ALPHA_V1_LIVE_ACCEPTANCE_PROJECTION_TRANSFORM_OWNER_UX_RECOVERY_V1`

This addendum is PM scope clarification for the already ACTIVE implementation recovery. It does not create a new task, claim, QA stage, or recovery generation.

## Owner directive

The current calibration is too complex and has already caused repeated Owner mis-click / repeated-click failure. The normal live path must no longer require the Owner to understand or manually choose coordinate models such as `Y`, `Y-Z`, or `Y+Z`.

Target normal path:

`menu 6 -> enter WOF -> normal play -> automatic calibration -> overlays`

Preferred interaction budget:

- **zero clicks** if the implementation can obtain a sufficiently strict visual/render authority automatically;
- otherwise **at most one P1-head click** to seed a visual tracker / ROI;
- never require a second/third calibration click merely because tracking/model fitting continues;
- never require manual model-name selection.

## Vision-assisted approach is explicitly in scope

Evaluate and prefer an automatic visual calibration path that uses the live game canvas / rendered frames to establish the P1 head screen coordinate and pairs that with authoritative RAM/runtime samples.

A safe implementation may use one or more of:

- runtime self-captured P1 head patch/template after one optional seed click;
- multi-frame template matching / normalized correlation;
- optical-flow or equivalent bounded visual tracking;
- sprite/foreground bounding evidence when authoritative and stable;
- WebGL/render-pipeline geometry evidence if it can provide stronger entity-to-screen authority than pixel matching;
- automatic fitting of the projection transform from many paired samples `(RAM world/camera state <-> observed screen head position)`.

Do **not** treat a single static screenshot/template match as sufficient authority by itself. Pixel matching must be confidence-bounded and temporally verified because animation frames, occlusion, scaling, palette changes, overlap, death/respawn, room changes, and fullscreen/resize can produce false matches.

## Do not embed unneeded game-art assets

Prefer runtime self-captured/local ephemeral templates or render evidence. Do not add copyrighted game sprite/head artwork to the repository/package merely to support matching when the same authority can be derived from the Owner's live session. Local session-derived visual patches may be retained only as bounded evidence/cache where appropriate and must remain tied to the exact runtime/session authority.

## Required automatic transform fitting

The purpose of vision is not merely to draw a marker over a matched bitmap. Use the observed head positions to solve/validate the actual projection transform.

The implementation should collect multiple paired samples across naturally occurring movement and, when needed, automatically requested bounded actions. Fit only parameters supported by evidence (for example sign/scale/bias/depth/Z terms if the data establishes them); do not pre-assume or guess the formula merely because previous candidates were `Y`, `Y-Z`, `Y+Z`.

Require:

- minimum sample count / geometric coverage;
- residual/error bounds;
- hold-out or temporal validation;
- ambiguity rejection;
- confidence degradation/revocation when tracking is lost;
- exact binding to Camera authority generation, Worker/runtime session and player lifecycle;
- re-establishment after room/runtime/player replacement as needed.

If visual tracking loses authority, production overlays must fail closed. Do not silently reuse stale screen coordinates.

## Owner UX hard requirement

Normal successful flow must not show a screen full of candidate labels.

The Owner should see only simple Chinese guidance such as:

- `正在自动定位 P1 头部，请正常玩。`
- `需要一次确认：请点一下 P1 头顶。` (only if automatic localization confidence is insufficient)
- `正在自动校准，请正常玩。`
- `校准完成，头顶提示已启用。`

If one specific motion is genuinely required for observability, request **one action at a time** and auto-detect completion, e.g. `现在跳一次` or `请上下走动几秒`. Do not present a checklist the Owner must memorize.

No normal-path buttons named after mathematical models. No repeated P1 click unless the exact previous authority has been revoked and the UI explicitly says why a new seed is required.

## Enemy/head validation

The final authority must still support both P1 warning placement and enemy target-head placement. Do not declare success solely because P1 tracking looks good. Use authoritative/render/visual evidence to validate that the derived transform generalizes to observed enemies; if enemy-specific head clearance/offset is needed, derive it from evidence and keep it type/lifecycle bound rather than guessing.

## Evidence and packaging

Menu 6 should automatically preserve:

- whether visual localization was zero-click or one-click-seeded;
- tracker confidence timeline;
- paired sample counts/coverage;
- fitted transform parameters and residuals;
- authority generation/session/lifecycle binding;
- revocation/reacquisition events;
- final projection verdict;
- the authoritative `WOF_LIVE_ACCEPTANCE_<session>.zip` path.

The Owner must not need menu 7/8 for the normal flow.

## Exit expectation

This addendum does not change the existing recovery exit condition. The worker must still finish the whole recovery through immutable successor package, Windows portable validation, durable RESULT and canonical/stage COMPLETE. Do not stop after proving a CV prototype or a single frame match.
