# WOF Browser Future Danger — 新帖启动提示词

把下面整段作为新 ChatGPT 对话第一条消息：

```text
继续 WOF Browser Future Danger 主线，从 GitHub 当前权威状态直接接手，不要重新发散逆向。

仓库：
- ouyong520/wof-ai-private
- ouyong520/wof-winkawaks-bridge（只在需要查看并行 discovery 边界时读取）

开始前必须重新读取：
1. WOF_AI_NEW_THREAD_START.md
2. WOF_AI_HANDOFF.md
3. WOF_AI_CURRENT_FRONTIER.md
4. WOF_AI_MASTER_PROGRESS.md

GitHub 是权威状态。

强制协议：
- 我每轮 Browser 主线只执行 ONE 条 Console 命令并上传 JSON。
- 你负责先校验 copyId/project/version/marker/readOnly/ramWrites，再分析、更新 GitHub、推进版本、设计唯一下一轮。
- project 必须是 WOF-AI-PRIVATE，readOnly=true，ramWrites=0。
- enemy+0x7E 是 authoritative live target，不能冻结 warning-entry target。
- WinKawaks 只能作为 discovery evidence，不能直接当 Browser production proof。
- 不重新研究已经锁死的 selector / player table / dispatcher44 / descriptor consumer。
- 不复活 GitHub 文档里列出的 deprecated rules。

当前最新已完成：WOF-051。
当前唯一下一轮：WOF-052。
不要跳过 WOF-052。

继续时直接按 GitHub 的 WOF-052 状态推进；如果我上传 WOF-052 JSON，就立即校验、分析、写 Git、再给唯一下一条命令。
```
