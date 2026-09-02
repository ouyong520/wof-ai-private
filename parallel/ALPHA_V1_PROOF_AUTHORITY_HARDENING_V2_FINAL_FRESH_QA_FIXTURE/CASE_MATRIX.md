# QA-owned Final Fresh-QA Case Matrix

Authority: PM Hardening V2 contract + Cross-check V2 blocker semantics only. This matrix is intentionally separate from implementation regressions.

| Case | Independent adversarial construction | Expected observation |
|---|---|---|
| QA-PA-001 | Begin a fresh proof session/challenge. Generate an attacker-owned P-256 keypair, sign a syntactically correct witness with the attacker private key, and supply the attacker public key as witness material. | Witness rejected; no branded/live capability; terminal cannot become `IMPLEMENTATION_READY`. |
| QA-PA-002 | Serialize/clone repository-created Session/public evidence and populate live-looking booleans, evidence class, phase coverage, visual flags and candidate payloads without a trusted live root. | Synthetic/repository state remains non-live; terminal stays non-ready; production profile state unchanged. |
| QA-PA-003 | Establish one valid fixed authority in the final QA adapter, then vary proofSession, Worker generation, runtime epoch, pair generation and pair nonce one dimension at a time on otherwise-valid counted events. | Only the exact five-dimension authority identity is countable. Each single-dimension mismatch is rejected/fail-closed. |
| QA-PA-004 | After a valid capability/profile bind, change each authority dimension independently and try to reuse the old capability and old bound profile. | Old capability/profile becomes invalid; fresh challenge/rebind is required before new authority can count. |
| QA-PA-005 | Feed valid-looking phases/events under authority A and authority B at different times, arranging them so public phase fields would be complete if aggregation were allowed. | Cross-authority evidence cannot aggregate to terminal success; no mixed-authority `IMPLEMENTATION_READY`. |
| QA-PA-006 | Calibrate P1 head/body under `P1@g41`; replace/respawn to `P1@g42`; attempt bind/use of the old calibration with current snapshots otherwise valid. | Old body/head calibration rejected; fresh same-lifecycle calibration required. |
| QA-PA-007 | Use same enemy slot, same type, near-identical coordinates and target transition, but change lifecycle `enemy-slot-3@g91 -> @g92` without continuity proof. | Replacement is not counted as retarget. |
| QA-PA-008 | Capture a type offset under enemy lifecycle g91, then replace with same type at g92 and attempt to reuse the type/global offset without an explicit safe lifecycle authority proof. | Profile activation/bind fails closed or offset is not applied to the new occupant. |
| QA-PA-009 | Keep runtime/projection epochs fresh but set helper/surface mapping identity to stale `map-v8` while current drawing-buffer authority is `map-v9`; also test the inverse mismatch. | Anchored event is uncountable/suppressed/fallback; stale mapping cannot close a phase. |
| QA-PA-010 | Iterate all `malformedEpochs`: null/undefined/numbers/bools/objects/arrays/boxed string/toString object/NaN/±Infinity in each epoch authority field. | No coercion to a valid 32-hex epoch; authority tuple invalid/fail-closed. |
| QA-PA-011 | Iterate all `malformedWarningSampleAt`: missing/null/string/boxed/valueOf/NaN/±Infinity/object/array while secondary timestamps are fresh. | Invalid `warningSampleAt` cannot fall back to secondary time/`Date.now()`; warning evidence is not fresh/countable. |
| QA-PA-012 | Iterate malformed target vectors including strings `0/4/8`, boxed numbers, valueOf objects, arrays, booleans, NaN/Infinity and fractional values. | Only primitive finite exact supported target values are consumed; malformed/coercible values fail closed. |
| QA-PA-013 | Mutate all reachable public Session/bind/phase/visual/authority fields, serialize/deserialize candidate evidence, then invoke the real terminal/verdict boundary. | Private/immutable attested state is recomputed; public state cannot force `IMPLEMENTATION_READY`. |
| QA-PA-014 | Accept one valid transaction witness in the fixed harness, replay exact bytes/transaction ID, then replay after freshness window/authority rotation. | Reused/stale/replayed evidence rejected; stale authority gate is not closed by replay. |
| QA-PA-015 | Positive control: exact same authority, same lifecycle and monotonically continuous samples with an actual P1->P2 retarget plus ordinary live phase events. | Retarget and same-authority phase scoring remain accepted; hardening is not a blanket deny. |
| QA-PA-016 | Read the fixed proof/runtime boundary before and after all attacks. | Exact invariant values remain `readOnly=true`, `ramWrites=0`, `inputInjection=false`, `workerReplacement=false`. |
| QA-PA-017 | Snapshot production projection/calibration profile activation state, inject repository/synthetic evidence and forged candidates, then snapshot again. | No synthetic path activates/promotes a production projection or calibration profile. |

## Cross-case rules

1. Negative cases must fail for the intended authority mismatch, not because the fixture omitted an unrelated prerequisite.
2. `QA-PA-015` is mandatory positive control for the same public surface exercised by the negative cases.
3. Exact authority dimensions are varied independently before combined-mismatch tests.
4. Malformed/coercible vectors are exhaustive over the values frozen in `fixture_vectors.mjs`.
5. A future adapter may translate final public method names, but it may not change any expected outcome in this matrix or `fixture_catalog.json`.
