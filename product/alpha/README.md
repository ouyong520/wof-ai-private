# WOF Future Danger — Alpha RC5 Browser Bootstrap Candidate

Status: **RC5 bootstrap candidate — gameplay-first bootstrap fix in progress; real-Browser room-entry retest remains required.**

Supported Browser lineage remains **WOF / Warriors of Fate (World 921031)**. The authoritative program identity is the exact full 1 MiB CPU-logical SHA-256:

`5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`

RC5 does not change the RC4 detector/HUD safety contract or promote any new attack rule. It only changes the normal-user Browser bootstrap after real Browser acceptance proved that the previous Blob Worker replacement could prevent the game from entering a room.

## RC5 gameplay-first bootstrap invariant

The normal userscript entry remains:

`product/alpha/wof_alpha_bootstrap.user.js`

It still runs at `document-start` and creates a fresh 128-bit per-page session, but RC5 **does not wrap, replace, proxy, or reconstruct `window.Worker` at all**. In particular it creates no Blob Worker and does not rewrite the target Worker URL/options.

This is intentional. The previous userscript replaced the game's native Worker target with a generated Blob wrapper so it could run the original game code and then inject Alpha. That replacement can change Worker `self.location`, relative resource resolution, `importScripts()` / module import behavior, CSP behavior, and classic/module construction semantics. The repository's earlier ALPHABOOT audit had already identified those as unacceptable production risks; the real Browser room-entry failure is consistent with that risk.

RC5 therefore enforces this priority:

1. base game Worker construction and room entry are authoritative and must remain native;
2. Alpha warnings remain fail-closed/silent until a compatible **non-replacing live-Worker transport** has actually paired with this page session;
3. page HUD code is not fetched/evaluated until a valid session-bound detector `state` message has been observed;
4. secure-session failure, BroadcastChannel failure, detector absence, loader failure, HUD failure, or diagnostic state may disable Alpha, but must not block the base game.

A normal userscript with no safe live-Worker transport will therefore show **no danger warnings**. That is a deliberate RC5 fail-closed state, not permission to fall back to Worker replacement.

## Minimal real-Browser RC5 room-entry retest

For the blocker retest, keep **Browser Acceptance Helper disabled**. Enable only the current normal Alpha userscript, refresh the game page, and answer one question:

**Can the game enter a room normally?**

No Worker-console work, warning triggering, attack testing, or Console data collection is required for this RC5 blocker retest.

The old Acceptance Helper was built around the RC3 `workerIntercepted=true` bootstrap contract and is not the readiness authority for this retest.

## Authoritative runtime identity gate — unchanged

Warnings cannot initialize until all of the following are true inside a safely attached live Worker:

1. Browser/WASM layout sanity passes: shared HEAP buffer, valid CPS RAM window, self indexes `0/4/8`.
2. The retained reset-vector/dispatch checks locate exactly one plausible 1 MiB program candidate. These checks are locator/sanity helpers only, not proof of build identity.
3. The candidate is normalized to CPU-logical byte order and SHA-256 hashed once for that Worker/runtime startup.
4. The resulting lowercase digest equals exactly `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`.

Hash pending, missing, malformed, mismatched, ambiguous-locator, Web Crypto failure, timeout, or exception all fail closed. No sparse-vector/dispatch/layout fallback can enable warnings.

Canonical provenance for the confirmed 921031 lineage:

- `tk2e_23c.8f` SHA-1 `10b8cb53a4600e3e76f471a3eee8a600e93096fc`
- `tk2e_22c.7f` SHA-1 `52c2d05279623d93b27856e6b76830796a089eae`
- historical live dispatch delta `+0x34`

## Active production rules — unchanged

Exactly two rules remain user-facing, both stateless hold-only current-level warnings:

1. `T18_5440_CYCLE_BODY7512_TM4_LEVEL_90` — A5440.
2. `T18_5424_CYCLE_BODY7520_TM4_LEVEL_90` — A5424.

For both rules, publication is based only on the exact current sample. The warning disappears on the first current nonmatch. A matching same-type replacement is valid only because that replacement independently supplies fresh current evidence; it inherits no `atMs`, age, watch/cycle state, prior target provenance, or previous/current transition state.

Target is reread live from `enemy+0x7E`; threat side is recomputed from current enemy/target X. Invalid/UNKNOWN target is silent.

## Quarantined frozen candidates — unchanged

The following remain frozen research candidates and cannot publish user-facing warnings:

- `T16_B4_DANGER_40`
- `T20_5136_B0_TO_B255_1250`
- `D867BA_3232_TM6_220`
- `D8811E_3232_TM6_135`

Reason: each depends on previous/current or watch history, while `same slot + same type` is not proven enemy continuity in the Browser contract.

## Preserved RC4 safety contract

RC5 keeps the RC4/RC3 safety behavior intact:

- exact World 921031 full SHA-256 identity gate;
- F1-F4 quarantine and only the two T18 current-level production rules;
- same-type slot reuse cannot inherit warning history;
- random session/message binding and cross-tab isolation for paired transport;
- simultaneous multi-warning HUD aggregation;
- legacy `WOFHUD.dispose()` cleanup before Alpha HUD takeover;
- accepted runtime disable/error/diag immediately invalidates old warning authority;
- ordinary no-diag stale behavior remains 1500 ms;
- later valid paired state may become authoritative again;
- live target/side recomputation and UNKNOWN silence;
- read-only game memory contract, `ramWrites=0`, no gameplay input injection;
- WebGL state snapshot/restore.

Still excluded: BODY4728/A4704-specific promotion, T23, T24, discovery/local promotion, WOF-052, and Beta features.

## Product regression

Run:

```bash
cd product/alpha
node regression.mjs
```

RC5 adds focused bootstrap/failure-injection assertions on top of the complete prior product regression. The bootstrap tests verify that evaluating the userscript preserves the original Worker constructor identity, constructs no Worker itself, creates no Blob/ObjectURL wrapper, performs no HUD fetch before detector pairing, passes original Worker URL/options through unchanged, and remains non-throwing with secure-random or BroadcastChannel failure.

The same regression continues to cover the golden SHA-256 gate, F1-F4 quarantine, the two current-level rules, same-type replacement behavior, session isolation, multi-warning HUD, runtime diagnostic invalidation, the unchanged 1500 ms ordinary stale boundary, target/side, UNKNOWN, read-only/no-input, legacy HUD cleanup, and GL restoration.

## Release boundary

RC5 is not Beta and does not solve or resume WOF-052. It does not expand attack research or coverage.

The only intended human blocker check after offline regression is the single real-Browser room-entry question above. A future safe detector transport must attach to the **actual live game Worker without replacing its construction target**; until such a transport is present, Alpha is allowed to remain warning-silent so the game itself stays usable.
