import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const adapter=require('./wof_alpha_auto_baseline_hud_adapter.js');

const CLASSIFICATION='UNVERIFIED_AUTO_BASELINE';
const ELIGIBILITY={p29Pass:false,p32NativeMarkerQualification:false,p36RendererSourceTrace:false,p34RetryReadiness:false,promotion:false};
const SAFETY={readOnly:true,ramWrites:0,inputInjection:false};

function track(player,x,y,state='TRACKED',extra={}){
  return{player,labelSemantic:`${player[1]}P`,state,x:state==='TRACKED'?x:null,y:state==='TRACKED'?y:null,observed:state==='TRACKED',coordinateClass:state==='TRACKED'?'OBSERVED_DIAGNOSTIC_PIXEL_STRUCTURE':null,nativeWidth:384,nativeHeight:224,nativeYAxis:'TOP_LEFT_POSITIVE_DOWN',ageMs:0,acceptedCount:1,reacquireCount:0,...extra};
}
function envelope({p1=track('P1',80,80),p2=track('P2',190,100),p3=track('P3',300,120),state='TRACKING_ALL_PLAYERS',rendererSourceProof=null,eligibility=ELIGIBILITY}={}){
  return{schema:'wof-native-marker-auto-acquisition-baseline-v1',classification:CLASSIFICATION,state,timestampMs:0,nativeWidth:384,nativeHeight:224,nativeYAxis:'TOP_LEFT_POSITIVE_DOWN',coordinateAuthority:'DIAGNOSTIC_FRAME_PIXEL_NATIVE_384X224_NOT_RENDERER',zeroClick:true,manualSeedRequired:false,manualPlayerSelectionRequired:false,rendererSourceProof,authorityEligibility:{...eligibility},safety:{...SAFETY},tracks:{P1:p1,P2:p2,P3:p3}};
}
function fakeP37(){
  let calls=0,resets=0;
  return{
    CLASSIFICATION,SCHEMA:'wof-native-marker-auto-acquisition-baseline-v1',NATIVE_WIDTH:384,NATIVE_HEIGHT:224,
    createBaselineTracker(){return{ingestFrame(frame){calls++;return frame.envelope;},reset(){resets++;}};},
    mapNativeToViewport(point,rect){return{x:rect.left+point.x*rect.width/384,y:rect.top+point.y*rect.height/224,yTransform:'PRESERVE_TOP_LEFT_POSITIVE_DOWN_NO_INVERSION'};},
    counts(){return{calls,resets};}
  };
}

function testGateOffIsInert(){
  const p37=fakeP37(),c=adapter.createController(p37);
  const st=c.ingestFrame({envelope:envelope()},0,1000);
  assert.equal(st.enabled,false);assert.equal(st.state,'DISABLED');assert.equal(p37.counts().calls,0);
  assert.deepEqual(c.drawPlan({width:768,height:448},1000).items,[]);
}
function testZeroClickP1P2P3AndCoordinates(){
  const p37=fakeP37(),c=adapter.createController(p37);c.setEnabled(true);
  c.ingestFrame({envelope:envelope()},0,1000);
  const plan=c.drawPlan({width:768,height:448},1000);
  assert.equal(plan.classification,CLASSIFICATION);assert.equal(plan.items.length,3);assert.deepEqual(plan.items.map(x=>x.player),['P1','P2','P3']);
  assert.equal(plan.zeroClick,true);assert.equal(plan.manualSeedRequired,false);assert.equal(plan.manualPlayerSelectionRequired,false);
  assert.equal(plan.items[0].anchorDb.x,160);assert.equal(plan.items[0].anchorDb.y,160);assert.equal(plan.items[0].anchorDb.yTransform,'PRESERVE_TOP_LEFT_POSITIVE_DOWN_NO_INVERSION');
  assert.ok(plan.items[0].anchorDb.x<plan.items[1].anchorDb.x&&plan.items[1].anchorDb.x<plan.items[2].anchorDb.x);
}
function testDirectionPreservedNoYInversion(){
  const p37=fakeP37(),c=adapter.createController(p37);c.setEnabled(true);
  c.ingestFrame({envelope:envelope({p1:track('P1',100,80)})},0,1000);const up=c.drawPlan({width:384,height:224},1000).items.find(x=>x.player==='P1');
  c.ingestFrame({envelope:envelope({p1:track('P1',130,110)})},100,1100);const downRight=c.drawPlan({width:384,height:224},1100).items.find(x=>x.player==='P1');
  assert.ok(downRight.anchorDb.x>up.anchorDb.x,'right must increase x');assert.ok(downRight.anchorDb.y>up.anchorDb.y,'down must increase y');
}
function testLostStaleAndAutomaticReacquireVisibility(){
  const p37=fakeP37(),c=adapter.createController(p37);c.setEnabled(true);
  c.ingestFrame({envelope:envelope()},0,1000);assert.equal(c.drawPlan({width:384,height:224},1000).items.length,3);
  c.ingestFrame({envelope:envelope({p1:track('P1',0,0,'LOST',{reason:'TRACK_LOST_REACQUIRE_AUTOMATIC'}) ,state:'TRACKING_PARTIAL'})},900,1100);
  assert.deepEqual(c.drawPlan({width:384,height:224},1100).items.map(x=>x.player),['P2','P3'],'lost P1 marker must hide');
  c.ingestFrame({envelope:envelope({p1:track('P1',165,115,'TRACKED',{acquisition:'AUTO_REACQUIRED',reacquireCount:1})})},1000,1200);
  const reacquired=c.drawPlan({width:384,height:224},1200).items.find(x=>x.player==='P1');assert.equal(reacquired.acquisition,'AUTO_REACQUIRED');assert.equal(reacquired.reacquireCount,1);
  const stale=c.drawPlan({width:384,height:224},1651);assert.equal(stale.reason,'STALE_BASELINE_ENVELOPE');assert.equal(stale.items.length,0);
}
function testAmbiguityAndProofBoundaryFailClosed(){
  const p37=fakeP37(),c=adapter.createController(p37);c.setEnabled(true);
  c.ingestFrame({envelope:envelope({p1:track('P1',0,0,'AMBIGUOUS',{ambiguityReason:'MULTIPLE_NATIVE_LABEL_ARROW_CLUSTERS'}),state:'AMBIGUOUS'})},0,1000);
  let plan=c.drawPlan({width:384,height:224},1000);assert.equal(plan.reason,'AMBIGUOUS_FAIL_CLOSED');assert.equal(plan.items.length,0);
  c.ingestFrame({envelope:envelope({rendererSourceProof:{fake:true}})},100,1100);const st=c.status(1100);assert.equal(st.state,'P37_RENDERER_PROOF_BOUNDARY_VIOLATION');
  plan=c.drawPlan({width:384,height:224},1100);assert.equal(plan.items.length,0);assert.equal(plan.rendererSourceProof,null);assert.deepEqual(plan.authorityEligibility,ELIGIBILITY);assert.equal(plan.promotionEligibility,false);
}
function testNoP37HeuristicCopy(){
  const src=fs.readFileSync(new URL('./wof_alpha_auto_baseline_hud_adapter.js',import.meta.url),'utf8');
  for(const forbidden of ['function playerColor','function buildMask','function components(','function textCandidates','function canonicalMarkerCandidates'])assert.equal(src.includes(forbidden),false,`must reuse P37 rather than copy ${forbidden}`);
  assert.ok(src.includes('p37.createBaselineTracker()'));assert.ok(src.includes('p37.mapNativeToViewport'));
}

const tests=[testGateOffIsInert,testZeroClickP1P2P3AndCoordinates,testDirectionPreservedNoYInversion,testLostStaleAndAutomaticReacquireVisibility,testAmbiguityAndProofBoundaryFailClosed,testNoP37HeuristicCopy];
for(const test of tests){test();console.log(`PASS ${test.name}`);}console.log(`PASS ${tests.length}/${tests.length} P39 adapter self-checks`);
