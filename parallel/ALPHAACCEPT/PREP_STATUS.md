# WOF Alpha Transport-Aware Browser Acceptance V2 — Prep Status

Updated: 2026-09-01

## Preparation verdict

**ACCEPTANCE PREP READY — WAITING FOR TRANSPORT INTEGRATION**

The old RC3-era acceptance package has been superseded by a transport-aware V2 preparation package.

## Why acceptance is not runnable yet

This prep lane does not pretend the Safe Transport already exists.

Current external blockers are outside `parallel/ALPHAACCEPT/**`:

1. PYLAUNCH still requires one fresh real Windows proof after the Worker-discovery v2 repository fix;
2. Safe Transport Integration must then be implemented from the PM contract;
3. product regression + transport integration tests + PYLAUNCH tests must all PASS before the bounded real Browser acceptance is authorized.

RC5 itself is not blocked by the old RC3 diagnostic issue. Fresh RC5 independent QA already says:

`PASS — RC5 ROOM-ENTRY REPAIR QA`

and preserves immediate current-diag invalidation, 1500 ms ordinary stale behavior, exact World 921031 identity, the two T18 production rules, fail-open gameplay, and read-only/no-input requirements.

## Prepared acceptance surfaces

V2 now has:

- exact acceptance matrix;
- fixed driver/collector handoff contract;
- machine-readable fixture vectors;
- compact final JSON schema;
- stdlib-only result validator;
- transport-aware page collector;
- Simplified-Chinese owner steps/UI;
- explicit negative checks for old generation/wrong nonce;
- explicit reconnect/rebind freshness checks;
- explicit gameplay liveness/owner playability confirmation;
- explicit safety fields `readOnly=true`, `ramWrites=0`, `inputInjection=false`.

## No owner action now

Do **not** ask the owner to run Browser acceptance yet.

The future integration stage may authorize the run only after its own stop condition is:

`INTEGRATION IMPLEMENTED — READY FOR BOUNDED REAL BROWSER ACCEPTANCE`

At that point the acceptance flow is already specified and should be wired to the fixed V2 driver contract rather than redesigned.

## Files modified by this prep lane

Only `parallel/ALPHAACCEPT/**`.

No `product/alpha/**` modification.
No `parallel/PYLAUNCH/**` modification.
No WOF-052L modification.

## Stop condition

**ACCEPTANCE PREP READY — WAITING FOR TRANSPORT INTEGRATION**
