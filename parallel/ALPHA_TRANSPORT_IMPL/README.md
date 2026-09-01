# WOF Alpha Safe Transport Reference Implementation V1

状态：**ALPHA TRANSPORT REFERENCE IMPLEMENTATION READY FOR INTEGRATION**

这个目录是冻结 Safe Transport Contract 的浏览器解耦 reference runtime。它不连接真实 Chrome，不修改 `product/alpha/**`、`parallel/PYLAUNCH/**`、Recorder、Prospective 或 Live Proof，也不假设真实 Chrome topology 已经最终证明。真实运行能力全部通过 adapter 注入。

## 实现边界

- `constants.mjs`：冻结 schema/version、World 921031 golden SHA、pair/session 校验、exact identity gate、CDP allowlist、snapshot/warning/safety 校验。
- `page_authority.mjs`：page/HUD warning authority；session/generation/nonce/seq 隔离；current diag 立即清权；1500/1501 ms stale 边界；fixed HUD output contract。
- `worker_runtime.mjs`：runtime epoch、dual identity gate、最多一个 tick in-flight、immutable tick authority、stale completion revoke、跳过 missed interval、不做 catch-up queue、warning change/clear 立即发布、<=250 ms heartbeat、failure fail-open gameplay/fail-closed warning。
- `stale_inflight_generation_regression.mjs`：覆盖旧 generation tick 未完成时 rebind/runtime epoch/Worker replacement 的 deterministic race regression，证明旧 completion 不发布且不消费新 generation in-flight ownership。
- `detector_adapter.mjs`：只包装 canonical `WOFAlphaCore.createEngine().step(...)`；不复制/重写 warning predicate。
- `adapters.mjs`：未来正式 Integration 的 Discovery / Native Worker runtime / Page-HUD transport adapter 接口，以及固定 CDP allowlist wrapper。
- `reference_runtime.mjs`：把 adapter 编排为 page -> exact Worker -> launcher identity -> page bind -> detector-local identity -> observer install 的 reference control flow。
- `acceptance_adapter.mjs`：直接读取 sibling `parallel/ALPHA_TRANSPORT_MOCK/{fixtures,vectors,expected_results}.json`，按同一 V01-V67 catalog 验证本 reference implementation；没有另建更宽松标准。
- `selftest.mjs`：reference-only 接口/编排自测。
- `run_all.mjs` / `RUN_REFERENCE_ACCEPTANCE.cmd`：统一运行 stale-generation regression + selftest + 67-vector acceptance，生成 `selftest_result.json` 与 `result.json`。

## Tick authority completion contract

每个 detector tick 在启动时都绑定 immutable authority：`runtimeEpoch + session + pairGeneration + pairNonce + unique tickAuthorityId`。异步 detector callback 应使用：

```text
const authority = worker.startTick({ captureAuthority: true });
...
worker.finishTick({ nowMonoMs, warnings, tickAuthority: authority });
```

completion 只有在该 authority 仍同时匹配当前 runtime/pair 且仍持有当前 in-flight slot 时才能发布。rebind/reinstall/runtime epoch reset/Worker replacement 会立即撤销旧 authority；旧 callback 返回 no-op，且绝不能清除或借用新 generation 的 slot。

为兼容已有同步 reference vectors，未发生 unresolved-tick revoke 前，旧的 `startTick() === true` / untagged `finishTick(...)` 仍可工作。一旦发生“旧 tick 未完成即 rebind/reset”，untagged completion 因无法证明归属而永久 fail closed；新异步接线必须传 `tickAuthority`。

## 安全不变量

固定：

```text
readOnly=true
ramWrites=0
inputInjection=false
workerReplacement=false
blobRewrite=false
gamePostMessageControl=false
heapWrites=false
assistMode=false
```

reference implementation 没有 Worker 构造/替换、Blob Worker、游戏 RAM 写、`Input.*`、键鼠/手柄注入、游戏 `postMessage` command/control、自动移动或游戏速度控制路径。

## 运行

Windows：双击 `RUN_REFERENCE_ACCEPTANCE.cmd`。

Node：

```text
node run_all.mjs
```

成功条件：

```text
stale in-flight generation regression: PASS
selftest: PASS
contract: 67/67 PASS
ALPHA TRANSPORT REFERENCE IMPLEMENTATION READY FOR INTEGRATION
```

## 正式 Integration 仍需接入的最小接口

### 1. Discovery adapter

```text
readPageConfig(pageRef)
listTargets()
resolveWorker(targets, pageRef)
```

输入来自 hardening 后 PYLAUNCH discovery。必须保留 exact page/session/tab association；歧义必须 fail closed。

### 2. Native Worker runtime adapter

```text
launcherIdentityProbe(workerRef)
detectorLocalIdentityProbe(workerRef)
installObserver(workerRef, binding, detectorAdapter)
statusObserver(workerRef)
stopObserver(workerRef)
```

`launcherIdentityProbe` 必须提供 module/heap/candidateCount/hashStatus/golden SHA/readOnly/ramWrites/inputInjection 的固定探针结果；`detectorLocalIdentityProbe` 必须提供 canonical detector-local identity signature 与安全字段。任何 gate 不满足都不得建立 warning authority。

### 3. Alpha detector adapter

```text
constructor(canonicalAlphaCore)
evaluate(snapshot)
reset()
diagnostics()
```

正式 Integration 传入 release-pinned canonical Alpha core；transport 不得在 Python/reference layer 复制规则或 RAM predicate。

### 4. Page/HUD transport adapter

```text
bind(pageRef, pairNonce)
status(pageRef)
reset(pageRef)
```

page 必须拥有单调 `pairGeneration`；bind 立即撤销旧 authority；首次 valid current-pair state 后才允许 HUD warning authority。

## 不属于本 stage 的事项

- 不实现真实 CDP/Chrome topology。
- 不修改 RC5 bootstrap/product Alpha。
- 不修改 PYLAUNCH hardening。
- 不做新攻击研究/Beta rule。
- 不要求 Owner 真人测试。
