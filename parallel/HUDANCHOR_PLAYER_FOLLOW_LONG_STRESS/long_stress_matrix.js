'use strict';

const assert = require('node:assert/strict');
const {
  PlayerAnchorResolver,
  TargetLockIndicatorRouter,
  AnchoredWarningRenderer,
} = require('../HUDANCHOR_PLAYER_FOLLOW/src/player_follow_reference');

const SUT_BLOB = '4beb7f8d4c9f815e125ed795aca536f02562f5d1';
const PLAYERS = ['P1', 'P2', 'P3'];
const SEEDS = [
  0x1a2b3c4d, 0x22334455, 0x31415926, 0x5eed0001,
  0x5eed0002, 0x5eed0003, 0x6a09e667, 0x7f4a7c15,
  0x89abcdef, 0x9e3779b9, 0xa5a5a5a5, 0xbadc0ffe,
  0xc001d00d, 0xd15ea5ed, 0xdecafbad, 0xf00dbabe,
];
const STEPS_PER_SEED = 1024;

function lcg(seed) {
  let state = seed >>> 0;
  return () => {
    state = (Math.imul(state, 1664525) + 1013904223) >>> 0;
    return state / 0x100000000;
  };
}

function playerState(nowMs, player, rng, options = {}) {
  const index = PLAYERS.indexOf(player);
  return {
    present: options.present !== false,
    x: options.x ?? ((rng() - 0.5) * 100 + index * 8),
    y: options.y ?? ((rng() - 0.5) * 40),
    z: options.z ?? (rng() * 24),
    sampleAtMs: options.sampleAtMs ?? nowMs,
    epoch: options.epoch ?? 'epoch-1',
    lifecycleId: options.lifecycleId ?? `${player}-life-1`,
    confidence: options.confidence ?? 1,
  };
}

function projectionState(nowMs, options = {}) {
  const cameraX = options.cameraX ?? 0;
  const cameraY = options.cameraY ?? 0;
  const forceAnchor = options.forceAnchor || null;
  return {
    source: 'long-stress-synthetic-not-browser-proof',
    version: options.version ?? 'proj-gen-1',
    epoch: options.epoch ?? 'epoch-1',
    sampleAtMs: options.sampleAtMs ?? nowMs,
    nativeWidth: 384,
    nativeHeight: 224,
    confidence: Object.prototype.hasOwnProperty.call(options, 'confidence') ? options.confidence : 1,
    camera: { x: cameraX, y: cameraY },
    validationBounds: { minX: -64, maxX: 448, minY: -64, maxY: 288 },
    projectNative({ x, y, z, camera }) {
      const bodyXNative = 192 + (x - camera.x) * 0.55;
      const bodyYNative = 145 + (y - camera.y) * 0.35 - z;
      return {
        bodyXNative: forceAnchor?.bodyXNative ?? bodyXNative,
        bodyYNative: forceAnchor?.bodyYNative ?? bodyYNative,
        anchorXNative: forceAnchor?.x ?? bodyXNative,
        anchorYNative: forceAnchor?.y ?? (bodyYNative - 24),
        confidence: Object.prototype.hasOwnProperty.call(options, 'projectedConfidence') ? options.projectedConfidence : 1,
      };
    },
  };
}

function drawingBufferState(nowMs, options = {}) {
  const width = options.width ?? 768;
  const height = options.height ?? 448;
  return {
    width,
    height,
    sampleAtMs: options.sampleAtMs ?? nowMs,
    epoch: options.epoch ?? 'epoch-1',
    confidence: 1,
    dpr: options.dpr ?? 1,
    fullscreen: !!options.fullscreen,
    mappingVersion: options.mappingVersion ?? 'map-1',
    contentRect: options.contentRect ?? { x: 0, y: 0, width, height },
  };
}

function warning(sourceId, targetPlayer, options = {}) {
  return {
    sourceId,
    targetPlayer,
    priority: options.priority ?? 1,
    active: options.active !== false,
    visible: options.visible !== false,
    label: sourceId,
  };
}

function routeOne(router, nowMs, targetPlayer, sourceId = 'enemy-A') {
  return router.route({
    nowMs,
    targets: { [sourceId]: targetPlayer },
    warnings: [warning(sourceId, targetPlayer)],
  });
}

function planOne({ nowMs, target, players, projection, drawingBuffer, renderer, router, cameraDiscontinuity = false }) {
  const routed = routeOne(router, nowMs, target);
  const plan = renderer.buildPlan({
    nowMs,
    routed,
    players,
    projectionState: projection,
    drawingBufferState: drawingBuffer,
    cameraDiscontinuity,
  });
  return { routed, plan };
}

const failures = [];
let directedPassed = 0;
function directed(name, fn) {
  try {
    fn();
    directedPassed += 1;
    process.stdout.write(`PASS directed: ${name}\n`);
  } catch (error) {
    failures.push({ kind: 'directed', name, message: error.message });
    process.stdout.write(`FAIL directed: ${name}: ${error.message}\n`);
  }
}

directed('P1/P2/P3 single target isolation', () => {
  for (const player of PLAYERS) {
    const routed = routeOne(new TargetLockIndicatorRouter(), 1000, player);
    assert.deepEqual(routed.byPlayer.map((row) => row.player), [player]);
  }
});

directed('same-frame and neighbor-frame retarget clears old owner', () => {
  const router = new TargetLockIndicatorRouter({ holdMs: 1000 });
  routeOne(router, 1000, 'P1');
  let routed = routeOne(router, 1000, 'P2');
  assert.deepEqual(routed.byPlayer.map((row) => row.player), ['P2']);
  routed = routeOne(router, 1001, 'P3');
  assert.deepEqual(routed.byPlayer.map((row) => row.player), ['P3']);
});

directed('stale, nonfinite and finite out-of-bounds anchors use fixed fallback', () => {
  const resolver = new PlayerAnchorResolver();
  const renderer = new AnchoredWarningRenderer({ resolver });
  const router = new TargetLockIndicatorRouter();
  const rng = lcg(1);
  const base = playerState(1000, 'P1', rng, { x: 0, y: 0, z: 0 });
  let out = planOne({ nowMs: 1000, target: 'P1', players: { P1: { ...base, sampleAtMs: 800 } }, projection: projectionState(1000), drawingBuffer: drawingBufferState(1000), renderer, router });
  assert.equal(out.plan.fixed[0].reason, 'STALE_PLAYER');
  out = planOne({ nowMs: 1001, target: 'P1', players: { P1: { ...base, x: NaN, sampleAtMs: 1001 } }, projection: projectionState(1001), drawingBuffer: drawingBufferState(1001), renderer, router });
  assert.equal(out.plan.fixed[0].reason, 'INVALID_PLAYER_XYZ');
  out = planOne({ nowMs: 1002, target: 'P1', players: { P1: { ...base, sampleAtMs: 1002 } }, projection: projectionState(1002, { forceAnchor: { x: -0.01, y: 80, bodyXNative: 192, bodyYNative: 112 } }), drawingBuffer: drawingBufferState(1002), renderer, router });
  assert.equal(out.plan.fixed[0].reason, 'PROJECTION_OUT_OF_BOUNDS');
});

directed('near-edge valid anchor remains real anchor; only rectangle clamps', () => {
  const resolver = new PlayerAnchorResolver();
  const renderer = new AnchoredWarningRenderer({ resolver, boxWidth: 120, boxHeight: 40 });
  const router = new TargetLockIndicatorRouter();
  const rng = lcg(2);
  const out = planOne({
    nowMs: 1000,
    target: 'P1',
    players: { P1: playerState(1000, 'P1', rng, { x: 0, y: 0, z: 0 }) },
    projection: projectionState(1000, { forceAnchor: { x: 383.75, y: 223.75, bodyXNative: 192, bodyYNative: 112 } }),
    drawingBuffer: drawingBufferState(1000), renderer, router,
  });
  assert.equal(out.plan.anchored.length, 1);
  assert.ok(out.plan.anchored[0].anchor.xDb > out.plan.anchored[0].drawRectDb.x);
});

directed('resize/fullscreen/DPR and lifecycle changes reset smoothing', () => {
  const resolver = new PlayerAnchorResolver();
  const renderer = new AnchoredWarningRenderer({ resolver, smoothingAlpha: 0.2 });
  const router = new TargetLockIndicatorRouter();
  const rng = lcg(3);
  let out = planOne({ nowMs: 1000, target: 'P1', players: { P1: playerState(1000, 'P1', rng, { lifecycleId: 'life-1' }) }, projection: projectionState(1000), drawingBuffer: drawingBufferState(1000), renderer, router });
  assert.equal(out.plan.anchored[0].smoothingReset, true);
  out = planOne({ nowMs: 1001, target: 'P1', players: { P1: playerState(1001, 'P1', rng, { lifecycleId: 'life-1' }) }, projection: projectionState(1001), drawingBuffer: drawingBufferState(1001, { width: 1152, height: 672, fullscreen: true, dpr: 1.5, mappingVersion: 'map-2' }), renderer, router });
  assert.equal(out.plan.anchored[0].smoothingReset, true);
  out = planOne({ nowMs: 1002, target: 'P1', players: { P1: playerState(1002, 'P1', rng, { lifecycleId: 'life-2' }) }, projection: projectionState(1002), drawingBuffer: drawingBufferState(1002, { width: 1152, height: 672, fullscreen: true, dpr: 2, mappingVersion: 'map-2' }), renderer, router });
  assert.equal(out.plan.anchored[0].smoothingReset, true);
});

directed('warning clear and unsupported target do not leave old-player ghost', () => {
  const clearRouter = new TargetLockIndicatorRouter({ holdMs: 0 });
  routeOne(clearRouter, 1000, 'P1');
  let routed = clearRouter.route({ nowMs: 1001, targets: { 'enemy-A': 'P1' }, warnings: [] });
  assert.equal(routed.byPlayer.length, 0);
  const router = new TargetLockIndicatorRouter({ holdMs: 1000 });
  routeOne(router, 1000, 'P1');
  routed = routeOne(router, 1001, 'PX');
  assert.equal(routed.byPlayer.length, 0);
  assert.ok(routed.invalidated.some((item) => item.player === 'P1'));
});

directed('multi-warning/multi-player isolation preserves owner identity', () => {
  const router = new TargetLockIndicatorRouter();
  const routed = router.route({
    nowMs: 1000,
    targets: { a: 'P2', b: 'P2', c: 'P3' },
    warnings: [warning('a', 'P2', { priority: 2 }), warning('b', 'P2', { priority: 8 }), warning('c', 'P3', { priority: 3 })],
  });
  assert.deepEqual(routed.byPlayer.map((row) => [row.player, row.threatCount]), [['P2', 2], ['P3', 1]]);
});

directed('invalid projection confidence must fail closed', () => {
  const resolver = new PlayerAnchorResolver();
  const renderer = new AnchoredWarningRenderer({ resolver });
  const router = new TargetLockIndicatorRouter();
  const rng = lcg(4);
  const out = planOne({
    nowMs: 1000,
    target: 'P1',
    players: { P1: playerState(1000, 'P1', rng, { x: 0, y: 0, z: 0 }) },
    projection: projectionState(1000, { confidence: NaN }),
    drawingBuffer: drawingBufferState(1000), renderer, router,
  });
  assert.equal(out.plan.anchored.length, 0, 'non-finite projection confidence must not authorize anchored rendering');
  assert.equal(out.plan.fixed.length, 1, 'invalid projection confidence must use fixed HUD fallback');
});

let transitions = 0;
const seedSummaries = [];
for (const seed of SEEDS) {
  const rng = lcg(seed);
  const resolver = new PlayerAnchorResolver();
  const renderer = new AnchoredWarningRenderer({ resolver, smoothingAlpha: 0.2 });
  const router = new TargetLockIndicatorRouter({ holdMs: 240 });
  let priorTarget = null;
  let playerGeneration = 1;
  let projectionGeneration = 1;
  let mappingGeneration = 1;
  let anchoredCount = 0;
  let fallbackCount = 0;
  let invalidConfidenceAnchored = 0;
  let lastState = null;

  for (let step = 0; step < STEPS_PER_SEED; step += 1) {
    const nowMs = 10000 + step * 16;
    const target = PLAYERS[Math.floor(rng() * PLAYERS.length)];
    if (step && step % 131 === 0) playerGeneration += 1;
    if (step && step % 149 === 0) projectionGeneration += 1;
    if (step && step % 127 === 0) mappingGeneration += 1;

    const invalidConfidence = step > 0 && step % 257 === 0;
    const staleProjection = step > 0 && step % 251 === 0;
    const stalePlayer = step > 0 && step % 241 === 0;
    const outOfBounds = step > 0 && step % 239 === 0;
    const epochMismatch = step > 0 && step % 233 === 0;
    const cameraDiscontinuity = step > 0 && step % 137 === 0;
    const fullscreen = mappingGeneration % 2 === 0;
    const dpr = [1, 1.25, 1.5, 2, 3][step % 5];
    const width = fullscreen ? 1152 : 768;
    const height = fullscreen ? 672 : 448;

    const players = {};
    for (const player of PLAYERS) {
      players[player] = playerState(nowMs, player, rng, {
        sampleAtMs: stalePlayer && player === target ? nowMs - 121 : nowMs,
        epoch: epochMismatch && player === target ? 'epoch-stale' : 'epoch-1',
        lifecycleId: `${player}-life-${playerGeneration}`,
      });
    }
    const projection = projectionState(nowMs, {
      version: `proj-gen-${projectionGeneration}`,
      sampleAtMs: staleProjection ? nowMs - 121 : nowMs,
      confidence: invalidConfidence ? NaN : 1,
      cameraX: (rng() - 0.5) * 20,
      cameraY: (rng() - 0.5) * 8,
      forceAnchor: outOfBounds ? { x: -0.5, y: 80, bodyXNative: 192, bodyYNative: 112 } : null,
    });
    const drawingBuffer = drawingBufferState(nowMs, {
      width, height, fullscreen, dpr, mappingVersion: `map-${mappingGeneration}`,
    });
    const { plan } = planOne({ nowMs, target, players, projection, drawingBuffer, renderer, router, cameraDiscontinuity });
    transitions += 1;

    const owners = [...plan.anchored, ...plan.fixed].map((item) => item.player);
    if (owners.some((owner) => owner !== target)) {
      if (failures.length < 64) failures.push({ kind: 'stress', seed, step, invariant: 'visible owner must equal current target', target, owners });
    }
    if (priorTarget && priorTarget !== target && owners.includes(priorTarget)) {
      if (failures.length < 64) failures.push({ kind: 'stress', seed, step, invariant: 'old target ghost after retarget', priorTarget, target, owners });
    }

    const expectedInvalid = invalidConfidence || staleProjection || stalePlayer || outOfBounds || epochMismatch;
    if (expectedInvalid && plan.anchored.length !== 0) {
      if (invalidConfidence) invalidConfidenceAnchored += 1;
      if (failures.length < 64) failures.push({
        kind: 'stress', seed, step,
        invariant: 'invalid/stale projection state must never remain anchored',
        conditions: { invalidConfidence, staleProjection, stalePlayer, outOfBounds, epochMismatch },
        target,
      });
    }
    if (!expectedInvalid && plan.anchored.length !== 1) {
      if (failures.length < 64) failures.push({ kind: 'stress', seed, step, invariant: 'valid synthetic anchor should remain anchored', target, fixedReason: plan.fixed[0]?.reason || null });
    }

    anchoredCount += plan.anchored.length;
    fallbackCount += plan.fixed.length;
    lastState = {
      targetPlayer: target,
      playerGeneration,
      projectionGeneration,
      anchorValidity: plan.anchored.length === 1,
      rendererMode: plan.anchored.length === 1 ? 'anchored' : (plan.fixed.length ? 'fallback' : 'clear'),
      visibleOwner: owners[0] ?? null,
      staleOrClearReason: plan.fixed[0]?.reason ?? null,
    };
    priorTarget = target;
  }

  seedSummaries.push({ seed, steps: STEPS_PER_SEED, anchoredCount, fallbackCount, invalidConfidenceAnchored, lastState });
}

const summary = {
  status: failures.length ? 'BLOCKED' : 'PASS',
  stageId: 'HUDANCHOR_PLAYER_FOLLOW_LONG_STRESS_MATRIX_V1',
  sutBlob: SUT_BLOB,
  deterministic: true,
  seedCount: SEEDS.length,
  stepsPerSeed: STEPS_PER_SEED,
  transitions,
  directed: { passed: directedPassed, total: 8 },
  failureCount: failures.length,
  firstFailures: failures.slice(0, 16),
  seedSummaries,
};
process.stdout.write(JSON.stringify(summary, null, 2) + '\n');
if (failures.length) {
  process.stdout.write('BLOCKED — HUDANCHOR PLAYER-FOLLOW LONG STRESS — invalid/non-finite projection confidence authorizes anchored rendering instead of fixed-HUD fail-closed fallback\n');
  process.exitCode = 1;
} else {
  process.stdout.write('PASS — HUDANCHOR PLAYER-FOLLOW LONG STRESS — READY FOR REAL PROJECTION FREEZE\n');
}
