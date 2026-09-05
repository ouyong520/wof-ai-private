# P36 Native Marker Renderer Submit Source Trace

Status: implementation contract only. This module **does not claim that a real WOF marker has passed live authority**.

## Scope

P36 closes the repo-side producer gap between an exact displayed CPS1 renderer submit source and the existing P32 fail-closed qualifier.

The checked-in W3 capture remains structural. It is not promoted. Screenshot/OCR/template/world-projection/nearest-object/list-order/timing evidence is not accepted as marker authority.

The checked-in repository does not contain the running gstyphoon WASM or a proven exported native renderer pointer. Therefore offline code cannot truthfully assert that a particular browser/WASM address is the displayed CPS1 object submit hook. P36 instead provides a bounded live observer that auto-attaches **only** when the runtime exposes one exact source-traced renderer-submit surface. Absence or ambiguity preserves:

`NATIVE_PLAYER_MARKER_DIRECT_RENDERER_CAUSAL_EDGE_NOT_CHECKED_IN`

No Owner click, player selection, or manual seed is part of the producer contract.

## Files

- `native_marker_renderer_submit_source_trace_worker.js`
  - bounded read-only observer for an exact direct renderer-submit source;
  - auto-discovers only explicit P36 source surfaces on `self`, `Module`, or `Module.asm`;
  - rejects multiple distinct qualifying surfaces;
  - rejects stale/mixed runtimeEpoch / rendererEpoch / authorityKey;
  - records at most 96 events and at most 15 seconds;
  - never reads HEAP to infer authority and never injects input or writes game RAM.

- `native_marker_renderer_submit_source_trace.py`
  - validates the source and exact submit events;
  - selects events only by explicit `(player, generation)` association;
  - deterministically orders already-associated samples by explicit renderer `frameGeneration`; arrival order is not an identity signal;
  - emits the existing `wof-native-player-marker-direct-evidence-v1` contract;
  - immediately calls `qualify_native_player_marker(...)` from P32 without changing P32 rules.

## Exact live source surface

The observer looks for exactly one qualifying object under one of these names:

- `self.__WOF_NATIVE_MARKER_RENDERER_SUBMIT_SOURCE_V1__`
- `self.WOFNativeMarkerRendererSubmitSourceV1`
- the same names on `self.Module`
- the same names on `self.Module.asm`

The object must have schema:

`wof-native-marker-renderer-submit-source-v1`

and must truthfully declare:

- `derivationKind`: one of `SOURCE_TRACED_POINTER`, `DIRECT_RENDER_HOOK`, `EXPORTED_RENDERER_POINTER`;
- `guessed: false`;
- `displayedFrameCausalLink: true`;
- `coordinateAuthority: NATIVE_RENDERER_OBJECT_384X224`;
- all screenshot/OCR/template/world-projection coordinate flags false;
- a non-empty exact `sourceTrace`, `instrumentationId`, and `hookSite`;
- `readOnly: true`, `ramWrites: 0`, `inputInjection: false`;
- `ownerSelectionRequired: false`, `manualSeedRequired: false`;
- `subscribe(observer, binding)`.

A source object is not authority merely because it uses the expected property name. The producer validates the full declaration, and the later live run must still establish that the source descriptor is attached to the actual displayed renderer submit path.

## Direct submit event

Each observer callback must be one exact:

`wof-native-marker-renderer-submit-event-v1`

with:

- exact `runtimeEpoch`, `rendererEpoch`, `authorityKey`;
- monotonic renderer `frameGeneration`;
- unique `displayedFrameId` and `submissionId`;
- `displayedFrameCausalLink: true`;
- `coordinateAuthority: NATIVE_RENDERER_OBJECT_384X224`;
- `guessed: false`;
- explicit, generation-bound, unambiguous P1/P2/P3 `actorAssociation`;
- exact one-object or deterministic multi-object `marker` cluster in the same shape P32 already validates.

The marker's downward-arrow native `x/y` is validated by P32 against 384x224. P36 does not derive it from a screenshot or world projection.

## Fail-closed behavior

The producer never falls back to structural HEAP, image evidence, nearest object, row/list order, wall-clock timing, or guessed offsets.

- no exact source surface -> BLOCKED with the original P32 blocker;
- multiple exact source surfaces -> BLOCKED;
- stale/mixed authority -> REJECTED;
- ambiguous actor association -> REJECTED;
- visual-only/structural-only source -> BLOCKED;
- malformed/out-of-bounds marker evidence -> existing P32 qualifier rejects it;
- fewer than three exact direct displayed-frame samples -> BLOCKED.

Wall-clock and event-count limits bound resource use only. They are not evidence and never select marker identity.

## Zero-click boundary

`start(binding)` performs source discovery automatically. The Owner is not asked to click an avatar, choose P1/P2/P3, pick a sprite, or paste a seed. The later bounded live verification only starts the existing acceptance flow and observes whether the exact source surface is truly present.

## Source-trace note

FBNeo CPS1 source architecture documents `CpsObjGet()` buffering active CPS1 objects and `Cps1ObjDraw()` converting native object x/y before per-tile draw submission. That architecture explains why the direct renderer submit edge is materially stronger than a HEAP snapshot. It is **not** used here as proof that the current gstyphoon WASM exports those symbols or that any guessed WASM address is authoritative.

P36 therefore deliberately refuses to synthesize an export/pointer that is not present in checked-in/runtime evidence.
