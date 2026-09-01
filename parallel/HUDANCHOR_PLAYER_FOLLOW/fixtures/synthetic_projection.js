'use strict';

// SYNTHETIC ONLY. None of these constants are claimed to match the real WOF Browser projection.
function makeSyntheticProjection(options = {}) {
  const sampleAtMs = options.sampleAtMs ?? 1000;
  const epoch = options.epoch ?? 'synthetic-epoch-1';
  const cameraX = options.cameraX ?? 0;
  const cameraY = options.cameraY ?? 0;

  return {
    source: 'synthetic-fixture-not-browser-proof',
    version: options.version ?? 'synthetic-player-follow-v1',
    epoch,
    sampleAtMs,
    nativeWidth: 384,
    nativeHeight: 224,
    confidence: 1,
    camera: { x: cameraX, y: cameraY },
    validationBounds: { minX: -64, maxX: 448, minY: -64, maxY: 288 },
    projectNative({ x, y, z, camera }) {
      // Arbitrary affine fixture chosen only to exercise movement/camera/depth/jump behavior.
      const bodyXNative = 100 + x - camera.x;
      const bodyYNative = 140 + (y - camera.y) * 0.5 - z;
      return {
        bodyXNative,
        bodyYNative,
        anchorXNative: bodyXNative,
        anchorYNative: bodyYNative - 24,
        confidence: 1,
      };
    },
  };
}

function makeDrawingBuffer(options = {}) {
  const width = options.width ?? 768;
  const height = options.height ?? 448;
  return {
    width,
    height,
    sampleAtMs: options.sampleAtMs ?? 1000,
    epoch: options.epoch ?? 'synthetic-epoch-1',
    confidence: 1,
    fullscreen: !!options.fullscreen,
    mappingVersion: options.mappingVersion ?? 'synthetic-map-1',
    contentRect: options.contentRect || { x: 0, y: 0, width, height },
  };
}

function makePlayer(x, y, z, options = {}) {
  return {
    present: options.present !== false,
    x,
    y,
    z,
    sampleAtMs: options.sampleAtMs ?? 1000,
    epoch: options.epoch ?? 'synthetic-epoch-1',
    lifecycleId: options.lifecycleId ?? 'life-1',
    confidence: 1,
  };
}

module.exports = { makeSyntheticProjection, makeDrawingBuffer, makePlayer };
