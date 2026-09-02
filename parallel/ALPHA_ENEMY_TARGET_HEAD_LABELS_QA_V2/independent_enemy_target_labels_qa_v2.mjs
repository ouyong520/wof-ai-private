import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const L=require('../../product/alpha/wof_alpha_enemy_target_labels.js');
const repoProfile=JSON.parse(fs.readFileSync(new URL('../../product/alpha/wof_alpha_enemy_head_projection.json',import.meta.url),'utf8'));
const NOW=42000;
const baseProfile={
  schema:L.PROJECTION_SCHEMA,verdict:L.PROJECTION_VERDICT,proofId:'independent-qa-v2-synthetic-proof',romSha256:L.SUPPORTED_ROM_SHA,
  nativeWidth:384,nativeHeight:224,cameraAddress:0xFF1000,cameraRead:'u16be',cameraSign:1,cameraScale:1,xBias:10,yModel:'Y-Z',
  enemyHeadOffsetsByType:{18:-20,20:-24}
};
const projection=(extra={})=>({...baseProfile,epoch:'runtime-a',sampleAt:NOW,confidence:1,cameraRaw:50,cameraX:50,...extra});
const marker=(raw=0,extra={})=>({slot:0,sourceId:'enemy-slot-0',type:18,target7E:raw,target:L.targetForField(raw),enemyX:100,enemyY:100,enemyZ:10,
  sampleAt:NOW,confidence:1,epoch:'runtime-a',projectionEpoch:'runtime-a',...extra});
const db=(extra={})=>({width:384,height:224,contentRect:{x:0,y:0,width:384,height:224},sampleAt:NOW,confidence:1,
  mappingVersion:'384:224:0:0:384:224',fullscreen:false,epoch:'runtime-a',projectionEpoch:'runtime-a',...extra});
const plan=(markers,p=projection(),d=db(),now=NOW)=>L.buildPlan({markers,projection:p,drawingBufferState:d,nowMs:now});
const results=[];
function test(name,fn){try{fn();results.push({name,ok:true});}catch(error){results.push({name,ok:false,error:String(error?.message||error)});}}
function expectSuppressed(x,reason){assert.equal(x.labels.length,0); if(reason!==undefined){assert.equal(x.suppressed[0]?.reason??x.reason,reason);}}

test('primitive numeric 0/4/8 map exactly to P1/P2/P3 and 1P/2P/3P',()=>{
  assert.equal(L.targetForField(0),'P1');assert.equal(L.labelForTarget('P1'),'1P');
  assert.equal(L.targetForField(4),'P2');assert.equal(L.labelForTarget('P2'),'2P');
  assert.equal(L.targetForField(8),'P3');assert.equal(L.labelForTarget('P3'),'3P');
  assert.deepEqual([0,4,8].map(v=>plan([marker(v)]).labels[0]?.label),['1P','2P','3P']);
});

test('numeric strings 0/4/8 fail closed',()=>{
  for(const [raw,target] of [['0','P1'],['4','P2'],['8','P3']]){
    assert.equal(L.targetForField(raw),null);
    const x=plan([marker(0,{target7E:raw,target})]);expectSuppressed(x,'INVALID_TARGET');
  }
});

test('boxed/object/boolean/array/null/undefined/NaN/Infinity/fractional/coercible/bigint/symbol/-0 fail closed',()=>{
  const coercible={valueOf(){return 0;},toString(){return '0';}};
  const bad=[new Number(0),new Number(4),new Number(8),{},coercible,true,false,[],[0],[4],[8],null,undefined,NaN,Infinity,-Infinity,0.5,4.1,8.9,0n,Symbol('0'),-0];
  for(const raw of bad){
    assert.equal(L.targetForField(raw),null,`raw ${String(raw)} must fail closed`);
    const x=plan([marker(0,{target7E:raw,target:'P1'})]);expectSuppressed(x,'INVALID_TARGET');
  }
});

test('unsupported numeric raw targets fail closed',()=>{
  for(const raw of [-8,-4,1,2,3,5,6,7,9,12,65535]){assert.equal(L.targetForField(raw),null);expectSuppressed(plan([marker(raw,{target:null})]),'INVALID_TARGET');}
});

test('raw/normalized target inconsistency fails closed',()=>{
  for(const [raw,target] of [[0,'P2'],[0,'P3'],[4,'P1'],[4,'P3'],[8,'P1'],[8,'P2'],[0,null],[4,undefined],[8,'1P']]){
    expectSuppressed(plan([marker(raw,{target})]),'INVALID_TARGET');
  }
});

test('same enemy retarget P1->P2->P3 updates immediately with no stale hold',()=>{
  const ids={slot:4,sourceId:'enemy-slot-4',type:18};
  const seq=[0,4,8].map(raw=>plan([marker(raw,ids)]));
  assert.deepEqual(seq.map(x=>x.labels.map(y=>y.label)),[['1P'],['2P'],['3P']]);
  assert.deepEqual(seq.map(x=>x.labels[0].sourceId),['enemy-slot-4','enemy-slot-4','enemy-slot-4']);
});

test('simultaneous enemies remain independent',()=>{
  const x=plan([
    marker(0,{slot:0,sourceId:'enemy-slot-0',type:18,enemyX:90}),
    marker(4,{slot:1,sourceId:'enemy-slot-1',type:20,enemyX:120}),
    marker(8,{slot:2,sourceId:'enemy-slot-2',type:18,enemyX:150})
  ]);
  assert.deepEqual(x.labels.map(v=>[v.slot,v.label]),[[0,'1P'],[1,'2P'],[2,'3P']]);
});

test('disappearance and same-slot replacement cannot inherit prior label',()=>{
  assert.equal(plan([marker(0,{slot:3,sourceId:'enemy-slot-3'})]).labels[0].label,'1P');
  assert.equal(plan([]).labels.length,0);
  expectSuppressed(plan([marker(6,{slot:3,sourceId:'enemy-slot-3',target:null})]),'INVALID_TARGET');
  assert.equal(plan([marker(4,{slot:3,sourceId:'enemy-slot-3'})]).labels[0].label,'2P');
});

test('marker and projection freshness boundary is 300ms inclusive and 301ms closed',()=>{
  assert.equal(plan([marker(0,{sampleAt:NOW-300})]).labels.length,1);
  expectSuppressed(plan([marker(0,{sampleAt:NOW-301})]),'STALE_MARKER');
  assert.equal(plan([marker(0)],projection({sampleAt:NOW-300})).labels.length,1);
  const stale=plan([marker(0)],projection({sampleAt:NOW-301}));assert.equal(stale.reason,'STALE_PROJECTION');assert.equal(stale.labels.length,0);
});

test('drawing-buffer stale and malformed mapping fail closed',()=>{
  const stale=plan([marker(0)],projection(),db({sampleAt:NOW-1001}));assert.equal(stale.reason,'STALE_DRAWING_BUFFER');assert.equal(stale.labels.length,0);
  for(const d of [db({width:0}),db({height:NaN}),db({contentRect:{x:-1,y:0,width:384,height:224}}),db({contentRect:{x:0,y:0,width:385,height:224}})]){
    const x=plan([marker(0)],projection(),d);assert.equal(x.labels.length,0);assert.equal(x.reason,'INVALID_DRAWING_BUFFER');
  }
});

test('marker/projection epoch mismatch fails closed',()=>{
  for(const m of [marker(0,{epoch:'old',projectionEpoch:'old'}),marker(0,{epoch:'runtime-a',projectionEpoch:'old'}),marker(0,{epoch:'',projectionEpoch:'runtime-a'})]){
    expectSuppressed(plan([m]),'EPOCH_MISMATCH');
  }
});

test('drawing-buffer internal epoch mismatch fails closed',()=>{
  const x=plan([marker(0)],projection(),db({epoch:'old',projectionEpoch:'runtime-a'}));assert.equal(x.labels.length,0);assert.equal(x.reason,'DRAWING_BUFFER_EPOCH_MISMATCH');
});

test('drawing-buffer epoch from a different runtime must not be accepted against current projection',()=>{
  const x=plan([marker(0)],projection({epoch:'runtime-a'}),db({epoch:'runtime-old',projectionEpoch:'runtime-old'}));
  assert.equal(x.labels.length,0,'stale drawing-buffer runtime epoch must not render against current projection');
});

test('invalid confidence and non-finite XYZ/projection/camera fail closed',()=>{
  for(const bad of [NaN,Infinity,-Infinity,-0.1,1.1])expectSuppressed(plan([marker(0,{confidence:bad})]));
  for(const bad of [NaN,Infinity,-Infinity])for(const key of ['enemyX','enemyY','enemyZ'])expectSuppressed(plan([marker(0,{[key]:bad})]),'INVALID_ENEMY_XYZ');
  for(const bad of [NaN,Infinity,-Infinity]){const x=plan([marker(0)],projection({confidence:bad}));assert.equal(x.labels.length,0);assert.equal(x.reason,'INVALID_PROJECTION_CONFIDENCE');}
  for(const bad of [NaN,Infinity,-Infinity]){const x=plan([marker(0)],projection({cameraX:bad}));assert.equal(x.labels.length,0);assert.equal(x.reason,'INVALID_CAMERA_SAMPLE');}
  const mismatch=plan([marker(0)],projection({cameraRaw:50,cameraX:51}));assert.equal(mismatch.labels.length,0);assert.equal(mismatch.reason,'CAMERA_SAMPLE_MISMATCH');
});

test('unsupported enemy type and invalid slot suppress labels',()=>{
  expectSuppressed(plan([marker(0,{type:19})]),'UNSUPPORTED_ENEMY_TYPE');
  for(const slot of [-1,20,1.5,'0',null,NaN])expectSuppressed(plan([marker(0,{slot})]),'INVALID_MARKER_SLOT');
});

test('valid near-edge anchor clamps only compact label rect; invalid anchor is suppressed before clamp',()=>{
  const p=projection({cameraRaw:50,cameraX:50,xBias:10,enemyHeadOffsetsByType:{18:-30},yModel:'Y'});
  const near=plan([marker(0,{enemyX:41,enemyY:31,enemyZ:0})],p);assert.equal(near.labels.length,1);assert.deepEqual(near.labels[0].anchorDb,{x:1,y:1});assert.equal(near.labels[0].drawRectDb.x,0);assert.equal(near.labels[0].drawRectDb.y,0);
  expectSuppressed(plan([marker(0,{enemyX:39,enemyY:31,enemyZ:0})],p),'PROJECTION_OUT_OF_BOUNDS');
  expectSuppressed(plan([marker(0,{enemyX:41,enemyY:29,enemyZ:0})],p),'PROJECTION_OUT_OF_BOUNDS');
});

test('resize/fullscreen remap generates fresh mapping key and coordinates',()=>{
  const a=plan([marker(0)],projection(),db());
  const b=plan([marker(0)],projection(),db({width:768,height:448,contentRect:{x:0,y:0,width:768,height:448},mappingVersion:'768:448:0:0:768:448'}));
  const c=plan([marker(0)],projection(),db({fullscreen:true,mappingVersion:'384:224:fs'}));
  assert.notEqual(a.mappingKey,b.mappingKey);assert.notEqual(a.mappingKey,c.mappingKey);
  assert.equal(b.labels[0].anchorDb.x,a.labels[0].anchorDb.x*2);assert.equal(b.labels[0].anchorDb.y,a.labels[0].anchorDb.y*2);
});

test('repository UNPROVEN profile keeps live labels silent',()=>{
  assert.equal(repoProfile.verdict,'UNPROVEN');assert.equal(repoProfile.status,'FAIL_CLOSED_UNTIL_IMPLEMENTATION_READY_PROOF');
  assert.equal(L.validateProofProfile(repoProfile).ok,false);
  const x=L.buildPlan({markers:[marker(0)],projection:repoProfile,drawingBufferState:db(),nowMs:NOW});assert.equal(x.labels.length,0);assert.equal(x.reason,'PROJECTION_UNPROVEN');
});

test('malformed proof/profile facts fail closed',()=>{
  const variants=[
    projection({proofId:''}),projection({romSha256:'bad'}),projection({nativeWidth:383}),projection({cameraAddress:0xFEFFFE}),projection({cameraAddress:0xFF0001}),
    projection({cameraRead:'u16le'}),projection({cameraSign:0}),projection({cameraScale:0}),projection({xBias:Infinity}),projection({yModel:'bogus'}),
    projection({enemyHeadOffsetsByType:{}}),projection({enemyHeadOffsetsByType:{18:Infinity}})
  ];
  for(const p of variants){const x=plan([marker(0)],p);assert.equal(x.labels.length,0);assert.notEqual(x.reason,null);}
});

const failed=results.filter(x=>!x.ok);
const out={schema:'wof-alpha-enemy-target-head-labels-independent-repository-qa-v2',evidenceClass:'SYNTHETIC_REPOSITORY_QA_ONLY_NOT_BROWSER_WOF_PROJECTION_PROOF',status:failed.length?'FAIL':'PASS',testCount:results.length,passCount:results.length-failed.length,failCount:failed.length,results};
console.log(JSON.stringify(out,null,2));
fs.writeFileSync(new URL('./independent_qa_result.json',import.meta.url),JSON.stringify(out,null,2)+'\n');
if(failed.length)process.exit(1);
