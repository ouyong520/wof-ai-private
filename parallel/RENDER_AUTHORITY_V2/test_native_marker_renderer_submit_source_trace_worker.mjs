import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

const sourceCode = fs.readFileSync(new URL("./native_marker_renderer_submit_source_trace_worker.js", import.meta.url), "utf8");

function makeContext() {
  const timers = new Map();
  let nextTimer = 1;
  const context = {
    console,
    structuredClone,
    setTimeout(fn) { const id = nextTimer++; timers.set(id, fn); return id; },
    clearTimeout(id) { timers.delete(id); },
  };
  context.globalThis = context;
  context.self = context;
  vm.createContext(context);
  vm.runInContext(sourceCode, context);
  return context;
}

const binding = {
  runtimeEpoch: "runtime-epoch-0001",
  rendererEpoch: "renderer-epoch-001",
  authorityKey: "authority-key",
};

function makeBridge() {
  let observer = null;
  let stopped = false;
  return {
    schema: "wof-native-marker-renderer-submit-source-v1",
    derivationKind: "DIRECT_RENDER_HOOK",
    guessed: false,
    displayedFrameCausalLink: true,
    coordinateAuthority: "NATIVE_RENDERER_OBJECT_384X224",
    screenshotCoordinatesUsed: false,
    ocrCoordinatesUsed: false,
    templateCoordinatesUsed: false,
    worldProjectionCoordinatesUsed: false,
    sourceTrace: ["Cps1ObjDraw source-traced submit", "displayed CPS1 frame"],
    instrumentationId: "p36-node-test",
    hookSite: "exact CPS1 displayed object submit",
    readOnly: true,
    ramWrites: 0,
    inputInjection: false,
    ownerSelectionRequired: false,
    manualSeedRequired: false,
    subscribe(fn, gotBinding) {
      assert.deepEqual(gotBinding, binding);
      observer = fn;
      return () => { stopped = true; };
    },
    emit(event) { return observer(event); },
    stopped() { return stopped; },
  };
}

function makeEvent(index) {
  return {
    schema: "wof-native-marker-renderer-submit-event-v1",
    ...binding,
    frameGeneration: 100 + index,
    displayedFrameId: `display-${index}`,
    submissionId: `submit-${index}`,
    displayedFrameCausalLink: true,
    coordinateAuthority: "NATIVE_RENDERER_OBJECT_384X224",
    guessed: false,
    actorAssociation: {
      player: "P1",
      generation: 7,
      explicit: true,
      generationBound: true,
      ambiguous: false,
      candidateCount: 1,
      guessed: false,
    },
    marker: {
      player: "P1",
      generation: 7,
      labelSemantic: "1P",
      clusterKey: "p1:g7",
      clusterJoin: { explicit: true, guessed: false, key: "p1:g7" },
      actorAssociation: {
        player: "P1",
        generation: 7,
        explicit: true,
        generationBound: true,
        ambiguous: false,
        candidateCount: 1,
        guessed: false,
      },
      members: [{
        memberKey: "arrow",
        semanticRole: "DOWN_ARROW",
        clusterKey: "p1:g7",
        guessed: false,
        anchorPoint: { x: 108, y: 72 },
      }],
    },
  };
}

{
  const context = makeContext();
  const api = context.WOFNATIVEMARKERSUBMITSOURCETRACEV1;
  const status = api.start(binding);
  assert.equal(status.state, "BLOCKED");
  assert.equal(status.reason, "EXACT_DIRECT_RENDERER_SOURCE_SURFACE_NOT_EXPOSED");
  assert.equal(status.blocker, "NATIVE_PLAYER_MARKER_DIRECT_RENDERER_CAUSAL_EDGE_NOT_CHECKED_IN");
  assert.equal(status.ownerSelectionRequired, false);
  assert.equal(status.manualSeedRequired, false);
}

{
  const context = makeContext();
  const bridge = makeBridge();
  context.__WOF_NATIVE_MARKER_RENDERER_SUBMIT_SOURCE_V1__ = bridge;
  const api = context.WOFNATIVEMARKERSUBMITSOURCETRACEV1;
  const started = api.start(binding);
  assert.equal(started.state, "OBSERVING");
  assert.equal(started.ownerSelectionRequired, false);
  assert.equal(started.manualSeedRequired, false);
  for (const i of [3, 1, 2]) bridge.emit(makeEvent(i));
  const sealed = api.seal("TEST_SEAL");
  assert.equal(sealed.state, "CAPTURE_READY");
  assert.equal(sealed.eventCount, 3);
  const result = api.result();
  assert.equal(result.source.derivationKind, "DIRECT_RENDER_HOOK");
  assert.equal(result.events.length, 3);
  assert.equal(result.readOnly, true);
  assert.equal(result.ramWrites, 0);
  assert.equal(result.inputInjection, false);
  assert.equal(bridge.stopped(), true);
}

{
  const context = makeContext();
  const bridge = makeBridge();
  context.__WOF_NATIVE_MARKER_RENDERER_SUBMIT_SOURCE_V1__ = bridge;
  const api = context.WOFNATIVEMARKERSUBMITSOURCETRACEV1;
  api.start(binding);
  const stale = makeEvent(1);
  stale.rendererEpoch = "stale";
  bridge.emit(stale);
  const status = api.status();
  assert.equal(status.state, "REJECTED");
  assert.equal(status.reason, "STALE_OR_MIXED_AUTHORITY_BINDING");
  assert.equal(status.blocker, "NATIVE_PLAYER_MARKER_DIRECT_RENDERER_CAUSAL_EDGE_NOT_CHECKED_IN");
}

{
  const context = makeContext();
  const a = makeBridge();
  const b = makeBridge();
  b.instrumentationId = "second";
  context.__WOF_NATIVE_MARKER_RENDERER_SUBMIT_SOURCE_V1__ = a;
  context.Module = { WOFNativeMarkerRendererSubmitSourceV1: b };
  const api = context.WOFNATIVEMARKERSUBMITSOURCETRACEV1;
  const status = api.start(binding);
  assert.equal(status.state, "BLOCKED");
  assert.equal(status.reason, "AMBIGUOUS_DIRECT_RENDERER_SOURCE_SURFACE");
}

console.log("P36 native marker renderer submit source trace worker: PASS");
