# WOF Alpha QA Findings

Updated: 2026-09-01
Artifact audited: `wof-alpha-rc1`
Decision: **QA BLOCKED**

Severity convention follows `parallel/PM/ALPHA_QA_START_PROMPT.md`:

- P0 = release blocker / false-warning or unsafe fail-open risk
- P1 = Alpha blocker / major correctness or usability issue
- P2 = may remain after Alpha if explicitly accepted

---

## ALPHAQA-001 — P0 — runtime/build identity guard is layout-only and can fail open

**Status:** OPEN

**Affected:**

- `product/alpha/wof_alpha_core.js` — `validateIdentityProbe()`
- `product/alpha/wof_alpha_loader.js` — identity probe construction and warning enablement
- `product/alpha/rules_manifest.json` / `README.md` — declared supported identity

### Reproduction

The core accepts this probe:

```js
WOFAlphaCore.validateIdentityProbe({
  moduleOk: true,
  ramBase: 123,
  ramWithinHeap: true,
  selfIndexes: [0,4,8]
})
```

Current result is `ok: true` with signature:

```text
wofr1-world-921002-browser-layout-v1
```

But the input contains **no ROM/game/build/revision evidence at all**. The loader supplies exactly those structural fields: compatible HEAP, RAM base/window, and P1/P2/P3 self-index layout.

Therefore the signature is assigned after a layout check; it is not a positive recognition of `World 921002 / wofr1`.

### Impact

An unsupported WOF revision/runtime that shares the same broad layout can enter the active warning path. Its offsets/rule semantics may differ, creating unsafe false warnings or wrong target/state interpretation. This is exactly the release-blocking R3 class.

### Minimal required fix

Warnings must remain disabled until the Browser runtime positively proves the declared supported build/revision with evidence that actually distinguishes `World 921002 / wofr1` from lookalike layouts.

The fix must include a negative regression fixture representing a structurally compatible but unsupported/unknown revision and prove it stays disabled. Do not synthesize a supported-build signature from layout-only checks.

---

## ALPHAQA-002 — P1 — same-type slot replacement can inherit a prior enemy warning

**Status:** OPEN

**Affected:**

- `product/alpha/wof_alpha_core.js` — watch lifetime / `clearSlot()`
- `product/alpha/wof_alpha_loader.js` — snapshots contain no episode/replacement identity

### Reproduction

1. In slot 0, feed the T20 B0 state.
2. Feed the exact T20 B255 state; the A5136 watch arms.
3. Before the 1250 ms warning horizon expires, replace the object with a **different enemy episode of the same type 20 in the same slot**, still `attack=0`, using a neutral nonmatching state.
4. Do not insert an observed null sample or a type change between the two samples.
5. `warningRows()` continues to publish the old A5136 watch because current cleanup only recognizes `slotGone` or `typeChanged`.

This adversarial sequence is encoded in `parallel/ALPHAQA/independent_qa.mjs`.

### Why this is not a purely hypothetical lifecycle class

Existing retained EFIELD evidence explicitly contains same-type replacement boundaries. `ROUND_008_INSTANCE_METADATA.md` reports 11 same-type replacement boundaries and shows episode-stable metadata can change across them. It also states those metadata fields are not unique IDs. This proves that `same slot + same type` is not sufficient to establish enemy-instance continuity.

That WinKawaks evidence does **not** authorize copying any local offset into Browser code. It only invalidates the assumption that type equality alone proves the same episode.

### Impact

A watch created by enemy A may be rendered against enemy B, including B's live target/side. This can become a false warning and defeats the slot-reuse safety requirement.

### Minimal required fix

Add a conservative Browser-proven way to invalidate watches across enemy episode/replacement boundaries, including same-type replacement, or otherwise prove that the Browser runtime always exposes an observed gap/reset that the current 10 ms reader cannot miss.

Do not adopt WinKawaks-local instance/profile offsets directly without Browser validation.

---

## ALPHAQA-003 — P1 — HUD silently drops simultaneous warnings after the first row

**Status:** OPEN

**Affected:**

- `product/alpha/wof_alpha_hud.js`
- multi-enemy / multiplayer acceptance path

### Reproduction

The core can publish multiple warnings at once; `warningRows()` returns an ordered array. The HUD, however, selects only:

```js
lastMsg?.warnings?.[0]
```

and renders only that one warning.

A deterministic core fixture can arm the same valid T18 rule on two different slots/targets in the same poll and obtain two warning rows. The HUD exposes only the first row and gives no indication that another warning exists.

### Impact

With multiple simultaneous enemies, one player's or one side's valid danger can be silently hidden behind another active warning. This is a missed-warning/usability failure in the exact scenario the Alpha QA mandate requires testing.

### Minimal required fix

The user-facing HUD must not silently discard active warning rows. A compact aggregation is acceptable, but it must conservatively communicate all currently relevant threats/targets/sides or otherwise define and validate a product policy that cannot hide a safety-relevant warning without indication.

---

## ALPHAQA-004 — P1 — supported load path still requires researcher-level DevTools Worker operation

**Status:** OPEN

**Affected:**

- `product/alpha/README.md`
- `product/alpha/wof_alpha_loader.js`

### Reproduction

The documented RC path requires the user to:

1. open DevTools;
2. locate/select the **live `gstyphoon.js` Worker console**;
3. paste/eval the raw GitHub loader there;
4. switch back to the top page console;
5. paste/eval the same loader again.

The loader itself confirms this split by telling the top-page user to load the same code in the Worker.

### Impact

This is bounded for a researcher, but it is not yet a normal-user Alpha load path. It assumes knowledge of DevTools execution contexts and how to identify the correct live emulator worker. Wrong-context loading can leave the HUD present while detection is not active.

Repository visibility was checked: `ouyong520/wof-ai-private` is currently public, so GitHub authentication is **not** the blocker here.

### Minimal required fix

Provide one supported user bootstrap/install path that does not require manually identifying and switching to the live Worker console, or explicitly reclassify the artifact as developer/researcher-only rather than user Alpha. Reliable and minimal is sufficient; polished installation UX is not required.

---

## ALPHAQA-005 — P0 — fixed BroadcastChannel permits cross-session/cross-tab warning contamination

**Status:** OPEN

**Affected:**

- `product/alpha/wof_alpha_loader.js`
- `product/alpha/wof_alpha_hud.js`
- runtime/HUD pairing and fail-closed warning provenance

### Reproduction

Both Worker producer and top-page HUD use the same origin-global channel name:

```js
const CHANNEL='wof-alpha-v1';
const bc=new BroadcastChannel(CHANNEL);
```

The HUD accepts any same-origin message with:

```js
if(m?.schema!==CHANNEL)return;
```

and then treats `kind:'state'` as current detector state. It does not validate a per-page/per-runtime session token, Worker identity, release instance id, or a pairing nonce.

Deterministic browser reproduction:

1. Open two game pages/tabs on the same origin, A and B.
2. Install the current Alpha HUD/runtime in both.
3. Trigger a valid Alpha warning only in game B while game A is safe/quiet.
4. Because `BroadcastChannel` is origin-scoped rather than tab-scoped, A's HUD is eligible to receive B's Worker `wof-alpha-v1` state message.
5. A can therefore render B's warning, target and side as if they belonged to A. The inverse is also possible, and diagnostic/state messages from one runtime can overwrite the other HUD's most recent state.

The same fixed channel also means any other same-origin context capable of posting the accepted schema can inject an Alpha-looking warning without passing A's local runtime identity guard.

### Impact

This is a direct false-warning/fail-open provenance path. A HUD is not guaranteed to display warnings from the runtime attached to the same game page. The local identity guard therefore does not fully protect the user-facing output path.

This is P0 under the QA severity definition because a warning can be displayed for the wrong game session even when the local page itself has no valid warning.

### Minimal required fix

Bind every accepted HUD state/diagnostic message to the intended Alpha runtime/page session. A safe fix may use a per-session channel name, a cryptographically unpredictable pairing nonce/session id carried and verified in every message, or an equivalent same-page runtime binding.

Requirements:

- HUD must ignore state/diagnostic messages not belonging to its paired runtime session;
- two same-origin game tabs running Alpha simultaneously must remain isolated;
- runtime restart/reinstall must establish a clean pairing and cannot inherit another tab's producer;
- add a deterministic two-producer/two-session regression or browser fixture proving foreign-session messages are ignored;
- do not weaken stale fail-closed behavior while adding pairing.

---

## Non-blocking / pending real-Browser checks

These are not currently recorded as code defects, but still require real-Browser acceptance after the blockers above are fixed:

- WebGL HUD rendering and performance under actual game draw cadence;
- final confirmation that GL state restoration does not visibly corrupt the emulator;
- actual Browser CSP/network behavior for the supported loader path;
- short real-game retarget/scene-transition observation after lifecycle fix.

## Checks that currently passed static/evidence audit

- Six frozen rule predicates match the audited Browser sources checked through WOF-051.
- T16 remains danger-only; it is not labeled A6432-exclusive.
- T18 BODY4728/A4/B2/TM1 is absent from the production rule set as an A4704-specific predictor.
- T23/T24/discovery/local candidates are absent from the release rule engine.
- Current source contains no game RAM write path or gameplay input injection found by manual audit.
- Live `enemy+0x7E` target reread and current target-side recomputation are implemented.
- Unknown target values are silent.
- Slot disappearance and type change clear watches.
- Warning horizons expire stale watches.
- Worker runtime exceptions clear engine state and stop further warning publication.
