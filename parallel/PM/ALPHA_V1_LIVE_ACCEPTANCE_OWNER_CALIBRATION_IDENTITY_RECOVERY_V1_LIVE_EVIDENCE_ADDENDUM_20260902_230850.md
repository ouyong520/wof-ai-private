# Alpha V1 Live Acceptance Owner Calibration + Local Identity Recovery V1 — Live Evidence Addendum 2026-09-02 23:08:50

This PM evidence addendum supplements, but does not replace or alter ownership metadata in:

`parallel/PM/ALPHA_V1_LIVE_ACCEPTANCE_OWNER_CALIBRATION_IDENTITY_RECOVERY_V1_START_PROMPT.md`

The current recovery canonical claim remains authoritative and ACTIVE. This addendum does not authorize a second worker or a new dedup generation.

## Owner evidence artifact

Owner-uploaded automatic evidence package:

`WOF_LIVE_ACCEPTANCE_live_session_20260902_230850.zip`

Observed SHA-256:

`aade84374e72f09aa6524fd60003e48a310b1a225d5fcdde2a0de88bbdf7be8b`

ZIP contains exactly:

- `launcher.stderr.txt`
- `launcher.stdout.txt`
- `SESSION_SUMMARY.json`
- `WINDOWS_PROOF_STATUS.json`

## 1. New Windows tray defect captured in launcher.stderr

`launcher.stderr.txt` records a real uncaught Python/Tkinter exception:

```text
Exception in thread Thread-5 (run):
...
File "...\\parallel\\PYLAUNCH\\wof_launcher\\tray.py", line 121, in run
    messagebox.showinfo(title, body); root.destroy()
...
RuntimeError: main thread is not in main loop
```

This is a real Windows Owner-facing defect. Tkinter messagebox work is being invoked from a background thread in a way that can fail under Python 3.13 / the Owner runtime. It can cause status/diagnostic prompts to stop appearing even though the launcher process itself continues.

Required recovery integration:

- fix tray/UI dispatch so Tk/Tkinter calls execute on a valid Tk main-loop thread or use an equivalent thread-safe Owner notification path;
- no silent thread death;
- deterministic test for repeated status/diagnostic notifications and shutdown;
- keep launcher/game safety unchanged.

Do not assume this alone explains HUDANCHOR `NEED_MORE_SAMPLES`; treat it as an independent, concrete Owner UX/runtime defect unless implementation evidence proves coupling.

## 2. Automatic evidence package is losing the useful live failure state

`SESSION_SUMMARY.json` shows:

```json
{
  "launcherReturnCode": 0,
  "launcherError": null,
  "finalState": "UNKNOWN",
  "projectionVerdict": null,
  "partialEvidenceRetained": true,
  "zipReady": true,
  "safety": {
    "readOnly": true,
    "ramWrites": 0,
    "inputInjection": false
  },
  "upload": {
    "attempted": false,
    "status": "LOCAL_ONLY_NO_REPOSITORY_DEFINED_SECURE_UPLOADER"
  }
}
```

The package successfully created the ZIP and retained partial evidence, but it did not preserve the live `P1/P2/P3 local identity mismatch` shown to the Owner or any calibration progression/terminal result.

`launcher.stdout.txt` is empty.

`WINDOWS_PROOF_STATUS.json` at session end contains only the shutdown/disconnected state:

- `automatedResult: WAITING`
- all Browser/WOF page/Worker/WASM/World checks are `--`
- `launcherState: ERROR`
- `alphaRunning: false`
- `alphaError: Launcher 与浏览器连接中断... CDP is not connected`
- `lastError` is the same CDP-disconnected message

This end-of-session snapshot overwrote or failed to retain the earlier useful accepted runtime state that the Owner visibly observed:

- Browser connected
- WOF page found
- Worker found
- WASM/heap found
- exact World 921031 accepted
- Alpha activation failed specifically on `P1/P2/P3 local identity mismatch`
- calibration reached `samples 29 / NEED_MORE_SAMPLES`

Therefore current automatic evidence is insufficient for field diagnosis even though ZIP packaging itself works.

Required recovery integration:

- preserve a bounded event/timeline or last-known-significant-state record, not only the terminal disconnect snapshot;
- retain exact Alpha activation failure reason before later disconnect/revoke;
- retain last accepted Browser/Page/Worker/WASM/World authority tuple and generation before shutdown;
- retain calibration stage/reason/progress transitions, including `NEED_MORE_SAMPLES`, restart/reset, timeout/watchdog, camera-ready, click-needed, later checklist states, and terminal result if any;
- SESSION_SUMMARY should distinguish `session ended normally` from `final status snapshot is disconnected` and should not collapse a diagnostically useful run to `UNKNOWN` solely because the browser closed;
- evidence must remain bounded, local-safe, secret-free, and automatically ZIPped.

## 3. Safety evidence remains good

The uploaded ZIP confirms:

- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`
- automatic ZIP ready
- no automatic Git upload attempted without repository-defined authority

These boundaries must remain unchanged.

## PM interpretation

This new evidence does **not** invalidate the current recovery task. It strengthens it with two additional concrete implementation defects inside the same coherent Owner live-acceptance recovery scope:

1. Tkinter tray/status UI thread crash on Windows/Python 3.13.
2. Auto-evidence final-snapshot collapse that loses the actual live identity/calibration failure.

Do not open a new QA/second worker. Fold these fixes into the already ACTIVE `ALPHA_V1_LIVE_ACCEPTANCE_OWNER_CALIBRATION_IDENTITY_RECOVERY_V1`, alongside the previously identified active/inactive player local identity semantics and HUDANCHOR calibration continuity work.

Final successor package must not be sent to Owner until these defects and the original recovery goals have package-selected implementation, module-owned self-check, Windows portable validation, durable RESULT, and canonical/stage COMPLETE closeout.
