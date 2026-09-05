import assert from 'node:assert/strict';
import envelopeApi from './wof_alpha_canonical_anchor_envelope.js';

const {normalizeEnvelope,toPlayerAnchorSamples,toEnemyAnchorArray,VERSION}=envelopeApi;
const nowMs=10_000;
const authorityBinding={
  authorityKey:'authority-alpha-v1',
  runtimeEpoch:'runtime-epoch-0001',
  rendererEpoch:'renderer-epoch-001',
  worldSha256:'a'.repeat(64)
};
const safe={readOnly:true,ramWrites:0,inputInjection:false};
const readySource={
  schema:'wof-render-object-anchor-v1',state:'READY',actor:'P1',generation:7,
  nativeWidth:384,nativeHeight:224,anchor:{x:192,y:80},
  authorityKey:authorityBinding.authorityKey,runtimeEpoch:authorityBinding.runtimeEpoch,
  rendererEpoch:authorityBinding.rendererEpoch,...safe
};
const suppressedSource={
  schema:'wof-render-object-anchor-v1',state:'SUPPRESSED',reason:'RENDERER_SOURCE_UNPROVEN',
  nativeWidth:384,nativeHeight:224,...safe
};

const valid=normalizeEnvelope({
  nowMs,authorityBinding,
  records:[
    {kind:'player',actor:'P1',generation:7,sampleAt:9_900,canonicalAnchor:readySource,
      legacyProjection:{x:1,y:2}},
    {kind:'enemy',actor:'enemy-slot-4',slot:4,generation:12,sampleAt:9_950,canonicalAnchor:suppressedSource}
  ]
});
assert.equal(valid.ok,true);
assert.equal(valid.schema,VERSION);
assert.equal(valid.records.length,2);
assert.deepEqual(valid.ready[0].renderAnchor,{x:192,y:80});
assert.equal(valid.suppressed[0].renderAnchor,null);
assert.equal(valid.suppressed[0].suppressionReason,'RENDERER_SOURCE_UNPROVEN');
assert.equal(valid.records[0].generation,7);
assert.equal(valid.records[1].generation,12);
assert.equal(valid.records[0].authorityKey,authorityBinding.authorityKey);
assert.equal(valid.records[0].runtimeEpoch,authorityBinding.runtimeEpoch);
assert.equal(valid.records[0].rendererEpoch,authorityBinding.rendererEpoch);
assert.equal(valid.records[0].renderAnchor.x,192,'legacy projection must not replace canonical x');
assert.equal(toPlayerAnchorSamples(valid).P1.canonicalAnchor.state,'READY');
assert.equal(toEnemyAnchorArray(valid)[0].canonicalAnchor.state,'SUPPRESSED');

const mixedEpoch=normalizeEnvelope({
  nowMs,authorityBinding,
  records:[{kind:'player',actor:'P1',generation:7,sampleAt:9_900,canonicalAnchor:{...readySource,rendererEpoch:'renderer-epoch-999'}}]
});
assert.equal(mixedEpoch.ok,false);
assert.equal(mixedEpoch.reason,'MIXED_AUTHORITY_BINDING');

const duplicate=normalizeEnvelope({
  nowMs,authorityBinding,
  records:[
    {kind:'player',actor:'P1',generation:7,sampleAt:9_900,canonicalAnchor:readySource},
    {kind:'player',actor:'P1',generation:7,sampleAt:9_900,canonicalAnchor:readySource}
  ]
});
assert.equal(duplicate.ok,false);
assert.equal(duplicate.reason,'DUPLICATE_ACTOR_GENERATION');

const unsafe=normalizeEnvelope({
  nowMs,authorityBinding,
  records:[{kind:'player',actor:'P1',generation:7,sampleAt:9_900,canonicalAnchor:{...readySource,ramWrites:1}}]
});
assert.equal(unsafe.ok,false);
assert.equal(unsafe.reason,'UNSAFE_SOURCE');

const suppressedFallback=normalizeEnvelope({
  nowMs,authorityBinding,
  records:[{kind:'enemy',actor:'enemy-slot-4',slot:4,generation:12,sampleAt:9_950,
    fallbackAnchor:{x:2,y:3},canonicalAnchor:suppressedSource}]
});
assert.equal(suppressedFallback.ok,false);
assert.equal(suppressedFallback.reason,'SUPPRESSED_FALLBACK_POSITION_FORBIDDEN');

console.log('canonical anchor envelope selfcheck PASS');
