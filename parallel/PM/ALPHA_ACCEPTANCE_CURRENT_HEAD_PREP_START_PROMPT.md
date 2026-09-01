# WOF Alpha — Current-HEAD Acceptance Prep

stageId: `ALPHA_ACCEPTANCE_CURRENT_HEAD_PREP_V1`

Priority: **P1 — Alpha release support / owner-time reducer**

Follow `parallel/PM/STAGE_DEDUP_GUARD.md`; re-read current HEAD. If equivalent durable prep already exists, return `ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`; if claimed, return `ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`.

Claim `parallel/PM/STAGE_CLAIMS/ALPHA_ACCEPTANCE_CURRENT_HEAD_PREP_V1.json`.

Purpose: prepare the final bounded Windows/Browser/WOF acceptance so that once formal integration + release gates are green, Owner performs one minimal run instead of repeated manual diagnosis.

Allowed writes only under `parallel/ALPHA_ACCEPTANCE_CURRENT_HEAD_PREP/**` plus own claim. Do not modify `product/alpha/**`, PYLAUNCH, Recorder, Unified Live Proof, HUD, or Owner OneClick package.

Continuously re-read current-head contracts while preparing: exact World 921031 identity; Browser/CDP attestation; page/Worker/WASM pair identity; transport session/generation/nonce; detector-local identity; first valid warning; clear/stale behavior; reconnect/rebind; readOnly=true; ramWrites=0; inputInjection=false; gameplay unaffected on failure; Chinese owner-facing status/errors.

Build only repository-side fixture/schema/one-click acceptance orchestration and failure classification. No DevTools, Worker Console, pasted JS, or owner testing now. Produce a compact final JSON schema and a single bounded owner procedure for later use.

Success: `ALPHA CURRENT-HEAD ACCEPTANCE PREP READY — WAITING RELEASE GATES`. Stop/park if active upstream contract drift makes a field unknowable; record the exact dependency rather than guessing. Owner action: **NO**.
