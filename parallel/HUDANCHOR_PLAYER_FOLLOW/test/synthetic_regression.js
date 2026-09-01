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

function routeOne(router, nowMs, sourceId, targetPlayer, priority = 1) {
  return router.route({
    nowMs,
    targets: { [sourceId]: targetPlayer },
    warnings: [{ sourceId, targetPlayer, priority, active: true, visible: true, label: sourceId }],
  });
}

function planOne({ nowMs = 1000, player = 'P1', playerState, projectionState, drawingBufferState, renderer }) {
  const router = new TargetLockIndicatorRouter();
  const routed = routeOne(router, nowMs, 'enemy-A', player);
  return renderer.buildPlan({
    nowMs,
    routed,
    players: { [player]: playerState },
    projectionState,
    drawingBufferState,
  });
}

test('horizontal movement follows live player X', () => {
  const resolver = new PlayerAnchorResolver();
  const projection = makeSyntheticProjection();
  const db = makeDrawingBuffer();
  const a = resolver.resolve({ player: 'P1', nowMs: 1000, playerState: makePlayer(40, 20, 0), projectionState: projection, drawingBufferState: db });
  const b = resolver.resolve({ player: 'P1', nowMs: 1000, playerState: makePlayer(70, 20, 0), projectionState: projection, drawingBufferState: db });
  assert.equal(a.ok, true);
  assert.equal(b.ok, true);
  assert.equal(b.xDb - a.xDb, 60); // 30 native px * 2 drawing-buffer scale.
});

test('camera scroll is part of projection and prevents drift', () => {
  const resolver = new PlayerAnchorResolver();
  const db = makeDrawingBuffer();
  const a = resolver.resolve({
    player: 'P1', nowMs: 1000, playerState: makePlayer(140, 20, 0),
    projectionState: makeSyntheticProjection({ cameraX: 20 }), drawingBufferState: db,
  });
  const b = resolver.resolve({
    player: 'P1', nowMs: 1000, playerState: makePlayer(160, 20, 0),
    projectionState: makeSyntheticProjection({ cameraX: 40 }), drawingBufferState: db,
  });
  assert.equal(a.xDb, b.xDb);
});

test('depth changes screen Y', () => {
  const resolver = new PlayerAnchorResolver();
  const projection = makeSyntheticProjection();
  const db = makeDrawingBuffer();
  const a = resolver.resolve({ player: 'P1', nowMs: 1000, playerState: makePlayer(40, 10, 0), projectionState: projection, drawingBufferState: db });
  const b = resolver.resolve({ player: 'P1', nowMs: 1000, playerState: makePlayer(40, 30, 0), projectionState: projection, drawingBufferState: db });
  assert.notEqual(a.yDb, b.yDb);
});

test('jump Z moves anchor vertically', () => {
  const resolver = new PlayerAnchorResolver();
  const projection = makeSyntheticProjection();
  const db = makeDrawingBuffer();
  const floor = resolver.resolve({ player: 'P1', nowMs: 1000, playerState: makePlayer(40, 20, 0), projectionState: projection, drawingBufferState: db });
  const jump = resolver.resolve({ player: 'P1', nowMs: 1000, playerState: makePlayer(40, 20, 15), projectionState: projection, drawingBufferState: db });
  assert.ok(jump.yDb < floor.yDb);
});

test('P1/P2/P3 route independently', () => {
  const router = new TargetLockIndicatorRouter();
  const routed = router.route({
    nowMs: 1000,
    targets: { a: 'P1', b: 'P2', c: 'P3' },
    warnings: [
      { sourceId: 'a', targetPlayer: 'P1', priority: 1, active: true },
      { sourceId: 'b', targetPlayer: 'P2', priority: 1, active: true },
      { sourceId: 'c', targetPlayer: 'P3', priority: 1, active: true },
    ],
  });
  assert.deepEqual(routed.byPlayer.map((row) => row.player), ['P1', 'P2', 'P3']);
});

test('retarget P1 -> P2 -> P3 invalidates old target immediately even with hold', () => {
  const router = new TargetLockIndicatorRouter({ holdMs: 1000 });
  let routed = routeOne(router, 1000, 'enemy-A', 'P1');
  assert.deepEqual(routed.byPlayer.map((row) => row.player), ['P1']);
  routed = routeOne(router, 1010, 'enemy-A', 'P2');
  assert.deepEqual(routed.byPlayer.map((row) => row.player), ['P2']);
  assert.equal(routed.invalidated.some((x) => x.player === 'P1' && x.reason === 'RETARGET'), true);
  routed = routeOne(router, 1020, 'enemy-A', 'P3');
  assert.deepEqual(routed.byPlayer.map((row) => row.player), ['P3']);
  assert.equal(routed.invalidated.some((x) => x.player === 'P2' && x.reason === 'RETARGET'), true);
});

test('resize/fullscreen remaps current anchor from live drawing buffer', () => {
  const resolver = new PlayerAnchorResolver();
  const projection = makeSyntheticProjection();
  const player = makePlayer(40, 20, 0);
  const a = resolver.resolve({ player: 'P1', nowMs: 1000, playerState: player, projectionState: projection, drawingBufferState: makeDrawingBuffer() });
  const b = resolver.resolve({
    player: 'P1', nowMs: 1000, playerState: player, projectionState: projection,
    drawingBufferState: makeDrawingBuffer({ width: 1152, height: 672, fullscreen: true, mappingVersion: 'synthetic-map-2' }),
  });
  assert.equal(b.xDb / a.xDb, 1.5);
  assert.equal(b.yDb / a.yDb, 1.5);
  assert.notEqual(a.mappingKey, b.mappingKey);
});

test('DPR-only change does not drift when drawing-buffer mapping is unchanged', () => {
  const resolver = new PlayerAnchorResolver();
  const projection = makeSyntheticProjection();
  const player = makePlayer(40, 20, 0);
  const a = resolver.resolve({ player: 'P1', nowMs: 1000, playerState: player, projectionState: projection, drawingBufferState: makeDrawingBuffer({ dpr: 1 }) });
  const b = resolver.resolve({ player: 'P1', nowMs: 1000, playerState: player, projectionState: projection, drawingBufferState: makeDrawingBuffer({ dpr: 2 }) });
  assert.equal(a.xDb, b.xDb);
  assert.equal(a.yDb, b.yDb);
});

test('stale projection fails closed to fixed HUD fallback', () => {
  const resolver = new PlayerAnchorResolver({ maxProjectionAgeMs: 100 });
  const renderer = new AnchoredWarningRenderer({ resolver });
  const projection = makeSyntheticProjection({ sampleAtMs: 700 });
  const db = makeDrawingBuffer({ sampleAtMs: 1000 });
  const plan = planOne({ nowMs: 1000, playerState: makePlayer(40, 20, 0), projectionState: projection, drawingBufferState: db, renderer });
  assert.equal(plan.anchored.length, 0);
  assert.equal(plan.fixed.length, 1);
  assert.equal(plan.fixed[0].reason, 'STALE_PROJECTION');
});

test('epoch mismatch fails closed', () => {
  const resolver = new PlayerAnchorResolver();
  const result = resolver.resolve({
    player: 'P1', nowMs: 1000,
    playerState: makePlayer(40, 20, 0, { epoch: 'player-epoch' }),
    projectionState: makeSyntheticProjection({ epoch: 'projection-epoch' }),
    drawingBufferState: makeDrawingBuffer({ epoch: 'projection-epoch' }),
  });
  assert.equal(result.ok, false);
  assert.equal(result.reason, 'EPOCH_MISMATCH');
});

test('multi-warning aggregates per targeted player without new prediction semantics', () => {
  const router = new TargetLockIndicatorRouter();
  const routed = router.route({
    nowMs: 1000,
    targets: { a: 'P2', b: 'P2' },
    warnings: [
      { sourceId: 'a', targetPlayer: 'P2', priority: 2, active: true, family: 'existing-A' },
      { sourceId: 'b', targetPlayer: 'P2', priority: 9, active: true, family: 'existing-B' },
    ],
  });
  assert.equal(routed.byPlayer.length, 1);
  assert.equal(routed.byPlayer[0].player, 'P2');
  assert.equal(routed.byPlayer[0].threatCount, 2);
  assert.equal(routed.byPlayer[0].warning.sourceId, 'b');
});

test('player disappearance never reuses last anchored coordinate', () => {
  const resolver = new PlayerAnchorResolver();
  const renderer = new AnchoredWarningRenderer({ resolver, smoothingAlpha: 0.2 });
  const projection = makeSyntheticProjection();
  const db = makeDrawingBuffer();
  let plan = planOne({ playerState: makePlayer(40, 20, 0), projectionState: projection, drawingBufferState: db, renderer });
  assert.equal(plan.anchored.length, 1);
  plan = planOne({ playerState: makePlayer(40, 20, 0, { present: false }), projectionState: projection, drawingBufferState: db, renderer });
  assert.equal(plan.anchored.length, 0);
  assert.equal(plan.fixed.length, 1);
  assert.equal(plan.fixed[0].reason, 'PLAYER_ABSENT');
});

test('respawn lifecycle replacement resets smoothing immediately', () => {
  const resolver = new PlayerAnchorResolver();
  const renderer = new AnchoredWarningRenderer({ resolver, smoothingAlpha: 0.1 });
  const router = new TargetLockIndicatorRouter();
  const projection = makeSyntheticProjection();
  const db = makeDrawingBuffer();
  const routed = routeOne(router, 1000, 'enemy-A', 'P1');
  let plan = renderer.buildPlan({ nowMs: 1000, routed, players: { P1: makePlayer(40, 20, 0, { lifecycleId: 'life-1' }) }, projectionState: projection, drawingBufferState: db });
  assert.equal(plan.anchored[0].smoothingReset, true);
  plan = renderer.buildPlan({ nowMs: 1000, routed, players: { P1: makePlayer(100, 20, 0, { lifecycleId: 'life-2' }) }, projectionState: projection, drawingBufferState: db });
  assert.equal(plan.anchored[0].smoothingReset, true);
  assert.equal(plan.anchored[0].followPointDb.x, plan.anchored[0].anchor.xDb);
});

test('camera discontinuity resets smoothing instead of carrying old point', () => {
  const resolver = new PlayerAnchorResolver();
  const renderer = new AnchoredWarningRenderer({ resolver, smoothingAlpha: 0.1 });
  const router = new TargetLockIndicatorRouter();
  const projection = makeSyntheticProjection();
  const db = makeDrawingBuffer();
  const routed = routeOne(router, 1000, 'enemy-A', 'P1');
  renderer.buildPlan({ nowMs: 1000, routed, players: { P1: makePlayer(40, 20, 0) }, projectionState: projection, drawingBufferState: db });
  const plan = renderer.buildPlan({ nowMs: 1000, routed, players: { P1: makePlayer(100, 20, 0) }, projectionState: projection, drawingBufferState: db, cameraDiscontinuity: true });
  assert.equal(plan.anchored[0].smoothingReset, true);
  assert.equal(plan.anchored[0].followPointDb.x, plan.anchored[0].anchor.xDb);
});

test('viewport clamp keeps WebGL draw rectangle inside content rect', () => {
  const resolver = new PlayerAnchorResolver();
  const renderer = new AnchoredWarningRenderer({ resolver, boxWidth: 120, boxHeight: 40 });
  const projection = makeSyntheticProjection();
  const db = makeDrawingBuffer({ width: 768, height: 448, contentRect: { x: 50, y: 30, width: 600, height: 350 } });
  const plan = planOne({ playerState: makePlayer(-40, -40, 0), projectionState: projection, drawingBufferState: db, renderer });
  assert.equal(plan.anchored.length, 1);
  const r = plan.anchored[0].drawRectDb;
  assert.ok(r.x >= 50 && r.y >= 30);
  assert.ok(r.x + r.width <= 650 && r.y + r.height <= 380);
  assert.equal(plan.coordinateSpace, 'webgl-drawing-buffer');
});

let passed = 0;
for (const { name, fn } of tests) {
  fn();
  passed += 1;
  process.stdout.write(`PASS ${name}\n`);
}
process.stdout.write(JSON.stringify({ status: 'PASS', passed, total: tests.length, fixture: 'SYNTHETIC_ONLY_NOT_BROWSER_PROOF' }) + '\n');
