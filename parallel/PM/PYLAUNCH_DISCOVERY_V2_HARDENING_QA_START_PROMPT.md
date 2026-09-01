# WOF PYLAUNCH Discovery V2 Hardening — Fresh Independent QA

stageId: `PYLAUNCH_DISCOVERY_V2_HARDENING_QA_V1`

## 启动去重守卫

先读取：
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/OWNER_INTERVENTION_GATE.md`
- `parallel/PYLAUNCH/DISCOVERY_V2_HARDENING_RESULT.md`
- GitHub 默认分支最新状态

如果本 QA stop condition 已经有 durable 结果：输出 `ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲` 并停止。
如果 `parallel/PM/STAGE_CLAIMS/PYLAUNCH_DISCOVERY_V2_HARDENING_QA_V1.json` 已存在：输出 `ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲` 并停止。
否则原子 create-file claim，成功后才开始 QA；完成/阻断时更新 claim。

## 独立 QA 边界

这是 fresh independent QA。

只允许写：
- `parallel/PYLAUNCH_QA_DISCOVERY_V2_HARDENING/**`
- mandatory PM stage claim

严禁修改：
- `parallel/PYLAUNCH/**`
- `parallel/WOF052L_RECORDER/**`
- `parallel/PROSPECTIVE_VALIDATOR/**`
- `parallel/LIVE_PROOF_BUNDLE/**`
- `product/alpha/**`

发现问题只记录，不修复；修复必须交给新的 fresh fix thread。

## QA 目标

独立验证最新 PYLAUNCH Discovery V2 hardening 是否真的关闭此前 P1，不接受实现帖自己的 PASS 作为证据。

必须至少检查：
1. remote HTTP/CDP host fail closed；
2. returned websocket remote/cross-port fail closed；
3. localhost / 127.0.0.1 / ::1 等合法 loopback normalization；
4. existing blob/data/hashed/extensionless Worker URL 不被 URL shape 本身错误拒绝；
5. wrong World 921031 identity 对任何 URL shape 都 fail closed；
6. openerId 不能成为 direct Worker parent authority；
7. real parentId / uniquely mapped parentFrameId 保持有效；
8. direct fallback 只有唯一 WOF page 时才允许；两 WOF pages 必须拒绝；
9. cross-page exact pair ambiguity 必须拒绝；
10. reload/recreated Worker targetId 不能继承 stale identity cache；
11. disconnect/reconnect 清理旧 authority；
12. exact World 921031 SHA authority 保持；
13. readOnly=true / ramWrites=0 / inputInjection=false；
14. no Worker replacement/wrap / no Blob creation / no URL rewrite；
15. CDP allowlist 不得出现 gameplay `Input.*` 或任意 `Runtime.callFunctionOn`。

优先增加 adversarial fixture / synthetic topology，而不是复述原测试。

同时记录但不要在本 QA 修复：
- Owner OneClick package manifest 是否已经 stale；
- Windows CP1252/中文输出问题是否仍存在。
这些属于后续 package/integration stage，不应伪装成 PYLAUNCH core QA PASS。

## 输出

写入：
- `parallel/PYLAUNCH_QA_DISCOVERY_V2_HARDENING/RESULT.md`
- machine-readable QA result JSON
- 必要的独立 fixture/tests

## Stop condition

二选一：

`PASS — PYLAUNCH DISCOVERY V2 HARDENING INDEPENDENT QA`

或

`BLOCKED — PYLAUNCH DISCOVERY V2 HARDENING QA — <精确 P0/P1>`

不请求 Owner 真人 Browser。