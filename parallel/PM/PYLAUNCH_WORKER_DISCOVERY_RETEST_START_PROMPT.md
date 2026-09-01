# WOF PYLAUNCH Worker Discovery — Fresh Real Windows Retest

你负责最新 PYLAUNCH Worker Discovery V2 修复后的全新真人 Windows/Chrome Retest 阶段。

这是 fresh retest，不是继续开发旧 fix stage。

开始前读取：
- `parallel/PYLAUNCH/RESULT.md`
- 最新 `parallel/PYLAUNCH/**`
- `parallel/PM/PYLAUNCH_WORKER_DISCOVERY_FIX_START_PROMPT.md`
- 当前 Worker Surface audit 结果（如已有）
- `parallel/PM/CHINESE_UI_UX_REQUIREMENT.md`

已知旧真人证据：
- Browser/CDP OK
- 房间正常可玩
- readOnly=true
- ramWrites=0
- 旧 discovery 得到 `no gstyphoon worker target`

当前修复已经仓库侧完成：
- discovery_v2 page-session auto-attach / related target tree；
- iframe -> Worker；
- Worker URL variation；
- exact World 921031 gate；
- 13/13 offline PASS；
- 中文 owner UX。

你的目标只有一个：把新的真人 proof 压成最简单的一次操作，并接收结果。

Owner UX 必须是：
`直接下载一个中文一键文件 -> 双击 -> 自动打开/连接专用 Chrome/Edge -> 正常进入 WOF 房间 -> 自动判断`

不要要求：
- Git/GitHub Desktop
- 找仓库目录
- DevTools
- Worker Console
- 粘 JS
- 手工找 JSON

自动 PASS 必须同时满足：
- 浏览器：已连接
- WOF 页面：已找到
- Worker：已找到
- WASM / 内存：已找到
- World 921031：已确认
- readOnly=true
- ramWrites=0
- inputInjection=false
- owner 确认房间仍正常可玩

如果失败：只让 owner 返回一个自动生成的 `WINDOWS_PROOF_STATUS.json` 或截图。不得要求额外技术操作。

本 Retest 阶段原则上不修改代码。若真人 proof 暴露明确 P0/P1，则记录精确证据并停止，交给新的 fresh fix stage；不要在 Retest 帖内继续大修。

如果 PASS：写回 GitHub，明确 `PASS — PYLAUNCH WORKER DISCOVERY REAL WINDOWS PROOF`，然后停止。PM 将立即开启 Alpha Safe Transport Integration。
