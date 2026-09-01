import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { webcrypto } from 'node:crypto';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '../..');
const workerPath = path.join(ROOT, 'product/alpha/wof_alpha_real_worker.js');
const adapterPath = path.join(HERE, 'real_adapter.py');
const workerSource = fs.readFileSync(workerPath, 'utf8');
const adapterSource = fs.readFileSync(adapterPath, 'utf8');
const GOLDEN_SHA = '5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62';

const results = [];
async function test(name, fn) {
  try { await fn(); results.push({ name, ok: true }); }
  catch (error) { results.push({ name, ok: false, error: String(error?.stack || error) }); }
}

await test('production source requires detector-local SHA-256', async () => {
  const start = workerSource.indexOf('async function localIdentity');
  const end = workerSource.indexOf('function stableWarningsHash');
  assert.ok(start >= 0 && end > start);
  const block = workerSource.slice(start, end);
  assert.match(block, /scope\.crypto\?\.subtle\?\.digest/);
  assert.match(block, /digest\('SHA-256',logical\)/);
  assert.match(block, /sha256!==GOLDEN_SHA/);
  assert.match(block, /sha256,expectedSha256:GOLDEN_SHA/);
  assert.match(adapterSource, /identity\.get\("sha256"\) != GOLDEN_SHA/);
  assert.match(adapterSource, /"launcherIdentitySha": discovery_identity_sha/);
  assert.doesNotMatch(adapterSource, /"launcherIdentitySha"\s*:\s*GOLDEN_SHA/);
});

await test('same-targetId replacement with golden Discovery assertion fails closed on fresh local hash', async () => {
  const buffer = new ArrayBuffer(0x400000);
  const HEAPU8 = new Uint8Array(buffer);
  const HEAPU32 = new Uint32Array(buffer);
  const put32 = (offset, value) => {
    HEAPU8[offset] = (value >>> 24) & 0xff;
    HEAPU8[offset + 1] = (value >>> 16) & 0xff;
    HEAPU8[offset + 2] = (value >>> 8) & 0xff;
    HEAPU8[offset + 3] = value & 0xff;
  };
  put32(0, 0x00FF62EE);
  put32(4, 0x0000754A);
  const dispatch = [0x06F4E4,0x07494C,0x071ADA,0x077B8E,0x07C6D2];
  dispatch.forEach((value, i) => put32(0x25DC + i * 4, value));

  // Keep the RAM pointer/self-index shape valid so the fresh ROM digest is the
  // decision-changing gate. The ROM bytes are deliberately not World 921031.
  const ramBase = 0x180000;
  HEAPU32[0x2e39e4 >>> 2] = ramBase;
  const writeB = (address, value) => { HEAPU8[ramBase + ((((address - 0xFF0000) & 0xffff) ^ 1))] = value & 0xff; };
  const writeU16 = (address, value) => { writeB(address, value >>> 8); writeB(address + 1, value); };
  writeU16(0xFFBE1C + 0x7C, 0);
  writeU16(0xFFBEFC + 0x7C, 4);
  writeU16(0xFFBFDC + 0x7C, 8);

  const binding = {
    release: 'wof-alpha-rc3', schema: 'wof-alpha-v2', transportVersion: 'wof-alpha-safe-transport-v1',
    session: '1'.repeat(32), channel: 'WOF_ALPHA_' + '1'.repeat(32), pairGeneration: 7,
    pairNonce: '2'.repeat(32), runtimeEpoch: '3'.repeat(32), launcherIdentitySha: GOLDEN_SHA,
  };
  class BroadcastChannelStub { postMessage() {} close() {} }
  const workerScope = {
    __WOF_ALPHA_REAL_ADAPTER_BINDING: binding,
    _0x515056: { HEAPU8, HEAPU32 },
    WOFAlphaCore: { VERSION: 'wof-alpha-core-rc3', SCHEMA: 'wof-alpha-v2', createEngine() { return { step() { return { warnings: [] }; }, reset() {} }; } },
    BroadcastChannel: BroadcastChannelStub,
    performance: { now: () => 1000 },
    crypto: webcrypto,
  };
  const moduleBox = { exports: {} };
  const context = {
    module: moduleBox, exports: moduleBox.exports, self: workerScope,
    Uint8Array, Uint32Array, Set, Promise, Date, console, setInterval() { return 1; }, clearInterval() {}, setTimeout, clearTimeout,
  };
  vm.createContext(context);
  vm.runInContext(workerSource, context, { filename: workerPath });
  for (let i = 0; i < 120 && workerScope.__WOF_ALPHA_REAL_TRANSPORT?.running !== false; i++) {
    await new Promise(resolve => setImmediate(resolve));
  }
  const failed = workerScope.__WOF_ALPHA_REAL_TRANSPORT;
  assert.ok(failed, 'worker install did not publish fail-closed status');
  assert.equal(failed.running, false);
  assert.match(String(failed.lastError || ''), /World 921031|SHA-256|身份校验失败/);
  assert.equal(failed.readOnly, true);
  assert.equal(failed.ramWrites, 0);
  assert.equal(failed.inputInjection, false);
  assert.equal(failed.workerReplacement, false);
});

const failures = results.filter(x => !x.ok);
console.log(JSON.stringify({
  schema: 'wof-alpha-detector-local-identity-tocou-regression-v1',
  status: failures.length ? 'FAIL' : 'PASS',
  testCount: results.length,
  passCount: results.length - failures.length,
  failCount: failures.length,
  sameTargetIdRuntimeReplacementFailsClosed: failures.length === 0,
  results
}, null, 2));
if (failures.length) process.exitCode = 1;
