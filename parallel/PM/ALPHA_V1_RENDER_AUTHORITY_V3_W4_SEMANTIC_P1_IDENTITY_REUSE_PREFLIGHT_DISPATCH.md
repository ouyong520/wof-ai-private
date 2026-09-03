# Alpha V3 W4 — Semantic P1 Identity Reuse Preflight Dispatch

Status: **AUTHORIZED SUBWORKSTREAM OF THE EXISTING ACTIVE ALPHA V3 UMBRELLA**

This does not create V4, does not replace the existing V3 umbrella authority, and does not permit production integration changes. The purpose is to accelerate the active V3 W2 semantic-identity integration correction by finding reusable, already-proven P1 character identity evidence in the repository.

## Authority / dedup

- parent stage: `ALPHA_V1_LIVE_ACCEPTANCE_RENDER_AUTHORITY_OWNER_VISIBLE_STARTUP_RECOVERY_V3`
- substageId: `ALPHA_V1_RENDER_AUTHORITY_V3_W4_SEMANTIC_P1_IDENTITY_REUSE_PREFLIGHT`
- dedupProtocol: `v2`
- dedupKey: `alpha.v1.render-authority-v3.w4-semantic-p1-identity-reuse-preflight`
- dedupMode: `exclusive`
- W4 must acquire only its own canonical/stage subworkstream claim.
- W4 must not acquire, modify, close, or reuse the V3 umbrella canonical/stage claim.
- Equivalent W4 ACTIVE/COMPLETE => NO EXECUTION.

## Scope

Read-only repository preflight to locate and rank real semantic P1 identity authorities that the umbrella worker can feed into `parallel/PYLAUNCH/wof_launcher/zero_click_identity_acquisition.py`.

Prioritize reuse from existing Alpha / PYLAUNCH / HUD / exact-World / renderer evidence, including where present:

- P1 HUD portrait / character identity logic;
- exact World 921031 player character `type` semantics;
- local identity / player-slot binding evidence;
- proven sprite/tile/render-object identity evidence;
- existing fixtures/results that establish a mapping between HUD portrait identity and runtime character identity;
- current lifecycle generation and runtime-generation authority that can invalidate stale identity evidence.

The key question is not “which image is colorful”. The key question is: **what existing evidence can non-circularly prove that the current HUD/portrait/tile/render identity belongs to the same P1 character type/generation as the live scene candidate?**

## Hard rules

1. Do not modify production runtime.
2. Do not modify `head_visual_tracker.py`, `measurement_runner.py`, `owner_zh_cn.py`, package manifest/generator, Alpha production JS, or V3 umbrella claims.
3. Do not launch Browser/WOF.
4. Do not fabricate semantic identity by copying runtime P1 type into a HUD candidate.
5. Generic palette similarity, world X/Y/Z projection guesses, or “looks like P1” are not semantic authority.
6. Prefer exact reusable functions/data/contracts already in main over creating new algorithms.
7. If a tiny independent adapter/normalizer is genuinely required, W4 may create it only under a new W4-owned file path plus focused tests; it must remain integration-ready and must not edit existing production callers.
8. No unrelated historical PASS reruns.

## Required output

Produce a durable W4 SUBRESULT containing:

- exact reusable source files/functions/data and commits/blobs;
- for each candidate authority: what it proves, what it does not prove, lifecycle/runtime invalidation semantics, and whether it is safe to feed W2;
- a ranked recommendation for the umbrella worker;
- exact field mapping into W2 `hud_identity_candidates` / scene evidence, avoiding circular identity;
- any precise blocker if the repository truly has no semantic HUD/portrait/tile/render authority.

If there is a safe reusable authority, verdict:

`SUBCOMPLETE — REUSABLE SEMANTIC P1 IDENTITY AUTHORITY FOUND — HAND OFF TO V3 UMBRELLA`

If none exists after exhaustive repository reuse preflight:

`BLOCKED — NO NON-CIRCULAR SEMANTIC P1 IDENTITY AUTHORITY EXISTS IN CURRENT REPOSITORY — <exact missing evidence>`

W4 is finished after durable SUBRESULT and its own claim/stage closeout. It must not publish a package or mark V3 COMPLETE.
