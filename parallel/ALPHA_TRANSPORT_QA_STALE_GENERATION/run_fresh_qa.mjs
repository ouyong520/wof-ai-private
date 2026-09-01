import { strict as assert } from 'node:assert';
import crypto from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const parallelDir = path.resolve(here, '..');
const implDir = path.join(parallelDir, 'ALPHA_TRANSPORT_IMPL');
const mockDir = path.join(parallelDir, 'ALPHA_TRANSPORT_MOCK');
const summaryPath = path.join(here, 'summary.json');

const expectedBlobShas = Object.freeze({
  'ALPHA_TRANSPORT_IMPL/constants.mjs': 'a29cb3ad714598e2e6aeeed64acc9e3eca8b221e',
  'ALPHA_TRANSPORT_IMPL/page_authority.mjs': '5e53bd2ad40823a8768802df0a1c5431adb19ee9',
  'ALPHA_TRANSPORT_IMPL/worker_runtime.mjs': 'c353b4500640e31950cde42173a934d541f22531',
  'ALPHA_TRANSPORT_IMPL/acceptance_adapter.mjs': 'd79dff0b2708c671ab8a11644fcc4f771ec75003',
  'ALPHA_TRANSPORT_MOCK/fixtures.json': '35bf36b4c741cda5d94be3f9884511a86653c11f',
  'ALPHA_TRANSPORT_MOCK/vectors.json': '5a0cbe2ccfcf7eb6e875552f56748f736722c14d',
  'ALPHA_TRANSPORT_MOCK/expected_results.json': '1231e0946d18068284724d92e732ea185e4e6af8'
});

function gitBlobSha(filePath) {
  const body = fs.readFileSync(filePath);
  const header = Buffer.from(`blob ${body.length}\0`);
  return crypto.createHash('sha1').update(header).update(body).digest('hex');
}
function runNode(script, options = {}) {
  const x = spawnSync(process.execPath, [script], {
    cwd: options.cwd || parallelDir,
    env: options.env || process.env,
    encoding: 'utf8'
  });
  if (x.status !== 0) {
    throw new Error(`node ${script} failed (${x.status}): ${x.stderr || x.stdout}`);
  }
  return x.stdout.trim();
}
function lastJsonLine(text) {
  const lines = text.split(/\r?\n/).filter(Boolean);
  return JSON.parse(lines.at(-1));
}
function relFile(key) {
  const [area, ...rest] = key.split('/');
  return path.join(parallelDir, area, ...rest);
}

const observedBlobShas = {};
for (const [key, expected] of Object.entries(expectedBlobShas)) {
  const observed = gitBlobSha(relFile(key));
  observedBlobShas[key] = observed;
  assert.equal(observed, expected, `frozen/source blob changed: ${key}`);
}

const targeted = lastJsonLine(runNode(path.join(here, 'targeted_stale_generation_qa.mjs')));
assert.equal(targeted.status, 'PASS');
assert.equal(targeted.caseCount, 12);
assert.equal(targeted.passCount, 12);
assert.equal(targeted.failCount, 0);

// Execute the exact frozen acceptance adapter bytes in a temp mirror so its
// own result.json write cannot modify parallel/ALPHA_TRANSPORT_IMPL/**.
const tmpRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'wof-alpha-stale-gen-qa-'));
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

  const frozenStdout = runNode(path.join(tmpImpl, 'acceptance_adapter.mjs'), {
    cwd: tmpImpl,
    env: { ...process.env, WOF_ALPHA_TRANSPORT_MOCK_DIR: tmpMock }
  });
  const frozenConsole = lastJsonLine(frozenStdout);
  const frozenResult = JSON.parse(fs.readFileSync(path.join(tmpImpl, 'result.json'), 'utf8'));

  assert.equal(frozenConsole.status, 'PASS');
  assert.equal(frozenResult.status, 'PASS');
  assert.equal(frozenResult.vectorCount, 67);
  assert.equal(frozenResult.passCount, 67);
  assert.equal(frozenResult.failCount, 0);
  assert.equal(frozenResult.results.length, 67);
  assert.equal(frozenResult.results.every(x => x.status === 'PASS'), true);

  const summary = {
    schema: 'wof-alpha-transport-stale-generation-fresh-qa-v1',
    status: 'PASS',
    targeted: {
      caseCount: targeted.caseCount,
      passCount: targeted.passCount,
      failCount: targeted.failCount,
      results: targeted.results
    },
    frozenCatalog: {
      source: 'parallel/ALPHA_TRANSPORT_MOCK/vectors.json',
      vectorCount: frozenResult.vectorCount,
      passCount: frozenResult.passCount,
      failCount: frozenResult.failCount,
      status: frozenResult.status
    },
    sourceIntegrity: {
      algorithm: 'git-blob-sha1',
      observedBlobShas
    },
    safety: {
      readOnly: frozenResult.safety.readOnly,
      ramWrites: frozenResult.safety.ramWrites,
      inputInjection: frozenResult.safety.inputInjection,
      workerReplacement: frozenResult.safety.workerReplacement,
      blobRewrite: frozenResult.safety.blobRewrite
    },
    deliveryReassessment: {
      formerP1Closed: true,
      formalRealAdapterIntegrationUnblockedByReference: true,
      remainingReferenceContractBlocker: null,
      downstreamIntegrationStillRequiresItsOwnQA: true
    }
  };
  fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2) + '\n');
  console.log(JSON.stringify({
    status: summary.status,
    targeted: `${targeted.passCount}/${targeted.caseCount}`,
    frozenCatalog: `${frozenResult.passCount}/${frozenResult.vectorCount}`,
    resultPath: path.relative(process.cwd(), summaryPath)
  }));
} finally {
  fs.rmSync(tmpRoot, { recursive: true, force: true });
}
