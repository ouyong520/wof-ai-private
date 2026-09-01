# WOF Unified Windows Live Proof Bundle — Result

Updated: 2026-09-01

Verdict: **UNIFIED LIVE PROOF READY — ONE OWNER WOF RUN REMAINS**

## Scope

本阶段只新增：

`parallel/LIVE_PROOF_BUNDLE/**`

没有修改：
- `parallel/PYLAUNCH/**`
- `parallel/BROWSER_FLEET/**`
- `parallel/WOF052L_RECORDER/**`
- `parallel/WOF052L_LIVE_CAPTURE/**`
- `parallel/WOF052L_ANALYSIS/**`
- `parallel/WORKER_SURFACE/**`
- `parallel/OWNER_ONECLICK/**`
- `product/alpha/**`

## 组合前提已核对

当前仓库已经分别具备：
- PYLAUNCH Discovery V2：repository fix ready，只剩真人 Windows proof；
- Browser Fleet Discovery V2：repository regression PASS，Worker 仅 cheap indicator；
- WOF-052L Recorder Discovery V2：repository ready，准入要求 WASM/heap + exact World 921031；
- WOF-052L Live Capture：`READY FOR 10-ROOM LONG CAPTURE`；
- WOF-052L Analysis：`READY`；
- owner-facing Windows 工具默认简体中文。

因此本阶段没有重新实现这些核心，只做统一编排和总结果。

## 新的一键入口

`RUN_WOF_UNIFIED_LIVE_PROOF.cmd`

支持直接下载单个 CMD 后双击：

```text
download/double-click
-> latest repository snapshot
-> Python/venv/dependencies
-> one isolated proof Browser Fleet room
-> PYLAUNCH authoritative proof
-> Recorder Discovery V2 admission
-> one consolidated Chinese status
```

正常 owner 不需要 Git、DevTools、Worker Console 或粘贴 JS。

## 自动验证

统一入口同时汇总：

- Browser connected；
- WOF page found；
- Browser Fleet Discovery V2 Worker indicator；
- PYLAUNCH Worker；
- PYLAUNCH WASM / heap；
- exact World 921031；
- Recorder Discovery V2 admission；
- `readOnly=true`；
- `ramWrites=0`；
- `inputInjection=false`；
- no Worker replacement。

Fleet Worker indicator 明确保持 `cheap-indicator-only`，不会被当作 World identity authority。

## 唯一真人确认

自动项全部 PASS 后，只出现一次：

`当前 WOF 房间是否仍能正常运行？ Y / N`

这样既能确认 playability，又不通过 Input.* 或其他输入注入伪造真人 proof。

## 10-room gate

只有：

```text
Fleet Discovery V2 PASS
+ PYLAUNCH authoritative PASS
+ Recorder Discovery V2 admission PASS
+ safety PASS
+ owner playability CONFIRMED
```

才写：

```json
{
  "overallResult": "PASS",
  "tenRoomLongCaptureReady": true,
  "longCaptureAutoStarted": false
}
```

不会自动开始一小时长采集。

## Failure preservation

任一分支失败时：
- 总 JSON 仍保留 Fleet 已取得证据；
- 保留 PYLAUNCH 已取得证据；
- 保留 Recorder admission/最近输出；
- 保留子进程退出码和 blocker；
- 不把 GitHub/CI PASS 冒充真人 live PASS。

## Output

仓库模板：
- `UNIFIED_LIVE_PROOF_STATUS.json`

真人运行：
- `%LOCALAPPDATA%\WOF Future Danger\UnifiedLiveProof\runs\<run-id>\UNIFIED_LIVE_PROOF_STATUS.json`
- 稳定 latest copy：`%LOCALAPPDATA%\WOF Future Danger\UnifiedLiveProof\UNIFIED_LIVE_PROOF_STATUS.json`

最终 owner 只需要返回一个 JSON 或一张最终状态截图。

## Mock / offline regression

Bundle regression: **9/9 PASS**

Covered:
1. Fleet indicator remains non-authoritative;
2. all three automatic lanes are required;
3. missing Recorder admission fails closed;
4. safety violation fails closed;
5. playability confirmation is required for 10-room ready;
6. full PASS never auto-starts long capture;
7. partial failure preserves positive evidence;
8. Recorder admission marker detection;
9. repository PASS and live PASS remain distinct.

## Safety

Preserved:
- read-only;
- RAM writes 0;
- no input injection;
- no Worker replacement/wrap;
- no Blob/Data/ObjectURL Worker;
- no game-speed control;
- no attack automation;
- no Alpha changes.

## Stop condition

**UNIFIED LIVE PROOF READY — ONE OWNER WOF RUN REMAINS**

Repository-side unified proof bundle is complete. Stop here and do not require the owner to run it immediately; PM can decide when to schedule the single real Windows/WOF proof.
