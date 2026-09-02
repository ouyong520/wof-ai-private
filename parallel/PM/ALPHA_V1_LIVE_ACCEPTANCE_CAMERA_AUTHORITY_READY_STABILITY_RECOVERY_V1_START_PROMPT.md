# Alpha V1 Live Acceptance — Camera Authority READY Stability Recovery V1

stageId: `ALPHA_V1_LIVE_ACCEPTANCE_CAMERA_AUTHORITY_READY_STABILITY_RECOVERY_V1`
dedupProtocol: `v2`
dedupKey: `alpha.v1.live-acceptance.camera-authority-ready-stability-recovery-v1`
dedupMode: `exclusive`

你负责 **Alpha V1 Live Acceptance Camera Authority READY Stability Recovery V1**。

这是 successor package `2026.09.02.ffa2cb162df0` 的真实 Owner 实机测试暴露出的窄 implementation recovery。不是 Fresh QA，不重做已 COMPLETE 的 Owner Calibration + Local Identity Recovery V1。

仓库：`ouyong520/wof-ai-private`

开始前重新读取 current `main`、`parallel/PM/STAGE_DEDUP_GUARD.md`、`parallel/PM/TESTING_CADENCE_POLICY.md`、以下 COMPLETE authority：

- `parallel/PM/RESULTS/ALPHA_V1_LIVE_ACCEPTANCE_OWNER_CALIBRATION_IDENTITY_RECOVERY_V1_RESULT.md`
- `parallel/PM/DEDUP_CLAIMS/alpha.v1.live-acceptance.owner-calibration-identity-recovery-v1.json`
- current `parallel/OWNER_ONECLICK/package_manifest.json`
- package source `ffa2cb162df0cda65e6fa09b6b0e4fa8f6025399`
- `parallel/HUDANCHOR_PROOF/wof_owner_projection_worker.js`
- `parallel/HUDANCHOR_PROOF/wof_owner_projection_top.js`
- `parallel/PYLAUNCH/**`
- `parallel/OPTOOLKIT/**`

## Canonical ownership

第一项 mutation 必须 create-only：

`parallel/PM/DEDUP_CLAIMS/alpha.v1.live-acceptance.camera-authority-ready-stability-recovery-v1.json`

使用 fresh unpredictable `claimToken`，re-read current main 验证 exact ownership 后，再 create-only：

`parallel/PM/STAGE_CLAIMS/ALPHA_V1_LIVE_ACCEPTANCE_CAMERA_AUTHORITY_READY_STABILITY_RECOVERY_V1.json`

已有等价 ACTIVE/COMPLETE successor => duplicate stop，禁止抢 claim。

---

## 最新真实 Owner evidence

Owner 使用正式 successor package：

- packageVersion `2026.09.02.ffa2cb162df0`
- sourceCommit `ffa2cb162df0cda65e6fa09b6b0e4fa8f6025399`

同一真人验证期间出现明显 authority/UI 冲突：

游戏内 Top calibration overlay 显示：

- `samples 692 / 80 · READY`
- `Camera 已稳定：只点击一次 P1 头顶上方希望警告中心出现的位置。`

而 Owner 状态/诊断窗口随后同时显示：

- `头顶校准：samples 880 / 80 · CANDIDATE_AMBIGUOUS`
- `出现多个接近的 camera 候选。继续跨更长距离左右卷屏以拉开候选；旧样本会继续复用。`
- `下一步：继续当前窗口做更长距离左右卷屏。`

World/Worker/WASM authority此时正常：

- Browser connected
- Page found
- Worker found
- WASM / memory found
- exact World 921031 confirmed
- SHA-256 `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`
- readOnly=true / ramWrites=0 / inputInjection=false

因此这不是 local identity defect，也不是 World identity defect，而是 **Camera candidate READY authority 可在继续采样后退回 CANDIDATE_AMBIGUOUS，且 Top UI / tray diagnostics 可在短时间内给出互相冲突 Owner 指令**。

不要让 Owner继续当前包的 calibration，也不要建议在这种冲突状态下点击 P1 头顶。

---

## Package-source truth

在 `ffa2cb...` 的 `wof_owner_projection_worker.js`：

- `quality(rows())` 每个采样周期重新计算 top candidate 与 score gap；
- `ok` 依赖当前时刻 `gap >= .10` 等条件；
- 后续新增样本可改变候选排序 / score gap，使曾经 `READY` 的状态重新变成 `CANDIDATE_AMBIGUOUS`；
- 当前没有“same candidate stable for bounded evidence window -> authority generation -> immutable ready snapshot”语义。

在 `wof_owner_projection_top.js`：

- `q.ok` 时立即显示“Camera 已稳定，点击一次 P1 头顶”；
- Owner 点击时 `calibrate()` 又重新依赖当下 `last.cameraQuality.ok` 和当前 `candidate()`；
- 因此 READY 到 click 之间存在 TOCTOU / authority drift 窗口；
- tray/diagnostics 与 Top UI 可消费不同时刻 snapshot，产生互相冲突的 Owner 指令。

这是本 recovery 的核心 defect。

---

# Recovery goals

## A. Camera candidate READY 必须成为严格稳定 authority

1. 禁止使用单一瞬时 `q.ok` 直接升级 Owner 到可点击状态。
2. 定义 bounded、deterministic、可自测的 READY stability contract，至少包含：
   - same top camera address 持续稳定；
   - score/range/changes/valid/strong/follow/gap 在连续证据窗口内满足阈值；
   - candidate generation / evidence sample range 明确绑定；
   - READY authority 一旦产生，要有唯一 authority id / generation / selected address / proof sample window。
3. READY 后到 Owner 点击之间不得重新使用一个不同的瞬时 top candidate。
4. 两种安全语义任选其一，但必须严格且一致：
   - **latched verified candidate**：READY 时冻结已验证 candidate authority，Owner 点击只绑定该 authority；或者
   - **revocable authority**：若证据退化则明确 revoke READY，并在所有 UI 同步回到继续采样，禁止接受 click。
5. 禁止因为“曾经 READY”就永久信任一个没有持续证据的错误 candidate。
6. 禁止猜 camera 地址/scale/bias；所有 projection constants 仍只能来自真实 bounded proof。

## B. 消除 Top / tray / evidence 状态冲突

1. Worker publication 加入单调 sequence / authority generation / snapshot identity，使 Top UI、tray diagnostics、evidence 能知道自己消费的是哪一代状态。
2. Owner-facing“可以点击 P1”只能由同一个 authoritative READY snapshot 驱动。
3. tray / Top UI 对同一 authority generation 必须给一致 next action；不允许一边 `READY click`、另一边 `CANDIDATE_AMBIGUOUS continue scrolling`。
4. 如果 tray 比 Top 新，Top 必须及时 revoke/更新；如果 READY 已 latched，则 tray 必须显示 latched authority 而不是继续用未锁定 ranking 给相反指令。
5. 自动 evidence/ZIP 记录 READY_CREATED / READY_REVOKED / CAMERA_LOCKED / candidate generation / sequence / reason timeline。

## C. Owner novice flow

1. Owner只需要看一个明确动作：
   - 继续左右卷屏；或
   - Camera 已稳定，可以点一次 P1 头顶；或
   - authority 已撤销，继续卷屏。
2. 不允许两个窗口给相反命令。
3. 如果长时间多个 camera 候选始终无法拉开，给 bounded、明确中文终态/下一步，不静默无限采样。
4. 不能通过放宽 ambiguity 阈值简单“让它过”。必须解决 authority stability 与 TOCTOU。

## D. Preserve prior recoveries

必须保持：

- lifecycle-aware P1/P2/P3 local identity semantics；
- exact World 921031 SHA hard gate；
- re-entry Worker/WASM rediscovery；
- Alpha reactivation；
- cheap cached-runtime-health；
- Tk owner UI thread safety；
- disconnect 后 significant live evidence retention；
- automatic evidence/ZIP；
- readOnly=true / ramWrites=0 / inputInjection=false。

## E. Deterministic self-check

至少覆盖：

- candidate A 瞬时领先一次不能 READY；
- A 连续稳定达到窗口 -> READY authority；
- READY 前候选 A/B 交替 -> remains ambiguous；
- READY 后 ranking 短暂变化的定义行为（latched 或 revoke）严格符合 contract；
- click 只能消费 exact READY authority generation/address，不得 TOCTOU 换 candidate；
- stale Top snapshot 与 newer ambiguous tray snapshot 不得产生冲突可点击状态；
- Worker/runtime generation replacement 撤销旧 camera authority；
- one-player identity regression；
- re-entry regression；
- evidence timeline；
- Windows portable / package integrity / safety boundaries。

这是 implementation recovery + module-owned self-check，不开 Fresh QA / second opinion / cross-check，不启动 Browser/WOF，不伪造真人 visual PASS。

---

# Successor package / closeout

生成新的 immutable successor package；旧 `2026.09.02.ffa2cb162df0` 不再让 Owner重复测试。

完成：

- implementation；
- integration；
- deterministic self-check；
- implementation-source workflow；
- Windows portable validation；
- successor manifest exact pinning；
- durable RESULT：
  `parallel/PM/RESULTS/ALPHA_V1_LIVE_ACCEPTANCE_CAMERA_AUTHORITY_READY_STABILITY_RECOVERY_V1_RESULT.md`
- matching claimToken canonical/stage COMPLETE 收口。

RESULT 必须明确：root cause、READY stability contract、TOCTOU fix、Top/tray一致性、authority generation语义、self-check/workflow/Windows结果、exact successor package pins、安全边界、Owner下一步。

最终只允许：

`COMPLETE — ALPHA V1 LIVE ACCEPTANCE CAMERA AUTHORITY READY STABILITY RECOVERY V1 — SUCCESSOR PACKAGE READY — READY FOR ONE FOCUSED OWNER LIVE RETEST`

或精确：

`BLOCKED — ALPHA V1 LIVE ACCEPTANCE CAMERA AUTHORITY READY STABILITY RECOVERY V1 — <exact concrete blocker>`

少汇报、不要中断、持续执行；不要停在 claim、单 patch、单测试、workflow in-progress、manifest publication、RESULT 未收口或 claim 未关闭阶段。