# Training Farm Owner Local ROM Reference

Status: **LOCAL-ONLY GAME ASSET — ROM BYTES MUST NOT BE COMMITTED**

This file records only metadata for the Owner-provided local WOF ROM used by Training Farm real-runtime proof. The ROM archive itself must remain outside the repository and must never be uploaded, copied, vendored, or committed.

## Owner-provided file reference

- uploaded/local filename observed by PM: `wof(2).zip`
- size: `6366259` bytes
- SHA-256: `6355d82b9457433725fe53cf1723f94eef752b569f3c07b51ac7e57be4a3cbaa`

## Intended local use

Place the Owner's legally held ROM archive somewhere outside the repository, for example:

```text
D:\ROM\wof.zip
```

Then set `WOF_ROM_PATH` to that external file and run:

```text
training\farm\run_real_wof_proof.cmd
```

The Training Farm proof runner hashes the local ROM in place for identity binding. ROM bytes must not be copied into Git results or evidence bundles.

## Repository boundary

`training/farm/.gitignore` already blocks common ROM/archive/binary forms including `*.zip`, `*.7z`, `*.chd`, `*.rom`, `*.bin`, and savestate/core-binary formats. This metadata record does not weaken that boundary.
