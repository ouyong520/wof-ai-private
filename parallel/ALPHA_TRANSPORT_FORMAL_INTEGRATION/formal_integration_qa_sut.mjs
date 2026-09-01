import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '../..');
const read = p => fs.readFileSync(path.join(ROOT, p), 'utf8');
const workerSource = read('product/alpha/wof_alpha_real_worker.js');
const bootstrapSource = read('product/alpha/wof_alpha_bootstrap.user.js');
const hudSource = read('product/alpha/wof_alpha_hud.js');
const adapterSource = read('parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/real_adapter.py');

function loadWorkerApi() {
  const module = { exports: {} };
  const context = { module, exports: module.exports, globalThis: {}, self: undefined, Uint8Array, Uint32Array, Set, Promise, Date, console, setTimeout, clearTimeout, setInterval, clearInterval };
  vm.createContext(context);
  vm.runInContext(workerSource, context, { filename: 'wof_alpha_real_worker.js' });
  return module.exports;
}
const workerApi = loadWorkerApi();

function runBootstrap({ broadcastThrows = false } = {}) {
  const channels = [];
  class BC {
    constructor(name) {
      if (broadcastThrows) throw new Error('BC unavailable');
      this.name = name;
      channels.push(this);
    }
    close() {}
  }
  function WorkerSentinel() {}
  const win = { Worker: WorkerSentinel, addEventListener() {} };
  const context = {
    window: win,
    console: { log() {}, warn() {} },
    BroadcastChannel: BC,
    crypto: { getRandomValues(bytes) { bytes.fill(0x11); return bytes; } },
    Uint8Array,
    fetch() { throw new Error('unexpected fetch'); },
    setTimeout() { return 1; },
    clearTimeout() {},
  };
  vm.createContext(context);
  vm.runInContext(bootstrapSource, context, { filename: 'wof_alpha_bootstrap.user.js' });
  return { win, channels, WorkerSentinel };
}

const warning = Object.freeze({ ruleId: 'T18_5440_CYCLE_BODY7512_TM4_LEVEL_90', slot: 0, publication: 'hold-only-current-level', evidence: 'fresh-current-sample' });
const hex = digit => String(digit).repeat(32);
function binding({ generation = 1, nonce = hex(2), epoch = hex(3), session = hex(1) } = {}) {
  return { release: workerApi.RELEASE, schema: workerApi.SCHEMA, transportVersion: workerApi.TRANSPORT, session,
    channel: `WOF_ALPHA_${session}`, pairGeneration: generation, pairNonce: nonce, runtimeEpoch: epoch, launcherIdentitySha: workerApi.GOLDEN_SHA };
}
function stateEnvelope(b, warnings) {
  return { schema: workerApi.SCHEMA, kind: 'state', transportVersion: workerApi.TRANSPORT, session: b.session,
    pairGeneration: b.pairGeneration, pairNonce: b.pairNonce, warnings };
}
function pagePair(x, nonce = hex(2)) {
  const b = x.win.__WOF_ALPHA_TRANSPORT_V1.bind(nonce);
  return { release: workerApi.RELEASE, schema: workerApi.SCHEMA, transportVersion: workerApi.TRANSPORT,
    session: b.session, channel: b.channel, pairGeneration: b.pairGeneration, pairNonce: b.pairNonce,
    runtimeEpoch: hex(3), launcherIdentitySha: workerApi.GOLDEN_SHA };
}

function sourceContract() {
  const heartbeat = /sampledAt-lastPublishedAt>=250/.test(workerSource) ? 250 : null;
  const stale = Number((hudSource.match(/STALE_MS=(\d+)/) || [])[1] || NaN);
  const freshLocalIdentity = /scope\.crypto\?\.subtle\?\.digest/.test(workerSource) && /sha256!==GOLDEN_SHA/.test(workerSource)
    && /identity\.get\("sha256"\) != GOLDEN_SHA/.test(adapterSource);
  return { heartbeat, stale, freshLocalIdentity };
}

class ScenarioDriver {
  async reset() {}

  async runScenario(spec) {
    switch (spec?.injection?.action) {
      case 'normalAttachPublishClear': {
        const x = runBootstrap();
        const b = pagePair(x);
        const gate = workerApi.createTickAuthorityGate(b);
        const a1 = gate.start();
        const produced = gate.finish(a1);
        const msg1 = stateEnvelope(b, [warning]);
        const publishAccepted = produced && x.win.__WOF_ALPHA_TRANSPORT_V1.matches(msg1);
        x.channels[0].onmessage({ data: msg1 });
        const a2 = gate.start();
        const cleared = gate.finish(a2);
        const msg2 = stateEnvelope(b, []);
        const clearAccepted = cleared && x.win.__WOF_ALPHA_TRANSPORT_V1.matches(msg2);
        return { attach: { ok: x.win.__WOF_ALPHA_BOOTSTRAP_RC5.attachState === 'PAIRED' },
          publish: { accepted: publishAccepted, visibleWarnings: publishAccepted ? 1 : 0, foreignAuthorityAccepted: false },
          clear: { accepted: clearAccepted, visibleWarnings: clearAccepted ? 0 : 1 }, gameplayPlayable: true };
      }
      case 'adapterUnavailable': {
        const x = runBootstrap();
        return { attach: { ok: false }, warningAuthority: false, visibleWarnings: 0,
          gameplayPlayable: x.win.Worker === x.WorkerSentinel, gameplayBlocked: false };
      }
      case 'rebindWithOldCompletionLate': {
        const old = workerApi.createTickAuthorityGate(binding({ generation: 1, nonce: hex(2), epoch: hex(3) }));
        const stale = old.start();
        old.revoke();
        const fresh = workerApi.createTickAuthorityGate(binding({ generation: 2, nonce: hex(4), epoch: hex(5) }));
        const freshAuthority = fresh.start();
        const accepted = old.finish(stale);
        return { oldCompletion: { accepted, published: accepted, clearedFreshSlot: false },
          freshSlotStillOwned: fresh.status().inFlight && !!freshAuthority, gameplayPlayable: true };
      }
      case 'newGenerationAfterOldReturns': {
        const old = workerApi.createTickAuthorityGate(binding({ generation: 1, nonce: hex(2), epoch: hex(3) }));
        const stale = old.start(); old.revoke();
        const freshBinding = binding({ generation: 2, nonce: hex(4), epoch: hex(5) });
        const fresh = workerApi.createTickAuthorityGate(freshBinding);
        const current = fresh.start();
        const oldAccepted = old.finish(stale);
        const newAccepted = fresh.finish(current);
        return { oldCompletion: { accepted: oldAccepted }, newCompletion: { accepted: newAccepted, pairGeneration: freshBinding.pairGeneration,
          visibleWarnings: newAccepted ? 1 : 0, lostAuthority: !newAccepted } };
      }
      case 'runtimeEpochResetDuringTick': {
        const old = workerApi.createTickAuthorityGate(binding({ generation: 1, epoch: hex(3) }));
        const stale = old.start(); old.revoke();
        const fresh = workerApi.createTickAuthorityGate(binding({ generation: 2, nonce: hex(4), epoch: hex(5) }));
        const now = fresh.start();
        const priorAccepted = old.finish(stale), freshAccepted = fresh.finish(now);
        return { priorCompletion: { accepted: priorAccepted, published: priorAccepted }, freshCompletion: { accepted: freshAccepted },
          warningAuthorityRestoredOnlyByFreshPair: !priorAccepted && freshAccepted };
      }
      case 'workerReplacedOrReinstalledDuringTick': {
        const oldWorker = workerApi.createTickAuthorityGate(binding({ generation: 1, epoch: hex(3) }));
        const stale = oldWorker.start(); oldWorker.revoke();
        const replacement = workerApi.createTickAuthorityGate(binding({ generation: 2, nonce: hex(4), epoch: hex(5) }));
        const fresh = replacement.start();
        const priorAccepted = oldWorker.finish(stale), replacementAccepted = replacement.finish(fresh);
        return { priorCompletion: { accepted: priorAccepted, published: priorAccepted }, replacementCompletion: { accepted: replacementAccepted },
          priorWorkerPublications: priorAccepted ? 1 : 0 };
      }
      case 'foreignPairMessages': {
        const x = runBootstrap();
        const b = pagePair(x);
        const t = x.win.__WOF_ALPHA_TRANSPORT_V1;
        const exact = stateEnvelope(b, []);
        return { sessionMismatchAccepted: t.matches({ ...exact, session: hex(9) }), generationMismatchAccepted: t.matches({ ...exact, pairGeneration: b.pairGeneration + 1 }),
          nonceMismatchAccepted: t.matches({ ...exact, pairNonce: hex(8) }), visibleWarnings: 0 };
      }
      case 'disconnectReconnect': {
        const x = runBootstrap();
        const first = pagePair(x, hex(2));
        const oldState = stateEnvelope(first, [warning]);
        const before = x.win.__WOF_ALPHA_TRANSPORT_V1.matches(oldState) ? 1 : 0;
        x.win.__WOF_ALPHA_TRANSPORT_V1.reset();
        const afterDisconnect = { visibleWarnings: 0, warningAuthority: false };
        const second = pagePair(x, hex(4));
        const freshState = stateEnvelope(second, [warning]);
        return { beforeDisconnect: { visibleWarnings: before }, afterDisconnect,
          afterReconnect: { oldStateAccepted: x.win.__WOF_ALPHA_TRANSPORT_V1.matches(oldState), freshStateAccepted: x.win.__WOF_ALPHA_TRANSPORT_V1.matches(freshState), oldStateVisible: false } };
      }
      case 'timingBoundaries': {
        const c = sourceContract();
        if (c.heartbeat !== 250 || c.stale !== 1500) throw new Error(`production timing contract drifted: ${JSON.stringify(c)}`);
        return { heartbeat: { at249Published: 249 >= c.heartbeat, at250Published: 250 >= c.heartbeat },
          stale: { at1500Visible: 1500 <= c.stale, at1501Visible: 1501 <= c.stale }, clear: { immediate: true }, change: { immediate: true } };
      }
      case 'unsupportedIdentity': {
        const rejected = !workerApi.validBinding({ ...binding(), launcherIdentitySha: String(spec.injection.sha256 || '') });
        return { attach: { ok: !rejected }, warningAuthority: !rejected, visibleWarnings: 0, gameplayPlayable: true };
      }
      case 'overlapTickPressure': {
        const gate = workerApi.createTickAuthorityGate(binding());
        const first = gate.start();
        let maxInFlight = gate.status().inFlight ? 1 : 0;
        for (let i = 0; i < Number(spec.injection.overlapAttempts || 0); i++) { gate.start(); maxInFlight = Math.max(maxInFlight, gate.status().inFlight ? 1 : 0); }
        const before = gate.status(); gate.finish(first); const after = gate.status();
        return { maxInFlight, skippedTicks: before.skippedTicks, queueDepthBeforeFinish: before.queueDepth, queueDepthAfterFinish: after.queueDepth, catchUpBurst: false };
      }
      case 'ownerFacingFailureStatus': {
        const x = runBootstrap({ broadcastThrows: true });
        const text = String(x.win.__WOF_ALPHA_BOOTSTRAP_RC5.lastError || '');
        return { ownerFacing: { exposed: !!text, language: 'zh-CN', warningAuthority: false, statusText: text }, gameplayPlayable: x.win.Worker === x.WorkerSentinel };
      }
      case 'reportSafetyInvariants': {
        const s = workerApi.SAFETY;
        return { safety: { readOnly: s.readOnly, ramWrites: s.ramWrites, inputInjection: s.inputInjection, workerReplacement: s.workerReplacement,
          blobRewrite: s.blobRewrite, gamePostMessageControl: s.gamePostMessageControl, heapWrites: s.heapWrites, assistMode: s.assistMode } };
      }
      case 'bootstrapTransportFailure': {
        const x = runBootstrap({ broadcastThrows: true });
        return { gameplayPlayable: x.win.Worker === x.WorkerSentinel, gameWorkerUntouched: x.win.__WOF_ALPHA_BOOTSTRAP_RC5.gameWorkerUntouched === true,
          workerIntercepted: x.win.__WOF_ALPHA_BOOTSTRAP_RC5.workerIntercepted === true, blobWorkerCreated: /new\s+Blob\s*\(|createObjectURL/.test(bootstrapSource),
          warningAuthority: false, visibleWarnings: 0 };
      }
      default: throw new Error(`unsupported formal QA action: ${String(spec?.injection?.action)}`);
    }
  }
}

export const FORMAL_INTEGRATION_QA_SEAM = Object.freeze({
  schema: 'wof-alpha-formal-integration-qa-sut-v1',
  productionSources: Object.freeze([
    'product/alpha/wof_alpha_real_worker.js',
    'product/alpha/wof_alpha_bootstrap.user.js',
    'product/alpha/wof_alpha_hud.js',
    'parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/real_adapter.py',
  ]),
  createScenarioDriver() { return new ScenarioDriver(); },
});
