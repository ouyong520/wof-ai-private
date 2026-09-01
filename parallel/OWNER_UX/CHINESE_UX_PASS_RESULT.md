# WOF Owner Tools 简体中文 UX Pass — 结果

Updated: 2026-09-01  
Overall: **PASS**

最终结论：

**CHINESE OWNER UX PASS — Browser Fleet / WOF-052L / Operator Toolkit repository-side owner-facing workflow all Simplified Chinese by default**

## 范围

本阶段只处理 owner 能直接看到的文字与入口：

- Browser Fleet
- WOF-052L Recorder
- Operator Toolkit
- 根目录 `WOF_TOOLKIT.cmd`
- 与当前工具安装链路兼容性检查

本阶段没有修改：

- `parallel/PYLAUNCH/**`
- `product/alpha/**`
- 游戏逻辑
- 攻击规则
- WOF-052L 研究判定标准
- 游戏 RAM 写入或输入注入行为

## Browser Fleet — PASS

默认双击入口：

`parallel/BROWSER_FLEET/RUN_WOF_FLEET.cmd`

现在默认显示简体中文：

- CMD 标题与启动提示
- 浏览器房间数量输入
- Browser / WOF 页面 / Worker 状态
- 房间编号、PID、独立 profile
- 刷新 / 重启 / 关闭一个 / 全部关闭 / 保留浏览器退出
- 错误说明
- 安全状态
- README owner 使用说明

正常入口调用 `fleet_owner_zh_cn.py`。底层 `fleet_manager.py` 和 `instances.json` 机器契约保持原有英文 key/schema/status 兼容性。

## WOF-052L Recorder — PASS

默认双击入口：

`parallel/WOF052L_RECORDER/RUN_WOF052L_RECORDER.cmd`

现在默认显示简体中文：

- 首次环境准备
- 保存目录选择
- Browser 等待 / 已连接
- 在线房间 / 已完成房间
- T18/T23 样本与候选计数
- Worker/房间 attach/finalize 提示
- Ctrl+C 停止提示
- merged JSON 保存提示
- self-test PASS
- 错误说明
- README owner 使用说明

错误默认先显示中文人话，再显示 `技术详情：...`。

底层 `recorder.py`、`fleet_recorder.py`、`worker_probe.js`、JSON schema/key 和研究逻辑未修改。

## Operator Toolkit — PASS

根入口：

`WOF_TOOLKIT.cmd`

现在默认使用 UTF-8/简体中文 owner 路径，菜单包含：

1. 更新项目
2. 启动 Python Launcher
3. 启动多房间采集器
4. 启动多房间浏览器
5. 运行回归测试
6. 运行真人 Windows 验证
7. 收集诊断信息
8. 打包结果
9. 打开结果目录
0. 退出

状态、错误、保存提示以及通过/失败/缺失/受阻/需要关注等 owner-facing 展示均为中文。

Toolkit 的 Recorder 动作显式进入 `parallel/WOF052L_RECORDER/owner_zh_cn.py`，避免从中文菜单启动后子窗口重新退回英文。Fleet 动作继续进入已经中文化的 `RUN_WOF_FLEET.cmd`。

## Windows UTF-8 / 中文路径验证 — PASS

GitHub Actions workflow：

`.github/workflows/owner-tools-chinese-ux.yml`

最终验证 run：`33506500512`

### Windows job `windows-utf8-smoke` — PASS

Job: `99851686574`

已通过：

- 真实 Windows `cmd.exe` + `chcp 65001` 输出 `简体中文 CMD 输出正常`
- PowerShell + Python UTF-8 输出中文正常
- Windows 中文目录 `中文路径/状态.json` 创建、写入、读取正常
- 中文 JSON 内容正常，英文机器字段 `schema/status/readOnly/ramWrites` 保持兼容
- 三个中文 owner frontend 在 Windows 上 `py_compile` 通过
- 实际调用 `RUN_WOF052L_RECORDER.cmd --self-test` 通过
- 输出 `自检通过 — WOF-052L 采集器安全约束与序列汇总正常`
- Operator Toolkit 中文 CLI/中文路径 smoke 通过

Hosted Windows 环境为 Windows Server 2025 / NT 10.0.26100；本阶段已经直接验证 Windows `cmd.exe` / PowerShell UTF-8 与中文路径链路。个人 Windows 10/11 的字体/终端视觉差异不构成仓库侧 blocker。

### Offline job `offline-ux-regression` — PASS

Job: `99851686810`

已通过：

- Browser Fleet offline regression
- WOF-052L self-test
- WOF-052L Fleet manifest regression
- Operator Toolkit existing tests
- Simplified Chinese CLI smoke
- Chinese path smoke
- internal English JSON/schema compatibility smoke

## 一键工具兼容性 — PASS

当前根目录还存在并发 owner-tool lane 创建的：

`WOF_一键工具.cmd`

该入口本身已经是简体中文。

当前 `parallel/OWNER_ONECLICK/package_manifest.json` 已包含：

- `WOF_TOOLKIT.cmd`
- `parallel/OPTOOLKIT/owner_zh_cn.py`
- `parallel/WOF052L_RECORDER/RUN_WOF052L_RECORDER.cmd`
- `parallel/WOF052L_RECORDER/owner_zh_cn.py`
- `parallel/BROWSER_FLEET/RUN_WOF_FLEET.cmd`
- `parallel/BROWSER_FLEET/fleet_owner_zh_cn.py`

因此当前一键安装/更新包不会因为漏装中文 frontend 而退回英文默认 owner 路径。

## 机器契约保持英文

有意保持英文、不做翻译的内容包括：

- JSON key
- schema/version
- Python 变量名
- CDP method 名称
- manifest 内部 status 值
- safety machine fields，例如 `readOnly`, `ramWrites`, `inputInjection`

这是兼容性要求，不属于 owner-facing 英文残留。

## 安全边界

本阶段保持：

- read-only
- `ramWrites=0`
- no gameplay input injection
- no `window.Worker` replacement
- no Blob Worker / game Worker URL rewrite changes
- no Alpha/game logic changes

## Stop condition

没有发现仍然阻断这次简体中文 owner UX 的 P0/P1。

**CHINESE OWNER UX PASS — Browser Fleet / WOF-052L / Operator Toolkit repository-side owner-facing workflow all Simplified Chinese by default**
