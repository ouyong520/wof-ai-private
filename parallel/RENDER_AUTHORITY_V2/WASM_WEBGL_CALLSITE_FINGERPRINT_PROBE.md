# P46 WASM / WebGL Call-Site Fingerprint Probe

Status: **diagnostic mapping evidence only**. This probe does not solve P40 and must never be treated as native renderer authority.

## Purpose

`wasm_webgl_callsite_fingerprint_probe.js` instruments the actual page WebGL boundary around:

- `drawArrays` / `drawElements`;
- `bufferData` / `bufferSubData`;
- `bindBuffer` / `bindBufferBase` / `bindBufferRange` when present;
- `vertexAttribPointer` / `vertexAttribIPointer` / enable/disable/divisor setup when present.

Each successful wrapped WebGL call can carry a bounded raw JavaScript stack, a deterministic normalized call-site fingerprint, browser-exposed WASM frame facts, JS caller frame identity, `Module` / `Module.asm` object identity, monotonic event/draw sequence, and the exact `runtimeEpoch` / `rendererEpoch` / `authorityKey` binding supplied at start.

The emitted bundle schema is:

`wof-wasm-webgl-callsite-fingerprint-probe-v1`

## WASM truth rules

The probe preserves only facts actually present in the browser stack.

- If there is no WebAssembly frame, WASM index/name/offset fields are `NOT_AVAILABLE`.
- If a WebAssembly frame exists but a specific function index/name/offset is not exposed in parseable stack text, that field is `UNRESOLVED`.
- Exact `wasm-function[N]`, explicit function names and explicit hexadecimal offsets are preserved when present.
- No guessed function number, guessed symbol, guessed offset, source-map fabrication or inferred import role is allowed.

`jsWrapperOrImport.semanticRole` therefore remains `UNRESOLVED`; a stack frame such as `_glDrawArrays` is preserved as observed frame identity, not promoted to a proven gstyphoon semantic role.

## Fingerprint normalization

The normalized fingerprint is FNV-1a-64 over a canonical JSON form containing:

- boundary kind and exact WebGL method;
- bounded normalized non-probe stack frames;
- frame classification;
- exact exposed WASM index/name/offset fields.

The full bounded raw stack is retained separately. Probe-internal frames are removed only from the normalized fingerprint input, never from the raw captured stack.

If no usable external frame remains, fingerprint status is `NOT_AVAILABLE`; the probe does not synthesize a boundary-only fingerprint and pretend it identifies a caller.

## Exact buffer/setup association

P46 may associate upload/setup evidence with a later draw only through exact runtime object/state identity:

- uploads are keyed by the exact WebGL buffer object identity observed at the call boundary;
- draw buffer association includes only upload events for the exact bound buffer object id;
- vertex-attrib association requires exact attrib index plus the buffer object identity captured at the setup transition;
- all matching events are preserved; there is no nearest/timing/order ranking or semantic winner selection.

Every draw reports:

`exactAssociations.associationRule = EXACT_OBJECT_OR_ATTRIB_STATE_IDENTITY_ONLY`

and:

`semanticSelectionMade = false`.

## Binding / mixed-runtime rejection

Start requires non-empty:

- `runtimeEpoch`;
- `rendererEpoch`;
- `authorityKey`.

When a `bindingProvider` is supplied, any change rejects the capture as:

`STALE_OR_MIXED_AUTHORITY_BINDING`.

By default P46 also pins the exact `Module` and `Module.asm` object references seen at start. Identity drift rejects as:

`MODULE_OR_ASM_IDENTITY_CHANGED`.

No evidence after that boundary is accepted into the diagnostic bundle.

## Bounded capture and teardown

Default limits bound wall time, total events, draw submissions, buffer/attrib events, raw stack characters, stack lines and normalized frame count. Reaching a limit seals the bundle and restores installed WebGL methods.

Teardown restores a method only when that method is still P46's own wrapper. External wrapper replacement is never overwritten and is reported under `teardown.conflicts`.

When composed with another direct WebGL wrapper such as P42, orchestration should use wrapper-stack LIFO discipline: install P46 before the inner/secondary wrapper and tear the secondary wrapper down before P46. P46 itself does not modify P42 or P45 integration ownership.

## Authority boundary

The result always remains:

- `authorityEligible=false`;
- `mappingOnly=true`;
- `mappingAssessment.status=CALLSITE_CORRELATION_EVIDENCE_ONLY`;
- `mappingAssessment.selectionMade=false`;
- `semanticRendererMapping=UNRESOLVED`.

P46 does not create either native-marker source surface, does not emit `rendererSourceProof`, does not create P29 PASS, does not qualify P32, and does not change P36/P39/P42 criteria.

It also does not use screenshot, OCR, template matching, nearest candidate, timing-only, order-only or guessed WASM symbol/offset evidence.

## Focused deterministic self-check

`test_wasm_webgl_callsite_fingerprint_probe.mjs` covers:

1. raw stack + deterministic fingerprint + browser-exposed WASM index/name/offset + JS caller + Module/asm identity;
2. explicit `NOT_AVAILABLE` when no WASM frame exists;
3. explicit `UNRESOLVED` when a WASM frame exists without parseable details;
4. exact buffer-object / vertex-attrib-state association and unrelated-buffer exclusion;
5. stale authority-binding rejection with original GL calls left intact;
6. Module/asm identity drift rejection;
7. bounded sealing, deterministic teardown and proof-boundary non-impersonation.

No real WOF run is part of P46 worker acceptance. Real-runtime call-site meaning remains to be established only by a later authorized bounded diagnostic.
