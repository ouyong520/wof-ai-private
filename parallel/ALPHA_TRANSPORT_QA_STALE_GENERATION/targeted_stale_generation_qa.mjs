import { strict as assert } from 'node:assert';
import { CONTRACT, SAFETY, makeStateEnvelope } from '../ALPHA_TRANSPORT_IMPL/constants.mjs';
import { PageTransportAuthority } from '../ALPHA_TRANSPORT_IMPL/page_authority.mjs';
import { ReferenceWorkerRuntime } from '../ALPHA_TRANSPORT_IMPL/worker_runtime.mjs';

const SESSION_A = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa';
const SESSION_B = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb';
const identity = {
  moduleOk: true, heapOk: true, candidateCount: 1, hashStatus: 'accepted',
  sha256: CONTRACT.goldenSha256, readOnly: true, ramWrites: 0, inputInjection: false
};
const warningA = {
  ruleId: CONTRACT.allowedRuleIds[0], slot: 0, target7E: 0,
  sourceSide: 'RIGHT', threatSide: 'LEFT', attack: 5440,
  publication: 'hold-only-current-level', evidence: 'fresh-current-sample'
};
const warningB = {
  ruleId: CONTRACT.allowedRuleIds[1], slot: 1, target7E: 4,
  sourceSide: 'LEFT', threatSide: 'RIGHT', attack: 5424,
  publication: 'hold-only-current-level', evidence: 'fresh-current-sample'
};
const pair = (session, generation, ch) => ({
  session, pairGeneration: generation, pairNonce: ch.repeat(32)
});
const install = (worker, epoch, p) => {
  assert.equal(worker.install({
    runtimeEpoch: epoch, pair: p, launcherIdentityProbe: identity, detectorLocalIdentityOk: true
  }), true);
};
const deferred = () => {
  let resolve;
  const promise = new Promise(r => { resolve = r; });
  return { promise, resolve };
};

const cases = [];
const T = (name, fn) => cases.push([name, fn]);

T('independent async old generation completion is dropped and cannot steal fresh slot', async () => {
  const worker = new ReferenceWorkerRuntime();
  const page = new PageTransportAuthority({ session: SESSION_A });
  const p1 = pair(SESSION_A, 1, '1');
  const p2 = pair(SESSION_A, 2, '2');
  install(worker, 'epoch-a', p1);
  page.bind(p1);
  const oldAuthority = worker.startTick({ captureAuthority: true });
  assert.equal(Object.isFrozen(oldAuthority), true);
  assert.deepEqual(
    [oldAuthority.runtimeEpoch, oldAuthority.session, oldAuthority.pairGeneration, oldAuthority.pairNonce],
    ['epoch-a', SESSION_A, 1, p1.pairNonce]
  );
  const gate = deferred();
  const oldCompletion = gate.promise.then(warnings => worker.finishTick({
    nowMonoMs: 10, warnings, tickAuthority: oldAuthority
  }));

  install(worker, 'epoch-a', p2);
  page.bind(p2);
  const freshAuthority = worker.startTick({ captureAuthority: true });
  gate.resolve([warningA]);
  assert.equal(await oldCompletion, null);
  assert.equal(worker.publications.length, 0);
  assert.equal(worker.inFlight, true);
  assert.equal(worker.inFlightAuthority.tickAuthorityId, freshAuthority.tickAuthorityId);

  const fresh = worker.finishTick({ nowMonoMs: 11, warnings: [warningB], tickAuthority: freshAuthority });
  assert.ok(fresh);
  assert.equal(fresh.session, SESSION_A);
  assert.equal(fresh.pairGeneration, 2);
  assert.equal(fresh.pairNonce, p2.pairNonce);
  assert.equal(page.accept(fresh, 11), true);
  assert.equal(page.visibleWarnings(11).length, 1);
  assert.equal(worker.publications.length, 1);
});

T('runtime epoch reset revokes old authority but fresh completion remains valid', () => {
  const worker = new ReferenceWorkerRuntime();
  const p1 = pair(SESSION_A, 1, '3');
  const p2 = pair(SESSION_A, 2, '4');
  install(worker, 'epoch-a', p1);
  const oldAuthority = worker.startTick({ captureAuthority: true });
  assert.equal(worker.runtimeEpochChanged('epoch-b'), true);
  install(worker, 'epoch-b', p2);
  const freshAuthority = worker.startTick({ captureAuthority: true });
  assert.equal(worker.finishTick({ nowMonoMs: 20, warnings: [warningA], tickAuthority: oldAuthority }), null);
  assert.equal(worker.inFlightAuthority.tickAuthorityId, freshAuthority.tickAuthorityId);
  const fresh = worker.finishTick({ nowMonoMs: 21, warnings: [], tickAuthority: freshAuthority });
  assert.ok(fresh);
  assert.equal(fresh.pairGeneration, 2);
});

T('worker replacement revokes old worker authority', () => {
  const p1 = pair(SESSION_A, 1, '5');
  const p2 = pair(SESSION_A, 2, '6');
  const oldWorker = new ReferenceWorkerRuntime();
  install(oldWorker, 'epoch-a', p1);
  const oldAuthority = oldWorker.startTick({ captureAuthority: true });
  oldWorker.stop('worker-replaced');
  const newWorker = new ReferenceWorkerRuntime();
  install(newWorker, 'epoch-b', p2);
  const freshAuthority = newWorker.startTick({ captureAuthority: true });
  assert.equal(oldWorker.finishTick({ nowMonoMs: 30, warnings: [warningA], tickAuthority: oldAuthority }), null);
  assert.equal(oldWorker.publications.length, 0);
  const fresh = newWorker.finishTick({ nowMonoMs: 31, warnings: [], tickAuthority: freshAuthority });
  assert.ok(fresh);
  assert.equal(fresh.pairGeneration, 2);
});

T('reinstall with session change revokes old authority', () => {
  const worker = new ReferenceWorkerRuntime();
  const pA = pair(SESSION_A, 1, '7');
  const pB = pair(SESSION_B, 1, '8');
  install(worker, 'epoch-a', pA);
  const oldAuthority = worker.startTick({ captureAuthority: true });
  install(worker, 'epoch-a', pB);
  const freshAuthority = worker.startTick({ captureAuthority: true });
  assert.equal(worker.finishTick({ nowMonoMs: 40, warnings: [warningA], tickAuthority: oldAuthority }), null);
  assert.equal(worker.inFlightAuthority.tickAuthorityId, freshAuthority.tickAuthorityId);
  const fresh = worker.finishTick({ nowMonoMs: 41, warnings: [], tickAuthority: freshAuthority });
  assert.equal(fresh.session, SESSION_B);
});

T('legacy untagged completion after unresolved revoke fails closed', () => {
  const worker = new ReferenceWorkerRuntime();
  install(worker, 'epoch-a', pair(SESSION_A, 1, '9'));
  assert.equal(worker.startTick(), true);
  install(worker, 'epoch-a', pair(SESSION_A, 2, 'a'));
  const freshAuthority = worker.startTick({ captureAuthority: true });
  assert.equal(worker.finishTick({ nowMonoMs: 50, warnings: [warningA] }), null);
  assert.equal(worker.inFlight, true);
  assert.equal(worker.inFlightAuthority.tickAuthorityId, freshAuthority.tickAuthorityId);
  assert.ok(worker.finishTick({ nowMonoMs: 51, warnings: [], tickAuthority: freshAuthority }));
});

T('current untagged compatibility remains valid with no unresolved revoke', () => {
  const worker = new ReferenceWorkerRuntime();
  install(worker, 'epoch-a', pair(SESSION_A, 1, 'b'));
  assert.equal(worker.startTick(), true);
  const message = worker.finishTick({ nowMonoMs: 0, warnings: [warningA] });
  assert.ok(message);
  assert.equal(message.pairGeneration, 1);
});

T('one tick in flight skips overlap and never builds catch-up queue', () => {
  const worker = new ReferenceWorkerRuntime();
  install(worker, 'epoch-a', pair(SESSION_A, 1, 'c'));
  const authority = worker.startTick({ captureAuthority: true });
  for (let i = 0; i < 8; i++) assert.equal(worker.startTick(), false);
  assert.equal(worker.skippedTicks, 8);
  assert.equal(worker.queueDepth, 0);
  worker.finishTick({ nowMonoMs: 0, warnings: [], tickAuthority: authority });
  assert.equal(worker.queueDepth, 0);
});

T('stale boundary is fresh at 1500 ms and silent at 1501 ms', () => {
  const p = pair(SESSION_A, 1, 'd');
  const page = new PageTransportAuthority({ session: SESSION_A });
  page.bind(p);
  assert.equal(page.accept(makeStateEnvelope(p, 1, [warningA]), 0), true);
  assert.equal(page.visibleWarnings(1500).length, 1);
  assert.equal(page.visibleWarnings(1501).length, 0);
});

T('warning clear and warning change publish immediately', () => {
  const worker = new ReferenceWorkerRuntime();
  install(worker, 'epoch-a', pair(SESSION_A, 1, 'e'));
  let a = worker.startTick({ captureAuthority: true });
  assert.ok(worker.finishTick({ nowMonoMs: 0, warnings: [warningA], tickAuthority: a }));
  a = worker.startTick({ captureAuthority: true });
  const clear = worker.finishTick({ nowMonoMs: 1, warnings: [], tickAuthority: a });
  assert.ok(clear);
  assert.equal(clear.warnings.length, 0);
  a = worker.startTick({ captureAuthority: true });
  const changed = worker.finishTick({ nowMonoMs: 2, warnings: [warningB], tickAuthority: a });
  assert.ok(changed);
  assert.equal(changed.warnings[0].ruleId, warningB.ruleId);
});

T('unchanged state heartbeat is bounded at 250 ms', () => {
  const worker = new ReferenceWorkerRuntime();
  install(worker, 'epoch-a', pair(SESSION_A, 1, 'f'));
  let a = worker.startTick({ captureAuthority: true });
  assert.ok(worker.finishTick({ nowMonoMs: 0, warnings: [], tickAuthority: a }));
  a = worker.startTick({ captureAuthority: true });
  assert.equal(worker.finishTick({ nowMonoMs: 249, warnings: [], tickAuthority: a }), null);
  a = worker.startTick({ captureAuthority: true });
  assert.ok(worker.finishTick({ nowMonoMs: 250, warnings: [], tickAuthority: a }));
});

T('pair and session isolation reject old or foreign state', () => {
  const p1 = pair(SESSION_A, 1, '1');
  const p2 = pair(SESSION_A, 2, '2');
  const foreign = pair(SESSION_B, 1, '3');
  const page = new PageTransportAuthority({ session: SESSION_A });
  page.bind(p1);
  assert.equal(page.accept(makeStateEnvelope(foreign, 1, [warningA]), 0), false);
  page.bind(p2);
  assert.equal(page.accept(makeStateEnvelope(p1, 1, [warningA]), 1), false);
  assert.equal(page.visibleWarnings(1).length, 0);
});

T('safety invariants stay exact', () => {
  assert.deepEqual(
    {
      readOnly: SAFETY.readOnly,
      ramWrites: SAFETY.ramWrites,
      inputInjection: SAFETY.inputInjection,
      workerReplacement: SAFETY.workerReplacement,
      blobRewrite: SAFETY.blobRewrite
    },
    { readOnly: true, ramWrites: 0, inputInjection: false, workerReplacement: false, blobRewrite: false }
  );
});

const results = [];
for (const [name, fn] of cases) {
  try {
    await fn();
    results.push({ name, status: 'PASS' });
  } catch (error) {
    results.push({ name, status: 'FAIL', error: String(error?.stack || error) });
  }
}
const passCount = results.filter(x => x.status === 'PASS').length;
const failCount = results.length - passCount;
const summary = {
  schema: 'wof-alpha-transport-stale-generation-fresh-qa-targeted-v1',
  status: failCount === 0 ? 'PASS' : 'FAIL',
  caseCount: results.length,
  passCount,
  failCount,
  results
};
console.log(JSON.stringify(summary));
if (failCount) process.exitCode = 1;
