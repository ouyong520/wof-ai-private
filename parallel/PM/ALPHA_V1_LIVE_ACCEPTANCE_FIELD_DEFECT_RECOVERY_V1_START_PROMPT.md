# Alpha V1 — Bounded Real WOF Live Acceptance Field Defect Recovery V1

你这次负责 **Alpha V1 Bounded Real WOF Live Acceptance — Field Defect Recovery V1**。

这是 **真实 Owner 实机验收暴露出的 implementation recovery**，不是 Fresh QA、不是 second opinion、不是 readiness reconciliation，也不是重新做历史已经 PASS 的 repository QA。

仓库：

`ouyong520/wof-ai-private`

开始前必须重新读取 current `main`，以及：

- `parallel/PM/PM_CORE_OPERATING_CHARTER.md`
- `parallel/PM/TESTING_CADENCE_POLICY.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/ALPHA_V1_BOUNDED_LIVE_ACCEPTANCE_OWNER_FLOW_V2.md`
- `parallel/PM/ALPHA_V1_BOUNDED_REAL_WOF_ACCEPTANCE_AUTHORIZATION.md`
- current `parallel/PYLAUNCH/**`
- current `parallel/OPTOOLKIT/**`
- current `parallel/OWNER_ONECLICK/**`
- current package manifest / selected runtime
- current `product/alpha/**` release integration only as needed to trace the end-to-end launch path

严格执行 canonical dedup v2。

建议 dedup key：

`alpha.v1.live-acceptance.field-defect-recovery-v1`

先 create-only canonical claim，重新读取并验证 claimToken，再创建 stage claim，然后才开始 implementation。若已有等价 ACTIVE/COMPLETE successor，按 dedup 规则 duplicate stop，禁止抢 claim。

---

## 现场事实 / Owner evidence

本任务由真实 WOF bounded acceptance 触发，不是 synthetic 推演。

Owner 已经实际进入活跃 WOF 房间，并明确报告：

1. **游戏每隔几秒明显卡顿/停顿一次**；
2. **游戏内完全没有出现 Alpha V1 用户可见内容**：没有玩家头顶 `[危险]`，也没有怪物头顶 `1P / 2P / 3P`；
3. 早期托盘状态显示：
   - Browser 已连接；
   - WOF 页面已找到；
   - Worker 未找到；
   - WASM / heap 未找到；
4. 随后采集到的诊断表明 Worker / WASM / heap 后来可以发现，但 World 身份门停在：

   `ROM locator candidate count 2`

   因此 authority 未进入可用终态；
5. Owner 菜单 `8 自动整理并打包结果` 当前报：

   `没有找到自动结果整理器。请先选择 1“更新项目”。`

6. Owner 明确要求 OneClick/便携行为：
   - 第一次运行允许自动下载；
   - **下载内容放在启动器当前目录的本地子目录，不安装到其它隐蔽位置作为主体**；
   - 第二次以后直接运行应直接进入菜单；
   - **不能每次启动都重新下载/更新**；
   - 只有 Owner 主动选择更新时才联网校验/补缺。

这些都是当前真实验收链的具体 defect/UX requirement。

---

# 目标

把这批真实验收 defect 作为 **一个 coherent live-acceptance runtime integration recovery module** 完整修掉，让下一次 Owner 只需要一次新的便携 OneClick：

`双击启动 -> 菜单 6 -> 正常进入 WOF -> Alpha 真正运行且不周期卡顿 -> 菜单 7/8 可直接收集/打包`

不要让 Owner 在 implementation 未完成前反复进入游戏试错。

---

# A. 周期性卡顿：必须查明并消除

当前代码中有一个需要重点验证、但不能未经证明直接当结论的嫌疑链：

- `LauncherMonitor` 当前约 1 秒 cadence 调 `discover(...)`；
- discovery / identity authority 逻辑可能反复执行高成本 Worker identity probe；
- current World identity probe 会扫描大块 WASM heap / ROM locator 并做 SHA authority 工作；
- 如果它在游戏 Worker 上周期执行，可能直接干扰游戏主 runtime，形成 Owner 观察到的周期性 hitch。

你必须通过 current source + deterministic/local instrumentation/self-check 证明实际调用路径和成本，而不是只凭猜测改 polling number。

要求：

- 已经接受的 World identity authority **不得每个普通 monitor tick 重跑全 heap/ROM 扫描**；
- 但也绝不能为了性能而把旧 identity 无限缓存；
- Browser/CDP generation、Worker replacement、runtime/heap generation、page/worker authority 变化时必须严格撤销旧 authority；
- cheap health/replacement detection 与 expensive identity establishment 要分层；
- stale targetId / same targetId replacement 不得沿用旧 authority；
- fail-closed 语义保持；
- readOnly=true、ramWrites=0、inputInjection=false 保持；
- 不允许通过增大到一个很慢的 polling interval 来掩盖根因，同时导致 stale detection 失效。

增加足够的 regression/self-check，能证明：

- stable same-generation runtime 不会周期重复做 full identity scan；
- generation/Worker/runtime replacement 一定触发 re-attestation；
- stale cached identity 不能复活；
- disconnected / ambiguous / malformed 状态仍 fail-closed。

---

# B. `ROM locator candidate count 2`：严格消歧，不得放宽身份门

真实现场已经看到 **2 个 locator candidate**。

当前逻辑把 `found.length !== 1` 直接拒绝，导致即便真实 World ROM 在 heap 中存在也无法进入 identity accepted。

必须设计 **严格、可证明的消歧**，禁止：

- `found[0]` / first match；
- 随便按地址高低选；
- 因为两个 candidate 看起来相似就接受；
- 跳过 World 921031 exact identity；
- 降级为 partial hash / weak signature；
- 把 ambiguous 当 PASS。

目标仍然是 exact World 921031 authority。

可接受的方向必须满足这样的性质：

- 对候选逐一进行足够强的 exact identity 验证；
- **只有唯一一个候选能够被 exact expected authority 证明时才接受**；
- 0 个 exact match => reject；
- >1 个 exact match => ambiguous reject；
- 输出结构化 candidate diagnostics，便于以后现场定位；
- 不能把 ROM bytes 写出/提交仓库。

具体实现由你根据 current runtime/source 事实决定，不要机械照抄 PM 描述。

---

# C. “游戏里什么都没有”：必须验证真正 end-to-end Alpha launch path

不要把“没有 `[危险]`”简单归类为 supported move 未触发，因为 Owner 同时报告：

- 连最基础的怪物头顶 `1P/2P/3P` 也没有任何可见 Alpha 内容；
- authority 当前又没有成功完成。

必须从菜单 `6 运行真人浏览器验证` 的真实路径向下追：

`OPTOOLKIT -> PYLAUNCH -> Browser/CDP -> runtime authority -> release-selected Alpha bootstrap/adapter/HUD`

明确回答并修复：

1. 菜单 6 当前是否真的启动/连接了 **package-selected Alpha V1 release runtime**，还是只启动了 proof/status monitor；
2. World authority accepted 后，production Alpha bootstrap / worker / HUD 是否会被实际激活；
3. 用户不打开 DevTools、不粘 JS 时，完整发布路径是否可达；
4. package selection 是否漏了实际 runtime entrypoint / wiring；
5. fixed HUD fallback / anchored projection 的权限边界是否仍正确。

如果 current menu 6 只监控、不启动实际 Alpha release runtime，这是本任务必须修的 P0 integration defect。

保持冻结产品语义：

- 不改 danger rules；
- 不新增/猜测 danger move；
- 不改 `target7E` / 0,4,8 -> 1P,2P,3P 语义；
- 不放宽 player/enemy projection authority；
- 不伪造 live evidence；
- authority 不可信时仍 hide/fallback，不能为了“让东西出现”而强画。

必须建立 repository-side end-to-end self-check，至少证明：

- accepted authority + valid package-selected runtime => Alpha release entrypoint 实际启动；
- no accepted authority => 不得产生 anchored false overlay；
- target label 基本 flow 在合法 authority 下可达；
- danger warning 仍只由已有 production-enabled rules 触发。

---

# D. Owner 菜单 8 必须自带、离线可用

修复当前 package/OPTOOLKIT 中：

`8 自动整理并打包结果`

因 `EVIDENCE_INGESTOR` / result organizer 不在 selected package 或 entrypoint 不可达而失败的问题。

要求：

- 当前 package 自身必须包含菜单 8 所需组件；
- 不得提示 Owner 为了打包结果先更新整个项目；
- 菜单 8 在一次 live session 后可直接把当前 `Documents/WOF_RESULTS` 中本次结果整理为 ZIP；
- 不递归把旧 packages 套娃进新 ZIP；
- 输出位置明确、稳定；
- menu 7 -> 8 -> 9 连续流程可用；
- 对不存在结果、权限错误、部分文件占用等情况给中文可理解错误；
- 保持结果和 proof provenance，不伪造缺失 evidence。

---

# E. Official OneClick / portable local behavior

把 Owner 已明确要求的行为做成 **repository durable implementation**，不是聊天里临时补丁：

第一次：

- 从 immutable/pinned manifest/source 获取所需文件；
- 下载到启动器当前目录下的明确本地 runtime 目录；
- Python venv / deps 也应尽量在该本地目录；
- 中文路径 / 空格路径可用；
- hash/manifest verification 保持 fail-closed。

第二次及以后：

- 本地完整且 verified/installed marker 有效时，**直接打开菜单**；
- 普通启动不做全量联网下载；
- 普通启动不因为 remote main 有变化就偷偷漂移；
- 只有 Owner 明确选择菜单 `1 更新 WOF 工具` 时才做 update/check；
- update 只补缺失/损坏/目标版本需要变化的内容；
- 保留 immutable candidate / manifest authority，不下载“随 main 漂移”的 release payload。

不要把 `%LOCALAPPDATA%` 作为唯一主体安装位置来违背 Owner 的 portable-local 要求。

---

# F. Package / release candidate authority

当前 Owner OneClick V4 是历史 immutable PASS candidate，但真实 live acceptance 已发现 defect，所以：

- **不得继续把旧 candidate 当可验收成功版本**；
- 不得修改旧 manifest 后仍冒用旧 packageVersion/source identity；
- 修复后必须生成一个新的、明确 successor candidate identity/manifest；
- selected blobs exact pin；
- package contents 与真实 menu 6 / menu 8 路径一致；
- stale/mutated payload rejection 继续有效；
- atomic local update / last-known-good 语义不能被破坏。

如果 repair 改变了 package-selected PYLAUNCH / OPTOOLKIT / Alpha integration assets，必须按新 successor candidate 正确 repin。

---

# G. 测试纪律

这是 implementation recovery。

你必须自己做 **module-level implementation self-check**，但不要自己另开 Fresh QA / second opinion / cross-check。

至少覆盖：

- exact World identity：0 / 1 / 2+ locator candidates；
- 2 candidates 中唯一 exact match；
- 2 candidates 都不 match；
- 多个 exact match ambiguous fail-closed；
- stable runtime 不重复 full scan；
- Worker/runtime/browser generation replacement 会撤销 cache；
- same targetId replacement；
- WOF page early / Worker late / WASM late readiness；
- runtime identity accepted 后 end-to-end Alpha start；
- invalid authority no false overlay；
- periodic monitor path 无重型 Worker scan cadence；
- menu 6 packaged path；
- menu 7/8/9；
- portable first run / second run offline direct-menu / explicit update；
- 中文路径 / 空格路径；
- manifest/blob mutation rejection；
- readOnly=true / ramWrites=0 / inputInjection=false。

历史 PASS QA 只做 regression inputs/reference，不要重跑整个历史 QA 链。

若 implementation self-check 发现具体 defect，继续修到 coherent module candidate 完成，不要做一点就停。

---

# H. 禁止

- 不启动新的真实 Browser/WOF Owner session；Owner 已经承担过一次失败验收，implementation 完成前不要让他再测；
- 不让 Owner 打开 DevTools；
- 不要求 Owner 粘 JS；
- 不修改 danger rule coverage 来“制造提示”；
- 不猜敌人/招式映射；
- 不改 Training Farm / Collector；
- 不开启多 worker/fleet 作为解决方案；
- 不通过关闭 fail-closed identity 来让 HUD 出现；
- 不反复新开 QA；
- 不篡改历史 PASS RESULT；
- 不复用旧 package identity 冒充新 candidate。

---

# I. Durable terminal output

完成时必须：

1. implementation commits 全部落到 `main`；
2. self-check / regression durable；
3. 写结构化 RESULT，例如：

`parallel/PM/RESULTS/ALPHA_V1_LIVE_ACCEPTANCE_FIELD_DEFECT_RECOVERY_V1_RESULT.md`

RESULT 必须明确：

- Owner 现场 defect 原因；
- periodic stutter 根因及修复；
- `ROM locator candidate count 2` 如何严格处理；
- menu 6 是否/如何真正启动 Alpha release runtime；
- no-overlay 根因；
- menu 8 修复；
- portable-local first/subsequent run 行为；
- successor package candidate / manifest exact pins；
- 所有 self-check 数量和结果；
- readOnly / ramWrites / inputInjection；
- 是否 `READY FOR ONE FOCUSED OWNER LIVE RETEST`。

4. 只有 matching claimToken 才关闭 canonical claim 和 stage claim；
5. 若遇到真实外部 blocker，写精确 BLOCKED RESULT，说明已证明的事实和最短下一步。

最终只允许：

`COMPLETE — ALPHA V1 LIVE ACCEPTANCE FIELD DEFECT RECOVERY V1 — <self-check summary> — READY FOR ONE FOCUSED OWNER LIVE RETEST`

或：

`BLOCKED — ALPHA V1 LIVE ACCEPTANCE FIELD DEFECT RECOVERY V1 — <精确具体 blocker>`

少汇报，优先实现；不要做一点就停，不要提前拆 QA，不要反复确认。持续执行完整模块、集成、自测、RESULT、claim 收口，只有 COMPLETE / 精确 BLOCKED / duplicate stop 时再回报。
