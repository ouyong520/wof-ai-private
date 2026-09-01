# WOF HUDANCHOR BROWSER PROOF TOOLING — START PROMPT

You own a bounded Beta-support tooling stage that consumes the completed `parallel/HUDANCHOR/**` research handoff.

Repository:
- `ouyong520/wof-ai-private`

## Goal

Reduce the one remaining player-anchor Browser projection proof to the smallest safe, preferably one-line, diagnostic operation for the owner.

This is NOT Alpha implementation and must not modify Alpha product code.

## Read first

- `parallel/HUDANCHOR/IMPLEMENTATION_RECOMMENDATION.md`
- `parallel/HUDANCHOR/ANCHOR_MODEL.md`
- `parallel/HUDANCHOR/BROWSER_EVIDENCE.md`
- `parallel/HUDANCHOR/MINIMAL_BROWSER_PROBE.md`
- existing Browser GEO/WebGL/camera/HUD probe code

## Write boundary

Write only under:
- `parallel/HUDANCHOR_PROOF/**`

Do NOT modify:
- `product/alpha/**`
- warning/rule semantics
- existing HUDANCHOR research conclusions except through a separate result handoff

## Required tooling

Prepare a support-only Browser diagnostic that can prove or falsify, in one bounded run where practical:

1. authoritative camera/native X transform;
2. floor/depth screen-Y model;
3. live Z/jump contribution to screen Y;
4. drawing-buffer/content-viewport mapping;
5. one stable above-character clearance usable across ordinary player states;
6. P1/P2/P3 structural reuse if observable;
7. resize/fullscreen/DPR mapping sanity when practical;
8. fail-closed result when projection evidence is insufficient.

Do not use image/color/pixel tracking as the primary method.
Prefer RAM/native render evidence and direct WebGL diagnostics.
Do not require combat or attack choreography.

If human movement is unavoidable, minimize it to a short prescribed sequence and make the diagnostic automatically record evidence so the owner does not need to describe coordinates manually.

## Required outputs

Create:
- `parallel/HUDANCHOR_PROOF/README.md`
- support-only Browser JS/loader if useful
- `OPERATOR_STEPS.md`
- `RESULT_SCHEMA.md`
- `HANDOFF.md`

The final result schema must clearly classify:
- `IMPLEMENTATION_READY`, or
- `FAILED_COMPONENT:<component>` / equivalent bounded failure.

## Stop condition

Stop when the owner can perform the remaining Browser anchor proof with the smallest practical action and return one compact result object.

Do not implement the Beta player-anchored HUD in this stage.