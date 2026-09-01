# WOF Local WinKawaks ROM Identity Audit

Updated: 2026-09-01
Status: **STOP CONDITION B — one minimal read-only local probe remains**
Scope: local WinKawaks ROM identity only

## Question

Determine exactly which WOF program revision the owner's local WinKawaks instance is running, then compare it with the Browser production lineage.

Browser production lineage is already cryptographically bound to:

```text
MAME set: wof
Description: Warriors of Fate (World 921031)
maincpu halves:
  tk2e_23c.8f  SHA-1 10b8cb53a4600e3e76f471a3eee8a600e93096fc
  tk2e_22c.7f  SHA-1 52c2d05279623d93b27856e6b76830796a089eae
full normalized 1 MiB CPU-logical SHA-256:
  5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62
```

## Current audit state

Retained local evidence is strong but not yet cryptographic:

```text
process: WinKawaks.exe
emulator: Kawaks 1.59
retained live title:
  Kawaks 1.59 - 暂停 - Warriors of Fate (World 921002)
```

That title was captured by the read-only local runtime compatibility probe on 2026-08-31 while it was attached to the same WinKawaks process used for WOF research.

Canonical World 921002 program identity used by the project is:

```text
MAME set: wofr1
Description: Warriors of Fate (World 921002)
maincpu halves:
  tk2e_23b.8f  SHA-1 19e09ad6f9edc7997b030cddfe1d9c96d88135f2
  tk2e_22b.7f  SHA-1 9fb8ae06856fe115addfb6794c28978a4f6716ec
```

Therefore the retained evidence strongly predicts that local WinKawaks is **World 921002 / wofr1**, which would be a **DIFFERENT PROGRAM REVISION** from Browser World 921031.

However, the retained Collector/raw corpus does not contain a ROM file digest or a cryptographic digest of the loaded 68000 program. The current strict classification is therefore:

```text
NOT YET PROVEN
```

The remaining gap is exactly one read-only local command documented in `MINIMAL_PROBE.md`. It does not require gameplay, replay, new BASECAP, or memory writes.

## Files

- `EVIDENCE.md` — retained evidence and what it proves
- `VERDICT.md` — strict comparison and transfer consequences
- `MINIMAL_PROBE.md` — the only remaining owner/local action
- `local_rom_identity_probe.ps1` — read-only implementation used by that one command

## Guardrails respected

- no changes under `product/alpha/**`
- no Browser production-rule changes
- no broad recollection
- no inference of ROM revision from RAM offsets alone
- local probe is read-only and hashes ROM files only
