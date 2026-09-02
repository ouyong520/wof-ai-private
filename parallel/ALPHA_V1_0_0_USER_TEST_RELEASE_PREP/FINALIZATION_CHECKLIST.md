# Alpha V1.0.0 — 玩家测试包最终定版清单

Status: **PREPARED / NOT RELEASED**

这是 release-finalization 用的内部清单，不是玩家需要执行的步骤。本 stage 不刷新最终 package manifest，也不锁定最终 commit/hash。

## 只有所有 release gates 通过后才执行

- [ ] 当前 P0/P1 release gates 全部 PASS，且没有被更新的 main 再次 supersede。
- [ ] bounded Browser/WOF live acceptance 已真实执行并 PASS。
- [ ] 玩家头顶危险提醒完成真实动态 non-drift：左右、纵深、跳跃、快速推进/卷屏、retarget、resize/fullscreen。
- [ ] 怪物头顶 `1P / 2P / 3P` 完成真实动态 non-drift 与 retarget 验证。
- [ ] 定位不可信时确认隐藏/fixed HUD fail-closed，而不是保留错误坐标。
- [ ] 在最终稳定 snapshot 上重新生成 Owner OneClick package manifest；不要沿用旧 snapshot 的 Alpha blobs。
- [ ] 最终 one-click package 自身完整性/Windows/中文路径门禁 PASS。
- [ ] 包根目录保留并验证唯一推荐玩家入口：`WOF_一键工具.cmd`。
- [ ] 将本目录 `README.md`、`BUG反馈模板.md`、`RELEASE_NOTES_V1.0.0.md` 以玩家容易看到的方式放入最终测试包或交付页。
- [ ] 玩家文档中的 `NOT RELEASED` 只在上述门禁全部关闭、最终 package 已验证后才改为明确的测试发布状态。

## 不要做

- 不要为了赶版本号绕过 Browser/WOF non-drift proof。
- 不要把 repository/synthetic PASS 写成真实视觉证明。
- 不要因为内部 refactor/QA/tooling 完成就发布 V1.0.1/V1.0.2。
- 不要在 final package 尚未稳定时提前写死 commit、package hash 或 projection 常量到玩家 release notes。
- 不要修改 danger rules、`target7E` 语义、Transport authority、projection 常量或 `product/alpha/**` 行为来完成“发布准备”。
