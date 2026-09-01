# WOF PYLAUNCH Discovery V2 parentFrame Authority Fix — Fresh Stage

stageId: `PYLAUNCH_PARENTFRAME_AUTHORITY_FIX_V1`
priority: `P1`

## 启动去重守卫
先读取 `parallel/PM/STAGE_DEDUP_GUARD.md`、`parallel/PM/OWNER_INTERVENTION_GATE.md`、`parallel/PYLAUNCH_QA_DISCOVERY_V2_HARDENING/RESULT.md` 与最新 GitHub。

若等价修复已完成：`ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`，停止。
若 claim `parallel/PM/STAGE_CLAIMS/PYLAUNCH_PARENTFRAME_AUTHORITY_FIX_V1.json` 已存在：`ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`，停止。
否则原子 claim 后工作。

## 写入范围
只允许：
- `parallel/PYLAUNCH/**`
- mandatory stage claim

不要修改 OneClick / Recorder / Prospective / Fleet / Alpha / Live Proof。

## 精确 P1
Fresh QA 已证明：PYLAUNCH 虽声明支持 direct Worker `parentFrameId` 唯一映射，但 production discovery path 没有真正取得可用 frame->page map，因此双 WOF page 下会错误落入 ambiguity fallback。

## 必须修复
1. 增加最小、只读 CDP frame identity introspection，例如 `Page.getFrameTree` 或等价 execution-context `auxData.frameId` mapping。
2. 只把必要只读方法加入 allowlist；不得放开 gameplay Input 或 arbitrary function-call 能力。
3. 在 unique-page fallback 前真正解析 `parentFrameId` -> page。
4. `parentId` 保持最高直接 authority；`openerId` 继续非 authority。
5. 多重 frame mapping / 不唯一 mapping 必须 fail closed。
6. exact World 921031 SHA authority 不变。
7. 保持 readOnly=true / ramWrites=0 / inputInjection=false / no Worker replacement / no Blob/ObjectURL creation / no URL rewrite。
8. 使用 QA adversarial parentFrame fixture 做回归；加生产路径 reachability test，不只测 helper。
9. 不要求 Owner 真人 Browser。

## Stop condition
`PYLAUNCH PARENTFRAME AUTHORITY FIX READY — READY FOR FRESH QA RETEST`

必须证明 production discovery path 确实可消费唯一 `parentFrameId` authority，而不是仅新增未调用 helper。