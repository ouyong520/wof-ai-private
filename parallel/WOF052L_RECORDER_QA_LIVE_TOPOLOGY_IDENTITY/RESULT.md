# WOF-052L Recorder Live Topology Identity — Fresh Independent QA Result

stageId: `WOF052L_RECORDER_LIVE_TOPOLOGY_IDENTITY_QA_V1`

## Final stop condition

`PASS — WOF052L RECORDER LIVE TOPOLOGY IDENTITY FRESH QA — READY FOR LONG-CAPTURE QA RETEST`

This is a fresh independent QA result against the current Recorder implementation surface. No Recorder production file was modified by this QA stage.

## SUT lock and parallel-drift handling

The default branch moved during QA because other parallel PM lanes were active. The last pre-result HEAD observed was:

- `6a9af095003ccee17c3edce35d56166237461949`

The Recorder implementation blobs were re-read after parallel drift and remained unchanged from the implementation verification surface:

- `parallel/WOF052L_RECORDER/discovery_v2_sync.py` — `a66731dbf9dd1c6eac8666b2c42ebe8f3f61eddf`
- `parallel/WOF052L_RECORDER/discovery_v2_sync_base.py` — `ddde07ed550110058ef1cae1ed62ae873382c462`
- `parallel/WOF052L_RECORDER/hardening_v2.py` — `4ade786786ec815a0c165c82b25cf41e07f218db`
- `parallel/WOF052L_RECORDER/hardening_v2_base.py` — `4268d39f62d62a624966e7d9fd4afda65f6e94c0`
- `parallel/WOF052L_RECORDER/recorder.py` — `9552d168534f3b742e7390597ff07ea5cfcaeaa2`
- `parallel/WOF052L_RECORDER/fleet_recorder.py` — `9398ef1569815439e6c141890f069674a30dca0f`

Therefore unrelated branch drift did not change the SUT and did not require repeating already-completed vectors.

## Fresh independent fixture

QA-only fixture:

- `parallel/WOF052L_RECORDER_QA_LIVE_TOPOLOGY_IDENTITY/test_fresh_live_topology_identity_qa.py`
- fixture commit: `be84235a9f4ac225b085c35f455cbc5759f6166d`
- fixture blob: `85e84734c152cf75d92e15f87b090e56863888f4`

The committed fixture blob was verified byte-for-byte against the locally executed fixture using Git blob hashing.

Fresh execution result:

```text
Ran 12 tests in 0.002s
OK
```

The hermetic execution loaded byte-exact current copies of `discovery_v2_sync.py`, `hardening_v2.py`, and `hardening_v2_base.py` (Git blob hashes matched the repository blobs above). For the identity compatibility seam, the current `_identity_ok` / `_probe_session` behavior from `discovery_v2_sync_base.py` was mirrored verbatim for the called path; the complete current `discovery_v2_sync_base.py` blob was additionally exercised by the full Windows regression described below.

## Mandatory fresh QA vectors

1. **PASS — live/live shared Worker transition inside the old audit interval.** The fixture starts two already-live rooms, introduces a second live-page relation to the exact same Worker at `now=100` while the old audit timestamp is `95`, and proves the current wrapper forces a full-page proof epoch (`skip_page_ids == set()`). All affected rooms finalize before the subsequent poll and zero evidence polls occur afterward.

2. **PASS — polling between proof epochs cannot collect evidence.** After a valid proof/poll at `100.0`, discovery at `100.2` is not due and the wrapped `poll_rooms(100.2)` is suppressed. Evidence-poll count remains unchanged.

3. **PASS — discovery/probe failure and missing exact current pair fail closed.** A synthetic discovery exception finalizes all live rooms, leaves the reproof token unset, and admits no evidence. A separate missing-current-pair/probe-error topology finalizes the affected room with `live-topology-reproof-failed`; no buffered evidence is deferred into a later epoch.

4. **PASS — reused targetId/new runtime/wrong World.** The same Worker targetId is reused by a different CDP runtime/session. The replacement receives a fresh identity probe and is rejected as `wrong-identity`; the old cache authority does not carry.

5. **PASS — reused targetId/correct recreated runtime.** A correct recreated runtime with the same targetId also receives a fresh identity probe before readmission.

6. **PASS — same still-live CDP session may reuse only its own authority.** Repeated probes on the same client/session lifecycle reuse the proven identity without a second identity evaluation; a different session on the same client immediately forces a fresh probe.

7. **PASS — two distinct pages/two distinct Workers remain independent.** Both exact pairs remain live and admissible, no finalization occurs, and one proof-epoch evidence poll is permitted.

8. **PASS — endpoint/port confinement remains fail-closed.** An explicit request for `127.0.0.1:9444` whose `/json/version` returns a websocket on port `9555` is rejected as `returned-websocket-cross-port`. Only port `9444` is queried and `candidate_ports()` is never invoked, proving no silent cross-port fallover.

9. **PASS — ambiguity finalization preserves accounting/autosave/unrelated isolation.** The affected room finalizes exactly once, contributes exactly one `completed` record and one `room_files` entry, while an unrelated room remains live and untouched.

10. **PASS — Chinese owner-facing failure text remains intact.** Fresh runtime assertions cover the fail-closed Chinese topology message, including `实时拓扑无法重新证明唯一 Worker↔页面归属` and `相关房间已先完成并停止继续收证据`, with the technical reason preserved.

11. **PASS — exact World 921031 SHA remains authoritative.** Authority is pinned to `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`; an alternate SHA is rejected.

12. **PASS — safety contract remains intact.** Runtime diagnostics assert `readOnly=true`, `ramWrites=0`, `inputInjection=false`. Fresh source assertions found no `URL.createObjectURL`, `new Blob(`, gameplay `Input.dispatch*` / `Input.insertText`, or `window.Worker` replacement assignment in the fix/hardening surface, while the owner safety text still states `只读模式开启 / 游戏内存写入 0 / 无游戏输入注入 / 不替换 window.Worker`.

## Current Windows regression evidence

The implementation workflow was independently re-run during this QA:

- workflow: `WOF052L Recorder Live Topology Identity`
- run: `33522460226`
- attempt: `2`
- job: `99913696891` (`windows-regression`)
- runner: Microsoft Windows Server 2025
- Python: `3.11.9`
- conclusion: `success`

The rerun checked out implementation verification commit `e71e12294c5f3692ee8a9296003bff423bc6865d`. The Recorder blobs listed above were re-read at current HEAD and matched that implementation surface, so the Windows regression remains applicable to the current SUT.

Exact Windows test counts from the rerun log:

- existing Discovery V2 regression: `3/3`
- existing fleet regression: `21/21`
- live topology + identity fix regression: `7/7`
- prior independent hardening adversarial suite: `3/3`
- total: `34/34`

All compile and test steps completed successfully.

## Prior blockers re-verified closed

The earlier independent hardening QA blocked on two defects:

- P0: a live/live shared-Worker topology transition could remain invisible during the old 10-second audit gap and evidence polling could continue;
- P1: a recreated Worker could inherit targetId-keyed cached World identity authority.

Fresh QA closes both independently:

- every due discovery epoch is now evidence-gated by fresh live-topology reproof, and polling without an exact same-epoch proof token is blocked;
- identity authority is bound to the current CDP runtime/session token, so targetId reuse alone cannot carry authorization.

No replacement blocker was found.

## Safety / write-boundary audit

This QA stage wrote only:

- `parallel/WOF052L_RECORDER_QA_LIVE_TOPOLOGY_IDENTITY/**`
- `parallel/PM/STAGE_CLAIMS/WOF052L_RECORDER_LIVE_TOPOLOGY_IDENTITY_QA_V1.json`

It did **not** modify `parallel/WOF052L_RECORDER/**`, Alpha, PYLAUNCH, game RAM, game input, Worker construction, Blob/ObjectURL behavior, or gameplay input capability.

Safety contract:

- exact World SHA-256: `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`
- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`
- no `window.Worker` replacement/wrap
- no Blob/ObjectURL rewrite
- no gameplay Input capability

## Owner intervention

`你现在需要操作：NO`

## Final

**PASS. This lane is ready for the long-capture QA retest.**

`PASS — WOF052L RECORDER LIVE TOPOLOGY IDENTITY FRESH QA — READY FOR LONG-CAPTURE QA RETEST`
