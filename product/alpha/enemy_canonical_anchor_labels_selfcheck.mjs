import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const L=require('./wof_alpha_enemy_target_labels.js');

const NOW=10000;
const authority={authorityKey:'authority-key-0001',runtimeEpoch:'runtime-epoch-0001',rendererEpoch:'renderer-epoch-001'};
const db={width:800,height:488,contentRect:{x:16,y:20,width:768,height:448},sampleAt:NOW,confidence:1,mappingVersion:'800:488:16:20:768:448',fullscreen:false,epoch:authority.runtimeEpoch};
const marker=(slot,target7E,generation=7)=>({slot,sourceId:'enemy-slot-'+slot,actor:'enemy-slot-'+slot,generation,target7E,target:L.targetForField(target7E),sampleAt:NOW,confidence:1,enemyX:999,enemyY:999,enemyZ:999});
const ready=(slot,generation,x,y,extra={})=>({schema:L.CANONICAL_ANCHOR_SCHEMA,state:'READY',actor:'enemy-slot-'+slot,generation,nativeWidth:384,nativeHeight:224,anchor:{x,y},authorityKey:authority.authorityKey,runtimeEpoch:authority.runtimeEpoch,rendererEpoch:authority.rendererEpoch,readOnly:true,ramWrites:0,inputInjection:false,...extra});

const markers=[marker(0,0),marker(1,4),marker(2,8)];
const anchors={0:ready(0,7,192,112),1:ready(1,7,96,56),2:ready(2,7,288,168)};
const plan=L.buildCanonicalPlan({markers,canonicalAnchors:anchors,canonicalAuthority:authority,drawingBufferState:db,nowMs:NOW});
assert.deepEqual(plan.labels.map(x=>x.label),['1P','2P','3P']);
assert.deepEqual(plan.labels.map(x=>x.target),['P1','P2','P3']);
assert.deepEqual(plan.labels.map(x=>x.anchorDb),[{x:400,y:244},{x:208,y:132},{x:592,y:356}]);

const stale=L.buildCanonicalPlan({markers:[marker(0,0)],canonicalAnchors:{0:ready(0,7,192,112,{sampleAt:NOW-301})},canonicalAuthority:authority,drawingBufferState:db,nowMs:NOW});
assert.equal(stale.labels.length,0);assert.equal(stale.suppressed[0].reason,'STALE_CANONICAL_ANCHOR');
const suppressed=L.buildCanonicalPlan({markers:[marker(0,0)],canonicalAnchors:{0:{schema:L.CANONICAL_ANCHOR_SCHEMA,state:'SUPPRESSED',reason:'RENDERER_SOURCE_UNPROVEN',nativeWidth:384,nativeHeight:224,readOnly:true,ramWrites:0,inputInjection:false}},canonicalAuthority:authority,drawingBufferState:db,nowMs:NOW});
assert.equal(suppressed.labels.length,0);assert.equal(suppressed.suppressed[0].reason,'CANONICAL_ANCHOR_SUPPRESSED');
const mismatch=L.buildCanonicalPlan({markers:[marker(0,0,7)],canonicalAnchors:{0:ready(0,8,192,112)},canonicalAuthority:authority,drawingBufferState:db,nowMs:NOW});
assert.equal(mismatch.labels.length,0);assert.equal(mismatch.suppressed[0].reason,'CANONICAL_GENERATION_MISMATCH');
const unproven=L.buildCanonicalPlan({markers:[marker(0,0)],canonicalAnchors:{0:ready(0,7,192,112,{rendererSourceProven:false})},canonicalAuthority:authority,drawingBufferState:db,nowMs:NOW});
assert.equal(unproven.labels.length,0);assert.equal(unproven.suppressed[0].reason,'CANONICAL_ANCHOR_UNPROVEN');

const noFallbackArgs={markers:[marker(0,0)],canonicalAnchors:{0:ready(0,8,192,112)},canonicalAuthority:authority,drawingBufferState:db,nowMs:NOW};
Object.defineProperty(noFallbackArgs,'projection',{get(){throw new Error('legacy projection fallback accessed');}});
const noFallback=L.buildCanonicalPlan(noFallbackArgs);
assert.equal(noFallback.labels.length,0);
assert.doesNotMatch(String(L.buildCanonicalPlan),/projectMarkerNative|validateProjection|cameraX|enemyX|enemyY|enemyZ|yModel/);

console.log(JSON.stringify({schema:'wof-alpha-enemy-canonical-anchor-selfcheck-v1',status:'PASS',checks:['parse/load','0/4/8 => 1P/2P/3P drawing-buffer mapping','stale/SUPPRESSED/generation-mismatch/unproven suppress','no legacy projection fallback']},null,2));
