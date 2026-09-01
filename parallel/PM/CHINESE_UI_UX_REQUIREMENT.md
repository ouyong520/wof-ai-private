# WOF Project — Chinese UI / UX Requirement

Updated: 2026-09-01

## Product decision

All owner-facing WOF tools must use **Simplified Chinese by default**.

This applies project-wide to current and future tools, including but not limited to:
- Python Launcher / future EXE launcher
- Browser Fleet Manager
- WOF-052L Recorder
- WOF Operator Toolkit
- Windows proof helpers
- diagnostics/status windows
- tray menus
- CMD / BAT / PowerShell prompts
- save-folder prompts
- error messages
- pass/fail summaries
- packaging/install/update helpers
- future Beta/v1 desktop tooling

## Required owner-facing language

Owner-visible text should be Chinese wherever practical:
- window titles
- buttons and menus
- status labels
- setup instructions
- warnings
- errors
- success/failure messages
- help text
- save/output descriptions
- interactive prompts

Examples:

```text
浏览器：已连接
WOF 页面：已找到
Worker：已找到
WASM / 内存：已找到
游戏版本：World 921031 已确认
只读模式：开启
游戏内存写入：0
```

Instead of owner-facing English such as:

```text
Browser: OK
Worker: OK
WAITING_WOF
Download failed
Diagnostics
```

## Internal compatibility exception

Internal machine-facing identifiers may remain English when changing them would risk compatibility or create unnecessary churn, including:
- source-code identifiers
- Python variable/class/function names
- JSON keys / schema fields
- protocol names
- CDP method names
- file formats consumed by automation
- exact technical constants and build identifiers

If internal JSON remains English, any UI rendering that shows it to the owner should translate the field labels and status values into Chinese where practical.

## Error UX

Do not show raw technical errors as the only owner-facing message.

Preferred pattern:

```text
未找到 WOF 游戏 Worker。
游戏本身没有受到影响。
请保持游戏房间打开，然后点击“重新连接”。

技术详情：no gstyphoon worker target
```

Technical detail may be shown secondarily for debugging, but the first-line explanation must be Chinese and understandable to a non-programmer.

## Command-line UX

CMD / BAT tools should also be Chinese. Example:

```text
WOF 多房间采集器
保存目录：D:\WOF_CAPTURE
浏览器：已连接
在线房间：8
已完成房间：15
T18 样本：3482
只读模式：开启
游戏内存写入：0
```

## Scope boundary

This is a UX/localization requirement only. It does not authorize:
- RAM writes
- gameplay input injection
- Worker replacement
- Alpha rule changes
- attack research expansion

## Acceptance requirement

A tool is not considered owner-ready if the normal owner workflow still requires understanding English-only status/error text.
