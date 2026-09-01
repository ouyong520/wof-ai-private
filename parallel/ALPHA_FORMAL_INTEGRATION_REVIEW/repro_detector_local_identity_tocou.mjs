import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '../..');
const workerPath = path.join(ROOT, 'product/alpha/wof_alpha_real_worker.js');
const adapterPath = path.join(ROOT, 'parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/real_adapter.py');
const workerSource = fs.readFileSync(workerPath, 'utf8');
const adapterSource = fs.readFileSync(adapterPath, 'utf8');

const GOLDEN_SHA = '5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62';
const IDENTITY_SIGNATURE = 'wof-world-921031-maincpu-sha256-v1:5c369ce2de4f53d8';

// Guard the exact vulnerable current-head shape. If implementation is fixed,
// this fixture should stop reproducing and therefore fail these assertions.
const localStart = workerSource.indexOf('function localIdentity');
const localEnd = workerSource.indexOf('function stableWarningsHash');
assert.ok(localStart >= 0 && localEnd > localStart, 'localIdentity block not found');
const localBlock = workerSource.slice(localStart, localEnd);
assert.match(localBlock, /binding\.launcherIdentitySha!==GOLDEN_SHA/);
assert.doesNotMatch(localBlock, /subtle\.digest|ROM_IDENTITY|hashLogicalProgram|sha256\s*:/i);
assert.match(adapterSource, /"launcherIdentitySha"\s*:\s*GOLDEN_SHA/);

// Build a Worker heap with only the RAM pointer and P1/P2/P3 self-index shape
// expected by localIdentity(). There is deliberately no World 921031 ROM image
// and no fresh ROM SHA-256 evidence anywhere in this runtime.
const buffer = new ArrayBuffer(0x400000);
const HEAPU8 = new Uint8Array(buffer);
const HEAPU32 = new Uint32Array(buffer);
const ramBase = 0x100000;
HEAPU32[0x2e39e4 >>> 2] = ramBase;

const writeB = (address, value) => {
  const offset = ((address - 0xFF0000) & 0xffff) ^ 1;
  HEAPU8[ramBase + offset] = value & 0xff;
};
const writeU16 = (address, value) => {
  writeB(address, value >>> 8);
  writeB(address + 1, value);
};
writeU16(0xFFBE1C + 0x7C, 0);
writeU16(0xFFBEFC + 0x7C, 4);
writeU16(0xFFBFDC + 0x7C, 8);

const messages = [];
class BroadcastChannelStub {
  constructor(name) { this.name = name; }
  postMessage(message) { messages.push(message); }
  close() {}
}

const binding = {
  release: 'wof-alpha-rc3',
  schema: 'wof-alpha-v2',
  transportVersion: 'wof-alpha-safe-transport-v1',
  session: '1'.repeat(32),
  channel: 'WOF_ALPHA_' + '1'.repeat(32),
  pairGeneration: 7,
  pairNonce: '2'.repeat(32),
  runtimeEpoch: '3'.repeat(32),
  // This is the stale launcher-side assertion the adapter injects as a constant.
  launcherIdentitySha: GOLDEN_SHA,
};

const workerScope = {
  __WOF_ALPHA_REAL_ADAPTER_BINDING: binding,
  _0x515056: { HEAPU8, HEAPU32 },
  WOFAlphaCore: {
    VERSION: 'wof-alpha-core-rc3',
    SCHEMA: 'wof-alpha-v2',
    createEngine() {
      return {
        step() { return { warnings: [] }; },
        reset() {},
      };
    },
  },
  BroadcastChannel: BroadcastChannelStub,
  performance: { now: () => 1000 },
};

const moduleBox = { exports: {} };
const context = {
  module: moduleBox,
  exports: moduleBox.exports,
  self: workerScope,
  Uint8Array,
  Uint32Array,
  Promise,
  Date,
  console,
  setInterval() { return 1; },
  clearInterval() {},
  setTimeout,
  clearTimeout,
};
vm.createContext(context);
vm.runInContext(workerSource, context, { filename: workerPath });

for (let i = 0; i < 20 && !workerScope.__WOF_ALPHA_REAL_TRANSPORT?.status; i++) {
  await new Promise(resolve => setImmediate(resolve));
}

const runtime = workerScope.__WOF_ALPHA_REAL_TRANSPORT;
assert.ok(runtime && typeof runtime.status === 'function', 'observer did not install');
const status = runtime.status();

// The blocker: an arbitrary/non-921031 runtime is admitted as exact identity
// without computing a detector-local ROM SHA-256.
assert.equal(status.running, true);
assert.equal(status.identity?.ok, true);
assert.equal(status.identitySignature, IDENTITY_SIGNATURE);
assert.equal(Object.prototype.hasOwnProperty.call(status.identity || {}, 'sha256'), false);
assert.equal(status.readOnly, true);
assert.equal(status.ramWrites, 0);
assert.equal(status.inputInjection, false);

runtime.stop('repro-complete');

console.log(JSON.stringify({
  schema: 'wof-alpha-formal-integration-adversarial-repro-v1',
  status: 'BLOCKER_REPRODUCED',
  severity: 'P1',
  finding: 'detector-local exact World identity is not freshly verified at observer install',
  unsupportedRuntimeAccepted: true,
  freshDetectorLocalRomSha256Present: false,
  reportedIdentitySignature: status.identitySignature,
  launcherIdentityBindingIsConstantGoldenSha: true,
  readOnly: status.readOnly,
  ramWrites: status.ramWrites,
  inputInjection: status.inputInjection,
}, null, 2));
