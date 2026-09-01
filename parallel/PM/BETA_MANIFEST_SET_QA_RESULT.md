# WOF Beta Prospective Manifest Set — Fresh Independent QA Result

日期：2026-09-01

## 最终结论

**BLOCKED — P1 Prospective Validator 主入口不会执行 READY manifest 中声明的必要 target/type/lifecycle gate，因此当前 manifest set 不能安全交给 Validator 做 research-only validation。**

本 QA 按 `parallel/PM/BETA_MANIFEST_SET_QA_START_PROMPT.md` 执行。发现 P1 后不修改候选 manifest、不修改 Validator core，按停止条件立即停止并记录 blocker。

## P1 blocker

当前 READY manifest 中存在用于保守验证的额外 gate：

- `parallel/BETA_MANIFESTS/D867BA_3232_TM6_220.json`
  - `minDistinctTargets: 2`
  - `minObservedTypes: 2`
- `parallel/BETA_MANIFESTS/D8811E_3232_TM6_135.json`
  - `minDistinctTargets: 2`
- `parallel/BETA_MANIFESTS/T20_5136_B0_TO_B255_1250.json`
  - `requireLifecycleReset: true`

这些 gate 与启动提示第 10 条要求直接相关：READY manifest 必须保留必要的 target/type/lifecycle 条件。

但是当前实际 owner-facing 主入口：

`parallel/PROSPECTIVE_VALIDATOR/RUN_PROSPECTIVE_VALIDATOR.cmd`

调用：

`parallel/PROSPECTIVE_VALIDATOR/live_validator_v2.py`

V2 最终通过 `core.LiveValidator.write()` 调用 `validator.validate()` 生成最终 verdict。

当前 `parallel/PROSPECTIVE_VALIDATOR/validator.py::validate()` 的 PASS gate 只执行：

- `minProspectiveSignals`
- `minProspectiveRooms`
- `requireZeroHardMiss`

并没有读取或执行：

- `minDistinctTargets`
- `minObservedTypes`
- `requireLifecycleReset`

因此只要 signals / rooms / hard miss 三项满足，即使没有达到 manifest 明确声明的 target/type/lifecycle 条件，Validator 仍可能输出：

`PROSPECTIVE_PASS_RESEARCH_ONLY`

这会把 manifest 中的关键保守 gate 变成“仅文档字段”，不能作为实际 PASS 条件。

## 为什么是 P1

这不是 production promotion 风险：Validator 仍保持 `research-only`，不会自动生产晋级。

但它会直接影响 prospective research PASS 的真实性：

- descriptor family 可以在 target/type 覆盖不足时被判 PASS；
- lifecycle-sensitive history candidate 可以在没有证明 lifecycle reset 条件时被判 PASS；
- 最终结果会比 manifest 自己声明的安全门槛更宽松。

所以当前状态不满足：

> 每个 READY manifest 的 gate 必须足够保守，并由实际 Validator verdict 执行。

## 已确认无此 blocker 的硬属性

在发现 P1 前已独立确认当前 manifest set 的以下硬属性：

- READY manifest 使用 `wof-prospective-candidate-v1`。
- promotion 为 `research-only`。
- identity 固定为 `Warriors of Fate (World 921031)`。
- 黄金 SHA-256 为 `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`。
- T24 使用 canonical `T24 (0x18)`。
- T20 使用 canonical `T20 (0x14)`，且保持 ordered/history 语义。
- T16 使用 canonical `T16 (0x10)`，语义明确为 `IMMINENT DANGER, not A6432-exclusive`。
- T23 A5888 BODY4936 保持 `tail3` ordered sequence，没有退化成 constituent single-state。
- index 将 T18 BODY4728 post-anchor split 保持 `NOT_READY`，没有生成 A4704-specific manifest。
- index 明确 `automaticProductionPromotion:false`。
- Validator 对 discovery / prospective 有 freeze-time 隔离，旧 discovery evidence 不会自动满足 prospective gate。
- owner-facing CMD/主要运行提示已为简体中文。

## 解除 blocker 的最低条件

不在本 QA 中修复。后续修复线至少需要做到：

1. 实际最终 verdict 必须执行 manifest 中声明的所有受支持保守 gate；至少包括当前 set 已使用的：
   - `minDistinctTargets`
   - `minObservedTypes`
   - `requireLifecycleReset`
2. result JSON 必须显式输出这些 gate 的 observed / required / passed，不能静默忽略未知 gate。
3. 增加独立 mock regression：
   - signals / rooms / hard miss 满足，但 target 数不足 => FAIL/INSUFFICIENT；
   - signals / rooms / hard miss 满足，但 observed type 数不足 => FAIL/INSUFFICIENT；
   - T20 history 命中但 lifecycle reset 未满足 => FAIL/INSUFFICIENT。
4. 修复后重新进行 fresh independent Beta manifest set QA。

## 停止条件

**BLOCKED — P1 Prospective Validator ignores required target/type/lifecycle gates declared by READY manifests.**
