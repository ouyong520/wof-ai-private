# Alpha V1 P28 — Durable Owner Acceptance Provenance

P28 is a read-only provenance/session layer. It does not run WOF, ask the Owner a visual question, promote `alpha-live`, inject input, write game RAM, or derive production coordinates from screenshots/world projection.

`durable_session.py` is the production-shaped P28 entrypoint. It persists an immutable session root, binds evidence incrementally, exposes deterministic monotonic states, records explicit runtime/renderer epoch transitions, fails closed on incompatible evidence, and provides verify-only reload plus a concise terminal summary.

The supported causal chain is:

`P19 -> P21 -> W3/P16/P18 -> P22/P24[/P25] -> P17 -> P20 receipt -> P20 plan/result -> P23`.

The durable session binds the exact P19 source/package/candidate/attestation identity; session/run nonce; exact World/page/authority/runtime/renderer identity; P21 identity when available; ordered artifact byte/semantic hashes; ACK generation; P17 dependency hashes; P20 receipt/plan/result consistency; and P23 promoted-session close evidence. Runtime/renderer replacement is accepted only through an explicit ordered epoch-transition artifact with before/after authority evidence and the same World/page identity.

Monotonic states are:

`OPEN -> WAITING_FOR_LIVE_W3 -> WAITING_FOR_CANONICAL_EVIDENCE -> WAITING_FOR_DYNAMIC_TEMPORAL_EVIDENCE -> READY_FOR_OWNER_VISUAL_CONFIRMATION -> WAITING_FOR_PROMOTION -> WAITING_FOR_POST_PROMOTION_VERIFY -> CHAIN_COMPLETE`

Any first incompatible artifact transitions the session to terminal `REJECTED`. `CHAIN_COMPLETE` proves provenance consistency only; it does not itself prove Owner-visible acceptance or move `alpha-live`.

Persistence is sibling-temp -> file flush/fsync -> atomic publication -> best-effort parent-directory fsync. Terminal sessions are immutable. `verify`/`status` reload the persisted bytes and do not mutate the session or source artifacts. Artifact and epoch-transition counts are bounded.

## Durable CLI

Python:

```text
python durable_session.py open --root <root.json> --session <session.json>
python durable_session.py bind --session <session.json> --stage P19 --artifact <artifact.json> --bindings-json <json>
python durable_session.py transition --session <session.json> --artifact <epoch-transition.json>
python durable_session.py status --session <session.json>
python durable_session.py verify --session <session.json>
python durable_session.py finalize --session <session.json> [--summary <summary.md>]
```

Windows wrapper uses the same arguments and routes to `durable_session.py`:

```text
WOF_ALPHA_VERIFY_ACCEPTANCE_PROVENANCE.cmd status --session "C:\path with spaces\session.json"
WOF_ALPHA_VERIFY_ACCEPTANCE_PROVENANCE.cmd verify --session "C:\path with spaces\session.json"
```

`provenance_chain.py` remains as the earlier one-shot manifest compatibility path for already-authored P28 fixtures; the durable CLI above is the authoritative incremental session interface required by the P28 rebuild.

The implementation safety contract is fixed: `readOnly=true`, `ramWrites=0`, `inputInjection=false`, `visibleProof=NOT_PROVEN`, `realWofAcceptance=NOT_RUN`, `ownerVisualAcceptance=NOT_RUN`, and `alphaLiveMoved=false`.
