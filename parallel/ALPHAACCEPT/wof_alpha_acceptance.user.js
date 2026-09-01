// ==UserScript==
// @name         WOF Alpha Browser Acceptance V2 Collector
// @namespace    https://github.com/ouyong520/wof-ai-private
// @version      0.2.0
// @description  Support-only current-pair acceptance collector for the future safe native-Worker transport. No game RAM writes or gameplay input.
// @match        *://*/*
// @run-at       document-start
// @grant        none
// ==/UserScript==
(()=>{
'use strict';
if(window.__WOF_ALPHA_ACCEPTANCE_V2_COLLECTOR)return;

const VERSION='wof-alpha-browser-acceptance-collector-v2';
const RESULT_SCHEMA='wof-alpha-browser-acceptance-v2';
const PRODUCT_SCHEMA='wof-alpha-v2';
const RELEASE='wof-alpha-rc3';
const TRANSPORT='wof-alpha-safe-transport-v1';
const BUILD='wof / Warriors of Fate (World 921031)';
const GOLDEN='5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62';
const ID_SIG='wof-world-921031-maincpu-sha256-v1:5c369ce2de4f53d8';
const ALLOWED_RULES=new Set(['T18_5440_CYCLE_BODY7512_TM4_LEVEL_90','T18_5424_CYCLE_BODY7520_TM4_LEVEL_90']);
const TARGET_BY_7E={0:'P1',4:'P2',8:'P3'};
const SIDE=new Set(['LEFT','CENTER','RIGHT']);
const HEX32=/^[0-9a-f]{32}$/;
const nowIso=()=>new Date().toISOString();
const clone=x=>{try{return structuredClone(x);}catch(_){try{return JSON.parse(JSON.stringify(x));}catch(__){return null;}}};

let rafCount=0;
(function raf(){rafCount++;requestAnimationFrame(raf);})();

const obs={
  started:false,startedAt:null,ownerConfirmedPlayable:false,marks:[],bc:null,bcName:null,
  pageConfig:null,currentPair:null,pairHistory:[],lastSeqByGeneration:new Map(),
  currentStates:0,currentDiags:0,rejected:[],firstState:null,emptyStateSeen:false,
  identityAccepted:false,identitySignature:null,safetySeen:null,warningRows:0,invalidWarnings:[],
  diags:[],negative:[],rafAtBegin:0,rafAtLastMark:0,lastError:null
};

function safeConfig(){
  try{
    const c=window.__WOF_ALPHA_CONFIG;
    if(!c)return null;
    return {release:c.release??null,schema:c.schema??null,session:c.session??null,channel:c.channel??null};
  }catch(e){obs.lastError=String(e?.message||e);return null;}
}
function safeTransport(){
  try{
    const t=window.__WOF_ALPHA_TRANSPORT_V1;
    const s=typeof t?.status==='function'?t.status():null;
    return s&&typeof s==='object'?clone(s):null;
  }catch(e){obs.lastError=String(e?.message||e);return null;}
}
function safeHud(){
  try{return clone(window.WOFALPHAHUD?.status?.()||null);}catch(e){return{lastError:String(e?.message||e)};}
}
function normalizePair(cfg,t){
  if(!cfg||!t)return null;
  const session=String(t.session??cfg.session??'');
  const generation=Number(t.pairGeneration);
  const nonce=String(t.pairNonce??'');
  const version=String(t.transportVersion??'');
  if(cfg.schema!==PRODUCT_SCHEMA||cfg.release!==RELEASE||!HEX32.test(session)||cfg.session!==session)return null;
  if(version!==TRANSPORT||!Number.isInteger(generation)||generation<1||!HEX32.test(nonce))return null;
  return {transportVersion:version,session,pairGeneration:generation,pairNonce:nonce};
}
function samePair(a,b){return !!a&&!!b&&a.session===b.session&&a.pairGeneration===b.pairGeneration&&a.pairNonce===b.pairNonce&&a.transportVersion===b.transportVersion;}
function updatePair(){
  const cfg=safeConfig(),t=safeTransport(),p=normalizePair(cfg,t);
  obs.pageConfig=cfg;
  if(p&&!samePair(p,obs.currentPair)){
    obs.currentPair=p;
    obs.pairHistory.push({...p,seenAt:nowIso()});
    if(obs.pairHistory.length>20)obs.pairHistory.shift();
    attachChannel(cfg?.channel);
  }else if(cfg?.channel&&cfg.channel!==obs.bcName)attachChannel(cfg.channel);
  if(t){
    const ident=t.identity||t.detectorIdentity||null;
    if(ident?.ok===true||ident?.accepted===true){obs.identityAccepted=true;obs.identitySignature=ident.signature||t.identitySignature||obs.identitySignature;}
    if(typeof t.identitySignature==='string')obs.identitySignature=t.identitySignature;
  }
  return {cfg,t,p};
}
function attachChannel(name){
  if(typeof name!=='string'||!name)return;
  if(obs.bc&&obs.bcName===name)return;
  try{obs.bc?.close?.();}catch(_){}
  try{obs.bc=new BroadcastChannel(name);obs.bcName=name;obs.bc.onmessage=e=>observeMessage(e.data);}catch(e){obs.lastError='BroadcastChannel: '+String(e?.message||e);}
}
function rejectReason(m){
  const p=obs.currentPair;
  if(!m||typeof m!=='object')return'not-object';
  if(m.schema!==PRODUCT_SCHEMA)return'wrong-schema';
  if(m.transportVersion!==TRANSPORT)return'wrong-transport-version';
  if(!p)return'no-current-pair';
  if(m.session!==p.session)return'wrong-session';
  if(m.pairGeneration!==p.pairGeneration)return'wrong-generation';
  if(m.pairNonce!==p.pairNonce)return'wrong-nonce';
  return null;
}
function validateWarning(w){
  const e=[];
  if(!w||typeof w!=='object')return['not-object'];
  if(!ALLOWED_RULES.has(w.ruleId))e.push('ruleId');
  if(!['P1','P2','P3'].includes(w.target))e.push('target');
  if(TARGET_BY_7E[w.target7E]!==w.target)e.push('target7E');
  if(!SIDE.has(w.sourceSide))e.push('sourceSide');
  if(!SIDE.has(w.threatSide))e.push('threatSide');
  if(w.publication!=='hold-only-current-level')e.push('publication');
  if(w.evidence!=='fresh-current-sample')e.push('evidence');
  for(const k of ['ageMs','watchId','watch','history','previous','priorTarget','atMs'])if(Object.prototype.hasOwnProperty.call(w,k))e.push('forbidden:'+k);
  return e;
}
function observeMessage(m){
  updatePair();
  const reason=rejectReason(m);
  if(reason){if(obs.started&&obs.rejected.length<100)obs.rejected.push({at:nowIso(),kind:m?.kind??null,reason,pairGeneration:m?.pairGeneration??null});return;}
  if(m.kind==='state'){
    const seq=Number(m.seq),g=obs.currentPair.pairGeneration,last=obs.lastSeqByGeneration.get(g)??-1;
    if(!Number.isInteger(seq)||seq<=last){if(obs.started)obs.rejected.push({at:nowIso(),kind:'state',reason:'duplicate-or-out-of-order-seq',seq});return;}
    obs.lastSeqByGeneration.set(g,seq);
    if(!obs.started)return;
    obs.currentStates++;
    if(!obs.firstState)obs.firstState={at:nowIso(),pair:clone(obs.currentPair),seq,hud:safeHud()};
    if(m.identitySignature===ID_SIG){obs.identityAccepted=true;obs.identitySignature=m.identitySignature;}
    if(typeof m.identitySignature==='string'&&m.identitySignature!==ID_SIG)obs.identitySignature=m.identitySignature;
    obs.safetySeen={readOnly:m.readOnly,ramWrites:m.ramWrites,inputInjection:m.inputInjection};
    const rows=Array.isArray(m.warnings)?m.warnings:[];
    if(rows.length===0)obs.emptyStateSeen=true;
    obs.warningRows+=rows.length;
    for(const w of rows){const errors=validateWarning(w);if(errors.length&&obs.invalidWarnings.length<30)obs.invalidWarnings.push({ruleId:w?.ruleId??null,errors});}
  } else if(m.kind==='diag'){
    if(!obs.started)return;
    obs.currentDiags++;
    const before=safeHud()?.warningCount??null;
    const d={at:nowIso(),pair:clone(obs.currentPair),code:m.code??null,status:m.status??null,warningCountBefore:before,warningCountNextTask:null};
    obs.diags.push(d);
    setTimeout(()=>{d.warningCountNextTask=safeHud()?.warningCount??null;},0);
  }
}
function status(){
  const {cfg,t,p}=updatePair();
  return {version:VERSION,ready:!!p,pageConfig:cfg,transport:t,currentPair:p,hud:safeHud(),identityAccepted:obs.identityAccepted,identitySignature:obs.identitySignature,currentStates:obs.currentStates,currentDiags:obs.currentDiags,rafCount,lastError:obs.lastError};
}
function resetRun(){
  obs.started=false;obs.startedAt=null;obs.ownerConfirmedPlayable=false;obs.marks=[];obs.currentStates=0;obs.currentDiags=0;obs.rejected=[];obs.firstState=null;obs.emptyStateSeen=false;
  obs.identityAccepted=false;obs.identitySignature=null;obs.safetySeen=null;obs.warningRows=0;obs.invalidWarnings=[];obs.diags=[];obs.negative=[];obs.lastSeqByGeneration=new Map();obs.pairHistory=[];obs.currentPair=null;obs.rafAtBegin=rafCount;obs.rafAtLastMark=rafCount;obs.lastError=null;
  updatePair();
}
function begin(opts={}){
  resetRun();
  if(opts.ownerConfirmedPlayable!==true)return{ok:false,error:'ownerConfirmedPlayable must be true'};
  obs.started=true;obs.startedAt=nowIso();obs.ownerConfirmedPlayable=true;obs.marks.push({name:'begin',at:obs.startedAt,detail:{pair:clone(obs.currentPair)}});
  return{ok:true,status:status()};
}
function mark(name,detail=null){
  if(!obs.started)return{ok:false,error:'not-started'};
  const item={name:String(name),at:nowIso(),rafDelta:rafCount-obs.rafAtLastMark,detail:clone(detail)};obs.rafAtLastMark=rafCount;obs.marks.push(item);return{ok:true,item};
}
function makeNegative(kind){
  const p=obs.currentPair;if(!p)throw new Error('no current pair');
  const common={schema:PRODUCT_SCHEMA,release:RELEASE,transportVersion:TRANSPORT,session:p.session,pairGeneration:p.pairGeneration,pairNonce:p.pairNonce,readOnly:true,ramWrites:0,inputInjection:false};
  if(kind.startsWith('old-generation-')){common.pairGeneration=Math.max(0,p.pairGeneration-1);common.pairNonce='00000000000000000000000000000000';}
  if(kind.startsWith('wrong-nonce-'))common.pairNonce='ffffffffffffffffffffffffffffffff'===p.pairNonce?'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee':'ffffffffffffffffffffffffffffffff';
  if(kind.endsWith('-state'))return{...common,kind:'state',seq:2147483000,identitySignature:ID_SIG,warnings:[]};
  return{...common,kind:'diag',status:'DISABLED',code:'acceptance-negative-pair-probe',reason:'support-only acceptance negative-pair fixture'};
}
async function postNegative(kind){
  const allowed=new Set(['old-generation-state','old-generation-diag','wrong-nonce-state','wrong-nonce-diag']);
  if(!obs.started)return{ok:false,error:'not-started'};
  if(!allowed.has(kind))return{ok:false,error:'unsupported-kind'};
  updatePair();if(!obs.bc||!obs.currentPair)return{ok:false,error:'no-current-pair-channel'};
  const m=makeNegative(kind),before=safeHud();obs.bc.postMessage(m);await new Promise(r=>setTimeout(r,0));const after=safeHud();
  const item={kind,postedAt:nowIso(),collectorRejectReason:rejectReason(m),warningCountBefore:before?.warningCount??null,warningCountAfter:after?.warningCount??null,pairGeneration:m.pairGeneration,pairNonce:m.pairNonce};
  obs.negative.push(item);return{ok:true,item};
}
function snapshot(){return{status:status(),started:obs.started,startedAt:obs.startedAt,ownerConfirmedPlayable:obs.ownerConfirmedPlayable,marks:clone(obs.marks),pairHistory:clone(obs.pairHistory),firstState:clone(obs.firstState),emptyStateSeen:obs.emptyStateSeen,currentStates:obs.currentStates,currentDiags:obs.currentDiags,identityAccepted:obs.identityAccepted,identitySignature:obs.identitySignature,safetySeen:clone(obs.safetySeen),diags:clone(obs.diags),negative:clone(obs.negative),rejected:clone(obs.rejected),warningRows:obs.warningRows,invalidWarnings:clone(obs.invalidWarnings),rafDelta:rafCount-obs.rafAtBegin};}
function gatePass(g){return !!g&&['status','productRegression','transportIntegrationTests','pylaunchTests','rc5NoWorkerReplacementRegression','rc4DiagSessionStaleRegression','exactStaleBoundary1500_1501'].every(k=>g[k]==='PASS');}
function launcherPass(l){return !!l&&['browser','wofPage','worker','wasmHeap','world921031','launcherIdentityGate'].every(k=>l[k]===true);}
function safetyPass(s){return !!s&&s.readOnly===true&&s.ramWrites===0&&s.inputInjection===false&&s.windowWorkerReplacement===false;}
function negativeSummary(){
  const by=k=>obs.negative.find(x=>x.kind===k);
  const rejected=x=>!!x&&['wrong-generation','wrong-nonce'].includes(x.collectorRejectReason);
  return{result:['old-generation-state','old-generation-diag','wrong-nonce-state','wrong-nonce-diag'].every(k=>rejected(by(k)))?'PASS':'INCOMPLETE',oldGenerationStateRejected:rejected(by('old-generation-state')),oldGenerationDiagRejected:rejected(by('old-generation-diag')),wrongNonceStateRejected:rejected(by('wrong-nonce-state')),wrongNonceDiagRejected:rejected(by('wrong-nonce-diag'))};
}
function finalize(driver={}){
  updatePair();
  const failures=[],incomplete=[];
  const integration=driver.integrationGate||{};const launcher=driver.launcher||{};const safety=driver.safety||{};const actions=driver.actions||{};
  if(!gatePass(integration))failures.push('integration gate is not fully PASS');
  if(!launcherPass(launcher))failures.push('launcher Browser/page/Worker/WASM/World gate is incomplete');
  if(!safetyPass(safety))failures.push('safety contract mismatch');
  const hist=obs.pairHistory.filter((x,i,a)=>i===0||!samePair(x,a[i-1]));const initial=hist.length?hist[0]:null,rebound=hist.length>1?hist[hist.length-1]:null;
  const pair={session:initial?.session??obs.currentPair?.session??null,initialGeneration:initial?.pairGeneration??null,initialNonce:initial?.pairNonce??null,reboundGeneration:rebound?.pairGeneration??null,reboundNonce:rebound?.pairNonce??null,generationIncreased:!!(initial&&rebound&&rebound.pairGeneration>initial.pairGeneration),nonceChanged:!!(initial&&rebound&&rebound.pairNonce!==initial.pairNonce)};
  if(!pair.generationIncreased||!pair.nonceChanged)incomplete.push('fresh rebind pair not fully observed');
  const identityOk=obs.identityAccepted&&obs.identitySignature===ID_SIG;if(!identityOk)incomplete.push('detector-local World 921031 identity acceptance not observed');
  if(!obs.firstState)incomplete.push('first valid current-pair state not observed');
  if(!obs.emptyStateSeen)incomplete.push('fresh no-warning state not observed');
  const lastDiag=obs.diags.length?obs.diags[obs.diags.length-1]:null;
  const diagResult=lastDiag?(lastDiag.warningCountBefore>0?(lastDiag.warningCountNextTask===0?'PASS':'FAIL'):'NO_ACTIVE_WARNING'):'INCOMPLETE';
  if(diagResult==='FAIL')failures.push('current-pair diag did not immediately clear warning');else if(diagResult==='INCOMPLETE')incomplete.push('current-pair diag not observed');
  const neg=negativeSummary();if(neg.result!=='PASS')incomplete.push('all four old-generation/wrong-nonce negative probes not observed');
  if(obs.invalidWarnings.length)failures.push('invalid warning row observed');
  const warningResult=obs.invalidWarnings.length?'FAIL':(obs.warningRows?'PASS':'NOT_EXERCISED');
  const staleResult=actions.staleProbe||'INCOMPLETE';if(!['PASS','OFFLINE_GATE_ONLY'].includes(staleResult))incomplete.push('live stale probe unavailable or incomplete');
  const renderAlive=obs.rafAtBegin>0&&(rafCount-obs.rafAtBegin)>0;const gameplayOk=obs.ownerConfirmedPlayable&&renderAlive&&launcher.roomRemainedPlayable===true;
  if(!gameplayOk)incomplete.push('room playability/render liveness evidence incomplete');
  let result='PASS — REAL BROWSER ACCEPTANCE V2';
  if(!gatePass(integration))result='BLOCKED — TRANSPORT INTEGRATION NOT READY';
  else if(failures.length)result='FAIL — REAL BROWSER ACCEPTANCE V2';
  else if(incomplete.length)result='INCOMPLETE — REAL BROWSER ACCEPTANCE V2';
  const out={schema:RESULT_SCHEMA,result,release:RELEASE,transportVersion:TRANSPORT,supportedBuild:BUILD,goldenSha256:GOLDEN,expectedIdentitySignature:ID_SIG,startedAt:obs.startedAt,finishedAt:nowIso(),durationMs:obs.startedAt?Date.now()-Date.parse(obs.startedAt):0,integrationGate:clone(integration),launcher:clone(launcher),pair,detectorIdentity:{result:identityOk?'PASS':'INCOMPLETE',accepted:obs.identityAccepted,signature:obs.identitySignature},firstCurrentPairState:{result:obs.firstState?'PASS':'INCOMPLETE',observed:!!obs.firstState,seq:obs.firstState?.seq??null,hudAuthorityOnlyAfterState:driver.firstCurrentPairState?.hudAuthorityOnlyAfterState??null},noWarningState:{result:obs.emptyStateSeen?'PASS':'INCOMPLETE',observed:obs.emptyStateSeen},stale1500:{result:staleResult,exactBoundaryAuthority:'offline integration regression',exact1500_1501Gate:integration.exactStaleBoundary1500_1501??null,browserObservedSilentAfter1500:driver.stale1500?.browserObservedSilentAfter1500??null},diagImmediateClear:{result:diagResult,currentPairDiagObserved:!!lastDiag,warningCountBefore:lastDiag?.warningCountBefore??null,warningCountNextTask:lastDiag?.warningCountNextTask??null,waitedForStaleTimeout:false},rebind:{result:pair.generationIncreased&&pair.nonceChanged?'PASS':'INCOMPLETE',freshPair:pair.generationIncreased&&pair.nonceChanged,freshStateObserved:driver.rebind?.freshStateObserved??false,oldAuthorityInherited:driver.rebind?.oldAuthorityInherited??null},negativePairRejection:neg,warningSanity:{result:warningResult,observedWarningRows:obs.warningRows,allowedRuleIds:[...ALLOWED_RULES],invalidRows:clone(obs.invalidWarnings)},gameplay:{result:gameplayOk?'PASS':'INCOMPLETE',ownerConfirmedPlayableAtStart:obs.ownerConfirmedPlayable,renderAliveAcrossStopRebind:renderAlive,roomRemainedPlayable:launcher.roomRemainedPlayable===true,navigationInjected:false},safety:{result:safetyPass(safety)?'PASS':'FAIL',readOnly:safety.readOnly??null,ramWrites:safety.ramWrites??null,inputInjection:safety.inputInjection??null,windowWorkerReplacement:safety.windowWorkerReplacement??null},failures:[...new Set(failures)],incomplete:[...new Set(incomplete)],notes:[warningResult==='NOT_EXERCISED'?'No approved T18 warning occurred naturally; no attack research was added.':null,'Browser acceptance evidence does not itself declare Alpha released.'].filter(Boolean)};
  window.__WOF_ALPHA_ACCEPTANCE_RESULT=out;console.log('WOF_ALPHA_ACCEPTANCE_RESULT_V2',JSON.stringify(out));return out;
}

window.__WOF_ALPHA_ACCEPTANCE_V2_COLLECTOR={version:VERSION,status,begin,mark,snapshot,postNegative,finalize,reset:()=>{resetRun();return status();}};

let ui,stat;
function ensureUi(){
  if(ui||!document.documentElement)return;
  const d=document.createElement('div');d.style.cssText='position:fixed;right:10px;top:10px;z-index:2147483647;width:330px;background:rgba(15,15,18,.95);color:#fff;border:1px solid #aaa;border-radius:8px;padding:10px;font:13px/1.45 sans-serif;box-shadow:0 2px 12px #0008';
  const title=document.createElement('div');title.textContent='WOF Alpha 真人验收 V2';title.style.cssText='font-weight:700;font-size:15px;margin-bottom:6px';
  stat=document.createElement('div');stat.style.cssText='margin-bottom:8px;color:#ddd';
  const b=document.createElement('button');b.textContent='当前房间可以正常操作，开始验收';b.style.cssText='width:100%;padding:8px;font-weight:700';
  b.onclick=()=>{const r=begin({ownerConfirmedPlayable:true});stat.textContent=r.ok?'已开始采集。后续 stale / diag / rebind 由集成后的 Launcher 自动执行。':'无法开始：'+r.error;};
  d.append(title,stat,b);document.documentElement.appendChild(d);ui=d;
}
setInterval(()=>{
  const s=status();
  if((s.pageConfig||s.transport)&&!ui)ensureUi();
  if(stat&&!obs.started)stat.textContent=s.ready?'已发现 Safe Transport current pair；等待开始验收。':'验收准备已完成；当前等待 Safe Transport Integration / current pair。';
},100);
addEventListener('pagehide',()=>{try{obs.bc?.close?.();}catch(_){}},{once:true});
})();
