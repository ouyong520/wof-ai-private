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

  startTick() {
    if (!this.active) return false;
    if (this.inFlight) {
      this.skippedTicks += 1;
      this.queueDepth = 0;
      return false;
    }
    this.inFlight = true;
    return true;
  }

  finishTick({ nowMonoMs, warnings }) {
    if (!this.inFlight) throw new Error('no detector tick in flight');
    this.inFlight = false;
    const warningCheck = validateWarningRows(warnings || []);
    if (!warningCheck.ok) return this.fail('detector-output', warningCheck.reason);
    const hash = stableWarningsHash(warnings || []);
    const changed = hash !== this.lastPublishedHash;
    const heartbeat = this.lastPublishedAt === null || nowMonoMs - this.lastPublishedAt >= this.heartbeatMaxMs;
    if (changed || heartbeat) {
      this.seq += 1;
      const message = makeStateEnvelope(this.pair, this.seq, warnings || []);
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
    this.inFlight = false;
    this.queueDepth = 0;
    this.lastFailure = { stage, reason };
    const diag = pair ? makeDiagEnvelope(pair, { code: String(stage), reason: String(reason) }) : null;
    return { stage, reason, gameplayPlayable: true, warningSilent: true, diag };
  }

  stop(reason = 'stopped') {
    this.active = false;
    this.agentCount = 0;
    this.inFlight = false;
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
