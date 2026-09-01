# WOF Owner One-Click Package — PYLAUNCH Fix Refresh Stage

你负责把最新 PYLAUNCH Real Chrome Worker Discovery Fix 纳入 Owner 一键包。

背景：
- 一键包最近一次 Windows 验证完成后，PYLAUNCH 又合并了新的 Worker Discovery V2 修复；
- 当前必须避免 owner 下载到一个通过安装测试、但内部仍是旧 Worker discovery 的包。

开始前读取：
- `parallel/PYLAUNCH/RESULT.md`
- 最新 `parallel/PYLAUNCH/**`
- `parallel/OWNER_ONECLICK/**`
- 根目录 `WOF_一键工具.cmd`
- `parallel/PM/CHINESE_UI_UX_REQUIREMENT.md`

写入范围：
- `parallel/OWNER_ONECLICK/**`
- 根目录一键 bootstrap/manifest，如确实需要

不要修改 `parallel/PYLAUNCH/**` 实现。
不要修改 `product/alpha/**`。

目标：
1. 刷新 immutable/package manifest，使最新 PYLAUNCH discovery-v2、中文 proof、`WOF_ONECLICK_PROOF_CN.cmd` 被一键安装链完整包含；
2. 防止旧/新 PYLAUNCH 文件混装；
3. staging 全部完成后原子切换 current；失败保留 last-known-good；
4. 包版本必须明确可见；
5. Windows CI/测试必须验证安装后的 PYLAUNCH 文件 SHA/版本确实对应本次最新修复，而不仅仅验证文件存在；
6. 所有用户提示简体中文；
7. 最终给出一个稳定直接下载入口，owner 不需要 Git/GitHub Desktop/找目录。

至少测试：
- fresh install；
- update from previous package；
- partial download failure rollback；
- 中文路径/空格路径；
- 安装后 discovery-v2 文件存在且版本正确；
- 安装后可启动新的中文 Windows proof；
- 不要求真正进游戏完成此 packaging stage。

停止条件：
`OWNER ONE-CLICK PACKAGE REFRESH PASS — 最新 PYLAUNCH Worker Discovery Fix 已进入可直接下载包`
