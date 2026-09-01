# WOF Project Status Scanner — Fresh Start Prompt

你负责 WOF 项目新的项目加速工具：Project Status Scanner / 项目状态扫描器。

这不是产品代码，不是攻击研究。

开始前读取：
- `parallel/PM/ACTIVE_PRIORITIES.md`
- `parallel/PM/OWNER_ACTIONS.md`
- `parallel/PM/RELEASE_READINESS.md`
- 当前 `parallel/**/RESULT*.md` / `IMPLEMENTATION_RESULT.md` / `AUDIT_STATUS.md`
- 最近 GitHub commits
- `parallel/PM/CHINESE_UI_UX_REQUIREMENT.md`

目标：把“检查所有帖子进度、哪些完成、哪些等待真人、哪些该关闭、下一步开什么新帖”自动化，减少 PM 每次人工翻大量目录的时间。

优先实现独立工具，例如 `parallel/PROJECT_STATUS/**`，只读扫描仓库。

要求：
- 只读；
- 自动扫描最近 commits；
- 自动发现常见结果文件；
- 输出各 lane 的状态：进行中 / 仓库侧 READY / 等待真人 / PASS / FAIL / BLOCKED / CLOSED；
- 自动提取 stop condition / remaining owner action；
- 自动标出可能重复的 active lanes；
- 自动标出已经完成但仍可能被误开的旧阶段；
- 自动给出 `当前 P0 / P1 / 非阻塞`；
- 自动给出 `Owner Action: YES/NO`；
- 自动给出 `Next Fresh Stage` 建议，但不得自行改产品代码；
- 自动生成一个机器可读 `PROJECT_STATUS.json`；
- 自动生成一个简体中文 `项目状态.txt`；
- 对信息冲突要标记 `NEEDS_PM_REVIEW`，不要猜；
- 可以被 `WOF_TOOLKIT.cmd` 调用；
- 用户可见文字全部简体中文。

理想输出类似：

```text
WOF 项目状态

P0：PYLAUNCH Worker 自动发现修复
状态：进行中

已完成：
- RC5 QA：PASS / CLOSED
- Browser Fleet：仓库侧 READY / 等待 Windows proof
- WOF-052L Recorder：READY / 等待 live Worker proof
- Operator Toolkit：Windows V1 READY

项目所有者当前操作：NO
下一阶段：PYLAUNCH PASS 后打开 Alpha Transport Integration
重复工作风险：无
```

不要修改 `product/alpha/**`。
不要修改 PYLAUNCH / Recorder / Fleet 的实现逻辑。
不要写游戏 RAM。
不要注入游戏输入。

做到仓库侧 READY，并让以后 PM 可以先读这一个状态文件再决定下一阶段。