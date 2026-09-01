# WOF-052L Recorder Discovery V2 Hardening Result

stageId: `WOF052L_RECORDER_DISCOVERY_V2_HARDENING_V1`

## Stop condition

`WOF052L RECORDER DISCOVERY V2 HARDENING READY — P0/P1 + CHINESE UX CLOSED IN REPOSITORY`

Repository-side hardening is complete. No Owner intervention is required to close this stage.

## Closed findings

### P0 — cross-page shared Worker ambiguity

- Added an endpoint-level Worker <-> page relation graph across both newly discovered candidates and already-live rooms.
- If one exact Worker `targetId` becomes associated with more than one page, admission fails closed with the exact diagnostic reason:
  - `cross-page-worker-association-ambiguous`
- New ambiguous candidates are closed/rejected.
- If the ambiguity appears after capture has started, only the affected live room(s) are finalized with that reason before later evidence polling; unrelated rooms remain live.
- Page-local ambiguity handling remains fail closed.

### P1 — endpoint confinement

- Generic and owner-facing Recorder discovery now accepts only loopback CDP hosts.
- `127.0.0.1`, `localhost`, and IPv6 loopback are normalized/accepted as loopback aliases.
- `/json/version` `webSocketDebuggerUrl` must resolve to a loopback host and the exact requested CDP port.
- Returned remote-host or cross-port websocket endpoints fail closed.
- When `--cdp-port` is explicitly supplied, Recorder probes only that exact port and no longer falls through to another common CDP port.
- A simulated 10-endpoint regression proves one bad endpoint does not poison the other nine.

### P1 — existing Worker URL drift

- For an already-existing attachable `worker`, `shared_worker`, or `service_worker`, URL scheme is now only a hint/diagnostic.
- Existing `blob:`, `data:`, hashed/no-extension, and `.mjs?query` Worker URLs can proceed to runtime readiness and identity checks.
- Exact World 921031 identity remains authoritative.
- Wrong-identity blob/data Workers remain rejected.
- No Blob Worker is created, replaced, rewritten, or wrapped.

### P1 — direct fallback association

- Worker `openerId` is no longer used as parent authority.
- Direct association prefers actual `parentId`, then `parentFrameId` where available.
- Compatibility fallback is allowed only when the endpoint has one unique page; with multiple pages and no real parent relation it fails closed.
- Page-rooted auto-attach remains the preferred topology path.

### P1 — Simplified Chinese owner UX

- Normal Recorder/Fleet child startup, waiting, browser connection, CDP failure, finalize, shutdown, and merged-result paths are Chinese-first.
- Technical details/reason codes remain available after the Chinese explanation.
- One-click `RUN_WOF052L_RECORDER.cmd` routes through the hardened Chinese frontend and advertises Discovery V2 Hardening plus read-only safety state.
- Live Capture normal aggregate status now uses Chinese owner-visible labels while machine/internal keys remain unchanged.

## Safety and identity invariants retained

- Golden World 921031 SHA-256 remains:
  - `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`
- Runtime/WASM/heap readiness remains required before admission.
- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`
- no `window.Worker` replacement
- no game RAM writes
- no game input injection
- room/session/endpoint isolation retained
- existing cadence/checkpoint/merged JSON schema contracts retained

## Regression evidence

Validated commit:

- `4cb964bda64ced7706d344e95468235abbf9a094` — `WOF052L: route one-click CMD through hardened Chinese owner frontend`

GitHub Actions:

- Workflow: `Owner Tools Chinese UX`
- Run: `33516087731`
- Conclusion: **SUCCESS**
- Both jobs passed:
  - `offline-ux-regression`
  - `windows-utf8-smoke`

### Recorder hardening regression — 21 / 21 PASS

Command executed by CI:

`python -m unittest -v test_fleet_recorder.py`

Result:

`Ran 21 tests ... OK`

The 21-test invocation includes the new hardening matrix plus the existing Discovery V2 regression module. It covers:

1. one page / one exact Worker admission;
2. two pages / two distinct exact Workers independent admission;
3. two pages / same shared exact Worker -> admit none;
4. mid-capture ambiguity -> finalize affected room only;
5. remote CDP host rejection;
6. returned websocket cross-port rejection;
7. loopback alias acceptance;
8. explicit CDP port cannot fall over to another common port;
9. existing blob/data/hashed/no-extension Worker URL handling;
10. wrong-identity Worker rejection despite allowed URL shape;
11. misleading `openerId` cannot misassociate a page;
12. unique-page direct fallback;
13. multi-page direct fallback fail closed;
14. simulated 10-endpoint one-endpoint failure isolation;
15. Chinese-path-with-spaces merged JSON round trip;
16. Chinese-first normal Recorder/Fleet runtime messages;
17. Chinese-first remote-host/CDP error with technical detail second;
18. World SHA/read-only/no-Worker-replacement safety invariants;
19. existing cadence/checkpoint constants;
20. existing Discovery V2 matrix/read-only install regression;
21. existing reload/replacement and 10-endpoint isolation regression.

### Existing/self-test evidence

- WOF-052L Recorder self-test: **PASS**
  - `自检通过 — WOF-052L 采集器安全约束与序列汇总正常`
- Browser Fleet offline regression in the same workflow: **15 / 15 PASS**.
- Operator Toolkit/Chinese CLI regression in the same workflow: **15 / 15 PASS**.

### Windows UTF-8 / owner-entry evidence

The same successful workflow executed on **Microsoft Windows Server 2025**:

- real CMD UTF-8 Simplified Chinese output smoke: **PASS**;
- PowerShell UTF-8 + Chinese path JSON round trip: **PASS**;
- Chinese owner frontends compile on Windows: **PASS**;
- actual `RUN_WOF052L_RECORDER.cmd --self-test`: **PASS**;
- Windows owner-UX regression: **7 / 7 PASS**.

The actual CMD output confirmed:

- `WOF-052L 自动多房间采集器`
- `Worker 自动发现：Discovery V2 Hardening（支持 page / iframe / Worker topology）`
- `只读模式：开启 | 游戏内存写入：0 | 游戏输入注入：无`
- `自检通过 — WOF-052L 采集器安全约束与序列汇总正常`

## Files changed in this stage

Core write scope:

- `parallel/WOF052L_RECORDER/hardening_v2.py`
- `parallel/WOF052L_RECORDER/owner_v2_zh_cn.py`
- `parallel/WOF052L_RECORDER/owner_zh_cn.py`
- `parallel/WOF052L_RECORDER/RUN_WOF052L_RECORDER.cmd`
- `parallel/WOF052L_RECORDER/test_fleet_recorder.py`
- this result file

Minimal Live Capture wrapper adaptation:

- `parallel/WOF052L_LIVE_CAPTURE/live_capture.py`

PM protocol only:

- `parallel/PM/STAGE_CLAIMS/WOF052L_RECORDER_DISCOVERY_V2_HARDENING_V1.json`

No modifications were made by this stage to PYLAUNCH, Browser Fleet, Prospective Validator, WOF052L Analysis, Alpha, OPTOOLKIT, or Regression Orchestrator.

## Minimal facts only a real Owner Windows/WOF session can still prove

Repository-side uncertainty for this stage is closed, and Windows CMD/UTF-8 behavior has already been exercised in CI. The only facts that synthetic/offline tests cannot manufacture are environment-specific observations from an actual Owner machine and live WOF session, for example:

- the installed Chrome/Edge instance exposes the expected loopback CDP endpoint in that machine's real environment;
- a live World 921031 room exposes the expected page/iframe/Worker topology and exact golden identity at runtime;
- real room reload/disconnect timing produces the same topology transitions as the synthetic regressions.

These are future live-proof evidence only, **not repository blockers**, and this result does **not** require the Owner to run anything immediately.

## Final state

**PASS — repository-side P0/P1 hardening and Simplified Chinese owner UX are closed.**

`WOF052L RECORDER DISCOVERY V2 HARDENING READY — P0/P1 + CHINESE UX CLOSED IN REPOSITORY`
