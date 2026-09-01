# WOF Project Status Scanner / 项目状态扫描器

状态：**REPOSITORY-SIDE READY**

这是一个仓库只读项目加速工具。它不会修改 `product/alpha/**`，不会写游戏 RAM，也不会注入游戏输入。

## 最简单用法

Windows：

```text
双击 parallel\PROJECT_STATUS\RUN_PROJECT_STATUS.cmd
```

输出：

- `parallel/PROJECT_STATUS/PROJECT_STATUS.json` — 机器可读状态；
- `parallel/PROJECT_STATUS/项目状态.txt` — 简体中文 PM/Owner 摘要。

也可以直接运行：

```text
python parallel/PROJECT_STATUS/scan_project_status.py
```

## 扫描内容

扫描器会自动读取：

- `parallel/PM/ACTIVE_PRIORITIES.md`
- `parallel/PM/OWNER_ACTIONS.md`
- `parallel/PM/RELEASE_READINESS.md`
- `parallel/PM/CHINESE_UI_UX_REQUIREMENT.md`
- `parallel/**/RESULT*.md`
- `parallel/**/IMPLEMENTATION_RESULT.md`
- `parallel/**/AUDIT_STATUS.md`
- `parallel/PM/*_START_PROMPT.md`
- 最近 Git commits 及其改动路径

## 输出判断

每个 lane 使用以下标准状态：

- `进行中`
- `仓库侧 READY`
- `等待真人`
- `PASS`
- `FAIL`
- `BLOCKED`
- `CLOSED`
- `NEEDS_PM_REVIEW`

冲突不会自动猜测。例如同一 lane 同时出现当前 `PASS` 和当前 `FAIL`，扫描器会标记 `NEEDS_PM_REVIEW`。

扫描器还会输出：

- 当前 P0 / P1 / 非阻塞；
- `Owner Action: YES/NO`；
- PM Fresh Stage 调度动作（与真人操作分开）；
- stop condition；
- remaining owner action；
- 可能重复/边界重叠的 active lanes；
- 已完成但可能被误开的旧阶段；
- `Next Fresh Stage` 建议；
- 最近 commits；
- PM 文件与近期实现提交可能发生的状态漂移。

## Owner Action 语义

`Owner Action` 专指 **是否需要项目所有者现在执行真人 Windows / Browser 操作**。

“需要开一个新的 fresh engineering stage”属于 PM 调度，不等于真人 Browser 操作。JSON 中两者分开：

```json
{
  "owner_action": {
    "required": "NO",
    "pm_stage_dispatch_required": "YES"
  }
}
```

这避免 `OWNER_ACTIONS.md` 中“YES — 只需开 fresh stage”被误读成“现在需要再次进游戏做真人测试”。

## WOF Toolkit 调用

`RUN_PROJECT_STATUS.cmd` 是稳定的 Windows 入口，`WOF_TOOLKIT.cmd` 可以直接 `call` 它；Scanner 本身不要求 Toolkit 改菜单，也不会与 Toolkit/Browser Fleet/Recorder/PYLAUNCH 的实现逻辑耦合。

示例调用：

```bat
call "%REPO_ROOT%\parallel\PROJECT_STATUS\RUN_PROJECT_STATUS.cmd"
```

## CI / 离线验证

标准库实现，无第三方 Python 依赖。单元测试：

```text
python -m unittest discover -s parallel/PROJECT_STATUS/tests -p "test_*.py" -v
```

CI 会在 Linux 上验证：

1. Python 编译；
2. 单元测试；
3. 对当前仓库执行一次只读扫描到临时目录；
4. 校验 JSON schema 和中文摘要存在。

## 安全边界

Scanner 不执行以下操作：

- 不修改 `product/alpha/**`；
- 不修改 PYLAUNCH / Recorder / Fleet 实现逻辑；
- 不连接游戏进程；
- 不连接 CDP；
- 不写游戏 RAM；
- 不注入键盘/鼠标/手柄输入；
- 不替换 `window.Worker`。

它只读取本地仓库文本文件和本地 `git log`。
