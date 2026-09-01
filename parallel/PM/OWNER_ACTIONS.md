# WOF Future Danger AI — Owner Actions

Updated: 2026-09-01 — RC2 support audits converging

## Current owner action required: YES — one read-only Browser identity probe

Three RC2 support lanes have now produced implementation-ready guidance:

1. Runtime Identity: safest release guard is a full 1 MiB CPU-logical main-program SHA-256, but one known-good Browser binding is still required before the golden digest may be embedded.
2. Enemy Lifecycle: current Browser evidence does not positively prove same-type same-slot continuity. RC2 must fail closed for history-derived warnings unless continuity is proven; current-level T18 rules can remain as hold-only current evidence.
3. Normal-user Bootstrap: recommended Alpha path is a Chrome/Chromium bootstrap extension that automatically finds the real game Worker and injects Worker + top HUD, with an end-to-end freshness/session handshake.

The Alpha RC2 implementation thread has not yet published product-code fixes at this snapshot.

## Action O1 — Run the one-shot ALPHAID probe

Use a known-good supported `wofr1 / Warriors of Fate (World 921002)` Browser session.

Open the same live game Worker DevTools Console where prior WOF Browser probes can access `_0x515056` / `HEAPU8`.

Read and paste the **entire exact command** from:

`parallel/ALPHAID/MINIMAL_BROWSER_PROBE.md`

This probe is read-only:
- no CPS RAM writes;
- no player control/input injection;
- no gameplay choreography;
- no WOF-052 collection.

Copy back the single JSON object printed by the probe.

Acceptance requires at minimum:
- `accepted == true`
- `readOnly == true`
- `ramWrites == 0`
- `canonical.wofr1Match == true`
- `fullCpuLogicalSha256 == repeatCpuLogicalSha256`
- `stable == true`

Do not use a result from another WOF revision as the golden value.

## Why this action is needed now

GitHub does not retain a canonically bound Browser SHA-256 for the supported `wofr1` program. The value cannot safely be guessed from RAM layout, sparse code anchors, published SHA-1 strings, or WinKawaks offsets.

Once the accepted probe JSON is committed under `parallel/ALPHAID/**`, RC2 can implement:

`layout sanity AND exact full-program SHA-256 match => warnings eligible; otherwise fail closed`.

## Do not do yet

- Do not run full Alpha Browser acceptance.
- Do not resume WOF-052 as part of this action.
- Do not perform broad gameplay/WinKawaks collection.
- Do not manually test RC1 as a release candidate.

## Active work while owner runs the probe

- Alpha RC2 implementation continues to close all current QA OPEN P0/P1 findings.
- Runtime Identity lane waits for the one probe result, then can seal its handoff.
- Lifecycle and Bootstrap support outputs are ready for RC2 consumption.

## Next PM trigger

After the probe prints its JSON, paste that JSON into the PM or Runtime Identity thread. PM/ALPHAID will commit the evidence and route the approved digest to RC2. Then continue until RC2 is ready for a fresh independent QA retest.
