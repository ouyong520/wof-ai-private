# Alpha V1 Owner Final Acceptance Orchestrator

P17 only coordinates existing evidence producers. It never becomes renderer/object position authority and never moves `alpha-live`.

## Owner path

Run `WOF_ALPHA_FINAL_ACCEPTANCE.cmd`. The wrapper invokes the existing bounded W3 qualification runner, then reads:

- W3 renderer/object qualification output;
- `~/Documents/WOF_RESULTS/ALPHA_CANONICAL_ACCEPTANCE_EVIDENCE.json` from P16;
- optional `~/Documents/WOF_RESULTS/ALPHA_CANONICAL_DRAW_EVIDENCE.json` from P18.

It writes `ALPHA_FINAL_ACCEPTANCE_BUNDLE.json` and `.md` to the Owner results directory.

## Automatic states

`WAITING_W3_QUALIFICATION`, `W3_INCONCLUSIVE`, `WAITING_CANONICAL_RUNTIME_EVIDENCE`, `CANONICAL_RUNTIME_SUPPRESSED`, `WAITING_DRAW_EVIDENCE`, `FAILED_EVIDENCE_MISMATCH`, and `READY_FOR_OWNER_VISUAL_CONFIRMATION`.

`READY_FOR_OWNER_VISUAL_CONFIRMATION` is the highest automatic state. Repository/runtime/draw acknowledgement never becomes visual `PASS`; `visibleProof` remains `NOT_PROVEN` until an explicit Owner screen confirmation is supplied outside this module.

## Offline / focused mode

Use `--w3-qualification <qualification.json>` to consume an existing W3 qualification instead of launching WOF. `--p16-evidence` and `--p18-evidence` may point at synthetic fixtures for focused tests.

The reader fails closed on mixed World, authority, runtime epoch, renderer epoch, renderer authority, page target, package version, or source commit identities where those fields are present. It also requires read-only/zero-write/no-input safety and rejects any automatic visible-proof promotion.
