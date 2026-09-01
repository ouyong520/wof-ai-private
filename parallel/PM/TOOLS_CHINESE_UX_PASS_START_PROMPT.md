# WOF Owner Tools — Fresh Simplified Chinese UX Pass

你负责一个全新的工具中文化 / UX 收口阶段。

仓库：
- `ouyong520/wof-ai-private`

## 开始前必须读取

- `parallel/PM/CHINESE_UI_UX_REQUIREMENT.md`
- `parallel/BROWSER_FLEET/**`
- `parallel/WOF052L_RECORDER/**`
- `parallel/OPTOOLKIT/**`
- `parallel/PM/ACTIVE_PRIORITIES.md`

## 目标

把目前已经完成仓库侧实现的 owner-facing 工具统一改成**简体中文默认界面**，让非程序员用户不需要看懂英文状态、错误、菜单或操作提示。

本阶段重点范围：
- Browser Fleet Manager
- WOF-052L Automatic Multi-Room Recorder
- WOF Windows Operator Toolkit
- 这些工具的 CMD/BAT/PowerShell 启动器、菜单、状态、帮助、错误和结果提示

PYLAUNCH 当前有独立的真人 Worker discovery P0 修复阶段。为避免写冲突，本阶段**不要修改 `parallel/PYLAUNCH/**`**；PYLAUNCH 中文化由它自己的 fresh fix stage 同步完成。

## 必须中文化

Owner 可见的：
- CMD 窗口标题
- 启动提示
- 菜单项
- 输入提示
- Browser / page / Worker 状态标签
- 在线房间/完成房间/采样计数
- 保存目录提示
- 关闭/重启/刷新命令说明
- 错误说明
- PASS / FAIL / WAITING 等展示值
- 诊断窗口说明
- README 中“真人怎么操作”的部分

示例：

```text
WOF 多房间浏览器管理器
浏览器实例：10
已启动：10
WOF 页面：已找到
Worker：已找到
只读模式：开启
游戏内存写入：0

[S] 刷新状态
[R] 重启一个房间
[X] 关闭一个房间
[A] 全部关闭
[Q] 退出管理器但保留浏览器
```

不要把内部兼容字段强行翻译：
- JSON key
- schema/version
- Python identifier
- CDP method
- protocol constant
- exact build/hash identifiers

但如果这些内部字段需要展示给 owner，显示层必须给中文标签和中文解释。

## Windows 中文兼容

必须验证：
- Windows 10/11 CMD/PowerShell 不出现乱码；
- 中文路径可正常处理；
- UTF-8/BOM/codepage 方案稳定；
- 简体中文错误信息不会破坏脚本控制流；
- 中文输出目录名不是硬依赖，用户仍可用任意合法路径。

## UX 原则

错误第一行先说人话，再给技术详情。

例如：

```text
未找到可连接的 WOF 浏览器房间。
游戏本身没有受到影响。
请确认房间已经打开，然后选择“刷新状态”。

技术详情：no live fleet endpoint
```

不要只显示英文异常栈。

## 安全边界

本阶段只做 UI/UX/本地化，不改变核心采集或游戏逻辑。

禁止：
- 修改 `product/alpha/**`；
- 修改 `parallel/PYLAUNCH/**`；
- 新增 RAM writes；
- 新增 input injection；
- 替换/包装 Worker；
- 改攻击规则；
- 改 WOF-052L 研究判定标准。

## 回归要求

至少跑并记录：
- Browser Fleet offline regression
- WOF-052L self-test / relevant offline regression
- Operator Toolkit tests
- 中文 CLI smoke tests
- 中文路径 smoke test
- 英文内部 JSON/schema compatibility check

## Stop condition

直到：

**CHINESE OWNER UX PASS — Browser Fleet / WOF-052L / Operator Toolkit repository-side owner-facing workflow all Simplified Chinese by default**

或者给出一个明确的平台乱码/兼容阻断点。
