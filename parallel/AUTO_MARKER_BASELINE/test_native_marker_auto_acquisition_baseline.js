'use strict';
const assert = require('node:assert/strict');
const baseline = require('./native_marker_auto_acquisition_baseline.js');

const W = baseline.NATIVE_WIDTH, H = baseline.NATIVE_HEIGHT;
const COLORS = {
  P1: [220, 70, 70, 255],
  P2: [80, 120, 220, 255],
  P3: [70, 220, 80, 255]
};

function blankFrame() { return {width: W, height: H, data: new Uint8ClampedArray(W * H * 4)}; }
function pixel(frame, x, y, rgba) {
  const i = (y * W + x) * 4;
  frame.data[i] = rgba[0]; frame.data[i + 1] = rgba[1]; frame.data[i + 2] = rgba[2]; frame.data[i + 3] = rgba[3];
}
function rect(frame, x, y, w, h, rgba) {
  for (let yy = y; yy < y + h; yy++) for (let xx = x; xx < x + w; xx++) pixel(frame, xx, yy, rgba);
}
function downArrow(frame, cx, top, rgba) {
  rect(frame, cx - 1, top, 3, 4, rgba);
  rect(frame, cx - 3, top + 4, 7, 2, rgba);
  rect(frame, cx - 2, top + 6, 5, 2, rgba);
  rect(frame, cx - 1, top + 8, 3, 2, rgba);
  pixel(frame, cx, top + 10, rgba);
}
function marker(frame, player, x, labelTop) {
  const color = COLORS[player];
  rect(frame, x - 6, labelTop, 12, 7, color);
  downArrow(frame, x, labelTop + 15, color);
}
function frameWith(spec) {
  const f = blankFrame();
  for (const [player, rows] of Object.entries(spec)) for (const row of rows) marker(f, player, row.x, row.y);
  return f;
}
function fullFrame(p1 = {x: 90, y: 70}, p2 = {x: 190, y: 90}, p3 = {x: 290, y: 110}) {
  return frameWith({P1: [p1], P2: [p2], P3: [p3]});
}

function testZeroClickStartupAndPlayerDistinction() {
  const t = baseline.createBaselineTracker();
  const apiKeys = Object.keys(t).sort();
  assert.deepEqual(apiKeys, ['ingestFrame', 'reset', 'status']);
  assert.equal(globalThis.WOFAutoMarkerBaselineP37, baseline);
  const out = t.ingestFrame(fullFrame(), 0);
  assert.equal(out.classification, 'UNVERIFIED_AUTO_BASELINE');
  assert.equal(out.zeroClick, true);
  assert.equal(out.manualSeedRequired, false);
  assert.equal(out.manualPlayerSelectionRequired, false);
  assert.equal(out.state, 'TRACKING_ALL_PLAYERS');
  for (const p of ['P1', 'P2', 'P3']) {
    assert.equal(out.tracks[p].state, 'TRACKED');
    assert.equal(out.tracks[p].labelSemantic, `${p[1]}P`);
    assert.equal(out.tracks[p].observed, true);
  }
  assert.ok(out.tracks.P1.x < out.tracks.P2.x && out.tracks.P2.x < out.tracks.P3.x);
}

function testHorizontalAndVerticalOrientation() {
  const tx = baseline.createBaselineTracker();
  const x0 = tx.ingestFrame(fullFrame({x: 120, y: 95}), 0).tracks.P1;
  const right = tx.ingestFrame(fullFrame({x: 140, y: 95}), 100).tracks.P1;
  assert.ok(right.x > x0.x, 'right movement must increase native x');

  const txLeft = baseline.createBaselineTracker();
  const lx0 = txLeft.ingestFrame(fullFrame({x: 140, y: 95}), 0).tracks.P1;
  const left = txLeft.ingestFrame(fullFrame({x: 120, y: 95}), 100).tracks.P1;
  assert.ok(left.x < lx0.x, 'left movement must decrease native x');

  const tyUp = baseline.createBaselineTracker();
  const y0 = tyUp.ingestFrame(fullFrame({x: 120, y: 100}), 0).tracks.P1;
  const up = tyUp.ingestFrame(fullFrame({x: 120, y: 75}), 100).tracks.P1;
  assert.equal(up.state, 'TRACKED');
  assert.ok(up.y < y0.y, 'up movement must lower native y in top-left coordinates');

  const tyDown = baseline.createBaselineTracker();
  const dy0 = tyDown.ingestFrame(fullFrame({x: 120, y: 75}), 0).tracks.P1;
  const down = tyDown.ingestFrame(fullFrame({x: 120, y: 100}), 100).tracks.P1;
  assert.equal(down.state, 'TRACKED');
  assert.ok(down.y > dy0.y, 'down movement must increase native y');

  const viewport = {left: 40, top: 20, width: 768, height: 448};
  const mappedUp = baseline.mapNativeToViewport({x: up.x, y: up.y}, viewport);
  const mappedDown = baseline.mapNativeToViewport({x: down.x, y: down.y}, viewport);
  assert.ok(mappedDown.y > mappedUp.y, 'viewport mapping must preserve vertical orientation, not flip it');
  assert.equal(mappedDown.yTransform, 'PRESERVE_TOP_LEFT_POSITIVE_DOWN_NO_INVERSION');
  const roundTrip = baseline.mapViewportToNative(mappedDown, viewport);
  assert.ok(Math.abs(roundTrip.x - down.x) < 1e-9 && Math.abs(roundTrip.y - down.y) < 1e-9);
}

function testJumpShortLossAndAutomaticReacquire() {
  const t = baseline.createBaselineTracker();
  let out = t.ingestFrame(fullFrame({x: 90, y: 105}), 0);
  assert.equal(out.tracks.P1.state, 'TRACKED');
  out = t.ingestFrame(fullFrame({x: 102, y: 80}), 100);
  assert.equal(out.tracks.P1.state, 'TRACKED', 'jump-like up movement within historical bound stays tracked');

  out = t.ingestFrame(frameWith({P2: [{x: 190, y: 90}], P3: [{x: 290, y: 110}]}), 200);
  assert.equal(out.tracks.P1.state, 'COASTING');
  assert.equal(out.tracks.P1.observed, false);
  out = t.ingestFrame(frameWith({P2: [{x: 190, y: 90}], P3: [{x: 290, y: 110}]}), 1000);
  assert.equal(out.tracks.P1.state, 'LOST');

  out = t.ingestFrame(fullFrame({x: 165, y: 115}), 1100);
  assert.equal(out.tracks.P1.state, 'PENDING_REACQUIRE');
  out = t.ingestFrame(fullFrame({x: 167, y: 114}), 1200);
  assert.equal(out.tracks.P1.state, 'TRACKED');
  assert.equal(out.tracks.P1.acquisition, 'AUTO_REACQUIRED');
  assert.equal(out.tracks.P1.reacquireCount, 1);
}

function testAmbiguityFailsClosed() {
  const t = baseline.createBaselineTracker();
  const f = frameWith({
    P1: [{x: 80, y: 70}, {x: 250, y: 120}],
    P2: [{x: 170, y: 90}],
    P3: [{x: 300, y: 110}]
  });
  const out = t.ingestFrame(f, 0);
  assert.equal(out.state, 'AMBIGUOUS');
  assert.equal(out.tracks.P1.state, 'AMBIGUOUS');
  assert.equal(out.tracks.P1.x, null);
  assert.equal(out.tracks.P1.y, null);
  assert.equal(out.tracks.P1.ambiguityReason, 'MULTIPLE_NATIVE_LABEL_ARROW_CLUSTERS');
  assert.equal(out.tracks.P1.candidateCount, 2);
}

function testProofBoundaryCanNeverQualifyAuthority() {
  const t = baseline.createBaselineTracker();
  const out = t.ingestFrame(fullFrame(), 0);
  assert.equal(out.rendererSourceProof, null);
  assert.notEqual(out.coordinateAuthority, 'NATIVE_RENDERER_OBJECT_384X224');
  assert.deepEqual(out.authorityEligibility, {
    p29Pass: false,
    p32NativeMarkerQualification: false,
    p36RendererSourceTrace: false,
    p34RetryReadiness: false,
    promotion: false
  });
  assert.deepEqual(out.safety, {readOnly: true, ramWrites: 0, inputInjection: false});
}

function testInvalidFrameFailsClosed() {
  const t = baseline.createBaselineTracker();
  const out = t.ingestFrame({width: 192, height: 112, data: new Uint8ClampedArray(192 * 112 * 4)}, 0);
  assert.equal(out.state, 'FRAME_REJECTED');
  assert.equal(out.reason, 'FRAME_NATIVE_DIMENSIONS_INVALID');
  assert.equal(out.classification, 'UNVERIFIED_AUTO_BASELINE');
}

const tests = [
  testZeroClickStartupAndPlayerDistinction,
  testHorizontalAndVerticalOrientation,
  testJumpShortLossAndAutomaticReacquire,
  testAmbiguityFailsClosed,
  testProofBoundaryCanNeverQualifyAuthority,
  testInvalidFrameFailsClosed
];
for (const test of tests) {
  test();
  console.log(`PASS ${test.name}`);
}
console.log(`PASS ${tests.length}/${tests.length} P37 deterministic baseline tests`);
