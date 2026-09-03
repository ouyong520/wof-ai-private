import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const R=require('./wof_alpha_relative_head_anchor.js');

const overlaySource=fs.readFileSync(new URL('./wof_alpha_relative_enemy_overlay.js',import.meta.url),'utf8');
const hudSource=fs.readFileSync(new URL('./wof_alpha_hud.js',import.meta.url),'utf8');
const captureWorkerSource=fs.readFileSync(new URL('../../parallel/RENDER_AUTHORITY_V2/wof_render_authority_capture_worker.js',import.meta.url),'utf8');
const capturePySource=fs.readFileSync(new URL('../../parallel/PYLAUNCH/wof_launcher/render_authority_capture.py',import.meta.url),'utf8');
const productionOverlayPy=fs.readFileSync(new URL('../../parallel/PYLAUNCH/wof_launcher/production_p1_overlay.py',import.meta.url),'utf8');

const db={width:768,height:448,contentRect:{x:0,y:0,width:768,height:448}};
let passed=0;const test=(name,fn)=>{fn();passed++;};

test('css tracker point maps through current drawing buffer to native raster',()=>{
  const p=R.nativeFromCss({x:384,y:224,cssWidth:768,cssHeight:448,drawingBufferState:db});
  assert.equal(p.x,192);assert.equal(p.y,112);
  const letter={width:800,height:488,contentRect:{x:16,y:20,width:768,height:448}};
  const q=R.nativeFromCss({x:400,y:244,cssWidth:800,cssHeight:488,drawingBufferState:letter});
  assert.ok(Math.abs(q.x-192)<1e-9);assert.ok(Math.abs(q.y-112)<1e-9);
});

test('normal movement plus jump resolves Y-Z and positive top-origin sign',()=>{
  const rows=[];
  for(const [y,z] of [[40,0],[50,0],[60,0],[60,8],[60,16],[55,8],[45,0]])rows.push({worldY:y,worldZ:z,headNativeY:(y-z)+70});
  const fit=R.fitVertical(rows,{minSamples:6,minYRange:5,minZRange:5,maxResidual:.01,minGap:.5});
  assert.equal(fit.ok,true);assert.equal(fit.sign,1);assert.equal(fit.model,'Y-Z');assert.ok(fit.residual<1e-9);
});

test('Y+Z is selected when jump/depth evidence demands it',()=>{
  const rows=[];
  for(const [y,z] of [[35,0],[45,0],[55,0],[55,7],[55,14],[48,7],[38,0]])rows.push({worldY:y,worldZ:z,headNativeY:150-(y+z)});
  const fit=R.fitVertical(rows,{minSamples:6,minYRange:5,minZRange:5,maxResidual:.01,minGap:.5});
  assert.equal(fit.ok,true);assert.equal(fit.sign,-1);assert.equal(fit.model,'Y+Z');
});

test('reversed screen direction is represented only by y-axis sign',()=>{
  const rows=[];
  for(const [y,z] of [[40,0],[50,0],[60,0],[60,8],[60,16],[50,8],[40,0]])rows.push({worldY:y,worldZ:z,headNativeY:160-(y-z)});
  const fit=R.fitVertical(rows,{minSamples:6,minYRange:5,minZRange:5,maxResidual:.01,minGap:.5});
  assert.equal(fit.ok,true);assert.equal(fit.sign,-1);assert.equal(fit.model,'Y-Z');
});

test('without Z separation sign may lock but model stays unresolved',()=>{
  const rows=[40,45,50,55,60,65].map(y=>({worldY:y,worldZ:0,headNativeY:y+70}));
  const fit=R.fitVertical(rows,{minSamples:6,minYRange:5,minZRange:5,maxResidual:.01,minGap:.5});
  assert.equal(fit.ok,true);assert.equal(fit.sign,1);assert.equal(fit.model,null);assert.equal(fit.reason,'SIGN_ONLY_Z_NOT_SEPARATED');
});

test('horizontal movement follows enemy while camera/world scroll cancels through P1 reference',()=>{
  const fit={ok:true,sign:1,model:'Y-Z',preferredModel:'Y-Z'};
  const base=R.projectEnemyRelative({enemy:{x:150,y:70,z:0},p1:{x:100,y:50,z:0},p1HeadNative:{x:120,y:100},fit});
  const enemyMoved=R.projectEnemyRelative({enemy:{x:170,y:70,z:0},p1:{x:100,y:50,z:0},p1HeadNative:{x:120,y:100},fit});
  assert.equal(enemyMoved.x-base.x,20);
  const scrolled=R.projectEnemyRelative({enemy:{x:190,y:70,z:0},p1:{x:140,y:50,z:0},p1HeadNative:{x:120,y:100},fit});
  assert.deepEqual({x:scrolled.x,y:scrolled.y},{x:base.x,y:base.y});
});

test('depth movement follows selected sign without mirrored response',()=>{
  const plus={ok:true,sign:1,model:'Y',preferredModel:'Y'};
  const a=R.projectEnemyRelative({enemy:{x:120,y:50,z:0},p1:{x:100,y:50,z:0},p1HeadNative:{x:100,y:90},fit:plus});
  const b=R.projectEnemyRelative({enemy:{x:120,y:70,z:0},p1:{x:100,y:50,z:0},p1HeadNative:{x:100,y:90},fit:plus});
  assert.equal(b.y-a.y,20);
  const minus={...plus,sign:-1};
  const c=R.projectEnemyRelative({enemy:{x:120,y:70,z:0},p1:{x:100,y:50,z:0},p1HeadNative:{x:100,y:90},fit:minus});
  assert.equal(c.y-a.y,-20);
});

test('jump Z correction moves anchor in the selected Y-Z direction and returns on landing',()=>{
  const fit={ok:true,sign:1,model:'Y-Z',preferredModel:'Y-Z'};
  const ys=[0,8,16,8,0].map(z=>R.projectEnemyRelative({enemy:{x:120,y:60,z},p1:{x:100,y:50,z:0},p1HeadNative:{x:100,y:100},fit}).y);
  assert.deepEqual(ys,[110,102,94,102,110]);
});

test('extra per-type clearance moves only anchor upward',()=>{
  const fit={ok:true,sign:1,model:'Y',preferredModel:'Y'};
  const a=R.projectEnemyRelative({enemy:{x:120,y:60,z:0},p1:{x:100,y:50,z:0},p1HeadNative:{x:100,y:90},fit,extraClearanceNative:0});
  const b=R.projectEnemyRelative({enemy:{x:120,y:60,z:0},p1:{x:100,y:50,z:0},p1HeadNative:{x:100,y:90},fit,extraClearanceNative:12});
  assert.equal(a.x,b.x);assert.equal(b.y,a.y-12);
});

test('unresolved Z model suppresses mismatched airborne depth',()=>{
  const fit={ok:true,sign:1,model:null,preferredModel:'Y-Z'};
  const bad=R.projectEnemyRelative({enemy:{x:120,y:60,z:10},p1:{x:100,y:50,z:0},p1HeadNative:{x:100,y:90},fit});
  assert.equal(bad.ok,false);assert.equal(bad.reason,'Z_MODEL_UNRESOLVED');
  const ground=R.projectEnemyRelative({enemy:{x:120,y:60,z:0},p1:{x:100,y:50,z:0},p1HeadNative:{x:100,y:90},fit});
  assert.equal(ground.ok,true);
});

test('native projection remaps after resize/fullscreen/letterbox without frozen DPR',()=>{
  const point={ok:true,x:192,y:112};
  assert.deepEqual(R.nativeToDb(point,db),{x:384,y:224});
  const resized={width:800,height:488,contentRect:{x:16,y:20,width:768,height:448}};
  assert.deepEqual(R.nativeToDb(point,resized),{x:400,y:244});
  const rect=R.labelRect({x:400,y:244},resized,30,18);assert.deepEqual(rect,{x:385,y:235,width:30,height:18});
});

test('maintained HUD consumes direct P1 screen tracker and hides stale/lost authority',()=>{
  assert.match(hudSource,/function drawP1Tracker\(now\)/);
  assert.match(hudSource,/p1TrackerStatus\(now\)/);
  assert.match(hudSource,/now-p1TrackerRx<=P1_TRACKER_STALE_MS/);
  assert.match(hudSource,/drawLabelPlan\(\{labels:\[\{label:'1P'/);
  assert.match(productionOverlayPy,/visual\.get\("state"\) == "HEAD_TRACKING"/);
  assert.match(productionOverlayPy,/visual\.get\("lostFrames"\)/);
  assert.match(productionOverlayPy,/h\.clearP1HeadTracker/);
});

test('enemy geometry stage uses neutral marker, fresh-only data, and immediate clear on every frame',()=>{
  assert.match(overlaySource,/mode:'HEAD_ANCHOR_MARKER'/);
  assert.match(overlaySource,/function drawMarker\(x,y\)/);
  assert.doesNotMatch(overlaySource,/function drawLabel\(/);
  assert.match(overlaySource,/ctx\.clearRect\(0,0,view\.rect\.width,view\.rect\.height\)/);
  assert.match(overlaySource,/now-lastMarkerRx>MARKER_STALE_MS/);
  assert.match(overlaySource,/now-lastPlayerRx>PLAYER_STALE_MS/);
  assert.match(overlaySource,/now-p1TrackerRx>TRACKER_STALE_MS/);
  assert.match(overlaySource,/clearFit\('TRACKER_AUTHORITY_REVOKED'\)/);
  assert.match(overlaySource,/inputSource='DIRECT_EXACT_RUNTIME_ACTORS'/);
});

test('exact-runtime actor feed remains live after bounded capture instead of auto-packaging stop',()=>{
  assert.match(captureWorkerSource,/continuousActorFeed=binding\.continuousActorFeed===true/);
  assert.match(captureWorkerSource,/state\.state='ANCHOR_STREAMING'/);
  assert.match(captureWorkerSource,/actors:state\.currentActors/);
  assert.match(capturePySource,/"continuousActorFeed":True/);
  assert.match(capturePySource,/ingestActorSnapshot/);
  assert.match(capturePySource,/"ANCHOR_STREAMING"/);
});

test('read-only safety remains explicit across the dual-anchor production path',()=>{
  for(const src of [overlaySource,captureWorkerSource,capturePySource,productionOverlayPy]){
    assert.match(src,/readOnly/);assert.match(src,/ramWrites/);assert.match(src,/inputInjection/);
  }
  assert.doesNotMatch(captureWorkerSource,/HEAPU8\s*\[[^\]]+\]\s*=/);
});

console.log(JSON.stringify({status:'PASS',passed,total:passed,fixture:'FOCUSED_DUAL_HEAD_ANCHOR_GEOMETRY_AND_PRODUCTION_CONTRACT_NOT_LIVE_WOF'}));
