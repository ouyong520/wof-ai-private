import {
  CONTRACT, clone, isSession, safetyFieldsExact, validatePair, validateWarningRows
} from './constants.mjs';

export class PageTransportAuthority {
  constructor({ session, staleMs = CONTRACT.staleMs } = {}) {
    if (!isSession(session)) throw new Error('invalid page session');
    this.session = session;
    this.staleMs = staleMs;
    this.generation = 0;
    this.nonce = null;
    this.lastSeq = -1;
    this.lastReceiveMonoMs = null;
    this.authority = [];
    this.lastDiag = null;
    this.attachState = 'WAITING_EXTERNAL_TRANSPORT';
    this.hudLoadAllowed = false;
  }

  bind(pair) {
    const check = validatePair(pair, this.session);
    if (!check.ok) throw new Error(check.reason);
    if (pair.pairGeneration <= this.generation) throw new Error('pairGeneration must increase');
    this.generation = pair.pairGeneration;
    this.nonce = pair.pairNonce;
    this.lastSeq = -1;
    this.lastReceiveMonoMs = null;
    this.authority = [];
    this.lastDiag = null;
    this.attachState = 'PAIRING';
    this.hudLoadAllowed = false;
    return this.status();
  }

  validEnvelope(message) {
    return !!message &&
      message.schema === CONTRACT.applicationSchema &&
      message.session === this.session &&
      message.transportVersion === CONTRACT.transportVersion &&
      message.pairGeneration === this.generation &&
      message.pairNonce === this.nonce;
  }

  accept(message, receiveMonoMs) {
    if (!this.validEnvelope(message)) return false;
    if (!Number.isFinite(receiveMonoMs)) return false;

    if (message.kind === 'diag') {
      if (!safetyFieldsExact(message)) return false;
      this.authority = [];
      this.lastReceiveMonoMs = null;
      this.lastDiag = { code: message.code || null, status: message.status || null, reason: message.reason || null };
      this.attachState = 'DISABLED';
      return true;
    }

    if (message.kind !== 'state') return false;
    if (!Number.isInteger(message.seq) || message.seq <= this.lastSeq) return false;
    if (message.identitySignature !== CONTRACT.identitySignature) return false;
    if (!safetyFieldsExact(message)) return false;
    const warnings = validateWarningRows(message.warnings || []);
    if (!warnings.ok) return false;

    this.lastSeq = message.seq;
    this.lastReceiveMonoMs = receiveMonoMs;
    this.authority = clone(message.warnings || []);
    this.lastDiag = null;
    this.attachState = 'PAIRED';
    this.hudLoadAllowed = true;
    return true;
  }

  visibleWarnings(nowMonoMs) {
    if (this.lastReceiveMonoMs === null || !Number.isFinite(nowMonoMs)) return [];
    if (nowMonoMs - this.lastReceiveMonoMs > this.staleMs) return [];
    return clone(this.authority);
  }

  hudOutput(nowMonoMs) {
    const warnings = this.visibleWarnings(nowMonoMs);
    return {
      schema: CONTRACT.applicationSchema,
      release: CONTRACT.release,
      transportVersion: CONTRACT.transportVersion,
      session: this.session,
      pairGeneration: this.generation,
      attachState: this.attachState,
      hudLoadAllowed: this.hudLoadAllowed,
      stale: this.lastReceiveMonoMs === null ? true : (nowMonoMs - this.lastReceiveMonoMs > this.staleMs),
      warnings,
      diagnostic: clone(this.lastDiag)
    };
  }

  status() {
    return {
      session: this.session,
      pairGeneration: this.generation,
      pairNonce: this.nonce,
      lastSeq: this.lastSeq,
      attachState: this.attachState,
      hudLoadAllowed: this.hudLoadAllowed,
      warningCount: this.authority.length,
      lastDiag: clone(this.lastDiag)
    };
  }
}
