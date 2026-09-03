import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const R=require('./wof_alpha_relative_head_anchor.js');
const overlaySource=fs.readFileSync(new URL('./wof_alpha_relative_enemy_overlay.js',import.meta.url),'utf8');
let passed=0;const test=(name,fn)=>{fn();passed++;};

const fitY={ok:true,sign:1,model:'Y',preferredModel:'Y',offset:100};
const profileY={yAxisSign:1,yModel:'Y',yBias:120,enemyHeadClearanceByType:{18:20,20:28,31:16}};
const p1={x:100,y:50,z:0};
const p1Head={x:120,y:100};

test('Y/Y-Z/Y+Z and sign remain explicit, not guessed from draw output',()=>{
  const rows=[];for(const [y,z] of [[40,0],[50,0],[60,0],[60,8],[60,16],[55,8],[45,0]])rows.push({worldY:y,worldZ:z,headNativeY:(y-z)+70});
  const fit=R.fitVertical(rows,{minSamples:6,minYRange:5,minZRange:5,maxResidual:.01,minGap:.5});
  assert.equal(fit.ok,true);assert.equal(fit.sign,1);assert.equal(fit.model,'Y-Z');
  const reverse=rows.map(r=>({...r,headNativeY:210-(r.worldY-r.worldZ)}));
  const fitReverse=R.fitVertical(reverse,{minSamples:6,minYRange:5,minZRange:5,maxResidual:.01,minGap:.5});
  assert.equal(fitReverse.ok,true);assert.equal(fitReverse.sign,-1);assert.equal(fitReverse.model,'Y-Z');
});

test('horizontal enemy motion follows 1:1 and common camera/world scroll cancels through P1 reference',()=>{
  const a=R.projectEnemyRelative({enemy:{x:150,y:50,z:0},p1,p1HeadNative:p1Head,fit:fitY});
  const b=R.projectEnemyRelative({enemy:{x:170,y:50,z:0},p1,p1HeadNative:p1Head,fit:fitY});
  assert.equal(b.x-a.x,20);
  const scrolled=R.projectEnemyRelative({enemy:{x:190,y:50,z:0},p1:{x:140,y:50,z:0},p1HeadNative:p1Head,fit:fitY});
  assert.equal(scrolled.x,a.x);
});

test('depth response respects selected Y-Z/Y+Z model and top-origin sign',()=>{
  const minus={ok:true,sign:1,model:'Y-Z',preferredModel:'Y-Z',offset:100};
  const plus={ok:true,sign:1,model:'Y+Z',preferredModel:'Y+Z',offset:100};
  const ground=R.projectEnemyRelative({enemy:{x:120,y:60,z:0},p1,p1HeadNative:p1Head,fit:minus});
  const jumpMinus=R.projectEnemyRelative({enemy:{x:120,y:60,z:12},p1,p1HeadNative:p1Head,fit:minus});
  const jumpPlus=R.projectEnemyRelative({enemy:{x:120,y:60,z:12},p1,p1HeadNative:p1Head,fit:plus});
  assert.equal(jumpMinus.y,ground.y-12);assert.equal(jumpPlus.y,ground.y+12);
});

test('per-type clearance is applied relative to P1 head baseline, including smaller and taller enemy types',()=>{
  const t18=R.projectEnemyHead({enemy:{type:18,x:120,y:60,z:0},p1,p1HeadNative:p1Head,fit:fitY,profile:profileY});
  const t20=R.projectEnemyHead({enemy:{type:20,x:120,y:60,z:0},p1,p1HeadNative:p1Head,fit:fitY,profile:profileY});
  const t31=R.projectEnemyHead({enemy:{type:31,x:120,y:60,z:0},p1,p1HeadNative:p1Head,fit:fitY,profile:profileY});
  assert.equal(t18.referenceClearanceNative,20);assert.equal(t18.extraClearanceNative,0);
  assert.equal(t20.extraClearanceNative,8);assert.equal(t20.y,t18.y-8);
  assert.equal(t31.extraClearanceNative,-4);assert.equal(t31.y,t18.y+4);
});

test('unknown enemy type or incompatible clearance profile fails closed instead of reverting to zero clearance',()=>{
  assert.equal(R.projectEnemyHead({enemy:{type:46,x:120,y:60,z:0},p1,p1HeadNative:p1Head,fit:fitY,profile:profileY}).reason,'UNSUPPORTED_ENEMY_TYPE');
  assert.equal(R.projectEnemyHead({enemy:{type:18,x:120,y:60,z:0},p1,p1HeadNative:p1Head,fit:fitY,profile:{...profileY,yAxisSign:-1}}).reason,'CLEARANCE_PROFILE_SIGN_MISMATCH');
  assert.equal(R.projectEnemyHead({enemy:{type:18,x:120,y:60,z:0},p1,p1HeadNative:p1Head,fit:fitY,profile:{...profileY,yModel:'Y-Z'}}).reason,'CLEARANCE_PROFILE_Y_MODEL_MISMATCH');
});

test('drawing-buffer viewport and CSS remap survive resize and letterbox',()=>{
  const db={width:800,height:488,contentRect:{x:16,y:20,width:768,height:448}};
  const native=R.nativeFromCss({x:400,y:244,cssWidth:800,cssHeight:488,drawingBufferState:db});
  assert.ok(Math.abs(native.x-192)<1e-9);assert.ok(Math.abs(native.y-112)<1e-9);
  const q=R.nativeToDb({ok:true,x:192,y:112},db);assert.deepEqual(q,{x:400,y:244});
  assert.deepEqual(R.dbToCss(q,db,1600,976),{x:800,y:488});
});

test('freshness policy hides stale enemy samples and permits fresh recovery',()=>{
  assert.equal(R.isFreshSample(1000,1200,350),true);
  assert.equal(R.isFreshSample(1000,1400,350),false);
  assert.equal(R.isFreshSample(1450,1400,350),true);
  assert.equal(R.isFreshSample(1451,1400,350),false);
});

test('production enemy stage stays neutral, clearance-profile gated, and never treats drawCount as position PASS',()=>{
  assert.match(overlaySource,/mode:'HEAD_ANCHOR_MARKER'/);
  assert.match(overlaySource,/projectEnemyHead/);
  assert.doesNotMatch(overlaySource,/extraClearanceNative:0/);
  assert.match(overlaySource,/ENEMY_HEAD_CLEARANCE_PROFILE_MISSING/);
  assert.match(overlaySource,/now-lastMarkerRx>MARKER_STALE_MS/);
  assert.match(overlaySource,/now-lastPlayerRx>PLAYER_STALE_MS/);
  assert.match(overlaySource,/now-p1TrackerRx>TRACKER_STALE_MS/);
  assert.match(overlaySource,/ctx\.clearRect\(0,0,view\.rect\.width,view\.rect\.height\)/);
  assert.match(overlaySource,/drawCountIsPositionProof:false/);
  assert.match(overlaySource,/positionPass:false/);
  assert.match(overlaySource,/liveGeometryConfirmed:false/);
  assert.doesNotMatch(overlaySource,/function drawLabel\(/);
});

test('stale authority clears geometry and fresh actor/projection paths can recover automatically',()=>{
  assert.match(overlaySource,/clearGeometryProfile\('RUNTIME_DIAG'\)/);
  assert.match(overlaySource,/clearGeometryProfile\('TRACKER_AUTHORITY_REVOKED'\)/);
  assert.match(overlaySource,/if\(snapshot\.projection\)rememberGeometryProfile/);
  assert.match(overlaySource,/if\(m\.projection\)rememberGeometryProfile/);
  assert.match(overlaySource,/inputSource='DIRECT_EXACT_RUNTIME_ACTORS'/);
});

console.log(JSON.stringify({status:'PASS',passed,total:passed,fixture:'FOCUSED_ENEMY_NEUTRAL_HEAD_ANCHOR_SYNTHETIC_NOT_LIVE_WOF'}));