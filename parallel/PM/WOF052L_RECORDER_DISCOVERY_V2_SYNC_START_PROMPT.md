# WOF-052L Recorder Worker Discovery V2 Sync — Fresh Start Prompt

你负责 WOF-052L Recorder 的独立兼容修复线。

背景：
- 真人 Windows 已证明旧 PYLAUNCH 仅依赖 browser-level `Target.getTargets` 会出现 `no gstyphoon worker target`；
- 最新 PYLAUNCH 已加入 page-session `Target.setAutoAttach` / related target tree / iframe -> Worker discovery v2，并完成 13/13 offline PASS；
- WOF-052L 长采集依赖稳定发现真实游戏 Worker，因此不能继续只假设顶层 `gstyphoon*.js` worker target 一定直接可见。

开始前读取：
- `parallel/PYLAUNCH/RESULT.md`
- `parallel/PYLAUNCH/wof_launcher/discovery_v2.py`
- `parallel/WOF052L_RECORDER/**`
- `parallel/WORKER_SURFACE/**`
- `parallel/PM/WOF052L_MULTIROOM_LIVE_CAPTURE_START_PROMPT.md`
- `parallel/PM/CHINESE_UI_UX_REQUIREMENT.md`

写入范围：只修改 `parallel/WOF052L_RECORDER/**` 及其测试/文档。
不要修改 `parallel/PYLAUNCH/**`。
不要修改 `product/alpha/**`。

目标：
1. 把最新、已验证的 Worker topology discovery 思路安全同步到 WOF-052L Recorder；
2. 支持 direct worker、page-attached worker、iframe -> worker、URL shape variation；
3. 仍然以 WASM/heap + exact World 921031 SHA-256 作为最终采集准入；
4. 多 page / 多 worker 关联不唯一时 fail closed，不跨房间串采；
5. reload / Worker replacement 后独立重发现，不继承旧 session 状态；
6. 保持 Fleet 每个 CDP endpoint 独立，不允许 child 跳到别的 endpoint；
7. 所有 owner-facing 状态/错误默认简体中文；
8. 不改变 WOF-052L 采集字段、T18/T23 研究语义或输出 schema，除非新增 topology diagnostics 字段且向后兼容；
9. 补 offline regression，至少覆盖旧 direct-worker、root worker 缺失但 page-attached worker 可见、iframe worker、ambiguity、wrong identity、WASM not ready、reload replacement、10 fleet endpoint isolation。

安全边界：
- readOnly=true
- ramWrites=0
- inputInjection=false
- no Worker replacement/wrap
- no Blob URL rewrite
- no game speed/input control

停止条件：
`WOF-052L DISCOVERY V2 READY — 可进入 10 房间真人长采集 proof`
或一个精确的真人 Chrome blocker。
