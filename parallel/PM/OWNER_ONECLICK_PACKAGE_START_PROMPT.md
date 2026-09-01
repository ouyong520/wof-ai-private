# WOF Owner One-Click Package — Fresh Acceleration Stage

你负责一个全新的“降低 owner 操作复杂度”项目加速工具阶段。

仓库：
- `ouyong520/wof-ai-private`

## 背景

Owner 已明确表示：
- 不会 GitHub Desktop；
- 不希望找 `parallel/PYLAUNCH` 等目录；
- 不希望下载整个仓库后再找文件；
- 希望我给一个直接下载地址；
- 理想操作是“下载一个文件 -> 双击 -> 自动完成剩下的事情”。

此前真人 PYLAUNCH proof 已经证明这种简化非常重要。

## 开始前读取

- `parallel/PM/CHINESE_UI_UX_REQUIREMENT.md`
- `parallel/OPTOOLKIT/**`
- `parallel/BROWSER_FLEET/**`
- `parallel/WOF052L_RECORDER/**`
- `parallel/PYLAUNCH/**` 只读参考其现有一键 proof 入口
- `parallel/PM/ACTIVE_PRIORITIES.md`

## 目标

做一个**直接可下载、简体中文、单文件或极小包的 Owner Bootstrap/Installer**。

理想最终 UX：

```text
点击一个下载地址
-> 得到“WOF_一键工具.cmd”或一个很小的 ZIP
-> 放桌面并双击
-> 自动下载/更新所需组件到固定本地目录
-> 自动准备 Python 环境/依赖
-> 打开中文 WOF Toolkit
```

Owner 不需要：
- Git
- GitHub Desktop
- 找仓库目录
- 找 `parallel/**`
- 手工复制 PowerShell
- 手工下载十几个 Python 文件
- 理解 venv/pip

## 推荐实现

优先实现一个安全的、仓库根目录可直接 Raw 下载的 bootstrap CMD，例如：

`WOF_一键工具.cmd`

它可以：
- 从 GitHub `main` 或一个明确版本 manifest 下载固定的工具文件；
- 保存到 `%LOCALAPPDATA%\WOF Future Danger\Tools` 或其他清晰固定目录；
- 自动创建目录；
- 自动检测 Python 3；
- 自动准备共享 venv/依赖；
- 自动启动 `WOF_TOOLKIT.cmd` / Python Toolkit；
- 以后再次双击可自动检查/更新；
- 下载/更新失败时保留已有可用版本并给中文提示；
- 不因为更新失败影响游戏或浏览器。

如果纯 CMD 不够稳，可生成一个很小 ZIP，但必须给出**一个直接下载地址**，而不是让 owner 浏览 GitHub 目录。

## 中文要求

所有 owner-facing 提示必须简体中文：

```text
正在下载 WOF 工具...
正在检查 Python...
工具已准备完成。
正在打开 WOF 工具箱...

下载失败，旧版本仍然保留。
游戏本身没有受到影响。
```

技术详情可附在后面。

## 版本/完整性

必须避免“部分文件新、部分文件旧”的混装。

需要一种简单的原子/manifest 方案，例如：
- manifest 定义版本和文件清单；
- 下载到 staging；
- 全部成功后再原子切换 current；
- 下载失败不破坏 last-known-good；
- 可记录安装版本；
- owner 可看到“当前工具版本”。

不要做复杂企业安装器；第一版目标是可靠和简单。

## 组件范围

Bootstrap/packager 可以安装/启动已经存在的工具：
- Operator Toolkit
- Browser Fleet Manager
- WOF-052L Recorder
- PYLAUNCH/Windows proof（只调用其已有入口，不在本阶段修 Worker discovery 逻辑）

本阶段不要复制重写这些工具的核心实现。

## 安全边界

禁止：
- 修改 `product/alpha/**`；
- 修改攻击规则；
- 增加 RAM 写入；
- 增加游戏输入注入；
- Worker replacement/wrap；
- Chrome process-memory hook；
- 自动登录/保存用户密码；
- 绕过浏览器安全限制。

下载源限制到明确的官方项目 GitHub 路径，不执行任意远程 URL/任意用户脚本。

## 测试

必须覆盖至少：
- 首次安装；
- 已安装再次运行；
- 更新成功；
- 下载中断；
- 某个文件下载失败；
- Python 缺失；
- 中文 Windows 用户路径；
- 路径含空格；
- last-known-good 回滚；
- 组件启动失败不破坏安装；
- owner-facing 中文无乱码。

## Stop condition

直到：

**OWNER ONE-CLICK PACKAGE READY — PM 可以直接给 owner 一个下载链接，owner 只需下载并双击，不再需要理解仓库目录。**

最终结果必须明确给出：
- 直接下载 URL；
- 文件名；
- owner 只需做的 1~2 个动作；
- 出错时只需返回的一个日志/截图位置。
