# WOF-052L 10-Room Endurance Simulation Result

## Verdict

**WOF052L 10-ROOM ENDURANCE SIM READY**

Repository-side synthetic/replay endurance gate: **PASS 16/16**.

This stage does not claim that a real Windows/Chrome 10-room overnight run has happened. It proves the repository-side orchestration, evidence lifecycle, schema compatibility, isolation, failure preservation, Analyzer/Handoff fixture contracts, and safety invariants without asking Owner to run a real long capture.

## What was executed

Local isolated execution of the exact staged files before commit:

```text
python -m py_compile endurance_sim.py test_endurance_sim.py
python -m unittest -v test_endurance_sim.py
python endurance_sim.py --self-test
python endurance_sim.py
```

Results:

```text
unit tests: 2/2 PASS
endurance matrix: 16/16 PASS
stop condition: WOF052L 10-ROOM ENDURANCE SIM READY
```

The machine-readable result is `ENDURANCE_MATRIX.json`.

## Required matrix

All required gates passed:

1. 10 rooms normal 1h equivalent;
2. 10 rooms 2h equivalent;
3. 10 rooms overnight equivalent (8h event-time fixture);
4. one room disconnects while the other 9 continue;
5. Worker reload/replacement advances only that room epoch/session;
6. page close/finalize produces that room final evidence;
7. stale browser endpoint pauses only that room and recovery starts a fresh epoch;
8. logical checkpoint cadence matches current Recorder 10-second interval; event-time acceleration materializes only the latest overwrite snapshot;
9. per-room final JSON uses current Recorder v1 room contract;
10. child merged + Fleet merged JSON use current aggregation contracts;
11. Ctrl+C/graceful-equivalent path finalizes children before Fleet final index;
12. abrupt child failure preserves last checkpoint + local final + recovery bundle while other 9 continue;
13. Analyzer running/final fixture contract is checked, and when run inside the full repo the harness invokes the actual current `analyzer.py` for both passes;
14. Prospective Handoff ordered candidate / research-only manifest / canonical SHA freeze contract is checked, and full-repo mode invokes current `handoff.py --prepare-only`;
15. endpoint/page/Worker/session/room identities and traces remain room-isolated;
16. every generated evidence surface asserts `readOnly=true`, `ramWrites=0`, `inputInjection=false`; Fleet evidence also asserts `windowWorkerReplacement=false`.

## Current HEAD compatibility snapshot

Final compatibility read was performed against repository HEAD around commit:

```text
9abe324373fe5f0b488f19f951eb9eb0e3b7d74e
```

Verified blobs:

```text
parallel/WOF052L_RECORDER/recorder.py                     9552d168534f3b742e7390597ff07ea5cfcaeaa2
parallel/WOF052L_RECORDER/fleet_recorder.py               9398ef1569815439e6c141890f069674a30dca0f
parallel/WOF052L_RECORDER/hardening_v2.py                 4268d39f62d62a624966e7d9fd4afda65f6e94c0
parallel/BROWSER_FLEET/DISCOVERY_CONTRACT.md              0de1fcf7aa1a540f682b6edd0ed8316831f7d912
parallel/WOF052L_LIVE_CAPTURE/live_capture.py             4482c8e8e5d65b603f16698d5183cc3bdaa7e9ee
parallel/WOF052L_ANALYSIS/analyzer.py                     0da2a7ba50bf5cc47df03eb73f0e2f2cdcd838cb
parallel/WOF052L_ANALYSIS/ingest.py                       d057f98dd2dba7e7602a74509ac8c8e4fadce135
parallel/WOF052L_ANALYSIS/test_analyzer.py                 1c59d1522bb3d399d32ce91ffd109a62c26adb56
parallel/WOF052L_PROSPECTIVE_HANDOFF/handoff.py           8ec85c45eede320adc888320c3fc97d1e6c82df0
```

A concurrent Live Capture change after the stage claim was re-read. It only translated owner-visible status text (`candidate` / `RAM writes`) into Simplified Chinese; it did not change the Recorder/Fleet JSON schemas or the Analyzer/Handoff fixture contract. Discovery V2 hardening was also re-read: it adds loopback/same-port endpoint enforcement and fail-closed cross-page Worker association handling while preserving per-room finalization and other-room continuation. No simulator schema adaptation was required after that drift check.

## Existing fixture/history used

The stage did not invent a conflicting aggregation model. It explicitly re-read the existing Analyzer fixtures that prove:

- merged run preferred over duplicate room primary aggregation;
- room JSON may supplement T23/rare evidence;
- identical traces remain separate by room;
- partial Fleet + child input does not double counts;
- missing safety metadata blocks resolution.

It also re-read existing Fleet recorder tests for sorted localhost-only manifest handling and fail-open empty/wrong manifests, plus an existing BASECAP read-only task JSON as a historical acquisition-schema example. The endurance `--replay` mode can consume existing Recorder/Fleet JSON read-only without altering source data.

## One-click offline entry

```text
parallel/WOF052L_ENDURANCE_SIM/RUN_WOF052L_10ROOM_ENDURANCE_SIM.cmd
```

No real browser is required for this endurance simulation stage.

## Outputs

```text
parallel/WOF052L_ENDURANCE_SIM/endurance_sim.py
parallel/WOF052L_ENDURANCE_SIM/test_endurance_sim.py
parallel/WOF052L_ENDURANCE_SIM/RUN_WOF052L_10ROOM_ENDURANCE_SIM.cmd
parallel/WOF052L_ENDURANCE_SIM/README.md
parallel/WOF052L_ENDURANCE_SIM/ENDURANCE_MATRIX.json
parallel/WOF052L_ENDURANCE_SIM/RESULT.md
```

## Real-only facts intentionally not claimed

These still require a real long capture if/when product evidence needs them:

- real Windows Chrome/Edge process, OS, GPU and network stability for 1h/2h/overnight;
- actual WOF page/Worker/WASM resource behavior and real reload/CDP disconnect timing over long duration;
- real 10-room event distribution, coverage rate and prospective evidence production speed;
- OS-level Ctrl+C/window close/browser crash/kill-process behavior.

They are separated from repository-side orchestration bugs and are **not** Owner actions required to close this stage.

## Safety

```text
readOnly=true
ramWrites=0
inputInjection=false
windowWorkerReplacement=false
product/alpha/** unchanged
Recorder/Fleet/Live Capture/Analyzer/Handoff core unchanged
```

## Stop condition

`WOF052L 10-ROOM ENDURANCE SIM READY`
