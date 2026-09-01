'use strict';

const assert = require('node:assert/strict');
const {
  PlayerAnchorResolver,
  TargetLockIndicatorRouter,
  AnchoredWarningRenderer,
} = require('../HUDANCHOR_PLAYER_FOLLOW/src/player_follow_reference');
const {
  makeSyntheticProjection,
  makeDrawingBuffer,
  makePlayer,
} = require('../HUDANCHOR_PLAYER_FOLLOW/fixtures/synthetic_projection');

const INVALID = [NaN, Infinity, -Infinity, undefined, null, '1', {}, []];
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

function projectionWith({
  confidence = 1,
  projectedConfidence = 1,
  sampleAtMs = 1000,
  anchorXNative = 140,
  anchorYNative = 100,
  bodyXNative = 140,
  bodyYNative = 124,
  countRef = null,
} = {}) {
  return {
    source: 'fresh-confidence-qa-synthetic-only',
    version: 'fresh-confidence-qa-v1',
    epoch: 'synthetic-epoch-1',
    sampleAtMs,
    nativeWidth: 384,
    nativeHeight: 224,
    confidence,
    camera: null,
    validationBounds: { minX: 0, maxX: 384, minY: 0, maxY: 224 },
    projectNative() {
      if (countRef) countRef.calls += 1;
      return { anchorXNative, anchorYNative, bodyXNative, bodyYNative, confidence: projectedConfidence };
    },
  };
}

function playerAt(nowMs = 1000, x = 40, confidence = 1, lifecycleId = 'life-1') {
  return { ...makePlayer(x, 20, 0, { sampleAtMs: nowMs, lifecycleId }), confidence };
}

function dbAt(nowMs = 1000, confidence = 1) {
  return { ...makeDrawingBuffer({ sampleAtMs: nowMs }), confidence };
}

function withConfidence(object, value) {
  return { ...object, confidence: value };
}

function withProjectionConfidence(value, options = {}) {
  const projection = projectionWith(options);
  projection.confidence = value;
  return projection;
}

function withProjectedConfidence(value, options = {}) {
  const projection = projectionWith(options);
  const original = projection.projectNative;
  projection.projectNative = (...args) => ({ ...original(...args), confidence: value });
  return projection;
}

function render({
  nowMs = 1000,
  target = 'P1',
  playerState = playerAt(nowMs),
  projectionState = projectionWith({ sampleAtMs: nowMs }),
  drawingBufferState = dbAt(nowMs),
  renderer = new AnchoredWarningRenderer({ resolver: new PlayerAnchorResolver() }),
  router = new TargetLockIndicatorRouter(),
} = {}) {
  const routed = routeOne(router, nowMs, target);
  const players = {
    P1: playerAt(nowMs, 40),
    P2: playerAt(nowMs, 60),
    P3: playerAt(nowMs, 80),
    [target]: playerState,
  };
  const plan = renderer.buildPlan({ nowMs, routed, players, projectionState, drawingBufferState });
  return { routed, plan };
}

function assertFixed(out, reason, player = 'P1') {
  assert.equal(out.plan.anchored.length, 0);
  assert.equal(out.plan.fixed.length, 1);
  assert.equal(out.plan.fixed[0].player, player);
  assert.equal(out.plan.fixed[0].reason, reason);
}

for (const [surface, reason] of [
  ['player', 'INVALID_PLAYER_CONFIDENCE'],
  ['projection', 'INVALID_PROJECTION_CONFIDENCE'],
  ['drawingBuffer', 'INVALID_DRAWING_BUFFER_CONFIDENCE'],
  ['projected', 'INVALID_PROJECTED_CONFIDENCE'],
]) {
  test(`${surface} confidence rejects NaN/Inf/missing/null/string/object`, () => {
    for (const value of INVALID) {
      let options = {};
      if (surface === 'player') options.playerState = withConfidence(playerAt(1000, 40), value);
      if (surface === 'projection') options.projectionState = withProjectionConfidence(value);
      if (surface === 'drawingBuffer') options.drawingBufferState = withConfidence(dbAt(1000), value);
      if (surface === 'projected') options.projectionState = withProjectedConfidence(value);
      assertFixed(render(options), reason);
    }
  });
}

test('invalid projection confidence prevents projection call even with valid body coordinates', () => {
  for (const value of INVALID) {
    const countRef = { calls: 0 };
    const out = render({
      projectionState: withProjectionConfidence(value, {
        anchorXNative: 383.75,
        anchorYNative: 223.75,
        bodyXNative: 192,
        bodyYNative: 112,
        countRef,
      }),
    });
    assertFixed(out, 'INVALID_PROJECTION_CONFIDENCE');
    assert.equal(countRef.calls, 0);
  }
});

test('confidence domain boundaries are exact: 0..1 valid, just outside invalid', () => {
  for (const value of [0, Number.EPSILON, 0.5, 1 - Number.EPSILON, 1]) {
    const out = render({
      playerState: playerAt(1000, 40, value),
      projectionState: projectionWith({ confidence: value, projectedConfidence: value }),
      drawingBufferState: dbAt(1000, value),
    });
    assert.equal(out.plan.fixed.length, 0);
    assert.equal(out.plan.anchored.length, 1);
    assert.equal(out.plan.anchored[0].anchor.confidence, value);
  }
  for (const value of [-Number.EPSILON, 1 + Number.EPSILON]) {
    assertFixed(render({ playerState: playerAt(1000, 40, value) }), 'INVALID_PLAYER_CONFIDENCE');
    assertFixed(render({ projectionState: projectionWith({ confidence: value }) }), 'INVALID_PROJECTION_CONFIDENCE');
    assertFixed(render({ drawingBufferState: dbAt(1000, value) }), 'INVALID_DRAWING_BUFFER_CONFIDENCE');
    assertFixed(render({ projectionState: projectionWith({ projectedConfidence: value }) }), 'INVALID_PROJECTED_CONFIDENCE');
  }
});

test('valid high -> invalid -> valid low cannot reuse stale high confidence or stale follow point', () => {
  const renderer = new AnchoredWarningRenderer({ resolver: new PlayerAnchorResolver(), smoothingAlpha: 0.1 });
  const router = new TargetLockIndicatorRouter({ holdMs: 1000 });

  let out = render({
    renderer, router,
    playerState: playerAt(1000, 40, 0.99),
    projectionState: projectionWith({ confidence: 0.99, projectedConfidence: 0.99, sampleAtMs: 1000 }),
    drawingBufferState: dbAt(1000, 0.99),
  });
  assert.equal(out.plan.anchored.length, 1);
  assert.equal(out.plan.anchored[0].anchor.confidence, 0.99);
  const oldX = out.plan.anchored[0].followPointDb.x;

  out = render({
    nowMs: 1010, renderer, router,
    playerState: playerAt(1010, 80, 1),
    projectionState: projectionWith({ confidence: null, sampleAtMs: 1010, anchorXNative: 220 }),
    drawingBufferState: dbAt(1010, 1),
  });
  assertFixed(out, 'INVALID_PROJECTION_CONFIDENCE');
  assert.equal(renderer.follow.state.has('P1'), false);

  out = render({
    nowMs: 1020, renderer, router,
    playerState: playerAt(1020, 100, 0.05),
    projectionState: projectionWith({ confidence: 0.05, projectedConfidence: 0.05, sampleAtMs: 1020, anchorXNative: 260 }),
    drawingBufferState: dbAt(1020, 0.05),
  });
  assert.equal(out.plan.anchored.length, 1);
  assert.equal(out.plan.anchored[0].anchor.confidence, 0.05);
  assert.equal(out.plan.anchored[0].smoothingReset, true);
  assert.equal(out.plan.anchored[0].followPointDb.x, out.plan.anchored[0].anchor.xDb);
  assert.notEqual(out.plan.anchored[0].followPointDb.x, oldX);
});

test('retarget P1 -> P2 during invalid confidence removes P1 immediately and fixed-fallbacks P2', () => {
  const renderer = new AnchoredWarningRenderer({ resolver: new PlayerAnchorResolver(), smoothingAlpha: 0.2 });
  const router = new TargetLockIndicatorRouter({ holdMs: 1000 });
  let out = render({ renderer, router, target: 'P1' });
  assert.deepEqual(out.plan.anchored.map((x) => x.player), ['P1']);

  out = render({
    nowMs: 1010,
    renderer,
    router,
    target: 'P2',
    playerState: playerAt(1010, 60, 1, 'p2-life'),
    projectionState: projectionWith({ confidence: 'bad', sampleAtMs: 1010 }),
    drawingBufferState: dbAt(1010),
  });
  assert.equal(out.routed.invalidated.some((x) => x.player === 'P1' && x.reason === 'RETARGET'), true);
  assertFixed(out, 'INVALID_PROJECTION_CONFIDENCE', 'P2');
  assert.equal(renderer.follow.state.has('P1'), false);
  assert.equal(renderer.follow.state.has('P2'), false);
});

test('valid near-edge anchor remains attached; only final draw rectangle clamps', () => {
  const renderer = new AnchoredWarningRenderer({ resolver: new PlayerAnchorResolver(), boxWidth: 120, boxHeight: 40 });
  const out = render({
    renderer,
    projectionState: projectionWith({ anchorXNative: 383.75, anchorYNative: 223.75, bodyXNative: 192, bodyYNative: 112 }),
  });
  assert.equal(out.plan.fixed.length, 0);
  assert.equal(out.plan.anchored.length, 1);
  const item = out.plan.anchored[0];
  assert.ok(item.anchor.xDb > item.drawRectDb.x);
  assert.ok(item.anchor.yDb > item.drawRectDb.y);
  assert.equal(item.drawRectDb.x, 648);
  assert.equal(item.drawRectDb.y, 408);
});

test('near-edge geometry with invalid confidence never masquerades as clamped attachment', () => {
  const renderer = new AnchoredWarningRenderer({ resolver: new PlayerAnchorResolver(), boxWidth: 120, boxHeight: 40 });
  const out = render({
    renderer,
    projectionState: projectionWith({
      confidence: NaN,
      anchorXNative: 383.75,
      anchorYNative: 223.75,
      bodyXNative: 192,
      bodyYNative: 112,
    }),
  });
  assertFixed(out, 'INVALID_PROJECTION_CONFIDENCE');
  assert.equal(Object.prototype.hasOwnProperty.call(out.plan.fixed[0], 'drawRectDb'), false);
});

test('finite out-of-bounds anchor remains fail-closed and is not edge-clamped into attachment', () => {
  for (const coords of [
    { anchorXNative: -0.001, anchorYNative: 100 },
    { anchorXNative: 384, anchorYNative: 100 },
    { anchorXNative: 100, anchorYNative: -0.001 },
    { anchorXNative: 100, anchorYNative: 224 },
  ]) {
    const out = render({ projectionState: projectionWith({ ...coords, bodyXNative: 192, bodyYNative: 112 }) });
    assertFixed(out, 'PROJECTION_OUT_OF_BOUNDS');
  }
});

test('body coordinates can be valid while projected confidence invalid; result is fixed HUD', () => {
  for (const value of [NaN, null, '0.9', {}]) {
    const out = render({
      projectionState: projectionWith({
        confidence: 1,
        projectedConfidence: value,
        anchorXNative: 192,
        anchorYNative: 80,
        bodyXNative: 192,
        bodyYNative: 112,
      }),
    });
    assertFixed(out, 'INVALID_PROJECTED_CONFIDENCE');
  }
});

let passed = 0;
for (const { name, fn } of tests) {
  fn();
  passed += 1;
  process.stdout.write(`PASS ${name}\n`);
}
const summary = {
  status: 'PASS',
  stageId: 'HUDANCHOR_PLAYER_FOLLOW_CONFIDENCE_FAILCLOSED_QA_V1',
  passed,
  total: tests.length,
  invalidValuesPerSurface: INVALID.length,
  sutBlob: 'e36e80fdad7bcf7f73485f9093aa9014428c86b1',
  fixtureBlob: '79e42e675d371ec91715116227fecf0ed3c27d97',
  fixture: 'FRESH_SYNTHETIC_CONFIDENCE_QA_NOT_BROWSER_PROOF',
};
process.stdout.write(JSON.stringify(summary) + '\n');
