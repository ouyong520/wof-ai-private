# GEO facing closure

Updated: 2026-09-01

Scope: WinKawaks local discovery only. Read-only. No Browser/WASM production promotion. No game-memory writes.

## Final verdict

- `player+0x47` — **CONFIRMED: current horizontal facing/orientation state**.
- `player+0x99` — **CONFIRMED: requested/queued horizontal direction state**, not the authoritative current-facing field.
- In the repeatedly observed P1/P2 conventional states, `0` corresponds to right-facing/rightward orientation and `255` corresponds to left-facing/leftward orientation.
- The complete cross-player/form value encoding is **not asserted to be globally binary**: retained static P3 evidence includes `+0x47 = 1`. Consumers must therefore treat `+0x47` as an orientation-state field whose common P1/P2 left/right encodings are known, not as a universal boolean/sign bit.

The GEO `facing` phase is **CLOSED**. The next permitted phase is `top/bottom`.

## Why `+0x47` is current facing rather than horizontal velocity

Using the already-confirmed world-X reconstruction

```text
X = 256 * U8(+0x0B) + U8(+0x04)
```

as the independent movement truth, the retained multi-capture corpus shows:

- left-moving frames: `+0x47 = 255` on 491 frames, while `+0x47 = 0` appears only 7 times;
- right-moving frames: `+0x47 = 0` on 745 frames, while `+0x47 = 255` appears only 4 times;
- many static episodes keep their prior `0` or `255` value instead of returning to zero.

The static retention directly rejects the simpler hypothesis that `+0x47` is merely horizontal velocity/delta. It behaves as persistent orientation state.

## Why `+0x99` is upstream/requested direction rather than current facing

Repeated turn episodes establish a stable temporal ordering:

```text
+0x99 switch  ->  +0x47 switch  ->  X movement
```

Typical retained timing:

- `+0x99` changes first, roughly 5–7 frames before motion;
- `+0x47` changes later, roughly 1–2 frames before X begins moving;
- then the confirmed X composite changes.

This ordering is incompatible with treating `+0x99` as the authoritative current visual orientation when `+0x47` is the field that persists into the committed facing state closer to actual motion. The narrow semantic split is therefore:

```text
+0x99 = requested / queued horizontal direction state
+0x47 = current horizontal facing / orientation state
```

## Static control and representation caveat

`GEO-0006-passive-geometry-camera-20s60-20260831-1657Z` supplies a strong static control: all three players remain geometrically static for 1200 frames while the orientation-related bytes persist rather than behave like velocity.

Observed static state includes:

- P1/P2 `+0x47 = 0`;
- P3 `+0x47 = 1`;
- all three `+0x99 = 0` in that retained episode.

Therefore a downstream decoder must not globally hard-code only `{0,255}` for every player/form. The proof locks the field role and the common P1/P2 encodings, while explicitly preserving representation-specific exceptions.

## Adjacent-width rejection

The facing semantics belong to the low bytes themselves, not to an invented aligned S16 field:

- the byte adjacent to `+0x47` has independent player-specific high-byte behavior (including P3 values unrelated to facing);
- the byte adjacent to `+0x99` also has independent state variation.

Thus neither `+0x47` nor `+0x99` should be widened merely because of address adjacency.

## Canonical BASECAP acquisition reused

No new facing capture is required. BASECAP v1 already contains the canonical timing-robust facing scene:

```text
taskId:      BASECAP-B12R-facing-delayed-30s60-20260901-0527Z
taskBlobSha: 881d8a73802a4221936bf15dbd479d2326ebedd0
rawPath:     captures/BASECAP-B12R-facing-delayed-30s60-20260901-0527Z.jsonl.gz
result:      PASS / readOnly / no game-memory writes
samples:     1800 @ ~59.997 Hz
```

Its acquisition label deliberately asks P1 to perform minimal-displacement visual left/right facing changes after a timing guard, with P2/P3 untouched and no UP/DOWN/attack/jump/camera-scroll action. This canonical acquisition is used as supporting scene evidence; field semantics remain GEO-owned and are established by the retained cross-corpus timing and movement relationship above.

The earlier timing-racy B12 run is not needed for the closure.

## Stop rule

Do not create another facing capture. BASECAP already contains the discriminating scene, and the retained corpus already distinguishes the two direction-state bytes.

Proceed only to `top/bottom`, first reusing retained animation/action, geometry, metadata, and ROM/static evidence before considering any acquisition.