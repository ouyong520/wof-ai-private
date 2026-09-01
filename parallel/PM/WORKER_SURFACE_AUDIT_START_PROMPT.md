# WOF Chrome Worker Surface Audit — Fresh Start Prompt

你负责 WOF 项目独立并行线：真实 Chrome Worker Surface / CDP Target 暴露审计。

目的：独立查清真人 Windows 里为什么游戏已正常运行，但 PYLAUNCH 得到 `no gstyphoon worker target`。

这是诊断/审计线，不是 PYLAUNCH 修复线。

读取：
- `parallel/PYLAUNCH/**`
- `parallel/BROWSER_FLEET/**`
- `parallel/WOF052L_RECORDER/**`
- 当前 PM Worker discovery blocker
- 真人 proof 已知结果：Browser/CDP OK、游戏正常、worker_found=false、`no gstyphoon worker target`

写入范围：仅新目录 `parallel/WORKER_SURFACE/**`。
不要修改 `parallel/PYLAUNCH/**`，避免和主修复帖撞代码。

目标：
- 审计 Chrome/Edge 当前版本中 dedicated worker / shared_worker / service_worker / iframe / target flattening 的真实 CDP 暴露方式；
- 检查 `Target.getTargets` 是否足够；
- 检查是否需要 `Target.setDiscoverTargets` / auto-attach / execution-context 事件才能看到游戏 Worker；
- 检查 Worker URL 是否可能不再以 `gstyphoon*.js` 形式直接暴露；
- 检查 worker 是否可能嵌在 page/iframe execution context；
- 检查 openerId/page 关联假设；
- 使用离线 mock / Chromium CDP 文档/现有代码构造可复现诊断；
- 如最终必须真人 Windows，只生成一个“一键中文诊断 CMD”，自动输出一个 JSON，不要求 DevTools、不要求手选 Worker、不要求粘 JS。

输出必须给出：
1. 最可能根因排序；
2. 可实施修复建议给 PYLAUNCH 主修复帖；
3. 若需要真人证据，只要一个最小中文一键操作。

安全边界：
- read-only；
- no RAM writes；
- no input injection；
- no Worker replacement；
- no product/alpha changes。

持续到：根因锁定，或只剩一个最小真人诊断。