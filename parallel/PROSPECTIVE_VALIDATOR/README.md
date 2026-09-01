# WOF Prospective Validator Framework

状态：**PROSPECTIVE VALIDATOR DISCOVERY V2 READY**

本目录只负责“候选规则冻结后的前瞻验证”。它不负责发现攻击规则，也不会把任何候选自动提升为生产规则。

## 最短使用路径

未来分析线只需要产出一个符合 `wof-prospective-candidate-v1` 的候选 manifest。

Windows：

```bat
RUN_PROSPECTIVE_VALIDATOR.cmd candidate.json
```

也可以把 `candidate.json` 直接拖到 `RUN_PROSPECTIVE_VALIDATOR.cmd` 上。

这个 owner 入口现在固定执行 `live_validator_v2.py`。为了兼容旧调用，直接运行：

```bat
python live_validator.py candidate.json
```

也会进入 Discovery V2；旧 live engine 仅以内部 `live_validator_core.py` 形式保留给 V2 复用，不再作为真人 discovery 入口。

## Live Validator Discovery V2 做什么

1. 冻结候选 manifest：SHA-256 + freeze time；
2. 自动读取默认 Browser Fleet manifest；没有 Fleet 时扫描现有 localhost Chrome/Edge CDP；
3. 每个 endpoint 独立重新 probe，不信任 Fleet 的旧状态；
4. 保留 direct Worker backward compatibility；
5. 从 page session 使用 `Target.setAutoAttach` 自动观察 related topology；
6. 支持 page -> iframe -> Worker / shared_worker / service_worker；
7. **不再把 `gstyphoon*.js` URL shape 当身份 gate**，hashed / changed / blob 等 URL 可以进入只读 runtime probe；
8. 只读确认 WASM/module/heap readiness；
9. 严格确认 `Warriors of Fate (World 921031)` 和黄金 SHA-256；
10. wrong / missing / ambiguous runtime fail-closed；
11. 每个 endpoint / page / Worker session 独立运行候选 matcher；
12. reload / recreated Worker 结束旧 room，并允许后续重新发现；
13. 自动记录 signal / strict / jitter / late / hard miss / censored；
14. 自动保存统一 prospective corpus 和 result JSON；
15. `Ctrl+C` 结束时把仍在等待结果的 signal 记为 censored，而不是伪装成 PASS。

黄金 World 921031 SHA-256：

`5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`

Browser Fleet 只是 endpoint 入口；Validator 不修改 Fleet，也不修改 WOF-052L Recorder。

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
- 推荐写入黄金 SHA-256。

完整约束见 `manifest.schema.json`，运行时还有额外语义检查。

## 支持的规则表达

### Ordered sequence

支持：

- `tail2`
- `pair`
- `tail3`
- `triple`

每个 state matcher 可以使用：

- `signature`：完全匹配；
- `family`：例如把 timer 归一化为 `TM*`；
- `predicates`：对解析出的 state 字段做条件判断。

### Current-level predicate

`rule.currentPredicates` 可以单独使用，也可以和 ordered sequence 同时使用。

支持 live snapshot 字段包括：

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

一个规则在 `attack == 0` 阶段第一次满足时，当前 cycle 只 arm 一次 signal。

默认时间窗口：

- `strictMaxMs`: 150
- `jitterMaxMs`: 220
- `lateMaxMs`: 1000
- `hardMissMs`: 1500

结果分类：

- `signal`：候选在攻击前实际触发；
- `strict`：命中期望 attack 且 lead <= strict；
- `jitter`：命中期望 attack 且落在 jitter 窗；
- `late`：命中期望 attack 但更晚；
- `hardMiss`：错误 ACTIVE attack，或 signal 后超过 hardMiss 窗仍无 ACTIVE；
- `censored`：signal 已触发，但 Worker/房间/validator 在结局前结束。

## Discovery 与 prospective 严格隔离

这是框架硬约束：

- Discovery V2 topology / runtime 诊断固定为 `discovery-only`，不会写进 prospective corpus；
- `wof-052l-recorder-v1` 历史 JSON 默认按 `discovery` 读取；
- discovery signal 可以统计，但绝不能满足 prospective gate；
- `start_session.py` 固定候选 manifest SHA-256 和 freeze time；
- 使用 session 读取 Recorder 文件时，只有 `startedAt >= frozenAt` 的新房间才可标为 prospective；
- manifest 在 freeze 后被改动，session hash 校验直接失败；
- V2 在真人 probe 准入前和写 corpus 前都会再次校验冻结 session。

离线示例：

```bat
python start_session.py candidate.json --output prospective_session.json
python validator.py candidate.json rooms\room1.json rooms\room2.json --session prospective_session.json --output result.json
```

## WOF-052L 兼容路径

`validator.py` 可以读取：

- `wof-prospective-corpus-v1`；
- WOF-052L `wof-052l-recorder-v1` per-room JSON；
- WOF-052L merged JSON 中保留的 T18 candidate evidence。

`prospective_run.py` 仍保留“冻结候选 -> 调用现有 Recorder -> 自动读取 per-room JSON -> 出结果”的兼容路径。主真人入口是 Discovery V2 live path。

## 多房间与生命周期

- Fleet 每个 localhost endpoint 独立 CDP client；
- endpoint 内每个 page / Worker room 独立 session/history/signal；
- 2 / 10 endpoint 即使出现相同 targetId，也不会跨 endpoint 合并；
- 一个 endpoint/Worker discovery、attach 或 drain 失败不清掉其他房间；
- direct Worker 消失会结束旧 room；
- related Worker 由 page 生命周期 + session 健康度处理 reload/recreated；
- 周期 topology audit 若发现同一 page 有多个通过身份 gate 的 Worker，会 fail-closed；
- 断线前最后一次已知 pending signal 保守记为 censored；
- 不跨 endpoint 复用 session 状态。

## 输出

默认保存到：

```text
parallel/PROSPECTIVE_VALIDATOR/results/
  <timestamp>_<candidate>_live_corpus.json
  <timestamp>_<candidate>_live_corpus.result.json
```

Result schema：`wof-prospective-result-v1`。

即使 gate PASS，verdict 也只允许：

`PROSPECTIVE_PASS_RESEARCH_ONLY`

并且：

`productionPromotionAllowed=false`

## 安全边界

固定：

- `readOnly=true`；
- `ramWrites=0`；
- `inputInjection=false`；
- `windowWorkerReplacement=false`；
- 不替换 / wrap `window.Worker`；
- 不做 Blob/Data/ObjectURL Worker rewrite；
- 不创建 gameplay input；
- 不写游戏 RAM；
- 不自动提升生产规则；
- 不修改 `product/alpha/**`；
- 不修改 `parallel/PYLAUNCH/**`；
- 不修改 `parallel/WOF052L_RECORDER/**`；
- 不修改 `parallel/BROWSER_FLEET/**`。

Discovery V2 CDP 方法只使用 target attach/discovery 与 `Runtime.enable` / `Runtime.evaluate`，不允许 gameplay `Input.*` 或 `Runtime.callFunctionOn`。

## 回归

Fresh Discovery V2 + live-entry regression：**16/16 PASS**。

仓库命令：

```bat
cd parallel\PROSPECTIVE_VALIDATOR
python -m unittest -v test_validator.py test_discovery_v2.py test_entrypoint_v2.py
```

其中：

- `test_discovery_v2.py`：12 项 Discovery V2 / fail-closed / 2-10 endpoint / evidence / safety 回归；
- `test_entrypoint_v2.py`：4 项真人入口防回退检查；
- `test_validator.py`：既有 manifest freeze、pre-freeze discovery、research-only 等 framework regression。

机器结果：`DISCOVERY_V2_REGRESSION_RESULT.json`。

## 真人 Browser proof

不需要为 Discovery V2 单独增加一次 owner 操作。

未来第一次真实 prospective candidate session 正常运行时，同时确认一次 page / iframe / Worker admission、World 921031 identity、read-only safety 与 prospective trace 输出即可。该 proof 与真实 prospective session 合并，不额外浪费真人操作。
