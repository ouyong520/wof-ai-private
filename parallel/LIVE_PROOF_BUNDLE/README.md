# WOF Unified Windows Live Proof Bundle

状态：**UNIFIED LIVE PROOF READY — ONE OWNER WOF RUN REMAINS**

这个目录只负责把已经 READY 的 Windows 工具拼成一次真人短验证，不修改它们的核心实现。

## Owner 最终只做一次

双击：

`RUN_WOF_UNIFIED_LIVE_PROOF.cmd`

流程：

```text
双击中文入口
-> 自动下载/准备最新仓库工具
-> 自动准备 Python 环境
-> 启动 1 个专用 Browser Fleet 房间
-> 自动启动 PYLAUNCH 权威只读 proof
-> 自动启动 WOF-052L Recorder Discovery V2 准入
-> owner 正常进入一个 WOF 房间
-> 自动汇总 Browser / page / Worker / WASM / World 921031 / Fleet / Recorder / safety
-> 自动项全部 PASS 后，只问一次“游戏是否仍正常运行？”
-> 生成一个中文总结果 + UNIFIED_LIVE_PROOF_STATUS.json
```

不需要：
- DevTools；
- Worker Console；
- 粘贴 JavaScript；
- 分别跑 3~4 个 proof；
- 手工检查 RAM；
- GitHub Actions 冒充真人 proof。

## 为什么仍有一次 Y/N

`Browser/page/Worker/WASM/World 921031`、Fleet Discovery V2、Recorder Discovery V2 admission 和安全字段都能自动验证。

“游戏当前仍可正常运行”是 owner 真人事实。统一入口不会注入按键、鼠标、手柄，也不会为了自动验证可玩性改变游戏。因此自动项全部通过后，只要求一次：

```text
当前 WOF 房间是否仍能正常运行？ Y / N
```

这不是额外技术 proof；它是唯一的真人可玩性确认。

## 证据权威层级

统一结果明确区分：

1. **Browser Fleet Discovery V2**
   - 只做快速 Worker indicator；
   - `workerStatusAuthority = cheap-indicator-only`；
   - 不能冒充 World 921031 身份证明。

2. **PYLAUNCH**
   - Browser / WOF page / Worker / WASM / heap / exact World 921031 的权威短 proof；
   - 精确 SHA-256：
     `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`。

3. **WOF-052L Recorder Discovery V2**
   - 必须独立达到真实 Recorder admission；
   - 输出中只有出现 `World 921031 已确认 / Discovery V2 / 只读模式` 才记为准入 PASS。

4. **Owner playability**
   - 自动项全部通过后一次 Y/N。

只有四层都通过，`tenRoomLongCaptureReady=true`。

## 专用 proof 房间隔离

统一入口不会复用正在运行的普通 Fleet 房间。

它为本次 proof 单独创建：
- 独立 run 目录；
- 独立 profile；
- 独立 Fleet manifest；
- 独立 localhost CDP port（9423-9499 中自动选择空闲端口）；
- 独立 PYLAUNCH proof JSON；
- 独立 Recorder 输出目录。

因此不会把另一个房间的 Worker/session 状态串进本次 proof。

## 一处失败不丢其他证据

总 JSON 分开保存：
- Fleet 当前证据；
- PYLAUNCH 当前权威证据；
- Recorder admission 证据和最近输出；
- 安全字段；
- 子进程退出码；
- blocker。

任一分支失败时，其他已经 PASS 的证据仍保留，不会被一个 FAIL 覆盖成空结果。

## 总结果

运行结果位于：

`%LOCALAPPDATA%\WOF Future Danger\UnifiedLiveProof\runs\<run-id>\UNIFIED_LIVE_PROOF_STATUS.json`

同时更新稳定路径：

`%LOCALAPPDATA%\WOF Future Danger\UnifiedLiveProof\UNIFIED_LIVE_PROOF_STATUS.json`

最终 owner 只需要返回：
- 这个 JSON；或
- 一张最终中文状态截图。

## PASS 后的行为

如果真人短 proof 全 PASS：

```text
tenRoomLongCaptureReady = true
longCaptureAutoStarted = false
```

工具只提示“已具备 10 房间长采集条件”。

**不会未经 owner 同意自动开始一小时长采集。**

## Repo/CI 与真人 live 明确分开

仓库侧状态只能写：

`UNIFIED LIVE PROOF READY — ONE OWNER WOF RUN REMAINS`

它不等于真人 Windows 已 PASS。

`UNIFIED_LIVE_PROOF_STATUS.json` 的仓库模板会保持：
- repository.result = PASS
- repository.liveProofClaimed = false
- live.result = NOT_RUN
- tenRoomLongCaptureReady = false

只有 owner 真机运行后，runtime JSON 才可能变成 `overallResult=PASS`。

## Mock / offline regression

```bat
py -3 -m unittest -v parallel\LIVE_PROOF_BUNDLE\test_unified_live_proof.py
```

覆盖：
- Fleet quick indicator 绝不冒充 World identity；
- 三条自动链全部通过才可进入 playability confirm；
- Recorder 未准入时 fail closed；
- RAM write / safety violation fail closed；
- 真人 playability 未确认时不能宣布 10-room ready；
- 全 PASS 后也不会自动开始 long capture；
- 单分支失败保留其他正证据；
- Recorder admission marker；
- repo PASS 与 live PASS 明确分离。

## Safety

端到端固定：
- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`
- no `window.Worker` replacement/wrap
- no Blob/Data/ObjectURL Worker
- no gameplay input injection
- no `product/alpha/**` modification

本目录只新增 `parallel/LIVE_PROOF_BUNDLE/**`。
