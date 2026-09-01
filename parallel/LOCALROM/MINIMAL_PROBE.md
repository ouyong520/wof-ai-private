# Minimal Local ROM Identity Probe

Updated: 2026-09-01
Purpose: close the only remaining cryptographic identity gap

## Preconditions

- WinKawaks is running with WOF loaded.
- The game may remain paused; no gameplay is required.
- Run from the local `ouyong520/wof-ai-private` checkout after normal sync.

## The only operator command

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\parallel\LOCALROM\local_rom_identity_probe.ps1
```

Do not run any BASECAP/Collector gameplay task for this audit.

## What the command does

Read-only only:

1. finds the running WinKawaks process;
2. reads its executable path and live window title;
3. checks the normal WinKawaks ROM locations adjacent to the executable;
4. opens candidate WOF ZIP archives read-only;
5. SHA-1 hashes only the four known World 921031 / World 921002 main-program filenames if present;
6. compares them with the canonical program pairs;
7. prints one JSON verdict.

It does not:

- write WinKawaks memory;
- send game input;
- modify ROM files;
- change emulator settings;
- start a Collector task;
- require replay or any new gameplay capture.

## Expected decisive result

Given the retained live title, the expected JSON is equivalent to:

```text
process.windowTitle contains: World 921002
loadedSet: wofr1
canonicalSetMatches[wofr1].canonicalProgramPairMatch: true
verdict: DIFFERENT PROGRAM REVISION
```

If instead the exact 921031 pair is found as the loaded program, the verdict becomes:

```text
EXACT SAME PROGRAM REVISION
```

Any title/hash contradiction or missing canonical pair remains fail-closed as:

```text
NOT YET PROVEN
```

## What to return

Return the single JSON block printed by the command. No screenshots, gameplay description, ROM browsing, or additional collection are needed.
