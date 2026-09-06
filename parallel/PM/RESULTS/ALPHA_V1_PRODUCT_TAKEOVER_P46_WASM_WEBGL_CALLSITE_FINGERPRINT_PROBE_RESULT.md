# Alpha V1 P46 — WASM / WebGL Call-Site Fingerprint Probe — RESULT

State: **COMPLETE**

Tested commit: `210efdda5bbf3715989c751eb90442f26f42d0a9`

Tested tree: `98b81df25e3c32eb7d5fdde612f020a16ad4fea6`

## Verdict

P46 now provides an exact-byte-tested, bounded, read-only diagnostic probe at the actual WebGL draw/buffer/vertex-attrib boundary. It records raw JavaScript stacks, deterministic normalized call-site fingerprints, browser-exposed WASM frame details, observed JS caller identity, exact `Module` / `Module.asm` object identity, draw/event sequence, exact authority binding, and exact object/state associations between buffer/setup events and later draws.

This is **correlation / call-site mapping evidence only**. P40 remains blocked by `NATIVE_PLAYER_MARKER_DISPLAYED_SUBMIT_SOURCE_EXPORT_NOT_PRESENT`.

## Implemented surfaces

- `parallel/RENDER_AUTHORITY_V2/wasm_webgl_callsite_fingerprint_probe.js`
- `parallel/RENDER_AUTHORITY_V2/test_wasm_webgl_callsite_fingerprint_probe.mjs`
- `parallel/RENDER_AUTHORITY_V2/WASM_WEBGL_CALLSITE_FINGERPRINT_PROBE.md`

The runtime API is exposed only as the diagnostic helper `WOFWasmWebGLCallsiteFingerprintProbeP46`.

## Captured evidence

At successful `drawArrays`, `drawElements`, buffer upload/bind, and vertex-attrib setup calls, P46 can capture:

- bounded raw stack text;
- normalized non-probe stack frames;
- deterministic FNV1A64 call-site fingerprint bound to the exact WebGL boundary method;
- exact `wasm-function[N]`, explicit WASM function name, and explicit hexadecimal offset when the browser stack actually exposes them;
- explicit `NOT_AVAILABLE` when no WASM frame is exposed;
- explicit `UNRESOLVED` when a WASM frame exists but an index/name/offset is not exposed;
- observed JS caller frame/function identity while leaving wrapper/import semantic role `UNRESOLVED`;
- exact `Module` / `Module.asm` object identity and relationship;
- monotonic event sequence and draw submission sequence;
- exact `runtimeEpoch` / `rendererEpoch` / `authorityKey` binding;
- exact buffer-object and vertex-attrib-state associations to later draw calls.

## Exact association rule

Buffer/setup evidence is never matched by nearest, timing, or list order.

A later draw may carry upload/setup evidence only when there is an exact buffer object identity match or an exact vertex-attrib index + buffer object state transition match. All matching evidence is preserved; P46 never selects a semantic winner.

## Fail-closed behavior

P46 rejects mixed evidence when:

- `runtimeEpoch`, `rendererEpoch`, or `authorityKey` changes under a supplied binding provider;
- `Module` or `Module.asm` object identity changes during the capture.

The respective terminal reasons are:

- `STALE_OR_MIXED_AUTHORITY_BINDING`
- `MODULE_OR_ASM_IDENTITY_CHANGED`

Capture is bounded by explicit wall/event/draw/buffer/attrib/stack limits. Teardown restores only P46-owned wrappers and records external wrapper replacement conflicts rather than overwriting them.

## Exact-byte self-check

Durable candidate blobs:

- probe JS: `efd71e25e28f171e080774eb5aa1309a0d7bbe2b`
- focused test: `990b4e7c0419d568ee645828f8791f985e773bc0`
- contract doc: `fcfa5f9dc6898d40f83b62a34922f0769dac1311`

Fresh Git readback matched the local bytes used for the terminal-significant checks.

Results:

- `node --check` on exact probe bytes: **PASS**
- deterministic focused self-check: **7/7 PASS**
- durable candidate/blob readback: **PASS**
- real WOF live diagnostic: **NOT RUN** — explicitly outside P46 Worker authority

The focused self-check covers browser-exposed WASM facts, `NOT_AVAILABLE`, `UNRESOLVED`, deterministic fingerprints, exact object/state association, stale binding rejection, Module/asm identity rejection, bounds, teardown, and proof-boundary non-impersonation.

## Authority boundary

P46 does **not** create or modify:

- `__WOF_NATIVE_MARKER_RENDERER_SUBMIT_SOURCE_V1__`
- `WOFNativeMarkerRendererSubmitSourceV1`
- `rendererSourceProof`
- P29 PASS
- P32 qualification
- P36 authority criteria
- P39 tracker/HUD semantics
- P42 correlation semantics
- P43 harness
- P45 staging integration
- promotion / alpha-live

It also does not use screenshot, OCR, template, nearest-only, timing-only, order-only, guessed WASM symbol, or guessed WASM offset evidence.

## Next action

PM may consume exact tested commit `210efdda5bbf3715989c751eb90442f26f42d0a9` in a later authorized diagnostic integration. A real bounded run may then reveal which call-site fingerprints and browser-exposed WASM frames actually correlate with the native marker draws. That future runtime evidence, not P46 alone, decides whether a truthful source-mapping successor is justified.
