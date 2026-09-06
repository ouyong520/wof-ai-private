# Alpha V1 P42 — GStyphoon Renderer Submit Correlation Probe — RESULT

State: **COMPLETE**

P42 is complete as a bounded diagnostic-mapping toolchain only. Exact tested candidate `7b523187a955179b04155b758847c82aaf569a0d` provides a zero-click, read-only WebGL/gstyphoon renderer-submit correlation probe and does **not** resolve P40 blocker `NATIVE_PLAYER_MARKER_DISPLAYED_SUBMIT_SOURCE_EXPORT_NOT_PRESENT`.

## What is now captured

The probe emits schema `wof-gstyphoon-renderer-correlation-probe-v1` and preserves raw frame/submission evidence needed for a later live reverse-mapping pass:

- exact `drawArrays` / `drawElements` arguments and monotonic submission sequence;
- program identity plus attached shader type/source/hash identity;
- ARRAY/ELEMENT buffer identity and observable sizes;
- indexed buffer range/base index, offset and size where observable;
- enabled vertex attribute descriptors: buffer, size, type, normalized, stride, pointer offset and divisor;
- active texture plus texture-unit bindings observed through real calls; semantic bank identity is explicitly left unavailable rather than guessed;
- viewport, scissor box and scissor-enable state;
- rAF-derived or explicit frame sequence/identity, without inventing unavailable renderer frame IDs;
- CPU-side typed-array / ArrayBuffer payload type, source offsets/ranges, bounded raw bytes and FNV-1a-64 diagnostic fingerprint coverage for observed buffer/texture uploads;
- exact `runtimeEpoch`, `rendererEpoch`, `authorityKey` binding;
- P37/P39 P1/P2/P3 x/y only when still classified `UNVERIFIED_AUTO_BASELINE`, and only as diagnostic correlation metadata.

Every output remains `authorityEligible=false`. No submit/group is selected by nearest distance, timing, list order, pixel, screenshot, OCR, template, or guessed offset. Ambiguity remains explicit.

## Bounds and teardown

Default capture limits are bounded by wall time, submission count, buffer-upload count, texture-upload count, raw payload bytes, hash coverage, shader-source bytes, vertex-attrib count, and observed texture-unit count. Every installed wrapper forwards the original method and teardown restores only the exact wrapper it installed; third-party replacement is reported as a conflict rather than overwritten.

When a binding provider is available, every observed hook rechecks `runtimeEpoch / rendererEpoch / authorityKey`. Mixed or stale authority terminates with `STALE_OR_MIXED_AUTHORITY_BINDING` before mixed evidence is recorded.

## Exact tested candidate

- tested commit: `7b523187a955179b04155b758847c82aaf569a0d`
- tested tree: `a1333a0e90ec7e56a55565ee5298df981a92da4a`
- `parallel/RENDER_AUTHORITY_V2/gstyphoon_renderer_submit_correlation_probe.js`: `32b9c50e8a72de1a097b8ce5dc91b69bdcef0219`
- `parallel/RENDER_AUTHORITY_V2/test_gstyphoon_renderer_submit_correlation_probe.mjs`: `fd8b2eb861543cda454e16b965d75389e00dda86`
- `parallel/RENDER_AUTHORITY_V2/GSTYPHOON_RENDERER_SUBMIT_CORRELATION_PROBE.md`: `5d3fc54e0c5ceda48b1a9c0d48950d8c33b3ce14`

Fresh GitHub readback of all three candidate files matched the exact local Git blob identities used for the terminal-significant rerun.

## Focused self-check

- JavaScript syntax: **PASS**.
- Deterministic renderer-correlation suite: **6/6 PASS**.
- Durable exact-byte candidate readback: **PASS**.
- Real WOF live diagnostic: **NOT_RUN**, as explicitly required by P42 scope.

The deterministic suite covers bounded capture/teardown, exact draw/state metadata, CPU payload hash/offset/range preservation, texture/range observation, P39 diagnostic correlation, stale/mixed binding rejection, ambiguity preservation, and proof-boundary non-impersonation.

## Authority and safety boundary

P42 does not create either native-marker renderer-submit source export, does not emit renderer authority proof, does not modify P29/P32 acceptance or P36 authority semantics, does not change P37 acquisition or P39 maintained-HUD semantics, does not run the real game, and performs no RAM write, input injection, promotion, or alpha-live movement.

P40 therefore remains BLOCKED. P42 is COMPLETE because its exact-byte-tested diagnostic probe is ready to be included in one later bounded live diagnostic run; this is not a claim that the native marker renderer source has been found.

## Next action

PM should integrate this exact P42 probe with the separately authorized P43 bounded live diagnostic harness. That later run should retain the complete raw P42 bundle so a future successor can map one truthful exact native-marker displayed-submit source if the evidence supports it.
