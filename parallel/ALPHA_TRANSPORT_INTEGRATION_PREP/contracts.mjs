import {
  CONTRACT,
  SAFETY,
  safetyFieldsExact,
  validateLauncherIdentityProbe,
  validatePageConfig,
  validateWarningRows
} from '../ALPHA_TRANSPORT_IMPL/constants.mjs';
import {
  DiscoveryAdapter,
  NativeWorkerRuntimeAdapter,
  PageHudTransportAdapter
} from '../ALPHA_TRANSPORT_IMPL/adapters.mjs';

export const DISCOVERY_INPUT_SCHEMA = 'wof-alpha-real-adapter-discovery-observation-v1';
export const OBSERVER_STATUS_SCHEMA = 'wof-alpha-native-observer-status-v1';
export const WORKER_TARGET_TYPES = Object.freeze(['worker', 'shared_worker', 'service_worker']);
export const HUD_ATTACH_STATES = Object.freeze(['WAITING_EXTERNAL_TRANSPORT', 'PAIRING', 'PAIRED', 'DISABLED']);

function fail(reason, extra = {}) {
  return { ok: false, reason, warningAuthority: false, gameplayPlayable: true, ...SAFETY, ...extra };
}

function nonEmpty(value) {
  return typeof value === 'string' && value.length > 0;
}

export function lifecycleEpochKey(lifecycle) {
  if (!lifecycle || !nonEmpty(lifecycle.connectionId) || !nonEmpty(lifecycle.pageTargetId) || !nonEmpty(lifecycle.workerTargetId)) {
    throw new Error('lifecycle identity incomplete');
  }
  if (!Number.isInteger(lifecycle.pageEpoch) || lifecycle.pageEpoch < 0 || !Number.isInteger(lifecycle.workerEpoch) || lifecycle.workerEpoch < 0) {
    throw new Error('lifecycle epoch malformed');
  }
  return [lifecycle.connectionId, lifecycle.pageTargetId, lifecycle.pageEpoch, lifecycle.workerTargetId, lifecycle.workerEpoch].join('|');
}

export class RuntimeEpochGuard {
  constructor() { this.current = null; }
  observe(lifecycle) {
    const next = lifecycleEpochKey(lifecycle);
    const previous = this.current;
    const changed = previous !== null && previous !== next;
    this.current = next;
    return { changed, previous, current: next, warningAuthority: !changed };
  }
  invalidate() {
    const previous = this.current;
    this.current = null;
    return { changed: previous !== null, previous, current: null, warningAuthority: false };
  }
}

export function toReferenceLauncherIdentity(identity, workerProbe = {}) {
  const sha256 = typeof identity?.sha256 === 'string' ? identity.sha256.toLowerCase() : '';
  const hashAccepted = identity?.ok === true && identity?.candidateCount === 1 && sha256 === CONTRACT.goldenSha256;
  return {
    moduleOk: workerProbe?.moduleOk === true && identity?.moduleOk === true,
    heapOk: workerProbe?.heapOk === true && identity?.heapOk === true,
    candidateCount: identity?.candidateCount,
    hashStatus: hashAccepted ? 'accepted' : 'rejected',
    sha256,
    readOnly: identity?.readOnly === true && workerProbe?.readOnly === true,
    ramWrites: identity?.ramWrites === 0 && workerProbe?.ramWrites === 0 ? 0 : Number.NaN,
    inputInjection: identity?.inputInjection === false && workerProbe?.inputInjection === false ? false : true
  };
}

export function projectPylaunchTargetChoice(choice, pageConfig, lifecycle) {
  const pageCheck = validatePageConfig(pageConfig);
  if (!pageCheck.ok) return fail('malformed-page-config');
  if (!choice || choice.reason != null) return fail('discovery-not-authoritative', { discoveryReason: choice?.reason ?? 'missing-choice' });
  const page = choice.page;
  const worker = choice.worker;
  const workerProbe = choice.worker_probe ?? choice.workerProbe;
  const identity = choice.identity;
  if (!page || page.type !== 'page' || !nonEmpty(page.targetId)) return fail('page-target-invalid');
  if (!worker || !WORKER_TARGET_TYPES.includes(worker.type) || !nonEmpty(worker.targetId)) return fail('worker-target-invalid');
  if (!workerProbe || workerProbe.moduleOk !== true || workerProbe.heapOk !== true) return fail('wasm-heap-not-ready');
  if (!identity || identity.ok !== true) return fail('world-identity-not-accepted');
  const referenceIdentity = toReferenceLauncherIdentity(identity, workerProbe);
  if (!validateLauncherIdentityProbe(referenceIdentity).ok) return fail('world-identity-gate-failed');

  const expectedLifecycle = {
    ...lifecycle,
    pageTargetId: page.targetId,
    workerTargetId: worker.targetId
  };
  let runtimeEpoch;
  try { runtimeEpoch = lifecycleEpochKey(expectedLifecycle); }
  catch (error) { return fail('lifecycle-invalid', { detail: String(error?.message || error) }); }

  return {
    ok: true,
    schema: DISCOVERY_INPUT_SCHEMA,
    pageTargetId: page.targetId,
    workerTargetId: worker.targetId,
    workerType: worker.type,
    workerUrlHint: String(worker.url || ''),
    associationPath: String(choice.diagnostics?.path || 'authoritative-target-choice'),
    associationExact: true,
    pageConfig: { ...pageConfig },
    runtimeEpoch,
    lifecycle: { ...expectedLifecycle },
    workerProbe: { ...workerProbe },
    identityAuthority: { ...identity },
    referenceLauncherIdentity: referenceIdentity,
    readOnly: true,
    ramWrites: 0,
    inputInjection: false,
    workerReplacement: false,
    urlRewrite: false
  };
}

export class PreparedDiscoveryAdapter extends DiscoveryAdapter {
  constructor(ops) {
    super();
    if (!ops || typeof ops.readPageConfig !== 'function' || typeof ops.discover !== 'function' || typeof ops.lifecycle !== 'function') {
      throw new Error('PreparedDiscoveryAdapter requires readPageConfig/discover/lifecycle operations');
    }
    this.ops = ops;
    this.lastPageRef = null;
    this.lastPageConfig = null;
    this.lastProjection = null;
  }

  async readPageConfig(pageRef) {
    const config = await this.ops.readPageConfig(pageRef);
    if (!validatePageConfig(config).ok) throw new Error('malformed-page-config');
    this.lastPageRef = pageRef;
    this.lastPageConfig = { ...config };
    return { ...config };
  }

  async listTargets() {
    if (!this.lastPageRef || !this.lastPageConfig) throw new Error('readPageConfig must precede listTargets');
    const choice = await this.ops.discover(this.lastPageRef);
    const lifecycle = await this.ops.lifecycle(this.lastPageRef, choice);
    const projected = projectPylaunchTargetChoice(choice, this.lastPageConfig, lifecycle);
    this.lastProjection = projected;
    return projected.ok ? [projected] : [];
  }

  resolveWorker(targets, pageRef) {
    if (pageRef !== this.lastPageRef) return { ok: false, worker: null, workerId: null, reason: 'page-ref-changed' };
    if (this.lastProjection && this.lastProjection.ok !== true) {
      return { ok: false, worker: null, workerId: null, reason: this.lastProjection.reason || 'none' };
    }
    const exact = (targets || []).filter(row => row?.ok === true && row.associationExact === true);
    if (exact.length !== 1) return { ok: false, worker: null, workerId: null, reason: exact.length === 0 ? 'none' : 'ambiguous' };
    const row = exact[0];
    return { ok: true, worker: row, workerId: row.workerTargetId };
  }
}

function ensureSafeResult(value, label) {
  if (!safetyFieldsExact(value)) throw new Error(`${label} violated read-only/no-input invariants`);
  return value;
}

export class PreparedNativeWorkerRuntimeAdapter extends NativeWorkerRuntimeAdapter {
  constructor(ops) {
    super();
    const required = ['launcherIdentityProbe', 'detectorLocalIdentityProbe', 'installObserver', 'statusObserver', 'stopObserver'];
    if (!ops || required.some(name => typeof ops[name] !== 'function')) throw new Error('native Worker operations incomplete');
    this.ops = ops;
  }

  async launcherIdentityProbe(workerRef) {
    if (!workerRef?.runtimeEpoch || !workerRef?.workerProbe) throw new Error('missing Worker runtime authority');
    const fresh = await this.ops.launcherIdentityProbe(workerRef);
    if (!fresh || fresh.runtimeEpoch !== workerRef.runtimeEpoch || !fresh.identity) throw new Error('launcher identity runtime epoch mismatch');
    const probe = toReferenceLauncherIdentity(fresh.identity, workerRef.workerProbe);
    ensureSafeResult(probe, 'launcher identity');
    if (!validateLauncherIdentityProbe(probe).ok) throw new Error('launcher identity gate failed');
    return probe;
  }

  async detectorLocalIdentityProbe(workerRef) {
    const proof = await this.ops.detectorLocalIdentityProbe(workerRef);
    if (!proof || proof.runtimeEpoch !== workerRef?.runtimeEpoch) throw new Error('detector-local identity runtime epoch mismatch');
    return ensureSafeResult(proof, 'detector-local identity');
  }

  async installObserver(workerRef, binding, detectorAdapter) {
    ensureSafeResult(binding, 'observer binding');
    if (!workerRef?.runtimeEpoch) throw new Error('runtime epoch missing');
    if (!detectorAdapter || typeof detectorAdapter.evaluate !== 'function' || typeof detectorAdapter.reset !== 'function') {
      throw new Error('canonical detector adapter required');
    }
    const installed = await this.ops.installObserver(workerRef, {
      ...binding,
      runtimeEpoch: workerRef.runtimeEpoch,
      observerStatusSchema: OBSERVER_STATUS_SCHEMA
    }, detectorAdapter);
    ensureSafeResult(installed, 'observer install');
    if (installed?.runtimeEpoch !== workerRef.runtimeEpoch) throw new Error('observer install runtime epoch mismatch');
    return installed;
  }

  async statusObserver(workerRef) {
    const status = await this.ops.statusObserver(workerRef);
    ensureSafeResult(status, 'observer status');
    if (status.schema !== OBSERVER_STATUS_SCHEMA || status.runtimeEpoch !== workerRef.runtimeEpoch) {
      throw new Error('observer runtime epoch/status mismatch');
    }
    return status;
  }

  async stopObserver(workerRef) {
    const stopped = await this.ops.stopObserver(workerRef);
    if (stopped && typeof stopped === 'object') ensureSafeResult(stopped, 'observer stop');
    return stopped;
  }
}

export class PreparedPageHudTransportAdapter extends PageHudTransportAdapter {
  constructor(ops) {
    super();
    if (!ops || typeof ops.bind !== 'function' || typeof ops.status !== 'function' || typeof ops.reset !== 'function') {
      throw new Error('page/HUD operations incomplete');
    }
    this.ops = ops;
  }
  async bind(pageRef, pairNonce) {
    const result = await this.ops.bind(pageRef, pairNonce);
    if (!result || !Number.isInteger(result.pairGeneration) || result.pairGeneration <= 0 || !nonEmpty(result.session)) {
      throw new Error('page bind invalid');
    }
    return result;
  }
  async status(pageRef) { return this.ops.status(pageRef); }
  async reset(pageRef) { return this.ops.reset(pageRef); }
}

export function validateFixedHudOutput(output) {
  if (!output || output.schema !== CONTRACT.applicationSchema || output.release !== CONTRACT.release || output.transportVersion !== CONTRACT.transportVersion) {
    return { ok: false, reason: 'hud-envelope' };
  }
  if (!nonEmpty(output.session) || !Number.isInteger(output.pairGeneration) || output.pairGeneration < 0) return { ok: false, reason: 'hud-pair' };
  if (!HUD_ATTACH_STATES.includes(output.attachState) || typeof output.hudLoadAllowed !== 'boolean' || typeof output.stale !== 'boolean') return { ok: false, reason: 'hud-state' };
  const warnings = validateWarningRows(output.warnings || []);
  if (!warnings.ok) return { ok: false, reason: warnings.reason };
  if (output.diagnostic !== null && output.diagnostic !== undefined && typeof output.diagnostic !== 'object') return { ok: false, reason: 'hud-diagnostic' };
  return { ok: true, reason: null };
}

export function failClosedWarning(reason) {
  return fail(String(reason || 'adapter-failure'));
}
