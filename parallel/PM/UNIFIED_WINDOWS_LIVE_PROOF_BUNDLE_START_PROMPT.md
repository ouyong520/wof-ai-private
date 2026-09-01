# WOF Unified Windows Live Proof Bundle — Fresh Start Prompt

你负责一个新的“拼线型”Windows 真人验证准备阶段。

目标不是修改 Alpha，也不是重复实现 PYLAUNCH / Browser Fleet / WOF-052L Recorder，而是把它们当前已经 READY 的真实 Windows 验证压缩成 **owner 一次操作**。

读取：
- `parallel/PYLAUNCH/**`
- `parallel/BROWSER_FLEET/**`
- `parallel/WOF052L_RECORDER/**`
- `parallel/WOF052L_LIVE_CAPTURE/**`
- `parallel/WOF052L_ANALYSIS/**`
- `parallel/WORKER_SURFACE/**`
- `parallel/OWNER_ONECLICK/**`
- `parallel/PM/CHINESE_UI_UX_REQUIREMENT.md`

写入范围：仅 `parallel/LIVE_PROOF_BUNDLE/**`。
不要修改以上工具核心实现；发现问题只报告给对应 fresh fix stage。

## 目标 UX

未来 owner 只需要：

```text
下载/双击一个中文入口
-> 自动准备最新版工具
-> 启动 1 个专用 WOF Browser 做短验证
-> owner 正常进入一个 WOF 房间
-> 自动同时验证：
   PYLAUNCH Browser/page/Worker/WASM/World 921031
   Browser Fleet Discovery V2
   WOF-052L Recorder Discovery V2 admission
   readOnly=true / ramWrites=0 / inputInjection=false
   游戏仍然可正常运行
-> 自动生成一个中文总结果 + 一个 JSON
```

如果上述短验证全部 PASS，工具可以提示“已具备 10 房间长采集条件”，但不要未经 owner 同意自动开始一小时长采集。

## 必须做到

- 不要求 DevTools；
- 不要求 Worker Console；
- 不要求粘 JS；
- 不要求 owner 分别跑 3~4 个 proof；
- 不把 GitHub Actions Windows runner 冒充 owner 真实 WOF proof；
- 真实 WOF Worker / WASM / World gate 必须来自实际 Browser room；
- 一处失败不能让其他证据丢失；
- 汇总结果明确区分：仓库/CI PASS 与真人 live PASS；
- 所有 owner-facing 提示简体中文；
- 最终只要求 owner 返回一个 JSON 或一张截图。

## 输出

至少：
- `RUN_WOF_UNIFIED_LIVE_PROOF.cmd`
- `UNIFIED_LIVE_PROOF_STATUS.json`
- 中文状态窗口/CLI
- mock/offline regression
- README
- RESULT.md

## 安全

read-only / ramWrites=0 / no input injection / no Worker replacement / no Blob Worker / no product Alpha changes。

## Stop condition

`UNIFIED LIVE PROOF READY — ONE OWNER WOF RUN REMAINS`

做到这个 stop condition 后停止，不要求 owner 立即执行；由 PM 统一决定什么时候真人跑。