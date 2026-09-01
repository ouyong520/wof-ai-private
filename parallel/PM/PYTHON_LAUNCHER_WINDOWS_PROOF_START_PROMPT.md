# WOF Python Launcher — Fresh Windows/Browser Live Proof

You own the next fresh stage after the completed PYLAUNCH foundation implementation.

Repository:
- `ouyong520/wof-ai-private`

Read first:
- `parallel/PM/PYTHON_LAUNCHER_FOUNDATION_START_PROMPT.md`
- `parallel/PM/PYTHON_LAUNCHER_TRAY_UI_REQUIREMENTS.md`
- `parallel/PYLAUNCH/RESULT.md`
- `parallel/PYLAUNCH/README.md`
- `parallel/PYLAUNCH/ARCHITECTURE.md`
- current `parallel/PYLAUNCH/**`

## Current authoritative state

Foundation code exists and has reached its stage stop condition. The remaining question is one real Windows/Browser proof.

The owner has separately proven that RC5 can enter a real Browser room when the game Worker is left untouched, but RC5 has no HUD/warnings because no safe live-Worker transport is paired. This PYLAUNCH proof is now the primary candidate transport path.

## Goal

Prove on the owner's Windows machine that the launcher can:
1. start or attach to its dedicated Chrome/Edge CDP profile;
2. let WOF enter a room normally;
3. discover the actual `gstyphoon*.js` Worker after normal startup;
4. locate the Emscripten/WASM module and heap;
5. verify exact `WOF / World 921031` identity using the authoritative full 1 MiB CPU-logical SHA-256;
6. keep the game playable while attached;
7. show all of this through the Windows tray/status UI;
8. remain read-only / `ramWrites=0` / no input injection.

## Owner-UX requirement

Before asking the owner to do anything, reduce the proof to the easiest safe operation practical on Windows.

Preferred owner experience:
- update local repository;
- double-click one `.cmd` / `.bat` proof launcher or run one exact command;
- enter WOF normally in the browser window opened by the launcher;
- read one compact tray/status result.

If the current foundation command is already the shortest reliable path, keep it. Otherwise you may add proof-only helper files under `parallel/PYLAUNCH/**` to reduce setup friction.

If proof fails, expose/export one compact diagnostics JSON. Do not require DevTools, Worker console selection, pasted JavaScript, frame counting, or gameplay capture.

## Hard boundaries

- do not modify `product/alpha/**`;
- do not modify WOF-052/WOF-052L tooling;
- do not add RAM writes;
- do not add gameplay input injection;
- do not implement one-key moves / Assist Mode;
- do not reintroduce `window.Worker` replacement or Blob Worker wrapping;
- do not use native Chrome process memory as the primary transport.

## Pass condition

Real owner proof reaches simultaneously:

```text
Browser: OK
WOF page: OK
Worker: OK
WASM / heap: OK
World 921031: OK
READ ONLY / RAM writes: 0
```

and the room remains normally playable.

## After PASS

Do not directly modify Alpha in this stage. Record exactly what CDP/live-Worker transport capability is proven and prepare a handoff for a separate fresh Alpha transport-integration stage.

## Stop condition

Stop when either:
- only one minimal owner Windows proof remains, with exact operation and expected output; or
- the owner proof has passed and a concise result/handoff is committed; or
- one precise platform/browser limitation remains.
