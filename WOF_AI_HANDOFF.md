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
- broad T16 FAST/MID 已否定
- broad T30_FAST 已因 hard miss 降级
- absDx130 不是 hitbox/range
- T16 4840 divergence 不是 production rule

## WOF-034 正确结果
身份校验：
- copyId `WOF-034`
- project `WOF-AI-PRIVATE`
- version `wof-future-danger-adaptive-terminal-miner-v34`
- marker `=== WOF FUTURE DANGER ADAPTIVE TERMINAL MINER V34 JSON ===`
- readOnly `true`
- ramWrites `0`

运行：120000.5ms / 10ms；enemySamples 28271；ACTIVE edges 150。
主要 type：T19/T31/T12/T24/T18/T7/T9/T11/T10。
T24 coverage 很强：A4704=13, A5440=13, A5424=9, A4712=6。

### 最强 T24 discovery fingerprints（仍只是 correlation/discovery）
1. 预计 A5440：
`T24 S2/A2/B4 BODY5424 FE8AEEC NX8A6C6 V180001 TM2 P6C0`
WOF-034 在 ~100ms lag 5/5 对应 A5440，target/side 5/5 稳定，并覆盖 LEFT+RIGHT。

2. 预计 A5424：
`T24 S2/A2/B4 BODY5440 FE8AF28 NX8A6DA V180001 TM2 P6C0`
WOF-034 在 ~100ms lag 5/5 对应 A5424，target/side 5/5 稳定，并覆盖 LEFT+RIGHT。

3. V100001 RIGHT-only discovery：
`BODY5440 FE8AF28 NX8A756 V100001 TM2` → A5424，4/4 near100ms。

4. V100001 RIGHT-only discovery：
`BODY5424 FE8AEEC NX8A76A V100001 TM2` → A5440，4/4 near100ms。

### 重要排除
WOF-034 里一些看起来很漂亮的 T24 TM3/TM4 countdown 状态其实具有歧义：同一个 exact state 可在不同时间出现在 A5424 和 A5440 之前。因此不能因为按 actual attack 聚合后漂亮就直接把这些 TM3/TM4 状态当 attack-identity rule。

## 当前 frontier
```text
version = wof-resume-dispatch-selector-v45
nextCopyId = WOF-035
nextScript = wof_future_danger_t24_exact_prospective_validator_v35.js
nextMarker = === WOF FUTURE DANGER T24 EXACT PROSPECTIVE VALIDATOR V35 JSON ===
```

WOF-035：独立 prospective validator，只验证上述四条 exact T24 ~100ms fingerprints；输出 strict / jitter / late / hard miss / expected attack / target stability / side stability。horizon=140ms，tail=400ms，poll=10ms。

通过 prospective 后才能升级 production-shadow。
