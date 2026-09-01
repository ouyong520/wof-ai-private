# Browser Identity Evidence — WOF World 921031

Date: 2026-09-01
Status: **ACCEPTED / CANONICAL FOR CURRENT BROWSER LINEAGE**
Source: project-owner live Browser Worker probe
Probe: `wof-world-921031-maincpu-binding-v1`

## Verdict

The current Browser WOF lineage used by the project is positively bound to:

```text
MAME set: wof
Description: Warriors of Fate (World 921031)
maincpu logical bytes: 0x100000
```

The previously assumed `wofr1 / World 921002` label is not the live Browser program identity for this lineage.

## Accepted read-only probe result

```json
{
  "project": "WOF-AI-PRIVATE",
  "audit": "PM-RUNTIME-IDENTITY-CORRECTION",
  "probe": "wof-world-921031-maincpu-binding-v1",
  "readOnly": true,
  "ramWrites": 0,
  "accepted": true,
  "target": {
    "set": "wof",
    "description": "Warriors of Fate (World 921031)"
  },
  "romBytes": 1048576,
  "locator": {
    "heapBase": "0xc08748",
    "pairSwap": true,
    "source": "vector-scan-swap16",
    "dispatchOffset": "0x25dc",
    "dispatchMode": "uniform-live-delta",
    "dispatchMatched": 5,
    "dispatchDelta": 52
  },
  "canonical": {
    "expectedHalfSha1": [
      "10b8cb53a4600e3e76f471a3eee8a600e93096fc",
      "52c2d05279623d93b27856e6b76830796a089eae"
    ],
    "directHalfSha1": [
      "10b8cb53a4600e3e76f471a3eee8a600e93096fc",
      "52c2d05279623d93b27856e6b76830796a089eae"
    ],
    "pairSwappedHalfSha1": [
      "97e487dd55f4af18a5914812cf378c9f6a59e02b",
      "dbfce79a2dd0d5a658639c6ec57f222e9e8b8280"
    ],
    "orientation": "heap-direct",
    "world921031Match": true,
    "old921002Match": false
  },
  "fullCpuLogicalSha256": "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62",
  "repeatCpuLogicalSha256": "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62",
  "stable": true
}
```

## Production identity contract

For the current Alpha lineage, warnings may be enabled only when all required Browser/runtime sanity checks pass **and** the normalized full 1 MiB CPU-logical main-program digest is exactly:

```text
5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62
```

Reset vectors, RAM layout, player self-index values, page/ROM labels, and the historical `+0x34` dispatch delta are locator/sanity evidence only. None may act as an alternate acceptance path.

## Negative identity boundary

The probe explicitly proved:

```text
World 921031 canonical half SHA-1 pair: MATCH
old World 921002 canonical pair:       NO MATCH
stable repeated full SHA-256:          MATCH
readOnly:                              true
ramWrites:                             0
```

Therefore Alpha documentation, runtime signature and support messaging for this Browser lineage must be corrected from `wofr1 / World 921002` to `wof / World 921031`.
