export const CONTRACT = Object.freeze({
  applicationSchema: 'wof-alpha-v2',
  release: 'wof-alpha-rc3',
  coreVersion: 'wof-alpha-core-rc3',
  transportVersion: 'wof-alpha-safe-transport-v1',
  snapshotSchema: 'wof-alpha-snapshot-v1',
  goldenSha256: '5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62',
  identitySignature: 'wof-world-921031-maincpu-sha256-v1:5c369ce2de4f53d8',
  staleMs: 1500,
  heartbeatMaxMs: 250,
  maxEnemyRows: 20,
  allowedRuleIds: Object.freeze([
    'T18_5440_CYCLE_BODY7512_TM4_LEVEL_90',
    'T18_5424_CYCLE_BODY7520_TM4_LEVEL_90'
  ]),
  allowedCdpMethods: Object.freeze([
    'Target.getTargets',
    'Target.attachToTarget',
    'Target.detachFromTarget',
    'Runtime.enable',
    'Runtime.evaluate'
  ])
});

export const SAFETY = Object.freeze({
  readOnly: true,
  ramWrites: 0,
  inputInjection: false,
  workerReplacement: false,
  blobRewrite: false,
  gamePostMessageControl: false,
  heapWrites: false,
  assistMode: false
});

const HEX32 = /^[0-9a-f]{32}$/;
const SHA256 = /^[0-9a-f]{64}$/;
const GSTYPHOON = /\/gstyphoon(?:\.[^/?#]+)?\.js(?:[?#].*)?$/i;

export const clone = value => value == null ? value : JSON.parse(JSON.stringify(value));
export const isSession = value => typeof value === 'string' && HEX32.test(value);
export const isPairNonce = value => typeof value === 'string' && HEX32.test(value);

export function safetyFields() {
  return { readOnly: true, ramWrites: 0, inputInjection: false };
}

export function safetyFieldsExact(value) {
  return !!value && value.readOnly === true && value.ramWrites === 0 && value.inputInjection === false;
}

export function validatePageConfig(config) {
  const ok = !!config &&
    config.release === CONTRACT.release &&
    config.schema === CONTRACT.applicationSchema &&
    isSession(config.session) &&
    config.channel === `WOF_ALPHA_${config.session}`;
  return { ok, reason: ok ? null : 'malformed-page-config' };
}

export function validatePair(pair, expectedSession = null) {
  const ok = !!pair &&
    isSession(pair.session) &&
    Number.isInteger(pair.pairGeneration) && pair.pairGeneration > 0 &&
    isPairNonce(pair.pairNonce) &&
    (expectedSession == null || pair.session === expectedSession);
  return { ok, reason: ok ? null : 'malformed-pair' };
}

export function validateLauncherIdentityProbe(probe) {
  const ok = !!probe &&
    probe.moduleOk === true &&
    probe.heapOk === true &&
    probe.candidateCount === 1 &&
    probe.hashStatus === 'accepted' &&
    typeof probe.sha256 === 'string' && SHA256.test(probe.sha256) &&
    probe.sha256 === CONTRACT.goldenSha256 &&
    safetyFieldsExact(probe);
  return { ok, reason: ok ? null : 'identity-gate-failed' };
}

export function validateDetectorLocalIdentityProof(proof) {
  const ok = !!proof && proof.ok === true &&
    proof.identitySignature === CONTRACT.identitySignature &&
    safetyFieldsExact(proof);
  return { ok, reason: ok ? null : 'detector-local-identity-gate-failed' };
}

export function validateDualIdentityHandshake(probe, detectorLocalOk) {
  const launcher = validateLauncherIdentityProbe(probe);
  const localOk = detectorLocalOk === true;
  return {
    ok: launcher.ok && localOk,
    launcherOk: launcher.ok,
    detectorLocalOk: localOk,
    identity: launcher.ok && localOk ? {
      ok: true,
      game: 'wof',
      description: 'Warriors of Fate (World 921031)',
      logicalBytes: 1048576,
      sha256: CONTRACT.goldenSha256,
      signature: CONTRACT.identitySignature
    } : null,
    ...safetyFields()
  };
}

export function workerEligible(worker) {
  return !!worker &&
    worker.type === 'worker' &&
    GSTYPHOON.test(worker.url || '') &&
    worker.moduleOk === true &&
    worker.identityOk === true;
}

export function resolveWorkerForPage(targets, pageId) {
  const eligible = (targets || []).filter(workerEligible);
  const exact = eligible.filter(w => w.associationExact === true && w.page === pageId);
  if (exact.length === 1) return { ok: true, worker: exact[0], workerId: exact[0].id };
  return { ok: false, worker: null, workerId: null, reason: exact.length === 0 ? 'none' : 'ambiguous' };
}

export function assertAllowedCdpMethod(method) {
  if (typeof method !== 'string' || !CONTRACT.allowedCdpMethods.includes(method) || method.startsWith('Input.')) {
    throw new Error(`CDP method not allowed: ${String(method)}`);
  }
  return true;
}

export function validateWarningRows(warnings) {
  if (!Array.isArray(warnings)) return { ok: false, reason: 'warnings-not-array' };
  for (const row of warnings) {
    if (!row || !CONTRACT.allowedRuleIds.includes(row.ruleId)) return { ok: false, reason: 'unknown-rule' };
    if (row.publication !== 'hold-only-current-level' || row.evidence !== 'fresh-current-sample') {
      return { ok: false, reason: 'non-current-warning-evidence' };
    }
    if (!Number.isInteger(row.slot) || row.slot < 0 || row.slot >= CONTRACT.maxEnemyRows) {
      return { ok: false, reason: 'warning-slot-out-of-range' };
    }
  }
  return { ok: true, reason: null };
}

export function validateSnapshot(snapshot) {
  if (!snapshot || snapshot.snapshotSchema !== CONTRACT.snapshotSchema) return { ok: false, reason: 'snapshot-schema' };
  if (!Number.isInteger(snapshot.sampleSeq) || snapshot.sampleSeq < 0) return { ok: false, reason: 'sample-seq' };
  if (!Number.isFinite(snapshot.sampledAtMonoMs)) return { ok: false, reason: 'sample-time' };
  if (!Number.isInteger(snapshot.pairGeneration) || snapshot.pairGeneration <= 0) return { ok: false, reason: 'pair-generation' };
  if (!Array.isArray(snapshot.enemies) || snapshot.enemies.length > CONTRACT.maxEnemyRows) return { ok: false, reason: 'enemy-count' };
  const seen = new Set();
  for (const e of snapshot.enemies) {
    if (!e || !Number.isInteger(e.slot) || e.slot < 0 || e.slot >= CONTRACT.maxEnemyRows || seen.has(e.slot)) {
      return { ok: false, reason: 'enemy-slot' };
    }
    seen.add(e.slot);
    if (!Number.isFinite(e.enemyX)) return { ok: false, reason: 'enemy-x' };
    if (e.targetX !== null && e.targetX !== undefined && !Number.isFinite(e.targetX)) return { ok: false, reason: 'target-x' };
    if ('roomId' in e || 'watchId' in e || 'ageMs' in e || 'previous' in e || 'history' in e) {
      return { ok: false, reason: 'forbidden-history-field' };
    }
  }
  return { ok: true, reason: null };
}

export function makeStateEnvelope(pair, seq, warnings = [], extra = {}) {
  const p = validatePair(pair);
  if (!p.ok) throw new Error(p.reason);
  if (!Number.isInteger(seq) || seq < 0) throw new Error('seq must be a non-negative integer');
  return {
    schema: CONTRACT.applicationSchema,
    kind: 'state',
    release: CONTRACT.release,
    coreVersion: CONTRACT.coreVersion,
    transportVersion: CONTRACT.transportVersion,
    session: pair.session,
    pairGeneration: pair.pairGeneration,
    pairNonce: pair.pairNonce,
    seq,
    sentAt: Date.now(),
    identitySignature: CONTRACT.identitySignature,
    ...safetyFields(),
    warnings: clone(warnings),
    ...extra
  };
}

export function makeDiagEnvelope(pair, extra = {}) {
  const p = validatePair(pair);
  if (!p.ok) throw new Error(p.reason);
  return {
    schema: CONTRACT.applicationSchema,
    kind: 'diag',
    release: CONTRACT.release,
    transportVersion: CONTRACT.transportVersion,
    session: pair.session,
    pairGeneration: pair.pairGeneration,
    pairNonce: pair.pairNonce,
    sentAt: Date.now(),
    status: 'DISABLED',
    code: 'runtime-exception',
    reason: 'reference runtime diagnostic',
    ...safetyFields(),
    ...extra
  };
}
