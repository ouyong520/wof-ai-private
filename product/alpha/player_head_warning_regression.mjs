import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import fs from 'node:fs';
const require=createRequire(import.meta.url);
const A=require('./wof_alpha_player_head_warning.js');

const E='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa';
const E2='bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb';
const profile={
  schema:A.PROFILE_SCHEMA,status:'PROVED',proofId:'synthetic-proof-v1',projectionVersion:'synthetic-projection-v1',
  projectionKind:A.PROJECTION_KIND,source:'SYNTHETIC_ONLY_NOT_BROWSER_PROOF',
  nativeWidth:384,nativeHeight:224,cameraAddress:0xFF0100,cameraSign:1,cameraScale:1,
  worldXScale:1,xBias:80,floorYScale:1,zScale:-1,yBias:120,headClearanceNative:24,
  validationBounds:{minX:0,maxX:383,minY:0,maxY:223}
};
const good=A.validateProofProfile(profile);
assert.equal(good.ok,true,JSON.stringify(good));
const proj=(cameraX=0,sampleAt=1000,epoch=E)=>({
  schema:A.PROFILE_SCHEMA,status:'PROVED',proofId:profile.proofId,version:profile.projectionVersion,projectionKind:A.PROJECTION_KIND,
  source:'SYNTHETIC_ONLY_NOT_BROWSER_PROOF',epoch,projectionEpoch:epoch,sampleAt,confidence:1,
  nativeWidth:384,nativeHeight:224,cameraX,worldXScale:1,xBias:80,floorYScale:1,zScale:-1,yBias:120,headClearanceNative:24,
  validationBounds:{minX:0,maxX:383,minY:0,maxY:223}
});
const db=(sampleAt=1000,epoch=E,width=768,height=448,contentRect={x:0,y:0,width,height},fullscreen=false)=>({
  width,height,contentRect,sampleAt,confidence:1,epoch,projectionEpoch:epoch,mappingVersion:`${width}:${height}:${contentRect.x}:${contentRect.y}:${contentRect.width}:${contentRect.height}`,fullscreen
});
const player=(x=100,y=50,z=0,sampleAt=1000,epoch=E,present=true)=>({present,x,y,z,sampleAt,confidence:1,epoch,projectionEpoch:epoch});
const warning=(target='P1',slot=0)=>({target,slot,ruleId:'SYNTH',threatSide:'LEFT',attack:5440});
const plan=(warnings,players,projection=proj(),drawing=db(),now=1010,warningSampleAt=1000,warningEpoch=E)=>A.buildPlan({
  warnings,players,projection,drawingBufferState:drawing,nowMs:now,warningSampleAt,warningEpoch
});
const center=r=>[r.drawRectDb.x+r.drawRectDb.width/2,r.drawRectDb.y+r.drawRectDb.height/2];

let passed=0;
const test=(name,fn)=>{fn();passed++;};

// 1 horizontal current-snapshot following.
test('horizontal movement',()=>{
  const a=plan([warning() ],{P1:player(80)}).anchored[0];
  const b=plan([warning() ],{P1:player(140)}).anchored[0];
  assert.equal(center(b)[0]-center(a)[0],120);
});
// 2 depth/lane Y.
test('depth movement',()=>{
  const a=plan([warning()],{P1:player(100,30,0)}).anchored[0];
  const b=plan([warning()],{P1:player(100,60,0)}).anchored[0];
  assert.equal(center(b)[1]-center(a)[1],60);
});
// 3 jump ascent/apex/descent/landing uses fresh Z and returns.
test('jump series',()=>{
  const zs=[0,12,24,12,0];
  const ys=zs.map(z=>center(plan([warning()],{P1:player(100,50,z)}).anchored[0])[1]);
  assert.deepEqual(ys,[292,268,244,268,292]);
});
// 4 rapid forward/back has no smoothing/hold.
test('rapid movement no smoothing',()=>{
  const xs=[60,220,70].map(x=>center(plan([warning()],{P1:player(x)}).anchored[0])[0]);
  assert.deepEqual(xs,[280,600,300]);
});
// 5 camera scroll compensates current frame.
test('camera scroll',()=>{
  const a=plan([warning()],{P1:player(160)},proj(0)).anchored[0];
  const b=plan([warning()],{P1:player(160)},proj(50)).anchored[0];
  assert.equal(center(b)[0]-center(a)[0],-100);
});
// 6 player + camera simultaneous.
test('simultaneous player camera',()=>{
  const a=plan([warning()],{P1:player(100)},proj(0)).anchored[0];
  const b=plan([warning()],{P1:player(150)},proj(30)).anchored[0];
  assert.equal(center(b)[0]-center(a)[0],40);
});
// 7 resize/fullscreen remap uses live dimensions only.
test('resize fullscreen remap',()=>{
  const a=plan([warning()],{P1:player(100)},proj(),db()).anchored[0];
  const d=db(1000,E,1152,672,{x:192,y:0,width:768,height:672},true);
  const b=plan([warning()],{P1:player(100)},proj(),d).anchored[0];
  assert.notDeepEqual(a.drawRectDb,b.drawRectDb);
  assert.equal(b.anchor.mappingKey.includes(':fs:'),true);
});
// 8 simultaneous P1/P2/P3.
test('three players',()=>{
  const p=plan([warning('P1',0),warning('P2',1),warning('P3',2)],{
    P1:player(80,40),P2:player(120,50),P3:player(160,60)
  });
  assert.deepEqual(p.anchored.map(x=>x.player),['P1','P2','P3']);
  assert.equal(p.fixed.length,0);
});
// 9 death/respawn replacement cannot reuse old coordinates.
test('death respawn',()=>{
  const alive=plan([warning()],{P1:player(80)}); assert.equal(alive.anchored.length,1);
  const dead=plan([warning()],{P1:player(80,50,0,1000,E,false)}); assert.equal(dead.anchored.length,0); assert.equal(dead.fixed[0].reason,'PLAYER_ABSENT');
  const reborn=plan([warning()],{P1:player(180)}); assert.equal(center(reborn.anchored[0])[0],520);
});
// 10 retarget invalidates old player before fresh new spatial sample.
test('retarget sample barrier',()=>{
  const p1=plan([warning('P1')],{P1:player(80,50,0,1000),P2:player(180,50,0,1000)},proj(0,1000),db(1000),1010,1000);
  assert.equal(p1.anchored[0].player,'P1');
  const stale=plan([warning('P2')],{P1:player(80,50,0,1000),P2:player(180,50,0,1000)},proj(0,1000),db(1010),1020,1010);
  assert.equal(stale.anchored.length,0); assert.equal(stale.fixed[0].player,'P2'); assert.equal(stale.fixed[0].reason,'SPATIAL_BEFORE_WARNING_SAMPLE');
  const fresh=plan([warning('P2')],{P2:player(190,50,0,1010)},proj(0,1010),db(1010),1020,1010);
  assert.equal(fresh.anchored[0].player,'P2');
});
// 11 stale and malformed/nonfinite/out-of-bounds.
test('stale malformed bounds',()=>{
  assert.equal(plan([warning()],{P1:player(100,50,0,900)},proj(),db(),1010).fixed[0].reason,'STALE_PLAYER');
  assert.equal(plan([warning()],{P1:{...player(),x:NaN}}).fixed[0].reason,'INVALID_PLAYER_XYZ');
  assert.equal(plan([warning()],{P1:player(360)}).fixed[0].reason,'PROJECTION_OUT_OF_BOUNDS');
});
// 12 epoch mismatch.
test('epoch mismatch',()=>{
  assert.equal(plan([warning()],{P1:player(100,50,0,1000,E2)},proj(),db()).fixed[0].reason,'EPOCH_MISMATCH');
});
// 13 rapid valid/invalid alternation has no last-coordinate reuse.
test('valid invalid valid',()=>{
  const a=plan([warning()],{P1:player(80)}); assert.equal(a.anchored.length,1);
  const b=plan([warning()],{P1:player(80,50,0,1000,E,false)}); assert.equal(b.anchored.length,0);
  const c=plan([warning()],{P1:player(160)}); assert.equal(center(c.anchored[0])[0],480);
});
// 14 invalid confidence.
test('confidence fail closed',()=>{
  const p={...player(),confidence:NaN};
  assert.equal(plan([warning()],{P1:p}).fixed[0].reason,'INVALID_PLAYER_CONFIDENCE');
});
// 15 unproved production profile is non-activatable.
test('unproved profile fail closed',()=>{
  const unproved=JSON.parse(fs.readFileSync(new URL('./wof_alpha_player_head_projection.json',import.meta.url),'utf8'));
  const v=A.validateProofProfile(unproved);
  assert.equal(v.ok,false); assert.equal(v.reasons.includes('PROFILE_NOT_PROVED'),true);
});
// 16 invalid projection and drawing-buffer confidence.
test('projection db confidence',()=>{
  assert.equal(plan([warning()],{P1:player()}, {...proj(),confidence:'1'}).fixed[0].reason,'INVALID_PROJECTION_CONFIDENCE');
  assert.equal(plan([warning()],{P1:player()}, proj(), {...db(),confidence:null}).fixed[0].reason,'INVALID_DRAWING_BUFFER_CONFIDENCE');
});
// 17 multiple warnings aggregate by target.
test('aggregation',()=>{
  const p=plan([warning('P1',0),warning('P1',1)],{P1:player()});
  assert.equal(p.anchored.length,1); assert.equal(p.anchored[0].warningCount,2);
});
// 18 strict invalid target never anchors.
test('invalid target',()=>{
  const p=plan([{...warning(),target:'1P'}],{P1:player()});
  assert.equal(p.anchored.length,0); assert.equal(p.fixed[0].reason,'INVALID_TARGET');
});
// 19 production worker uses a bounded 20 ms active-warning spatial publication cadence.
test('worker cadence integration',()=>{
  const src=fs.readFileSync(new URL('./wof_alpha_real_worker.js',import.meta.url),'utf8');
  assert.match(src,/const PLAYER_SPATIAL_PUBLISH_MS=20;/);
  assert.match(src,/warnings\.length>0&&spatialHeartbeat/);
  assert.match(src,/envelope\('player-head-spatial'/);
  assert.match(src,/envelope\('state',\{seq,warnings,sampleAt:sampleAtEpoch\}\)/);
  assert.match(src,/timer=setInterval\(beginTick,10\)/);
});
// 20 page HUD is wired to player-head helper and fixed fallback.
test('hud integration',()=>{
  const src=fs.readFileSync(new URL('./wof_alpha_hud.js',import.meta.url),'utf8');
  assert.match(src,/WOFAlphaPlayerHeadWarning\?\.buildPlan/);
  assert.match(src,/m\.kind==='player-head-spatial'/);
  assert.match(src,/drawFixedWarnings\(fixedWarnings\)/);
  assert.match(src,/holdMs:0,smoothing:false/);
});
// 21 loader includes helper before HUD.
test('loader integration',()=>{
  const src=fs.readFileSync(new URL('./wof_alpha_loader.js',import.meta.url),'utf8');
  const helper=src.indexOf("await load('wof_alpha_player_head_warning.js')");
  const hud=src.indexOf("await load('wof_alpha_hud.js')");
  assert.ok(helper>=0&&hud>helper);
});

console.log(JSON.stringify({status:'PASS',passed,total:21,fixture:'SYNTHETIC_PLAYER_HEAD_WARNING_ONLY_NOT_BROWSER_PROOF'}));
