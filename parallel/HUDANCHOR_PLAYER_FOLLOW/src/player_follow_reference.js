'use strict';

const PLAYERS = Object.freeze(['P1', 'P2', 'P3']);
const PLAYER_SET = new Set(PLAYERS);

function finite(value) {
  return Number.isFinite(value);
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function own(obj, key) {
  return Object.prototype.hasOwnProperty.call(obj || {}, key);
}

function ageMs(nowMs, sampleAtMs) {
  return finite(nowMs) && finite(sampleAtMs) ? Math.max(0, nowMs - sampleAtMs) : Infinity;
}

function confidenceOf(value, fallback = 1) {
  return finite(value) ? clamp(value, 0, 1) : fallback;
}

function contentRectOf(drawingBufferState) {
  if (!drawingBufferState) return null;
  const width = drawingBufferState.width;
  const height = drawingBufferState.height;
  if (!(finite(width) && width > 0 && finite(height) && height > 0)) return null;

  const rect = drawingBufferState.contentRect || { x: 0, y: 0, width, height };
  if (!(finite(rect.x) && finite(rect.y) && finite(rect.width) && rect.width > 0 && finite(rect.height) && rect.height > 0)) {
    return null;
  }
  if (rect.x < 0 || rect.y < 0 || rect.x + rect.width > width || rect.y + rect.height > height) {
    return null;
  }
  return { x: rect.x, y: rect.y, width: rect.width, height: rect.height };
}

function epochMismatch(states) {
  const epochs = states
    .map((state) => state && state.epoch)
    .filter((value) => value !== undefined && value !== null);
  if (epochs.length < 2) return false;
  return epochs.some((value) => value !== epochs[0]);
}

function failAnchor(player, reason, metadata = {}) {
  return {
    ok: false,
    player,
    xDb: null,
    yDb: null,
    bodyXDb: null,
    bodyYDb: null,
    source: metadata.source || null,
    projectionVersion: metadata.projectionVersion || null,
    sampleAtMs: metadata.sampleAtMs ?? null,
    ageMs: metadata.ageMs ?? Infinity,
    confidence: 0,
    reason,
    mappingKey: metadata.mappingKey || null,
  };
}

class PlayerAnchorResolver {
  constructor(options = {}) {
    this.maxPlayerAgeMs = finite(options.maxPlayerAgeMs) ? options.maxPlayerAgeMs : 120;
    this.maxProjectionAgeMs = finite(options.maxProjectionAgeMs) ? options.maxProjectionAgeMs : 120;
    this.maxDrawingBufferAgeMs = finite(options.maxDrawingBufferAgeMs) ? options.maxDrawingBufferAgeMs : 1000;
  }

  resolve({ player, nowMs, playerState, projectionState, drawingBufferState }) {
    if (!PLAYER_SET.has(player)) return failAnchor(player, 'INVALID_PLAYER');
    if (!playerState || playerState.present === false) return failAnchor(player, 'PLAYER_ABSENT');
    if (!(finite(playerState.x) && finite(playerState.y) && finite(playerState.z))) {
      return failAnchor(player, 'INVALID_PLAYER_XYZ');
    }

    const playerAge = ageMs(nowMs, playerState.sampleAtMs);
    if (playerAge > this.maxPlayerAgeMs) {
      return failAnchor(player, 'STALE_PLAYER', { ageMs: playerAge, sampleAtMs: playerState.sampleAtMs });
    }

    if (!projectionState || typeof projectionState.projectNative !== 'function' || !projectionState.version) {
      return failAnchor(player, 'INVALID_PROJECTION_STATE');
    }
    const projectionAge = ageMs(nowMs, projectionState.sampleAtMs);
    if (projectionAge > this.maxProjectionAgeMs) {
      return failAnchor(player, 'STALE_PROJECTION', {
        source: projectionState.source,
        projectionVersion: projectionState.version,
        ageMs: projectionAge,
        sampleAtMs: projectionState.sampleAtMs,
      });
    }

    const rect = contentRectOf(drawingBufferState);
    if (!rect) {
      return failAnchor(player, 'INVALID_DRAWING_BUFFER', {
        source: projectionState.source,
        projectionVersion: projectionState.version,
      });
    }
    const bufferAge = ageMs(nowMs, drawingBufferState.sampleAtMs);
    if (bufferAge > this.maxDrawingBufferAgeMs) {
      return failAnchor(player, 'STALE_DRAWING_BUFFER', {
        source: projectionState.source,
        projectionVersion: projectionState.version,
        ageMs: bufferAge,
        sampleAtMs: drawingBufferState.sampleAtMs,
      });
    }

    if (epochMismatch([playerState, projectionState, drawingBufferState])) {
      return failAnchor(player, 'EPOCH_MISMATCH', {
        source: projectionState.source,
        projectionVersion: projectionState.version,
      });
    }

    const nativeWidth = projectionState.nativeWidth;
    const nativeHeight = projectionState.nativeHeight;
    if (!(finite(nativeWidth) && nativeWidth > 0 && finite(nativeHeight) && nativeHeight > 0)) {
      return failAnchor(player, 'INVALID_NATIVE_VIEWPORT', {
        source: projectionState.source,
        projectionVersion: projectionState.version,
      });
    }

    let projected;
    try {
      projected = projectionState.projectNative({
        player,
        x: playerState.x,
        y: playerState.y,
        z: playerState.z,
        lifecycleId: playerState.lifecycleId ?? null,
        camera: projectionState.camera || null,
        projectionState,
      });
    } catch (error) {
      return failAnchor(player, 'PROJECTION_ERROR', {
        source: projectionState.source,
        projectionVersion: projectionState.version,
      });
    }

    if (!projected || ![
      projected.anchorXNative,
      projected.anchorYNative,
      projected.bodyXNative,
      projected.bodyYNative,
    ].every(finite)) {
      return failAnchor(player, 'PROJECTION_NONFINITE', {
        source: projectionState.source,
        projectionVersion: projectionState.version,
      });
    }

    const bounds = projectionState.validationBounds || {
      minX: 0,
      maxX: nativeWidth,
      minY: 0,
      maxY: nativeHeight,
    };
    if (!(finite(bounds.minX) && finite(bounds.maxX) && finite(bounds.minY) && finite(bounds.maxY))) {
      return failAnchor(player, 'INVALID_VALIDATION_BOUNDS', {
        source: projectionState.source,
        projectionVersion: projectionState.version,
      });
    }
    if (
      projected.bodyXNative < bounds.minX || projected.bodyXNative > bounds.maxX ||
      projected.bodyYNative < bounds.minY || projected.bodyYNative > bounds.maxY
    ) {
      return failAnchor(player, 'PROJECTION_OUT_OF_BOUNDS', {
        source: projectionState.source,
        projectionVersion: projectionState.version,
      });
    }

    const sx = rect.width / nativeWidth;
    const sy = rect.height / nativeHeight;
    const xDb = rect.x + projected.anchorXNative * sx;
    const yDb = rect.y + projected.anchorYNative * sy;
    const bodyXDb = rect.x + projected.bodyXNative * sx;
    const bodyYDb = rect.y + projected.bodyYNative * sy;

    if (![xDb, yDb, bodyXDb, bodyYDb].every(finite)) {
      return failAnchor(player, 'DRAWING_BUFFER_PROJECTION_NONFINITE', {
        source: projectionState.source,
        projectionVersion: projectionState.version,
      });
    }

    const mappingKey = [
      drawingBufferState.width,
      drawingBufferState.height,
      rect.x,
      rect.y,
      rect.width,
      rect.height,
      drawingBufferState.mappingVersion ?? '',
      drawingBufferState.fullscreen ? 'fs' : 'win',
      projectionState.version,
    ].join(':');

    return {
      ok: true,
      player,
      xDb,
      yDb,
      bodyXDb,
      bodyYDb,
      source: projectionState.source || 'injected-projection',
      projectionVersion: projectionState.version,
      sampleAtMs: Math.min(playerState.sampleAtMs, projectionState.sampleAtMs, drawingBufferState.sampleAtMs),
      ageMs: Math.max(playerAge, projectionAge, bufferAge),
      confidence: Math.min(
        confidenceOf(playerState.confidence),
        confidenceOf(projectionState.confidence),
        confidenceOf(drawingBufferState.confidence),
        confidenceOf(projected.confidence),
      ),
      reason: null,
      mappingKey,
      lifecycleId: playerState.lifecycleId ?? null,
    };
  }
}

function defaultPriorityOf(warning) {
  return finite(warning && warning.priority) ? warning.priority : 0;
}

class TargetLockIndicatorRouter {
  constructor(options = {}) {
    this.holdMs = finite(options.holdMs) && options.holdMs >= 0 ? options.holdMs : 0;
    this.priorityOf = typeof options.priorityOf === 'function' ? options.priorityOf : defaultPriorityOf;
    this.holds = new Map();
    this.lastTargets = new Map();
  }

  reset() {
    this.holds.clear();
    this.lastTargets.clear();
  }

  _invalidateSource(sourceId, reason, invalidated) {
    const prior = this.holds.get(sourceId);
    if (prior) {
      invalidated.push({ sourceId, player: prior.targetPlayer, reason });
      this.holds.delete(sourceId);
    }
  }

  route({ nowMs, warnings = [], targets = {} }) {
    if (!finite(nowMs)) throw new TypeError('nowMs must be finite');
    const invalidated = [];

    for (const [sourceId, rawTarget] of Object.entries(targets || {})) {
      const target = PLAYER_SET.has(rawTarget) ? rawTarget : null;
      const previous = this.lastTargets.get(sourceId);
      if (previous !== undefined && previous !== target) {
        this._invalidateSource(sourceId, 'RETARGET', invalidated);
      }
      this.lastTargets.set(sourceId, target);
      if (target === null) this._invalidateSource(sourceId, 'TARGET_INVALID', invalidated);
    }

    for (const warning of warnings || []) {
      if (!warning || typeof warning.sourceId !== 'string' || warning.sourceId.length === 0) continue;
      const sourceId = warning.sourceId;
      const explicitTarget = own(targets, sourceId) ? targets[sourceId] : warning.targetPlayer;
      const targetPlayer = PLAYER_SET.has(explicitTarget) ? explicitTarget : null;
      const previous = this.lastTargets.get(sourceId);
      if (previous !== undefined && previous !== targetPlayer) {
        this._invalidateSource(sourceId, 'RETARGET', invalidated);
      }
      this.lastTargets.set(sourceId, targetPlayer);

      if (!targetPlayer) {
        this._invalidateSource(sourceId, 'TARGET_INVALID', invalidated);
        continue;
      }

      if (warning.visible === false || warning.active === false) {
        continue;
      }

      this.holds.set(sourceId, {
        sourceId,
        targetPlayer,
        warning,
        expiresAtMs: nowMs + this.holdMs,
        lastSeenAtMs: nowMs,
      });
    }

    for (const [sourceId, hold] of this.holds.entries()) {
      if (hold.expiresAtMs < nowMs) this.holds.delete(sourceId);
    }

    const grouped = new Map(PLAYERS.map((player) => [player, []]));
    for (const hold of this.holds.values()) {
      if (PLAYER_SET.has(hold.targetPlayer)) grouped.get(hold.targetPlayer).push(hold);
    }

    const byPlayer = [];
    for (const player of PLAYERS) {
      const threats = grouped.get(player);
      if (!threats.length) continue;
      threats.sort((a, b) => {
        const p = this.priorityOf(b.warning) - this.priorityOf(a.warning);
        return p || a.sourceId.localeCompare(b.sourceId);
      });
      byPlayer.push({
        player,
        warning: threats[0].warning,
        threats: threats.map((item) => item.warning),
        threatCount: threats.length,
        sourceIds: threats.map((item) => item.sourceId),
      });
    }

    return { byPlayer, invalidated };
  }
}

function dbRectToClip(rect, drawingBufferState) {
  const width = drawingBufferState && drawingBufferState.width;
  const height = drawingBufferState && drawingBufferState.height;
  if (!(finite(width) && width > 0 && finite(height) && height > 0)) {
    throw new TypeError('valid drawing buffer dimensions required');
  }
  return {
    left: rect.x / width * 2 - 1,
    right: (rect.x + rect.width) / width * 2 - 1,
    top: 1 - rect.y / height * 2,
    bottom: 1 - (rect.y + rect.height) / height * 2,
  };
}

class PlayerFollowStateMachine {
  constructor(options = {}) {
    this.smoothingAlpha = finite(options.smoothingAlpha) && options.smoothingAlpha > 0 && options.smoothingAlpha < 1
      ? options.smoothingAlpha
      : null;
    this.state = new Map();
  }

  clear(player) {
    this.state.delete(player);
  }

  clearExcept(players) {
    const keep = new Set(players);
    for (const player of this.state.keys()) {
      if (!keep.has(player)) this.state.delete(player);
    }
  }

  update({ player, anchor, cameraDiscontinuity = false }) {
    if (!anchor || !anchor.ok) {
      this.clear(player);
      return null;
    }

    const previous = this.state.get(player);
    const reset = !previous ||
      previous.lifecycleId !== anchor.lifecycleId ||
      previous.projectionVersion !== anchor.projectionVersion ||
      previous.mappingKey !== anchor.mappingKey ||
      cameraDiscontinuity;

    let x = anchor.xDb;
    let y = anchor.yDb;
    if (!reset && this.smoothingAlpha !== null) {
      x = previous.x + (anchor.xDb - previous.x) * this.smoothingAlpha;
      y = previous.y + (anchor.yDb - previous.y) * this.smoothingAlpha;
    }

    const next = {
      x,
      y,
      lifecycleId: anchor.lifecycleId,
      projectionVersion: anchor.projectionVersion,
      mappingKey: anchor.mappingKey,
    };
    this.state.set(player, next);
    return { x, y, reset };
  }
}

class AnchoredWarningRenderer {
  constructor(options = {}) {
    if (!options.resolver || typeof options.resolver.resolve !== 'function') {
      throw new TypeError('resolver is required');
    }
    this.resolver = options.resolver;
    this.boxWidth = finite(options.boxWidth) && options.boxWidth > 0 ? options.boxWidth : 96;
    this.boxHeight = finite(options.boxHeight) && options.boxHeight > 0 ? options.boxHeight : 28;
    this.follow = new PlayerFollowStateMachine({ smoothingAlpha: options.smoothingAlpha });
  }

  buildPlan({
    nowMs,
    routed,
    players,
    projectionState,
    drawingBufferState,
    cameraDiscontinuity = false,
  }) {
    const rect = contentRectOf(drawingBufferState);
    const byPlayer = routed && Array.isArray(routed.byPlayer) ? routed.byPlayer : [];
    const activePlayers = byPlayer.map((row) => row.player);
    this.follow.clearExcept(activePlayers);

    const anchored = [];
    const fixed = [];

    for (const row of byPlayer) {
      const playerState = players && players[row.player];
      const anchor = this.resolver.resolve({
        player: row.player,
        nowMs,
        playerState,
        projectionState,
        drawingBufferState,
      });

      if (!anchor.ok || !rect) {
        this.follow.clear(row.player);
        fixed.push({
          player: row.player,
          warning: row.warning,
          threats: row.threats,
          threatCount: row.threatCount,
          reason: anchor.reason || 'INVALID_VIEWPORT',
        });
        continue;
      }

      const point = this.follow.update({ player: row.player, anchor, cameraDiscontinuity });
      if (!point) {
        fixed.push({
          player: row.player,
          warning: row.warning,
          threats: row.threats,
          threatCount: row.threatCount,
          reason: 'FOLLOW_STATE_INVALID',
        });
        continue;
      }

      const maxX = rect.x + Math.max(0, rect.width - this.boxWidth);
      const maxY = rect.y + Math.max(0, rect.height - this.boxHeight);
      const drawRectDb = {
        x: clamp(point.x - this.boxWidth / 2, rect.x, maxX),
        y: clamp(point.y - this.boxHeight / 2, rect.y, maxY),
        width: Math.min(this.boxWidth, rect.width),
        height: Math.min(this.boxHeight, rect.height),
      };

      anchored.push({
        player: row.player,
        warning: row.warning,
        threats: row.threats,
        threatCount: row.threatCount,
        anchor,
        followPointDb: { x: point.x, y: point.y },
        smoothingReset: point.reset,
        drawRectDb,
        clipRect: dbRectToClip(drawRectDb, drawingBufferState),
      });
    }

    return {
      coordinateSpace: 'webgl-drawing-buffer',
      anchored,
      fixed,
      drawingBuffer: drawingBufferState ? {
        width: drawingBufferState.width,
        height: drawingBufferState.height,
        contentRect: rect,
      } : null,
    };
  }

  executePlan(plan, adapter) {
    if (!adapter) return plan;
    if (typeof adapter.beginFrame === 'function') adapter.beginFrame(plan);
    if (typeof adapter.drawAnchored === 'function') {
      for (const item of plan.anchored) adapter.drawAnchored(item);
    }
    if (typeof adapter.drawFixed === 'function') {
      for (const item of plan.fixed) adapter.drawFixed(item);
    }
    if (typeof adapter.endFrame === 'function') adapter.endFrame(plan);
    return plan;
  }
}

module.exports = {
  PLAYERS,
  PlayerAnchorResolver,
  TargetLockIndicatorRouter,
  PlayerFollowStateMachine,
  AnchoredWarningRenderer,
  dbRectToClip,
};
