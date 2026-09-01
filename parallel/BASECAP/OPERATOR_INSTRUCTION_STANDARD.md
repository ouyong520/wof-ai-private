# BASECAP Operator Instruction Standard

Updated: 2026-09-01

Purpose: eliminate ambiguity in every human-operated BASECAP capture. A Collector task must tell the operator exactly what to press, whether to hold it, exactly when to release it, how long to remain idle after release, what visible condition to confirm, and what inputs are forbidden.

## Hard rule

Never write ambiguous instructions such as:

- `按左 2 秒`
- `左右切换几次`
- `移动一下然后停`
- `攻击几次`

These can mean materially different experiments and are forbidden for canonical BASECAP acquisition.

Every input step must use one of the explicit forms below.

## Canonical action vocabulary

### TAP / 轻点

Meaning:

`按下指定按键 -> 立即松开；不要持续按住。`

Required wording example:

`轻点 LEFT 1 次：按下 LEFT 后立即松开，不要按住。`

A TAP duration is never described as `LEFT 2 秒`. Any waiting duration must be written as a separate step after release.

### HOLD / 按住

Meaning:

`持续按住指定按键达到明确时长 -> 到时立即松开。`

Required wording example:

`持续按住 LEFT 2 秒；2 秒结束时立即松开 LEFT。`

### WAIT / 静止

Meaning:

`所有指定 gameplay controls 保持松开，不输入任何动作，持续明确时长。`

Required wording example:

`LEFT 已松开后，双手离开方向键和动作键，静止 2 秒。`

### RELEASE / 松开

When a prior step used HOLD, release must be explicit:

`到时立即松开 LEFT；确认 LEFT 已完全松开后再进入下一步。`

## Required task structure

Every operator-gated BASECAP task with active inputs must be written in this order:

1. **Pre-scene** — where P1 must be, whether combat/camera scroll is allowed, P2/P3 requirements.
2. **READY identity** — exact taskId that `READY_WOF_TASK.bat` must print as accepted.
3. **Post-READY timing guard** — for short-action scenes under current Collector v1, provide 12 seconds of zero input after exact READY acceptance.
4. **Action sequence** — numbered, one physical action per step.
5. **Release step** — every HOLD must state when to release; every TAP must state immediate release.
6. **Idle interval** — any pause is a separate WAIT step and begins only after release.
7. **Visible confirmation** — when relevant, state what the operator should visually verify.
8. **Repeat count** — exact repeat count or explicit `if time remains, repeat once`; never `repeat several times`.
9. **Forbidden inputs** — list UP/DOWN/LEFT/RIGHT/attack/jump/etc. that must not be used outside the specified steps.
10. **Other players** — explicitly state whether P2/P3 must remain untouched.

## Example: correct B12 facing wording

After exact READY acceptance:

1. `什么都不要按，静止 12 秒。`
2. `轻点 LEFT 1 次：按下 LEFT 后立即松开，不要按住。`
3. `确认人物已经朝左；LEFT 已松开后，什么都不要按，静止 2 秒。`
4. `轻点 RIGHT 1 次：按下 RIGHT 后立即松开，不要按住。`
5. `确认人物已经朝右；RIGHT 已松开后，什么都不要按，静止 2 秒。`
6. `如果时间允许，只再完整重复一次步骤 2-5。`

This is intentionally different from:

`按住 LEFT 2 秒`

which would be a horizontal-movement experiment rather than a minimal-displacement facing experiment.

## User-facing instruction rule

When asking the operator to perform a capture, ChatGPT must present the exact ordered steps in Chinese, including:

- which key;
- TAP or HOLD;
- release timing;
- wait timing after release;
- repeat count;
- forbidden inputs;
- exact READY taskId when relevant.

Do not compress the steps into shorthand that changes semantics.

## Validation rule

A mechanically healthy Collector PASS does not prove that the intended human sequence was executed. If operator wording was ambiguous, timing was unsafe, the user reports a different action, or the control-plane timing cannot guarantee the action fell inside the raw window, the capture must not be promoted as a canonical labeled baseline.

## Scope

This standard applies only to BASECAP acquisition protocol. It does not authorize automatic keypresses, game-memory writes, Browser/WASM promotion, or semantic field conclusions.
