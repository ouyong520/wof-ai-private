import { randomBytes } from 'node:crypto';
import { AlphaDetectorAdapter } from './detector_adapter.mjs';
import { CONTRACT, SAFETY, isPairNonce, validateDetectorLocalIdentityProof, validateLauncherIdentityProbe, validatePair } from './constants.mjs';
import { requireValidPageConfig } from './adapters.mjs';

export function freshPairNonce() {
  return randomBytes(16).toString('hex');
}

export class ReferenceTransportRuntime {
  constructor({ discoveryAdapter, nativeWorkerAdapter, pageHudAdapter, canonicalAlphaCore }) {
    if (!discoveryAdapter || !nativeWorkerAdapter || !pageHudAdapter) throw new Error('all adapters are required');
    this.discovery = discoveryAdapter;
    this.nativeWorker = nativeWorkerAdapter;
    this.pageHud = pageHudAdapter;
    this.detector = new AlphaDetectorAdapter(canonicalAlphaCore);
    this.current = null;
  }

  async bindPage(pageRef, { pairNonce = freshPairNonce() } = {}) {
    if (!isPairNonce(pairNonce)) throw new Error('pairNonce must be fresh 128-bit lowercase hex');
    try {
      const config = requireValidPageConfig(await this.discovery.readPageConfig(pageRef));
      const targets = await this.discovery.listTargets();
      const resolved = this.discovery.resolveWorker(targets, pageRef);
      if (!resolved.ok) return this.failClosed('worker-association-' + resolved.reason);

      const launcherIdentity = await this.nativeWorker.launcherIdentityProbe(resolved.worker);
      if (!validateLauncherIdentityProbe(launcherIdentity).ok) return this.failClosed('launcher-identity-failed');

      const binding = await this.pageHud.bind(pageRef, pairNonce);
      const pair = {
        session: binding.session,
        pairGeneration: binding.pairGeneration,
        pairNonce
      };
      if (!validatePair(pair, config.session).ok) return this.failClosed('page-bind-invalid');

      const detectorLocal = await this.nativeWorker.detectorLocalIdentityProbe(resolved.worker);
      if (!validateDetectorLocalIdentityProof(detectorLocal).ok) {
        await this.pageHud.reset(pageRef).catch(() => {});
        return this.failClosed('detector-local-identity-failed');
      }

      await this.nativeWorker.stopObserver(resolved.worker).catch(() => {});
      await this.nativeWorker.installObserver(resolved.worker, {
        ...pair,
        channel: config.channel,
        transportVersion: CONTRACT.transportVersion,
        identitySignature: CONTRACT.identitySignature,
        ...SAFETY
      }, this.detector);

      this.current = { pageRef, worker: resolved.worker, pair, config };
      return { ok: true, ...this.current, ...SAFETY };
    } catch (error) {
      return this.failClosed('adapter-exception', error);
    }
  }

  async runtimeEpochChanged() {
    if (!this.current) return this.failClosed('no-current-pair');
    try {
      await this.pageHud.reset(this.current.pageRef);
      await this.nativeWorker.stopObserver(this.current.worker);
    } catch (_) {}
    this.detector.reset();
    this.current = null;
    return this.failClosed('runtime-epoch-changed');
  }

  failClosed(code, error = null) {
    return {
      ok: false,
      code,
      error: error ? String(error?.message || error) : null,
      gameplayPlayable: true,
      warningAuthority: false,
      ...SAFETY
    };
  }
}
