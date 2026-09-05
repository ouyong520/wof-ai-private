# Alpha V1 P28 — Durable Owner Acceptance Provenance

P28 is a read-only provenance/session layer. It does not run WOF, ask the Owner a visual question, promote `alpha-live`, inject input, write game RAM, or derive production coordinates from screenshots/world projection.

`provenance_chain.py` consumes a `wof-alpha-owner-acceptance-provenance-manifest-v1` that names the exact source artifact bytes for the ordered chain:

`P19 -> P21 -> W3/P16/P18 -> P22/P24 -> P17 -> P20 receipt/plan/result -> P23`.

The manifest supplies the immutable session root: exact P19 source/package/candidate/attestation identity; P21 session + run token; exact World/page/authority/runtime/renderer identity; P18 ACK generation; and same-run P22/P24 identifiers. Each stage record is byte-hashed and semantic-hashed into a deterministic artifact ledger. P17 dependency hashes, the P20 receipt/plan/result chain, and the P23 promoted-session binding are mandatory and fail closed.

The persisted session is terminal and immutable. It records explicit transitions:

`PRECHECK -> RENDERER_QUALIFIED -> OWNER_READY -> OWNER_RECEIPT -> OWNER_DECISION -> CLOSED`.

Every transition is bound to the exact runtime epoch, renderer epoch, ACK generation, and the byte hashes of the evidence that authorizes that edge. Any identity, epoch, generation, cross-run, dependency-hash, plan/result, or promoted-session mismatch invalidates the attempted root; callers must start a new session rather than rewrite a prior terminal root.

Persistence is sibling-temp -> file flush/fsync -> `os.replace` -> best-effort parent-directory fsync. `verify` is verify-only: it reloads every referenced source artifact, recalculates byte/semantic hashes, revalidates session identity and ACK generation, reconstructs transitions and the deterministic chain digest, and never mutates the session or source artifacts.

## CLI

Python:

```text
python provenance_chain.py build --manifest <manifest.json> --output <session.json>
python provenance_chain.py verify --session <session.json>
```

Windows wrapper:

```text
WOF_ALPHA_VERIFY_ACCEPTANCE_PROVENANCE.cmd verify --session "C:\path with spaces\session.json"
```

The implementation safety contract is fixed: `readOnly=true`, `ramWrites=0`, `inputInjection=false`, `visibleProof=NOT_PROVEN`, `realWofAcceptance=NOT_RUN`, `ownerVisualAcceptance=NOT_RUN`, and `alphaLiveMoved=false`.
