# Alpha V1 — Live Acceptance Overlay + Re-entry Recovery V1

stageId: `ALPHA_V1_LIVE_ACCEPTANCE_OVERLAY_REENTRY_RECOVERY_V1`
dedupProtocol: `v2`
dedupKey: `alpha.v1.live-acceptance.overlay-reentry-recovery-v1`
dedupMode: `exclusive`

你负责 **Alpha V1 Live Acceptance Overlay + Re-entry Recovery V1**。

这是 2026-09-02 最新真实 Owner focused live retest 暴露出的 **窄 implementation recovery**。不是 Fresh QA、不是 second opinion、不是重新做上一轮已 COMPLETE 的 field recovery。

仓库：`ouyong520/wof-ai-private`

开始前重新读取 current `main`、`parallel/PM/STAGE_DEDUP_GUARD.md`、`parallel/PM/TESTING_CADENCE_POLICY.md`，以及上一轮 COMPLETE RESULT / successor package：

- `parallel/PM/RESULTS/ALPHA_V1_LIVE_ACCEPTANCE_FIELD_DEFECT_RECOVERY_V1_RESULT.md`
- `parallel/PM/RESULTS/ALPHA_V1_LIVE_ACCEPTANCE_FIELD_DEFECT_RECOVERY_V1_CLOSEOUT_RECOVERY_V3_RESULT.md`
- current `parallel/PYLAUNCH/**`
- current `parallel/OPTOOLKIT/**`
- current `parallel/OWNER_ONECLICK/**`
- current `product/alpha/**`
- current package manifest
- `parallel/HUDANCHOR_REVERSE/MINIMAL_LIVE_PROOF.md`
- related HUDANCHOR proof/operator tooling as needed

## Canonical ownership

第一项 mutation 必须 create-only：

`parallel/PM/DEDUP_CLAIMS/alpha.v1.live-acceptance.overlay-reentry-recovery-v1.json`

用 fresh unpredictable `claimToken`，re-read current main 验证 exact ownership 后，再创建：

`parallel/PM/STAGE_CLAIMS/ALPHA_V1_LIVE_ACCEPTANCE_OVERLAY_REENTRY_RECOVERY_V1.json`

已有等价 ACTIVE/COMPLETE successor => duplicate stop，禁止抢 claim。

---

## 最新真实 Owner evidence

使用正式 successor package：

- packageVersion `2026.09.02.91be86ade8d4`
- sourceCommit `91be86ade8d4dcc7ee100458a1cedd87f5873bf7`

第一次进入活跃 WOF 房间：

- Browser 已连接；
- WOF page 已找到；
- Worker 已找到；
- WASM / heap 已找到；
- World 921031 已确认；
- 两个 structural ROM locator 被严格消歧：`unique exact World 921031 full CPU-logical SHA-256 among 2 locator candidates`；
- discovery path 为 `cached-runtime-health`；
- readOnly=true / ramWrites=0 / inputInjection=false；
- 游戏页面实际出现 `WOF Alpha RC5 已加载`，证明 package-selected Alpha runtime 首次 activation 已进入页面。

Owner 继续实际玩后反馈：

- 初次只短暂卡几秒，随后不再持续每隔几秒周期卡顿；因此上一轮 periodic-hitch 修复看起来有效，但本 recovery 仍应保留 compact regression，不能重新引入重型轮询；
- **敌人头顶完全没有 `1P / 2P / 3P`**；
- **玩家头顶也没有 `[危险]`**；
- 不是仅仅“危险动作未触发”，因为基础 enemy target labels 同样完全不可见。

重新退出/进入房间后：

- Browser 仍连接；
- WOF page 已找到；
- Worker 未找到；
- WASM / heap 未找到；
- World 未确认；
- discovery path 退回 `page-only`；
- 技术详情：`WOF page found; related game Worker not yet discovered`；
- 页面处于 portal/series 路径后再进入房间时没有自动恢复 Worker authority / Alpha overlays。

## 已确认 repository truth

当前正式 package 中：

`product/alpha/wof_alpha_enemy_head_projection.json`

仍是：

- `verdict: UNPROVEN`
- `status: FAIL_CLOSED_UNTIL_IMPLEMENTATION_READY_PROOF`
- camera/bias/head-offset authority 为空。

`product/alpha/wof_alpha_player_head_projection.json`

仍是：

- `status: UNPROVED`
- `activation: DISABLED_UNTIL_BOUNDED_BROWSER_WOF_PROOF`

因此当前包虽然可以成功启动 Alpha runtime，但 anchored enemy/player overlays 仍按设计 fail-closed。这说明之前的 live acceptance candidate **尚未真正完成头顶 projection production authority**。禁止通过硬编码/猜常量/关闭 fail-closed 来让标签出现。

已有 `parallel/HUDANCHOR_REVERSE/MINIMAL_LIVE_PROOF.md` 明确说明 player projection 剩余的是一次 bounded Browser proof，并且 Owner 输入应限制为正常移动、一次锚点点击、纵深、跳跃、resize/fullscreen 和最终视觉分类，不允许 DevTools、地址抄写或手算。

---

# Recovery goals

把下面内容作为一个 coherent live-acceptance module 做完整，不拆成多个 QA/fix 线程。

## A. 头顶 Overlay authority 真正闭环

1. 追 current player/enemy projection authority gate，证明为什么正式 package 在 exact World accepted + Alpha running 后仍无 anchored overlay。
2. 复用已有 HUDANCHOR proof/tooling；不要重新发明广泛 RAM reverse。
3. 把剩余 bounded live projection proof 做成 **Owner-friendly、package-selected、一键可达** 的流程：
   - 不开 DevTools；
   - 不粘 JS；
   - 不抄地址/坐标；
   - 不做手工算术；
   - 最少用户动作；
   - fail-closed。
4. 若已有 repository authority 足以完成 production profile，则直接正确生成/消费 authoritative projection profile；若必须依赖下一次 live bounded calibration，则本实现必须把校准流程集成进正式 OneClick，使 Owner 下次只按中文提示完成一次，不再需要开发者步骤。
5. enemy `1P/2P/3P` 必须在合法 current authority 下真正有可达的 anchored projection path；player `[危险]` 亦同，但 danger warning 仍只能由现有 production-enabled danger rules 触发。
6. 禁止：
   - 猜 camera address / scale / bias；
   - 猜 head clearance；
   - synthetic evidence 升 production；
   - 修改 danger rule coverage；
   - 修改 target7E 0/4/8 -> 1P/2P/3P 语义；
   - invalid authority 强画 overlay。

## B. Room leave/re-entry 自动 Worker rediscovery / Alpha reactivation

正常产品流程必须支持 launcher 持续运行期间：

`room A accepted -> 离开到 portal/series page -> old authority revoked -> 进入 room B/同一 room -> 新 page/frame/Worker generation 自动发现 -> exact World authority 重建 -> Alpha runtime 自动重新 activation`

要求：

- 不要求 Owner 手点“重新连接”；
- 不要求重启 OneClick；
- old Worker/page/runtime generation 必须失效，不能复用 stale authority；
- same targetId replacement 也必须重新证明 generation；
- page-only 状态必须持续轻量观察并在新 related Worker 出现后自动恢复；
- 不能为了恢复 Worker discovery 重新引入高频全 heap/ROM full scan；
- successful re-entry 后 overlays/Alpha runtime authority 必须绑定新 generation。

建立 deterministic lifecycle self-check，至少覆盖：

- first room success；
- room -> portal page-only；
- portal -> new room late Worker；
- late WASM / heap；
- same targetId new isolate；
- old Worker disappears/new Worker appears；
- invalid/ambiguous pair fail-closed；
- Alpha revoke then reactivation；
- stable new room 回到 cheap cached-runtime-health；
- 无周期性重型扫描回归。

## C. Owner evidence UX：自动收集 + 自动整理 + 自动打包

Owner 已明确要求不要再让玩家执行“先 7 收集、再 8 打包”两次操作。

正式 package 行为改为：

- menu 6 / focused live session 启动后自动建立 session evidence directory；
- session 过程中自动持续写必要 diagnostics/proof/status；
- session 完成、窗口关闭、明确结束动作或可证明的 terminal state 时，**自动整理并自动生成 ZIP**；
- menu 7 / 8 可以保留为 manual fallback/repair，但正常玩家流程不依赖它们；
- 不递归 package nesting；
- 不伪造缺失 evidence；
- 失败也保留 partial 原始 evidence；
- 中文提示只告诉玩家最终 ZIP 在哪里，不要求懂目录结构。

## D. 可安全自动上传 GitHub（仅在已有授权时）

Owner 希望最好自动上传 Git，减少手工传 ZIP。

实现前先查 repository/package 是否已有安全 upload authority/channel。要求：

- **绝不能把 GitHub PAT/token/secret 写进 package、repo、日志或 result ZIP**；
- 不要求普通玩家手工创建/粘贴 token；
- 如果机器已经有可安全复用的受限授权（例如现有 authenticated `gh` / approved credential helper / repository-defined secure uploader），可提供自动上传 evidence artifact 的 non-interactive path，并在本地保留 ZIP；
- 若没有安全既有授权，则自动 Git upload 不得硬做，必须 graceful fallback 为“ZIP 已自动生成”，不要弹复杂认证流程；
- RESULT 必须明确 direct Git upload 是 implemented / unavailable due no secure authority / blocked 的哪一种，不得假装上传成功。

## E. New successor package

当前 `2026.09.02.91be86ade8d4` 已被这次 live retest 证明仍不能完成 intended acceptance，因此修复后：

- 必须生成新的 successor package identity/manifest；
- 不复用旧 packageVersion/source identity；
- exact selected blobs pin；
- OneClick portable first-run/second-run offline behavior继续保持；
- menu6、自动 evidence、re-entry recovery、projection proof/authority consumer 都必须实际 selected；
- readOnly=true / ramWrites=0 / inputInjection=false 保持。

## F. Testing cadence

本轮是 implementation recovery + module-owned self-check。

不要开 Fresh QA / second opinion / cross-check；不要让 Owner 现在继续反复测试旧包。

至少做：

- projection gate/proof consumption deterministic checks；
- invalid/unproved projection no false anchored overlay；
- valid authoritative projection -> enemy target labels visible path reachable；
- player warning projection path reachable while danger semantics unchanged；
- re-entry lifecycle matrix；
- stable health no heavy scan regression；
- auto evidence collection/package；
- partial/error packaging；
- optional secure upload path/fallback；
- package mutation rejection；
- Windows Chinese/space paths；
- portable second launch offline；
- readOnly/ramWrites/inputInjection boundaries。

如果 proof authority 本身仍需要真实 Owner interaction，repository self-check 不能伪造 live PASS；把新的 successor package 做到 **READY FOR ONE MINIMAL OWNER CALIBRATION/LIVE RETEST**，并把 Owner 动作压缩到现有 MINIMAL_LIVE_PROOF 定义的最少步骤。

---

# Durable RESULT

写：

`parallel/PM/RESULTS/ALPHA_V1_LIVE_ACCEPTANCE_OVERLAY_REENTRY_RECOVERY_V1_RESULT.md`

必须明确：

- no-overlay 的真实原因；
- player/enemy projection authority 当前如何处理；
- 是否仍需 one bounded live calibration，若需要具体只剩什么；
- re-entry Worker rediscovery / authority / Alpha reactivation 修复；
- periodic hitch 是否保持修复；
- 自动收集/整理/打包行为；
- GitHub auto-upload authority/安全结论；
- successor package exact pins；
- self-check 数量/结果；
- readOnly=true / ramWrites=0 / inputInjection=false；
- 精确下一步。

matching claimToken 才能关闭 canonical/stage claim。

最终只允许：

`COMPLETE — ALPHA V1 LIVE ACCEPTANCE OVERLAY + REENTRY RECOVERY V1 — <summary> — READY FOR ONE MINIMAL OWNER CALIBRATION/LIVE RETEST`

或如果 repository authority 已足够无需再校准：

`COMPLETE — ALPHA V1 LIVE ACCEPTANCE OVERLAY + REENTRY RECOVERY V1 — <summary> — READY FOR ONE FOCUSED OWNER LIVE RETEST`

或：

`BLOCKED — ALPHA V1 LIVE ACCEPTANCE OVERLAY + REENTRY RECOVERY V1 — <exact blocker>`

少汇报、不要中断、持续执行；完整 implementation、integration、自测、successor package、durable RESULT、canonical/stage claim 全部收口后再停止。