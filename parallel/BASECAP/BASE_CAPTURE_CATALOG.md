# BASECAP Reusable Capture Catalog

Updated: 2026-09-01
Status: **BASECAP v1 COMPLETE**

本文件是共享 WinKawaks 基础 raw 的权威索引。原则：**先复用，后重采；永不根据 raw 数值猜操作者做过什么。**

标准 raw 身份：

```text
captures/<taskId>.jsonl.gz
```

每个 VALID 人工标签必须由 task/result/raw 身份和操作者动作/肉眼确认共同支持。Collector `PASS` 只证明机械采集健康。

所有 raw 的共同布局：

```text
P1 + P2 + P3 + 20 enemies
23 objects
stride = 0xE0
5152 bytes/frame
```

## 1. 基础覆盖总表

| Scene | State | Canonical / reuse source |
| --- | --- | --- |
| B00 stationary idle | **VALID** | `BASECAP-B00-idle-8s60-20260901-0510Z` |
| B10 P1 horizontal-only | **VALID LABELED PHASE / REUSE** | `RAWMINE-005-p1-depth-wide-window-40s60-20260901-0048Z` first operator-confirmed phase |
| B11 P1 floor/depth-only | **VALID LABELED PHASE / REUSE** | same `RAWMINE-005` second operator-confirmed phase |
| B12 facing/minimal displacement | **VALID** | `BASECAP-B12R-facing-delayed-30s60-20260901-0527Z` |
| B13 P1 ordinary-attack/action diversity | **VALID** | `BASECAP-B13-attack-12s60-20260901-0558Z` |
| B20 camera-scroll discriminator | **VALID** | `BASECAP-B20-camera-scroll-16s60-20260901-0559Z` |
| B30 natural gameplay/combat diversity | **VALID REUSE** | `EFIELD-003-passive-retarget-60s60` |
| B31 typed-enemy lifecycle enter/exit diversity | **VALID REUSE** | `EFIELD-003-passive-retarget-60s60` |
| B32 target/retarget diversity | **VALID REUSE** | `EFIELD-003-passive-retarget-60s60` |
| B40 P2 horizontal + depth movement | **VALID** | `BASECAP-B40-P2-xy-16s60-20260901-0600Z` |
| B40 P3 horizontal + depth movement | **VALID** | `BASECAP-B40-P3-xy-16s60-20260901-0601Z` |

BASECAP 当前没有必须继续向操作者采集的基础场景缺口。

---

## 2. Canonical VALID captures

### B00 — `BASECAP-B00-idle-8s60-20260901-0510Z`

- status: `VALID`
- rawPath: `captures/BASECAP-B00-idle-8s60-20260901-0510Z.jsonl.gz`
- taskBlobSha: `9743cf0a1762b1d0f595cb2639e1ffe1f8b50bb8`
- capturedAtUtc: `2026-09-01T05:17:05.567887+00:00`
- duration / hz: `8.0 s`, target `60`, achieved `59.951`
- frames: `480`
- bytesPerFrame: `5152`
- readErrors / frameSizeErrors: `0 / 0`
- readOnly / writesGameMemory: `true / false`
- operator scene: P1 安全位置静止；无移动、攻击、跳跃或其它游戏输入；P2/P3 不操作。
- changed intentionally: none at operator-input level.
- held stable intentionally: all P1 controls released; no intentional combat/camera scroll; P2/P3 untouched.
- reuse: idle/no-input baseline；背景动画/计时器/noise 筛选；与移动/攻击 capture 对照。
- confounder: raw 内部仍有动画/计时器/敌人状态自然变化，不可解释为 bytewise static。
- source evidence: matching task + PASS result + retained raw；场景标签来自操作协议，不来自 raw 推断。

### B10/B11 — `RAWMINE-005-p1-depth-wide-window-40s60-20260901-0048Z`

- status: `VALID LABELED PHASE / REUSE`
- rawPath: `captures/RAWMINE-005-p1-depth-wide-window-40s60-20260901-0048Z.jsonl.gz`
- taskBlobSha: `3d91bb9b77e3618500db9bde8b2145d909d4b441`
- capturedAtUtc: `2026-09-01T00:52:23.634810+00:00`
- duration / hz: `40.0 s`, target `60`, achieved `59.981`
- frames: `2400`
- readErrors / frameSizeErrors: `0 / 0`
- operator confirmation:
  - first phase: visible repeated RIGHT/LEFT traversal roughly `15 s`; no attack/jump/extra action；P2/P3 untouched；用于 B10；
  - second phase: visible repeated UP/DOWN floor-depth traversal roughly `20 s`; no attack/jump/extra action；P2/P3 untouched；用于 B11。
- confounder: phase boundary is operator-timed, not frame-marker timestamped. RAWMINE reconstructed-X positive-control anomaly does not erase the authoritative visible operator confirmation; do not invent exact frame boundaries from raw values.
- reuse: P1 horizontal/depth discriminators；GEO/RAWMINE candidate screening。

### B12 — `BASECAP-B12R-facing-delayed-30s60-20260901-0527Z`

- status: `VALID`
- rawPath: `captures/BASECAP-B12R-facing-delayed-30s60-20260901-0527Z.jsonl.gz`
- taskBlobSha: `881d8a73802a4221936bf15dbd479d2326ebedd0`
- capturedAtUtc: `2026-09-01T05:30:00.518197+00:00`
- duration / hz: `30.0 s`, target `60`, achieved `59.997`
- frames: `1800`
- readErrors / frameSizeErrors: `0 / 0`
- operator scene: 安全空旷，无战斗/镜头滚动；旧 v1 时序下使用 12 秒保护后短 LEFT/RIGHT facing taps；无 UP/DOWN、攻击、跳跃或 P2/P3 输入。
- intended changed: P1 facing，允许最小附带水平位移。
- reuse: facing/minimal-displacement discriminator。
- supersedes canonical use of `BASECAP-B12-facing-minimal-8s60-20260901-0518Z`。

### B13 — `BASECAP-B13-attack-12s60-20260901-0558Z`

- status: `VALID`
- rawPath: `captures/BASECAP-B13-attack-12s60-20260901-0558Z.jsonl.gz`
- taskBlobSha: `5f4eba115057e3feed97e03bdb205dade7bd98d1`
- capturedAtUtc: `2026-09-01T06:19:11.663344+00:00`
- duration / hz: `12.0 s`, target `60`, achieved `59.941`
- frames: `720`
- distinctRawFrameCount: `647`
- readErrors / frameSizeErrors: `0 / 0`
- streamSha256: `91d2fc47da509d755e11aab881ce0d284e01980c3f5c57ca9660fa3fb31a9816`
- compressedSha256: `6a75735c2940642c70acf5c713e46fe4513a821f9299cd6a9d2e2bda9956ff56`
- operator flow: Collector v2 单窗口；场景准备后在主窗口回车；看到“采集已开始”后执行动作。
- operator action: P1 原地轻点普通攻击共 4 次；前 3 次每次立即松开后静止 2 秒；第 4 次后不再输入；禁止方向、跳跃、其它动作；P2/P3 不操作。
- intentional changed: P1 ordinary-attack/action animation state.
- held stable: no intentional directional movement；camera intended not to scroll；P2/P3 untouched.
- confounder: 某些攻击动画可能自带少量位移；不得用方向键纠正。动作帧由人工时序产生，没有独立 frame marker。
- source evidence: exact task + matching PASS result + retained raw + operator completion confirmation。

### B20 — `BASECAP-B20-camera-scroll-16s60-20260901-0559Z`

- status: `VALID`
- rawPath: `captures/BASECAP-B20-camera-scroll-16s60-20260901-0559Z.jsonl.gz`
- taskBlobSha: `0de63c648dad1bebbafd5f81b3b9cc01fe26184b`
- capturedAtUtc: `2026-09-01T06:24:25.073330+00:00`
- duration / hz: `16.0 s`, target `60`, achieved `59.972`
- frames: `960`
- distinctRawFrameCount: `866`
- readErrors / frameSizeErrors: `0 / 0`
- streamSha256: `0f4dddc0f1f1b33a46a219d0b58a40374225d543e9166eeda9cfa2336729289c`
- compressedSha256: `196eb422b9d4a9131a876846b35c3ea3fdc62dd23ddd4497213fff078fff4480`
- operator action: 看到“采集已开始”后静止 2 秒；P1 持续按住右方向键 6 秒后立即松开；之后静止到结束；禁止其它方向、攻击、跳跃；P2/P3 不操作。
- required visual condition: 操作者明确确认 6 秒期间背景/整个画面出现明显横向滚动。
- intentional changed: P1 horizontal progression + camera/background horizontal scroll episode.
- held stable: no attack/jump/other direction；P2/P3 untouched.
- source evidence: exact task + matching DONE/PASS + retained raw + operator explicit “有滚动” confirmation。

### B30/B31/B32 — `EFIELD-003-passive-retarget-60s60`

- status: `VALID REUSE`
- rawPath: `captures/EFIELD-003-passive-retarget-60s60.jsonl.gz`
- taskBlobSha: `acb475dc253ab599b196f80651e18a2ffa2f2914`
- capturedAtUtc: `2026-08-31T16:04:36.616276+00:00`
- duration / hz: `60.0 s`, target `60`, achieved `60.001`
- frames: `3600`
- readErrors / frameSizeErrors: `0 / 0`
- B30 reuse: broad natural-gameplay/combat diversity；不是受控攻击实验。
- B31 reuse: typed-enemy episode diversity；retained EFIELD evidence reports `11 type-enter + 11 type-exit` edges。**不得未经 EFIELD 证据把这些边缘直接称为 semantic spawn/death。**
- B32 reuse: known retarget frames `492`, `1827`, `3322`。
- operator action: ungated natural gameplay，未记录为精确输入序列；BASECAP 不从 raw 猜输入。

### B40-P2 — `BASECAP-B40-P2-xy-16s60-20260901-0600Z`

- status: `VALID`
- rawPath: `captures/BASECAP-B40-P2-xy-16s60-20260901-0600Z.jsonl.gz`
- taskBlobSha: `5aa3fbbeb226ee411327ead0177e347841977a78`
- capturedAtUtc: `2026-09-01T06:27:48.626720+00:00`
- duration / hz: `16.0 s`, target `60`, achieved `59.997`
- frames: `960`
- distinctRawFrameCount: `888`
- readErrors / frameSizeErrors: `0 / 0`
- streamSha256: `9d3f36320da411f73ce11a47100c11806ac624589f28a092c6cf162706ee328f`
- compressedSha256: `2fe969346599d45ca3717857d7137552d305169fc9b1981b6840846cb130d1a1`
- operator scene: P2 已加入且可独立操作；安全空旷；短距离移动不触发镜头滚动；P1 静止，P3 不操作。
- operator action: P2 RIGHT hold 2s -> release -> idle 1s；LEFT 2s -> idle 1s；UP 2s -> idle 1s；DOWN 2s -> release -> idle to end；无攻击/跳跃/其它动作。
- reuse: P2 X/depth structure replication screening。**BASECAP 只提供数据，不宣告 offset 语义。**

### B40-P3 — `BASECAP-B40-P3-xy-16s60-20260901-0601Z`

- status: `VALID`
- rawPath: `captures/BASECAP-B40-P3-xy-16s60-20260901-0601Z.jsonl.gz`
- taskBlobSha: `c54ea1e777e4004501bad37cf8f350da8d65f7ea`
- capturedAtUtc: `2026-09-01T06:29:55.334706+00:00`
- duration / hz: `16.0 s`, target `60`, achieved `59.963`
- frames: `960`
- distinctRawFrameCount: `841`
- readErrors / frameSizeErrors: `0 / 0`
- streamSha256: `73018edd1b597b624769eef62c896912ec593a9d9527cb9c93f3b709c2dfb9fe`
- compressedSha256: `8b2d2225b5bd68facc3a7df5c6393d032f574f226f8c369c35f6d0de3f89b925`
- operator scene: P3 已加入且可独立操作；安全空旷；短距离移动不触发镜头滚动；P1/P2 静止。
- operator action: P3 RIGHT hold 2s -> release -> idle 1s；LEFT 2s -> idle 1s；UP 2s -> idle 1s；DOWN 2s -> release -> idle to end；无攻击/跳跃/其它动作。
- reuse: P3 X/depth structure replication screening。**BASECAP 只提供数据，不宣告 offset 语义。**

---

## 3. Historical NONCANONICAL / INVALID records

这些 raw/尝试保留历史价值，但不得作为对应基础标签的 canonical source。

| Capture/task | Classification | Reason |
| --- | --- | --- |
| `BASECAP-B12-facing-minimal-8s60-20260901-0518Z` | **INVALID for canonical B12** | 机械 PASS/raw retained，但旧 Collector v1 要求 READY 后立即动作；短动作可能发生在正式 capture 前。 |
| `BASECAP-B13-standing-attack-delayed-30s60-20260901-0536Z` | **INVALID / control-plane aborted** | 旧 READY 门控无法可靠推进；操作者多次动作不能证明落入正式 capture；旧 queue 后续移除。 |
| `BASECAP-B13R-standing-attack-ungated-60s60-20260901-0543Z` | **NONCANONICAL for B13** | 机械 PASS/raw retained，但 `operatorGate.required=false` 导致 Collector 在操作者动作前自动运行；无可靠攻击标签。 |
| `GEO-0008-p1-depth-only-5s60-20260831-2115Z` | **SUPERSEDED for B11** | 早期不足尝试；B11 由 `RAWMINE-005` 取代。 |
| `GEO-0009-p1-depth-visible-traverse-8s60-20260901-0024Z` | **INVALID for canonical B11** | GEO 后续归类为 ineffective/attribution-limited。 |
| `GEO-0010-p1-attribution-depth-calibration-10s60-20260901-0033Z` | **INVALID intended sequence** | 后续操作报告说明输入序列不正确。 |
| `RAWMINE-004-p1-attribution-depth-redo-10s60-20260901-0037Z` | **INVALID canonical baseline** | retained report: attribution/manipulation validity FAIL。 |
| `GEO-0011-p1-attribution-depth-calibration-10s60-20260901-0038Z` | **INVALID canonical B10/B11** | 后续 GEO 归类为 earlier insufficient attempt。 |
| `GEO-0012`, `GEO-0013` | **historical P2 evidence only** | 不替代新的 controlled B40-P2；`GEO-0013` distinct raw coverage 极低。 |
| `GEO-0001/0003/0004/0006` | **exploratory/passive only** | 不得重命名为受控 B00/B12/B13/B20。 |
| historical `GEO-0002/0005/0007` | **no canonical retained raw** | 不复用旧 taskId。 |

任何历史 raw 都不得覆盖；需要重做时使用新 taskId。

---

## 4. Collector 控制流版本说明

### 历史 v1

旧流程使用 `READY_WOF_TASK.bat`，READY 与正式 capture start 不同步，因此短动作存在时序竞态。历史 capture 按当时真实协议判定。

### 当前 v2

当前流程：任务自动出现 -> 准备场景 -> 主窗口按一次回车 -> 看到“采集已开始” -> 执行动作 -> 自动上传/结果/下一任务。

`READY_WOF_TASK.bat` 已废弃，新任务不再使用旧 12 秒防竞态延迟。

详见：

```text
parallel/BASECAP/OPERATOR_INSTRUCTION_STANDARD.md
parallel/BASECAP/OPERATOR_GATE_TIMING_NOTE.md
```

---

## 5. Downstream reuse rule

GEO / EFIELD / RAWMINE / future lanes 在新建人工采集前必须先查本目录。

可直接复用：

```text
B00 idle
B10 P1 horizontal phase
B11 P1 depth phase
B12 facing
B13 ordinary attack/action
B20 camera scroll
B30 natural gameplay diversity
B31 typed-enemy enter/exit diversity
B32 retarget diversity
B40-P2 controlled P2 X/depth motion
B40-P3 controlled P3 X/depth motion
```

BASECAP 的标签只描述**已验证的采集场景与操作者动作**，不等于字段语义证明。下游研究仍需自行完成 offset/field/production 结论。

## 6. Completion verdict

`BASECAP v1 = COMPLETE`

理由：

- 基础套件全部覆盖；
- 当前新增 B13/B20/P2/P3 均 `DONE/PASS`、0 read/frame-size errors、retained raw；
- B13 操作序列有操作者完成确认；
- B20 有明确“发生镜头滚动”的肉眼确认；
- P2/P3 controlled movement raw 已闭合；
- B30/B31/B32 已从 EFIELD retained corpus 复用；
- 历史非 canonical 尝试被显式隔离；
- 无需继续占用操作者进行 BASECAP 基础采集。
