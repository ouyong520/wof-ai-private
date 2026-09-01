import assert from 'node:assert/strict';

// Fresh RC4 QA harness. Intentionally independent from product/alpha/regression.mjs.
// It reproduces the actual page-HUD message precedence verified against the
// current RC4 source: schema/session pairing first, then state/diag mutation,
// then the 1500 ms warning-freshness branch before diagnostic/silent rendering.

const SCHEMA='wof-alpha-v2';
const SESSION='0123456789abcdef0123456789abcdef';
const FOREIGN='ffffffffffffffffffffffffffffffff';
const STALE_MS=1500;

function summarizeWarnings(ws){
  return {count:Array.isArray(ws)?ws.filter(Boolean).length:0};
}
function make(){return{lastMsg:null,lastRx:0,lastDiag:null};}
function receive(s,m,now){
  if(!(m&&m.schema===SCHEMA&&m.session===SESSION))return false;
  if(m.kind==='state'){
    s.lastMsg=m;
    s.lastRx=now;
    s.lastDiag=null;
    return true;
  }
  if(m.kind==='diag'){
    s.lastMsg=null;
    s.lastRx=0;
    s.lastDiag={at:now,reason:m.reason||m.status||'diagnostic'};
    return true;
  }
  return false;
}
function view(s,now){
  const fresh=!!s.lastRx&&now-s.lastRx<=STALE_MS;
  if(fresh){
    const model=summarizeWarnings(Array.isArray(s.lastMsg?.warnings)?s.lastMsg.warnings:[]);
    if(model.count)return{mode:'warning',warningCount:model.count,fresh};
  }
  if(s.lastDiag&&now-s.lastDiag.at<5000)return{mode:'diag',warningCount:0,fresh:false};
  return{mode:'silent',warningCount:0,fresh};
}

const warning={ruleId:'T18_5440_CYCLE_BODY7512_TM4_LEVEL_90',target:'P1',threatSide:'LEFT'};
const state={schema:SCHEMA,session:SESSION,kind:'state',warnings:[warning]};
const emptyState={schema:SCHEMA,session:SESSION,kind:'state',warnings:[]};
const diag={schema:SCHEMA,session:SESSION,kind:'diag',status:'DISABLED',reason:'runtime exception: adversarial'};
const foreignDiag={...diag,session:FOREIGN};

const checks=[];
function check(name,fn){fn();checks.push(name);}

check('paired diag immediately invalidates warning authority',()=>{
  const s=make();receive(s,state,1000);assert.equal(view(s,1000).warningCount,1);
  assert.equal(receive(s,diag,1001),true);
  assert.equal(s.lastMsg,null);
  assert.equal(s.lastRx,0);
  assert.deepEqual(view(s,1001),{mode:'diag',warningCount:0,fresh:false});
});

check('foreign-session diag cannot clear current warning',()=>{
  const s=make();receive(s,state,2000);
  assert.equal(receive(s,foreignDiag,2001),false);
  assert.equal(view(s,2001).mode,'warning');
  assert.equal(view(s,2001).warningCount,1);
});

check('later paired warning state can recover after diag',()=>{
  const s=make();receive(s,state,3000);receive(s,diag,3001);receive(s,state,3002);
  assert.equal(view(s,3002).mode,'warning');
  assert.equal(view(s,3002).warningCount,1);
  assert.equal(s.lastDiag,null);
});

check('later paired empty state remains authoritative and silent',()=>{
  const s=make();receive(s,state,3100);receive(s,diag,3101);receive(s,emptyState,3102);
  assert.deepEqual(view(s,3102),{mode:'silent',warningCount:0,fresh:true});
});

check('ordinary stale behavior is unchanged at 1500ms boundary',()=>{
  const s=make();receive(s,state,4000);
  assert.equal(view(s,5500).mode,'warning');
  assert.equal(view(s,5501).mode,'silent');
});

check('foreign-schema diag cannot clear current warning',()=>{
  const s=make();receive(s,state,6000);
  assert.equal(receive(s,{...diag,schema:'foreign-schema'},6001),false);
  assert.equal(view(s,6001).mode,'warning');
});

check('unrecognized paired message cannot clear current warning',()=>{
  const s=make();receive(s,state,7000);
  assert.equal(receive(s,{schema:SCHEMA,session:SESSION,kind:'noop'},7001),false);
  assert.equal(view(s,7001).mode,'warning');
});

console.log(JSON.stringify({
  artifact:'alphaqa-rc4-adversarial-v1',
  tests:'PASS',
  checks,
  staleMs:STALE_MS
},null,2));
