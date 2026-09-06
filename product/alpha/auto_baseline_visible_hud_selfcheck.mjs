import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const visible=require('./wof_alpha_auto_baseline_visible_hud.js');
const CLASSIFICATION='UNVERIFIED_AUTO_BASELINE';
const ELIGIBILITY={p29Pass:false,p32NativeMarkerQualification:false,p36RendererSourceTrace:false,p34RetryReadiness:false,promotion:false};

function fakeController(){
  let enabled=false,hasFrame=false;
  const items=()=>['P1','P2','P3'].map((p,i)=>({player:p,labelSemantic:`${i+1}P`,native:{x:80+i*100,y:90+i*10,width:384,height:224,yAxis:'TOP_LEFT_POSITIVE_DOWN'},anchorDb:{x:80+i*100,y:90+i*10,yTransform:'PRESERVE_TOP_LEFT_POSITIVE_DOWN_NO_INVERSION'},drawRectDb:{x:20+i*100,y:50+i*10,width:90,height:30}}));
  return{
    setEnabled(v){enabled=v===true;if(!enabled)hasFrame=false;return this.status();},
    ingestFrame(){if(enabled)hasFrame=true;return this.status();},
    drawPlan(){return{classification:CLASSIFICATION,items:enabled&&hasFrame?items():[],reason:enabled?(hasFrame?null:'WAITING_FOR_P37_FRAME'):'DIAGNOSTIC_GATE_OFF'};},
    status(){return{classification:CLASSIFICATION,enabled,state:enabled?(hasFrame?'READY':'WAITING_FOR_P37_FRAME'):'DISABLED',rendererSourceProof:null,authorityEligibility:{...ELIGIBILITY},promotionEligibility:false,safety:{readOnly:true,ramWrites:0,inputInjection:false}};}
  };
}
function fakeBrowser(){
  const calls={prior:0,append:0,remove:0,text:[],clear:0};
  const ctx={font:'',textBaseline:'',textAlign:'',fillStyle:'',strokeStyle:'',lineWidth:1,clearRect(){calls.clear++;},fillRect(){},strokeRect(){},beginPath(){},arc(){},stroke(){},moveTo(){},lineTo(){},measureText(text){return{width:String(text).length*6};},fillText(text){calls.text.push(String(text));}};
  function makeCanvas(){return{width:0,height:0,style:{},parentNode:null,setAttribute(){},getContext(kind){return kind==='2d'?ctx:null;},remove(){calls.remove++;this.parentNode=null;}};}
  const body={appendChild(node){calls.append++;node.parentNode=body;},removeChild(node){calls.remove++;node.parentNode=null;}};
  const doc={body,documentElement:body,createElement(tag){assert.equal(tag,'canvas');return makeCanvas();},getElementById(){return null;}};
  const gameCanvas={getBoundingClientRect(){return{left:10,top:20,width:384,height:224};}};
  const prior=function(){calls.prior++;return'prior-result';};
  const bridge={callback:prior};
  const root={document:doc,I_GF1TC:gameCanvas,__WOF_GL_HOOK:bridge,WOFAutoMarkerBaselineP37:{CLASSIFICATION},WOFAlphaAutoBaselineHudAdapter:{CLASSIFICATION,createController(){return fakeController();}},WOFALPHAHUD:{status(){return{version:'wof-alpha-hud-rc5',drawHooked:true};}}};
  return{root,doc,bridge,prior,calls};
}

function testExplicitGateAndExactCallbackRestore(){
  const b=fakeBrowser(),instance=visible.install({root:b.root,document:b.doc});
  assert.equal(b.bridge.callback,b.prior,'install alone must not alter maintained HUD callback');
  assert.equal(instance.status().enabled,false);assert.equal(instance.status().overlayAttached,false);
  instance.enable();assert.notEqual(b.bridge.callback,b.prior);assert.equal(instance.status().diagnosticCallbackHooked,true);assert.equal(b.calls.append,1);
  instance.ingestFrame({width:384,height:224,data:[]},0,1000);
  const result=b.bridge.callback();assert.equal(result,'prior-result');assert.equal(b.calls.prior,1,'maintained HUD callback must run exactly once before diagnostics');
  const st=instance.status(1000);assert.deepEqual(st.visiblePlayers,['P1','P2','P3']);assert.ok(st.markerDrawCount>=3);assert.equal(st.classification,CLASSIFICATION);
  assert.ok(b.calls.text.some(x=>x.includes(CLASSIFICATION)),'visible diagnostic must carry exact classification');assert.ok(b.calls.text.includes('1P AUTO')&&b.calls.text.includes('2P AUTO')&&b.calls.text.includes('3P AUTO'));
  instance.disable();assert.equal(b.bridge.callback,b.prior,'gate close must restore exact maintained HUD callback object');assert.equal(instance.status().enabled,false);assert.ok(b.calls.remove>=1);
}
function testAuthorityAndZeroClickBoundary(){
  const b=fakeBrowser(),instance=visible.install({root:b.root,document:b.doc});instance.enable();const st=instance.status();
  assert.equal(st.zeroClick,true);assert.equal(st.manualAvatarClickRequired,false);assert.equal(st.manualPortraitSeedRequired,false);assert.equal(st.manualSeedRequired,false);assert.equal(st.manualPlayerSelectionRequired,false);assert.deepEqual(st.automaticPlayers,['P1','P2','P3']);
  assert.equal(st.nativeWidth,384);assert.equal(st.nativeHeight,224);assert.equal(st.nativeYAxis,'TOP_LEFT_POSITIVE_DOWN');assert.equal(st.viewportYInversion,false);
  assert.equal(st.rendererSourceProof,null);assert.deepEqual(st.authorityEligibility,ELIGIBILITY);assert.equal(st.promotionEligibility,false);assert.equal(st.productAuthority,'NONE_DIAGNOSTIC_ONLY');assert.deepEqual(st.safety,{readOnly:true,ramWrites:0,inputInjection:false});instance.dispose();
}
function testLostOrAmbiguousPlanCannotLeavePlayerMarker(){
  const b=fakeBrowser();let mode='TRACKED';
  b.root.WOFAlphaAutoBaselineHudAdapter.createController=()=>({setEnabled(){},ingestFrame(){},status(){return{state:mode,rendererSourceProof:null};},drawPlan(){return{classification:CLASSIFICATION,reason:mode,items:mode==='TRACKED'?[{player:'P1',labelSemantic:'1P',anchorDb:{x:100,y:100},drawRectDb:{x:40,y:60,width:90,height:30}}]:[]};}});
  const instance=visible.install({root:b.root,document:b.doc});instance.enable();mode='AMBIGUOUS_FAIL_CLOSED';instance.ingestFrame({},0,1);assert.deepEqual(instance.status(1).visiblePlayers,[]);mode='STALE_BASELINE_ENVELOPE';instance.ingestFrame({},1,2);assert.deepEqual(instance.status(2).visiblePlayers,[]);instance.dispose();
}

const tests=[testExplicitGateAndExactCallbackRestore,testAuthorityAndZeroClickBoundary,testLostOrAmbiguousPlanCannotLeavePlayerMarker];
for(const test of tests){test();console.log(`PASS ${test.name}`);}console.log(`PASS ${tests.length}/${tests.length} P39 visible-HUD self-checks`);
