'use strict';

/**
 * P37 zero-click native player-marker auto-acquisition baseline.
 *
 * This deliberately remains a diagnostic pixel/structure tracker. It is NOT a
 * renderer source proof, never claims P29/P32/P36 authority, and never makes a
 * candidate retry/promotion eligible.
 */

const NATIVE_WIDTH = 384;
const NATIVE_HEIGHT = 224;
const CLASSIFICATION = 'UNVERIFIED_AUTO_BASELINE';
const SCHEMA = 'wof-native-marker-auto-acquisition-baseline-v1';
const TRACK_LOST_MS = 850;
const FREEZE_MS = 260;
const PENDING_WINDOW_MS = 220;
const PENDING_RADIUS = 18;
const PLAYERS = Object.freeze(['P1', 'P2', 'P3']);
const LABELS = Object.freeze({P1: '1P', P2: '2P', P3: '3P'});

function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }
function finite(v) { return Number.isFinite(v); }
function keyOf(c) { return `${c.minx}:${c.miny}:${c.maxx}:${c.maxy}:${c.n}`; }

function playerColor(player, r, g, b) {
  if (player === 'P1') return r > 150 && r > g * 1.16 && r > b * 1.08;
  if (player === 'P2') return b > 135 && b > r * 1.10 && g > 62 && b >= g * 0.76;
  return (g > 125 && g > r * 1.03 && g > b * 1.08) || (r > 155 && g > 135 && b < 118);
}

function validateFrame(frame) {
  if (!frame || frame.width !== NATIVE_WIDTH || frame.height !== NATIVE_HEIGHT) {
    return 'FRAME_NATIVE_DIMENSIONS_INVALID';
  }
  const data = frame.data;
  if (!data || typeof data.length !== 'number' || data.length !== NATIVE_WIDTH * NATIVE_HEIGHT * 4) {
    return 'FRAME_RGBA_LENGTH_INVALID';
  }
  return null;
}

function buildMask(frame, player) {
  const mask = new Uint8Array(NATIVE_WIDTH * NATIVE_HEIGHT);
  const data = frame.data;
  for (let y = 24; y < NATIVE_HEIGHT - 10; y++) {
    for (let x = 3; x < NATIVE_WIDTH - 3; x++) {
      const i = y * NATIVE_WIDTH + x;
      const p = i * 4;
      if (data[p + 3] > 180 && playerColor(player, data[p], data[p + 1], data[p + 2])) mask[i] = 1;
    }
  }
  return mask;
}

function components(mask) {
  const seen = new Uint8Array(NATIVE_WIDTH * NATIVE_HEIGHT);
  const stack = new Int32Array(NATIVE_WIDTH * NATIVE_HEIGHT);
  const out = [];
  for (let y = 24; y < NATIVE_HEIGHT - 10; y++) {
    for (let x = 3; x < NATIVE_WIDTH - 3; x++) {
      const start = y * NATIVE_WIDTH + x;
      if (!mask[start] || seen[start]) continue;
      let sp = 0;
      stack[sp++] = start;
      seen[start] = 1;
      let minx = x, maxx = x, miny = y, maxy = y, n = 0;
      while (sp) {
        const q = stack[--sp];
        const qy = (q / NATIVE_WIDTH) | 0;
        const qx = q - qy * NATIVE_WIDTH;
        n++;
        if (qx < minx) minx = qx;
        if (qx > maxx) maxx = qx;
        if (qy < miny) miny = qy;
        if (qy > maxy) maxy = qy;
        const left = q - 1, right = q + 1, up = q - NATIVE_WIDTH, down = q + NATIVE_WIDTH;
        if (qx > 3 && mask[left] && !seen[left]) { seen[left] = 1; stack[sp++] = left; }
        if (qx < NATIVE_WIDTH - 4 && mask[right] && !seen[right]) { seen[right] = 1; stack[sp++] = right; }
        if (qy > 24 && mask[up] && !seen[up]) { seen[up] = 1; stack[sp++] = up; }
        if (qy < NATIVE_HEIGHT - 11 && mask[down] && !seen[down]) { seen[down] = 1; stack[sp++] = down; }
      }
      const w = maxx - minx + 1, h = maxy - miny + 1, density = n / (w * h);
      if (n >= 2 && n <= 320 && w <= 30 && h <= 28 && density >= 0.09) {
        out.push({minx, maxx, miny, maxy, w, h, n, cx: (minx + maxx) / 2, cy: (miny + maxy) / 2, density});
      }
    }
  }
  return out;
}

function textCandidates(comps) {
  const out = [];
  for (const c of comps) {
    if (c.w >= 5 && c.w <= 18 && c.h >= 4 && c.h <= 11 && c.n >= 6) {
      out.push({...c, pair: false, componentKeys: [keyOf(c)]});
    }
  }
  for (let i = 0; i < comps.length; i++) {
    for (let j = i + 1; j < comps.length; j++) {
      let a = comps[i], b = comps[j];
      if (a.minx > b.minx) [a, b] = [b, a];
      const gap = b.minx - a.maxx - 1;
      const dy = Math.abs(a.cy - b.cy);
      const minx = a.minx, maxx = b.maxx, miny = Math.min(a.miny, b.miny), maxy = Math.max(a.maxy, b.maxy);
      const w = maxx - minx + 1, h = maxy - miny + 1, n = a.n + b.n;
      if (gap >= -1 && gap <= 6 && dy <= 3.5 && w >= 7 && w <= 24 && h >= 4 && h <= 12 && n >= 8 && n <= 150) {
        out.push({minx, maxx, miny, maxy, w, h, n, cx: (minx + maxx) / 2, cy: (miny + maxy) / 2,
          pair: true, componentKeys: [keyOf(a), keyOf(b)].sort()});
      }
    }
  }
  return out;
}

function arrowRelations(text, comps) {
  const out = [];
  for (const arrow of comps) {
    const arrowKey = keyOf(arrow);
    if (text.componentKeys.includes(arrowKey)) continue;
    const gap = arrow.miny - text.maxy;
    const dx = Math.abs(arrow.cx - text.cx);
    if (gap < 3 || gap > 26 || dx > 10) continue;
    if (arrow.w < 5 || arrow.w > 22 || arrow.h < 5 || arrow.h > 22 || arrow.n < 8) continue;
    const arrowScore = 80 - dx * 5 - Math.abs(gap - 11) * 2 - Math.abs(arrow.h - 10) * 1.5;
    const labelScore = (text.pair ? 28 : 6) - Math.abs(text.h - 7) * 2.5 - Math.abs(text.w - 12) * 1.2;
    out.push({text, arrow, arrowKey, score: labelScore + arrowScore});
  }
  return out;
}

function sharesComponent(a, b) {
  return a.text.componentKeys.some(k => b.text.componentKeys.includes(k));
}

function canonicalMarkerCandidates(comps) {
  const relations = [];
  for (const text of textCandidates(comps)) relations.push(...arrowRelations(text, comps));
  const byArrow = new Map();
  for (const relation of relations) {
    if (!byArrow.has(relation.arrowKey)) byArrow.set(relation.arrowKey, []);
    byArrow.get(relation.arrowKey).push(relation);
  }

  const candidates = [];
  const internalAmbiguities = [];
  for (const [arrowKey, rows] of byArrow.entries()) {
    const groups = [];
    for (const row of rows) {
      const touching = groups.filter(g => g.some(existing => sharesComponent(existing, row)));
      if (!touching.length) groups.push([row]);
      else {
        const merged = [row];
        for (const group of touching) {
          merged.push(...group);
          groups.splice(groups.indexOf(group), 1);
        }
        groups.push(merged);
      }
    }
    if (groups.length !== 1) {
      internalAmbiguities.push({arrowKey, reason: 'MULTIPLE_DISJOINT_LABEL_GROUPS_FOR_ARROW'});
      continue;
    }
    const group = groups[0];
    group.sort((a, b) => {
      if (b.score !== a.score) return b.score - a.score;
      if ((b.text.pair ? 1 : 0) !== (a.text.pair ? 1 : 0)) return (b.text.pair ? 1 : 0) - (a.text.pair ? 1 : 0);
      if (b.text.n !== a.text.n) return b.text.n - a.text.n;
      return a.text.componentKeys.join('|').localeCompare(b.text.componentKeys.join('|'));
    });
    const best = group[0];
    if (best.score < 20) continue;
    const arrow = best.arrow;
    candidates.push({
      x: arrow.cx,
      y: arrow.maxy,
      labelPoint: {x: best.text.cx, y: best.text.miny},
      arrowBox: {minx: arrow.minx, maxx: arrow.maxx, miny: arrow.miny, maxy: arrow.maxy},
      labelBox: {minx: best.text.minx, maxx: best.text.maxx, miny: best.text.miny, maxy: best.text.maxy},
      markerKey: `${best.text.componentKeys.join('+')}=>${arrowKey}`,
      score: best.score,
      source: 'HISTORICAL_NATIVE_COLOR_LABEL_ARROW_PIXEL_STRUCTURE'
    });
  }
  candidates.sort((a, b) => a.markerKey.localeCompare(b.markerKey));
  return {candidates, internalAmbiguities};
}

function detectPlayer(frame, player) {
  const mask = buildMask(frame, player);
  const comps = components(mask);
  const {candidates, internalAmbiguities} = canonicalMarkerCandidates(comps);
  if (internalAmbiguities.length) {
    return {state: 'AMBIGUOUS', reason: 'INTERNAL_MARKER_STRUCTURE_AMBIGUOUS', candidates: [], detail: internalAmbiguities};
  }
  if (candidates.length === 0) return {state: 'NOT_FOUND', reason: 'NO_NATIVE_LABEL_ARROW_CLUSTER', candidates: []};
  if (candidates.length > 1) {
    return {state: 'AMBIGUOUS', reason: 'MULTIPLE_NATIVE_LABEL_ARROW_CLUSTERS', candidates};
  }
  return {state: 'FOUND', reason: null, candidates};
}

function newTrack() {
  return {hit: null, vx: 0, vy: 0, pending: null, acceptedCount: 0, reacquireCount: 0};
}

function predicted(track, nowMs) {
  if (!track.hit) return null;
  const dt = clamp((nowMs - track.hit.at) / 1000, 0, 0.35);
  return {x: track.hit.x + track.vx * dt, y: track.hit.y + track.vy * dt};
}

function dynamicMaxDistance(ageMs) {
  if (ageMs < 220) return 34;
  if (ageMs < 450) return 52;
  return 70;
}

function acceptHit(track, candidate, nowMs, reacquired) {
  const old = track.hit;
  if (old) {
    const dt = Math.max(0.03, (nowMs - old.at) / 1000);
    const nvx = clamp((candidate.x - old.x) / dt, -280, 280);
    const nvy = clamp((candidate.y - old.y) / dt, -380, 380);
    track.vx = track.vx * 0.45 + nvx * 0.55;
    track.vy = track.vy * 0.45 + nvy * 0.55;
  }
  track.hit = {...candidate, at: nowMs};
  track.pending = null;
  track.acceptedCount++;
  if (reacquired) track.reacquireCount++;
}

function pendingConfirmed(track, candidate, nowMs) {
  if (!track.pending) return false;
  if (nowMs - track.pending.at > PENDING_WINDOW_MS) return false;
  return Math.hypot(candidate.x - track.pending.x, candidate.y - track.pending.y) < PENDING_RADIUS;
}

function snapshotTrack(player, track, state, nowMs, extras = {}) {
  const h = track.hit;
  const ageMs = h ? nowMs - h.at : null;
  const base = {
    player,
    labelSemantic: LABELS[player],
    state,
    x: null,
    y: null,
    observed: false,
    coordinateClass: null,
    nativeWidth: NATIVE_WIDTH,
    nativeHeight: NATIVE_HEIGHT,
    nativeYAxis: 'TOP_LEFT_POSITIVE_DOWN',
    ageMs,
    velocity: {xPerSecond: track.vx, yPerSecond: track.vy},
    acceptedCount: track.acceptedCount,
    reacquireCount: track.reacquireCount,
    ambiguityReason: null,
    candidateCount: 0,
    ...extras
  };
  if (state === 'TRACKED' && h) {
    base.x = h.x; base.y = h.y; base.observed = true; base.coordinateClass = 'OBSERVED_DIAGNOSTIC_PIXEL_STRUCTURE';
    base.markerKey = h.markerKey; base.labelPoint = {...h.labelPoint}; base.arrowBox = {...h.arrowBox}; base.labelBox = {...h.labelBox};
  } else if (state === 'COASTING' && h) {
    const p = predicted(track, nowMs);
    base.x = p.x; base.y = p.y; base.coordinateClass = 'PREDICTED_DIAGNOSTIC_ONLY';
  }
  return base;
}

function createBaselineTracker(options = {}) {
  const tracks = {P1: newTrack(), P2: newTrack(), P3: newTrack()};
  let lastTimestampMs = null;
  const cfg = {
    trackLostMs: options.trackLostMs ?? TRACK_LOST_MS,
    freezeMs: options.freezeMs ?? FREEZE_MS
  };

  function ingestFrame(frame, timestampMs) {
    if (!finite(timestampMs)) throw new TypeError('timestampMs must be finite');
    if (lastTimestampMs !== null && timestampMs < lastTimestampMs) throw new Error('timestampMs must be monotonic');
    lastTimestampMs = timestampMs;
    const frameError = validateFrame(frame);
    if (frameError) return diagnosticEnvelope('FRAME_REJECTED', timestampMs, {
      reason: frameError,
      tracks: Object.fromEntries(PLAYERS.map(p => [p, snapshotTrack(p, tracks[p], 'FRAME_REJECTED', timestampMs)]))
    });

    const detections = Object.fromEntries(PLAYERS.map(player => [player, detectPlayer(frame, player)]));
    const snapshots = {};

    for (const player of PLAYERS) {
      const track = tracks[player], detection = detections[player];
      if (detection.state === 'AMBIGUOUS') {
        track.pending = null;
        snapshots[player] = snapshotTrack(player, track, 'AMBIGUOUS', timestampMs, {
          ambiguityReason: detection.reason,
          candidateCount: detection.candidates.length,
          candidates: detection.candidates.map(c => ({x: c.x, y: c.y, markerKey: c.markerKey}))
        });
        continue;
      }

      if (detection.state === 'FOUND') {
        const candidate = detection.candidates[0];
        if (!track.hit) {
          acceptHit(track, candidate, timestampMs, false);
          snapshots[player] = snapshotTrack(player, track, 'TRACKED', timestampMs, {acquisition: 'AUTO_INITIAL'});
          continue;
        }
        const age = timestampMs - track.hit.at;
        const p = predicted(track, timestampMs);
        const distance = Math.hypot(candidate.x - p.x, candidate.y - p.y);
        if (age <= cfg.trackLostMs && distance <= dynamicMaxDistance(age)) {
          acceptHit(track, candidate, timestampMs, false);
          snapshots[player] = snapshotTrack(player, track, 'TRACKED', timestampMs, {acquisition: 'AUTO_CONTINUITY'});
          continue;
        }
        if (pendingConfirmed(track, candidate, timestampMs)) {
          acceptHit(track, candidate, timestampMs, true);
          snapshots[player] = snapshotTrack(player, track, 'TRACKED', timestampMs, {acquisition: 'AUTO_REACQUIRED'});
          continue;
        }
        track.pending = {...candidate, at: timestampMs};
        snapshots[player] = snapshotTrack(player, track, 'PENDING_REACQUIRE', timestampMs, {
          candidateCount: 1,
          pendingCandidate: {x: candidate.x, y: candidate.y, markerKey: candidate.markerKey},
          reason: age > cfg.trackLostMs ? 'LONG_LOSS_REQUIRES_SECOND_AUTOMATIC_CONFIRMATION' : 'LARGE_JUMP_REQUIRES_SECOND_AUTOMATIC_CONFIRMATION'
        });
        continue;
      }

      track.pending = null;
      if (!track.hit) {
        snapshots[player] = snapshotTrack(player, track, 'SEARCHING', timestampMs, {reason: detection.reason});
        continue;
      }
      const age = timestampMs - track.hit.at;
      if (age <= cfg.freezeMs) snapshots[player] = snapshotTrack(player, track, 'COASTING', timestampMs, {reason: 'BOUNDED_SHORT_LOSS'});
      else if (age <= cfg.trackLostMs) snapshots[player] = snapshotTrack(player, track, 'SEARCHING', timestampMs, {reason: 'TRACK_TEMPORARILY_MISSING'});
      else snapshots[player] = snapshotTrack(player, track, 'LOST', timestampMs, {reason: 'TRACK_LOST_REACQUIRE_AUTOMATIC'});
    }

    const ambiguousPlayers = PLAYERS.filter(p => snapshots[p].state === 'AMBIGUOUS');
    const trackedPlayers = PLAYERS.filter(p => snapshots[p].state === 'TRACKED');
    const overall = ambiguousPlayers.length ? 'AMBIGUOUS' : trackedPlayers.length === 3 ? 'TRACKING_ALL_PLAYERS' : 'TRACKING_PARTIAL';
    return diagnosticEnvelope(overall, timestampMs, {tracks: snapshots, ambiguousPlayers, trackedPlayers});
  }

  function reset() {
    for (const p of PLAYERS) tracks[p] = newTrack();
    lastTimestampMs = null;
  }

  return Object.freeze({ingestFrame, reset, status: () => diagnosticEnvelope('READY', lastTimestampMs, {
    tracks: Object.fromEntries(PLAYERS.map(p => [p, snapshotTrack(p, tracks[p], tracks[p].hit ? 'TRACKED' : 'SEARCHING', lastTimestampMs ?? 0)]))
  })});
}

function diagnosticEnvelope(state, timestampMs, extra = {}) {
  return {
    schema: SCHEMA,
    classification: CLASSIFICATION,
    state,
    timestampMs,
    nativeWidth: NATIVE_WIDTH,
    nativeHeight: NATIVE_HEIGHT,
    coordinateAuthority: 'DIAGNOSTIC_FRAME_PIXEL_NATIVE_384X224_NOT_RENDERER',
    nativeYAxis: 'TOP_LEFT_POSITIVE_DOWN',
    zeroClick: true,
    manualSeedRequired: false,
    manualPlayerSelectionRequired: false,
    rendererSourceProof: null,
    authorityEligibility: {
      p29Pass: false,
      p32NativeMarkerQualification: false,
      p36RendererSourceTrace: false,
      p34RetryReadiness: false,
      promotion: false
    },
    safety: {readOnly: true, ramWrites: 0, inputInjection: false},
    ...extra
  };
}

function mapNativeToViewport(point, rect) {
  if (!point || !rect || !finite(point.x) || !finite(point.y) || !finite(rect.left) || !finite(rect.top) || !finite(rect.width) || !finite(rect.height) || rect.width <= 0 || rect.height <= 0) {
    throw new TypeError('valid native point and viewport rect required');
  }
  if (point.x < 0 || point.x > NATIVE_WIDTH || point.y < 0 || point.y > NATIVE_HEIGHT) throw new RangeError('native point outside 384x224');
  return {
    x: rect.left + point.x * rect.width / NATIVE_WIDTH,
    y: rect.top + point.y * rect.height / NATIVE_HEIGHT,
    yTransform: 'PRESERVE_TOP_LEFT_POSITIVE_DOWN_NO_INVERSION'
  };
}

function mapViewportToNative(point, rect) {
  if (!point || !rect || !finite(point.x) || !finite(point.y) || !finite(rect.left) || !finite(rect.top) || !finite(rect.width) || !finite(rect.height) || rect.width <= 0 || rect.height <= 0) {
    throw new TypeError('valid viewport point and rect required');
  }
  return {
    x: (point.x - rect.left) * NATIVE_WIDTH / rect.width,
    y: (point.y - rect.top) * NATIVE_HEIGHT / rect.height,
    yTransform: 'PRESERVE_TOP_LEFT_POSITIVE_DOWN_NO_INVERSION'
  };
}

const API = Object.freeze({
  NATIVE_WIDTH,
  NATIVE_HEIGHT,
  CLASSIFICATION,
  SCHEMA,
  createBaselineTracker,
  detectPlayer,
  mapNativeToViewport,
  mapViewportToNative,
  _test: Object.freeze({playerColor, components, textCandidates, canonicalMarkerCandidates})
});

// Browser diagnostic use is zero-click: a caller feeds native 384x224 RGBA frames;
// no click/focus/portrait/manual seed API exists. This global is intentionally P37-only.
if (typeof globalThis !== 'undefined') globalThis.WOFAutoMarkerBaselineP37 = API;
if (typeof module !== 'undefined' && module.exports) module.exports = API;
