import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const L=require('../../product/alpha/wof_alpha_enemy_target_labels.js');

const now=1000;
const projection={
  schema:L.PROJECTION_SCHEMA,verdict:'IMPLEMENTATION_READY',proofId:'independent-strict-type-crosscheck',
  romSha256:L.SUPPORTED_ROM_SHA,nativeWidth:384,nativeHeight:224,cameraAddress:0xFF0000,
  cameraRead:'u16be',cameraSign:1,cameraScale:1,xBias:0,yModel:'Y',enemyHeadOffsetsByType:{'1':-10},
  epoch:'E1',sampleAt:now,confidence:1,cameraRaw:0,cameraX:0
};
const drawing={width:384,height:224,sampleAt:now,confidence:1,epoch:'E1',projectionEpoch:'E1'};
const marker=(target7E,target,slot=0,extra={})=>({slot,type:1,target7E,target,enemyX:100+slot*20,enemyY:100,enemyZ:0,epoch:'E1',projectionEpoch:'E1',sampleAt:now,confidence:1,...extra});
const plan=(markers,p=projection,d=drawing)=>L.buildPlan({markers,projection:p,drawingBufferState:d,nowMs:now});
let checks=0; const test=(name,fn)=>{fn();checks++;console.log('PASS',name);};

test('exact primitive 0/4/8 map and render',()=>{
  for(const [raw,target,label] of [[0,'P1','1P'],[4,'P2','2P'],[8,'P3','3P']]){
    assert.equal(L.targetForField(raw),target);
    assert.deepEqual(plan([marker(raw,target)]).labels.map(x=>x.label),[label]);
  }
});

const malformed=[
  ['string-0','0'],['string-4','4'],['string-8','8'],
  ['boxed-0',new Number(0)],['boxed-4',new Number(4)],['boxed-8',new Number(8)],
  ['valueOf',{valueOf(){return 0;}}],['toString',{toString(){return '4';}}],
  ['array-0',[0]],['array-string-8',['8']],['true',true],['false',false],['null',null],['undefined',undefined],
  ['NaN',NaN],['Infinity',Infinity],['-Infinity',-Infinity],['fraction',4.5],['negative-zero',-0]
];

test('malformed/coercible raw targets fail mapper exact-type boundary',()=>{
  for(const [name,raw] of malformed)assert.equal(L.targetForField(raw),null,name);
});

test('malformed raw plus normalized P1/P2/P3 cannot render',()=>{
  for(const [name,raw] of malformed){
    for(const target of ['P1','P2','P3']){
      const out=plan([marker(raw,target)]);
      assert.equal(out.labels.length,0,`${name}/${target}`);
      assert.equal(out.suppressed[0]?.reason,'INVALID_TARGET',`${name}/${target}`);
    }
  }
});

test('retarget P1 -> P2 -> P3 has no prior-label hold',()=>{
  for(const [raw,target,label] of [[0,'P1','1P'],[4,'P2','2P'],[8,'P3','3P']])
    assert.deepEqual(plan([marker(raw,target)]).labels.map(x=>x.label),[label]);
});

test('simultaneous enemies retain independent targets',()=>{
  assert.deepEqual(plan([marker(0,'P1',0),marker(4,'P2',1),marker(8,'P3',2)]).labels.map(x=>x.label),['1P','2P','3P']);
});

test('stale marker fails closed',()=>{
  const out=plan([marker(0,'P1',0,{sampleAt:699})]);
  assert.equal(out.labels.length,0);assert.equal(out.suppressed[0]?.reason,'STALE_MARKER');
});

test('stale projection fails closed',()=>{
  const out=plan([marker(0,'P1')],{...projection,sampleAt:699});
  assert.equal(out.labels.length,0);assert.equal(out.reason,'STALE_PROJECTION');
});

test('epoch mismatch fails closed',()=>{
  const out=plan([marker(0,'P1',0,{epoch:'OLD',projectionEpoch:'OLD'})]);
  assert.equal(out.labels.length,0);assert.equal(out.suppressed[0]?.reason,'EPOCH_MISMATCH');
});

test('unproven projection fails closed',()=>{
  const out=plan([marker(0,'P1')],{...projection,verdict:'UNPROVEN'});
  assert.equal(out.labels.length,0);assert.equal(out.reason,'PROJECTION_UNPROVEN');
});

console.log(JSON.stringify({schema:'wof-alpha-enemy-target-head-labels-strict-type-independent-crosscheck-v1',status:'PASS',checks,malformedVectors:malformed.length,evidenceClass:'SYNTHETIC_REPOSITORY_QA_ONLY_NOT_BROWSER_WOF_PROJECTION_PROOF'}));
