import { strict as assert } from 'node:assert';
import crypto from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

import { CONTRACT, SAFETY, makeStateEnvelope } from '../ALPHA_TRANSPORT_IMPL/constants.mjs';
import { PageTransportAuthority } from '../ALPHA_TRANSPORT_IMPL/page_authority.mjs';
import { ReferenceWorkerRuntime } from '../ALPHA_TRANSPORT_IMPL/worker_runtime.mjs';

const STAGE_ID = 'ALPHA_TRANSPORT_TRUE_5H_ENDURANCE_V1';
const here = path.dirname(fileURLToPath(import.meta.url));
const parallelDir = path.resolve(here, '..');
const implDir = path.join(parallelDir, 'ALPHA_TRANSPORT_IMPL');
const mockDir = path.join(parallelDir, 'ALPHA_TRANSPORT_MOCK');

const EXPECTED_BLOBS = Object.freeze({
  'ALPHA_TRANSPORT_IMPL/constants.mjs': 'a29cb3ad714598e2e6aeeed64acc9e3eca8b221e',
  'ALPHA_TRANSPORT_IMPL/page_authority.mjs': '5e53bd2ad40823a8768802df0a1c5431adb19ee9',
  'ALPHA_TRANSPORT_IMPL/worker_runtime.mjs': 'c353b4500640e31950cde42173a934d541f22531',
  'ALPHA_TRANSPORT_IMPL/acceptance_adapter.mjs': 'd79dff0b2708c671ab8a11644fcc4f771ec75003',
  'ALPHA_TRANSPORT_MOCK/fixtures.json': '35bf36b4c741cda5d94be3f9884511a86653c11f',
  'ALPHA_TRANSPORT_MOCK/vectors.json': '5a0cbe2ccfcf7eb6e875552f56748f736722c14d',
  'ALPHA_TRANSPORT_MOCK/expected_results.json': '1231e0946d18068284724d92e732ea185e4e6af8'
});

const identity = Object.freeze({
  moduleOk: true,
  heapOk: true,
  candidateCount: 1,
  hashStatus: 'accepted',
  sha256: CONTRACT.goldenSha256,
  readOnly: true,
  ramWrites: 0,
  inputInjection: false
});

function hashHex(text) {
  return crypto.createHash('sha256').update(String(text)).digest('hex');
}
function hex32(text) {
  return hashHex(text).slice(0, 32);
}
function rngFor(seedKey) {
  let state = Number.parseInt(hashHex(seedKey).slice(0, 8), 16) >>> 0;
  return () => {
    state ^= state << 13;
    state ^= state >>> 17;
    state ^= state << 5;
    return (state >>> 0) / 0x100000000;
  };
}
function int(rng, max) {
  return Math.floor(rng() * max);
}
function session(seedKey, suffix) {
  return hex32(`${seedKey}:session:${suffix}`);
}
function pair(seedKey, s, generation, suffix) {
  return { session: s, pairGeneration: generation, pairNonce: hex32(`${seedKey}:nonce:${suffix}`) };
}
function warning(seedKey, which = 0) {
  const rng = rngFor(`${seedKey}:warning:${which}`);
  const ruleIndex = int(rng, CONTRACT.allowedRuleIds.length);
  return {
    ruleId: CONTRACT.allowedRuleIds[ruleIndex],
    slot: int(rng, CONTRACT.maxEnemyRows),
    target7E: int(rng, 8),
    sourceSide: which % 2 === 0 ? 'RIGHT' : 'LEFT',
    threatSide: which % 2 === 0 ? 'LEFT' : 'RIGHT',
    attack: 5000 + int(rng, 1000),
    publication: 'hold-only-current-level',
    evidence: 'fresh-current-sample'
  };
}
function install(worker, epoch, p, probe = identity, detectorLocalIdentityOk = true) {
  return worker.install({
    runtimeEpoch: epoch,
    pair: p,
    launcherIdentityProbe: probe,
    detectorLocalIdentityOk
  });
}
function assertSafety(...workers) {
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
  for (const worker of workers) {
    if (!worker) continue;
    const safety = worker.safetyStatus();
    assert.equal(safety.readOnly, true);
    assert.equal(safety.ramWrites, 0);
    assert.equal(safety.inputInjection, false);
    assert.equal(safety.workerReplacement, false);
    assert.equal(safety.blobRewrite, false);
    assert.equal(safety.queueDepth, 0);
  }
}
function relFile(key) {
  const [area, ...rest] = key.split('/');
  return path.join(parallelDir, area, ...rest);
}
function gitBlobSha(filePath) {
  const body = fs.readFileSync(filePath);
  const header = Buffer.from(`blob ${body.length}\0`);
  return crypto.createHash('sha1').update(header).update(body).digest('hex');
}
function assertPinnedSnapshot() {
  const observedBlobShas = {};
  for (const [key, expected] of Object.entries(EXPECTED_BLOBS)) {
    const observed = gitBlobSha(relFile(key));
    observedBlobShas[key] = observed;
    assert.equal(observed, expected, `SUT/input snapshot invalidated: ${key}`);
  }
  return observedBlobShas;
}
function lastJsonLine(text) {
  const lines = String(text).split(/\r?\n/).filter(Boolean);
  return JSON.parse(lines.at(-1));
}
function runFrozenCatalog() {
  const tmpRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'wof-alpha-true-endurance-'));
  try {
    const tmpImpl = path.join(tmpRoot, 'ALPHA_TRANSPORT_IMPL');
    const tmpMock = path.join(tmpRoot, 'ALPHA_TRANSPORT_MOCK');
    fs.mkdirSync(tmpImpl, { recursive: true });
    fs.mkdirSync(tmpMock, { recursive: true });
    for (const name of ['constants.mjs', 'page_authority.mjs', 'worker_runtime.mjs', 'acceptance_adapter.mjs']) {
      fs.copyFileSync(path.join(implDir, name), path.join(tmpImpl, name));
    }
    for (const name of ['fixtures.json', 'vectors.json', 'expected_results.json']) {
      fs.copyFileSync(path.join(mockDir, name), path.join(tmpMock, name));
    }
    const run = spawnSync(process.execPath, [path.join(tmpImpl, 'acceptance_adapter.mjs')], {
      cwd: tmpImpl,
      env: { ...process.env, WOF_ALPHA_TRANSPORT_MOCK_DIR: tmpMock },
      encoding: 'utf8'
    });
    if (run.status !== 0) {
      throw new Error(`frozen 67-vector catalog failed: ${run.stderr || run.stdout}`);
    }
    const consoleResult = lastJsonLine(run.stdout);
    const result = JSON.parse(fs.readFileSync(path.join(tmpImpl, 'result.json'), 'utf8'));
    assert.equal(consoleResult.status, 'PASS');
    assert.equal(result.status, 'PASS');
    assert.equal(result.vectorCount, 67);
    assert.equal(result.passCount, 67);
    assert.equal(result.failCount, 0);
    assertSafety();
    return {
      status: 'PASS',
      vectorCount: result.vectorCount,
      passCount: result.passCount,
      failCount: result.failCount
    };
  } finally {
    fs.rmSync(tmpRoot, { recursive: true, force: true });
  }
}

function staleRebind(seedKey) {
  const s = session(seedKey, 'a');
  const p1 = pair(seedKey, s, 1, 'p1');
  const p2 = pair(seedKey, s, 2, 'p2');
  const worker = new ReferenceWorkerRuntime();
  const page = new PageTransportAuthority({ session: s });
  assert.equal(install(worker, 'epoch-a', p1), true);
  page.bind(p1);
  const oldAuthority = worker.startTick({ captureAuthority: true });
  assert.equal(install(worker, 'epoch-a', p2), true);
  page.bind(p2);
  const freshAuthority = worker.startTick({ captureAuthority: true });
  assert.equal(worker.finishTick({ nowMonoMs: 10, warnings: [warning(seedKey, 0)], tickAuthority: oldAuthority }), null);
  assert.equal(worker.inFlightAuthority.tickAuthorityId, freshAuthority.tickAuthorityId);
  const fresh = worker.finishTick({ nowMonoMs: 11, warnings: [warning(seedKey, 1)], tickAuthority: freshAuthority });
  assert.ok(fresh);
  assert.equal(page.accept(fresh, 11), true);
  assertSafety(worker);
}

function sessionChange(seedKey) {
  const a = session(seedKey, 'a');
  const b = session(seedKey, 'b');
  const pA = pair(seedKey, a, 1, 'a');
  const pB = pair(seedKey, b, 1, 'b');
  const worker = new ReferenceWorkerRuntime();
  assert.equal(install(worker, 'epoch-a', pA), true);
  const oldAuthority = worker.startTick({ captureAuthority: true });
  assert.equal(install(worker, 'epoch-a', pB), true);
  const freshAuthority = worker.startTick({ captureAuthority: true });
  assert.equal(worker.finishTick({ nowMonoMs: 20, warnings: [warning(seedKey, 0)], tickAuthority: oldAuthority }), null);
  const fresh = worker.finishTick({ nowMonoMs: 21, warnings: [], tickAuthority: freshAuthority });
  assert.ok(fresh);
  const page = new PageTransportAuthority({ session: b });
  page.bind(pB);
  assert.equal(page.accept(fresh, 21), true);
  assertSafety(worker);
}

function pairGenerationNonceChurn(seedKey) {
  const s = session(seedKey, 'churn');
  const worker = new ReferenceWorkerRuntime();
  const page = new PageTransportAuthority({ session: s });
  let previousMessage = null;
  for (let generation = 1; generation <= 4; generation++) {
    const p = pair(seedKey, s, generation, `g${generation}`);
    assert.equal(install(worker, `epoch-${generation}`, p), true);
    page.bind(p);
    if (previousMessage) assert.equal(page.accept(previousMessage, generation * 10), false);
    const authority = worker.startTick({ captureAuthority: true });
    const message = worker.finishTick({
      nowMonoMs: generation * 10 + 1,
      warnings: generation % 2 ? [warning(seedKey, generation)] : [],
      tickAuthority: authority
    });
    assert.ok(message);
    assert.equal(page.accept(message, generation * 10 + 1), true);
    previousMessage = message;
  }
  assertSafety(worker);
}

function runtimeEpochReset(seedKey) {
  const s = session(seedKey, 'epoch');
  const p1 = pair(seedKey, s, 1, 'old');
  const p2 = pair(seedKey, s, 2, 'new');
  const worker = new ReferenceWorkerRuntime();
  assert.equal(install(worker, 'epoch-a', p1), true);
  const oldAuthority = worker.startTick({ captureAuthority: true });
  assert.equal(worker.runtimeEpochChanged('epoch-b'), true);
  assert.equal(install(worker, 'epoch-b', p2), true);
  const freshAuthority = worker.startTick({ captureAuthority: true });
  assert.equal(worker.finishTick({ nowMonoMs: 30, warnings: [warning(seedKey)], tickAuthority: oldAuthority }), null);
  assert.ok(worker.finishTick({ nowMonoMs: 31, warnings: [], tickAuthority: freshAuthority }));
  assertSafety(worker);
}

function workerReplacementReinstall(seedKey) {
  const s = session(seedKey, 'worker');
  const p1 = pair(seedKey, s, 1, 'old');
  const p2 = pair(seedKey, s, 2, 'new');
  const oldWorker = new ReferenceWorkerRuntime();
  assert.equal(install(oldWorker, 'epoch-a', p1), true);
  const oldAuthority = oldWorker.startTick({ captureAuthority: true });
  oldWorker.stop('worker-replaced');
  const newWorker = new ReferenceWorkerRuntime();
  assert.equal(install(newWorker, 'epoch-b', p2), true);
  const freshAuthority = newWorker.startTick({ captureAuthority: true });
  assert.equal(oldWorker.finishTick({ nowMonoMs: 40, warnings: [warning(seedKey)], tickAuthority: oldAuthority }), null);
  assert.ok(newWorker.finishTick({ nowMonoMs: 41, warnings: [], tickAuthority: freshAuthority }));
  assertSafety(oldWorker, newWorker);
}

function disconnectReconnect(seedKey) {
  const s = session(seedKey, 'disconnect');
  const p = pair(seedKey, s, 1, 'pair');
  const worker = new ReferenceWorkerRuntime();
  const page1 = new PageTransportAuthority({ session: s });
  assert.equal(install(worker, 'epoch-a', p), true);
  page1.bind(p);
  let authority = worker.startTick({ captureAuthority: true });
  let message = worker.finishTick({ nowMonoMs: 0, warnings: [warning(seedKey)], tickAuthority: authority });
  assert.ok(message);
  assert.equal(page1.accept(message, 0), true);
  const disconnected = worker.disconnectCdp();
  assert.equal(disconnected.gameplayPlayable, true);
  assert.equal(disconnected.agentMayRemain, true);
  const page2 = new PageTransportAuthority({ session: s });
  page2.bind(p);
  authority = worker.startTick({ captureAuthority: true });
  message = worker.finishTick({ nowMonoMs: CONTRACT.heartbeatMaxMs, warnings: [warning(seedKey)], tickAuthority: authority });
  assert.ok(message);
  assert.equal(page2.accept(message, CONTRACT.heartbeatMaxMs), true);
  assertSafety(worker);
}

function staleWarningBoundary(seedKey) {
  const s = session(seedKey, 'stale');
  const p = pair(seedKey, s, 1, 'pair');
  const page = new PageTransportAuthority({ session: s });
  page.bind(p);
  const base = int(rngFor(seedKey), 10_000);
  assert.equal(page.accept(makeStateEnvelope(p, 1, [warning(seedKey)]), base), true);
  assert.equal(page.visibleWarnings(base + CONTRACT.staleMs).length, 1);
  assert.equal(page.visibleWarnings(base + CONTRACT.staleMs + 1).length, 0);
  assertSafety();
}

function warningClearChange(seedKey) {
  const s = session(seedKey, 'warning');
  const p = pair(seedKey, s, 1, 'pair');
  const worker = new ReferenceWorkerRuntime();
  const page = new PageTransportAuthority({ session: s });
  assert.equal(install(worker, 'epoch-a', p), true);
  page.bind(p);
  let authority = worker.startTick({ captureAuthority: true });
  let message = worker.finishTick({ nowMonoMs: 0, warnings: [warning(seedKey, 0)], tickAuthority: authority });
  assert.ok(message);
  assert.equal(page.accept(message, 0), true);
  authority = worker.startTick({ captureAuthority: true });
  message = worker.finishTick({ nowMonoMs: 1, warnings: [], tickAuthority: authority });
  assert.ok(message);
  assert.equal(page.accept(message, 1), true);
  assert.equal(page.visibleWarnings(1).length, 0);
  authority = worker.startTick({ captureAuthority: true });
  message = worker.finishTick({ nowMonoMs: 2, warnings: [warning(seedKey, 1)], tickAuthority: authority });
  assert.ok(message);
  assert.equal(page.accept(message, 2), true);
  assert.equal(page.visibleWarnings(2).length, 1);
  assertSafety(worker);
}

function heartbeatVariation(seedKey) {
  const s = session(seedKey, 'heartbeat');
  const p = pair(seedKey, s, 1, 'pair');
  const worker = new ReferenceWorkerRuntime();
  assert.equal(install(worker, 'epoch-a', p), true);
  const w = [warning(seedKey)];
  let authority = worker.startTick({ captureAuthority: true });
  assert.ok(worker.finishTick({ nowMonoMs: 0, warnings: w, tickAuthority: authority }));
  const early = 1 + int(rngFor(seedKey), CONTRACT.heartbeatMaxMs - 1);
  authority = worker.startTick({ captureAuthority: true });
  assert.equal(worker.finishTick({ nowMonoMs: early, warnings: w, tickAuthority: authority }), null);
  authority = worker.startTick({ captureAuthority: true });
  assert.ok(worker.finishTick({ nowMonoMs: CONTRACT.heartbeatMaxMs + int(rngFor(`${seedKey}:late`), 200), warnings: w, tickAuthority: authority }));
  assertSafety(worker);
}

function skippedTickPressure(seedKey) {
  const s = session(seedKey, 'skip');
  const p = pair(seedKey, s, 1, 'pair');
  const worker = new ReferenceWorkerRuntime();
  assert.equal(install(worker, 'epoch-a', p), true);
  const authority = worker.startTick({ captureAuthority: true });
  const attempts = 1 + int(rngFor(seedKey), 20);
  for (let i = 0; i < attempts; i++) assert.equal(worker.startTick(), false);
  assert.equal(worker.skippedTicks, attempts);
  assert.equal(worker.queueDepth, 0);
  assert.ok(worker.finishTick({ nowMonoMs: 0, warnings: [], tickAuthority: authority }));
  assert.equal(worker.queueDepth, 0);
  assertSafety(worker);
}

function unsupportedSupportedTransitions(seedKey) {
  const s = session(seedKey, 'support');
  const p1 = pair(seedKey, s, 1, 'bad');
  const p2 = pair(seedKey, s, 2, 'good');
  const worker = new ReferenceWorkerRuntime();
  const badIdentity = { ...identity, moduleOk: false };
  assert.equal(install(worker, 'epoch-a', p1, badIdentity, true), false);
  assert.equal(worker.startTick(), false);
  assert.equal(install(worker, 'epoch-b', p2, identity, true), true);
  const authority = worker.startTick({ captureAuthority: true });
  assert.ok(worker.finishTick({ nowMonoMs: 0, warnings: [warning(seedKey)], tickAuthority: authority }));
  assertSafety(worker);
}

function outOfOrderCompletions(seedKey) {
  const s = session(seedKey, 'ooo');
  const worker = new ReferenceWorkerRuntime();
  const p1 = pair(seedKey, s, 1, 'p1');
  const p2 = pair(seedKey, s, 2, 'p2');
  const p3 = pair(seedKey, s, 3, 'p3');
  assert.equal(install(worker, 'epoch-a', p1), true);
  const a1 = worker.startTick({ captureAuthority: true });
  assert.equal(install(worker, 'epoch-a', p2), true);
  const a2 = worker.startTick({ captureAuthority: true });
  assert.equal(install(worker, 'epoch-a', p3), true);
  const a3 = worker.startTick({ captureAuthority: true });
  assert.equal(worker.finishTick({ nowMonoMs: 1, warnings: [warning(seedKey, 1)], tickAuthority: a2 }), null);
  assert.equal(worker.finishTick({ nowMonoMs: 2, warnings: [warning(seedKey, 0)], tickAuthority: a1 }), null);
  assert.equal(worker.inFlightAuthority.tickAuthorityId, a3.tickAuthorityId);
  const message = worker.finishTick({ nowMonoMs: 3, warnings: [warning(seedKey, 2)], tickAuthority: a3 });
  assert.ok(message);
  assert.equal(message.pairGeneration, 3);
  assertSafety(worker);
}

function legacyUntaggedPermitted(seedKey) {
  const s = session(seedKey, 'legacy');
  const p = pair(seedKey, s, 1, 'pair');
  const worker = new ReferenceWorkerRuntime();
  assert.equal(install(worker, 'epoch-a', p), true);
  assert.equal(worker.startTick(), true);
  const message = worker.finishTick({ nowMonoMs: 0, warnings: [warning(seedKey)] });
  assert.ok(message);
  assert.equal(message.pairGeneration, 1);
  assertSafety(worker);
}

function failureInjection(seedKey) {
  const s = session(seedKey, 'failure');
  const p1 = pair(seedKey, s, 1, 'bad');
  const p2 = pair(seedKey, s, 2, 'recovery');
  const worker = new ReferenceWorkerRuntime();
  const page = new PageTransportAuthority({ session: s });
  assert.equal(install(worker, 'epoch-a', p1), true);
  page.bind(p1);
  const authority = worker.startTick({ captureAuthority: true });
  const invalid = { ...warning(seedKey), ruleId: `INVALID_${hex32(seedKey)}` };
  const failure = worker.finishTick({ nowMonoMs: 0, warnings: [invalid], tickAuthority: authority });
  assert.equal(failure.stage, 'detector-output');
  assert.equal(failure.warningSilent, true);
  assert.ok(failure.diag);
  assert.equal(page.accept(failure.diag, 0), true);
  assert.equal(page.visibleWarnings(0).length, 0);
  assert.equal(install(worker, 'epoch-b', p2), true);
  page.bind(p2);
  const recoveryAuthority = worker.startTick({ captureAuthority: true });
  const recovery = worker.finishTick({ nowMonoMs: 1, warnings: [], tickAuthority: recoveryAuthority });
  assert.ok(recovery);
  assert.equal(page.accept(recovery, 1), true);
  assertSafety(worker);
}

const FAMILIES = Object.freeze([
  ['stale-old-completion-rebind', staleRebind],
  ['session-change', sessionChange],
  ['pair-generation-nonce-churn', pairGenerationNonceChurn],
  ['runtime-epoch-reset', runtimeEpochReset],
  ['worker-replacement-reinstall', workerReplacementReinstall],
  ['disconnect-reconnect', disconnectReconnect],
  ['stale-warning-expiry-boundary', staleWarningBoundary],
  ['warning-clear-change-race', warningClearChange],
  ['heartbeat-timing-variation', heartbeatVariation],
  ['skipped-tick-one-in-flight-no-catch-up', skippedTickPressure],
  ['unsupported-supported-transition', unsupportedSupportedTransitions],
  ['out-of-order-completion', outOfOrderCompletions],
  ['legacy-untagged-compatible', legacyUntaggedPermitted],
  ['failure-injection-publish-clear-revoke', failureInjection]
]);

function writeJson(filePath, value) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(value, null, 2) + '\n');
}

async function runSegment() {
  const segmentIndex = Number.parseInt(process.env.ENDURANCE_SEGMENT_INDEX || '0', 10);
  const intendedDurationMs = Number.parseInt(process.env.ENDURANCE_SEGMENT_MS || '1500000', 10);
  const outputPath = process.env.ENDURANCE_CHECKPOINT_PATH ||
    path.join(here, 'checkpoints', `segment-${String(segmentIndex).padStart(2, '0')}.json`);
  if (!Number.isInteger(segmentIndex) || segmentIndex < 0) throw new Error('invalid ENDURANCE_SEGMENT_INDEX');
  if (!Number.isFinite(intendedDurationMs) || intendedDurationMs < 1000) throw new Error('invalid ENDURANCE_SEGMENT_MS');

  const startedAtUtc = new Date().toISOString();
  let observedBlobShas = {};
  let control = null;
  let scenarioCount = 0;
  let failureCount = 0;
  let rollingEvidenceSha256 = '0'.repeat(64);
  const familyCounts = Object.fromEntries(FAMILIES.map(([name]) => [name, 0]));
  let status = 'PASS';
  let blocker = null;
  let workloadStart = Date.now();

  try {
    observedBlobShas = assertPinnedSnapshot();
    control = runFrozenCatalog();
    workloadStart = Date.now();
    const deadline = workloadStart + intendedDurationMs;
    while (Date.now() < deadline) {
      const seedKey = `${STAGE_ID}:segment:${segmentIndex}:scenario:${scenarioCount}`;
      const [familyName, fn] = FAMILIES[scenarioCount % FAMILIES.length];
      try {
        fn(seedKey);
      } catch (error) {
        failureCount += 1;
        throw new Error(`P0/P1 candidate in family=${familyName} seed=${seedKey}: ${error?.stack || error}`);
      }
      familyCounts[familyName] += 1;
      rollingEvidenceSha256 = hashHex(`${rollingEvidenceSha256}|${seedKey}|${familyName}|PASS`);
      scenarioCount += 1;
    }
    observedBlobShas = assertPinnedSnapshot();
    control = runFrozenCatalog();
  } catch (error) {
    status = 'BLOCKED';
    blocker = String(error?.stack || error);
  }

  const actualElapsedMs = Math.max(0, Date.now() - workloadStart);
  const endedAtUtc = new Date().toISOString();
  const checkpoint = {
    schema: 'wof-alpha-transport-true-endurance-checkpoint-v1',
    stageId: STAGE_ID,
    segmentIndex,
    intendedDurationMs,
    actualElapsedMs,
    startedAtUtc,
    endedAtUtc,
    status,
    blocker,
    scenarioCount,
    seedRange: {
      start: `${STAGE_ID}:segment:${segmentIndex}:scenario:0`,
      end: scenarioCount > 0 ? `${STAGE_ID}:segment:${segmentIndex}:scenario:${scenarioCount - 1}` : null
    },
    familyCounts,
    failureCount,
    latestInvariantStatus: status === 'PASS' ? 'PASS' : 'BLOCKED',
    rollingEvidenceSha256,
    frozenCatalogControl: control,
    sourceIntegrity: {
      algorithm: 'git-blob-sha1',
      observedBlobShas
    },
    safety: {
      readOnly: SAFETY.readOnly,
      ramWrites: SAFETY.ramWrites,
      inputInjection: SAFETY.inputInjection,
      workerReplacement: SAFETY.workerReplacement,
      blobRewrite: SAFETY.blobRewrite
    }
  };
  writeJson(outputPath, checkpoint);
  console.log(JSON.stringify({
    status,
    segmentIndex,
    actualElapsedMs,
    scenarioCount,
    failureCount,
    checkpoint: path.relative(process.cwd(), outputPath)
  }));
  if (status !== 'PASS') process.exitCode = 1;
}

function collectJsonFiles(root) {
  const out = [];
  if (!fs.existsSync(root)) return out;
  for (const entry of fs.readdirSync(root, { withFileTypes: true })) {
    const p = path.join(root, entry.name);
    if (entry.isDirectory()) out.push(...collectJsonFiles(p));
    else if (/segment-\d+\.json$/i.test(entry.name)) out.push(p);
  }
  return out;
}

function aggregate() {
  const inputRoot = process.env.ENDURANCE_AGGREGATE_INPUT || path.join(here, 'downloaded-checkpoints');
  const outputPath = process.env.ENDURANCE_FINAL_SUMMARY_PATH || path.join(here, 'final-summary.json');
  const files = collectJsonFiles(inputRoot);
  const checkpoints = files.map(p => JSON.parse(fs.readFileSync(p, 'utf8')))
    .filter(x => x.stageId === STAGE_ID)
    .sort((a, b) => a.segmentIndex - b.segmentIndex);

  const intendedSegments = Number.parseInt(process.env.ENDURANCE_EXPECTED_SEGMENTS || '13', 10);
  const intendedDurationMs = Number.parseInt(process.env.ENDURANCE_TOTAL_INTENDED_MS || String(13 * 25 * 60 * 1000), 10);
  const actualExecutorElapsedMs = checkpoints.reduce((sum, x) => sum + Number(x.actualElapsedMs || 0), 0);
  const uniqueGeneratedScenarioCount = checkpoints.reduce((sum, x) => sum + Number(x.scenarioCount || 0), 0);
  const failureCount = checkpoints.reduce((sum, x) => sum + Number(x.failureCount || 0), 0);
  const startedTimes = checkpoints.map(x => Date.parse(x.startedAtUtc)).filter(Number.isFinite);
  const endedTimes = checkpoints.map(x => Date.parse(x.endedAtUtc)).filter(Number.isFinite);
  const actualWallClockMs = startedTimes.length && endedTimes.length ? Math.max(...endedTimes) - Math.min(...startedTimes) : 0;
  const allPass = checkpoints.length === intendedSegments &&
    checkpoints.every(x => x.status === 'PASS') &&
    checkpoints.every(x => x.frozenCatalogControl?.status === 'PASS') &&
    failureCount === 0;
  const durationSatisfied = actualExecutorElapsedMs >= 5 * 60 * 60 * 1000 && actualWallClockMs >= 5 * 60 * 60 * 1000;
  const status = allPass && durationSatisfied ? 'PASS' : 'BLOCKED';

  const mergedFamilyCounts = Object.fromEntries(FAMILIES.map(([name]) => [name, 0]));
  for (const checkpoint of checkpoints) {
    for (const [name, count] of Object.entries(checkpoint.familyCounts || {})) {
      mergedFamilyCounts[name] = (mergedFamilyCounts[name] || 0) + Number(count || 0);
    }
  }

  const summary = {
    schema: 'wof-alpha-transport-true-5h-endurance-summary-v1',
    stageId: STAGE_ID,
    status,
    verdict: status === 'PASS'
      ? 'ALPHA TRANSPORT TRUE 5H ENDURANCE PASS — READY AS INTEGRATION ROBUSTNESS EVIDENCE'
      : 'BLOCKED — ALPHA TRANSPORT TRUE 5H ENDURANCE DID NOT SATISFY SUCCESS STOP',
    intendedDurationMs,
    actualExecutorElapsedMs,
    actualWallClockMs,
    checkpointCount: checkpoints.length,
    intendedCheckpointCount: intendedSegments,
    uniqueGeneratedScenarioCount,
    seedScenarioCoverage: {
      segments: checkpoints.map(x => ({
        segmentIndex: x.segmentIndex,
        seedRange: x.seedRange,
        scenarioCount: x.scenarioCount,
        rollingEvidenceSha256: x.rollingEvidenceSha256
      })),
      familyCounts: mergedFamilyCounts
    },
    frozenCatalogControls: checkpoints.map(x => ({
      segmentIndex: x.segmentIndex,
      status: x.frozenCatalogControl?.status || null,
      passCount: x.frozenCatalogControl?.passCount || null,
      vectorCount: x.frozenCatalogControl?.vectorCount || null
    })),
    safety: {
      readOnly: true,
      ramWrites: 0,
      inputInjection: false,
      workerReplacement: false,
      blobRewrite: false
    },
    exactSutInputBlobs: EXPECTED_BLOBS,
    failureCount,
    blockers: checkpoints.filter(x => x.status !== 'PASS').map(x => ({
      segmentIndex: x.segmentIndex,
      blocker: x.blocker
    })),
    integrationRequirementChange: status === 'PASS'
      ? 'NONE — endurance evidence does not require a reference integration contract change.'
      : 'NO CHANGE AUTHORIZED — investigate blocker before changing integration requirements.'
  };
  writeJson(outputPath, summary);
  console.log(JSON.stringify({
    status,
    checkpointCount: checkpoints.length,
    actualExecutorElapsedMs,
    actualWallClockMs,
    uniqueGeneratedScenarioCount,
    outputPath: path.relative(process.cwd(), outputPath)
  }));
  if (status !== 'PASS') process.exitCode = 1;
}

if (process.argv.includes('--aggregate')) {
  aggregate();
} else {
  await runSegment();
}
