import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const R=require('./wof_alpha_relative_head_anchor.js');

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
  for(const [y,z] of [[40,0],[50,0],[60,0],[60,8],[60,16],[55,8],[45,0]]){
    rows.push({worldY:y,worldZ:z,headNativeY:(y-z)+70});
  }
  const fit=R.fitVertical(rows,{minSamples:6,minYRange:5,minZRange:5,maxResidual:.01,minGap:.5});
  assert.equal(fit.ok,true);assert.equal(fit.sign,1);assert.equal(fit.model,'Y-Z');assert.ok(fit.residual<1e-9);
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

test('relative enemy projection cancels camera and absolute bias',()=>{
  const fit={ok:true,sign:1,model:'Y-Z',preferredModel:'Y-Z'};
  const p=R.projectEnemyRelative({enemy:{x:150,y:70,z:0},p1:{x:100,y:50,z:0},p1HeadNative:{x:120,y:100},fit});
  assert.deepEqual({x:p.x,y:p.y},{x:170,y:120});
  const pScrolled=R.projectEnemyRelative({enemy:{x:190,y:70,z:0},p1:{x:140,y:50,z:0},p1HeadNative:{x:120,y:100},fit});
  assert.deepEqual({x:pScrolled.x,y:pScrolled.y},{x:170,y:120});
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

test('native projection maps back to current viewport and clamps label',()=>{
  const p={ok:true,x:192,y:112};const point=R.nativeToDb(p,db);assert.deepEqual(point,{x:384,y:224});
  const rect=R.labelRect(point,db,30,18);assert.deepEqual(rect,{x:369,y:215,width:30,height:18});
});

console.log(JSON.stringify({status:'PASS',passed,total:passed,fixture:'SYNTHETIC_RELATIVE_HEAD_GEOMETRY_ONLY_NOT_LIVE_WOF'}));
