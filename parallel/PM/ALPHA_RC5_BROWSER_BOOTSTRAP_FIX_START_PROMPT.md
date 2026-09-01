# WOF Alpha RC5 — Real Browser Bootstrap Fix Start Prompt

You own a fresh product-engineering stage for the real-Browser room-entry blocker found after RC4 QA PASS.

Repository:
- `ouyong520/wof-ai-private`

Read first:
- `parallel/PM/ALPHA_BROWSER_ACCEPTANCE_BLOCKER.md`
- `parallel/ALPHAQA_RC4/AUDIT_STATUS.md`
- `parallel/ALPHAACCEPT/**`
- current `product/alpha/**`
- prior `parallel/ALPHABOOT/**` findings

## Current owner evidence

The owner completed a stronger three-way A/B on the real Browser host:
- acceptance helper OFF + normal Alpha userscript ON -> game cannot enter the room;
- acceptance helper ON + normal Alpha userscript OFF -> game can enter the room;
- both WOF userscripts OFF -> game can enter normally.

Treat this as a P0 normal-user bootstrap/real-host compatibility blocker isolated to the normal Alpha bootstrap/product attach path rather than the acceptance helper.

## Goal

Produce the smallest RC5 candidate that restores normal room/game entry while preserving the validated Alpha detector/HUD safety contract.

## Scope

You may modify `product/alpha/**` only as needed to fix the bootstrap/Worker interception/injection compatibility defect.

Prioritize diagnosis of the real-host startup path, including:
- `window.Worker` wrapping behavior and constructor semantics;
- classic vs module Worker handling;
- replacing real Worker URL with a Blob URL and any origin/base/importScripts/module/CSP consequences;
- Worker options and credentials/name/type preservation;
- timing at `document-start`;
- page-side loader/HUD fetch/eval interactions only if they can block room entry;
- graceful fail-open for gameplay availability while keeping warnings fail-closed when Alpha cannot attach safely.

Do not spend time blaming or changing the Browser Acceptance helper unless new evidence contradicts the owner control result showing helper-only entry succeeds.
Do not guess from theory alone if existing Browser/host evidence can settle it.

## Mandatory invariant

Alpha must never prevent the base game from starting or entering a room.

If Alpha cannot safely attach, the correct behavior is:
- base game continues normally;
- Alpha warnings remain disabled/silent;
- diagnostic may be exposed without blocking gameplay.

## Preserve all already-passed RC4 safety

Do not regress:
- exact `wof / World 921031` full 1 MiB CPU-logical SHA-256 authority;
- exactly two current-level T18 production rules;
- F1-F4 quarantine;
- same-type slot reuse safety;
- session/cross-tab isolation;
- multi-warning HUD;
- legacy HUD cleanup;
- runtime diag immediate warning invalidation;
- ordinary 1500 ms no-diag stale behavior;
- live target/side and UNKNOWN silence;
- read-only / `ramWrites=0` / no input injection;
- GL state restoration.

Do not do WOF-052, Beta HUD work, attack research, coverage expansion, or broad recollection.

## Testing required before stop

Add focused regression/static tests for the chosen bootstrap fix where possible.
Run the full Alpha product regression.

Create an RC5 report under `product/alpha/**` describing:
- root cause or strongest proven cause;
- exact files changed;
- why base gameplay can no longer be blocked by Alpha attach failure;
- preserved RC4 gates;
- exact minimal owner Browser retest.

## Stop condition

Stop only when either:

A. an RC5 candidate is ready, offline regression passes, and only one minimal real-Browser room-entry retest remains; or

B. the blocker is reduced to one precise real-Browser observation that cannot be obtained from repository evidence.

Do not self-certify final Alpha release. A fresh independent QA/retest stage follows RC5.
