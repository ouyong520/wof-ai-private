'use strict';

const assert = require('node:assert/strict');
const {
  PlayerAnchorResolver,
  TargetLockIndicatorRouter,
  AnchoredWarningRenderer,
} = require('../src/player_follow_reference');
const {
  makeDrawingBuffer,
  makePlayer,
} = require('../fixtures/synthetic_projection');

const NATIVE_WIDTH = 384;
const NATIVE_HEIGHT = 224;

function projectionWith(projectNative) {
  return {
    source: 'bounds-regression-synthetic-only',
    version: 'bounds-regression-v1',
    epoch: 'synthetic-epoch-1',
    sampleAtMs: 1000,
    nativeWidth: NATIVE_WIDTH,
    nativeHeight: NATIVE_HEIGHT,
    confidence: 1,
    camera: null,
    validationBounds: { minX: 0, maxX: NATIVE_WIDTH, minY: 0, maxY: NATIVE_HEIGHT },
    projectNative,
  };
}

function pointProjection(anchorXNative, anchorYNative, bodyXNative = 192, bodyYNative = 112) {
  return projectionWith(() => ({
    anchorXNative,
    anchorYNative,
    bodyXNative,
    bodyYNative,
    confidence: 1,
  }));
}

function routeOne(router, nowMs, targetPlayer) {
  return router.route({
    nowMs,
    targets: { 'enemy-A': targetPlayer },
    warnings: [{
      sourceId: 'enemy-A',
      targetPlayer,
      priority: 1,
      active: true,
      visible: true,
      label: 'enemy-A',
    }],
  });
}

function renderOne(projectionState, renderer = new AnchoredWarningRenderer({ resolver: new PlayerAnchorResolver() })) {
  const router = new TargetLockIndicatorRouter();
  return renderer.buildPlan({
    nowMs: 1000,
    routed: routeOne(router, 1000, 'P1'),
    players: { P1: makePlayer(40, 20, 0) },
    projectionState,
    drawingBufferState: makeDrawingBuffer(),
  });
}

function expectFixedOutOfBounds(projectionState) {
  const plan = renderOne(projectionState);
  assert.equal(plan.anchored.length, 0);
  assert.equal(plan.fixed.length, 1);
  assert.equal(plan.fixed[0].reason, 'PROJECTION_OUT_OF_BOUNDS');
}

const tests = [];
function test(name, fn) { tests.push({ name, fn }); }

test('anchorXNative < 0 fails closed to fixed HUD', () => {
  expectFixedOutOfBounds(pointProjection(-0.001, 80));
});

test('anchorXNative >= native width fails closed to fixed HUD', () => {
  expectFixedOutOfBounds(pointProjection(NATIVE_WIDTH, 80));
});

test('anchorYNative < 0 fails closed to fixed HUD', () => {
  expectFixedOutOfBounds(pointProjection(192, -0.001));
});

test('anchorYNative >= native height fails closed to fixed HUD', () => {
  expectFixedOutOfBounds(pointProjection(192, NATIVE_HEIGHT));
});

test('body remains in bounds while derived head anchor is out of bounds', () => {
  expectFixedOutOfBounds(pointProjection(192, -1000, 192, 112));
});

test('valid anchor near viewport edge remains anchored and only final rectangle clamps', () => {
  const resolver = new PlayerAnchorResolver();
  const renderer = new AnchoredWarningRenderer({ resolver, boxWidth: 120, boxHeight: 40 });
  const plan = renderOne(pointProjection(NATIVE_WIDTH - 0.25, NATIVE_HEIGHT - 0.25), renderer);
  assert.equal(plan.fixed.length, 0);
  assert.equal(plan.anchored.length, 1);
  assert.equal(plan.anchored[0].anchor.ok, true);
  const r = plan.anchored[0].drawRectDb;
  assert.equal(r.x, 648);
  assert.equal(r.y, 408);
  assert.equal(r.width, 120);
  assert.equal(r.height, 40);
});

test('invalid anchor after valid frame clears smoothing state and never reuses last coordinate', () => {
  let anchor = { x: 100, y: 80 };
  const projection = projectionWith(() => ({
    anchorXNative: anchor.x,
    anchorYNative: anchor.y,
    bodyXNative: 192,
    bodyYNative: 112,
    confidence: 1,
  }));
  const resolver = new PlayerAnchorResolver();
  const renderer = new AnchoredWarningRenderer({ resolver, smoothingAlpha: 0.2 });
  const router = new TargetLockIndicatorRouter();
  const routed = routeOne(router, 1000, 'P1');
  const common = {
    nowMs: 1000,
    routed,
    players: { P1: makePlayer(40, 20, 0) },
    projectionState: projection,
    drawingBufferState: makeDrawingBuffer(),
  };

  let plan = renderer.buildPlan(common);
  assert.equal(plan.anchored.length, 1);

  anchor = { x: -1, y: 80 };
  plan = renderer.buildPlan(common);
  assert.equal(plan.anchored.length, 0);
  assert.equal(plan.fixed.length, 1);
  assert.equal(plan.fixed[0].reason, 'PROJECTION_OUT_OF_BOUNDS');
  assert.equal(renderer.follow.state.has('P1'), false);

  anchor = { x: 220, y: 80 };
  plan = renderer.buildPlan(common);
  assert.equal(plan.anchored.length, 1);
  assert.equal(plan.anchored[0].smoothingReset, true);
  assert.equal(plan.anchored[0].followPointDb.x, plan.anchored[0].anchor.xDb);
  assert.equal(plan.anchored[0].followPointDb.y, plan.anchored[0].anchor.yDb);
});

test('retarget during invalid-anchor frame removes old player cue immediately', () => {
  const projection = projectionWith(({ player }) => ({
    anchorXNative: player === 'P1' ? 100 : NATIVE_WIDTH,
    anchorYNative: 80,
    bodyXNative: player === 'P1' ? 100 : 192,
    bodyYNative: 112,
    confidence: 1,
  }));
  const resolver = new PlayerAnchorResolver();
  const renderer = new AnchoredWarningRenderer({ resolver, smoothingAlpha: 0.2 });
  const router = new TargetLockIndicatorRouter({ holdMs: 1000 });
  const db = makeDrawingBuffer();

  let routed = routeOne(router, 1000, 'P1');
  let plan = renderer.buildPlan({
    nowMs: 1000,
    routed,
    players: { P1: makePlayer(40, 20, 0), P2: makePlayer(60, 20, 0) },
    projectionState: projection,
    drawingBufferState: db,
  });
  assert.deepEqual(plan.anchored.map((item) => item.player), ['P1']);

  routed = routeOne(router, 1010, 'P2');
  assert.equal(routed.invalidated.some((item) => item.player === 'P1' && item.reason === 'RETARGET'), true);
  plan = renderer.buildPlan({
    nowMs: 1010,
    routed,
    players: {
      P1: makePlayer(40, 20, 0, { sampleAtMs: 1010 }),
      P2: makePlayer(60, 20, 0, { sampleAtMs: 1010 }),
    },
    projectionState: { ...projection, sampleAtMs: 1010 },
    drawingBufferState: makeDrawingBuffer({ sampleAtMs: 1010 }),
  });
  assert.equal(plan.anchored.length, 0);
  assert.deepEqual(plan.fixed.map((item) => item.player), ['P2']);
  assert.equal(plan.fixed[0].reason, 'PROJECTION_OUT_OF_BOUNDS');
  assert.equal(renderer.follow.state.has('P1'), false);
});

let passed = 0;
for (const { name, fn } of tests) {
  fn();
  passed += 1;
  process.stdout.write(`PASS ${name}\n`);
}
process.stdout.write(JSON.stringify({ status: 'PASS', passed, total: tests.length, fixture: 'SYNTHETIC_BOUNDS_ONLY_NOT_BROWSER_PROOF' }) + '\n');
