'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const {
  PlayerAnchorResolver,
  TargetLockIndicatorRouter,
  AnchoredWarningRenderer,
} = require('../HUDANCHOR_PLAYER_FOLLOW/src/player_follow_reference');

const W = 384;
const H = 224;

function player(x = 40, y = 20, z = 0, o = {}) {
  return {
    present: o.present !== false,
    x, y, z,
    sampleAtMs: o.sampleAtMs ?? 1000,
    epoch: o.epoch ?? 'e1',
    lifecycleId: o.lifecycleId ?? 'life-1',
    confidence: 1,
  };
}

function db(o = {}) {
  const width = o.width ?? 768;
  const height = o.height ?? 448;
  return {
    width,
    height,
    sampleAtMs: o.sampleAtMs ?? 1000,
    epoch: o.epoch ?? 'e1',
    confidence: 1,
    dpr: o.dpr ?? 1,
    fullscreen: !!o.fullscreen,
    mappingVersion: o.mappingVersion ?? 'm1',
    contentRect: o.contentRect ?? { x: 0, y: 0, width, height },
  };
}

function proj(fn, o = {}) {
  return {
    source: 'fresh-independent-bounds-qa',
    version: o.version ?? 'p1',
    epoch: o.epoch ?? 'e1',
    sampleAtMs: o.sampleAtMs ?? 1000,
    nativeWidth: o.nativeWidth ?? W,
    nativeHeight: o.nativeHeight ?? H,
    confidence: 1,
    camera: o.camera ?? null,
    validationBounds: o.validationBounds ?? { minX: 0, maxX: W, minY: 0, maxY: H },
    projectNative: fn,
  };
}

function point(ax, ay, bx = 192, by = 112, o = {}) {
  return proj(() => ({ anchorXNative: ax, anchorYNative: ay, bodyXNative: bx, bodyYNative: by, confidence: 1 }), o);
}

function warning(sourceId, targetPlayer, priority = 1) {
  return { sourceId, targetPlayer, priority, active: true, visible: true, label: sourceId };
}

function route(router, nowMs, targets, warnings) {
  return router.route({ nowMs, targets, warnings });
}

function oneRouted(router, nowMs, p = 'P1', sourceId = 'enemy-A') {
  return route(router, nowMs, { [sourceId]: p }, [warning(sourceId, p)]);
}

function build({ renderer, projectionState, routed, players, drawingBufferState = db(), nowMs = 1000, cameraDiscontinuity = false }) {
  return renderer.buildPlan({ nowMs, routed, players, projectionState, drawingBufferState, cameraDiscontinuity });
}

function freshRenderer(opts = {}) {
  return new AnchoredWarningRenderer({ resolver: new PlayerAnchorResolver(), ...opts });
}

function expectFixed(p, reason = 'PROJECTION_OUT_OF_BOUNDS') {
  const renderer = freshRenderer();
  const router = new TargetLockIndicatorRouter();
  const plan = build({ renderer, projectionState: p, routed: oneRouted(router, 1000), players: { P1: player() } });
  assert.equal(plan.anchored.length, 0);
  assert.equal(plan.fixed.length, 1);
  assert.equal(plan.fixed[0].reason, reason);
  assert.equal(renderer.follow.state.has('P1'), false);
  return plan;
}

const tests = [];
function test(name, fn) { tests.push({ name, fn }); }

test('1 X below zero rejects anchored cue', () => {
  expectFixed(point(-Number.EPSILON, 80));
});

test('2 X exactly nativeWidth and beyond reject', () => {
  expectFixed(point(W, 80));
  expectFixed(point(W + 0.001, 80));
});

test('3 Y below zero rejects anchored cue', () => {
  expectFixed(point(192, -Number.EPSILON));
});

test('4 Y exactly nativeHeight and beyond reject', () => {
  expectFixed(point(192, H));
  expectFixed(point(192, H + 0.001));
});

test('5 body valid but final head anchor invalid never edge-clamps as anchored', () => {
  const plan = expectFixed(point(192, -1000000, 192, 112));
  assert.equal(plan.anchored.length, 0);
});

test('6 valid near-edge anchor stays anchored while warning rectangle clamps', () => {
  const renderer = freshRenderer({ boxWidth: 120, boxHeight: 40 });
  const router = new TargetLockIndicatorRouter();
  const plan = build({
    renderer,
    projectionState: point(W - 1e-9, H - 1e-9),
    routed: oneRouted(router, 1000),
    players: { P1: player() },
  });
  assert.equal(plan.fixed.length, 0);
  assert.equal(plan.anchored.length, 1);
  const a = plan.anchored[0];
  assert.equal(a.anchor.ok, true);
  assert.equal(a.drawRectDb.x, 648);
  assert.equal(a.drawRectDb.y, 408);
  assert.ok(a.followPointDb.x > a.drawRectDb.x);
  assert.ok(a.followPointDb.y > a.drawRectDb.y);
});

test('7 valid -> invalid clears smoothing; next valid cannot reuse old coordinate', () => {
  let ax = 100;
  const p = proj(() => ({ anchorXNative: ax, anchorYNative: 80, bodyXNative: 192, bodyYNative: 112, confidence: 1 }));
  const renderer = freshRenderer({ smoothingAlpha: 0.1 });
  const router = new TargetLockIndicatorRouter({ holdMs: 1000 });
  const routed = oneRouted(router, 1000);
  let plan = build({ renderer, projectionState: p, routed, players: { P1: player() } });
  const oldX = plan.anchored[0].followPointDb.x;
  ax = -1;
  plan = build({ renderer, projectionState: p, routed, players: { P1: player() } });
  assert.equal(plan.anchored.length, 0);
  assert.equal(plan.fixed[0].reason, 'PROJECTION_OUT_OF_BOUNDS');
  assert.equal(renderer.follow.state.has('P1'), false);
  ax = 250;
  plan = build({ renderer, projectionState: p, routed, players: { P1: player() } });
  assert.equal(plan.anchored.length, 1);
  assert.equal(plan.anchored[0].smoothingReset, true);
  assert.equal(plan.anchored[0].followPointDb.x, plan.anchored[0].anchor.xDb);
  assert.notEqual(plan.anchored[0].followPointDb.x, oldX);
});

test('8 retarget P1->P2->P3 drops old target immediately; invalid new target only fixed-fallbacks', () => {
  const p = proj(({ player: who }) => ({
    anchorXNative: who === 'P1' ? 100 : who === 'P2' ? W : 220,
    anchorYNative: 80,
    bodyXNative: 192,
    bodyYNative: 112,
    confidence: 1,
  }));
  const renderer = freshRenderer({ smoothingAlpha: 0.2 });
  const router = new TargetLockIndicatorRouter({ holdMs: 1000 });
  let routed = oneRouted(router, 1000, 'P1');
  let plan = build({ renderer, projectionState: p, routed, players: { P1: player(), P2: player(), P3: player() } });
  assert.deepEqual(plan.anchored.map(x => x.player), ['P1']);
  routed = oneRouted(router, 1010, 'P2');
  assert.ok(routed.invalidated.some(x => x.player === 'P1' && x.reason === 'RETARGET'));
  plan = build({ renderer, projectionState: { ...p, sampleAtMs: 1010 }, routed, players: { P1: player(40,20,0,{sampleAtMs:1010}), P2: player(40,20,0,{sampleAtMs:1010}), P3: player(40,20,0,{sampleAtMs:1010}) }, drawingBufferState: db({sampleAtMs:1010}), nowMs: 1010 });
  assert.equal(plan.anchored.length, 0);
  assert.deepEqual(plan.fixed.map(x => x.player), ['P2']);
  assert.equal(renderer.follow.state.has('P1'), false);
  routed = oneRouted(router, 1020, 'P3');
  assert.ok(routed.invalidated.some(x => x.player === 'P2' && x.reason === 'RETARGET'));
  plan = build({ renderer, projectionState: { ...p, sampleAtMs: 1020 }, routed, players: { P1: player(40,20,0,{sampleAtMs:1020}), P2: player(40,20,0,{sampleAtMs:1020}), P3: player(40,20,0,{sampleAtMs:1020}) }, drawingBufferState: db({sampleAtMs:1020}), nowMs: 1020 });
  assert.deepEqual(plan.anchored.map(x => x.player), ['P3']);
  assert.equal(plan.fixed.length, 0);
});

test('9 nonfinite projection and malformed/zero/negative viewport dimensions fail closed', () => {
  expectFixed(point(NaN, 80), 'PROJECTION_NONFINITE');
  expectFixed(point(100, Infinity), 'PROJECTION_NONFINITE');
  expectFixed(point(100, 80, NaN, 112), 'PROJECTION_NONFINITE');
  expectFixed(point(100, 80, 192, Infinity), 'PROJECTION_NONFINITE');
  expectFixed(point(100, 80, 192, 112, { nativeWidth: 0 }), 'INVALID_NATIVE_VIEWPORT');
  expectFixed(point(100, 80, 192, 112, { nativeHeight: -1 }), 'INVALID_NATIVE_VIEWPORT');
  const renderer = freshRenderer();
  const router = new TargetLockIndicatorRouter();
  for (const bad of [db({ width: 0 }), db({ height: 0 }), db({ width: -1 }), db({ height: -1 }), db({ contentRect: {x:0,y:0,width:NaN,height:10} })]) {
    const plan = build({ renderer, projectionState: point(100,80), routed: oneRouted(router,1000), players: {P1:player()}, drawingBufferState: bad });
    assert.equal(plan.anchored.length, 0);
    assert.equal(plan.fixed.length, 1);
    assert.equal(plan.fixed[0].reason, 'INVALID_DRAWING_BUFFER');
  }
});

test('10 resize/fullscreen/DPR discontinuity resets mapping and never smooths from pre-change coordinates', () => {
  const renderer = freshRenderer({ smoothingAlpha: 0.05 });
  const router = new TargetLockIndicatorRouter({ holdMs: 1000 });
  const routed = oneRouted(router, 1000);
  const p = point(100, 80);
  let plan = build({ renderer, projectionState: p, routed, players: { P1: player() }, drawingBufferState: db({ width: 768, height: 448, dpr: 1, mappingVersion: 'm1' }) });
  const a = plan.anchored[0];
  plan = build({ renderer, projectionState: p, routed, players: { P1: player() }, drawingBufferState: db({ width: 1152, height: 672, dpr: 1.5, fullscreen: true, mappingVersion: 'm2' }) });
  const b = plan.anchored[0];
  assert.equal(b.smoothingReset, true);
  assert.notEqual(a.anchor.mappingKey, b.anchor.mappingKey);
  assert.equal(b.followPointDb.x, b.anchor.xDb);
  assert.equal(b.followPointDb.y, b.anchor.yDb);
  assert.notEqual(a.followPointDb.x, b.followPointDb.x);
});

test('11 camera discontinuity, respawn and lifecycle/object replacement reset follow state', () => {
  const renderer = freshRenderer({ smoothingAlpha: 0.05 });
  const router = new TargetLockIndicatorRouter({ holdMs: 1000 });
  const routed = oneRouted(router, 1000);
  let p = point(100, 80);
  build({ renderer, projectionState: p, routed, players: { P1: player(40,20,0,{lifecycleId:'life-1'}) } });
  p = point(200, 80);
  let plan = build({ renderer, projectionState: p, routed, players: { P1: player(40,20,0,{lifecycleId:'life-1'}) }, cameraDiscontinuity: true });
  assert.equal(plan.anchored[0].smoothingReset, true);
  assert.equal(plan.anchored[0].followPointDb.x, plan.anchored[0].anchor.xDb);
  p = point(260, 80);
  plan = build({ renderer, projectionState: p, routed, players: { P1: player(40,20,0,{lifecycleId:'life-2'}) } });
  assert.equal(plan.anchored[0].smoothingReset, true);
  assert.equal(plan.anchored[0].followPointDb.x, plan.anchored[0].anchor.xDb);
  plan = build({ renderer, projectionState: p, routed, players: { P1: player(40,20,0,{present:false,lifecycleId:'life-2'}) } });
  assert.equal(plan.anchored.length, 0);
  assert.equal(plan.fixed[0].reason, 'PLAYER_ABSENT');
  assert.equal(renderer.follow.state.has('P1'), false);
});

test('12 rapid alternating valid/out-of-bounds transitions never leave stale edge cue', () => {
  let ax = 100;
  const p = proj(() => ({ anchorXNative: ax, anchorYNative: 80, bodyXNative: 192, bodyYNative: 112, confidence: 1 }));
  const renderer = freshRenderer({ smoothingAlpha: 0.1, boxWidth: 120 });
  const router = new TargetLockIndicatorRouter({ holdMs: 5000 });
  const routed = oneRouted(router, 1000);
  const seq = [100, -1, W - 0.01, W, 200, W + 1, 0, -999, 383.999, Infinity, 150];
  for (const value of seq) {
    ax = value;
    const plan = build({ renderer, projectionState: p, routed, players: { P1: player() } });
    const valid = Number.isFinite(value) && value >= 0 && value < W;
    if (valid) {
      assert.equal(plan.anchored.length, 1, `expected anchored for ${value}`);
      assert.equal(plan.fixed.length, 0);
    } else {
      assert.equal(plan.anchored.length, 0, `stale anchored cue for ${value}`);
      assert.equal(plan.fixed.length, 1);
      assert.equal(renderer.follow.state.has('P1'), false);
    }
  }
});

test('13 simultaneous P1/P2/P3 routing and same-player aggregation remain intact', () => {
  const router = new TargetLockIndicatorRouter({ holdMs: 100 });
  const routed = route(router, 1000,
    { a:'P1', b:'P2', c:'P3', d:'P2' },
    [warning('a','P1',1), warning('b','P2',2), warning('c','P3',1), warning('d','P2',9)]);
  assert.deepEqual(routed.byPlayer.map(x => x.player), ['P1','P2','P3']);
  const p2 = routed.byPlayer.find(x => x.player === 'P2');
  assert.equal(p2.threatCount, 2);
  assert.equal(p2.warning.sourceId, 'd');
  assert.deepEqual(new Set(p2.sourceIds), new Set(['b','d']));
});

test('14 presentation path remains read-only: only frame/draw adapter calls and no gameplay/RAM write primitives', () => {
  const source = fs.readFileSync(require.resolve('../HUDANCHOR_PLAYER_FOLLOW/src/player_follow_reference'), 'utf8');
  for (const forbidden of [
    'WriteProcessMemory', 'writeProcessMemory', 'writeMemory', 'memory.write',
    'SendInput', 'keybd_event', 'mouse_event', 'dispatchEvent(new KeyboardEvent',
    'postMessage({type:"input"', 'setValue(', 'poke(', 'patchMemory'
  ]) {
    assert.equal(source.includes(forbidden), false, `forbidden primitive found: ${forbidden}`);
  }
  const renderer = freshRenderer();
  const router = new TargetLockIndicatorRouter();
  const plan = build({ renderer, projectionState: point(100,80), routed: oneRouted(router,1000), players: {P1:player()} });
  const calls = [];
  const adapter = {
    beginFrame() { calls.push('beginFrame'); },
    drawAnchored() { calls.push('drawAnchored'); },
    drawFixed() { calls.push('drawFixed'); },
    endFrame() { calls.push('endFrame'); },
  };
  renderer.executePlan(plan, adapter);
  assert.deepEqual(calls, ['beginFrame','drawAnchored','endFrame']);
});

test('15 invalid validation bounds fail closed', () => {
  expectFixed(point(100,80,192,112,{validationBounds:{minX:NaN,maxX:W,minY:0,maxY:H}}), 'INVALID_VALIDATION_BOUNDS');
});

test('16 projection version change resets smoothing', () => {
  const renderer = freshRenderer({ smoothingAlpha: 0.01 });
  const router = new TargetLockIndicatorRouter({ holdMs: 1000 });
  const routed = oneRouted(router,1000);
  build({renderer, projectionState:point(100,80,192,112,{version:'v1'}), routed, players:{P1:player()}});
  const plan = build({renderer, projectionState:point(250,80,192,112,{version:'v2'}), routed, players:{P1:player()}});
  assert.equal(plan.anchored[0].smoothingReset,true);
  assert.equal(plan.anchored[0].followPointDb.x, plan.anchored[0].anchor.xDb);
});

test('17 epoch discontinuity fails closed and clears prior follow state', () => {
  const renderer = freshRenderer({smoothingAlpha:0.2});
  const router = new TargetLockIndicatorRouter({holdMs:1000});
  const routed = oneRouted(router,1000);
  let plan = build({renderer, projectionState:point(100,80), routed, players:{P1:player()}, drawingBufferState:db()});
  assert.equal(plan.anchored.length,1);
  plan = build({renderer, projectionState:point(100,80,192,112,{epoch:'e2'}), routed, players:{P1:player(40,20,0,{epoch:'e1'})}, drawingBufferState:db({epoch:'e2'})});
  assert.equal(plan.anchored.length,0);
  assert.equal(plan.fixed[0].reason,'EPOCH_MISMATCH');
  assert.equal(renderer.follow.state.has('P1'),false);
});

test('18 stale projection/drawing-buffer samples fail closed instead of reusing old coordinate', () => {
  const renderer = new AnchoredWarningRenderer({resolver:new PlayerAnchorResolver({maxProjectionAgeMs:100,maxDrawingBufferAgeMs:100}), smoothingAlpha:0.2});
  const router = new TargetLockIndicatorRouter({holdMs:1000});
  const routed = oneRouted(router,1000);
  let plan = build({renderer, projectionState:point(100,80), routed, players:{P1:player()}, drawingBufferState:db()});
  assert.equal(plan.anchored.length,1);
  plan = build({renderer, projectionState:point(100,80,192,112,{sampleAtMs:800}), routed, players:{P1:player()}, drawingBufferState:db(), nowMs:1000});
  assert.equal(plan.anchored.length,0);
  assert.equal(plan.fixed[0].reason,'STALE_PROJECTION');
  assert.equal(renderer.follow.state.has('P1'),false);
  plan = build({renderer, projectionState:point(100,80), routed, players:{P1:player()}, drawingBufferState:db({sampleAtMs:800}), nowMs:1000});
  assert.equal(plan.anchored.length,0);
  assert.equal(plan.fixed[0].reason,'STALE_DRAWING_BUFFER');
});

let passed = 0;
for (const {name, fn} of tests) {
  fn();
  passed++;
  console.log(`PASS ${name}`);
}
console.log(JSON.stringify({status:'PASS', passed, total:tests.length, fixture:'FRESH_INDEPENDENT_SYNTHETIC_BOUNDS_QA_NOT_BROWSER_PROOF'}));
