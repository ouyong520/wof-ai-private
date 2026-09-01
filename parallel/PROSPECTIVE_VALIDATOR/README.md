# WOF Prospective Validator Framework

状态：**READY — 通用 prospective validation 基础设施已完成。**

本目录只负责“候选规则冻结后的前瞻验证”，不负责发现攻击规则，也不会把任何候选自动提升为生产规则。

## 一条规则以后怎么验证

未来分析线只需要产出一个符合 `wof-prospective-candidate-v1` 的候选 manifest。

Windows 上最短路径：

```bat
RUN_PROSPECTIVE_VALIDATOR.cmd candidate.json
```

也可以把 `candidate.json` 直接拖到 `RUN_PROSPECTIVE_VALIDATOR.cmd` 上。

Live validator 会：

1. 先冻结候选 manifest（SHA-256 + freeze time）；
2. 自动读取默认 Browser Fleet manifest；如果没有 Fleet，则扫描现有 localhost Chrome/Edge CDP；
3. 每个 endpoint 都重新 probe，不信任 Fleet 的旧状态；
4. 自动发现真实 `gstyphoon*.js` Worker；
5. 只读确认 WASM/heap；
6. 严格确认 `Warriors of Fate (World 921031)` 和黄金 SHA-256；
7. 每个 Worker/session 独立运行候选 matcher；
8. 自动记录 signal / strict / jitter / late / hard miss / censored；
9. 自动保存统一 prospective corpus 和 result JSON；
10. `Ctrl+C` 结束时把仍在等待结果的 signal 记为 censored，而不是伪装成 PASS。

Browser Fleet 只是发现入口；validator 不修改 Fleet，也不修改 WOF-052L Recorder。

## 候选 manifest

Schema：`wof-prospective-candidate-v1`

最小结构：

```json
{
  "schema": "wof-prospective-candidate-v1",
  "id": "MY_CANDIDATE",
  "promotion": "research-only",
  "rule": {
    "sequence": {
      "kind": "tail3",
      "states": [
        {"family": "..."},
        {"family": "..."},
        {"family": "..."}
      ]
    }
  },
  "outcome": {"expectedAttacks": [5888]}
}
```

固定要求：

- `promotion` 必须是 `research-only`；
- `outcome.expectedAttacks` 必须显式给出；
- manifest 不能要求生产自动晋级；
- World identity 可以固定为 `Warriors of Fate (World 921031)`；
- 推荐写入黄金 SHA-256：`5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`。

完整约束见 `manifest.schema.json`，运行时还有额外语义检查。

## 支持的规则表达

### Ordered sequence

支持四种名称：

- `tail2`
- `pair`
- `tail3`
- `triple`

`pair`/`tail2` 都表示“当前 distinct-state history 的末端连续两个状态”；`triple`/`tail3` 同理表示末端连续三个状态。

每个 state matcher 可以使用：

- `signature`：完全匹配；
- `family`：例如把 timer 归一化为 `TM*`；
- `predicates`：对解析出的 state 字段做条件判断。

因此可以表达 exact ordered tail，也可以表达 timer-normalized ordered tail。

### Current-level predicate

`rule.currentPredicates` 可以单独使用，也可以和 ordered sequence 同时使用。

支持字段包括 live snapshot 中的：

- `type`
- `target7E` / `target`
- `side`
- `x` / `y`
- `state99`
- `action2A`
- `b2B`
- `body`
- `attack`
- `frameEnd`
- `next`
- `value30`
- `timer34`
- `payload6C`

支持操作：`eq / ne / in / not_in / lt / lte / gt / gte / exists`。

## 统计语义

一个规则在 attack==0 阶段第一次满足时，当前 cycle 只 arm 一次 signal。

默认时间窗口：

- `strictMaxMs`: 150
- `jitterMaxMs`: 220
- `lateMaxMs`: 1000
- `hardMissMs`: 1500

manifest 可以覆盖。

结果分类：

- `signal`：候选在攻击前实际触发；
- `strict`：命中期望 attack 且 lead <= strict；
- `jitter`：命中期望 attack 且落在 jitter 窗；
- `late`：命中期望 attack 但更晚；
- `hardMiss`：出现错误 ACTIVE attack，或 signal 后超过 hardMiss 窗仍没有 ACTIVE；
- `censored`：signal 已触发，但 Worker/房间/validator 在结局前结束。

每条 evidence 同时保留：

- room/session；
- active attack；
- lead；
- target stable；
- side stable；
- retarget 列表；
- signal 时 current snapshot；
- ordered states。

## Discovery 与 prospective 严格隔离

这是框架的硬约束。

- `wof-052l-recorder-v1` 历史 JSON 默认永远按 `discovery` 读取；
- discovery signal 会统计，但绝不能满足 prospective gate；
- `start_session.py` 可以把候选 manifest 的 SHA-256 和 freeze time 固定下来；
- 使用 session 读取 Recorder 文件时，只有 `startedAt >= frozenAt` 的新房间才会标为 prospective；
- manifest 在 freeze 后被改动，session hash 校验会直接失败；
- live validator 自己产生的数据天然发生在 freeze 之后并标为 prospective。

离线示例：

```bat
python start_session.py candidate.json --output prospective_session.json
python validator.py candidate.json rooms\room1.json rooms\room2.json --session prospective_session.json --output result.json
```

## WOF-052L 兼容

`validator.py` 可以直接读取：

- `wof-prospective-corpus-v1`；
- WOF-052L `wof-052l-recorder-v1` per-room JSON；
- WOF-052L merged JSON 中保留的 T18 candidate evidence。

注意：当前 WOF-052L merged JSON 对 T23 只保存 summary、不保存完整 T23 traces，因此重新验证 T23 ordered rule 时应使用 per-room JSON。框架不会从 summary 反推不存在的原始 evidence。

`prospective_run.py` 保留了一条“冻结候选 -> 调用现有 Recorder -> 自动读取 per-room JSON -> 出结果”的兼容路径；主入口则是更通用的 `live_validator.py`。

## 三个已验证表达例

`manifests/t18_body4728_ordered_tail.example.json`

- 证明框架可以表达 T18 BODY4728 的 ordered tail；
- **只是表达/测试样例**；
- WOF-051 已证明 BODY4728 单状态本身同时可落到 A4704/A4712，本文件没有声称示例中的第二状态是真实 A4704 discriminator。

`manifests/t23_a5888_body4936_tail3.example.json`

- 表达 WOF-047 已观察到的 A5888 BODY4936 timer-normalized tail3：
  `A8/B2 -> A2/B0 -> A6/B4`。

`manifests/current_level.example.json`

- 表达一个简单 current-level predicate：BODY7512 + TM4 -> expected A5440；
- 用于证明 current-level 路径与 ordered sequence 共用同一统计引擎。

## 输出

Live 默认保存到：

```text
parallel/PROSPECTIVE_VALIDATOR/results/
  <timestamp>_<candidate>_live_corpus.json
  <timestamp>_<candidate>_live_corpus.result.json
```

Result schema：`wof-prospective-result-v1`。

紧凑结果固定包含：

- verdict；
- prospective 六类统计；
- discovery 六类统计；
- room / attack 计数；
- gate；
- 安全声明。

即使 gate PASS，verdict 也只会是：

`PROSPECTIVE_PASS_RESEARCH_ONLY`

且：

`productionPromotionAllowed=false`

## 多房间与生命周期

- Fleet 每个 localhost endpoint 独立 CDP client；
- 每个 Worker 独立 session/history/signal；
- 一个 endpoint/Worker 崩溃不会清掉其他房间；
- reload/recreated Worker 会重新发现并建立新 room id；
- 断线前最后一次已知 pending signal 会保守记为 censored；
- 不跨 endpoint 复用 session 状态。

## 安全边界

固定：

- read-only；
- `ramWrites=0`；
- `inputInjection=false`；
- `windowWorkerReplacement=false`；
- 不替换 `window.Worker`；
- 不创建攻击输入；
- 不写游戏 RAM；
- 不修改 `product/alpha/**`；
- 不修改 `parallel/PYLAUNCH/**`；
- 不修改 `parallel/WOF052L_RECORDER/**`；
- 不修改 `parallel/BROWSER_FLEET/**`。

Live probe 只在已附加的真实 Worker 中创建自己的 `globalThis.__WOF_PROSPECTIVE_VALIDATOR` 只读采样对象和 timer，不改变游戏数据结构或 Worker 创建机制。

## 离线回归

在本目录：

```bat
python -m unittest -v test_validator.py
```

覆盖：

- T18 tail2；
- T23 tail3 / TM* family；
- current-level predicate；
- discovery 不可满足 prospective gate；
- wrong attack hard miss；
- no-ACTIVE timeout hard miss；
- censored；
- Recorder 默认 discovery；
- session freeze 新旧 evidence 区分；
- manifest freeze 后篡改检测；
- research-only 强制约束。

生成的 live JS probe 也可做语法检查：

```bat
python live_validator.py manifests\t23_a5888_body4936_tail3.example.json --dump-probe probe.js
node --check probe.js
```
