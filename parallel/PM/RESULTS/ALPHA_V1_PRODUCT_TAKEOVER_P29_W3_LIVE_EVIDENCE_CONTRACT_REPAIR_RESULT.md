# Alpha V1 P29 — W3 Live Evidence Contract Repair — RESULT

State: **COMPLETE**

P29 repaired only the W3 live capture/analyzer evidence contract and is integration-ready for PM review. This result does **not** claim real WOF acceptance, Owner-visible acceptance, renderer-source proof, promotion, or alpha-live movement.

## Verdict

The exact tested candidate is `c02f7e108e73665f22eb950573622acb6f452732` / tree `a7b6d2ef443a004e1b3f93723b4139e33df6dc59`.

The repair closes the concrete first-live-run contract defects without weakening the renderer-source truth boundary:

- every analyzer-consumed `candidateTimeline` frame now carries exact `runtimeEpoch`, `rendererEpoch`, and `authorityKey`;
- intentional same-offset BE16/LE16 structural exploration is retained as diagnostic evidence and no longer creates a false `REJECTED` verdict solely because both byte orders were explored;
- safe structural-only evidence with no legitimate `rendererSourceProof` remains deterministically `INCONCLUSIVE`;
- stale/mixed `runtimeEpoch`, `rendererEpoch`, or `authorityKey` remains `REJECTED`;
- the existing strict `PASS` path remains gated on the direct displayed-frame `wof-renderer-source-proof-v1` contract;
- no `rendererSourceProof`, synthetic PASS, screenshot/world-projection production authority, guessed address, or alpha-live movement was introduced.

## Implementation

Implementation commits:

- `184594bf36347dc8a78b1c84d03b711822bea544` — analyzer classifies dual-byte-order structural exploration as an evidence gap rather than a false rejection.
- `e333cc77abad986f0aed500aa57ca3a92bb4caeb` — capture worker stamps every timeline frame with the active runtime/renderer/authority generation.
- `d66441b6b08babe720998510da0fa4f128365c83` — focused analyzer regressions for false BE16/LE16 rejection and stale epoch/authority rejection.
- `c02f7e108e73665f22eb950573622acb6f452732` — capture-worker regression asserts per-frame stamps and absence of fabricated `rendererSourceProof`.

Materially changed worker-owned files:

- `parallel/RENDER_AUTHORITY_V2/qualification_analyzer.py`
- `parallel/RENDER_AUTHORITY_V2/wof_render_authority_capture_worker.js`
- `parallel/RENDER_AUTHORITY_V2/test_qualification_analyzer.py`
- `parallel/RENDER_AUTHORITY_V2/selftest.mjs`

P16/P9 staging and page-association code were not modified.

## Exact candidate readback

Before terminal-significant tests, the durable candidate was bound in PROGRESS and the executed local files were checked against Git blob identity:

- `qualification_analyzer.py` → `a412faa31ac8d946e25f72868a57ae234d92b4b2`
- `test_qualification_analyzer.py` → `d243efbc092dac9fe80c0cfa8c517d9685d5272e`
- `wof_render_authority_capture_worker.js` → `fa3642388d7bf89d77334a86f8091858ff8ad2c2`
- `selftest.mjs` → `588a3781a37a9cc9e390e545328b4812c47cfa7f`

Those identities match the exact tested candidate bytes. No implementation byte changed after the focused tests.

## Focused self-check

Fresh deterministic checks against the exact durable candidate:

- `python -m unittest -v test_qualification_analyzer.py` → **PASS, 10/10**.
  - structural-only safe evidence → `INCONCLUSIVE`;
  - legitimate direct proof remains the only test path to `PASS`;
  - same-offset BE16/LE16 diagnostic exploration → `INCONCLUSIVE`, not false `REJECTED`;
  - stale `runtimeEpoch`, `rendererEpoch`, and `authorityKey` → `REJECTED`;
  - screenshot/world-projection/guessed proof violations remain rejected.
- `node selftest.mjs` → **PASS**.
  - every produced timeline frame carries exact runtime/renderer/authority stamps;
  - structural regions remain `UNVERIFIED_CANDIDATE_ONLY`;
  - result contains no fabricated `rendererSourceProof`.

No real game was launched or exercised.

## Product-proof boundary

This worker proves **repository-side implementation behavior only**.

- `realWofAcceptance = NOT_RUN`
- `ownerVisualAcceptance = NOT_RUN`
- `visibleProof = NOT_PROVEN`
- `alphaLiveMoved = false`

A future real bounded Owner run may still truthfully produce `INCONCLUSIVE` if the repository does not obtain a legitimate direct displayed-frame renderer/object proof. P29 deliberately does not convert structural/stable candidates into renderer authority and does not manufacture PASS.

## Next action

PM should review P29 together with the separately owned P30/P31 repair results. Only after those terminal reviews should PM authorize one fresh bounded Owner live retry. If that retry still lacks legitimate `rendererSourceProof`, the correct W3 verdict remains `INCONCLUSIVE` and the remaining direct renderer-proof blocker must be reported rather than bypassed.
