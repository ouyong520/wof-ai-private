import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const L=require('../../product/alpha/wof_alpha_enemy_target_labels.js');
const profileJson=JSON.parse(fs.readFileSync(new URL('../../product/alpha/wof_alpha_enemy_head_projection.json',import.meta.url),'utf8'));

const NOW=10000;
const profile={schema:L.PROJECTION_SCHEMA,verdict:L.PROJECTION_VERDICT,proofId:'synthetic-independent-qa-v3',romSha256:L.SUPPORTED_ROM_SHA,
  nativeWidth:384,nativeHeight:224,cameraAddress:0xFF1000,cameraRead:'u16be',cameraSign:1,cameraScale:1,xBias:10,yModel:'Y-Z',enemyHeadOffsetsByType:{18:-20,20:-24}};
const projection=(extra={})=>({...profile,epoch:'runtime-a',sampleAt:NOW,confidence:1,cameraRaw:50,cameraX:50,...extra});
const marker=(target7E=0,extra={})=>({slot:0,sourceId:'enemy-slot-0',type:18,target7E,target:L.targetForField(target7E),enemyX:100,enemyY:100,enemyZ:10,
  sampleAt:NOW,confidence:1,epoch:'runtime-a',projectionEpoch:'runtime-a',...extra});
const db=(extra={})=>({width:384,height:224,contentRect:{x:0,y:0,width:384,height:224},sampleAt:NOW,confidence:1,mappingVersion:'384:224:0:0:384:224',fullscreen:false,
  epoch:'runtime-a',projectionEpoch:'runtime-a',...extra});
const plan=(markers,p=projection(),d=db(),now=NOW)=>L.buildPlan({markers,projection:p,drawingBufferState:d,nowMs:now});
const results=[];
function test(name,fn){try{fn();results.push({name,ok:true});}catch(error){results.push({name,ok:false,error:String(error?.stack||error)});}}
function noLabel(x,reason){assert.equal(x.labels.length,0);if(reason!==undefined)assert.equal(x.reason??x.suppressed?.[0]?.reason,reason);}

test('01 primitive numeric raw targets 0/4/8 map exactly to 1P/2P/3P',()=>{
  assert.deepEqual([0,4,8].map(v=>L.targetForField(v)),['P1','P2','P3']);
  assert.deepEqual([0,4,8].map(v=>plan([marker(v)]).labels[0]?.label),['1P','2P','3P']);
});

test('02 numeric strings boxed/coercible targets arrays booleans nonfinite/fractional fail closed',()=>{
  const coercible={valueOf(){return 0;},toString(){return'0';}};
  const bad=['0','4','8',new Number(0),new Number(4),new Number(8),coercible,[],[0],[4],[8],true,false,null,undefined,NaN,Infinity,-Infinity,0.5,4.5,8.1,-0,1n,Symbol('0')];
  for(const raw of bad){
    assert.equal(L.targetForField(raw),null);
    const x=plan([marker(0,{target7E:raw,target:'P1'})]);
    assert.equal(x.labels.length,0);assert.equal(x.suppressed[0].reason,'INVALID_TARGET');
  }
});

test('03 raw/normalized target mismatch fails closed',()=>{
  for(const [raw,wrong] of [[0,'P2'],[4,'P3'],[8,'P1']]){
    const x=plan([marker(raw,{target:wrong})]);assert.equal(x.labels.length,0);assert.equal(x.suppressed[0].reason,'INVALID_TARGET');
  }
});

test('04 marker projection and drawing-buffer all runtime-a remains valid',()=>{
  const x=plan([marker(0)],projection({epoch:'runtime-a'}),db({epoch:'runtime-a',projectionEpoch:'runtime-a'}));
  assert.equal(x.labels.length,1);assert.equal(x.labels[0].label,'1P');assert.equal(x.labels[0].epoch,'runtime-a');
});

test('05 marker/projection runtime-a plus drawing-buffer runtime-old/runtime-old fails closed',()=>{
  noLabel(plan([marker(0)],projection({epoch:'runtime-a'}),db({epoch:'runtime-old',projectionEpoch:'runtime-old'})),'DRAWING_BUFFER_EPOCH_MISMATCH');
});

test('06 drawing-buffer epoch/projectionEpoch internal disagreement fails closed',()=>{
  noLabel(plan([marker(0)],projection(),db({epoch:'runtime-a',projectionEpoch:'runtime-old'})),'DRAWING_BUFFER_EPOCH_MISMATCH');
  noLabel(plan([marker(0)],projection(),db({epoch:'runtime-old',projectionEpoch:'runtime-a'})),'DRAWING_BUFFER_EPOCH_MISMATCH');
});

test('07 marker/projection/drawing-buffer three-way mixed epochs fail closed',()=>{
  const cases=[
    [marker(0,{epoch:'runtime-old',projectionEpoch:'runtime-a'}),projection(),db()],
    [marker(0,{epoch:'runtime-a',projectionEpoch:'runtime-old'}),projection(),db()],
    [marker(0,{epoch:'runtime-b',projectionEpoch:'runtime-b'}),projection(),db()],
    [marker(0),projection({epoch:'runtime-b'}),db({epoch:'runtime-a',projectionEpoch:'runtime-a'})],
    [marker(0,{epoch:'runtime-c',projectionEpoch:'runtime-c'}),projection({epoch:'runtime-b'}),db({epoch:'runtime-a',projectionEpoch:'runtime-a'})]
  ];
  for(const [m,p,d] of cases)assert.equal(plan([m],p,d).labels.length,0);
});

test('08 projection epoch missing malformed non-string or coercible fails closed',()=>{
  const coercible={valueOf(){return'runtime-a';},toString(){return'runtime-a';}};
  for(const bad of [undefined,null,'',new String('runtime-a'),['runtime-a'],coercible,0,true])
    noLabel(plan([marker(0)],projection({epoch:bad}),db()),'PROJECTION_EPOCH_MISSING');
});

test('09 drawing-buffer epoch/projectionEpoch missing malformed non-string or coercible fails closed',()=>{
  const coercible={valueOf(){return'runtime-a';},toString(){return'runtime-a';}};
  for(const bad of [undefined,null,'',new String('runtime-a'),['runtime-a'],coercible,0,true]){
    noLabel(plan([marker(0)],projection(),db({epoch:bad,projectionEpoch:'runtime-a'})),'DRAWING_BUFFER_EPOCH_MISSING');
    noLabel(plan([marker(0)],projection(),db({epoch:'runtime-a',projectionEpoch:bad})),'DRAWING_BUFFER_EPOCH_MISSING');
  }
});

test('10 marker epoch/projectionEpoch missing malformed coercible or mismatched fails closed',()=>{
  const coercible={valueOf(){return'runtime-a';},toString(){return'runtime-a';}};
  for(const bad of [undefined,null,'',new String('runtime-a'),['runtime-a'],coercible,0,true,'runtime-old']){
    const a=plan([marker(0,{epoch:bad})]);assert.equal(a.labels.length,0);assert.equal(a.suppressed[0].reason,'EPOCH_MISMATCH');
    const b=plan([marker(0,{projectionEpoch:bad})]);assert.equal(b.labels.length,0);assert.equal(b.suppressed[0].reason,'EPOCH_MISMATCH');
  }
});

test('11 P1 -> P2 -> P3 retarget is immediate with no stale hold',()=>{
  assert.deepEqual([0,4,8,0].map(v=>plan([marker(v)]).labels.map(x=>x.label)),[['1P'],['2P'],['3P'],['1P']]);
});

test('12 simultaneous enemies remain independent',()=>{
  const x=plan([marker(0,{slot:0}),marker(4,{slot:1}),marker(8,{slot:2})]);
  assert.deepEqual(x.labels.map(v=>[v.slot,v.label]),[[0,'1P'],[1,'2P'],[2,'3P']]);
});

test('13 disappearance and same-slot replacement cannot inherit stale label',()=>{
  assert.equal(plan([marker(0)]).labels[0].label,'1P');assert.equal(plan([]).labels.length,0);
  assert.equal(plan([marker(6,{target:null})]).labels.length,0);assert.equal(plan([marker(4,{slot:0})]).labels[0].label,'2P');
});

test('14 marker projection and drawing-buffer stale boundaries fail closed',()=>{
  assert.equal(plan([marker(0,{sampleAt:NOW-300})]).labels.length,1);assert.equal(plan([marker(0,{sampleAt:NOW-301})]).labels.length,0);
  assert.equal(plan([marker(0)],projection({sampleAt:NOW-300})).labels.length,1);noLabel(plan([marker(0)],projection({sampleAt:NOW-301})),'STALE_PROJECTION');
  assert.equal(plan([marker(0)],projection(),db({sampleAt:NOW-1000})).labels.length,1);noLabel(plan([marker(0)],projection(),db({sampleAt:NOW-1001})),'STALE_DRAWING_BUFFER');
});

test('15 invalid confidence nonfinite XYZ/camera unsupported type target or slot fail closed',()=>{
  for(const bad of [NaN,Infinity,-Infinity,-0.01,1.01])assert.equal(plan([marker(0,{confidence:bad})]).labels.length,0);
  for(const bad of [NaN,Infinity,-Infinity]){assert.equal(plan([marker(0,{enemyX:bad})]).labels.length,0);noLabel(plan([marker(0)],projection({cameraRaw:bad,cameraX:bad})),'INVALID_CAMERA_SAMPLE');}
  assert.equal(plan([marker(0,{type:46})]).labels.length,0);assert.equal(plan([marker(6,{target:null})]).labels.length,0);
  assert.equal(plan([marker(0,{slot:-1})]).labels.length,0);assert.equal(plan([marker(0,{slot:20})]).labels.length,0);
});

test('16 valid edge anchor clamps compact label rectangle; invalid anchor is suppressed before clamp',()=>{
  const p=projection({cameraRaw:50,cameraX:50,xBias:10,enemyHeadOffsetsByType:{18:-30},yModel:'Y'});
  const near=plan([marker(0,{enemyX:41,enemyY:31,enemyZ:0})],p);assert.equal(near.labels.length,1);
  assert.deepEqual(near.labels[0].anchorDb,{x:1,y:1});assert.deepEqual(near.labels[0].drawRectDb,{x:0,y:0,width:30,height:18});
  const outside=plan([marker(0,{enemyX:39,enemyY:31,enemyZ:0})],p);assert.equal(outside.labels.length,0);assert.equal(outside.suppressed[0].reason,'PROJECTION_OUT_OF_BOUNDS');
});

test('17 resize/fullscreen mapping changes and stale old-epoch remap cannot be reused',()=>{
  const a=plan([marker(0)],projection(),db());
  const b=plan([marker(0)],projection(),db({width:768,height:448,contentRect:{x:0,y:0,width:768,height:448},mappingVersion:'768:448'}));
  const c=plan([marker(0)],projection(),db({fullscreen:true,mappingVersion:'384:224:fs'}));
  assert.notEqual(a.mappingKey,b.mappingKey);assert.notEqual(a.mappingKey,c.mappingKey);
  assert.deepEqual(b.labels[0].anchorDb,{x:a.labels[0].anchorDb.x*2,y:a.labels[0].anchorDb.y*2});
  noLabel(plan([marker(0)],projection(),db({width:768,height:448,contentRect:{x:0,y:0,width:768,height:448},mappingVersion:'old',epoch:'runtime-old',projectionEpoch:'runtime-old'})),'DRAWING_BUFFER_EPOCH_MISMATCH');
});

test('18 invalid drawing-buffer geometry/content bounds suppress before clamp',()=>{
  for(const d of [db({width:0}),db({height:0}),db({contentRect:{x:-1,y:0,width:384,height:224}}),db({contentRect:{x:0,y:0,width:385,height:224}}),db({contentRect:{x:0,y:0,width:384,height:225}}),db({contentRect:{x:0,y:0,width:NaN,height:224}})])
    noLabel(plan([marker(0)],projection(),d),'INVALID_DRAWING_BUFFER');
});

test('19 repository projection profile remains UNPROVEN/fail-closed and malformed proof facts remain suppressed',()=>{
  assert.equal(profileJson.verdict,'UNPROVEN');assert.equal(profileJson.status,'FAIL_CLOSED_UNTIL_IMPLEMENTATION_READY_PROOF');assert.equal(L.validateProofProfile(profileJson).ok,false);
  noLabel(L.buildPlan({markers:[marker(0)],projection:profileJson,drawingBufferState:db(),nowMs:NOW}),'PROJECTION_UNPROVEN');
  for(const p of [projection({proofId:''}),projection({romSha256:'bad'}),projection({nativeWidth:383}),projection({cameraAddress:0xFF1001}),projection({cameraRead:'u16le'}),projection({cameraSign:0}),projection({cameraScale:0}),projection({xBias:NaN}),projection({yModel:'bad'}),projection({enemyHeadOffsetsByType:{}})])
    assert.equal(plan([marker(0)],p,db()).labels.length,0);
});

test('20 malformed marker collection and tiny valid drawing buffer stay bounded/no-crash',()=>{
  const malformed=L.buildPlan({markers:{not:'array'},projection:projection(),drawingBufferState:db(),nowMs:NOW});assert.equal(malformed.labels.length,0);assert.equal(malformed.suppressed.length,0);
  const tiny=plan([marker(0)],projection(),db({width:20,height:10,contentRect:{x:0,y:0,width:20,height:10},mappingVersion:'20:10'}));assert.equal(tiny.labels.length,1);assert.deepEqual(tiny.labels[0].drawRectDb,{x:0,y:0,width:20,height:10});
});

const failed=results.filter(x=>!x.ok);
const out={schema:'wof-alpha-enemy-target-head-labels-independent-repository-qa-v3',status:failed.length?'FAIL':'PASS',testCount:results.length,passCount:results.length-failed.length,failCount:failed.length,
  evidenceClass:'SYNTHETIC_REPOSITORY_QA_ONLY_NOT_BROWSER_WOF_PROJECTION_PROOF',results};
console.log(JSON.stringify(out,null,2));
if(failed.length)process.exit(1);
