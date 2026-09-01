# WOF Alpha — Transport-Aware Browser Acceptance V2 Preparation

Updated: 2026-09-01

Status: **ACCEPTANCE PREP READY — WAITING FOR TRANSPORT INTEGRATION**

This directory is the support-only preparation lane for the bounded real-Browser acceptance that follows the Safe Transport Integration offline PASS.

It does **not** modify `product/alpha/**`, does **not** implement the transport, does **not** modify WOF-052L, and does **not** declare Alpha released.

## Current authoritative gates

Already accepted and not reopened here:

- fresh RC5 independent QA: `PASS — RC5 ROOM-ENTRY REPAIR QA`;
- exact supported build: `wof / Warriors of Fate (World 921031)`;
- exact 1 MiB CPU-logical SHA-256:
  `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`;
- only two current-level T18 production rules;
- F1-F4 quarantined;
- same-type slot reuse carries no warning history;
- current valid `diag` immediately invalidates warning authority;
- ordinary no-diag stale boundary is exactly 1500 ms;
- read-only / `ramWrites=0` / `inputInjection=false`;
- no `window.Worker` replacement/wrapping and no Blob/Data/ObjectURL game Worker.

Current external sequence remains:

1. PYLAUNCH real Windows Browser/page/Worker/WASM/World proof passes while the room remains playable;
2. Safe Transport Integration is implemented and all offline/mock gates pass;
3. this V2 bounded Browser acceptance runs once;
4. PM decides whether Alpha may release.

Until step 2 is complete, the V2 helper intentionally reports **等待安全 Transport 集成** rather than pretending acceptance can run.

## Prepared V2 artifacts

- `ACCEPTANCE_PLAN.md` — exact real-Browser acceptance matrix and PASS/FAIL rules.
- `ACCEPTANCE_DRIVER_CONTRACT.md` — fixed handoff contract for the future PYLAUNCH integration/acceptance driver.
- `OPERATOR_STEPS.md` — Simplified-Chinese minimal owner workflow; no DevTools/Worker Console/pasted JS.
- `RESULT_SCHEMA.md` — compact `wof-alpha-browser-acceptance-v2` JSON contract.
- `fixtures/transport_acceptance_v2.json` — machine-readable constants and required scenario vectors.
- `validate_acceptance_result.py` — stdlib-only final JSON validator for QA/PM.
- `wof_alpha_acceptance.user.js` — support-only page collector/UI prepared for current-pair transport metadata and lifecycle evidence.

## What V2 is prepared to prove

The final bounded run must cover:

- `transportVersion`, page `session`, `pairGeneration`, `pairNonce`;
- Browser / WOF page / native Worker / WASM heap / exact World 921031 status;
- detector-local identity accepted;
- first valid **current-pair** state is what gives HUD authority;
- ordinary stale behavior: fresh through 1500 ms, silent after 1500 ms (exact 1500/1501 boundary remains an offline integration gate; Browser run records bounded live evidence);
- current-pair `diag` clears warning authority immediately;
- reconnect/rebind creates a fresh generation + nonce;
- old generation / wrong nonce messages are rejected;
- gameplay remains fail-open through attach/stop/rebind;
- `readOnly=true`, `ramWrites=0`, `inputInjection=false`;
- room remains playable;
- one compact final acceptance JSON.

An already-approved T18 warning is exercised only when practical with an existing bounded fixture. No new attack research is created to manufacture one.

## Owner UX

Owner-facing text in this lane is Simplified Chinese by default. Machine JSON keys/schema/version values remain English for compatibility.

The intended final operation is one bounded run from the integrated Launcher/Toolkit path:

`进入 WOF 房间 -> 确认当前可正常操作并点击一次“开始验收” -> 自动完成 -> 返回一个 JSON`

No DevTools, Worker Console, manual JavaScript paste, RAM inspection, or gameplay-input injection is part of the flow.

## Safety boundary

This lane never:

- writes game RAM;
- injects keyboard/mouse/controller/gameplay input;
- changes game speed;
- replaces/wraps `window.Worker`;
- creates or rewrites the native game Worker;
- adds warning rules or attack research;
- modifies `product/alpha/**`;
- modifies WOF-052L.

Synthetic stale/old-pair fixtures are support-only message/control tests and never mutate the game heap or gameplay controls.

## Stop condition

Repository-side acceptance preparation is complete.

**ACCEPTANCE PREP READY — WAITING FOR TRANSPORT INTEGRATION**
