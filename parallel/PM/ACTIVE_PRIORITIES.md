# WOF Future Danger AI — Active Priorities

Updated: 2026-09-01 — real Windows proof found a PYLAUNCH Worker-discovery P0; acceleration tools reached repository-side stop conditions

## P0 — Fresh PYLAUNCH real Chrome Worker discovery fix

Authoritative real Windows evidence:
- Chrome 151 localhost CDP connected successfully;
- owner entered a real WOF room and game remained playable;
- `browser_connected=true`;
- `read_only=true`, `ram_writes=0`, `input_injection=false`;
- but `wof_page_found=false`, `worker_found=false`, `wasm_module_found=false`, `world_921031=false`;
- exact diagnostic: `identity_reason="no gstyphoon worker target"`.

This is now the sole immediate Alpha P0.

Fresh stage:
- `parallel/PM/PYLAUNCH_WORKER_DISCOVERY_FIX_START_PROMPT.md`

Goal:
- fix real Chromium/WOF target discovery without DevTools or owner JS;
- preserve unique page/Worker association and exact World 921031 gate;
- keep game fail-open;
- keep readOnly / ramWrites=0 / no input injection;
- convert PYLAUNCH owner-facing UI/status/errors to Simplified Chinese;
- return to one direct-download / one-double-click Windows proof.

Do not run the old proof again until this fresh fix stage explicitly reports READY.

## CLOSED — RC5 independent room-entry repair QA

Verdict remains:

**PASS — RC5 ROOM-ENTRY REPAIR QA**

The former `Alpha prevents room entry` P0 is fully closed. Do not reopen without contrary evidence.

## READY / WAITING LIVE PROOF — Browser Fleet Manager

Repository-side Browser Fleet implementation is complete:
- one-click 1 / 5 / 10+ isolated Browser instances;
- independent profiles and localhost CDP ports;
- window layout;
- independent restart/close;
- shared manifest discoverable by PYLAUNCH/WOF-052L;
- offline regression PASS.

Do not request owner live proof yet. First finish the PYLAUNCH discovery fix and Chinese owner UX pass so one human run can validate the combined path.

## READY / WAITING LIVE PROOF — WOF-052L automatic multi-room recorder

Implementation is complete enough for live proof:
- remembered save folder;
- one CMD start;
- automatic multi-room Worker discovery;
- independent room/Worker lifecycle;
- compact checkpoints/per-room/final merged JSON;
- mandatory T18 ordered evidence + bounded secondary coverage;
- no long raw dump;
- read-only / no input injection.

Do not start long collection yet. Real Worker discovery must first be proven on the owner machine.

## READY — Operator Toolkit V1

Repository-side Windows Operator Toolkit V1 is ready and integrates existing Launcher / Fleet / Recorder / regression / diagnostics paths.

A fresh Chinese UX pass is now required before calling it owner-ready.

Fresh stage:
- `parallel/PM/TOOLS_CHINESE_UX_PASS_START_PROMPT.md`

This stage owns Browser Fleet / WOF-052L / Operator Toolkit owner-facing localization only; it must not touch PYLAUNCH while the P0 fix owns that directory.

## READY — Alpha Safe Transport Integration Contract

The full safe transport contract is implementation-ready:
- `parallel/PM/ALPHA_SAFE_TRANSPORT_INTEGRATION_CONTRACT.md`
- fresh implementation prompt already exists at `parallel/PM/ALPHA_SAFE_TRANSPORT_INTEGRATION_START_PROMPT.md`.

Actual Alpha transport implementation remains BLOCKED until the real PYLAUNCH Worker/WASM/World proof passes.

## P1 acceleration — Owner one-click package/bootstrap

Fresh stage:
- `parallel/PM/OWNER_ONECLICK_PACKAGE_START_PROMPT.md`

Goal:
- one direct download link;
- owner downloads one Chinese bootstrap CMD or tiny ZIP;
- double-click installs/updates the current tools atomically;
- no Git/GitHub Desktop/repository-directory knowledge required;
- then open the Chinese WOF Toolkit.

This is a project-acceleration lane and may proceed in parallel.

## Project-wide owner UI rule

Authoritative requirement:
- `parallel/PM/CHINESE_UI_UX_REQUIREMENT.md`

All owner-facing tools must default to Simplified Chinese. Internal JSON keys/schema/code identifiers may remain English.

## Browser acceptance / Alpha release

Full Browser acceptance remains PAUSED.

Required sequence now:
1. fresh PYLAUNCH Worker-discovery fix;
2. one new real Windows proof: Browser/page/Worker/WASM/World/read-only + game playable;
3. fresh Alpha safe transport integration implementation;
4. integrated regression;
5. bounded real Browser acceptance for actual warning/HUD behavior;
6. PM Alpha release decision.

## Current fastest path

**PYLAUNCH Worker discovery fix -> one new Windows proof -> Alpha transport integration -> bounded Browser acceptance -> Alpha release decision**

Parallel acceleration:
- Chinese owner UX pass;
- owner one-click package/bootstrap.

Parked at repository-side stop condition until live proof:
- Browser Fleet;
- WOF-052L Recorder;
- Operator Toolkit core implementation;
- Safe Transport Integration Prep/Contract.
