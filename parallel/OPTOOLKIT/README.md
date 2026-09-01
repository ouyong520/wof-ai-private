# WOF Windows 操作工具箱

状态：**Windows V1 仓库侧已就绪，默认简体中文 owner 界面**。

仓库根目录入口：

```text
WOF_TOOLKIT.cmd
```

工具箱只是操作外壳，不重新实现 Alpha、PYLAUNCH、WOF-052L Recorder 或 Browser Fleet。它调用仓库现有工具，把常用操作统一到一个中文菜单，并把结果集中到一个目录。

默认结果目录：

```text
%USERPROFILE%\Documents\WOF_RESULTS
```

需要时可以用环境变量 `WOF_RESULTS_DIR` 改到其他合法路径，包括中文路径。

## 你实际看到的菜单

```text
1 更新项目
2 启动 Python Launcher
3 启动多房间采集器
4 启动多房间浏览器
5 运行回归测试
6 运行真人 Windows 验证
7 收集诊断信息
8 打包结果
9 打开结果目录
0 退出
```

顶部固定显示：
- 项目目录；
- 结果目录；
- 只读模式；
- 游戏内存写入 0；
- Recorder / Browser Fleet 是否已就绪。

正常 owner 工作流不再要求理解 `READY / MISSING / PASS / FAIL / BLOCKED / ATTENTION` 等英文状态；显示层分别使用“已就绪 / 缺失 / 通过 / 失败 / 受阻 / 需要关注”。内部 JSON 状态值为了兼容仍保持英文。

## 1 更新项目

执行 Git fetch + 只允许 fast-forward 的 pull。

如果存在本地修改，工具箱不会覆盖，会用中文提示“发现本地未提交修改”，并保留你的工作。

更新后如果代码发生变化，工具箱会提示重新打开 `WOF_TOOLKIT.cmd`。

## 2 启动 Python Launcher

调用现有 `parallel/PYLAUNCH/launcher.py`。本中文 UX 阶段不修改 `parallel/PYLAUNCH/**`；PYLAUNCH 自己的中文化由它的独立修复阶段负责。

## 3 启动多房间采集器

从中文工具箱启动时会进入 WOF-052L 的中文 owner 入口，并把保存目录统一到：

```text
<WOF_RESULTS>\recorder
```

采集器自身的 JSON schema/key 不会被翻译。

## 4 启动多房间浏览器

调用：

`parallel/BROWSER_FLEET/RUN_WOF_FLEET.cmd`

它已经是简体中文默认界面，支持 1 / 5 / 10+ 独立浏览器房间、刷新状态、重启一个房间、关闭一个房间或全部关闭。

## 5 运行回归测试

复用现有测试，不重复实现断言：
- Alpha 产品 regression；
- RC5 独立 bootstrap retest；
- WOF-052L self-test；
- PYLAUNCH Python tests；
- Browser Fleet tests；
- Operator Toolkit tests。

结果保存到：

`WOF_RESULTS\regression_<timestamp>`

显示层使用“通过 / 失败 / 缺失 / 受阻 / 需要关注”；`regression_summary.json` 内部仍使用原来的英文机器字段和值。

## 6 运行真人 Windows 验证

复用现有 PYLAUNCH proof 路径：

```text
launcher.py --proof-json <WOF_RESULTS>\live_proof_<timestamp>\WINDOWS_PROOF_STATUS.json
```

不增加 DevTools 或 Worker Console 操作。

## 7 收集诊断信息

生成：

`WOF_RESULTS\diagnostics_<timestamp>`

会收集当前可用的 proof/result、RC5 QA、Alpha regression 结果副本、PM 状态、Git/Python/Node/平台信息、Browser Fleet manifest、最近 WOF-052L merged JSON 和 Toolkit log。

成功后显示“诊断信息已保存：...”而不是英文 `Diagnostics saved`。

## 8 打包结果

在：

`WOF_RESULTS\packages`

生成 ZIP，包含最新 diagnostics、regression、live-proof，以及可用的最近 WOF-052L merged JSON。

`PACKAGE_MANIFEST.json` 继续保持英文内部字段，不为了中文 UI 改 schema。

## 9 打开结果目录

在 Windows Explorer 打开统一结果目录。

## Windows 中文兼容

`WOF_TOOLKIT.cmd` 会：
- 先切换 `chcp 65001`；
- 设置 `PYTHONUTF8=1`；
- 设置 `PYTHONIOENCODING=utf-8`；
- 再输出中文标题、菜单和错误；
- Python/pip 技术日志不会作为唯一错误信息直接甩给用户。

路径全部通过 `%ROOT%` / `Path` / 引号处理，不依赖英文目录名；中文项目路径和中文结果路径属于 smoke-test 范围。

## 环境行为

工具箱会：
- 从自己的位置自动寻找项目根目录；
- 检测 `py -3` 或 `python`；
- 复用/创建外部 venv；
- 安装现有 PYLAUNCH 和 WOF-052L requirements；
- 不在 Git checkout 中创建新的 Toolkit/PYLAUNCH/Recorder venv 逻辑。

一键打包模式如果提供 `PACKAGE_MANIFEST.json` / `WOF_TOOLKIT_PYTHON`，根 CMD 会继续保留该兼容行为。

## 安全边界

Toolkit 固定安全声明仍然是：

```json
{"readOnly": true, "ramWrites": 0, "inputInjection": false}
```

本中文化阶段不会：
- 修改 `product/alpha/**`；
- 修改 `parallel/PYLAUNCH/**`；
- 写游戏 RAM；
- 注入键盘/鼠标/手柄游戏输入；
- 替换 `window.Worker`；
- 创建 Blob Worker；
- 改写 Worker URL；
- 改游戏逻辑或攻击规则。

## 错误显示原则

错误第一行先说中文人话，例如：

```text
启动失败。
游戏本身没有受到影响。
技术详情：<原始异常>
```

技术详情仍会保留，方便排查，但不会作为唯一 owner-facing 信息。

## 离线验证

仓库根目录：

```text
python -m py_compile parallel/OPTOOLKIT/toolkit.py parallel/OPTOOLKIT/owner_zh_cn.py
python -m unittest discover -s parallel/OPTOOLKIT/tests -p test_*.py -v
```

中文 UX 回归另外检查 CMD UTF-8 设置、中文菜单/错误、中文路径写入，以及内部 JSON/schema 兼容性。
