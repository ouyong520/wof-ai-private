import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createRequire} from 'node:module';

const require=createRequire(import.meta.url);
const L=require('../../product/alpha/wof_alpha_enemy_target_labels.js');
const repoProfile=JSON.parse(fs.readFileSync(new URL('../../product/alpha/wof_alpha_enemy_head_projection.json',import.meta.url),'utf8'));

const NOW=50000;
const VALID_PROFILE={
  schema:L.PROJECTION_SCHEMA,
  verdict:L.PROJECTION_VERDICT,
  proofId:'synthetic-independent-qa-only-not-browser-proof',
  romSha256:L.SUPPORTED_ROM_SHA,
  nativeWidth:384,
  nativeHeight:224,
  cameraAddress:0xFF1000,
  cameraRead:'u16be',
  cameraSign:1,
  cameraScale:1,
  xBias:10,
  yModel:'Y-Z',
  enemyHeadOffsetsByType:{18:-20,20:-24}
};
const projection=(extra={})=>({...VALID_PROFILE,epoch:'epoch-new',sampleAt:NOW,confidence:1,cameraRaw:50,cameraX:50,...extra});
const marker=(slot,target7E,extra={})=>({
  slot,
  sourceId:`enemy-slot-${slot}`,
  type:18,
  target7E,
  target:L.targetForField(target7E),
  enemyX:100+slot*20,
  enemyY:100,
  enemyZ:10,
  sampleAt:NOW,
  confidence:1,
  epoch:'epoch-new',
  projectionEpoch:'epoch-new',
  ...extra
});
const buffer=(extra={})=>({
  width:384,
  height:224,
  contentRect:{x:0,y:0,width:384,height:224},
  sampleAt:NOW,
  confidence:1,
  mappingVersion:'384x224-windowed',
  fullscreen:false,
  epoch:'epoch-new',
  projectionEpoch:'epoch-new',
  ...extra
});
const plan=(markers,p=projection(),d=buffer(),now=NOW)=>L.buildPlan({markers,projection:p,drawingBufferState:d,nowMs:now});

const results=[];
function check(name,fn){
  try{fn();results.push({name,status:'PASS'});}
  catch(error){results.push({name,status:'FAIL',error:String(error?.stack||error)});}
}

check('authoritative raw target map is exactly 0/4/8 -> 1P/2P/3P',()=>{
  assert.deepEqual([0,4,8].map(v=>[v,L.targetForField(v),L.labelForTarget(L.targetForField(v))]),[
    [0,'P1','1P'],[4,'P2','2P'],[8,'P3','3P']
  ]);
  for(const v of [-1,1,2,3,5,6,7,9,65535,null,undefined])assert.equal(L.targetForField(v),null);
});

check('malformed numeric-string raw targets must fail closed',()=>{
  for(const raw of ['0','4','8']){
    const m=marker(0,raw,{target:L.targetForField(raw)});
    const x=plan([m]);
    assert.equal(x.labels.length,0,`string ${raw} must not render a label; got ${x.labels.map(v=>v.label).join(',')}`);
    assert.equal(L.targetForField(raw),null,`string ${raw} must not normalize to a player`);
  }
});

check('unsupported or target-field/normalized-target disagreement suppresses label',()=>{
  assert.equal(plan([marker(0,6,{target:null})]).labels.length,0);
  const mismatch=plan([marker(0,0,{target:'P2'})]);
  assert.equal(mismatch.labels.length,0);
  assert.equal(mismatch.suppressed[0].reason,'INVALID_TARGET');
});

check('same enemy retarget P1 -> P2 -> P3 is stateless with zero old-label carryover',()=>{
  const frames=[0,4,8].map(v=>plan([marker(0,v)]));
  assert.deepEqual(frames.map(f=>f.labels.map(x=>x.label)),[['1P'],['2P'],['3P']]);
  assert.ok(frames.every(f=>f.labels.length===1));
});

check('simultaneous enemies keep independent targets and slots',()=>{
  const x=plan([marker(0,0),marker(1,4),marker(2,8)]);
  assert.deepEqual(x.labels.map(v=>[v.slot,v.target,v.label]),[[0,'P1','1P'],[1,'P2','2P'],[2,'P3','3P']]);
});

check('disappearance and same-slot replacement cannot inherit previous label',()=>{
  assert.equal(plan([marker(5,0)]).labels[0].label,'1P');
  assert.equal(plan([]).labels.length,0);
  assert.equal(plan([marker(5,6,{target:null})]).labels.length,0);
  assert.equal(plan([marker(5,8)]).labels[0].label,'3P');
});

check('marker freshness boundary is inclusive at 300 ms and suppresses at 301 ms',()=>{
  const atBoundary=plan([marker(0,0,{sampleAt:NOW-300})]);
  const overBoundary=plan([marker(0,0,{sampleAt:NOW-301})]);
  assert.equal(L.DEFAULT_MARKER_MAX_AGE_MS,300);
  assert.equal(atBoundary.labels.length,1);
  assert.equal(overBoundary.labels.length,0);
  assert.equal(overBoundary.suppressed[0].reason,'STALE_MARKER');
});

check('projection freshness boundary is inclusive at 300 ms and suppresses at 301 ms',()=>{
  assert.equal(L.DEFAULT_PROJECTION_MAX_AGE_MS,300);
  assert.equal(plan([marker(0,0)],projection({sampleAt:NOW-300})).labels.length,1);
  const stale=plan([marker(0,0)],projection({sampleAt:NOW-301}));
  assert.equal(stale.labels.length,0);
  assert.equal(stale.reason,'STALE_PROJECTION');
});

check('runtime/projection/drawing-buffer epoch mismatches fail closed',()=>{
  const markerEpoch=plan([marker(0,0,{epoch:'epoch-old',projectionEpoch:'epoch-old'})]);
  assert.equal(markerEpoch.labels.length,0);
  assert.equal(markerEpoch.suppressed[0].reason,'EPOCH_MISMATCH');
  const dbEpoch=plan([marker(0,0)],projection(),buffer({epoch:'epoch-new',projectionEpoch:'epoch-old'}));
  assert.equal(dbEpoch.labels.length,0);
  assert.equal(dbEpoch.reason,'DRAWING_BUFFER_EPOCH_MISMATCH');
});

check('invalid confidence and non-finite marker/projection values suppress',()=>{
  for(const bad of [NaN,Infinity,-Infinity,null,undefined,'1',{},[]]){
    assert.equal(plan([marker(0,0,{confidence:bad})]).labels.length,0);
    assert.equal(plan([marker(0,0)],projection({confidence:bad})).labels.length,0);
  }
  for(const bad of [NaN,Infinity,-Infinity]){
    for(const field of ['enemyX','enemyY','enemyZ'])assert.equal(plan([marker(0,0,{[field]:bad})]).labels.length,0);
  }
  const cameraMismatch=plan([marker(0,0)],projection({cameraRaw:50,cameraX:51}));
  assert.equal(cameraMismatch.labels.length,0);
  assert.equal(cameraMismatch.reason,'CAMERA_SAMPLE_MISMATCH');
});

check('unsupported enemy type and invalid slot fail closed',()=>{
  const unsupported=plan([marker(0,0,{type:46})]);
  assert.equal(unsupported.labels.length,0);
  assert.equal(unsupported.suppressed[0].reason,'UNSUPPORTED_ENEMY_TYPE');
  for(const slot of [-1,20,1.5])assert.equal(plan([marker(slot,0)]).labels.length,0);
});

check('valid near-edge anchor clamps only label rectangle; invalid anchor is suppressed',()=>{
  const p=projection({cameraRaw:50,cameraX:50,xBias:10,yModel:'Y',enemyHeadOffsetsByType:{18:-30}});
  const near=plan([marker(0,0,{enemyX:41,enemyY:31,enemyZ:0})],p);
  assert.equal(near.labels.length,1);
  assert.deepEqual(near.labels[0].anchorDb,{x:1,y:1});
  assert.equal(near.labels[0].drawRectDb.x,0);
  assert.equal(near.labels[0].drawRectDb.y,0);
  const outside=plan([marker(0,0,{enemyX:39,enemyY:31,enemyZ:0})],p);
  assert.equal(outside.labels.length,0);
  assert.equal(outside.suppressed[0].reason,'PROJECTION_OUT_OF_BOUNDS');
});

check('malformed drawing-buffer geometry, confidence, and staleness fail closed',()=>{
  for(const d of [
    buffer({width:0}),
    buffer({contentRect:{x:-1,y:0,width:384,height:224}}),
    buffer({contentRect:{x:0,y:0,width:385,height:224}}),
    buffer({confidence:NaN}),
    buffer({sampleAt:NOW-1001})
  ])assert.equal(plan([marker(0,0)],projection(),d).labels.length,0);
});

check('resize/fullscreen remapping is recomputed from current drawing buffer state',()=>{
  const a=plan([marker(0,0)],projection(),buffer());
  const doubled=buffer({width:768,height:448,contentRect:{x:0,y:0,width:768,height:448},mappingVersion:'768x448-windowed'});
  const b=plan([marker(0,0)],projection(),doubled);
  const c=plan([marker(0,0)],projection(),buffer({mappingVersion:'384x224-fullscreen',fullscreen:true}));
  assert.notEqual(a.mappingKey,b.mappingKey);
  assert.notEqual(a.mappingKey,c.mappingKey);
  assert.equal(b.labels[0].anchorDb.x,a.labels[0].anchorDb.x*2);
  assert.equal(b.labels[0].anchorDb.y,a.labels[0].anchorDb.y*2);
});

check('repository UNPROVEN projection profile is rejected and keeps labels silent',()=>{
  assert.equal(repoProfile.verdict,'UNPROVEN');
  assert.equal(repoProfile.status,'FAIL_CLOSED_UNTIL_IMPLEMENTATION_READY_PROOF');
  assert.equal(L.validateProofProfile(repoProfile).ok,false);
  const x=plan([marker(0,0)],repoProfile);
  assert.equal(x.labels.length,0);
  assert.equal(x.reason,'PROJECTION_UNPROVEN');
});

check('invalid proof/profile facts never become a confident projection',()=>{
  const variants=[
    {proofId:null},
    {romSha256:'0'.repeat(64)},
    {nativeWidth:383},
    {cameraAddress:0xFEFFFE},
    {cameraAddress:0xFF1001},
    {cameraRead:'u16le'},
    {cameraSign:0},
    {cameraScale:0},
    {xBias:NaN},
    {yModel:'GUESS'},
    {enemyHeadOffsetsByType:{}},
    {enemyHeadOffsetsByType:{18:NaN}}
  ];
  for(const patch of variants)assert.equal(L.validateProofProfile({...VALID_PROFILE,...patch}).ok,false);
});

const failed=results.filter(r=>r.status!=='PASS');
const report={
  schema:'wof-alpha-enemy-target-head-labels-independent-repository-qa-v1',
  status:failed.length?'FAIL':'PASS',
  testCount:results.length,
  passCount:results.length-failed.length,
  failCount:failed.length,
  evidenceClass:'SYNTHETIC_REPOSITORY_QA_ONLY_NOT_BROWSER_WOF_PROJECTION_PROOF',
  productionHelperBlob:'3f6f4410376756e6935a4236e40e76574b289169',
  projectionProfileBlob:'8de57739818503a0e14702d2fa0bb4eba58228d2',
  results
};
console.log(JSON.stringify(report,null,2));
if(failed.length)process.exit(1);
