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
const profile={schema:L.PROJECTION_SCHEMA,verdict:L.PROJECTION_VERDICT,projectionKind:L.PROJECTION_KIND,proofId:'synthetic-implementation-regression-only',romSha256:L.SUPPORTED_ROM_SHA,
  nativeWidth:384,nativeHeight:224,cameraAddress:0xFF1000,cameraRead:'u16be',cameraSign:1,cameraScale:1,xBias:10,
  yAxisSign:1,yModel:'Y-Z',yBias:20,enemyHeadClearanceByType:{18:20,20:24}};
const projection=(extra={})=>({...profile,epoch:'epoch-a',sampleAt:NOW,confidence:1,cameraRaw:50,cameraX:50,...extra});
const marker=(target7E=0,extra={})=>({slot:0,sourceId:'enemy-slot-0',type:18,target7E,target:L.targetForField(target7E),enemyX:100,enemyY:100,enemyZ:10,
  sampleAt:NOW,confidence:1,epoch:'epoch-a',projectionEpoch:'epoch-a',...extra});
const db=(extra={})=>({width:384,height:224,contentRect:{x:0,y:0,width:384,height:224},sampleAt:NOW,confidence:1,mappingVersion:'384:224:0:0:384:224',fullscreen:false,epoch:'epoch-a',projectionEpoch:'epoch-a',...extra});
const plan=(markers,p=projection(),d=db(),now=NOW)=>L.buildPlan({markers,projection:p,drawingBufferState:d,nowMs:now});

const results=[];
function test(name,fn){try{fn();results.push({name,ok:true});}catch(error){results.push({name,ok:false,error:String(error?.stack||error)});}}

test('1 target7E 0/4/8 maps to 1P/2P/3P',()=>{
  assert.equal(L.targetForField(0),'P1');assert.equal(L.labelForTarget(L.targetForField(0)),'1P');
  assert.equal(L.targetForField(4),'P2');assert.equal(L.labelForTarget(L.targetForField(4)),'2P');
  assert.equal(L.targetForField(8),'P3');assert.equal(L.labelForTarget(L.targetForField(8)),'3P');
  assert.match(workerSource,/core\.TARGETS\[s\.target7E\]\|\|null/,'real worker must consume existing core target authority');
});

test('2 malformed/coercible raw target7E values fail closed',()=>{
  const coercible={valueOf(){return 0;},toString(){return'0';}};
  const malformed=[['0','P1'],['4','P2'],['8','P3'],[new Number(0),'P1'],[NaN,'P1'],[Infinity,'P1'],[0.5,'P1'],[-0,'P1'],[true,'P1'],[null,'P1'],[undefined,'P1'],[[],'P1'],[[0],'P1'],[coercible,'P1']];
  for(const [raw,normalized] of malformed){
    assert.equal(L.targetForField(raw),null);
    const x=plan([marker(0,{target7E:raw,target:normalized})]);assert.equal(x.labels.length,0);assert.equal(x.suppressed[0].reason,'INVALID_TARGET');
  }
});

test('3 v2 geometry contract rejects legacy conflated offsets',()=>{
  assert.equal(L.validateProofProfile(profile).ok,true);
  assert.equal(L.validateProofProfile({...profile,enemyHeadOffsetsByType:{18:-20}}).reason,'LEGACY_ENEMY_HEAD_OFFSETS_UNSUPPORTED');
  assert.equal(L.validateProofProfile({...profile,yAxisSign:0}).reason,'INVALID_Y_AXIS_SIGN');
  assert.equal(L.validateProofProfile({...profile,yBias:NaN}).reason,'INVALID_PROJECTION_CONSTANTS');
  assert.equal(L.validateProofProfile({...profile,enemyHeadClearanceByType:{18:-1}}).reason,'INVALID_ENEMY_HEAD_CLEARANCE');
});

test('4 Y axis sign can correct reversed depth direction without changing Z model',()=>{
  const downA=L.projectMarkerNative(marker(0,{enemyY:80}),projection({yAxisSign:1,yBias:20}));
  const downB=L.projectMarkerNative(marker(0,{enemyY:100}),projection({yAxisSign:1,yBias:20}));
  assert.ok(downB.anchorYNative>downA.anchorYNative);
  const upA=L.projectMarkerNative(marker(0,{enemyY:80}),projection({yAxisSign:-1,yBias:220}));
  const upB=L.projectMarkerNative(marker(0,{enemyY:100}),projection({yAxisSign:-1,yBias:220}));
  assert.ok(upB.anchorYNative<upA.anchorYNative);
});

test('5 Y-Z/Y+Z/Y keep Z sign explicit in top-origin native Y',()=>{
  const ground=L.projectMarkerNative(marker(0,{enemyZ:0}),projection({yModel:'Y-Z'}));
  const minus=L.projectMarkerNative(marker(0,{enemyZ:20}),projection({yModel:'Y-Z'}));
  const plus=L.projectMarkerNative(marker(0,{enemyZ:20}),projection({yModel:'Y+Z'}));
  const none=L.projectMarkerNative(marker(0,{enemyZ:20}),projection({yModel:'Y'}));
  assert.ok(minus.anchorYNative<ground.anchorYNative,'Y-Z positive Z must move toward screen top');
  assert.ok(plus.anchorYNative>ground.anchorYNative,'Y+Z positive Z must move toward screen bottom');
  assert.equal(none.anchorYNative,ground.anchorYNative,'Y ignores Z');
});

test('6 common yBias and per-type head clearance are independent',()=>{
  const base=L.projectMarkerNative(marker(),projection({yBias:20,enemyHeadClearanceByType:{18:20,20:24}}));
  const bias=L.projectMarkerNative(marker(),projection({yBias:25,enemyHeadClearanceByType:{18:20,20:24}}));
  const clear=L.projectMarkerNative(marker(),projection({yBias:20,enemyHeadClearanceByType:{18:25,20:24}}));
  assert.equal(bias.bodyYNative-base.bodyYNative,5);assert.equal(bias.anchorYNative-base.anchorYNative,5);
  assert.equal(clear.bodyYNative,base.bodyYNative);assert.equal(clear.anchorYNative-base.anchorYNative,-5);
});

test('7 camera scroll compensation pins enemy X when world and camera advance together',()=>{
  const a=L.projectMarkerNative(marker(0,{enemyX:100}),projection({cameraRaw:50,cameraX:50}));
  const b=L.projectMarkerNative(marker(0,{enemyX:140}),projection({cameraRaw:90,cameraX:90}));
  assert.equal(a.anchorXNative,b.anchorXNative);
  const neg=projection({cameraSign:-1,cameraRaw:50,cameraX:-50});
  assert.equal(L.validateProjection(neg,NOW).ok,true,'camera sign must be explicit authority, not hard-coded by projector');
});

test('8 same enemy P1 -> P2 -> P3 retarget has no stale hold',()=>{
  const a=plan([marker(0)]),b=plan([marker(4)]),c=plan([marker(8)]);
  assert.deepEqual(a.labels.map(x=>x.label),['1P']);assert.deepEqual(b.labels.map(x=>x.label),['2P']);assert.deepEqual(c.labels.map(x=>x.label),['3P']);
  assert.doesNotMatch(workerSource,/markerHold|targetHold|smoothingAlpha/);assert.match(workerSource,/holdMs:0,smoothing:false/);
});

test('9 multiple current enemies render independently',()=>{
  const x=plan([marker(0,{slot:0,sourceId:'enemy-slot-0'}),marker(4,{slot:1,sourceId:'enemy-slot-1'}),marker(8,{slot:2,sourceId:'enemy-slot-2'})]);
  assert.deepEqual(x.labels.map(v=>v.label),['1P','2P','3P']);assert.deepEqual(x.labels.map(v=>v.slot),[0,1,2]);
});

test('10 stale/lost enemy hides immediately and fresh recovery reappears',()=>{
  const fresh=plan([marker(0)]);assert.equal(fresh.labels.length,1);
  const stale=plan([marker(0,{sampleAt:NOW-301})]);assert.equal(stale.labels.length,0);assert.equal(stale.suppressed[0].reason,'STALE_MARKER');
  const recovered=plan([marker(0,{sampleAt:NOW})]);assert.equal(recovered.labels.length,1);
});

test('11 projection/drawing-buffer/marker epoch authority must be exact-current',()=>{
  const currentProjection=projection({epoch:'runtime-a'}),currentMarker=marker(0,{epoch:'runtime-a',projectionEpoch:'runtime-a'}),currentDb=db({epoch:'runtime-a',projectionEpoch:'runtime-a'});
  assert.equal(plan([currentMarker],currentProjection,currentDb).labels.length,1);
  const stalePair=plan([currentMarker],currentProjection,db({epoch:'runtime-old',projectionEpoch:'runtime-old'}));assert.equal(stalePair.labels.length,0);assert.equal(stalePair.reason,'DRAWING_BUFFER_EPOCH_MISMATCH');
  const splitPair=plan([currentMarker],currentProjection,db({epoch:'runtime-a',projectionEpoch:'runtime-old'}));assert.equal(splitPair.labels.length,0);assert.equal(splitPair.reason,'DRAWING_BUFFER_EPOCH_MISMATCH');
});

test('12 invalid confidence/nonfinite XYZ fail closed',()=>{
  for(const bad of [NaN,Infinity,-Infinity]){
    assert.equal(plan([marker(0,{confidence:bad})]).labels.length,0);
    assert.equal(plan([marker(0)],projection({confidence:bad})).labels.length,0);
    assert.equal(plan([marker(0,{enemyX:bad})]).labels.length,0);
  }
});

test('13 top-origin WebGL viewport mapping preserves letterbox offsets and scale',()=>{
  const a=plan([marker(0)]);
  const b=plan([marker(0)],projection(),db({width:800,height:488,contentRect:{x:16,y:20,width:768,height:448},mappingVersion:'800:488:16:20:768:448'}));
  assert.equal(b.labels.length,1);
  assert.equal(b.labels[0].anchorDb.x,16+a.labels[0].anchorDb.x*2);
  assert.equal(b.labels[0].anchorDb.y,20+a.labels[0].anchorDb.y*2);
  assert.match(hudSource,/y=H-\(vp\[1\]\+vp\[3\]\)/,'HUD must convert GL bottom-origin viewport to top-origin content rect');
  assert.match(hudSource,/t=1-r\.y\/H\*2,b=1-\(r\.y\+r\.height\)\/H\*2/,'label draw must consume top-origin drawing-buffer Y exactly once');
});

test('14 near-edge anchor clamps label rectangle; invalid anchor never masquerades',()=>{
  const p=projection({cameraRaw:50,cameraX:50,xBias:10,yAxisSign:1,yModel:'Y',yBias:0,enemyHeadClearanceByType:{18:30,20:24}});
  const near=plan([marker(0,{enemyX:41,enemyY:31,enemyZ:0})],p);assert.equal(near.labels.length,1);assert.equal(near.labels[0].anchorDb.x,1);assert.equal(near.labels[0].anchorDb.y,1);assert.equal(near.labels[0].drawRectDb.x,0);assert.equal(near.labels[0].drawRectDb.y,0);
  const outside=plan([marker(0,{enemyX:39,enemyY:31,enemyZ:0})],p);assert.equal(outside.labels.length,0);assert.equal(outside.suppressed[0].reason,'PROJECTION_OUT_OF_BOUNDS');
});

test('15 resize/fullscreen mapping changes reset by construction',()=>{
  const a=plan([marker(0)],projection(),db());
  const b=plan([marker(0)],projection(),db({width:768,height:448,contentRect:{x:0,y:0,width:768,height:448},mappingVersion:'768:448:0:0:768:448'}));
  const c=plan([marker(0)],projection(),db({fullscreen:true,mappingVersion:'384:224:fs'}));
  assert.notEqual(a.mappingKey,b.mappingKey);assert.notEqual(a.mappingKey,c.mappingKey);assert.equal(b.labels[0].anchorDb.x,a.labels[0].anchorDb.x*2);assert.equal(b.labels[0].anchorDb.y,a.labels[0].anchorDb.y*2);
});

test('16 fixed danger warning HUD model remains intact',()=>{
  const model=H.summarizeWarnings([{target:'P1',threatSide:'LEFT',attackSpecific:true,attack:5440},{target:'P2',threatSide:'RIGHT',attackSpecific:false}]);
  assert.equal(model.count,2);assert.equal(model.groupCount,2);assert.match(hudSource,/summarizeWarnings/);assert.match(hudSource,/paintBox\(model\.count\+' 个危险'/);
});

test('17 read-only safety and current enemy XYZ sampling remain explicit',()=>{
  assert.match(workerSource,/readOnly:true,ramWrites:0,inputInjection:false,workerReplacement:false,blobRewrite:false/);
  assert.doesNotMatch(workerSource,/new\s+Worker\s*\(/);assert.doesNotMatch(workerSource,/new\s+Blob\s*\(/);assert.doesNotMatch(workerSource,/createObjectURL/);
  assert.match(workerSource,/enemyWorldX:F16\(a\+0x04\),enemyY:F16\(a\+0x08\),enemyZ:F16\(a\+0x0C\)/);
});

test('18 transport compatibility and bounded marker cadence remain intact',()=>{
  assert.match(workerSource,/const RELEASE='wof-alpha-rc3'/);assert.match(workerSource,/const SCHEMA='wof-alpha-v2'/);assert.match(workerSource,/const TRANSPORT='wof-alpha-safe-transport-v1'/);
  assert.match(workerSource,/envelope\('enemy-target-markers'/);assert.match(workerSource,/sampledAt-lastMarkerPublishedAt>=50/);
  assert.match(hudSource,/TRANSPORT\.matches\(m\)/);assert.match(hudSource,/m\.kind==='enemy-target-markers'/);assert.match(loaderSource,/wof_alpha_enemy_target_labels\.js/);
  assert.equal(L.validateProofProfile(profileJson).ok,false,'repository profile must remain fail-closed until corrected live enemy-head geometry is bound');
});

const failed=results.filter(x=>!x.ok);
console.log(JSON.stringify({schema:'wof-alpha-enemy-head-anchor-geometry-regression-v2',status:failed.length?'FAIL':'PASS',testCount:results.length,passCount:results.length-failed.length,failCount:failed.length,
  fixture:'SYNTHETIC_GEOMETRY_REGRESSION_ONLY_NOT_BROWSER_WOF_LIVE_PROOF',geometryVersion:L.GEOMETRY_VERSION,results},null,2));
if(failed.length)process.exit(1);
