# Local WinKawaks ROM Identity — Evidence

Updated: 2026-09-01

## 1. Canonical Browser identity

Current Browser production lineage is positively bound by the accepted PM runtime-identity probe to:

```text
set: wof
description: Warriors of Fate (World 921031)
romBytes: 1048576

maincpu half SHA-1:
  10b8cb53a4600e3e76f471a3eee8a600e93096fc
  52c2d05279623d93b27856e6b76830796a089eae

full CPU-logical SHA-256:
  5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62
```

The Browser probe also explicitly reports:

```text
world921031Match = true
old921002Match   = false
stable           = true
readOnly         = true
ramWrites        = 0
```

Sources:
- `parallel/PM/BROWSER_IDENTITY_921031_EVIDENCE.md`
- `parallel/PM/wof_runtime_identity_921031_probe.js`

## 2. Canonical World 921002 identity already retained in project code

The PM Browser identity probe retains the old World 921002 canonical pair for negative discrimination:

```text
set: wofr1
description: Warriors of Fate (World 921002)

maincpu:
  tk2e_23b.8f
    SHA-1 19e09ad6f9edc7997b030cddfe1d9c96d88135f2
  tk2e_22b.7f
    SHA-1 9fb8ae06856fe115addfb6794c28978a4f6716ec
```

This is materially different from the Browser World 921031 pair:

```text
  tk2e_23c.8f
    SHA-1 10b8cb53a4600e3e76f471a3eee8a600e93096fc
  tk2e_22c.7f
    SHA-1 52c2d05279623d93b27856e6b76830796a089eae
```

Therefore a positive match to the 23b/22b pair proves a different main-program revision from Browser.

## 3. Strongest retained local runtime identity evidence

`ouyong520/wof-winkawaks-bridge/results/i1_runtime_compatibility_latest.json` was captured read-only on:

```text
2026-08-31T10:43:06.692468+00:00
```

It records:

```text
pid:     24508
exeName: WinKawaks.exe
windowTitles:
  Kawaks 1.59 - 暂停 - Warriors of Fate (World 921002)
  MSCTFIME UI
  Default IME
```

The same result passed its read-only runtime checks:

```text
i1Pass: true
readOnly: true
writesGameMemory: false
freshDiscovery.candidateUnique: true
```

Why this matters:

- the title came directly from windows owned by the exact WinKawaks PID;
- the probe did not derive that title from RAM fields;
- the string identifies the emulator's active WOF driver description as `World 921002`;
- this is substantially stronger than any old prose label or offset-based guess.

## 4. Why the title is not the final cryptographic proof

The retained title can identify what WinKawaks says it loaded, but it cannot by itself exclude all of the following edge cases:

- a locally modified/patched ROM stored under the expected set name;
- renamed ROM contents accepted by an old emulator build;
- a noncanonical archive whose internal program bytes do not match the canonical revision.

For strict program-revision identity, the actual local program ROM bytes must be hashed.

## 5. What Collector already retains — and what it does not

`bridge/collector_platform.py` stores a session header containing fields such as:

```text
pid
exeName
ramBase
mapping
freshDiscoveryMethod
```

It does **not** store:

```text
loaded set name
ROM archive path
ROM member filenames
ROM CRC/SHA-1/SHA-256
main-program digest
```

The existing BASECAP raw corpus therefore cannot be upgraded into a cryptographic ROM identity proof without one local file-hash operation.

## 6. Existing bridge capabilities supporting a minimal probe

The bridge already contains read-only Windows runtime primitives:

- `bridge/process.py`
  - finds `WinKawaks.exe`, `WinKawaks64.exe`, or `Kawaks.exe`;
  - can enumerate modules and obtain the main executable path.
- `bridge/memory.py`
  - opens the target process with `PROCESS_QUERY_INFORMATION | PROCESS_VM_READ` only;
  - deliberately exposes no write operation.
- `bridge/i1_runtime_compatibility_probe.py`
  - already proved that the exact WinKawaks PID and its window titles can be captured without game writes.

No new gameplay collection is needed.

## 7. Evidence ranking

| Evidence | Result | Strength for exact ROM revision |
| --- | --- | --- |
| old project prose calling local/browser `wofr1` | historical only | weak / superseded for Browser |
| local RAM layout / offsets | local differs from Browser | not valid for ROM identity |
| local WinKawaks PID window title | `World 921002` | strong direct emulator metadata |
| local program ROM cryptographic hashes | not retained yet | decisive |
| Browser program hashes | exact `World 921031` | decisive |

## 8. Exhaustion conclusion

GitHub/Collector/bridge retained evidence has been exhausted sufficiently for this bounded audit.

There is no retained local program digest to compare with the canonical pairs. The only remaining information needed is a read-only hash of the local WOF program ROM files. That is implemented as a single command in `MINIMAL_PROBE.md`.
