import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import {
  CONTRACT,
  SAFETY,
  makeStateEnvelope
} from '../ALPHA_TRANSPORT_IMPL/constants.mjs';
import { PageTransportAuthority } from '../ALPHA_TRANSPORT_IMPL/page_authority.mjs';
import { ReferenceTransportRuntime } from '../ALPHA_TRANSPORT_IMPL/reference_runtime.mjs';
import {
  OBSERVER_STATUS_SCHEMA,
  PreparedDiscoveryAdapter,
  PreparedNativeWorkerRuntimeAdapter,
  PreparedPageHudTransportAdapter,
  RuntimeEpochGuard,
  projectPylaunchTargetChoice,
  validateFixedHudOutput
} from './contracts.mjs';
import { verifyDriftBaseline } from './drift_check.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, '../..');
const fixtures = JSON.parse(fs.readFileSync(path.join(here, 'fixtures.json'), 'utf8'));
const require = createRequire(import.meta.url);
const canonicalAlphaCore = require(path.join(repoRoot, 'product/alpha/wof_alpha_core.js'));

const results = [];
async function test(name, fn) {
  try {
    await fn();
    results.push({ name, ok: true });
  } catch (error) {
    results.push({ name, ok: false, error: String(error?.stack || error) });
  }
}

function makePageOps(session) {
  let generation = 0;
  let authority = new PageTransportAuthority({ session });
  return {
    async bind(_pageRef, pairNonce) {
      generation += 1;
      const pair = { session, pairGeneration: generation, pairNonce };
      authority.bind(pair);
      return pair;
    },
    async status() { return authority.status(); },
    async reset() {
      authority = new PageTransportAuthority({ session });
      return { ...authority.status(), reset: true };
    },
    authority: () => authority,
    generation: () => generation
  };
}

function makeNativeOps({ detectorLocalOk = true } = {}) {
  let active = false;
  let runtimeEpoch = null;
  return {
    async launcherIdentityProbe(workerRef) {
      return { runtimeEpoch: workerRef.runtimeEpoch, identity: { ...workerRef.identityAuthority } };
    },
    async detectorLocalIdentityProbe(workerRef) {
      return {
        ok: detectorLocalOk,
        identitySignature: detectorLocalOk ? CONTRACT.identitySignature : 'wrong',
        readOnly: true,
        ramWrites: 0,
        inputInjection: false,
        runtimeEpoch: workerRef.runtimeEpoch
      };
    },
    async installObserver(_workerRef, binding) {
      active = true;
      runtimeEpoch = binding.runtimeEpoch;
      return { active, runtimeEpoch, ...SAFETY };
    },
    async statusObserver() {
      return { schema: OBSERVER_STATUS_SCHEMA, active, runtimeEpoch, agentCount: active ? 1 : 0, ...SAFETY };
    },
    async stopObserver() {
      active = false;
      return { stopped: true, ...SAFETY };
    }
  };
}

function makeDiscoveryOps(choiceName = 'valid', lifecycleName = 'a1', configName = 'a') {
  return {
    async readPageConfig() { return { ...fixtures.pageConfigs[configName] }; },
    async discover() { return JSON.parse(JSON.stringify(fixtures.choices[choiceName])); },
    async lifecycle() { return { ...fixtures.lifecycle[lifecycleName] }; }
  };
}

function makeRuntime({ choiceName = 'valid', lifecycleName = 'a1', detectorLocalOk = true } = {}) {
  const pageOps = makePageOps(fixtures.sessions.a);
  const runtime = new ReferenceTransportRuntime({
    discoveryAdapter: new PreparedDiscoveryAdapter(makeDiscoveryOps(choiceName, lifecycleName, 'a')),
    nativeWorkerAdapter: new PreparedNativeWorkerRuntimeAdapter(makeNativeOps({ detectorLocalOk })),
    pageHudAdapter: new PreparedPageHudTransportAdapter(pageOps),
    canonicalAlphaCore
  });
  return { runtime, pageOps };
}

await test('valid exact pair accepts current Discovery V2 shared/blob Worker without URL gate', async () => {
  const { runtime } = makeRuntime();
  const result = await runtime.bindPage('page-a', { pairNonce: fixtures.nonces.a1 });
  assert.equal(result.ok, true);
  assert.equal(result.worker.workerType, 'shared_worker');
  assert.match(result.worker.workerUrlHint, /^blob:/);
  assert.equal(result.readOnly, true);
  assert.equal(result.ramWrites, 0);
  assert.equal(result.inputInjection, false);
});

await test('wrong World is rejected and gameplay stays fail-open', async () => {
  const { runtime } = makeRuntime({ choiceName: 'wrongWorld' });
  const result = await runtime.bindPage('page-a', { pairNonce: fixtures.nonces.a1 });
  assert.equal(result.ok, false);
  assert.equal(result.warningAuthority, false);
  assert.equal(result.gameplayPlayable, true);
});

await test('missing WASM/heap fails closed for warning authority', async () => {
  const { runtime } = makeRuntime({ choiceName: 'missingHeap' });
  const result = await runtime.bindPage('page-a', { pairNonce: fixtures.nonces.a1 });
  assert.equal(result.ok, false);
  assert.equal(result.warningAuthority, false);
  assert.equal(result.gameplayPlayable, true);
});

await test('unsafe identity cannot cross the adapter boundary', async () => {
  const projected = projectPylaunchTargetChoice(fixtures.choices.unsafe, fixtures.pageConfigs.a, fixtures.lifecycle.a1);
  assert.equal(projected.ok, false);
  assert.equal(projected.warningAuthority, false);
});

await test('stale page generation loses authority immediately', async () => {
  const ops = makePageOps(fixtures.sessions.a);
  const p1 = await ops.bind('page-a', fixtures.nonces.a1);
  assert.equal(ops.authority().accept(makeStateEnvelope(p1, 1, []), 10), true);
  const old = makeStateEnvelope(p1, 2, []);
  const p2 = await ops.bind('page-a', fixtures.nonces.a2);
  assert.equal(p2.pairGeneration, p1.pairGeneration + 1);
  assert.equal(ops.authority().accept(old, 20), false);
  assert.deepEqual(ops.authority().visibleWarnings(20), []);
});

await test('Worker replacement/runtime epoch change revokes the bound runtime', async () => {
  const guard = new RuntimeEpochGuard();
  const p1 = projectPylaunchTargetChoice(fixtures.choices.valid, fixtures.pageConfigs.a, fixtures.lifecycle.a1);
  const p2 = projectPylaunchTargetChoice(fixtures.choices.valid, fixtures.pageConfigs.a, fixtures.lifecycle.a2);
  assert.equal(p1.ok && p2.ok, true);
  assert.equal(guard.observe(p1.lifecycle).changed, false);
  assert.equal(guard.observe(p2.lifecycle).changed, true);
  const { runtime } = makeRuntime();
  assert.equal((await runtime.bindPage('page-a', { pairNonce: fixtures.nonces.a1 })).ok, true);
  const revoked = await runtime.runtimeEpochChanged();
  assert.equal(revoked.ok, false);
  assert.equal(revoked.warningAuthority, false);
  assert.equal(revoked.gameplayPlayable, true);
  assert.equal(runtime.current, null);
});

await test('reconnect/rebind creates a new page generation and old envelope stays rejected', async () => {
  const { runtime, pageOps } = makeRuntime();
  const first = await runtime.bindPage('page-a', { pairNonce: fixtures.nonces.a1 });
  const oldMessage = makeStateEnvelope(first.pair, 1, []);
  const second = await runtime.bindPage('page-a', { pairNonce: fixtures.nonces.a2 });
  assert.equal(second.ok, true);
  assert.equal(second.pair.pairGeneration, first.pair.pairGeneration + 1);
  assert.equal(pageOps.authority().accept(oldMessage, 50), false);
});

await test('cross-tab/session isolation rejects a foreign-session envelope', async () => {
  const a = new PageTransportAuthority({ session: fixtures.sessions.a });
  const b = new PageTransportAuthority({ session: fixtures.sessions.b });
  const pa = { session: fixtures.sessions.a, pairGeneration: 1, pairNonce: fixtures.nonces.a1 };
  const pb = { session: fixtures.sessions.b, pairGeneration: 1, pairNonce: fixtures.nonces.b1 };
  a.bind(pa);
  b.bind(pb);
  assert.equal(b.accept(makeStateEnvelope(pa, 1, []), 0), false);
  assert.deepEqual(b.visibleWarnings(0), []);
});

await test('fixed HUD transport contract remains independent of future anchor placement', async () => {
  const authority = new PageTransportAuthority({ session: fixtures.sessions.a });
  const pair = { session: fixtures.sessions.a, pairGeneration: 1, pairNonce: fixtures.nonces.a1 };
  authority.bind(pair);
  assert.equal(authority.accept(makeStateEnvelope(pair, 1, []), 100), true);
  const output = authority.hudOutput(100);
  assert.equal(validateFixedHudOutput(output).ok, true);
  const placement = { anchorMode: 'player-head', x: 100, y: 200 };
  assert.equal(validateFixedHudOutput(output).ok, true);
  assert.deepEqual(output.warnings, []);
  assert.equal(placement.anchorMode, 'player-head');
});

await test('canonical pinned Alpha core is consumed through the reference detector adapter', async () => {
  assert.equal(canonicalAlphaCore.VERSION, CONTRACT.coreVersion);
  assert.equal(canonicalAlphaCore.SCHEMA, CONTRACT.applicationSchema);
  const { runtime } = makeRuntime();
  const bound = await runtime.bindPage('page-a', { pairNonce: fixtures.nonces.a1 });
  assert.equal(bound.ok, true);
  const detectorState = runtime.detector.evaluate({
    snapshotSchema: CONTRACT.snapshotSchema,
    sampleSeq: 1,
    sampledAtMonoMs: 123,
    pairGeneration: bound.pair.pairGeneration,
    enemies: []
  });
  assert.equal(detectorState.coreVersion, CONTRACT.coreVersion);
  assert.deepEqual(detectorState.warnings, []);
});

await test('existing 67-vector reference acceptance remains the governing semantic baseline', async () => {
  const upstream = JSON.parse(fs.readFileSync(path.join(repoRoot, 'parallel/ALPHA_TRANSPORT_IMPL/result.json'), 'utf8'));
  assert.equal(upstream.status, 'PASS');
  assert.equal(upstream.vectorCount, 67);
  assert.equal(upstream.passCount, 67);
  assert.equal(upstream.failCount, 0);
  assert.equal(upstream.provenance.mockVectorsBlobSha, '5a0cbe2ccfcf7eb6e875552f56748f736722c14d');
  assert.equal(upstream.provenance.canonicalAlphaCoreBlobSha, '267a44190744b6848b0685712c3d5572627d3a8a');
});

await test('current-HEAD drift baseline matches all consumed interfaces', async () => {
  const drift = verifyDriftBaseline();
  assert.equal(drift.ok, true, JSON.stringify(drift.drift));
});

const failCount = results.filter(row => !row.ok).length;
const summary = {
  schema: 'wof-alpha-real-adapter-prep-selftest-v1',
  status: failCount === 0 ? 'PASS' : 'FAIL',
  passCount: results.length - failCount,
  failCount,
  testCount: results.length,
  referenceAcceptance: '67/67 PASS required',
  safety: SAFETY,
  results
};
console.log(JSON.stringify(summary, null, 2));
if (failCount) process.exitCode = 1;
