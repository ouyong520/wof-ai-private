# P42 GStyphoon Renderer Submit Correlation Probe

Schema: `wof-gstyphoon-renderer-correlation-probe-v1`

Purpose: provide one bounded, zero-click, read-only diagnostic capture that preserves enough exact WebGL/gstyphoon submission context for a later live mapping pass. This is mapping evidence only. It is not native-marker renderer authority and cannot satisfy P29/P32/P36 by itself.

## Runtime API

Load `gstyphoon_renderer_submit_correlation_probe.js`, then create one one-shot probe:

```js
const probe = WOFGStyphoonRendererCorrelationProbeP42.createProbe({
  root: window,
  gl: window.I_fdC8Q,
  bindingProvider: () => currentExactBinding,
  baselineProvider: now => window.WOFALPHAAUTOBASELINEHUD?.status?.(now) || null,
});
probe.start({ runtimeEpoch, rendererEpoch, authorityKey });
```

The later bounded harness should serialize `probe.result()` after the event/time bound seals, or call `probe.stop(reason)` during deterministic teardown. No Owner click, avatar selection, manual seed, RAM write, input injection, promotion, or alpha-live movement is part of this probe.

## Captured facts

For each observed `drawArrays` / `drawElements` submission the bundle records:

- exact method arguments and monotonic submission sequence;
- rAF-derived or explicitly supplied frame sequence/identity without guessing an unavailable frame id;
- current program object identity, attached shader types, raw shader source when within the bound, and bounded source hash coverage;
- current ARRAY/ELEMENT buffer identity and observable size;
- enabled vertex-attrib descriptors including buffer, size/type/normalized/stride/offset/divisor;
- observed indexed buffer-range/base bindings with exact index/offset/size from the real calls;
- viewport, scissor box, and scissor enable state;
- active texture plus texture units observed at install/through real `activeTexture` + `bindTexture` calls. The bundle explicitly says semantic texture-bank identity is unavailable rather than guessing it.

The probe also wraps existing `bufferData`, `bufferSubData`, `texImage2D`, and `texSubImage2D` calls only to observe the arguments already supplied by the runtime. For typed-array / ArrayBuffer payloads it preserves source type, byte/element offset, element length, total bytes, bounded raw hex (full or head/tail), and FNV-1a-64 hash coverage. Hashes are diagnostic fingerprints, not cryptographic authority; incomplete hash coverage is labeled `complete=false`.

## P37/P39 correlation boundary

P39 status may be sampled only when its classification is exactly `UNVERIFIED_AUTO_BASELINE`, its authority flags remain false, and it does not claim renderer proof. Fresh unambiguous P1/P2/P3 native x/y values are copied into each submission as diagnostic correlation metadata. Ambiguous/stale/boundary-violating baseline input is preserved as a rejected diagnostic correlation reason.

No renderer submission is selected by nearest distance, time, list order, pixels, screenshot, OCR, template, guessed offset, or any other heuristic. `submissionGroups` are deterministic exact-state fingerprints sorted only for stable serialization. `mappingAssessment.selectionMade` is always false and `authorityEligible` is always false.

## Binding and teardown

`start()` requires exact `runtimeEpoch`, `rendererEpoch`, and `authorityKey`. When a `bindingProvider` is supplied, every observed draw/upload hook re-reads the current binding and terminally rejects `STALE_OR_MIXED_AUTHORITY_BINDING` before recording mixed-epoch evidence.

Capture is bounded by wall time, submission count, buffer-upload count, texture-upload count, raw-payload bytes, shader-source bytes, vertex-attrib count, and observed texture-unit count. Teardown restores every wrapped WebGL/rAF method only if that exact wrapper is still installed; any third-party replacement is reported as a teardown conflict rather than overwritten.

## Authority boundary

P42 intentionally does not create either P36 native-marker source export, does not emit renderer authority proof, does not modify the P36 observer/producer, does not alter P29/P32 acceptance semantics, and does not upgrade P37/P39 coordinates into production coordinates. A later live diagnostic may use this raw bundle to identify a truthful exact source path; until then the P40 blocker remains unresolved.
