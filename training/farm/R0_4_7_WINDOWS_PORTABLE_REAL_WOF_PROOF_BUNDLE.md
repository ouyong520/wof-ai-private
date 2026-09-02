# Training Farm R0.4.7 — Windows Portable Real-WOF Proof Bundle V1

This stage packages the current strict Training Farm real-WOF proof path into a deterministic, ROM-free Windows portable ZIP. It is packaging/UX only: `realWofProof=false`, R0.2/R0.4 real proof remains Owner-local, and R0.5 remains locked.

## Portable closure

The builder uses a narrow allowlist: the current Stable-Retro/FBNeo adapter, R0.2 determinism runtime/schema/actions, the R0.2 proof-shape validator consumed by the Owner runner, R0.4 fork runtime/schemas/real smoke plan, strict Owner runner, beginner ROM picker, R0.4.6 one-click bootstrap, exact dependency pin, Owner ROM metadata reference, and the R0.4.7 package verifier/schema. It excludes Alpha/Collector/PM history, tests, `.git`, venvs, caches, evidence, runtime data, checkpoints, ROM/BIOS/game assets, and unrelated Training Farm modules.

Every selected repository file is checked against an exact Git blob SHA-1 before packaging. The package manifest records byte size, SHA-256 and Git blob identity for each source member. Package members are sorted, use `/`, fixed DOS epoch timestamps, and `ZIP_STORED`, so the same frozen source candidate produces the same ZIP bytes.

## Owner flow

1. Download the immutable R0.4.7 ZIP and its sidecar manifest.
2. Extract it to a normal local path such as `F:\三国\三国10训`; Chinese characters, spaces and parentheses are supported.
3. Optionally double-click `验证便携包.cmd` for a ROM-free integrity check.
4. Double-click `开始三国10训实机验证.cmd` (ASCII fallback: `START_WOF_PROOF.cmd`).
5. R0.4.6 discovers Python 3.10..3.14, creates/reuses the dedicated sibling `.venv`, installs exactly `stable-retro==0.9.8`, runs its ROM-free dependency/capability checks, then delegates to the existing beginner launcher and strict Owner runner.
6. Select only the legally held local WOF ZIP. The immutable bundle never contains or downloads it.
7. Evidence is written outside the immutable payload under the sibling `三国10训-data\evidence` root unless explicitly overridden.

Only the existing strict runner may produce authoritative R0.2 `REAL_WOF` and R0.4 `REAL_WOF_FORK` PASS. The portable package itself is never proof.

## Builder / verifier

Build from a frozen Git checkout:

```text
python -m training.farm.windows_portable_real_wof_bundle build --source-candidate <40-hex-current-candidate> --output <zip> --sidecar <sidecar-json>
```

Verify ZIP:

```text
python -m training.farm.windows_portable_real_wof_bundle verify-zip <zip> --source-candidate <candidate>
```

Verify extracted tree:

```text
python -m training.farm.windows_portable_real_wof_bundle verify-extracted <bundle-root> --source-candidate <candidate>
```

The shipped verifier performs the same ROM-free file-set/hash/path checks without needing the source repository.

## Fail-closed checks

The builder/verifier rejects source-blob drift, missing/extra/tampered members, duplicate or Windows-case-colliding members, path traversal, absolute/drive/UNC-like paths, unsafe separators, symlinks in the immutable extracted tree, non-deterministic ZIP timestamps/compression, forbidden local-state directories, and ROM/archive/game-like payload suffixes.
