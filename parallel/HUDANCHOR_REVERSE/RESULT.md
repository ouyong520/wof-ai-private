# HUDANCHOR Player Projection Reverse — Result

Stage: `HUDANCHOR_PLAYER_PROJECTION_REVERSE_V1`

## Terminal status

`HUDANCHOR PLAYER PROJECTION REVERSE READY — ONLY EXACT BOUNDED LIVE PROOF REMAINS`

This stage has exhausted the useful repository-side static/history/synthetic/replay evidence without guessing renderer/session constants.

## Mandatory checklist

| Item | Result |
|---|---|
| player X -> native X | **CANDIDATE CLOSED**: `worldX - camera + xBias`; exact camera + bias require bounded live proof |
| camera X address/read/sign/scale | **LIVE PROOF REQUIRED**: bounded `u16be` scanner and quality gate exist; no retained authoritative selected camera result exists |
| player Y/depth -> native/screen Y | **CANDIDATE FAMILY CLOSED**: raw floor/depth Y semantics are offline supported; exact visual model is one of `Y-Z`, `Y+Z`, `Y` |
| Z/jump correction | **LIVE PROOF REQUIRED**: one jump selects the stable member of the three-model family |
| drawing-buffer/content viewport mapping | **OFFLINE CLOSED**: use live WebGL `VIEWPORT`, 384x224 native raster, current drawing buffer |
| resize/fullscreen/DPR mapping | **OFFLINE CLOSED AS RUNTIME CONTRACT**: remeasure current CSS rect / DB / viewport; never freeze DPR or CSS scale |
| stable above-character clearance range | **LIVE PROOF REQUIRED**: one calibration click defines logical anchor; stability is checked through motion/depth/jump |
| shared P1/P2/P3 | **OFFLINE STRUCTURALLY CLOSED**: P1/P2 movement semantics plus common P1/P2/P3 record layout/stride; existing proof validates live extras only when observable |
| fail-closed stale/camera epoch mismatch | **OFFLINE CLOSED POLICY**: same Worker state for player+camera; <700 ms top freshness; locked camera must match calibration identity; otherwise no anchored cue |

## Frozen offline inputs

Machine-readable candidate:

`parallel/HUDANCHOR_REVERSE/projection_candidate.json`

Supporting reasoning:

`parallel/HUDANCHOR_REVERSE/OFFLINE_EVIDENCE.md`

Key closed inputs include:

- native raster `384 x 224`;
- P1/P2/P3 bases `0xFFBE1C / 0xFFBEFC / 0xFFBFDC`;
- record stride `0xE0`;
- Browser player XYZ reader: signed big-endian 32-bit 16.16 at `+0x04/+0x08/+0x0C` through the existing `address ^ 1` bridge mapping;
- direct native -> drawing-buffer mapping through the current WebGL viewport;
- fail-closed Worker freshness and locked-camera identity contract;
- exact objective thresholds already implemented by the support-only Browser proof tooling.

## Why implementation constants cannot be honestly derived further offline

The repository has a bounded camera-candidate algorithm but no retained successful Browser proof JSON that selects the real camera address. Likewise, the desired warning center is a visual renderer-space target, so its bias/clearance and the jump Z sign cannot be inferred from player RAM structure alone.

The existing proof tooling is specifically designed to observe these facts without pixel tracking or broad RAM expansion. Continuing offline would mean inventing game constants, which violates the fail-closed requirement.

## Exact remaining proof

`parallel/HUDANCHOR_REVERSE/MINIMAL_LIVE_PROOF.md`

It reuses `parallel/HUDANCHOR_PROOF/OPERATOR_STEPS.md` and requires one uninterrupted session only:

1. horizontal motion with real background scroll until the automatic bounded camera gate passes;
2. one click at the desired warning-anchor center above P1;
3. post-calibration horizontal/camera excursion;
4. one clear depth excursion;
5. one jump;
6. one resize/fullscreen/layout transition and stable remap;
7. P2/P3 observation only if they are already live;
8. one final visual classification button;
9. return the generated JSON only.

A valid success is exactly an `IMPLEMENTATION_READY` proof JSON with the frozen projection block. Any missing or disproved component remains `FAILED_COMPONENT:<component>`.

## Safety / scope

- no `product/alpha/**` modification;
- no current formal HUD implementation modification;
- no PYLAUNCH / Recorder / Browser Fleet / Prospective modification;
- no RAM writes;
- no input injection;
- no broad RAM-map expansion;
- no claim that sprite height/top was reversed.
