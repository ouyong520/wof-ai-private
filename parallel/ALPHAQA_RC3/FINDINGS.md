# WOF Alpha RC3 — Independent QA Findings

Updated: 2026-09-01
Overall: **BLOCKED**

## ALPHAQA-RC3-001 — P1 — runtime diagnostic does not immediately invalidate the last warning

### Requirement

RC3 must fail closed on stale/error/exception paths. A detector runtime exception must not leave any user warning visible from a prior state.

### Current product behavior

Worker detector (`product/alpha/wof_alpha_loader.js`):

- successful ticks post `state` messages;
- on a tick exception it sets `running=false`, calls `engine.reset()`, and posts a `diag` message;
- it does not post an immediate empty `state` after the exception.

Page HUD (`product/alpha/wof_alpha_hud.js`):

- on `state`, it sets `lastMsg` and `lastRx`;
- on `diag`, it only sets `lastDiag` and resets the paint key;
- it does **not** clear `lastMsg` or `lastRx`;
- `drawHud()` first checks whether `lastRx` is within `STALE_MS=1500` and renders warnings from `lastMsg`;
- only when no fresh warning is rendered does it check `lastDiag`.

Therefore a prior warning remains authoritative for up to 1500 ms after the detector has already disabled itself.

### Deterministic reproduction

State machine mirroring the exact message/update/render precedence:

```text
t=1000 ms  state(warnings=[T18...])
t=1001 ms  diag(reason="runtime exception")
t=1002 ms  visible = WARNING
t=2499 ms  visible = WARNING
t=2501 ms  visible = DIAGNOSTIC
```

This is not dependent on enemy lifecycle ambiguity, ROM identity ambiguity, or Browser timing. It follows directly from the current message handlers and stale timer.

### User impact

For up to 1.5 seconds after the detector has stopped and discarded its engine state, the user can still be shown an obsolete danger warning. That is a false retained alert on an explicit error path and violates RC3 fail-closed semantics.

### Severity

**P1 / release blocker.**

It does not reopen unsupported-ROM identity or manufacture a cross-episode rule, so it is not classified here as P0. It nevertheless blocks Alpha acceptance because error handling is explicitly required to clear/silence user warnings.

### Required product fix

Any equivalent implementation is acceptable provided the user-visible invariant holds immediately on `diag`. The smallest directions are:

- invalidate warning state in the HUD on `diag` (`lastMsg=null; lastRx=0`), and/or
- make a current disable diagnostic take precedence over all prior warning states.

Recommended regression:

```text
valid warning state -> runtime diag -> warningCount == 0 immediately
valid warning state -> runtime diag -> HUD renders disabled/silent state immediately
```

The independent QA line must be rerun after product engineering changes `product/alpha/**`.

---

## Passed adversarial areas before stop condition

### Identity gate — PASS (offline/source)

The positive gate requires exact equality of a normalized 1 MiB CPU-logical SHA-256 to the accepted World 921031 digest. Missing/pending/error/malformed/mismatch digests cannot make `validateIdentityProbe().ok` true. Vector/dispatch/layout signals remain additional sanity/locator checks only.

The accepted Browser identity evidence records the same stable full digest twice and explicitly records old World 921002 as nonmatching.

### Same-type slot reuse — PASS (offline/source)

The RC3 engine clears its entire current snapshot map every `step()` and has no production watch/history map. Warnings are recomputed only from the current sample against the two production T18 predicates.

Consequences:

- same slot + same type cannot inherit an old warning;
- direct same-type replacement by a nonmatching ACTIVE sample produces no warning;
- cross-episode history cannot produce a warning;
- T18 matching -> neutral clears on the first current nonmatch;
- a replacement that independently matches T18 may warn, but only as fresh current evidence.

### F1–F4 quarantine / two-rule scope — PASS (offline/source)

`RULES` contains exactly the two production T18 rules. The first four frozen candidates are `production:false` and absent from the evaluation loop. The manifest agrees and explicitly excludes BODY4728/A4704, T23, T24, WOF-052, Beta features, and provisional/local candidates.

### Session isolation — PASS (offline/source)

The userscript generates 16 cryptographically random bytes per page, incorporates the resulting session into the channel, and both loader and HUD require exact schema/session equality. Cross-session messages are ignored.

### Multi-warning HUD — PASS (offline/source)

The HUD model iterates the entire warning list, groups all rows by target/side, preserves total warning count, and marks multiplicity. It no longer truncates to the first warning.

### Legacy HUD cleanup — PASS (offline/source)

The historical canvas HUD's `dispose()` clears its callback, removes its keyboard listener, closes its BroadcastChannel and deletes its own texture/buffer/program, while leaving the persistent GL bridge. RC3 calls legacy `dispose()` and refuses takeover if it is unavailable.

### Normal-user bootstrap — PASS (offline/source; live interception not reached)

The userscript runs at `document-start`, installs the Worker wrapper, writes shared session config before Worker construction, and automatically loads the page HUD. No current RC3 user path falls back to the old two-console RC1 procedure.

### Target / side / UNKNOWN — PASS (offline/source, except error-stale blocker above)

Target and target X are reread each poll. User warning rows require selector 0/4/8 plus finite enemy/target X. Side is recomputed from current geometry. Invalid target/geometry remains silent.

### Read-only / no-input / GL restoration — PASS (offline/source, except user-visible error-clearing blocker above)

No game RAM write or automatic input injection path was found in the RC3 detector/bootstrap/HUD. HUD mutation is limited to its rendering resources and documented GL state, with snapshot/restore around upload/draw.
