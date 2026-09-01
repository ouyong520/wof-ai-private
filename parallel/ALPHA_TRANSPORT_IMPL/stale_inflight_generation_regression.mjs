import { strict as assert } from 'node:assert';
import { CONTRACT } from './constants.mjs';
import { PageTransportAuthority } from './page_authority.mjs';
import { ReferenceWorkerRuntime } from './worker_runtime.mjs';

const session = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa';
const launcherIdentityProbe = {
  moduleOk: true,
  heapOk: true,
  candidateCount: 1,
  hashStatus: 'accepted',
  sha256: CONTRACT.goldenSha256,
  readOnly: true,
  ramWrites: 0,
  inputInjection: false
};

function pair(pairGeneration, digit) {
  return {
    session,
    pairGeneration,
    pairNonce: String(digit).repeat(32)
  };
}

function install(worker, runtimeEpoch, authorityPair) {
  assert.equal(worker.install({
    runtimeEpoch,
    pair: authorityPair,
    launcherIdentityProbe,
    detectorLocalIdentityOk: true
  }), true);
}

const warning = {
  ruleId: CONTRACT.allowedRuleIds[0],
  slot: 0,
  publication: 'hold-only-current-level',
  evidence: 'fresh-current-sample'
};

const cases = [];
function T(name, fn) { cases.push([name, fn]); }

T('rebind revokes old generation without consuming new in-flight slot', () => {
  const worker = new ReferenceWorkerRuntime();
  const page = new PageTransportAuthority({ session });
  const pair1 = pair(1, 1);
  const pair2 = pair(2, 2);

  install(worker, 'epoch-a', pair1);
  page.bind(pair1);
  const staleAuthority = worker.startTick({ captureAuthority: true });
  assert.equal(staleAuthority.pairGeneration, 1);
  assert.equal(Object.isFrozen(staleAuthority), true);

  install(worker, 'epoch-a', pair2);
  page.bind(pair2);
  const freshAuthority = worker.startTick({ captureAuthority: true });
  assert.equal(freshAuthority.pairGeneration, 2);

  const staleMessage = worker.finishTick({
    nowMonoMs: 10,
    warnings: [warning],
    tickAuthority: staleAuthority
  });
  assert.equal(staleMessage, null);
  assert.equal(worker.inFlight, true);
  assert.equal(worker.inFlightAuthority.tickAuthorityId, freshAuthority.tickAuthorityId);
  assert.equal(page.visibleWarnings(10).length, 0);

  const freshMessage = worker.finishTick({
    nowMonoMs: 11,
    warnings: [],
    tickAuthority: freshAuthority
  });
  assert.equal(freshMessage.pairGeneration, 2);
  assert.equal(freshMessage.pairNonce, pair2.pairNonce);
  assert.equal(page.accept(freshMessage, 11), true);
  assert.equal(worker.inFlight, false);
});

T('runtime epoch replacement revokes old tick authority immediately', () => {
  const worker = new ReferenceWorkerRuntime();
  const page = new PageTransportAuthority({ session });
  const pair1 = pair(1, 3);
  const pair2 = pair(2, 4);

  install(worker, 'epoch-a', pair1);
  page.bind(pair1);
  const staleAuthority = worker.startTick({ captureAuthority: true });

  assert.equal(worker.runtimeEpochChanged('epoch-b'), true);
  install(worker, 'epoch-b', pair2);
  page.bind(pair2);
  const freshAuthority = worker.startTick({ captureAuthority: true });

  assert.equal(worker.finishTick({
    nowMonoMs: 20,
    warnings: [warning],
    tickAuthority: staleAuthority
  }), null);
  assert.equal(worker.inFlight, true);

  const freshMessage = worker.finishTick({
    nowMonoMs: 21,
    warnings: [warning],
    tickAuthority: freshAuthority
  });
  assert.equal(page.accept(freshMessage, 21), true);
  assert.equal(page.visibleWarnings(21).length, 1);
});

T('worker replacement cannot lend new worker authority to old completion', () => {
  const page = new PageTransportAuthority({ session });
  const pair1 = pair(1, 5);
  const pair2 = pair(2, 6);
  const oldWorker = new ReferenceWorkerRuntime();

  install(oldWorker, 'epoch-a', pair1);
  page.bind(pair1);
  const staleAuthority = oldWorker.startTick({ captureAuthority: true });
  oldWorker.stop('worker-replaced');

  const newWorker = new ReferenceWorkerRuntime();
  install(newWorker, 'epoch-b', pair2);
  page.bind(pair2);
  const freshAuthority = newWorker.startTick({ captureAuthority: true });

  assert.equal(oldWorker.finishTick({
    nowMonoMs: 30,
    warnings: [warning],
    tickAuthority: staleAuthority
  }), null);
  assert.equal(newWorker.inFlight, true);

  const freshMessage = newWorker.finishTick({
    nowMonoMs: 31,
    warnings: [],
    tickAuthority: freshAuthority
  });
  assert.equal(page.accept(freshMessage, 31), true);
  assert.equal(newWorker.inFlight, false);
});

T('ambiguous legacy completion fails closed after unresolved rebind', () => {
  const worker = new ReferenceWorkerRuntime();
  const pair1 = pair(1, 7);
  const pair2 = pair(2, 8);

  install(worker, 'epoch-a', pair1);
  assert.equal(worker.startTick(), true);
  install(worker, 'epoch-a', pair2);
  const freshAuthority = worker.startTick({ captureAuthority: true });

  assert.equal(worker.finishTick({ nowMonoMs: 40, warnings: [warning] }), null);
  assert.equal(worker.inFlight, true);
  assert.equal(worker.inFlightAuthority.tickAuthorityId, freshAuthority.tickAuthorityId);

  const freshMessage = worker.finishTick({
    nowMonoMs: 41,
    warnings: [],
    tickAuthority: freshAuthority
  });
  assert.equal(freshMessage.pairGeneration, 2);
  assert.equal(worker.inFlight, false);
});

T('one in-flight tick remains bounded with no catch-up queue', () => {
  const worker = new ReferenceWorkerRuntime();
  install(worker, 'epoch-a', pair(1, 9));
  const authority = worker.startTick({ captureAuthority: true });
  assert.ok(authority);
  assert.equal(worker.startTick(), false);
  assert.equal(worker.skippedTicks, 1);
  assert.equal(worker.queueDepth, 0);
  worker.finishTick({ nowMonoMs: 50, warnings: [], tickAuthority: authority });
  assert.equal(worker.queueDepth, 0);
});

let passCount = 0;
const failures = [];
for (const [name, fn] of cases) {
  try {
    fn();
    passCount += 1;
  } catch (error) {
    failures.push({ name, error: String(error?.stack || error) });
  }
}

const result = {
  schema: 'wof-alpha-transport-stale-inflight-generation-regression-v1',
  status: failures.length ? 'FAIL' : 'PASS',
  passCount,
  failCount: failures.length,
  failures
};
console.log(JSON.stringify(result, null, 2));
if (failures.length) process.exitCode = 1;
