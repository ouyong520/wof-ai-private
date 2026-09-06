# P49 Owner Windows One-Run Handoff

This bundle does **not** run automatically and does not authorize any retry. It is a local bridge for the single remaining PM-authorized P43 bounded diagnostic.

On the Owner Windows machine, first ensure the existing game/browser session and exact source checkout are already present. Do not launch or install anything through this bundle. Then run:

```cmd
parallel\OWNER_DIAGNOSTIC\WOF_ALPHA_P49_OWNER_WINDOWS_ONE_RUN_HANDOFF.cmd "<metadata-repo-root>" "<source-checkout>" "<exact-browser-websocket-debugger-url>" "<output-directory>"
```

All four arguments are mandatory and are never guessed. The source checkout must be clean and at exact HEAD `82b0b09ecd902f502ae5509bcb3ee5a713f43fee`. The only accepted interpreter is `%LOCALAPPDATA%\WOF Alpha Current Main\venv\Scripts\python.exe`.

Before live start, the runner verifies the pinned P49/P48/P47/P43/P45/P46/P38 authority bytes, P48's unconsumed budget, exact source checkout, managed interpreter, reachable debugger endpoint, output writability, and absence of a prior marker. Any failure before `RUN_STARTED` exits fail-closed without consuming the budget.

Immediately before invoking the existing `parallel\OWNER_DIAGNOSTIC\WOF_ALPHA_P43_BOUNDED_DIAGNOSTIC.cmd`, the runner atomically creates a permit-scoped `RUN_STARTED.json` under `%LOCALAPPDATA%\WOF Alpha Current Main\owner-diagnostic-permits\<permitIdentity>\`. Once that marker exists, the unique run budget is consumed even if P43 later times out or fails. A second launch with the same permit is rejected. There is no automatic retry.

After the run, keep the complete output directory unchanged. P43's raw evidence and receipt remain authoritative. P49 adds `P49_ONE_RUN_HANDOFF_IMPORT.json` plus unfiltered stdout/stderr pointers; it does not push, promote, move `alpha-live`, or change diagnostic semantics.
