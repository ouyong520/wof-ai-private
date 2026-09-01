'use strict';

const assert = require('node:assert/strict');
const {
  PlayerAnchorResolver,
  TargetLockIndicatorRouter,
  AnchoredWarningRenderer,
} = require('../src/player_follow_reference');
const {
  makeSyntheticProjection,
  makeDrawingBuffer,
  makePlayer,
} = require('../fixtures/synthetic_projection');

const tests = [];
function test(name, fn) { tests.push({ name, fn }); }

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

function projectionWith({ confidence = 1, projectedConfidence = 1, sampleAtMs = 1000 } = {}) {
  const base = makeSyntheticProjection({ sampleAtMs });
  return {
    ...base,
    confidence,
    projectNative(args) {
      return { ...base.projectNative(args), confidence: projectedConfidence };
    },
  };
}

function omit(object, key) {
  const copy = { ...object };
  delete copy[key];
  return copy;
}

function renderOne({
  nowMs = 1000,
  target = 'P1',
  playerState = makePlayer(40, 20, 0),
  projectionState = projectionWith(),
  drawingBufferState = makeDrawingBuffer(),
  renderer = new AnchoredWarningRenderer({ resolver: new PlayerAnchorResolver() }),
  router = new TargetLockIndicatorRouter(),
} = {}) {
  const routed = routeOne(router, nowMs, target);
  const players = {
    P1: makePlayer(40, 20, 0, { sampleAtMs: nowMs }),
    P2: makePlayer(60, 20, 0, { sampleAtMs: nowMs }),
    P3: makePlayer(80, 20, 0, { sampleAtMs: nowMs }),
    [target]: playerState,
  };
  return {
    routed,
    plan: renderer.buildPlan({
      nowMs,
      routed,
      players,
      projectionState,
      drawingBufferState,
    }),
  };
}

function expectFixed(reason, options) {
  const { plan } = renderOne(options);
  assert.equal(plan.anchored.length, 0);
  assert.equal(plan.fixed.length, 1);
  assert.equal(plan.fixed[0].reason, reason);
}

for (const value of [NaN, Infinity, -Infinity]) {
  test(`projection confidence ${String(value)} fails closed`, () => {
    expectFixed('INVALID_PROJECTION_CONFIDENCE', {
      projectionState: projectionWith({ confidence: value }),
    });
  });
}

for (const value of [NaN, Infinity, -Infinity]) {
  test(`player confidence ${String(value)} fails closed`, () => {
    expectFixed('INVALID_PLAYER_CONFIDENCE', {
      playerState: { ...makePlayer(40, 20, 0), confidence: value },
    });
  });
}

for (const value of [NaN, Infinity, -Infinity]) {
  test(`drawing-buffer confidence ${String(value)} fails closed`, () => {
    expectFixed('INVALID_DRAWING_BUFFER_CONFIDENCE', {
      drawingBufferState: { ...makeDrawingBuffer(), confidence: value },
    });
  });
}

for (const value of [NaN, Infinity, -Infinity]) {
  test(`projected confidence ${String(value)} fails closed`, () => {
    expectFixed('INVALID_PROJECTED_CONFIDENCE', {
      projectionState: projectionWith({ projectedConfidence: value }),
    });
  });
}

test('missing confidence fails closed on every authority surface', () => {
  expectFixed('INVALID_PLAYER_CONFIDENCE', {
    playerState: omit(makePlayer(40, 20, 0), 'confidence'),
  });
  expectFixed('INVALID_PROJECTION_CONFIDENCE', {
    projectionState: omit(projectionWith(), 'confidence'),
  });
  expectFixed('INVALID_DRAWING_BUFFER_CONFIDENCE', {
    drawingBufferState: omit(makeDrawingBuffer(), 'confidence'),
  });
  const base = projectionWith();
  expectFixed('INVALID_PROJECTED_CONFIDENCE', {
    projectionState: {
      ...base,
      projectNative(args) {
        return omit(base.projectNative(args), 'confidence');
      },
    },
  });
});

test('finite out-of-domain confidence is invalid rather than clamped into authority', () => {
  for (const value of [-0.001, 1.001]) {
    expectFixed('INVALID_PLAYER_CONFIDENCE', {
      playerState: { ...makePlayer(40, 20, 0), confidence: value },
    });
    expectFixed('INVALID_PROJECTION_CONFIDENCE', {
      projectionState: projectionWith({ confidence: value }),
    });
    expectFixed('INVALID_DRAWING_BUFFER_CONFIDENCE', {
      drawingBufferState: { ...makeDrawingBuffer(), confidence: value },
    });
    expectFixed('INVALID_PROJECTED_CONFIDENCE', {
      projectionState: projectionWith({ projectedConfidence: value }),
    });
  }
});

test('valid finite confidence at and near boundaries remains anchored', () => {
  for (const value of [0, Number.EPSILON, 0.5, 1 - Number.EPSILON, 1]) {
    const { plan } = renderOne({
      playerState: { ...makePlayer(40, 20, 0), confidence: value },
      projectionState: projectionWith({ confidence: value, projectedConfidence: value }),
      drawingBufferState: { ...makeDrawingBuffer(), confidence: value },
    });
    assert.equal(plan.fixed.length, 0);
    assert.equal(plan.anchored.length, 1);
    assert.equal(plan.anchored[0].anchor.confidence, value);
  }
});

test('valid finite confidence minimum semantics remain unchanged', () => {
  const { plan } = renderOne({
    playerState: { ...makePlayer(40, 20, 0), confidence: 0.8 },
    projectionState: projectionWith({ confidence: 0.6, projectedConfidence: 0.2 }),
    drawingBufferState: { ...makeDrawingBuffer(), confidence: 0.4 },
  });
  assert.equal(plan.anchored.length, 1);
  assert.equal(plan.anchored[0].anchor.confidence, 0.2);
});

test('invalid confidence after valid frame clears follow state and recovery resets smoothing', () => {
  const resolver = new PlayerAnchorResolver();
  const renderer = new AnchoredWarningRenderer({ resolver, smoothingAlpha: 0.2 });
  const router = new TargetLockIndicatorRouter();

  let out = renderOne({ renderer, router });
  assert.equal(out.plan.anchored.length, 1);
  assert.equal(renderer.follow.state.has('P1'), true);

  out = renderOne({
    nowMs: 1010,
    renderer,
    router,
    playerState: makePlayer(40, 20, 0, { sampleAtMs: 1010 }),
    projectionState: projectionWith({ confidence: NaN, sampleAtMs: 1010 }),
    drawingBufferState: makeDrawingBuffer({ sampleAtMs: 1010 }),
  });
  assert.equal(out.plan.anchored.length, 0);
  assert.equal(out.plan.fixed[0].reason, 'INVALID_PROJECTION_CONFIDENCE');
  assert.equal(renderer.follow.state.has('P1'), false);

  out = renderOne({
    nowMs: 1020,
    renderer,
    router,
    playerState: makePlayer(100, 20, 0, { sampleAtMs: 1020 }),
    projectionState: projectionWith({ sampleAtMs: 1020 }),
    drawingBufferState: makeDrawingBuffer({ sampleAtMs: 1020 }),
  });
  assert.equal(out.plan.anchored.length, 1);
  assert.equal(out.plan.anchored[0].smoothingReset, true);
  assert.equal(out.plan.anchored[0].followPointDb.x, out.plan.anchored[0].anchor.xDb);
  assert.equal(out.plan.anchored[0].followPointDb.y, out.plan.anchored[0].anchor.yDb);
});

test('retarget P1 -> P2 during invalid confidence removes P1 cue immediately', () => {
  const resolver = new PlayerAnchorResolver();
  const renderer = new AnchoredWarningRenderer({ resolver, smoothingAlpha: 0.2 });
  const router = new TargetLockIndicatorRouter({ holdMs: 1000 });

  let out = renderOne({ renderer, router, target: 'P1' });
  assert.deepEqual(out.plan.anchored.map((item) => item.player), ['P1']);

  out = renderOne({
    nowMs: 1010,
    renderer,
    router,
    target: 'P2',
    playerState: makePlayer(60, 20, 0, { sampleAtMs: 1010 }),
    projectionState: projectionWith({ confidence: NaN, sampleAtMs: 1010 }),
    drawingBufferState: makeDrawingBuffer({ sampleAtMs: 1010 }),
  });
  assert.equal(out.routed.invalidated.some((item) => item.player === 'P1' && item.reason === 'RETARGET'), true);
  assert.equal(out.plan.anchored.length, 0);
  assert.deepEqual(out.plan.fixed.map((item) => item.player), ['P2']);
  assert.equal(out.plan.fixed[0].reason, 'INVALID_PROJECTION_CONFIDENCE');
  assert.equal(renderer.follow.state.has('P1'), false);
});

let passed = 0;
for (const { name, fn } of tests) {
  fn();
  passed += 1;
  process.stdout.write(`PASS ${name}\n`);
}
process.stdout.write(JSON.stringify({
  status: 'PASS',
  passed,
  total: tests.length,
  fixture: 'SYNTHETIC_CONFIDENCE_FAILCLOSED_ONLY_NOT_BROWSER_PROOF',
}) + '\n');
