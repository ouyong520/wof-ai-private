# WOF LOCAL WINKAWAKS ROM IDENTITY AUDIT — START PROMPT

You own a bounded support audit for the WOF / Warriors of Fate / 三国志II project.

Repositories:
- `ouyong520/wof-ai-private`
- `ouyong520/wof-winkawaks-bridge`

## Question

Determine exactly which WOF ROM revision/set the owner's local WinKawaks instance is running, and whether it matches the Browser production lineage.

Browser production lineage is already positively bound to:
- MAME set: `wof`
- description: `Warriors of Fate (World 921031)`
- half SHA-1 values:
  - `10b8cb53a4600e3e76f471a3eee8a600e93096fc`
  - `52c2d05279623d93b27856e6b76830796a089eae`
- full 1 MiB CPU-logical SHA-256:
  `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`

Do not use the old `wofr1 / World 921002` label unless evidence proves the local ROM actually matches it.

## Read first

Read current GitHub state:
- `parallel/PM/RUNTIME_IDENTITY_CORRECTION.md`
- `parallel/PM/WORLD_921031_BROWSER_IDENTITY_RESULT.md`
- `parallel/BASECAP/BASE_CAPTURE_CATALOG.md`
- `WINKAWAKS_SINGLE_OPERATOR_SWEEP_GUIDE.md`
- bridge Collector implementation/runtime discovery code
- any retained local ROM metadata, filenames, emulator game/set identifiers, task headers, diagnostics, or logs.

## Scope

This is a local ROM identity audit only.

Do NOT modify `product/alpha/**`.
Do NOT modify Browser production rules.
Do NOT restart broad collection.
Do NOT ask the owner to replay the game.
Do NOT infer ROM revision from RAM offsets alone.

Write only under:
- `parallel/LOCALROM/**`

## Required work

1. Exhaust retained GitHub/bridge evidence first for:
   - WinKawaks loaded game/set name;
   - ROM filenames;
   - CRC/SHA-1/SHA-256 values;
   - emulator diagnostics/logs;
   - any ROM memory/read capability already present.

2. Compare any retained identity evidence against canonical WOF sets, especially:
   - `wof / World 921031`;
   - `wofr1 / World 921002`.

3. If retained evidence cannot positively identify the local ROM, design the smallest read-only local operation needed to hash or otherwise positively identify it.

4. Prefer an automated one-command / one-script operation. Do not ask the owner to manually inspect many ROM files or calculate hashes by hand if bridge/PowerShell/Python can do it safely.

5. State explicitly whether local WinKawaks and Browser are:
   - EXACT SAME PROGRAM REVISION;
   - DIFFERENT PROGRAM REVISION;
   - or NOT YET PROVEN.

6. If different, explain impact on existing BASECAP/EFIELD/RAWMINE/SEQMINER evidence:
   - which discovery evidence remains useful;
   - what may not transfer;
   - what Browser validation remains mandatory.

## Required outputs

Create:
- `parallel/LOCALROM/README.md`
- `parallel/LOCALROM/EVIDENCE.md`
- `parallel/LOCALROM/VERDICT.md`
- `parallel/LOCALROM/MINIMAL_PROBE.md` only if a human/local operation is truly required.

## Stop condition

Stop when either:
A. local ROM identity is positively proven and compared with Browser World 921031; or
B. exactly one minimal read-only operator command is specified.

Do not ask the owner to choose technical methods. Do not broaden into gameplay research or timing analysis.