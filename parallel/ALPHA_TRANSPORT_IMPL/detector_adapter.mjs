import { CONTRACT, validateSnapshot, validateWarningRows, clone } from './constants.mjs';

export class AlphaDetectorAdapter {
  constructor(core) {
    if (!core || core.VERSION !== CONTRACT.coreVersion || core.SCHEMA !== CONTRACT.applicationSchema || typeof core.createEngine !== 'function') {
      throw new Error('canonical Alpha core identity mismatch');
    }
    this.core = core;
    this.engine = core.createEngine();
  }

  evaluate(snapshot) {
    const check = validateSnapshot(snapshot);
    if (!check.ok) throw new Error(`invalid detector snapshot: ${check.reason}`);
    const state = this.engine.step(snapshot.enemies, snapshot.sampledAtMonoMs);
    const warnings = validateWarningRows(state?.warnings || []);
    if (!warnings.ok) throw new Error(`canonical core emitted invalid warning rows: ${warnings.reason}`);
    return {
      schema: CONTRACT.applicationSchema,
      kind: 'state',
      coreVersion: CONTRACT.coreVersion,
      sentAt: state.sentAt,
      warnings: clone(state.warnings || [])
    };
  }

  reset() {
    this.engine.reset();
  }

  diagnostics() {
    return this.engine.diagnostics?.() || null;
  }
}
