# Final Fresh-QA SUT Adapter Contract

Status: **QA-owned binding contract; not implementation regression authority.**

The post-Hardening Fresh QA may add one thin QA-owned adapter for the exact fixed SUT. The adapter exists only to translate the final public proof-tooling interface into the frozen fixture oracle. It must not import, call, copy, or derive expected outcomes from Hardening V2 implementation regression files.

Required module exports:

```js
export const ADAPTER_SCHEMA = 'wof-alpha-v1-proof-authority-hardening-v2-qa-adapter-v1';
export async function runCase(caseSpec, vectors) {
  return {
    caseId: caseSpec.id,
    expected: caseSpec.expected,
    pass: true | false,
    reason: '...',
    assertions: { /* every key in caseSpec.asserts must be literal true to pass */ },
    evidence: ['independent observable/result reference', '...']
  };
}
```

## Independence / fail-closed rules

- The adapter must load only the exact post-Hardening fixed blobs pinned by the Fresh-QA stage plus Node/platform primitives needed by the independent harness.
- Do not use `proof_authority_regression.mjs`, `tooling_regression.mjs`, or any Hardening V2 selftest verdict as an oracle.
- The adapter must actively construct the adversarial input from `fixture_vectors.mjs`; it may not replace a negative case with a source-text claim when the fixed public interface permits a behavioral attack.
- If the final public interface changed, adapt only the call/binding mechanics. Do **not** change `fixture_catalog.json`, case IDs, expected outcome, or required assertion names.
- If a case cannot be exercised independently against the fixed public interface, return `pass:false` with the precise untestable boundary. Do not silently mark it supportive/pass.
- A positive case must use the same fixed authority/lifecycle identity throughout. A negative case must demonstrate the requested mismatch/replay/replacement rather than failing for an unrelated prerequisite.
- Evidence refs must identify the concrete observed result for that case (for example: returned rejection reason, terminal verdict, authority tuple, profile activation state, transaction acceptance state, or exact safety status).

## Special case notes

`QA-PA-001` must use an attacker-owned P-256 key/signature and prove that the witness cannot choose the verification root that authenticates itself.

`QA-PA-003` / `004` / `005` must vary the exact authority dimensions independently: proof session, Worker generation, runtime epoch, pair generation, and pair nonce. An unrelated malformed witness is not sufficient evidence.

`QA-PA-006` / `007` / `008` must use explicit lifecycle-generation changes. Same slot/type/near coordinates are deliberately retained in the replacement vector so continuity cannot be inferred from proximity alone.

`QA-PA-009` must distinguish the helper/surface mapping identity from the current drawing-buffer mapping identity and demonstrate fail-closed scoring.

`QA-PA-010` / `011` / `012` must iterate the complete malformed/coercible vectors supplied by `fixture_vectors.mjs`.

`QA-PA-013` must mutate/serialize public state aggressively, then call the real terminal/verdict boundary; a mere schema parser rejection is not enough.

`QA-PA-014` must cover both reused transaction ID and stale/replayed signed evidence.

`QA-PA-015` is the positive control: same authority + same lifecycle retarget/scoring must still work so deny cases are not satisfied by globally disabling proof.

`QA-PA-016` must observe exact values `readOnly=true`, `ramWrites=0`, `inputInjection=false`, `workerReplacement=false` from the fixed proof/runtime boundary.

`QA-PA-017` must compare production projection/calibration profile state before and after synthetic/repository evidence injection and prove no activation/promotion occurred.
