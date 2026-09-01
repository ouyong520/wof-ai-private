# WOF PM Stage Claims

这个目录是 `parallel/PM/STAGE_DEDUP_GUARD.md` 的原子 stage claim 注册表。

规则：

- 每个 future fresh stage 使用唯一 `stageId`；
- 执行线程开始真正工作前，用 GitHub create-file 创建 `<stageId>.json`；
- 已存在即视为该 stage 已被认领，重复线程必须退出；
- 完成后更新 claim 为 `COMPLETE`；精确阻断则更新为 `BLOCKED`；
- 不删除历史 claim；下一阶段使用新的 stageId；
- stale `ACTIVE` claim 只能由 PM 通过新的 recovery/supersede stage 处理。

Owner 不需要手工维护此目录。
