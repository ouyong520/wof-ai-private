import { assertAllowedCdpMethod, resolveWorkerForPage, validatePageConfig } from './constants.mjs';

export class DiscoveryAdapter {
  async readPageConfig(_pageRef) { throw new Error('DiscoveryAdapter.readPageConfig not implemented'); }
  async listTargets() { throw new Error('DiscoveryAdapter.listTargets not implemented'); }
  resolveWorker(targets, pageRef) { return resolveWorkerForPage(targets, pageRef); }
}

export class NativeWorkerRuntimeAdapter {
  async launcherIdentityProbe(_workerRef) { throw new Error('NativeWorkerRuntimeAdapter.launcherIdentityProbe not implemented'); }
  async detectorLocalIdentityProbe(_workerRef) { throw new Error('NativeWorkerRuntimeAdapter.detectorLocalIdentityProbe not implemented'); }
  async installObserver(_workerRef, _binding, _detectorAdapter) { throw new Error('NativeWorkerRuntimeAdapter.installObserver not implemented'); }
  async statusObserver(_workerRef) { throw new Error('NativeWorkerRuntimeAdapter.statusObserver not implemented'); }
  async stopObserver(_workerRef) { throw new Error('NativeWorkerRuntimeAdapter.stopObserver not implemented'); }
}

export class PageHudTransportAdapter {
  async bind(_pageRef, _pairNonce) { throw new Error('PageHudTransportAdapter.bind not implemented'); }
  async status(_pageRef) { throw new Error('PageHudTransportAdapter.status not implemented'); }
  async reset(_pageRef) { throw new Error('PageHudTransportAdapter.reset not implemented'); }
}

export class SafeCdpAdapter {
  constructor(evaluate) {
    if (typeof evaluate !== 'function') throw new Error('SafeCdpAdapter requires an evaluate function');
    this.evaluate = evaluate;
  }
  async call(method, params) {
    assertAllowedCdpMethod(method);
    return this.evaluate(method, params);
  }
}

export function requireValidPageConfig(config) {
  const checked = validatePageConfig(config);
  if (!checked.ok) throw new Error(checked.reason);
  return config;
}
