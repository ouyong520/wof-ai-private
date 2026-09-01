import { strict as assert } from 'node:assert';
import { CONTRACT } from '../ALPHA_TRANSPORT_IMPL/constants.mjs';
import { PageTransportAuthority } from '../ALPHA_TRANSPORT_IMPL/page_authority.mjs';
import { ReferenceWorkerRuntime } from '../ALPHA_TRANSPORT_IMPL/worker_runtime.mjs';

const session = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa';
const pair1 = {
  session,
  pairGeneration: 1,
  pairNonce: '11111111111111111111111111111111'
};
const pair2 = {
  session,
  pairGeneration: 2,
  pairNonce: '22222222222222222222222222222222'
};
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
const staleOldGenerationWarning = {
  ruleId: CONTRACT.allowedRuleIds[0],
  slot: 0,
  publication: 'hold-only-current-level',
  evidence: 'fresh-current-sample'
};

const worker = new ReferenceWorkerRuntime();
const page = new PageTransportAuthority({ session });

assert.equal(worker.install({
  runtimeEpoch: 'epoch-1',
  pair: pair1,
  launcherIdentityProbe,
  detectorLocalIdentityOk: true
}), true);
page.bind(pair1);

// Old-generation detector work is now in flight.
assert.equal(worker.startTick(), true);

// Rebind/reinstall revokes pair1 and establishes pair2 while the old async work
// is still unresolved. stop()/install() clears only the shared inFlight boolean;
// it does not give the outstanding completion a generation/epoch token.
assert.equal(worker.install({
  runtimeEpoch: 'epoch-2',
  pair: pair2,
  launcherIdentityProbe,
  detectorLocalIdentityOk: true
}), true);
page.bind(pair2);

// A legitimate pair2 tick begins.
assert.equal(worker.startTick(), true);

// Model the late completion callback from the old pair1 tick. finishTick has no
// token/epoch/pair argument, so it consumes the current inFlight slot and stamps
// the stale result with worker.pair, which is already pair2.
const leaked = worker.finishTick({
  nowMonoMs: 10,
  warnings: [staleOldGenerationWarning]
});
const acceptedByNewPair = page.accept(leaked, 10);

let freshCompletionError = null;
try {
  worker.finishTick({ nowMonoMs: 11, warnings: [] });
} catch (error) {
  freshCompletionError = String(error?.message || error);
}

const result = {
  schema: 'wof-alpha-transport-reference-independent-qa-v1',
  status: acceptedByNewPair ? 'FAIL' : 'PASS',
  case: 'stale-inflight-completion-after-rebind',
  expected: {
    staleOldGenerationCompletionAcceptedByPair2: false,
    visibleWarningsOnPair2: 0
  },
  observed: {
    leakedPairGeneration: leaked?.pairGeneration ?? null,
    leakedPairNonce: leaked?.pairNonce ?? null,
    acceptedByNewPair,
    visibleWarningsOnPair2: page.visibleWarnings(10).length,
    workerInFlightAfterStaleCompletion: worker.inFlight,
    freshCompletionError
  },
  safety: {
    readOnly: leaked?.readOnly ?? null,
    ramWrites: leaked?.ramWrites ?? null,
    inputInjection: leaked?.inputInjection ?? null
  }
};

console.log(JSON.stringify(result, null, 2));
if (result.status === 'FAIL') process.exitCode = 1;
