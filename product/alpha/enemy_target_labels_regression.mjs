import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const L=require('./wof_alpha_enemy_target_labels.js');
const H=require('./wof_alpha_hud_model.js');
const workerSource=fs.readFileSync(new URL('./wof_alpha_real_worker.js',import.meta.url),'utf8');
const hudSource=fs.readFileSync(new URL('./wof_alpha_hud.js',import.meta.url),'utf8');
const loaderSource=fs.readFileSync(new URL('./wof_alpha_loader.js',import.meta.url),'utf8');
const profileJson=JSON.parse(fs.readFileSync(new URL('./wof_alpha_enemy_head_projection.json',import.meta.url),'utf8'));

const NOW=10000;
const profile={schema:L.PROJECTION_SCHEMA,verdict:L.PROJECTION_VERDICT,proofId:'synthetic-implementation-regression-only',romSha256:L.SUPPORTED_ROM_SHA,
  nativeWidth:384,nativeHeight:224,cameraAddress:0xFF1000,cameraRead:'u16be',cameraSign:1,cameraScale:1,xBias:10,yModel:'Y-Z',enemyHeadOffsetsByType:{18:-20,20:-24}};
const projection=(extra={})=>({...profile,epoch:'epoch-a',sampleAt:NOW,confidence:1,cameraRaw:50,cameraX:50,...extra});
const marker=(target7E=0,extra={})=>({slot:0,sourceId:'enemy-slot-0',type:18,target7E,target:L.targetForField(target7E),enemyX:100,enemyY:100,enemyZ:10,
  sampleAt:NOW,confidence:1,epoch:'epoch-a',projectionEpoch:'epoch-a',...extra});
const db=(extra={})=>({width:384,height:224,contentRect:{x:0,y:0,width:384,height:224},sampleAt:NOW,confidence:1,mappingVersion:'384:224:0:0:384:224',fullscreen:false,epoch:'epoch-a',projectionEpoch:'epoch-a',...extra});
const plan=(markers,p=projection(),d=db(),now=NOW)=>L.buildPlan({markers,pProjection:p,projection:p,drawingBufferState:d,nowMs:now});

const results=[];
function test(name,fn){try{fn();results.push({name,ok:true});}catch(error){results.push({name,ok:false,error:String(error?.stack||error)});}}

test('1 target7E 0/4/8 maps to 1P/2P/3P',()=>{
  assert.equal(L.targetForField(0),'P1');assert.equal(L.labelForTarget(L.targetForField(0)),'1P');
  assert.equal(L.targetForField(4),'P2');assert.equal(L.labelForTarget(L.targetForField(4)),'2P');
  assert.equal(L.targetForField(8),'P3');assert.equal(L.labelForTarget(L.targetForField(8)),'3P');
  assert.match(workerSource,/core\.TARGETS\[s\.target7E\]\|\|null/,'real worker must consume existing core target authority');
});

test('2 unsupported target fails closed with no confident label',()=>{
  assert.equal(L.targetForField(6),null);
  const x=plan([marker(6,{target:null})]);assert.equal(x.labels.length,0);assert.equal(x.suppressed[0].reason,'INVALID_TARGET');
});

test('3 same enemy P1 -> P2 -> P3 retarget has no stale hold',()=>{
  const a=plan([marker(0)]),b=plan([marker(4)]),c=plan([marker(8)]);
  assert.deepEqual(a.labels.map(x=>x.label),['1P']);assert.deepEqual(b.labels.map(x=>x.label),['2P']);assert.deepEqual(c.labels.map(x=>x.label),['3P']);
  assert.doesNotMatch(workerSource,/markerHold|targetHold|smoothingAlpha/);assert.match(workerSource,/holdMs:0,smoothing:false/);
});

test('4 simultaneous enemies can target different players',()=>{
  const x=plan([marker(0,{slot:0,sourceId:'enemy-slot-0'}),marker(4,{slot:1,sourceId:'enemy-slot-1'}),marker(8,{slot:2,sourceId:'enemy-slot-2'})]);
  assert.deepEqual(x.labels.map(v=>v.label),['1P','2P','3P']);assert.deepEqual(x.labels.map(v=>v.slot),[0,1,2]);
});

test('5 same slot replacement cannot inherit old label state',()=>{
  assert.equal(plan([marker(0)]).labels[0].label,'1P');
  const unknown=plan([marker(6,{target:null})]);assert.equal(unknown.labels.length,0);
  const replacement=plan([marker(4,{type:18})]);assert.equal(replacement.labels.length,1);assert.equal(replacement.labels[0].label,'2P');
});

test('6 stale marker/projection or epoch mismatch suppresses label',()=>{
  const staleMarker=plan([marker(0,{sampleAt:NOW-301})]);assert.equal(staleMarker.labels.length,0);assert.equal(staleMarker.suppressed[0].reason,'STALE_MARKER');
  const staleProjection=plan([marker(0)],projection({sampleAt:NOW-301}));assert.equal(staleProjection.labels.length,0);assert.equal(staleProjection.reason,'STALE_PROJECTION');
  const epochMismatch=plan([marker(0,{epoch:'old',projectionEpoch:'old'})]);assert.equal(epochMismatch.labels.length,0);assert.equal(epochMismatch.suppressed[0].reason,'EPOCH_MISMATCH');
});

test('7 invalid confidence NaN Infinity and nonfinite XYZ fail closed',()=>{
  for(const bad of [NaN,Infinity,-Infinity]){
    const a=plan([marker(0,{confidence:bad})]);assert.equal(a.labels.length,0);
    const b=plan([marker(0)],projection({confidence:bad}));assert.equal(b.labels.length,0);
    const c=plan([marker(0,{enemyX:bad})]);assert.equal(c.labels.length,0);
  }
});

test('8 valid near-edge anchor clamps label rectangle; invalid anchor never masquerades',()=>{
  const near=plan([marker(0,{enemyX:41,enemyY:31,enemyZ:0})],projection({cameraRaw:50,cameraX:50,xBias:10,enemyHeadOffsetsByType:{18:-30},yModel:'Y'}));
  assert.equal(near.labels.length,1);assert.equal(near.labels[0].anchorDb.x,1);assert.equal(near.labels[0].anchorDb.y,1);assert.equal(near.labels[0].drawRectDb.x,0);assert.equal(near.labels[0].drawRectDb.y,0);
  const outside=plan([marker(0,{enemyX:39,enemyY:31,enemyZ:0})],projection({cameraRaw:50,cameraX:50,xBias:10,enemyHeadOffsetsByType:{18:-30},yModel:'Y'}));
  assert.equal(outside.labels.length,0);assert.equal(outside.suppressed[0].reason,'PROJECTION_OUT_OF_BOUNDS');
});

test('9 resize/fullscreen mapping changes reset by construction',()=>{
  const a=plan([marker(0)],projection(),db());
  const b=plan([marker(0)],projection(),db({width:768,height:448,contentRect:{x:0,y:0,width:768,height:448},mappingVersion:'768:448:0:0:768:448'}));
  const c=plan([marker(0)],projection(),db({fullscreen:true,mappingVersion:'384:224:fs'}));
  assert.notEqual(a.mappingKey,b.mappingKey);assert.notEqual(a.mappingKey,c.mappingKey);assert.equal(b.labels[0].anchorDb.x,a.labels[0].anchorDb.x*2);assert.equal(b.labels[0].anchorDb.y,a.labels[0].anchorDb.y*2);
});

test('10 fixed danger warning HUD model remains intact',()=>{
  const model=H.summarizeWarnings([{target:'P1',threatSide:'LEFT',attackSpecific:true,attack:5440},{target:'P2',threatSide:'RIGHT',attackSpecific:false}]);
  assert.equal(model.count,2);assert.equal(model.groupCount,2);assert.match(hudSource,/summarizeWarnings/);assert.match(hudSource,/paintBox\(model\.count\+' 个危险'/);
});

test('11 read-only safety invariants remain explicit',()=>{
  assert.match(workerSource,/readOnly:true,ramWrites:0,inputInjection:false,workerReplacement:false,blobRewrite:false/);
  assert.doesNotMatch(workerSource,/new\s+Worker\s*\(/);assert.doesNotMatch(workerSource,/new\s+Blob\s*\(/);assert.doesNotMatch(workerSource,/createObjectURL/);
  assert.match(workerSource,/enemyWorldX:F16\(a\+0x04\),enemyY:F16\(a\+0x08\),enemyZ:F16\(a\+0x0C\)/);
});

test('12 Alpha/Formal transport contract stays compatible and marker cadence is bounded',()=>{
  assert.match(workerSource,/const RELEASE='wof-alpha-rc3'/);assert.match(workerSource,/const SCHEMA='wof-alpha-v2'/);assert.match(workerSource,/const TRANSPORT='wof-alpha-safe-transport-v1'/);
  assert.match(workerSource,/changed\|\|heartbeat/);assert.match(workerSource,/sampledAt-lastPublishedAt>=250/);
  assert.match(workerSource,/envelope\('enemy-target-markers'/);assert.match(workerSource,/sampledAt-lastMarkerPublishedAt>=50/);
  assert.match(hudSource,/TRANSPORT\.matches\(m\)/);assert.match(hudSource,/m\.kind==='enemy-target-markers'/);assert.match(loaderSource,/wof_alpha_enemy_target_labels\.js/);
  assert.equal(L.validateProofProfile(profileJson).ok,false,'repository profile must remain fail-closed until bounded Browser proof');
});

const failed=results.filter(x=>!x.ok);
console.log(JSON.stringify({schema:'wof-alpha-enemy-target-head-labels-implementation-regression-v1',status:failed.length?'FAIL':'PASS',testCount:results.length,passCount:results.length-failed.length,failCount:failed.length,
  fixture:'SYNTHETIC_IMPLEMENTATION_REGRESSION_ONLY_NOT_INDEPENDENT_QA_NOT_BROWSER_PROOF',results},null,2));
if(failed.length)process.exit(1);
