import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import fs from 'node:fs';
const require=createRequire(import.meta.url);
const A=require('../../product/alpha/wof_alpha_player_head_warning.js');

const E='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa';
const E2='bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb';
const profile={
  schema:A.PROFILE_SCHEMA,status:'PROVED',proofId:'independent-proof-v2',projectionVersion:'independent-projection-v2',
  projectionKind:A.PROJECTION_KIND,source:'FRESH_QA_V2_SYNTHETIC_ONLY_NOT_BROWSER_PROOF',
  nativeWidth:384,nativeHeight:224,cameraAddress:0xFF0100,cameraSign:1,cameraScale:1,
  worldXScale:1,xBias:80,floorYScale:1,zScale:-1,yBias:120,headClearanceNative:24,
  validationBounds:{minX:0,maxX:383,minY:0,maxY:223}
};
const projection=(sampleAt=1000,epoch=E,overrides={})=>({
  schema:A.PROFILE_SCHEMA,status:'PROVED',proofId:profile.proofId,version:profile.projectionVersion,projectionKind:A.PROJECTION_KIND,
  source:profile.source,epoch,projectionEpoch:epoch,sampleAt,confidence:1,nativeWidth:384,nativeHeight:224,cameraX:0,
  worldXScale:1,xBias:80,floorYScale:1,zScale:-1,yBias:120,headClearanceNative:24,
  validationBounds:{minX:0,maxX:383,minY:0,maxY:223},...overrides
});
const db=(sampleAt=1000,epoch=E,overrides={})=>({
  width:768,height:448,contentRect:{x:0,y:0,width:768,height:448},sampleAt,confidence:1,epoch,projectionEpoch:epoch,
  mappingVersion:'768:448:0:0:768:448',fullscreen:false,...overrides
});
const player=(x=100,y=50,z=0,sampleAt=1000,epoch=E,present=true,overrides={})=>({
  present,x,y,z,sampleAt,confidence:1,epoch,projectionEpoch:epoch,...overrides
});
const warning=(target='P1',slot=0)=>({target,slot,ruleId:'QA_V2',target7E:target==='P1'?0:target==='P2'?4:8,attack:5440});
const build=(warnings,players,{proj=projection(),drawing=db(),now=1010,warningSampleAt=1000,warningEpoch=E,omitWarningSampleAt=false}={})=>{
  const args={warnings,players,projection:proj,drawingBufferState:drawing,nowMs:now,warningEpoch};
  if(!omitWarningSampleAt)args.warningSampleAt=warningSampleAt;
  return A.buildPlan(args);
};
const oneFixed=(p,reason)=>{assert.equal(p.anchored.length,0);assert.equal(p.fixed.length,1);assert.equal(p.fixed[0].reason,reason);};
const oneAnchored=p=>{assert.equal(p.anchored.length,1);assert.equal(p.fixed.length,0);return p.anchored[0];};
const center=item=>[item.drawRectDb.x+item.drawRectDb.width/2,item.drawRectDb.y+item.drawRectDb.height/2];

let passed=0;
const cases=[];
const test=(name,fn)=>{cases.push(name);fn();passed++;};

// strict warningSampleAt fail-closed matrix, independent from implementation regression.
test('missing warningSampleAt',()=>oneFixed(build([warning()],{P1:player()},{omitWarningSampleAt:true}),'INVALID_WARNING_SAMPLE_TIME'));
for(const [name,value] of [
  ['null',null],['numeric string','1000'],['boxed number',new Number(1000)],['valueOf object',{valueOf(){return 1000;}}],
  ['toString object',{toString(){return '1000';}}],['empty array',[]],['numeric array',[1000]],['false',false],['true',true],
  ['NaN',NaN],['Infinity',Infinity],['-Infinity',-Infinity],['Date',new Date(1000)],['bigint',1000n],['function',()=>1000]
]) test('invalid warningSampleAt '+name,()=>oneFixed(build([warning()],{P1:player()},{warningSampleAt:value}),'INVALID_WARNING_SAMPLE_TIME'));

test('invalid warningSampleAt resolveAnchor has null coordinates',()=>{
  const a=A.resolveAnchor({player:'P1',playerState:player(),projection:projection(),drawingBufferState:db(),nowMs:1010,warningEpoch:E,warningSampleAt:null});
  assert.equal(a.ok,false);assert.equal(a.reason,'INVALID_WARNING_SAMPLE_TIME');assert.equal(a.xDb,null);assert.equal(a.yDb,null);assert.equal(a.bodyXDb,null);assert.equal(a.bodyYDb,null);
});
test('invalid warningSampleAt not repaired by newer player projection',()=>{
  const p=build([warning('P2')],{P2:player(180,50,0,1100)},{proj:projection(1100),drawing:db(1100),now:1110,warningSampleAt:'1050'});
  oneFixed(p,'INVALID_WARNING_SAMPLE_TIME');
});
test('valid primitive finite preserves anchor',()=>oneAnchored(build([warning()],{P1:player(100,50,0,1010)},{proj:projection(1010),drawing:db(1010),now:1020,warningSampleAt:1010})));
test('valid primitive finite zero accepted',()=>oneAnchored(build([warning()],{P1:player(100,50,0,0)},{proj:projection(0),drawing:db(0),now:10,warningSampleAt:0})));

test('old player sample blocked after retarget',()=>oneFixed(build([warning('P2')],{P2:player(180,50,0,1000)},{proj:projection(1010),drawing:db(1010),now:1020,warningSampleAt:1010}),'SPATIAL_BEFORE_WARNING_SAMPLE'));
test('old projection sample blocked after retarget',()=>oneFixed(build([warning('P2')],{P2:player(180,50,0,1010)},{proj:projection(1000),drawing:db(1010),now:1020,warningSampleAt:1010}),'PROJECTION_BEFORE_WARNING_SAMPLE'));
test('P1 P2 P3 retarget requires current samples',()=>{
  oneAnchored(build([warning('P1')],{P1:player(80,50,0,1000)},{proj:projection(1000),drawing:db(1000),now:1010,warningSampleAt:1000}));
  oneFixed(build([warning('P2')],{P2:player(160,50,0,1000)},{proj:projection(1000),drawing:db(1010),now:1020,warningSampleAt:1010}),'SPATIAL_BEFORE_WARNING_SAMPLE');
  oneAnchored(build([warning('P2')],{P2:player(160,50,0,1010)},{proj:projection(1010),drawing:db(1010),now:1020,warningSampleAt:1010}));
  oneFixed(build([warning('P3')],{P3:player(240,50,0,1010)},{proj:projection(1010),drawing:db(1020),now:1030,warningSampleAt:1020}),'SPATIAL_BEFORE_WARNING_SAMPLE');
  oneAnchored(build([warning('P3')],{P3:player(240,50,0,1020)},{proj:projection(1020),drawing:db(1020),now:1030,warningSampleAt:1020}));
});
test('simultaneous P1 P2 P3 no cross-player spatial leak',()=>{
  const p=build([warning('P1'),warning('P2'),warning('P3')],{P1:player(80,40),P2:player(140,50),P3:player(200,60)});
  assert.deepEqual(p.anchored.map(x=>x.player),['P1','P2','P3']);
  assert.notEqual(center(p.anchored[0])[0],center(p.anchored[1])[0]);
  assert.notEqual(center(p.anchored[1])[0],center(p.anchored[2])[0]);
});

test('death absent fails closed',()=>oneFixed(build([warning()],{P1:player(80,50,0,1000,E,false)}),'PLAYER_ABSENT'));
test('disappearance missing state fails closed',()=>oneFixed(build([warning()],{}),'PLAYER_ABSENT'));
test('respawn fresh coordinate does not retain old anchor',()=>{
  const a=oneAnchored(build([warning()],{P1:player(80)}));
  oneFixed(build([warning()],{P1:player(80,50,0,1000,E,false)}),'PLAYER_ABSENT');
  const b=oneAnchored(build([warning()],{P1:player(180)}));
  assert.notEqual(center(a)[0],center(b)[0]);assert.equal(center(b)[0],520);
});
test('same-slot replacement uses only new object coordinates',()=>{
  const old=oneAnchored(build([warning()],{P1:player(70)}));
  const replacement=oneAnchored(build([warning()],{P1:player(170,50,0,1001)},{proj:projection(1001),drawing:db(1001),now:1010,warningSampleAt:1001}));
  assert.notEqual(center(old)[0],center(replacement)[0]);
});

test('player freshness exactly 80ms accepted',()=>oneAnchored(build([warning()],{P1:player(100,50,0,930)},{proj:projection(930),drawing:db(1000),now:1010,warningSampleAt:900})));
test('player freshness over 80ms fails',()=>oneFixed(build([warning()],{P1:player(100,50,0,929)},{proj:projection(930),drawing:db(1000),now:1010,warningSampleAt:900}),'STALE_PLAYER'));
test('projection freshness exactly 80ms accepted',()=>oneAnchored(build([warning()],{P1:player(100,50,0,930)},{proj:projection(930),drawing:db(1000),now:1010,warningSampleAt:900})));
test('projection freshness over 80ms fails',()=>oneFixed(build([warning()],{P1:player(100,50,0,930)},{proj:projection(929),drawing:db(1000),now:1010,warningSampleAt:900}),'STALE_PROJECTION'));
test('semantic heartbeat cannot refresh spatial authority',()=>oneFixed(build([warning('P2')],{P2:player(180,50,0,1000)},{proj:projection(1000),drawing:db(1070),now:1070,warningSampleAt:1060}),'SPATIAL_BEFORE_WARNING_SAMPLE'));

for(const [name,mutate] of [
  ['missing warning epoch',({args})=>{args.warningEpoch=undefined;}],
  ['malformed warning epoch',({args})=>{args.warningEpoch='runtime-a';}],
  ['coercible warning epoch',({args})=>{args.warningEpoch={toString(){return E;}};}],
  ['player missing epoch',({players})=>{delete players.P1.epoch;}],
  ['player malformed epoch',({players})=>{players.P1.epoch='runtime-a';}],
  ['player coercible epoch',({players})=>{players.P1.epoch={toString(){return E;}};}],
  ['player epoch mismatch',({players})=>{players.P1.epoch=E2;}],
  ['player projectionEpoch mismatch',({players})=>{players.P1.projectionEpoch=E2;}],
  ['projection missing epoch',({proj})=>{delete proj.epoch;}],
  ['projection malformed epoch',({proj})=>{proj.epoch='runtime-a';}],
  ['projection coercible epoch',({proj})=>{proj.epoch={toString(){return E;}};}],
  ['projection epoch mismatch',({proj})=>{proj.epoch=E2;}],
  ['projection projectionEpoch mismatch',({proj})=>{proj.projectionEpoch=E2;}],
  ['drawing epoch mismatch',({drawing})=>{drawing.epoch=E2;}],
  ['drawing projectionEpoch mismatch',({drawing})=>{drawing.projectionEpoch=E2;}],
  ['drawing missing epoch',({drawing})=>{delete drawing.epoch;}],
  ['drawing coercible epoch',({drawing})=>{drawing.epoch={toString(){return E;}};}]
]) test('epoch strict '+name,()=>{
  const players={P1:player()},proj=projection(),drawing=db(),args={warningEpoch:E};mutate({players,proj,drawing,args});
  const p=A.buildPlan({warnings:[warning()],players,projection:proj,drawingBufferState:drawing,nowMs:1010,warningSampleAt:1000,warningEpoch:args.warningEpoch});
  oneFixed(p,name.includes('mismatch')?'EPOCH_MISMATCH':'INVALID_EPOCH');
});

for(const [name,players,proj,drawing,expected] of [
  ['player confidence NaN',{P1:player(100,50,0,1000,E,true,{confidence:NaN})},projection(),db(),'INVALID_PLAYER_CONFIDENCE'],
  ['player confidence string',{P1:player(100,50,0,1000,E,true,{confidence:'1'})},projection(),db(),'INVALID_PLAYER_CONFIDENCE'],
  ['projection confidence NaN',{P1:player()},projection(1000,E,{confidence:NaN}),db(),'INVALID_PROJECTION_CONFIDENCE'],
  ['projection confidence string',{P1:player()},projection(1000,E,{confidence:'1'}),db(),'INVALID_PROJECTION_CONFIDENCE'],
  ['db confidence null',{P1:player()},projection(),db(1000,E,{confidence:null}),'INVALID_DRAWING_BUFFER_CONFIDENCE'],
  ['db confidence >1',{P1:player()},projection(),db(1000,E,{confidence:1.01}),'INVALID_DRAWING_BUFFER_CONFIDENCE']
]) test(name,()=>oneFixed(build([warning()],players,{proj,drawing}),expected));

for(const [name,ps,pr,expected] of [
  ['player x NaN',player(NaN),projection(),'INVALID_PLAYER_XYZ'],
  ['player y Infinity',player(100,Infinity),projection(),'INVALID_PLAYER_XYZ'],
  ['player z -Infinity',player(100,50,-Infinity),projection(),'INVALID_PLAYER_XYZ'],
  ['projection camera nonfinite',player(),projection(1000,E,{cameraX:NaN}),'INVALID_PROJECTION_STATE'],
  ['projection scale nonfinite',player(),projection(1000,E,{worldXScale:Infinity}),'INVALID_PROJECTION_STATE']
]) test(name,()=>oneFixed(build([warning()],{P1:ps},{proj:pr}),expected));

test('body out of bounds fails closed',()=>oneFixed(build([warning()],{P1:player(360)}),'PROJECTION_OUT_OF_BOUNDS'));
test('anchor offscreen fails closed',()=>oneFixed(build([warning()],{P1:player(-81)}),'PROJECTION_OUT_OF_BOUNDS'));
test('left edge draw rect clamps inside content',()=>{
  const p=oneAnchored(build([warning()],{P1:player(-70,50)}));assert.equal(p.drawRectDb.x,0);
});
test('right edge draw rect clamps inside content',()=>{
  const p=oneAnchored(build([warning()],{P1:player(300,50)}));assert.equal(p.drawRectDb.x,684);
});
test('invalid content rect fails closed',()=>oneFixed(build([warning()],{P1:player()},{drawing:db(1000,E,{contentRect:{x:-1,y:0,width:768,height:448}})}),'INVALID_DRAWING_BUFFER'));
test('stale drawing buffer fails closed',()=>oneFixed(build([warning()],{P1:player(100,50,0,1000)},{drawing:db(700),now:1010,warningSampleAt:900}),'STALE_DRAWING_BUFFER'));

test('resize remaps current coordinate',()=>{
  const a=oneAnchored(build([warning()],{P1:player(100)}));
  const d=db(1000,E,{width:1536,height:896,contentRect:{x:0,y:0,width:1536,height:896},mappingVersion:'1536:896:0:0:1536:896'});
  const b=oneAnchored(build([warning()],{P1:player(100)},{drawing:d}));
  assert.equal(b.anchor.xDb,a.anchor.xDb*2);assert.equal(b.anchor.yDb,a.anchor.yDb*2);assert.notEqual(a.anchor.mappingKey,b.anchor.mappingKey);
});
test('fullscreen remap changes mapping key',()=>{
  const a=oneAnchored(build([warning()],{P1:player()}));
  const b=oneAnchored(build([warning()],{P1:player()},{drawing:db(1000,E,{fullscreen:true})}));
  assert.match(a.anchor.mappingKey,/:win:/);assert.match(b.anchor.mappingKey,/:fs:/);
});
test('DPR-like drawing-buffer scale remaps without stale coordinate reuse',()=>{
  const d=db(1000,E,{width:1152,height:672,contentRect:{x:192,y:0,width:768,height:672},mappingVersion:'1152:672:192:0:768:672'});
  const p=oneAnchored(build([warning()],{P1:player(100)},{drawing:d}));
  assert.equal(p.anchor.xDb,552);assert.equal(p.anchor.yDb,438);
});

test('invalid target string fixed only',()=>oneFixed(build([{...warning(),target:'1P'}],{P1:player()}),'INVALID_TARGET'));
test('fixed fallback retains warning payload',()=>{
  const w=warning('P1',7);const p=build([w],{P1:player()},{warningSampleAt:null});oneFixed(p,'INVALID_WARNING_SAMPLE_TIME');assert.equal(p.fixed[0].warning,w);
});
test('no hold no smoothing contract',()=>{
  const p=build([warning()],{P1:player()});assert.equal(p.holdMs,0);assert.equal(p.smoothing,false);assert.equal(p.maxPlayerAgeMs,80);assert.equal(p.maxProjectionAgeMs,80);
});
test('production projection remains unproved disabled',()=>{
  const raw=JSON.parse(fs.readFileSync(new URL('../../product/alpha/wof_alpha_player_head_projection.json',import.meta.url),'utf8'));
  assert.equal(raw.status,'UNPROVED');assert.equal(raw.activation,'DISABLED_UNTIL_BOUNDED_BROWSER_WOF_PROOF');
  const v=A.validateProofProfile(raw);assert.equal(v.ok,false);assert.equal(v.reasons.includes('PROFILE_NOT_PROVED'),true);
});

console.log(JSON.stringify({status:'PASS',passed,total:cases.length,fixture:'FRESH_INDEPENDENT_PLAYER_HEAD_WARNING_QA_V2_REPOSITORY_ONLY_NOT_BROWSER_WOF_PROOF',cases},null,2));
