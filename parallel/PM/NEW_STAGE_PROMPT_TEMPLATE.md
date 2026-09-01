# PM New Stage Prompt Template

所有从 2026-09-01 起新建的 `parallel/PM/*_START_PROMPT.md` 必须在最前面包含：

```text
stageId: <UNIQUE_STAGE_ID>

开始前必须先读取：
`parallel/PM/STAGE_DEDUP_GUARD.md`

先执行 DONE 检查和 Stage Claim。
若已完成：输出 `ALREADY COMPLETE — SAFE TO CLOSE` 并停止。
若已有 claim：输出 `ALREADY CLAIMED — SAFE TO CLOSE` 并停止。
只有 claim 成功后才允许继续本阶段任务。
```

然后再写正常的 scope、write ownership、inputs、outputs、tests、safety、stop condition。

PM 给 Owner 的启动方式保持不变：Owner 仍只需要让 fresh chat 读取具体 `*_START_PROMPT.md`。Owner 不需要手工处理 claim。
