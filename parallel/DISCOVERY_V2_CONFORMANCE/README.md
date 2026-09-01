# WOF Discovery V2 Cross-Component Conformance Harness

Status target: `DISCOVERY V2 CONFORMANCE HARNESS READY`

## Purpose

This lane converts the manual `parallel/DISCOVERY_V2_AUDIT/RESULT.md` comparison into a repeatable synthetic/fixture-driven cross-component harness.

It does **not** require a real Browser, DevTools, Worker Console, pasted JS, game input, or Owner intervention.

The harness executes the current repository regression adapters/public Discovery V2 entry surfaces for:

- Browser Fleet;
- PYLAUNCH;
- WOF-052L Recorder hardened V2 owner path;
- Prospective Validator hardened V2 path.

It normalizes the outcome into a per-scenario matrix with exactly three states:

- `PASS`
- `FAIL`
- `EXPECTED_ROLE_DIFFERENCE`

`EXPECTED_ROLE_DIFFERENCE` is intentionally not greenwashed into `PASS`. Browser Fleet remains advisory/cheap-indicator-only, while PYLAUNCH / Recorder / Prospective retain their own authoritative admission roles.

## Required topology coverage

`run_conformance.py` declares all required cases explicitly:

1. one page / one worker;
2. two pages / two workers;
3. two pages / same shared worker;
4. iframe -> worker;
5. direct worker fallback;
6. misleading openerId;
7. gstyphoon Worker URL;
8. hashed Worker URL;
9. blob Worker URL;
10. data Worker URL;
11. no-extension Worker URL;
12. remote host;
13. cross-port websocket;
14. loopback alias;
15. reload/recreated worker;
16. stale target/session;
17. exact supported identity;
18. wrong identity;
19. one-room failure isolation;
20. advisory Fleet vs authoritative role difference.

## Safety invariants

Every run also checks the component regression safety surfaces and a narrow production-source mutation scan for:

```json
{
  "readOnly": true,
  "ramWrites": 0,
  "inputInjection": false,
  "workerReplacementOrWrap": false,
  "blobDataObjectUrlCreationOrRewrite": false,
  "productionAutoPromotion": false
}
```

Observing an already-existing `blob:` / `data:` Worker is allowed. Creating/replacing/wrapping Workers, creating Blob/ObjectURL Workers, writing game RAM, or injecting gameplay input is not.

## Run

From repository root:

```text
python parallel/DISCOVERY_V2_CONFORMANCE/run_conformance.py
```

Outputs:

- `parallel/DISCOVERY_V2_CONFORMANCE/RESULT.json` — machine-readable current-HEAD result;
- `parallel/DISCOVERY_V2_CONFORMANCE/SUMMARY_ZH_CN.md` — Simplified Chinese summary.

The runner fingerprints current component source files, records the git HEAD, caches no live Browser state, and returns non-zero when a required fixture probe or safety invariant fails.

Harness declaration self-test:

```text
cd parallel/DISCOVERY_V2_CONFORMANCE
python test_harness.py
```

## Role rules encoded by the harness

- Browser Fleet: advisory `cheap-indicator-only`; exact World 921031 identity is deliberately `NOT_CHECKED` / non-authoritative.
- PYLAUNCH: authoritative single-selection proof; more than one exact supported pair fails closed.
- Recorder: evidence admission may keep independent rooms, but the same exact Worker associated with multiple pages must admit none of those relations.
- Prospective Validator: same cross-page fail-closed relation rule; discovery diagnostics remain `discovery-only` and never become prospective evidence.

No component implementation is modified by this harness lane.
