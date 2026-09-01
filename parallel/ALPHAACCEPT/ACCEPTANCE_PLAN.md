# WOF Alpha RC3 — Bounded Real-Browser Acceptance Plan

## Preconditions

Final owner acceptance is permitted only after fresh independent RC3 QA returns exactly:

`PASS — READY FOR ONE REAL BROWSER ACCEPTANCE`

At preparation time the QA gate is still closed by `ALPHAQA-RC3-001` (P1 runtime diagnostic stale-warning retention). Do not use a Browser run to waive that blocker.

## Browser-only questions this run answers

The run is intentionally limited to evidence that static/offline QA cannot fully prove.

### B1 — real document-start bootstrap / Worker interception

PASS requires, in the primary page:

- `window.__WOF_ALPHA_BOOTSTRAP_RC3.release === 'wof-alpha-rc3'`;
- `workerIntercepted === true`;
- `hudLoaded === true`;
- `window.__WOF_ALPHA_CONFIG.session` is present and agrees with the HUD/page session;
- the HUD receives a fresh matching-session detector state.

Failure to intercept/load/pair within the bounded startup window is FAIL/INCOMPLETE, never a fallback to a manual Worker Console path.

### B2 — exact World 921031 positive identity

Expected full digest:

`5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`

Expected accepted signature:

`wof-world-921031-maincpu-sha256-v1:5c369ce2de4f53d8`

PASS requires a live detector `state` containing exactly that signature.

Reason this is sufficient Browser evidence for the positive gate: RC3 Worker source computes the normalized full 1 MiB CPU-logical SHA-256 once, calls `validateIdentityProbe()`, and starts/post states only after `identity.ok`. `validateIdentityProbe()` requires an accepted, well-formed 64-hex digest exactly equal to the golden digest; sparse vector/dispatch/layout checks cannot substitute.

The acceptance helper does not duplicate the ROM locator/hash implementation, avoiding a second implementation that could disagree with production.

### B3 — fail-closed runtime behavior during the run

Any live `diag` from the paired detector makes the Browser run FAIL.

The helper records HUD warning count immediately after a diagnostic when possible. The product invariant `warning -> diag => immediate warningCount 0` must already be proven by the fresh QA rerun before this real-Browser stage; the owner is not asked to manufacture a runtime exception or bad ROM.

### B4 — real WebGL HUD path and state restoration

The helper wraps only the existing `window.__WOF_GL_HOOK.callback`; it does not replace the game draw hook or product renderer.

For sampled real HUD callbacks it captures the GL state touched by the product renderer immediately before and immediately after the original HUD callback and requires zero mismatches across:

- current program;
- array-buffer binding;
- active texture and 2D bindings;
- viewport;
- blend/depth/cull/scissor enables;
- blend function/equation;
- color mask;
- pixel-store flip/premultiply flags;
- vertex attribute 0 enable/buffer/layout/offset.

At least one sampled callback must actually increment Alpha HUD `drawCount`; this proves the comparison covered a real HUD draw, not merely an idle callback.

### B5 — cross-tab session isolation and reload pairing

One operator click opens one auxiliary same-origin game tab. The helper coordinates only through a dedicated support control channel.

PASS requires:

1. primary page is connected with session `P` and product channel `CP`;
2. auxiliary first load is connected with session `A1` and channel `CA1`;
3. `P != A1` and `CP != CA1`;
4. auxiliary tab is automatically reloaded;
5. auxiliary second load is connected with session `A2` and channel `CA2`;
6. `A2 != A1`, `A2 != P`, and `CA2 != CA1`;
7. primary remains connected to `P` throughout.

This is the real-Browser complement to offline exact-session message rejection tests.

### B6 — legacy research HUD takeover

If support instrumentation observes `window.WOFHUD` before Alpha HUD installation, a successful Alpha HUD load plus `WOFALPHAHUD.status().researchHudDisposed === true` is required.

If no legacy HUD was present in this run, result is `NOT_APPLICABLE`, not failure.

### B7 — target/side/UNKNOWN sanity without rare attacks

Every naturally observed warning must satisfy all of:

- `ruleId` is exactly one of the two RC3 production T18 rules;
- `target` is `P1`, `P2` or `P3`;
- `target7E` is `0`, `4` or `8` and agrees with `target`;
- `sourceSide` and `threatSide` are `LEFT`, `CENTER` or `RIGHT`;
- `publication === 'hold-only-current-level'`;
- `evidence === 'fresh-current-sample'`;
- no inherited age/watch/history fields are present.

If no active T18 warning occurs naturally, this sub-check is `NOT_EXERCISED`. Infrastructure acceptance may still PASS because attack coverage is outside this Browser run.

### B8 — acceptable Alpha runtime overhead

The helper records actual original HUD callback duration for the same GL-state samples and verifies the product stream/draw loop remains alive during a 6-second observation window.

Automatic catastrophic-overhead guard:

- at least 10 callback samples;
- p95 original HUD callback duration <= 16 ms;
- maximum sampled callback duration <= 50 ms;
- game draw counter advances;
- paired detector remains connected and state messages continue.

Raw measurements are retained in the JSON. These thresholds are smoke-test guards, not a claim that local emulator timing equals Browser attack timing.

### B9 — no RAM writes / no gameplay input injection

This is not re-proven by poking the live game. It is a required external precondition from fresh independent QA/static source inspection. The support helper itself performs no game-RAM access and sends no keyboard/mouse/gameplay input.

## Final result rules

The helper emits exactly one Browser result:

- `PASS — REAL BROWSER ACCEPTANCE` — all required Browser checks pass; optional attack-shape evidence may be `NOT_EXERCISED`.
- `FAIL — REAL BROWSER ACCEPTANCE` — a required Browser invariant fails or a live detector diagnostic/error occurs.
- `INCOMPLETE — REAL BROWSER ACCEPTANCE` — the environment prevented a required check (for example popup blocked or auxiliary page never became ready).

A Browser PASS is **not** an Alpha release declaration. PM/release ownership still consumes the independent QA verdict plus this Browser result.

## Deliberate exclusions

Do not ask the owner to:

- reproduce F1–F4 history rules (they are quarantined);
- provoke BODY4728/A4704, T23, T24, WOF-052 or Beta cases;
- inspect Worker Console manually;
- compare local WinKawaks timing numerically to Browser milliseconds;
- manually compare dozens of Console fields.
