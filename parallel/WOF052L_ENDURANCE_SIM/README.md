# WOF-052L 10-Room Endurance Simulation

状态目标：`WOF052L 10-ROOM ENDURANCE SIM READY`

这是纯离线、事件时间加速的 10 房间耐久模拟 / replay harness。它不需要真实浏览器，不连接 CDP，不写游戏 RAM，不注入输入，也不修改 Recorder/Fleet/Live Capture/Analyzer/Handoff/Alpha。

## 一键运行

Windows 双击：

```text
RUN_WOF052L_10ROOM_ENDURANCE_SIM.cmd
```

默认输出到本目录 `runtime/`：

```text
runtime/ENDURANCE_MATRIX.json
runtime/结果摘要.md
runtime/scenarios/**
```

也可运行：

```bat
py -3 endurance_sim.py --self-test
py -3 -m unittest -v test_endurance_sim.py
```

## 覆盖

固定矩阵覆盖 16 个必需 gate：10 房间 1h / 2h / overnight 等价时间、单房断开、Worker reload/replacement、page close/finalize、endpoint stale/recover、10 秒逻辑 checkpoint、per-room final JSON、child/Fleet merged JSON、Ctrl+C 等价收尾、abrupt child failure 证据保留、Analyzer watch/final fixture compatibility、Prospective Handoff frozen canonical SHA compatibility、room/session isolation，以及 `readOnly=true / ramWrites=0 / inputInjection=false`。

时间加速使用 event-time；不会真的等待 1/2/8 小时。checkpoint 逻辑频率与当前 Recorder 的 10 秒周期一致，但只物化最新 checkpoint 快照，等价于 Recorder 的原子覆盖语义，避免离线测试产生数万次冗余磁盘写。

## 当前组件兼容策略

生成的 fixture 使用当前合同：

- per-room / child merged: `wof-052l-recorder-v1`
- Fleet merged: `wof-052l-fleet-supervisor-v1`
- World: `Warriors of Fate (World 921031)`
- SHA-256: `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`

当脚本位于完整仓库中运行时，它会自动找到仓库根目录并额外执行真实当前 `WOF052L_ANALYSIS/analyzer.py` 的 running/final fixture pass，以及 `WOF052L_PROSPECTIVE_HANDOFF/handoff.py --prepare-only`，验证 ordered candidate、research-only manifest 与 canonical SHA freeze。若只复制本目录单独运行，则执行对应的静态 contract compatibility 断言。

## Replay

可对已有 Recorder/Fleet JSON 做只读 replay 合同检查：

```bat
py -3 endurance_sim.py --replay "D:\WOF_CAPTURE"
```

不会改写 replay 输入。

## 失败归属

`ENDURANCE_MATRIX.json` 每个 scenario 都包含 `layer`、`failedAssertions` 与中文详情。失败会精确归到 orchestration / analyzer / handoff / safety 等层，不要求 Owner 真人调试。

## 仍需真实长采集证明

离线 harness 无法证明真实 Windows/Chrome/Edge 1h/2h/overnight 的 OS/GPU/网络稳定性、真实 Worker/WASM 长时间资源行为、真实 10 房间事件分布和覆盖速度，以及 OS 级 Ctrl+C/进程崩溃边界。这些单独保留为 real-only facts，不影响 repository-side endurance simulation 的 READY 判定。
