'use strict';

const assert = require('node:assert/strict');
const {
  PlayerAnchorResolver,
  TargetLockIndicatorRouter,
  AnchoredWarningRenderer,
} = require('../HUDANCHOR_PLAYER_FOLLOW/src/player_follow_reference');

const NOW = 1000;

function drawingBuffer() {
  return {
    width: 768,
    height: 448,
    sampleAtMs: NOW,
    epoch: 'qa-epoch-1',
    confidence: 1,
    mappingVersion: 'qa-map-1',
    fullscreen: false,
    contentRect: { x: 0, y: 0, width: 768, height: 448 },
  };
}

function player() {
  return {
    present: true,
    x: 10,
    y: 20,
    z: 0,
    sampleAtMs: NOW,
    epoch: 'qa-epoch-1',
    lifecycleId: 'qa-life-1',
    confidence: 1,
  };
}

function projection(anchorXNative, anchorYNative) {
  return {
    source: 'fresh-independent-qa-synthetic-only',
    version: 'qa-oob-anchor-v1',
    sampleAtMs: NOW,
    epoch: 'qa-epoch-1',
    nativeWidth: 384,
    nativeHeight: 224,
    confidence: 1,
    validationBounds: { minX: 0, maxX: 384, minY: 0, maxY: 224 },
    projectNative() {
      return {
        bodyXNative: 192,
        bodyYNative: 112,
        anchorXNative,
        anchorYNative,
        confidence: 1,
      };
    },
  };
}

function routeP1() {
  const router = new TargetLockIndicatorRouter();
  return router.route({
    nowMs: NOW,
    targets: { 'enemy-A': 'P1' },
    warnings: [{
      sourceId: 'enemy-A',
      targetPlayer: 'P1',
      active: true,
      visible: true,
      priority: 1,
    }],
  });
}

function build(anchorXNative, anchorYNative) {
  const resolver = new PlayerAnchorResolver();
  const renderer = new AnchoredWarningRenderer({ resolver });
  return renderer.buildPlan({
    nowMs: NOW,
    routed: routeP1(),
    players: { P1: player() },
    projectionState: projection(anchorXNative, anchorYNative),
    drawingBufferState: drawingBuffer(),
  });
}

const cases = [
  { name: 'finite anchor Y far above validation bounds', x: 192, y: -1000 },
  { name: 'finite anchor X far right of validation bounds', x: 1000, y: 80 },
];

for (const c of cases) {
  const plan = build(c.x, c.y);
  assert.equal(
    plan.anchored.length,
    0,
    `${c.name}: out-of-bounds anchor must not produce an anchored draw`,
  );
  assert.equal(
    plan.fixed.length,
    1,
    `${c.name}: out-of-bounds anchor must fail closed to fixed HUD`,
  );
  assert.equal(
    plan.fixed[0].reason,
    'PROJECTION_OUT_OF_BOUNDS',
    `${c.name}: failure reason must identify projection bounds invalidation`,
  );
}

process.stdout.write(JSON.stringify({
  status: 'PASS',
  suite: 'HUDANCHOR_PLAYER_FOLLOW_REFERENCE_FRESH_INDEPENDENT_QA',
  cases: cases.length,
}) + '\n');
