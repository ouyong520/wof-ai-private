import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const M=require('./wof_alpha_screen_space_map.js');
const Enemy=require('./wof_alpha_enemy_target_labels.js');
const Player=require('./wof_alpha_player_head_warning.js');

let passed=0;
const test=(name,fn)=>{fn();passed++;};
const E='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa';
const state=(extra={})=>M.stateFromViewport({
  width:768,height:448,viewport:[0,0,768,448],sampleAt:1000,confidence:1,
  epoch:E,projectionEpoch:E,mappingVersion:'768:448:0:0:768:448',fullscreen:false,...extra
});

test('webgl bottom-left viewport converts to top-left drawing-buffer rect exactly once',()=>{
  const r=M.stateFromViewport({width:1000,height:800,viewport:[100,50,600,400],sampleAt:1,confidence:1});
  assert.equal(r.ok,true);
  assert.deepEqual(r.state.contentRect,{x:100,y:350,width:600,height:400});
  assert.deepEqual(r.state.viewport,{x:100,y:50,width:600,height:400,top:350,origin:'webgl-bottom-left'});
});

test('native 384x224 maps linearly into current WebGL content rect with top-left screen Y',()=>{
  const r=M.stateFromViewport({width:1000,height:800,viewport:[100,50,600,400],sampleAt:1,confidence:1}).state;
  const topLeft=M.mapNativePoint({xNative:0,yNative:0,drawingBufferState:r});
  const center=M.mapNativePoint({xNative:192,yNative:112,drawingBufferState:r});
  const bottomRight=M.mapNativePoint({xNative:384,yNative:224,drawingBufferState:r});
  assert.deepEqual([topLeft.xDb,topLeft.yDb],[100,350]);
  assert.deepEqual([center.xDb,center.yDb],[400,550]);
  assert.deepEqual([bottomRight.xDb,bottomRight.yDb],[700,750]);
});

test('increasing native Y moves downward on screen and is not flipped a second time',()=>{
  const r=state().state;
  const a=M.mapNativePoint({xNative:100,yNative:40,drawingBufferState:r});
  const b=M.mapNativePoint({xNative:100,yNative:80,drawingBufferState:r});
  assert.equal(b.yDb-a.yDb,80);
});

test('resize and fullscreen remap from live drawing-buffer viewport without CSS or DPR constants',()=>{
  const a=state().state;
  const b=state({width:1152,height:672,viewport:[192,0,768,672],mappingVersion:'1152:672:192:0:768:672',fullscreen:true}).state;
  const pa=M.mapNativePoint({xNative:192,yNative:112,drawingBufferState:a});
  const pb=M.mapNativePoint({xNative:192,yNative:112,drawingBufferState:b});
  assert.deepEqual([pa.xDb,pa.yDb],[384,224]);
  assert.deepEqual([pb.xDb,pb.yDb],[576,336]);
  assert.notEqual(M.mappingKeyOf(a,'v'),M.mappingKeyOf(b,'v'));
  assert.equal(M.mappingKeyOf(b,'v').includes(':fs:'),true);
});

test('letterbox viewport top is recomputed from current buffer height after resize',()=>{
  const a=M.stateFromViewport({width:900,height:600,viewport:[50,80,800,400],sampleAt:1,confidence:1}).state;
  const b=M.stateFromViewport({width:900,height:700,viewport:[50,80,800,400],sampleAt:2,confidence:1}).state;
  assert.equal(a.contentRect.y,120);
  assert.equal(b.contentRect.y,220);
});

test('invalid or lost viewport fails closed and recovery has no cached coordinate',()=>{
  assert.equal(M.stateFromViewport({width:768,height:448,viewport:[0,0,0,448],sampleAt:1,confidence:1}).ok,false);
  assert.equal(M.stateFromViewport({width:768,height:448,viewport:[0,-1,768,448],sampleAt:1,confidence:1}).ok,false);
  assert.equal(M.mapNativePoint({xNative:100,yNative:50,drawingBufferState:null}).ok,false);
  const recovered=state({sampleAt:2}).state;
  const p=M.mapNativePoint({xNative:100,yNative:50,drawingBufferState:recovered});
  assert.equal(p.ok,true);
  assert.deepEqual([p.xDb,p.yDb],[200,100]);
});

test('enemy geometry v2 and player consumer land identical native anchors at identical drawing-buffer coordinates',()=>{
  const db=state().state;
  const enemyProjection={
    schema:Enemy.PROJECTION_SCHEMA,verdict:Enemy.PROJECTION_VERDICT,projectionKind:Enemy.PROJECTION_KIND,proofId:'shared-map-synthetic',romSha256:Enemy.SUPPORTED_ROM_SHA,
    nativeWidth:384,nativeHeight:224,cameraAddress:0xFF1000,cameraRead:'u16be',cameraSign:1,cameraScale:1,xBias:0,
    yAxisSign:1,yModel:'Y',yBias:0,enemyHeadClearanceByType:{18:23},epoch:E,sampleAt:1000,confidence:1,cameraRaw:0,cameraX:0
  };
  const enemyPlan=Enemy.buildPlan({markers:[{slot:0,sourceId:'enemy-slot-0',type:18,target7E:0,target:'P1',enemyX:123,enemyY:100,enemyZ:0,
    sampleAt:1000,confidence:1,epoch:E,projectionEpoch:E}],projection:enemyProjection,drawingBufferState:db,nowMs:1010});
  assert.equal(enemyPlan.labels.length,1);
  assert.equal(enemyPlan.labels[0].bodyYNative,100);
  assert.equal(enemyPlan.labels[0].headClearanceNative,23);
  const playerProjection={
    schema:Player.PROFILE_SCHEMA,status:'PROVED',proofId:'shared-map-synthetic',version:'shared-map-projection-v1',projectionKind:Player.PROJECTION_KIND,
    source:'SYNTHETIC_ONLY',epoch:E,projectionEpoch:E,sampleAt:1000,confidence:1,nativeWidth:384,nativeHeight:224,cameraX:0,
    worldXScale:1,xBias:0,floorYScale:1,zScale:0,yBias:0,headClearanceNative:23,validationBounds:{minX:0,maxX:383,minY:0,maxY:223}
  };
  const playerAnchor=Player.resolveAnchor({player:'P1',playerState:{present:true,x:123,y:100,z:0,sampleAt:1000,confidence:1,epoch:E,projectionEpoch:E},
    projection:playerProjection,drawingBufferState:db,nowMs:1010,warningEpoch:E,warningSampleAt:1000});
  assert.equal(playerAnchor.ok,true);
  assert.deepEqual(enemyPlan.labels[0].anchorDb,{x:playerAnchor.xDb,y:playerAnchor.yDb});
});

test('HUD captures one live WebGL drawing-buffer mapping and feeds it to both anchor paths',()=>{
  const hud=fs.readFileSync(new URL('./wof_alpha_hud.js',import.meta.url),'utf8');
  assert.match(hud,/const SCREEN_MAP=window\.WOFAlphaScreenSpaceMap/);
  assert.match(hud,/SCREEN_MAP\.stateFromViewport\(\{/);
  assert.match(hud,/const db=drawingBufferState\(now,projection\?\.epoch\|\|null\);[\s\S]*TARGET_LABELS\.buildPlan/);
  assert.match(hud,/const db=drawingBufferState\(now,projection\?\.epoch\|\|null\);[\s\S]*PLAYER_WARNING\.buildPlan/);
  assert.doesNotMatch(hud,/devicePixelRatio/);
});

test('loader establishes shared mapper before enemy/player HUD consumers',()=>{
  const loader=fs.readFileSync(new URL('./wof_alpha_loader.js',import.meta.url),'utf8');
  const shared=loader.indexOf("await load('wof_alpha_screen_space_map.js')");
  const enemy=loader.indexOf("await load('wof_alpha_enemy_target_labels.js')");
  const player=loader.indexOf("await load('wof_alpha_player_head_warning.js')");
  const hud=loader.indexOf("await load('wof_alpha_hud.js')");
  assert.ok(shared>=0&&enemy>shared&&player>shared&&hud>player);
});

console.log(JSON.stringify({schema:'wof-alpha-shared-screen-space-map-regression-v1',status:'PASS',passed,total:9,enemyGeometryVersion:Enemy.GEOMETRY_VERSION||null}));
