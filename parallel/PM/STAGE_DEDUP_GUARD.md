# WOF PM Stage Dedup / Claim Guard

Updated: 2026-09-01

Status: **MANDATORY FOR ALL NEW PM START PROMPTS**

目的：Owner 可以放心重复复制某个 start prompt。重复启动不应重复做项目工作。

## 1. 启动前必须先做 DONE 检查

任何新执行帖在修改代码、生成大文件、启动测试前，必须先重新读取 GitHub 默认分支最新状态，并检查：

- 目标 lane 的 `RESULT.md` / `STATUS.md` / `*_RESULT.md` / `*_STATUS.md`；
- 与本 stage stop condition 等价的最新 commit；
- 是否已有后继阶段明确消费了本阶段结果；
- 是否已有同语义实现，只是文件名或旧 prompt 不同。

如果 stop condition 已经满足，必须立即停止，不重复实现，也不为了“有活干”扩 scope。

Owner-facing 最终只输出：

`ALREADY COMPLETE — SAFE TO CLOSE`

并指出现有 result/commit。

## 2. 未完成时必须做原子 Stage Claim

每个新 PM start prompt 必须声明稳定且唯一的：

`stageId: <UPPER_SNAKE_CASE_STAGE_ID>`

真正开始工作前，线程必须尝试在：

`parallel/PM/STAGE_CLAIMS/<stageId>.json`

创建 claim 文件。

建议内容：

```json
{
  "schema": "wof-pm-stage-claim-v1",
  "stageId": "...",
  "promptPath": "parallel/PM/..._START_PROMPT.md",
  "state": "ACTIVE",
  "startCommit": "<main HEAD at claim time>",
  "startedAtUtc": "<ISO-8601>"
}
```

GitHub create-file 是原子门：

- 创建成功：本线程获得该 stage；继续执行。
- 文件已存在 / create 失败：必须重新读取该 claim 和 GitHub 最新结果；不得直接继续实现。

若已存在 claim 且 stage 尚未完成，Owner-facing 输出：

`ALREADY CLAIMED — SAFE TO CLOSE`

然后停止。

这意味着 Owner 即使在多个窗口里误复制同一个 prompt，最多只有一个线程进入真正执行阶段。

## 3. Stage 完成 / 阻断时更新 claim

达到 stop condition 后，将自己的 claim 更新为：

- `COMPLETE`：stage 已完成；附 result path / result commit；或
- `BLOCKED`：精确 blocker 已记录；附 blocker result path / commit。

不得删除历史 claim。一个 stage 一次性使用；修复、retest、下一阶段必须使用新的 stageId 和新的 fresh chat。

## 4. Stale claim

如果 claim 是 `ACTIVE`，但对应线程明显已经丢失/停止且没有结果：

- 普通执行线程不得自行抢占；
- 由 PM 审计后创建新的 recovery stageId，或由 PM 明确标记旧 claim 为 superseded。

这样避免两个线程同时认为自己拥有同一任务。

## 5. 等价任务去重优先于文件名

不能只比较 prompt 文件名。以下情况也视为重复：

- 新 prompt 的 stop condition 已被另一条 lane 的结果完全满足；
- 同一核心实现已经 merged，只是文档/入口名称不同；
- 某后继 QA 已经证明前置 stage 完成；
- 同一真人 proof 已被更高层 unified proof 完整覆盖。

遇到等价覆盖，应退出并报告 existing result，不重新做一遍。

## 6. 不允许“为了不空闲而重复做”

如果任务已完成/已 claim：立即退出。并发槽位由 PM 补新 stage，而不是当前线程自行找相似工作扩 scope。

## 7. Owner UX

正常情况下 Owner 不需要查看 claim 文件，也不需要记住哪个 prompt 已经复制。

Owner 可以重复粘贴一个**带本 guard 的新 prompt**；结果应自动落在三种之一：

- `ALREADY COMPLETE — SAFE TO CLOSE`
- `ALREADY CLAIMED — SAFE TO CLOSE`
- `CLAIM ACQUIRED — WORK STARTED`

之后继续执行原 prompt。

## 8. 兼容当前正在运行的旧 wave

在本协议提交之前已经启动的线程可能没有 claim，无法被 retroactive 原子锁完全保护。

因此：

- 当前 wave 仍以 GitHub result/commit 的 DONE 检查为主；
- 从本协议之后 PM 新建的所有 start prompt 必须引用本文件并声明 `stageId`；
- 当前 wave 结束后，新的滚动并发槽全部进入 claim 保护。
