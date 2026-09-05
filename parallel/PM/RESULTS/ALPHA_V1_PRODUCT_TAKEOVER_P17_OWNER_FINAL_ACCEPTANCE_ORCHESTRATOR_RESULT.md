# Alpha V1 P17 — Owner Final Acceptance Orchestrator Result

## Outcome

**COMPLETE / integration-ready.** P17 now provides a repository-ready one-command final acceptance orchestrator. It invokes the existing bounded W3 qualification entrypoint when requested, consumes P16 canonical runtime evidence, consumes optional P18 maintained draw evidence through the shared contract, checks cross-evidence identity/safety consistency, and writes deterministic final JSON/Markdown acceptance bundles.

The highest automatic decision is `READY_FOR_OWNER_VISUAL_CONFIRMATION`. `visibleProof` is always `NOT_PROVEN` inside P17; repository/runtime/draw acknowledgement never becomes final visual PASS.

## Changes

- Added `parallel/OWNER_ACCEPTANCE/final_acceptance_orchestrator.py` with deterministic states:
  - `WAITING_W3_QUALIFICATION`
  - `W3_INCONCLUSIVE`
  - `WAITING_CANONICAL_RUNTIME_EVIDENCE`
  - `CANONICAL_RUNTIME_SUPPRESSED`
  - `WAITING_DRAW_EVIDENCE`
  - `FAILED_EVIDENCE_MISMATCH`
  - `READY_FOR_OWNER_VISUAL_CONFIRMATION`
- Reuses `parallel/RENDER_AUTHORITY_V2/run_long_qualification.py` as a subprocess; it does not modify W3 producer/analyzer code.
- Supports offline focused mode with an already-produced W3 qualification JSON/latest pointer.
- Validates P16 exact World/page/worker/runtime/authority/renderer identity and `HUD_INGEST_ACCEPTED` semantics.
- Defines a P18 reader for `ALPHA_CANONICAL_DRAW_EVIDENCE.json`; missing P18 yields `WAITING_DRAW_EVIDENCE`, never PASS.
- Rejects mixed World/page/authority/runtime/renderer/package/source identities fail-closed.
- Atomically writes `ALPHA_FINAL_ACCEPTANCE_BUNDLE.json` and `.md` under the Owner results directory.
- Added Windows-friendly `WOF_ALPHA_FINAL_ACCEPTANCE.cmd` with simple Chinese Owner instructions; no DevTools, manual JSON editing, calibration, coordinate choice, package hunting, or alpha-live movement.
- Added focused tests and protocol README.

Implementation commits:
- `663abef54e4f2249bf102d77101d0222d56dbc0d`
- `1688bf11a436d6a3728a13e496fc78d2751ce943`

The second commit repairs an upload truncation detected before closeout; final committed blob SHAs match the exact tested local files.

## Tests

- **PASS** — Python compile/parse for orchestrator and focused test.
- **PASS** — 6 focused unittests:
  - W3 PASS + P16 `HUD_INGEST_ACCEPTED` + P18 `CANONICAL_DRAW_ACKNOWLEDGED` -> `READY_FOR_OWNER_VISUAL_CONFIRMATION` only;
  - W3 `INCONCLUSIVE` never advances;
  - mixed renderer/runtime identity -> `FAILED_EVIDENCE_MISMATCH`;
  - missing P18 -> `WAITING_DRAW_EVIDENCE`;
  - fixed-timestamp bundle write/read is deterministic;
  - Windows wrapper resolves the intended orchestrator without DevTools/manual JSON editing.
- **PASS** — committed blob integrity; final orchestrator blob `bd97ea24b1669c03020b9d16ea0e43cdd100b7f0` equals the locally compiled/tested file.
- **NOT RUN** — real WOF / Owner visual acceptance, by explicit stage boundary.

## Integration

P17 touches only new files under `parallel/OWNER_ACCEPTANCE/` plus its RESULT files. It does not edit P15 runtime/package files, W3 producer/analyzer/claim, P16 state/tray/evidence implementation, maintained HUD JS, package manifests/pins, or alpha-live selection.

Product proof boundary:

`checked-in P15 candidate metadata -> existing W3 bounded qualification -> P16 canonical evidence -> optional P18 draw evidence -> exact identity consistency -> final acceptance bundle -> READY_FOR_OWNER_VISUAL_CONFIRMATION`

Safety remains read-only with zero RAM writes, no input injection, no screenshot/world-projection production coordinates, no guessed renderer/object address, and no alpha-live movement.

## Owner Action

No Owner action is required for this implementation stage. After PM refreshes one final candidate containing P15 + P16 + P17 + P18, the eventual single bounded gate is:

`parallel\OWNER_ACCEPTANCE\WOF_ALPHA_FINAL_ACCEPTANCE.cmd`

The Owner then only keeps/starts WOF, plays normally during the bounded W3 sample, and visually answers whether the overlay follows the correct actors.

## Recommended Next

PM should refresh/integrate the final candidate with P15 + P16 + P17 + P18 without moving alpha-live, then run the single bounded W3/Owner acceptance round. If W3 remains `INCONCLUSIVE` or any evidence identity disagrees, retain fail-closed state and do not guess coordinates or addresses.

Closeout: canonical and stage claims were re-read with the exact P17 claim token and are now `COMPLETE`; durable RESULT.json/RESULT.md are present.
