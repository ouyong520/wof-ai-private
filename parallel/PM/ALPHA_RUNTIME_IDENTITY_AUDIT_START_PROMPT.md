# WOF ALPHA RUNTIME IDENTITY AUDIT — START PROMPT

You own one bounded read-only product-support investigation for the Alpha RC2 P0 identity blocker.

Repositories:
- `ouyong520/wof-ai-private`
- `ouyong520/wof-winkawaks-bridge` read-only only if provenance is useful.

Read first:
- `parallel/ALPHAQA/FINDINGS.md` — especially ALPHAQA-001
- `parallel/ALPHAQA/AUDIT_STATUS.md`
- `parallel/PM/ALPHA_RC2_FIX_START_PROMPT.md`
- current `product/alpha/**`
- Browser/WASM coordinators, loaders, probes, ROM/runtime fingerprints and prior validation history in the repository.

## Role and boundary

This is NOT attack research and NOT an implementation owner.

Your only question is:

**What is the safest positive Browser-runtime/build identity mechanism that can distinguish the declared supported WOF World 921002 / `wofr1` environment from structurally compatible unknown/lookalike layouts before Alpha warnings are enabled?**

Treat `product/alpha/**` as READ-ONLY.
Write only under `parallel/ALPHAID/**`.
Do not modify PM, QA, research lanes or product implementation.

## Work

1. Exhaust current GitHub evidence for already-known build/revision identity signals.
2. Look for Browser-visible evidence such as ROM metadata, game identifiers, loaded asset names/hashes, emulator-provided ROM set identity, immutable code/data bytes, or another positively distinguishing signature.
3. Separate evidence classes:
   - proven positive supported-build identifier;
   - strong but not unique layout fingerprint;
   - unsupported guess / unsafe inference.
4. Do not copy WinKawaks numeric addresses or local offsets into Browser/WASM identity logic.
5. If a candidate uses Browser memory bytes, establish why those bytes are stable for the supported build and why a lookalike revision is expected to differ; do not fabricate certainty.
6. Define exact positive and negative regression fixtures the RC2 implementation should add.
7. If retained evidence cannot safely prove a build identifier, specify the smallest real-Browser owner probe needed to acquire one, with exact output to record, and explain why it is necessary.

## Outputs

Maintain under `parallel/ALPHAID/**`:
- `README.md`
- `IDENTITY_AUDIT.md`
- `RECOMMENDED_GUARD.md`
- `MINIMAL_BROWSER_PROBE.md` only if human evidence is truly required.

The recommendation must be implementation-ready for the RC2 fix owner and explicitly state confidence/limitations.

## Stop condition

Stop when either:

A. one safe positive supported-build identity mechanism is identified from retained evidence, with implementation-ready checks and negative-lookalike test requirements; or

B. retained evidence is insufficient, and exactly one minimal Browser probe is defined that would close the identity gap without broad gameplay or collection.

Do not ask the owner to choose technical alternatives. Do not start attack discovery or broad collection.