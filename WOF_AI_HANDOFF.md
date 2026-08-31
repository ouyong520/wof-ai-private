# WOF Future Danger AI — 最新交接 / START HERE

更新时间：2026-08-31
仓库：`ouyong520/wof-ai-private`
项目：Project A — Browser/MAME/gstyphoon.js Future Danger
游戏：Warriors of Fate / wofr1

> 与 `ouyong520/wof-winkawaks-bridge` 完全分开。不要混入 M3/M4。

## 强制协作协议
- 用户只在 live `gstyphoon.js` Worker Console 每轮执行一条命令并回传结果。
- 每轮命令第一行唯一 `// WOF-xxx`。
- 收到结果先核对 `copyId / project / version / marker`；不匹配就拒绝作为当前证据。
- 默认 read-only；`ramWrites=0`。
- Assistant 负责分析、GitHub 修改、下一版测试设计。

## 已锁死底层，不要重做
- P1/P2/P3：`0xFFBE1C / 0xFFBEFC / 0xFFBFDC`
- enemy pool `0xFFC0BC`, stride `0xE0`, 20 slots
- player self index `+0x7C = 0/4/8`
- enemy authoritative target selector `+0x7E = 0/4/8 → P1/P2/P3`
- player pointer table `0x010CF8`
- selector route `0x010E66 → 0x010E6A → 0x010E6E`
- dispatcher `0x25C8` + descriptor consumer `0x247C` 已解决；44 incoming edges 已完整
- `enemy+0x70 U16 0→nonzero` 仅是 ACTIVE-start convention，不是 exact hitbox / damage onset

## 当前 production / candidates
- T16 exact terminal B4 = `production-shadow`
- T33/T34 attack3232 TM6 = `production-shadow-candidate`
- T24 四条 exact ~100ms TM2 fingerprints = `prospective-candidate`，但 WOF-035 没有 T24 coverage，因此状态不升不降
- broad T16 FAST/MID 已否定
- broad T30_FAST 已因 hard miss 降级
- absDx130 不是 hitbox/range
- T16 4840 divergence 不是 production rule

## WOF-034 正确结果
WOF-034 coverage-adaptive mining 抓到 150 ACTIVE edges；T24 coverage 很强，挖出四条 exact ~100ms TM2 discovery fingerprints：
1. `T24 S2/A2/B4 BODY5424 FE8AEEC NX8A6C6 V180001 TM2 P6C0` → eventual A5440，5/5 near100ms，target/side stable，LEFT+RIGHT。
2. `T24 S2/A2/B4 BODY5440 FE8AF28 NX8A6DA V180001 TM2 P6C0` → eventual A5424，5/5 near100ms，target/side stable，LEFT+RIGHT。
3. `BODY5440 FE8AF28 NX8A756 V100001 TM2` → A5424，4/4 near100ms，RIGHT-only discovery。
4. `BODY5424 FE8AEEC NX8A76A V100001 TM2` → A5440，4/4 near100ms，RIGHT-only discovery。

WOF-034 mined fingerprints 仍只是 discovery/correlation evidence。部分 T24 TM3/TM4 exact states 对 A5424/A5440 存在歧义，不能当 attack-identity rule。

## WOF-035 正确结果
身份严格通过：
- copyId `WOF-035`
- project `WOF-AI-PRIVATE`
- version `wof-future-danger-t24-exact-prospective-validator-v35`
- marker `=== WOF FUTURE DANGER T24 EXACT PROSPECTIVE VALIDATOR V35 JSON ===`
- readOnly `true`
- ramWrites `0`

运行：120001.4ms / 10ms；enemySamples 48326；ACTIVE edges 194。
主要 type：T23/T20/T7/T30/T16/T22/T28/T10/T9。
**T24 samples=0**，所以四条 T24 candidate 全部 rawMatch=0 / transitionEntries=0 / signals=0。
这不是 candidate failure，只是 coverage=0；不得把它当负证据。

本轮值得保留的 coverage 信息：
- T16 A6432 = 22 ACTIVE edges
- T16 A4832 = 2
- T30 A6200 = 10, A2536 = 18, A2528 = 6
- T7 A2536 = 25, A2528 = 12
- T9/T10 A3232 覆盖也很高

## 当前 frontier
```text
version = wof-resume-dispatch-selector-v46
nextCopyId = WOF-036
nextScript = wof_future_danger_adaptive_terminal_miner_v36.js
nextMarker = === WOF FUTURE DANGER ADAPTIVE TERMINAL MINER V36 JSON ===
```

WOF-036：重新采用 coverage-adaptive miner，120s / 10ms。
- opportunistically 验证 T16 exact B4、T33/T34 TM6、四条 T24 exact candidates；
- 无论房间出现什么 type，都对每个 ACTIVE edge 挖 last-zero terminal fingerprint、20/50/100/150/250/500ms fingerprints、recent transitions；
- 按 type + actual attack 聚合，并统计 target/side stability；
- 当前房间若继续是 T7/T30/T16/T22/T28/T10/T9/T23/T20，也会产出有效 mining 证据，不再因 T24 缺席白跑。

WOF-036 新挖出的 signature 仍只能算 discovery/correlation，必须下一轮独立 prospective validation 后才能升级 production-shadow。
