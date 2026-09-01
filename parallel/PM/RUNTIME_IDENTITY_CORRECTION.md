# WOF Browser Runtime Identity — PM Correction

Updated: 2026-09-01
Status: **version-label correction in progress; one final read-only digest binding remains**

## PM decision

Do **not** ask the owner to switch ROMs to `wofr1 / World 921002`.

The latest real-Browser ALPHAID probe, run in the same WOF Browser environment used by the project owner, rejected the assumed `wofr1 / World 921002` identity and positively matched the known other World program pair:

- `tk2e_23c.8f` SHA-1 `10b8cb53a4600e3e76f471a3eee8a600e93096fc`
- `tk2e_22c.7f` SHA-1 `52c2d05279623d93b27856e6b76830796a089eae`
- set: `wof / Warriors of Fate (World 921031)`

The same probe reported `dispatchDelta = 52`, i.e. `+0x34`.

This independently matches the historical Browser ROM reverse-engineering lineage. Commit `4e6f32865302d2ed390f129b5c66123fdf5f04d0` was explicitly created to **Accept live ROM uniform +0x34 delta and cache location**. The historical Browser tooling therefore observed the same live-ROM displacement characteristic as the current cryptographic probe.

## Interpretation

The strongest current explanation is:

1. the project owner's Browser runtime has been `wof / World 921031` during the Browser research lineage;
2. the old project prose labeling that runtime as `wofr1 / World 921002` was an unverified/version-name assumption;
3. the Browser prospective / production-shadow rule evidence should not be discarded merely because that old label was wrong;
4. Alpha must bind to the **actual cryptographically observed Browser program identity**, not force the owner's runtime to match the stale prose label.

This does not prove that every historical Browser session was cryptographically identical, because old captures did not retain full ROM digests. However, the exact recurring `+0x34` live-ROM characteristic plus the current exact canonical 921031 half-ROM SHA-1 match is strong continuity evidence and is materially stronger than the prior unsupported 921002 label.

## RC2 identity direction

The RC2 implementation must not hard-code or advertise `wofr1 / World 921002` as the supported Browser build unless later cryptographic evidence establishes that separately.

For the current Alpha lineage, the intended positive build identity is provisionally:

```text
MAME set: wof
Description: Warriors of Fate (World 921031)
maincpu halves:
  10b8cb53a4600e3e76f471a3eee8a600e93096fc
  52c2d05279623d93b27856e6b76830796a089eae
```

The final production primitive remains a full 1 MiB CPU-logical SHA-256, computed read-only from the live Browser heap after the two canonical 921031 half-ROM hashes are matched exactly.

## One remaining owner action

Run `parallel/PM/wof_runtime_identity_921031_probe.js` once in the live `gstyphoon.js` Worker using the one-line GitHub loader supplied by PM.

Required success:

- canonical 921031 half SHA-1 pair exact match;
- readOnly = true;
- ramWrites = 0;
- full CPU-logical SHA-256 repeated twice and equal;
- stable = true.

After that SHA-256 is captured, PM can route the exact golden digest into RC2 and close the version-identity evidence gap.

## Product consequence

Until RC2 is updated and independently re-QA'd:

- RC1 remains blocked;
- do not run final Alpha acceptance;
- do not change ROMs for the sake of the stale 921002 label;
- keep all unsupported/uncertain runtime behavior fail-closed.
