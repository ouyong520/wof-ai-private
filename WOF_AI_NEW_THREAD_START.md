# WOF Future Danger AI — 新帖接手入口

更新时间：2026-09-01  
主仓库：`ouyong520/wof-ai-private`  
WinKawaks bridge：`ouyong520/wof-winkawaks-bridge`

> 这是给新 ChatGPT 对话直接接手当前 Browser Future Danger 主线用的入口。GitHub 是权威状态，不要重新发散逆向。

---

## 1. 项目最终目标

本项目不是 autoplay，也不是简单做“敌人在附近就报警”。目标是建立 **Future Danger AI / 未来危险预测层**：

```text
ROM AI / 招式逻辑
+ Browser/MAME live CPS RAM
+ enemy type/state/action/descriptor/position
+ 当前 P1/P2/P3 target
+ 当前 attack==0 zero-cycle
→ 在 enemy ACTIVE 之前预测未来危险
→ attack / target / side / lead
→ 最终服务 Future Danger Map / Safe Path
```

核心要求：低误报、跟随敌人真实 AI target、用 prospective forward evidence，不用事后回看冒充预测。

---

## 2. 强制协作协议

1. GitHub 是权威状态。
2. 用户每轮 Browser 主线只执行 **ONE 条 Console 命令**，然后上传 JSON。
3. 每条 Browser live 命令必须以唯一注释开头：`// WOF-xxx`。
4. Assistant 负责：
   - 回传校验
   - 结果分析
   - GitHub 更新
   - 版本推进
   - 下一轮实验设计
5. 每次回传必须先校验：

```text
copyId
project
version
marker / expectedMarker
readOnly
ramWrites
```

要求：

```text
project = WOF-AI-PRIVATE
readOnly = true
ramWrites = 0
```

身份不一致时，不把数据当当前轮证据。
6. 多房结果必须保留 per-room 边界。
7. `enemy+0x7E` 是 authoritative live target；warning entry target 不能冻结，ACTIVE/最终输出必须实时重读。
8. Browser production 与 WinKawaks discovery 严格隔离。WinKawaks 只能发现候选，不能直接视为 Browser production proof。
9. 不要求用户重复已经解决的 selector / dispatcher / descriptor 逆向。

---

## 3. 已锁死的 Browser 底层事实

### Players

```text
P1 = 0xFFBE1C
P2 = 0xFFBEFC
P3 = 0xFFBFDC
stride = 0xE0
```

player self index：

```text
P1+0x7C = 0
P2+0x7C = 4
P3+0x7C = 8
```

### Enemy pool

```text
base = 0xFFC0BC
stride = 0xE0
slots = 20
```

### Enemy target

```text
enemy+0x7E
0 -> P1
4 -> P2
8 -> P3
```

这是 authoritative selector field。

player pointer table：

```text
0x010CF8 = P1
0x010CFC = P2
0x010D00 = P3
```

关键 selector：

```text
0x010E66 MOVE.W 126(A0),D1
0x010E6A LEA 0x010CF8,A1
0x010E6E MOVE.L 0(A1,D1.W),A1
```

### XY

```text
object +4 = X 16.16
object +8 = Y 16.16
```

Z / floor-depth 仍不属于 Browser 主线当前瓶颈。

### State / action / dispatcher

```text
enemy+0x99 = first state dispatch
enemy+0x2A = second action dispatch
```

严格路线之一：

```text
state99=0 / action2A=2
→ 0x10EC6
→ ...
→ dispatcher 0x25C8
```

Dispatcher incoming edges 已解决：44 条 direct incoming。

### Descriptor consumer 0x247C

已确认：

```text
+0  frame/payload end -> enemy+0x12
+4  long              -> enemy+0x30
+8  timer/flag
next                  -> enemy+0x2C
timer                 -> enemy+0x34
payload tail          -> enemy+0x6C/+0x6E...
```

`frameEnd` 是 DATA boundary，不是代码地址。

---

## 4. ACTIVE 定义

当前 prospective validator 统一使用：

```text
enemy+0x70 U16
0 -> nonzero
```

称为 **ACTIVE-start convention**。

严格禁止误称为 exact hitbox / collision / damage onset。

`leadMs` 只表示距离 `+0x70 0->nonzero` 的时间。

---

## 5. 当前方法论

权威路线：

```text
attack == 0 current cycle
→ same-cycle state / ordered-sequence discovery
→ prospective arm
→ same enemy future 0->nonzero ACTIVE
→ verify attack / live target / side / lead / miss
```

### fixed-lag

50/100/150/250/500ms retrospective fingerprint 已降级为 discovery/correlation，不能直接 production。

### same-cycle miner

只记录当前 zero-attack cycle 内真正经历过的状态，再由同一 enemy 未来 ACTIVE 归因。

### held state

状态可能在首次 observation 时已经 held，所以使用 once-per-zero-cycle level arm，而不是只看 entry edge。

### ordered sequence

如果同一个 single-state 可以走向不同 active attack，则不能 promotion；必须升级到 transition pair / triple / ordered context，再另做 prospective validator。

---

## 6. 多房 Browser coordinator

WOF-040 起稳定：

```text
gstyphoon.js Worker = collect (~120s / room)
top                 = finalize + download one merged JSON
max rooms           = 5
no short join window
1P / 2P / 3P all accepted
```

同一条 JS：
- 先在每个 Worker 执行；
- 全部完成后切到 `top`；
- 在 `top` 再执行同一条，汇总并下载一个 JSON。

不要声称 JS 可以自动改变 DevTools execution-context dropdown。

---

## 7. 当前 production-shadow 集合

### T16

`T16_B4_DANGER_40`

状态：`production-shadow-imminent-danger`

语义只能是 **马上危险**，不是 A6432-exclusive。

历史和 WOF-051 都有非 A6432 反例；WOF-051 为：

```text
98/98 strict danger
A6432 = 97
A4840 = 1
target 98/98
side   98/98
lead   8.9..21.0ms
```

### T20

`T20_5136_B0_TO_B255_1250`

状态：`production-shadow-coarse`

语义：A5136 的 coarse early warning。

1250ms 是 audit horizon，不是 countdown / causal boundary。

WOF-051：

```text
5/5 strict A5136
target/side 5/5
lead 380.9..639.7ms
```

### D867

`D867BA_3232_TM6_220`

状态：production-shadow。

WOF-051：

```text
10/10 strict A3232
target/side 10/10
T33=8 / T9=2
P1/P2/P3 targets all covered
lead 99.1..109.4ms
```

### D881

`D8811E_3232_TM6_135`

状态：production-shadow。

135ms 只是 audit horizon；历史存在 clean 209.5ms correct tail hit。

WOF-051：

```text
22/22 strict A3232
target/side 22/22
T34=15 / T11=7
lead 98.6..119.2ms
```

### T24

```text
BODY7512 / TM3 -> A5440
BODY7520 / TM4 -> A5424
```

均 production-shadow。

### T18 已锁两条

```text
BODY7512 / TM4 -> A5440
BODY7520 / TM4 -> A5424
```

均 production-shadow。

WOF-051：

```text
A5440 4/4 strict, lead 62.3..70.9ms
A5424 4/4 strict, lead 69.1..70.0ms
```

历史 WOF-050 有 138.6ms / 128.5ms clean correct tail hit，所以 legacy 90ms 只是 audit label，不是 causal boundary。

---

## 8. T23 当前真实状态

旧：

```text
T23_4792_BODY4920_B0_ENTRY_180
```

已 retired，禁止复活。

WOF-045 曾发现 short candidate：

```text
S0/A6/B4|BODY4976|FE84868|NX83f20|V0|TM5|P6C0
```

但后续证明 T23 single-state 存在 attack ambiguity，因此不能 promotion。

### 最新正面 T23 evidence 仍是 WOF-047

唯一有 T23 的房间：

```text
8 resolved cycles
A4792 = 3
A4920 = 3
A5888 = 2
```

关键认识：order 比 single-state 更重要。

例如某 A5888 tail：

```text
S0/A8/B2 BODY4936
→ S0/A2/B0 BODY4936
→ S0/A6/B4 BODY4936
→ A5888
```

但第一状态本身也可出现在 A4792，所以必须看 ordered pair/triple/context。

WOF-049 五房、WOF-050 三房、WOF-051 三房全部没有 T23：

```text
t23Samples = 0
attackZeroStarts = 0
activeEdges = 0
resolvedCycles = 0
```

这是 scene/room coverage absence，不是 tracer failure，也不是候选 forward failure。

---

## 9. WOF-051 最新完成结果

Batch：

```text
b-2f39eb3f-4a7
```

身份：

```text
copyId = WOF-051
project = WOF-AI-PRIVATE
version = wof-future-danger-multiroom-coordinator-v51
readOnly = true
ramWrites = 0
3 joined / 3 complete
0 error / 0 interrupted
all embedded WOF-051R identity passed
```

覆盖：

```text
player histogram = [0,488,488,492]
≈ one pure1P + one pure2P + one pure3P room
```

总量：

```text
35999 polls
108463 enemy samples
558 ACTIVE edges
145 signals
144 strict
0 jitter
1 realLate
0 hard miss
0 censored
```

唯一 realLate 来自实验性 T18 A4704 candidate，不属于当前 production rule failure。

---

## 10. WOF-051 关键新结论：T18 BODY4728 single-state 不可直接预测 A4704

WOF-050 same-cycle discovery 曾找到：

```text
T18
S0/A4/B2|BODY4728|FE8b660|NX8b204|Vffff|TM1|P6C4736
```

WOF-050 discovery：

```text
18 resolved cycles
target 18/18
side   18/18
last-seen lead 29.6..51.1ms
```

因此 WOF-051 做 direct prospective once-per-zero-cycle arm。

WOF-051 真正得到两个 evaluable cycles：

```text
same exact state
→ A4704 @ 19.9ms
→ A4712 @ 100.4ms
```

且：

```text
target stable 2/2
side stable   2/2
hard miss     0
```

结论非常明确：

**BODY4728/A4/B2/TM1 是 forward-relevant，但不是 A4704-specific。**

因此：
- 不 promotion；
- 不再作为 A4704 predictor；
- 必须研究该状态之后的 ordered transition/context，区分 A4704 vs A4712。

---

## 11. 当前下一轮：WOF-052

当前权威状态：

```text
resume = wof-resume-dispatch-selector-v62
nextCopyId = WOF-052
nextScript = wof_future_danger_multiroom_coordinator_v52.js
nextMarker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V52 JSON ===
embedded = WOF-052R
IndexedDB = wof-future-danger-multiroom-v14
```

### WOF-052 目标

1. 继续全部 production audits。
2. 继续 T23 ordered tracer / exact-TM + TM* summaries。
3. 不再把 BODY4728 single-state 当 A4704 predictor。
4. 新增 **T18 candidate-context ordered tracer**：
   - 记录全部 T18 attack-zero cycle；
   - 标记 exact BODY4728/A4/B2/TM1 occurrence；
   - 保存 ordered distinct states；
   - 只对 candidate-containing cycles 做 summary；
   - 按 eventual activeAttack 分组；
   - 输出 exact/TM* final / tail2 / tail3 / transition pair / triple；
   - 优先寻找 A4704 vs A4712 的 post-candidate discriminator。
5. 新 sequence 仍然只是 discovery；找到 discriminator 后必须再建 prospective ordered validator 才可 promotion。
6. Prefer multiple rooms，最好至少一个真正包含 T18 的房间。

### WOF-052 当前 Console 命令

```js
// WOF-052
await fetch('https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/wof_future_danger_multiroom_coordinator_v52.js?x='+Date.now(),{cache:'no-store'}).then(r=>r.text()).then(s=>(0,eval)(s));
```

---

## 12. WinKawaks 并行线边界

另有本地 WinKawaks discovery infrastructure：

```text
GEO-*     人物几何/坐标
EFIELD-*  enemy 0xE0 字段地图
RAWMINE-* raw diff / transition / candidate ranking
BASECAP   shared base raw capture dataset
```

原则：

```text
WinKawaks = discovery
Browser   = production proof
```

不可把 WinKawaks capture 直接当 Browser production evidence。

本地完整关卡 sweep 的方向是：3P 高出怪量、无敌、每波约60秒采集、人工或编队移动、采完清怪推进；用于快速建立 stage/scene/wave/type/attack atlas。它可以显著减少等待随机网页房间，但最终高价值规则仍回 Browser prospective 验证。

---

## 13. 不要重新研究 / 不要复活

已解决，不重新发散：

```text
P1/P2/P3 identity
+0x7E selector
player pointer table
44 dispatcher incoming edges
descriptor consumer 0x247C
Focus Multiroom infrastructure
```

禁止复活：

```text
broad T16 FAST<=100
broad T16 MID<=250
broad T30_FAST
absDx causal timing
T20 absDx causal law
persistent broad T20/T34 imminent phases
fixed-lag predictor when state persists
old ambiguous T24 TM3/TM4 rules
T16 B4 exclusive A6432
old fixed-lag T24 BODY5424/5440
old T23 BODY4920/B0
T18 BODY4728/A4/B2/TM1 = A4704-specific predictor
```

并牢记：

```text
+0x70 != exact hitbox/damage onset
audit horizon != causal boundary
zero coverage != forward failure
warning entry target != final target lock
same-cycle discovery != production proof
sparse ordered sequence != production proof
```

---

## 14. 新帖接手时必须先读

按顺序读取：

```text
WOF_AI_NEW_THREAD_START.md
WOF_AI_HANDOFF.md
WOF_AI_CURRENT_FRONTIER.md
WOF_AI_MASTER_PROGRESS.md
```

若需要静态逆向历史再读：

```text
WOF_AI_REVERSE_PROCESS.md
```

当前完成报告：

```text
reports/WOF-049_ANALYSIS.md
reports/WOF-050_ANALYSIS.md
reports/WOF-051_ANALYSIS.md
```

当前下一步只有一个：**WOF-052**。

不要跳到 WOF-053，除非 WOF-052 已实际回传并完成分析/GitHub 更新。
