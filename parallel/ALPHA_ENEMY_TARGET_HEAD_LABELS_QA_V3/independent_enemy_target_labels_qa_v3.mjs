import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import fs from 'node:fs';
const require=createRequire(import.meta.url);
const L=require('../../product/alpha/wof_alpha_enemy_target_labels.js');
const profileJson=JSON.parse(fs.readFileSync(new URL('../../product/alpha/wof_alpha_enemy_head_projection.json',import.meta.url),'utf8'));
const NOW=10000;
const profile={schema:L.PROJECTION_SCHEMA,verdict:L.PROJECTION_VERDICT,proofId:'synthetic-independent-qa-v3',romSha256:L.SUPPORTED_ROM_SHA,nativeWidth:384,nativeHeight:224,cameraAddress:0xFF1000,cameraRead:'u16be',cameraSign:1,cameraScale:1,xBias:10,yModel:'Y-Z',enemyHeadOffsetsByType:{18:-20,20:-24}};
const projection=(extra={})=>({...profile,epoch:'runtime-a',sampleAt:NOW,confidence:1,cameraRaw:50,cameraX:50,...extra});
const marker=(target7E=0,extra={})=>({slot:0,sourceId:'enemy-slot-0',type:18,target7E,target:L.targetForField(target7E),enemyX:100,enemyY:100,enemyZ:10,sampleAt:NOW,confidence:1,epoch:'runtime-a',projectionEpoch:'runtime-a',...extra});
const db=(extra={})=>({width:384,height:224,contentRect:{x:0,y:0,width:384,height:224},sampleAt:NOW,confidence:1,mappingVersion:'384:224:0:0:384:224',fullscreen:false,epoch:'runtime-a',projectionEpoch:'runtime-a',...extra});
const plan=(markers,p=projection(),d=db(),now=NOW)=>L.buildPlan({markers,projection:p,drawingBufferState:d,nowMs:now});
const results=[];
function test(name,fn){try{fn();results.push({name,ok:true});}catch(error){results.push({name,ok:false,error:String(error?.stack||error)});}}
function noLabel(x,reason){assert.equal(x.labels.length,0);if(reason!==undefined)assert.equal(x.reason??x.suppressed?.[0]?.reason,reason);}

test('01 primitive numeric 0/4/8 map exactly to 1P/2P/3P',()=>{
  assert.deepEqual([0,4,8].map(v=>L.targetForField(v)),['P1','P2','P3']);
  assert.deepEqual([0,4,8].map(v=>plan([marker(v)]).labels[0]?.label),['1P','2P','3P']);
});

test('02 strict malformed/coercible raw target values fail closed',()=>{
  const coercible={valueOf(){return 0;},toString(){return '0';}};
  const boxed=[new Number(0),new Number(4),new Number(8)];
  const bad=['0','4','8',...boxed,coercible,[],[0],[4],[8],true,false,null,undefined,NaN,Infinity,-Infinity,0.5,4.5,8.1,-0,1n,Symbol('0')];
  for(const raw of bad){
    assert.equal(L.targetForField(raw),null,String(raw));
    const x=plan([marker(0,{target7E:raw,target:'P1'})]);
    assert.equal(x.labels.length,0);
    assert.equal(x.suppressed[0].reason,'INVALID_TARGET');
  }
});

test('03 raw/normalized target mismatch fails closed',()=>{
  for(const [raw,wrong] of [[0,'P2'],[4,'P3'],[8,'P1']]){
    const x=plan([marker(raw,{target:wrong})]);assert.equal(x.labels.length,0);assert.equal(x.suppressed[0].reason,'INVALID_TARGET');
  }
});

test('04 all marker/projection/drawing-buffer epochs runtime-a is valid',()=>{
  const x=plan([marker(0)],projection({epoch:'runtime-a'}),db({epoch:'runtime-a',projectionEpoch:'runtime-a'}));
  assert.equal(x.labels.length,1);assert.equal(x.labels[0].label,'1P');assert.equal(x.labels[0].epoch,'runtime-a');
});

test('05 current marker/projection runtime-a plus stale drawing-buffer runtime-old/runtime-old is suppressed',()=>{
  const x=plan([marker(0)],projection({epoch:'runtime-a'}),db({epoch:'runtime-old',projectionEpoch:'runtime-old'}));
  noLabel(x,'DRAWING_BUFFER_EPOCH_MISMATCH');
});

test('06 drawing-buffer epoch/projectionEpoch split is suppressed',()=>{
  for(const d of [db({epoch:'runtime-a',projectionEpoch:'runtime-old'}),db({epoch:'runtime-old',projectionEpoch:'runtime-a'})]){
    noLabel(plan([marker(0)],projection({epoch:'runtime-a'}),d),'DRAWING_BUFFER_EPOCH_MISMATCH');
  }
});

test('07 marker/projection/drawing-buffer three-way mixed epochs fail closed',()=>{
  const cases=[
    [marker(0,{epoch:'runtime-old',projectionEpoch:'runtime-a'}),projection({epoch:'runtime-a'}),db()],
    [marker(0,{epoch:'runtime-a',projectionEpoch:'runtime-old'}),projection({epoch:'runtime-a'}),db()],
    [marker(0,{epoch:'runtime-b',projectionEpoch:'runtime-b'}),projection({epoch:'runtime-a'}),db()],
    [marker(0,{epoch:'runtime-a',projectionEpoch:'runtime-a'}),projection({epoch:'runtime-b'}),db({epoch:'runtime-a',projectionEpoch:'runtime-a'})],
    [marker(0,{epoch:'runtime-c',projectionEpoch:'runtime-c'}),projection({epoch:'runtime-b'}),db({epoch:'runtime-a',projectionEpoch:'runtime-a'})]
  ];
  for(const [m,p,d] of cases){assert.equal(plan([m],p,d).labels.length,0);}
});

test('08 projection epoch missing/malformed/non-string/coercible is rejected',()=>{
  const coercible={toString(){return'runtime-a';},valueOf(){return'runtime-a';}};
  for(const bad of [undefined,null,'',new String('runtime-a'),['runtime-a'],coercible,0,true]){
    const x=plan([marker(0)],projection({epoch:bad}),db());noLabel(x,'PROJECTION_EPOCH_MISSING');
  }
});

test('09 drawing-buffer epoch fields missing/malformed/non-string/coercible are rejected',()=>{
  const coercible={toString(){return'runtime-a';},valueOf(){return'runtime-a';}};
  for(const bad of [undefined,null,'',new String('runtime-a'),['runtime-a'],coercible,0,true]){
    noLabel(plan([marker(0)],projection(),db({epoch:bad,projectionEpoch:'runtime-a'})),'DRAWING_BUFFER_EPOCH_MISSING');
    noLabel(plan([marker(0)],projection(),db({epoch:'runtime-a',projectionEpoch:bad})),'DRAWING_BUFFER_EPOCH_MISSING');
  }
});

test('10 marker epoch missing/malformed/coercible/mismatch is rejected',()=>{
  const coercible={toString(){return'runtime-a';},valueOf(){return'runtime-a';}};
  for(const bad of [undefined,null,'',new String('runtime-a'),['runtime-a'],coercible,0,true,'runtime-old']){
    const x=plan([marker(0,{epoch:bad})]);assert.equal(x.labels.length,0);assert.equal(x.suppressed[0].reason,'EPOCH_MISMATCH');
  }
  for(const bad of [undefined,null,'',new String('runtime-a'),['runtime-a'],coercible,0,true,'runtime-old']){
    const x=plan([marker(0,{projectionEpoch:bad})]);assert.equal(x.labels.length,0);assert.equal(x.suppressed[0].reason,'EPOCH_MISMATCH');
  }
});

test('11 P1->P2->P3 retarget updates immediately with no old label hold',()=>{
  const seq=[0,4,8,0].map(v=>plan([marker(v)]).labels.map(x=>x.label));
  assert.deepEqual(seq,[['1P'],['2P'],['3P'],['1P']]);
});

test('12 simultaneous enemies retain independent targets',()=>{
  const x=plan([marker(0,{slot:0,sourceId:'enemy-slot-0'}),marker(4,{slot:1,sourceId:'enemy-slot-1'}),marker(8,{slot:2,sourceId:'enemy-slot-2'})]);
  assert.deepEqual(x.labels.map(v=>[v.slot,v.label]),[[0,'1P'],[1,'2P'],[2,'3P']]);
});

test('13 disappearance/same-slot replacement cannot inherit stale label',()=>{
  assert.equal(plan([marker(0)]).labels[0].label,'1P');
  assert.equal(plan([]).labels.length,0);
  const bad=plan([marker(6,{target:null})]);assert.equal(bad.labels.length,0);
  assert.equal(plan([marker(4,{slot:0,sourceId:'enemy-slot-0'})]).labels[0].label,'2P');
});

test('14 marker/projection/drawing-buffer freshness boundaries fail closed',()=>{
  assert.equal(plan([marker(0,{sampleAt:NOW-300})]).labels.length,1);
  assert.equal(plan([marker(0,{sampleAt:NOW-301})]).labels.length,0);
  assert.equal(plan([marker(0)],projection({sampleAt:NOW-300})).labels.length,1);
  noLabel(plan([marker(0)],projection({sampleAt:NOW-301})),'STALE_PROJECTION');
  assert.equal(plan([marker(0)],projection(),db({sampleAt:NOW-1000})).labels.length,1);
  noLabel(plan([marker(0)],projection(),db({sampleAt:NOW-1001})),'STALE_DRAWING_BUFFER');
});

test('15 invalid confidence/non-finite coordinates/camera fail closed',()=>{
  for(const bad of [NaN,Infinity,-Infinity,-0.01,1.01])assert.equal(plan([marker(0,{confidence:bad})]).labels.length,0);
  for(const bad of [NaN,Infinity,-Infinity]){
    assert.equal(plan([marker(0,{enemyX:bad})]).labels.length,0);
    noLabel(plan([marker(0)],projection({cameraRaw:bad,cameraX:bad})),'INVALID_CAMERA_SAMPLE');
  }
});

test('16 unsupported type/slot/target and invalid native anchor suppress',()=>{
  assert.equal(plan([marker(0,{type:46})]).labels.length,0);
  assert.equal(plan([marker(0,{slot:-1})]).labels.length,0);
  assert.equal(plan([marker(0,{slot:20})]).labels.length,0);
  assert.equal(plan([marker(6,{target:null})]).labels.length,0);
  assert.equal(plan([marker(0,{enemyX:39,enemyY:31,enemyZ:0})],projection({cameraRaw:50,cameraX:50,xBias:10,enemyHeadOffsetsByType:{18:-30},yModel:'Y'})).labels.length,0);
});

test('17 edge clamp applies only to valid compact label rectangle',()=>{
  const near=plan([marker(0,{enemyX:41,enemyY:31,enemyZ:0})],projection({cameraRaw:50,cameraX:50,xBias:10,enemyHeadOffsetsByType:{18:-30},yModel:'Y'}));
  assert.equal(near.labels.length,1);assert.deepEqual(near.labels[0].anchorDb,{x:1,y:1});assert.deepEqual(near.labels[0].drawRectDb,{x:0,y:0,width:30,height:18});
  const outside=plan([marker(0,{enemyX:39,enemyY:31,enemyZ:0})],projection({cameraRaw:50,cameraX:50,xBias:10,enemyHeadOffsetsByType:{18:-30},yModel:'Y'}));
  assert.equal(outside.labels.length,0);assert.equal(outside.suppressed[0].reason,'PROJECTION_OUT_OF_BOUNDS');
});

test('18 resize/fullscreen remap changes mapping and stale generation cannot be reused',()=>{
  const a=plan([marker(0)],projection(),db());
  const resized=plan([marker(0)],projection(),db({width:768,height:448,contentRect:{x:0,y:0,width:768,height:448},mappingVersion:'768:448:0:0:768:448'}));
  const fs=plan([marker(0)],projection(),db({fullscreen:true,mappingVersion:'384:224:fs'}));
  assert.notEqual(a.mappingKey,resized.mappingKey);assert.notEqual(a.mappingKey,fs.mappingKey);
  assert.deepEqual(resized.labels[0].anchorDb,{x:a.labels[0].anchorDb.x*2,y:a.labels[0].anchorDb.y*2});
  noLabel(plan([marker(0)],projection(),db({width:768,height:448,contentRect:{x:0,y:0,width:768,height:448},mappingVersion:'old-resize',epoch:'runtime-old',projectionEpoch:'runtime-old'})),'DRAWING_BUFFER_EPOCH_MISMATCH');
});

test('19 invalid drawing-buffer geometry/content bounds suppress before clamp',()=>{
  const badStates=[
    db({width:0}),db({height:0}),db({contentRect:{x:-1,y:0,width:384,height:224}}),db({contentRect:{x:0,y:0,width:385,height:224}}),db({contentRect:{x:0,y:0,width:384,height:225}}),db({contentRect:{x:0,y:0,width:NaN,height:224}})
  ];
  for(const d of badStates)noLabel(plan([marker(0)],projection(),d),'INVALID_DRAWING_BUFFER');
});

test('20 repository projection profile remains UNPROVEN and fail-closed',()=>{
  assert.equal(profileJson.verdict,'UNPROVEN');assert.equal(profileJson.status,'FAIL_CLOSED_UNTIL_IMPLEMENTATION_READY_PROOF');
  assert.equal(L.validateProofProfile(profileJson).ok,false);
  noLabel(L.buildPlan({markers:[marker(0)],projection:profileJson,drawingBufferState:db(),nowMs:NOW}),'PROJECTION_UNPROVEN');
});

test('21 malformed proof/profile facts fail closed',()=>{
  const bad=[projection({proofId:''}),projection({romSha256:'bad'}),projection({nativeWidth:383}),projection({cameraAddress:0xFF1001}),projection({cameraRead:'u16le'}),projection({cameraSign:0}),projection({cameraScale:0}),projection({xBias:NaN}),projection({yModel:'bad'}),projection({enemyHeadOffsetsByType:{}})];
  for(const p of bad)assert.equal(plan([marker(0)],p,db()).labels.length,0);
});

test('22 marker array malformed input fails closed/no crash',()=>{
  const x=L.buildPlan({markers:{not:'array'},projection:projection(),drawingBufferState:db(),nowMs:NOW});assert.equal(x.labels.length,0);assert.equal(x.suppressed.length,0);
});

test('23 tiny valid drawing-buffer still clamps compact label rectangle within content rect',()=>{
  const tiny=db({width:20,height:10,contentRect:{x:0,y:0,width:20,height:10},mappingVersion:'20:10'});
  const x=plan([marker(0)],projection(),tiny);assert.equal(x.labels.length,1);assert.deepEqual(x.labels[0].drawRectDb,{x:0,y:0,width:20,height:10});
});

const failed=results.filter(x=>!x.ok);
const out={schema:'wof-alpha-enemy-target-head-labels-independent-repository-qa-v3',status:failed.length?'FAIL':'PASS',testCount:results.length,passCount:results.length-failed.length,failCount:failed.length,evidenceClass:'SYNTHETIC_REPOSITORY_QA_ONLY_NOT_BROWSER_WOF_PROJECTION_PROOF',results};
console.log(JSON.stringify(out,null,2));
if(failed.length)process.exit(1);
