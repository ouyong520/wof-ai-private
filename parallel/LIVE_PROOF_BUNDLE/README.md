# WOF Unified Windows Live Proof Bundle

状态：**UNIFIED LIVE PROOF PREFLIGHT HARDENING READY — OWNER NOT NEEDED FOR REPOSITORY CHECKS**

这个目录负责把 Browser Fleet、PYLAUNCH 与 WOF-052L Recorder 拼成一次真人短验证。现在真人阶段之前新增强制 repository-side preflight：仓库侧仍有 P0/P1、snapshot 不一致/过期、Discovery V2 contract 退化、测试入口缺失/失败、中文入口或安全声明不匹配时，Browser 不会启动，Owner 不需要进入 WOF。

## Owner 正常入口

双击：

`RUN_WOF_UNIFIED_LIVE_PROOF.cmd`

流程现在是：

```text
双击中文入口
-> 解析 GitHub main 的 40 位 commit SHA
-> 按该 SHA 下载单一 snapshot，并再次确认下载期间 main 没漂移
-> 自动准备 Python/依赖
-> 运行 UNIFIED_PREFLIGHT_STATUS.json 仓库侧预检
-> 只有 preflight PASS 才启动 1 个专用 Browser Fleet 房间
-> 自动启动 PYLAUNCH 权威只读 proof
-> 自动启动 WOF-052L Recorder Discovery V2 准入
-> owner 正常进入一个 WOF 房间
-> 自动汇总 Browser / page / Worker / WASM / World 921031 / Fleet / Recorder / safety
-> 自动项全部 PASS 后，只问一次“游戏是否仍正常运行？”
-> 生成中文总结果 + UNIFIED_LIVE_PROOF_STATUS.json
```

如果 preflight BLOCKED：

```text
Browser 未启动
Owner 不需要进入 WOF
不出现 Y/N 或任何点击确认
输出 %LOCALAPPDATA%\WOF Future Danger\UnifiedLiveProof\UNIFIED_PREFLIGHT_STATUS.json
退出码 20
```

## Preflight 检查什么

`unified_preflight.py` fail-closed 检查：

- Live Proof / Browser Fleet / PYLAUNCH / Recorder 必需实现、中文入口、RESULT/status 与测试入口存在；
- package snapshot 有可验证 40 位 SHA、时间新鲜，并且四个组件都 pin 到同一 commit；
- Browser Fleet、PYLAUNCH、Recorder 仍满足当前 hardened Discovery V2 capability，旧 direct-gstyphoon-only 逻辑不能冒充新实现；
- 当前 required RESULT/QA 不得是 `BLOCKED` / `SUPERSEDED`，并必须出现对应 PASS/READY marker；
- JSON status 必须可解析、结构完整，freshness/safety gate 必须匹配；
- owner-facing 入口必须保留简体中文；
- 安全声明保持 `readOnly=true / ramWrites=0 / inputInjection=false / no Worker replacement`；
- 运行 9 组安全离线 regression：Live Proof、preflight 自身、Browser Fleet、PYLAUNCH、Recorder；任一命令失败或 0 tests 都阻断。

Preflight 本身不会启动 Browser、不会 attach WOF、不会请求 Owner 操作。

## 当前仓库为什么仍会被 preflight 拦住

截至本 hardening stage 的最新仓库重新评估，至少两个 fresh independent QA 仍是 repository-side P1：

1. `parallel/PYLAUNCH_QA_PARENTFRAME_AUTHORITY/RESULT.md`
   - `P1-STALE-TARGETID-IDENTITY-CACHE-AUTHORITY`
   - 同一 targetId 跨 runtime/browser generation 可能继承旧 exact World identity authority。
2. `parallel/LIVE_PROOF_BUNDLE_QA_FRESHNESS/RESULT.md` / `RESULT.json`
   - `RECORDER_ARBITRARY_STDOUT_REFRESHES_STALE_ADMISSION`
   - arbitrary Recorder stdout 仍可刷新旧 admission freshness authority。

因此本 stage 的意义不是宣布真人 proof 已可运行，而是让入口在这些 repository blocker 关闭并 fresh QA PASS 之前自动拒绝进入真人阶段。

## Snapshot / package 一致性

外层 CMD 不再下载浮动 `refs/heads/main` ZIP 后假定它代表同一版本。它先解析 `main` SHA，再下载 `codeload/.../zip/<sha>`，生成 `UNIFIED_SNAPSHOT_MANIFEST.json`：

- `snapshotCommit=<40-char SHA>`
- `resolvedAtUtc=<UTC time>`
- `liveProof/browserFleet/pylaunch/recorder` 全部等于同一个 SHA

下载完成后会再次查询 main；如果下载期间 main 已变化，直接失败并要求重新取得最新 snapshot，不进入 Browser。

直接在正常 git checkout 中用 `--local` 运行时，preflight 读取本地 `git HEAD`，并要求相关组件工作树无未提交改动。

## Evidence authority

1. **Browser Fleet Discovery V2**
   - 只做快速 Worker indicator；
   - `workerStatusAuthority = cheap-indicator-only`；
   - 不能冒充 World 921031 identity authority。
2. **PYLAUNCH**
   - Browser / WOF page / Worker / WASM / heap / exact World 921031 权威短 proof。
3. **WOF-052L Recorder Discovery V2**
   - 必须独立达到当前 Recorder admission。
4. **Owner playability**
   - 只有前三层当前自动 authority 全 PASS 后才出现一次 Y/N。

只有真人阶段四层都通过，`tenRoomLongCaptureReady=true`。

## 专用 proof 房间隔离

统一入口只在 preflight PASS 后创建专用 proof 房间，并使用独立 run 目录、profile、Fleet manifest、localhost CDP port、PYLAUNCH proof JSON 和 Recorder 输出目录。不会复用普通 Fleet 房间。

## Result files

Preflight 稳定结果：

`%LOCALAPPDATA%\WOF Future Danger\UnifiedLiveProof\UNIFIED_PREFLIGHT_STATUS.json`

真人短 proof（只有 preflight PASS 后才可能生成）：

`%LOCALAPPDATA%\WOF Future Danger\UnifiedLiveProof\runs\<run-id>\UNIFIED_LIVE_PROOF_STATUS.json`

同时更新稳定 live 路径：

`%LOCALAPPDATA%\WOF Future Danger\UnifiedLiveProof\UNIFIED_LIVE_PROOF_STATUS.json`

## PASS 后也不自动长采集

即使真人短 proof 最终 PASS：

```text
tenRoomLongCaptureReady = true
longCaptureAutoStarted = false
```

不会未经 Owner 同意自动开始一小时/长时间 10-room capture。

## Repository / live 分离

`UNIFIED LIVE PROOF PREFLIGHT HARDENING READY` 只表示 preflight 能正确做 repository gate，不等于当前 repository 已通过 preflight，更不等于真人 Windows 已 PASS。

当前 P1 未关闭时，应看到 preflight `result=BLOCKED`，而不是启动 Browser。

## Offline regression

Preflight hardening 自身：

```bat
py -3 -m unittest -v parallel\LIVE_PROOF_BUNDLE\test_unified_preflight.py
```

覆盖至少：all-pass、component BLOCKED、stale snapshot、mixed commits、missing test、old discovery、English-only entry、安全 mismatch、malformed JSON、regression failure、PASS 才启动 live、FAIL 绝不启动 live，以及中文 blocker/Owner action NO。

运行时 preflight 还会重跑当前安全组件 regression；不会用历史 PASS 冒充当前命令结果。

## Safety

端到端固定：

- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`
- no `window.Worker` replacement/wrap
- no Blob/Data/ObjectURL Worker creation by this bundle
- no gameplay input injection
- no `product/alpha/**` modification
- repository preflight failure cannot launch Browser
