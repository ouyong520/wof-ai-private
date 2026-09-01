import {
  CONTRACT, SAFETY, clone, makeDiagEnvelope, makeStateEnvelope,
  validateDualIdentityHandshake, validatePair, validateWarningRows
} from './constants.mjs';

function stableWarningsHash(warnings) {
  return JSON.stringify((warnings || []).map(w => [
    w.ruleId, w.slot, w.target7E, w.sourceSide, w.threatSide, w.attack,
    w.publication, w.evidence
  ]));
}

export class ReferenceWorkerRuntime {
  constructor({ heartbeatMaxMs = CONTRACT.heartbeatMaxMs } = {}) {
    this.heartbeatMaxMs = heartbeatMaxMs;
    this.active = false;
    this.runtimeEpoch = null;
    this.pair = null;
    this.hashCount = 0;
    this.inFlight = false;
    this.inFlightAuthority = null;
    this.tickAuthoritySeq = 0;
    this.legacyCompletionBlocked = false;
    this.skippedTicks = 0;
    this.queueDepth = 0;
    this.publications = [];
    this.lastPublishedHash = null;
    this.lastPublishedAt = null;
    this.seq = 0;
    this.agentCount = 0;
    this.gameplayPlayable = true;
    this.identity = null;
    this.lastFailure = null;
  }

  install({ runtimeEpoch, pair, launcherIdentityProbe, detectorLocalIdentityOk }) {
    const pairCheck = validatePair(pair);
    if (!pairCheck.ok) throw new Error(pairCheck.reason);
    this.stop('reinstall');
    this.hashCount += 1;
    const identity = validateDualIdentityHandshake(launcherIdentityProbe, detectorLocalIdentityOk);
    this.pair = clone(pair);
    this.runtimeEpoch = runtimeEpoch;
    this.identity = identity;
    this.seq = 0;
    this.lastPublishedHash = null;
    this.lastPublishedAt = null;
    this.lastFailure = null;
    if (!identity.ok) {
      this.active = false;
      this.agentCount = 0;
      return false;
    }
    this.active = true;
    this.agentCount = 1;
    return true;
  }

  captureTickAuthority() {
    if (!this.active || !this.pair) return null;
    return Object.freeze({
      tickAuthorityId: ++this.tickAuthoritySeq,
      runtimeEpoch: this.runtimeEpoch,
      session: this.pair.session,
      pairGeneration: this.pair.pairGeneration,
      pairNonce: this.pair.pairNonce
    });
  }

  startTick({ captureAuthority = false } = {}) {
    if (!this.active) return false;
    if (this.inFlight) {
      this.skippedTicks += 1;
      this.queueDepth = 0;
      return false;
    }
    const authority = this.captureTickAuthority();
    this.inFlight = true;
    this.inFlightAuthority = authority;
    return captureAuthority ? authority : true;
  }

  authorityIsCurrent(authority) {
    return !!authority &&
      this.active === true &&
      this.inFlight === true &&
      !!this.inFlightAuthority &&
      authority.tickAuthorityId === this.inFlightAuthority.tickAuthorityId &&
      authority.runtimeEpoch === this.inFlightAuthority.runtimeEpoch &&
      authority.session === this.inFlightAuthority.session &&
      authority.pairGeneration === this.inFlightAuthority.pairGeneration &&
      authority.pairNonce === this.inFlightAuthority.pairNonce &&
      authority.runtimeEpoch === this.runtimeEpoch &&
      !!this.pair &&
      authority.session === this.pair.session &&
      authority.pairGeneration === this.pair.pairGeneration &&
      authority.pairNonce === this.pair.pairNonce;
  }

  revokeInFlightAuthority() {
    if (this.inFlight || this.inFlightAuthority) {
      // Once an untagged completion can race a revoked tick, it is permanently
      // ambiguous for this runtime object. Fail closed instead of ever lending
      // a newer generation's slot to that legacy callback.
      this.legacyCompletionBlocked = true;
    }
    this.inFlight = false;
    this.inFlightAuthority = null;
  }

  finishTick({ nowMonoMs, warnings, tickAuthority = null }) {
    let authority = tickAuthority;
    if (!authority) {
      if (this.legacyCompletionBlocked) return null;
      if (!this.inFlight || !this.inFlightAuthority) throw new Error('no detector tick in flight');
      authority = this.inFlightAuthority;
    }

    // A stale/revoked completion is a no-op. In particular, do not clear the
    // current in-flight slot before proving that this exact tick still owns it.
    if (!this.authorityIsCurrent(authority)) return null;

    this.inFlight = false;
    this.inFlightAuthority = null;
    const warningCheck = validateWarningRows(warnings || []);
    if (!warningCheck.ok) return this.fail('detector-output', warningCheck.reason);
    const hash = stableWarningsHash(warnings || []);
    const changed = hash !== this.lastPublishedHash;
    const heartbeat = this.lastPublishedAt === null || nowMonoMs - this.lastPublishedAt >= this.heartbeatMaxMs;
    if (changed || heartbeat) {
      this.seq += 1;
      const capturedPair = {
        session: authority.session,
        pairGeneration: authority.pairGeneration,
        pairNonce: authority.pairNonce
      };
      const message = makeStateEnvelope(capturedPair, this.seq, warnings || []);
      this.publications.push({ nowMonoMs, message });
      this.lastPublishedHash = hash;
      this.lastPublishedAt = nowMonoMs;
      return message;
    }
    return null;
  }

  runtimeEpochChanged(newEpoch) {
    if (newEpoch === this.runtimeEpoch) return false;
    this.stop('runtime-epoch-changed');
    this.runtimeEpoch = newEpoch;
    this.identity = null;
    return true;
  }

  disconnectCdp() {
    return { gameplayPlayable: true, agentMayRemain: this.active };
  }

  fail(stage, reason = stage) {
    const pair = this.pair;
    this.active = false;
    this.agentCount = 0;
    this.revokeInFlightAuthority();
    this.queueDepth = 0;
    this.lastFailure = { stage, reason };
    const diag = pair ? makeDiagEnvelope(pair, { code: String(stage), reason: String(reason) }) : null;
    return { stage, reason, gameplayPlayable: true, warningSilent: true, diag };
  }

  stop(reason = 'stopped') {
    this.active = false;
    this.agentCount = 0;
    this.revokeInFlightAuthority();
    this.queueDepth = 0;
    this.lastFailure = reason ? { stage: 'stop', reason } : null;
  }

  safetyStatus() {
    return {
      ...SAFETY,
      active: this.active,
      runtimeEpoch: this.runtimeEpoch,
      hashCount: this.hashCount,
      skippedTicks: this.skippedTicks,
      queueDepth: this.queueDepth,
      agentCount: this.agentCount
    };
  }
}
