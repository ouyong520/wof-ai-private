import { strict as assert } from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { AlphaDetectorAdapter } from './detector_adapter.mjs';
import { DiscoveryAdapter, NativeWorkerRuntimeAdapter, PageHudTransportAdapter } from './adapters.mjs';
import { CONTRACT, assertAllowedCdpMethod, validatePageConfig, validateSnapshot } from './constants.mjs';
import { ReferenceTransportRuntime } from './reference_runtime.mjs';

const session = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa';
const nonce = 'cccccccccccccccccccccccccccccccc';
const pageConfig = { release: CONTRACT.release, schema: CONTRACT.applicationSchema, session, channel: `WOF_ALPHA_${session}` };

const tests = [];
function T(name, fn) { tests.push([name, fn]); }

T('page config exact session/channel', () => assert.equal(validatePageConfig(pageConfig).ok, true));
T('wrong channel rejected', () => assert.equal(validatePageConfig({ ...pageConfig, channel: 'wrong' }).ok, false));
T('Input CDP method rejected', () => assert.throws(() => assertAllowedCdpMethod('Input.dispatchKeyEvent')));
T('snapshot forbids history fields', () => assert.equal(validateSnapshot({ snapshotSchema: CONTRACT.snapshotSchema, sampleSeq: 1, sampledAtMonoMs: 1, pairGeneration: 1, enemies: [{ slot: 0, enemyX: 1, targetX: 2, roomId: 3 }] }).ok, false));

const fakeCore = {
  VERSION: CONTRACT.coreVersion,
  SCHEMA: CONTRACT.applicationSchema,
  createEngine() {
    return {
      step(rows, now) { return { sentAt: now, warnings: rows.length ? [] : [] }; },
      reset() {},
      diagnostics() { return { fake: true }; }
    };
  }
};
T('detector adapter accepts canonical interface', () => {
  const d = new AlphaDetectorAdapter(fakeCore);
  const state = d.evaluate({ snapshotSchema: CONTRACT.snapshotSchema, sampleSeq: 1, sampledAtMonoMs: 1, pairGeneration: 1, enemies: [] });
  assert.equal(state.coreVersion, CONTRACT.coreVersion);
});

class D extends DiscoveryAdapter {
  async readPageConfig() { return pageConfig; }
  async listTargets() { return [{ id: 'w1', type: 'worker', url: 'https://game/gstyphoon.a.js', page: 'p1', associationExact: true, moduleOk: true, identityOk: true }]; }
}
class W extends NativeWorkerRuntimeAdapter {
  constructor() { super(); this.count = 0; }
  async launcherIdentityProbe() { return { moduleOk: true, heapOk: true, candidateCount: 1, hashStatus: 'accepted', sha256: CONTRACT.goldenSha256, readOnly: true, ramWrites: 0, inputInjection: false }; }
  async detectorLocalIdentityProbe() { return { ok: true, identitySignature: CONTRACT.identitySignature, readOnly: true, ramWrites: 0, inputInjection: false }; }
  async stopObserver() { this.count = 0; }
  async installObserver() { this.count = 1; }
}
class H extends PageHudTransportAdapter {
  constructor() { super(); this.generation = 0; this.resetCount = 0; }
  async bind(_page, pairNonce) { assert.equal(pairNonce, nonce); return { session, pairGeneration: ++this.generation }; }
  async reset() { this.resetCount += 1; }
  async status() { return {}; }
}
T('orchestrator pairs through injected adapters', async () => {
  const w = new W(), h = new H();
  const runtime = new ReferenceTransportRuntime({ discoveryAdapter: new D(), nativeWorkerAdapter: w, pageHudAdapter: h, canonicalAlphaCore: fakeCore });
  const result = await runtime.bindPage('p1', { pairNonce: nonce });
  assert.equal(result.ok, true); assert.equal(result.ramWrites, 0); assert.equal(w.count, 1);
});
T('orchestrator epoch reset is fail-closed and gameplay-open', async () => {
  const w = new W(), h = new H();
  const runtime = new ReferenceTransportRuntime({ discoveryAdapter: new D(), nativeWorkerAdapter: w, pageHudAdapter: h, canonicalAlphaCore: fakeCore });
  await runtime.bindPage('p1', { pairNonce: nonce });
  const result = await runtime.runtimeEpochChanged();
  assert.equal(result.ok, false); assert.equal(result.gameplayPlayable, true); assert.equal(result.warningAuthority, false); assert.equal(w.count, 0);
});
T('ambiguous discovery fails closed', async () => {
  class DAmb extends D { async listTargets() { return [{ id: 'w1', type: 'worker', url: 'https://game/gstyphoon.a.js', page: null, associationExact: false, moduleOk: true, identityOk: true }]; } }
  const runtime = new ReferenceTransportRuntime({ discoveryAdapter: new DAmb(), nativeWorkerAdapter: new W(), pageHudAdapter: new H(), canonicalAlphaCore: fakeCore });
  const result = await runtime.bindPage('p1', { pairNonce: nonce });
  assert.equal(result.ok, false); assert.equal(result.warningAuthority, false); assert.equal(result.gameplayPlayable, true);
});

let pass = 0;
const failures = [];
for (const [name, fn] of tests) {
  try { await fn(); pass += 1; }
  catch (e) { failures.push({ name, error: String(e?.stack || e) }); }
}
const result = { status: failures.length ? 'FAIL' : 'PASS', passCount: pass, failCount: failures.length, failures };
const here = path.dirname(fileURLToPath(import.meta.url));
fs.writeFileSync(path.join(here, 'selftest_result.json'), JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify(result));
if (failures.length) process.exitCode = 1;
