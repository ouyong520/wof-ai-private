import { strict as assert } from 'node:assert';
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const STAGE_ID = 'ALPHA_TRANSPORT_TRUE_5H_ENDURANCE_RECOVERY_V2';
const SUCCESS_VERDICT = 'ALPHA TRANSPORT TRUE 5H ENDURANCE V2 PASS — READY AS CURRENT-SNAPSHOT ROBUSTNESS EVIDENCE';
const BLOCKED_PREFIX = 'BLOCKED — ALPHA TRANSPORT TRUE 5H ENDURANCE V2 — ';
const here = path.dirname(fileURLToPath(import.meta.url));
const baseRunnerPath = path.resolve(here, '../ALPHA_TRANSPORT_TRUE_ENDURANCE/endurance_runner.mjs');
const BASE_RUNNER_BLOB_SHA = '8d7decc9f61bddecba6c8ce3d5c2b4cc56e0a670';

function gitBlobSha(filePath) {
  const body = fs.readFileSync(filePath);
  const header = Buffer.from(`blob ${body.length}\0`);
  return crypto.createHash('sha1').update(header).update(body).digest('hex');
}

function writeJson(filePath, value) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(value, null, 2) + '\n');
}

function runMetadata() {
  return {
    workflowRunId: process.env.GITHUB_RUN_ID || null,
    workflowRunAttempt: process.env.GITHUB_RUN_ATTEMPT || null,
    runHeadSha: process.env.GITHUB_SHA || null
  };
}

function preciseBlocker(summary) {
  const explicit = Array.isArray(summary.blockers)
    ? summary.blockers.find(x => x && typeof x.blocker === 'string' && x.blocker.trim())
    : null;
  if (explicit) return explicit.blocker.replace(/\s+/g, ' ').trim();

  const completed = Number(summary.checkpointCount || 0);
  const intended = Number(summary.intendedCheckpointCount || 0);
  if (completed !== intended) {
    return `durable checkpoint set incomplete: completed ${completed}/${intended}`;
  }

  const executorMs = Number(summary.actualExecutorElapsedMs || 0);
  if (executorMs < 5 * 60 * 60 * 1000) {
    return `actual executor elapsed ${executorMs} ms is below required 18000000 ms`;
  }

  const wallMs = Number(summary.actualWallClockMs || 0);
  if (wallMs < 5 * 60 * 60 * 1000) {
    return `actual wall-clock span ${wallMs} ms is below required 18000000 ms`;
  }

  const failures = Number(summary.failureCount || 0);
  if (failures !== 0) return `invariant failure count is ${failures}`;
  return 'true-longrun success criteria were not satisfied';
}

function transformedBaseRunner() {
  assert.equal(
    gitBlobSha(baseRunnerPath),
    BASE_RUNNER_BLOB_SHA,
    'V1 endurance executor infrastructure blob drifted; refuse to transform an unreviewed runner'
  );

  let source = fs.readFileSync(baseRunnerPath, 'utf8');
  source = source.replaceAll('ALPHA_TRANSPORT_TRUE_5H_ENDURANCE_V1', STAGE_ID);
  source = source.replaceAll('wof-alpha-transport-true-endurance-checkpoint-v1', 'wof-alpha-transport-true-endurance-checkpoint-v2');
  source = source.replaceAll('wof-alpha-transport-true-5h-endurance-summary-v1', 'wof-alpha-transport-true-5h-endurance-summary-v2');
  source = source.replaceAll(
    'ALPHA TRANSPORT TRUE 5H ENDURANCE PASS — READY AS INTEGRATION ROBUSTNESS EVIDENCE',
    SUCCESS_VERDICT
  );
  source = source.replaceAll(
    'BLOCKED — ALPHA TRANSPORT TRUE 5H ENDURANCE DID NOT SATISFY SUCCESS STOP',
    `${BLOCKED_PREFIX}DID NOT SATISFY SUCCESS STOP`
  );
  return source;
}

function patchCheckpoint() {
  const checkpointPath = process.env.ENDURANCE_CHECKPOINT_PATH;
  if (!checkpointPath || !fs.existsSync(checkpointPath)) return;
  const checkpoint = JSON.parse(fs.readFileSync(checkpointPath, 'utf8'));
  checkpoint.schema = 'wof-alpha-transport-true-endurance-checkpoint-v2';
  checkpoint.stageId = STAGE_ID;
  checkpoint.run = runMetadata();
  checkpoint.infrastructure = {
    baseRunnerPath: 'parallel/ALPHA_TRANSPORT_TRUE_ENDURANCE/endurance_runner.mjs',
    baseRunnerBlobSha: BASE_RUNNER_BLOB_SHA,
    wrapperBlobSha: gitBlobSha(fileURLToPath(import.meta.url)),
    v1ElapsedReused: false,
    idlePadding: false
  };
  writeJson(checkpointPath, checkpoint);
}

function patchSummary() {
  const summaryPath = process.env.ENDURANCE_FINAL_SUMMARY_PATH || path.join(here, 'final-summary.json');
  if (!fs.existsSync(summaryPath)) return;
  const summary = JSON.parse(fs.readFileSync(summaryPath, 'utf8'));
  summary.schema = 'wof-alpha-transport-true-5h-endurance-summary-v2';
  summary.stageId = STAGE_ID;
  summary.run = runMetadata();
  summary.infrastructure = {
    baseRunnerPath: 'parallel/ALPHA_TRANSPORT_TRUE_ENDURANCE/endurance_runner.mjs',
    baseRunnerBlobSha: BASE_RUNNER_BLOB_SHA,
    wrapperBlobSha: gitBlobSha(fileURLToPath(import.meta.url)),
    v1ElapsedReused: false,
    idlePadding: false
  };
  if (summary.status === 'PASS') {
    summary.blocker = null;
    summary.verdict = SUCCESS_VERDICT;
  } else {
    summary.blocker = preciseBlocker(summary);
    summary.verdict = `${BLOCKED_PREFIX}${summary.blocker}`;
  }
  writeJson(summaryPath, summary);
}

const generatedPath = path.join(here, `.generated-v2-runner-${process.pid}.mjs`);
let childStatus = 1;
try {
  fs.writeFileSync(generatedPath, transformedBaseRunner());
  const child = spawnSync(process.execPath, [generatedPath, ...process.argv.slice(2)], {
    cwd: process.cwd(),
    env: process.env,
    stdio: 'inherit'
  });
  childStatus = Number.isInteger(child.status) ? child.status : 1;
  if (process.argv.includes('--aggregate')) patchSummary();
  else patchCheckpoint();
  if (child.error) throw child.error;
} finally {
  fs.rmSync(generatedPath, { force: true });
}

process.exitCode = childStatus;
