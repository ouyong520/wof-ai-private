# ALPHAID — Browser Runtime Identity Audit

Date: 2026-09-01
Status: **STOP B — one minimal real-Browser proof required**
Scope: WOF Alpha RC2 runtime/build identity only
Write boundary: `parallel/ALPHAID/**` only
Product boundary: `product/alpha/**` was read-only and was not modified by this audit

## Verdict

The current Alpha identity gate is not a build identity gate. It proves only that a Browser worker exposes the expected emulator module/RAM shape and that the three player self-index bytes are `0/4/8`. A structurally compatible unknown WOF build can therefore pass.

The safest positive identity available from the current Browser architecture is **content identity of the complete 1 MiB Motorola 68000 program ROM region**, not RAM layout, a label, a reset vector, a few semantic addresses, or a ROM filename.

Existing Browser reverse-engineering already proves that the live WASM heap can locate/read that 1 MiB program region safely. The existing ROM-focus locator recognizes the 68000 vector and validates the type-dispatch area, while tolerating the live byte-pair representation used by the emulator. Those anchors are useful to locate the region, but they are not sufficient as the final identity predicate.

External emulator metadata identifies the supported set as:

- MAME machine: `wofr1`
- Description: `Warriors of Fate (World 921002)`
- `maincpu` ROM 0x000000..0x07ffff: `tk2e_23b.8f`, SHA-1 `19e09ad6f9edc7997b030cddfe1d9c96d88135f2`, CRC32 `11fb2ed1`
- `maincpu` ROM 0x080000..0x0fffff: `tk2e_22b.7f`, SHA-1 `9fb8ae06856fe115addfb6794c28978a4f6716ec`, CRC32 `479b3f24`

The later World parent `wof / World 921031` uses different main-program ROMs (`tk2e_23c.8f` / `tk2e_22c.7f`), so program-content identity distinguishes at least the directly relevant World revisions and, by exact digest equality, fails closed for unknown/lookalike program images.

## Why this audit stops at B, not A

The repository does **not** currently retain a Browser capture that binds the live program bytes to the canonical `wofr1` ROM hashes, nor a previously recorded full-region Browser SHA-256. It would be unsafe to invent that digest or infer it only from layout/semantic addresses.

Therefore exactly one owner Browser action remains: run the read-only probe in `MINIMAL_BROWSER_PROBE.md` in a known-good supported `wofr1 / World 921002` game worker. The probe:

1. locates the same live 1 MiB 68000 ROM region already used by prior Browser ROM research;
2. hashes each 512 KiB half in both possible byte-pair orientations;
3. requires one orientation to match **both** canonical `wofr1` SHA-1 values;
4. computes the full CPU-logical 1 MiB SHA-256 twice and requires stability;
5. performs no RAM writes and no game control.

Once that single result exists, the full CPU-logical SHA-256 is the recommended RC2 positive guard value.

## Files

- `IDENTITY_AUDIT.md` — evidence, rejected alternatives, canonical binding, stop decision
- `RECOMMENDED_GUARD.md` — implementation contract and positive/negative fixtures for the Alpha owner
- `MINIMAL_BROWSER_PROBE.md` — the one remaining real-Browser proof, including exact Console command and acceptance criteria

## External reference points

- MAME machine metadata for `wofr1`: https://www.arcade-museum.com/tech-center/machine/wofr1
- MAME XML-style metadata for `wofr1`: https://www.gamesdatabase.org/mame-rom/wofr1
- MAME metadata for `wof / World 921031`: https://mame.spludlow.co.uk/Machine.aspx?name=wof
- Historical MAME source note/declaration showing `ROM_LOAD16_WORD_SWAP` and the same `wofr1` hashes: https://git.redump.net/mame/commit/?h=mame0142&id=f02b5d78f2c4695d78a1bef20222072a532f15ad

Note: historical MAME source has discussed whether the dumped `wofr1` program may originate from a patched/desuicided board. That provenance question does not weaken this audit's runtime identity goal: the supported emulator set is defined here by the exact canonical `wofr1` program bytes/hashes, not by a claim about an untouched physical PCB.
