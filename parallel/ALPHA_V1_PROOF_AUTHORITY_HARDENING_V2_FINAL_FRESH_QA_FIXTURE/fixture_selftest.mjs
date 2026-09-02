import fs from 'node:fs';
import assert from 'node:assert/strict';
const p=new URL('./fixture_catalog.json',import.meta.url);
const c=JSON.parse(fs.readFileSync(p,'utf8'));
assert.equal(c.schema,'wof-alpha-v1-proof-authority-hardening-v2-final-fresh-qa-fixture-v1');
assert.equal(c.ownership,'QA-OWNED-INDEPENDENT');
assert.equal(c.implementationRegressionAuthority,false);
assert.equal(c.currentSutVerdictIssued,false);
assert.equal(c.futureExecution.requiresHardeningV2Complete,true);
assert.equal(c.futureExecution.requiresExactFixedBlobPins,true);
assert.equal(c.futureExecution.mayChangeExpectedOutcomes,false);
const ids=c.cases.map(x=>x.id);
assert.equal(new Set(ids).size,17);
for(let n=1;n<=17;n++) assert.ok(ids.includes(`QA-PA-${String(n).padStart(3,'0')}`));
for(const x of c.cases){ assert.ok(x.domain&&x.expected&&x.intent); assert.ok(Array.isArray(x.asserts)&&x.asserts.length); }
const required=['untrusted-signer-provenance','synthetic-repository-fake-live','exact-authority-binding','authority-change-revocation','cross-authority-aggregation','player-respawn-calibration','enemy-same-slot-replacement','enemy-type-offset-lifecycle','surface-mapping-authority','malformed-coercible-epoch','warning-sampleat-strict','target-strict','public-mutable-terminal','stale-replayed-transaction','same-authority-positive-flow','safety-boundary-exact','synthetic-no-production-activation'];
assert.deepEqual(new Set(c.cases.map(x=>x.domain)),new Set(required));
console.log('PASS — fixture schema/coverage self-check only — 17/17 — NO SUT LOADED — NO SUT VERDICT');
