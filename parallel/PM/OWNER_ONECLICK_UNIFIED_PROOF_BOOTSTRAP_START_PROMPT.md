# WOF Owner One-Click Unified Proof Bootstrap — Fresh Stage

stageId: `OWNER_ONECLICK_UNIFIED_PROOF_BOOTSTRAP_V1`

## 启动去重守卫

先读取：
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/OWNER_INTERVENTION_GATE.md`
- GitHub 默认分支最新状态

若 stop condition 已满足：`ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`。
若 claim `parallel/PM/STAGE_CLAIMS/OWNER_ONECLICK_UNIFIED_PROOF_BOOTSTRAP_V1.json` 已存在：`ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`。
否则原子 create-file claim；成功后才工作；完成/阻断更新 claim。不得因重复任务自行扩 scope。

## 写入范围

只允许：
- `parallel/OWNER_ONECLICK/**`

不要修改 LIVE_PROOF_BUNDLE / PYLAUNCH / Fleet / Recorder / Prospective / Alpha。

## 目标

把未来最后一次 Owner 真人 proof 的操作压缩成：

`下载一个 CMD -> 双击 -> 正常进入一次 WOF -> 最后只发一个 JSON 或截图`

但本阶段**不要求 Owner 实际运行**。

## 必须做到

1. 单文件 direct-download bootstrap；不要求 Git/GitHub Desktop/仓库路径。
2. 自动下载当前 Unified Live Proof bundle 所需 snapshot，避免 stale browser/cache；使用明确 no-cache/version query/hash 校验策略。
3. 下载后验证文件完整性/manifest，避免半更新/mixed snapshot。
4. 自动 Python/venv/dependency bootstrap；失败中文说明。
5. 自动调用 Unified Proof 的 repository preflight；preflight 不 PASS 时**不启动 Browser、不要求 Owner 进入 WOF**。
6. 只有 preflight PASS 时才进入 live proof。
7. 支持 Windows 10/11、中文用户名、中文路径、spaces、重复运行、断网/部分下载失败、旧安装目录存在。
8. 所有 owner-facing 文本简体中文；技术详情第二层。
9. 不要求 DevTools、Worker Console、粘 JS、长命令、手工找 JSON。
10. 最终固定生成/定位一个 `UNIFIED_LIVE_PROOF_STATUS.json`，并在 CMD 中明确告诉 Owner“只需要把这个结果发给 PM”。
11. 不自动启动 10-room long capture。
12. 不修改/包装/替换 Worker，不写 RAM，不注入输入。

## 离线/CI 自测

至少覆盖：
- fresh empty folder；
- Chinese path + spaces；
- existing stale install；
- partial download；
- cache-busting；
- checksum/hash mismatch；
- dependency install failure；
- preflight BLOCKED => no browser launch；
- preflight PASS => live proof entry selected；
- rerun replaces/refreshes stale payload safely；
- final JSON path always discoverable；
- Chinese encoding no mojibake。

允许用 mock download/local fixture，不要求 Owner 真人运行。

## Stop condition

`OWNER ONE-CLICK UNIFIED PROOF BOOTSTRAP READY — REPOSITORY/CI PASS`

结果必须明确：Owner 将来只剩哪一个不可模拟的真人动作。不要要求 Owner 当前就测试。