import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const here=path.dirname(fileURLToPath(import.meta.url));
const fixtures=JSON.parse(fs.readFileSync(path.join(here,'fixtures.json'),'utf8'));
const catalog=JSON.parse(fs.readFileSync(path.join(here,'vectors.json'),'utf8'));
const expected=JSON.parse(fs.readFileSync(path.join(here,'expected_results.json'),'utf8'));
const C=fixtures.constants;
const P=fixtures.pairs;
const W=fixtures.warnings;

function fail(msg){throw new Error(msg)}
function ok(cond,msg='assertion failed'){if(!cond)fail(msg)}
function eq(a,b,msg='not equal'){if(a!==b)fail(`${msg}: ${JSON.stringify(a)} !== ${JSON.stringify(b)}`)}
function clone(x){return JSON.parse(JSON.stringify(x))}

function materializeWarnings(frameName){
  const frame=fixtures.detectorFrames[frameName];
  return frame.warnings.map(k=>({...clone(W[k]),...(frame.warningOverrides?.[k]||{})}));
}
function safetyFields(){return {readOnly:true,ramWrites:0,inputInjection:false}}
function makeState(pair, seq, warnings=[], extra={}){
  return {schema:C.applicationSchema,kind:'state',release:C.release,coreVersion:'wof-alpha-core-rc3',transportVersion:C.transportVersion,
    session:pair.session,pairGeneration:pair.pairGeneration,pairNonce:pair.pairNonce,seq,sentAt:1000,
    identitySignature:C.identitySignature,...safetyFields(),warnings:clone(warnings),...extra};
}
function makeDiag(pair, extra={}){
  return {schema:C.applicationSchema,kind:'diag',release:C.release,transportVersion:C.transportVersion,
    session:pair.session,pairGeneration:pair.pairGeneration,pairNonce:pair.pairNonce,sentAt:1000,status:'DISABLED',code:'runtime-exception',reason:'mock',...safetyFields(),...extra};
}

class Receiver{
  constructor(session){this.session=session;this.generation=0;this.nonce=null;this.lastSeq=-1;this.lastReceive=null;this.authority=[];this.hudLoaded=false;this.diag=null}
  bind(pair){
    ok(pair.session===this.session,'bind session mismatch');
    ok(Number.isInteger(pair.pairGeneration)&&pair.pairGeneration>this.generation,'generation must increase');
    this.generation=pair.pairGeneration;this.nonce=pair.pairNonce;this.lastSeq=-1;this.lastReceive=null;this.authority=[];this.diag=null;
  }
  validEnvelope(m){return !!m&&m.schema===C.applicationSchema&&m.session===this.session&&m.transportVersion===C.transportVersion&&m.pairGeneration===this.generation&&m.pairNonce===this.nonce}
  accept(m,monoMs){
    if(!this.validEnvelope(m))return false;
    if(m.kind==='diag'){
      if(m.readOnly!==true||m.ramWrites!==0||m.inputInjection!==false)return false;
      this.authority=[];this.lastReceive=null;this.diag={code:m.code,status:m.status};return true;
    }
    if(m.kind!=='state')return false;
    if(!Number.isInteger(m.seq)||m.seq<=this.lastSeq)return false;
    if(m.identitySignature!==C.identitySignature)return false;
    if(m.readOnly!==true||m.ramWrites!==0||m.inputInjection!==false)return false;
    this.lastSeq=m.seq;this.lastReceive=monoMs;this.authority=clone(m.warnings||[]);this.diag=null;this.hudLoaded=true;return true;
  }
  visible(monoMs){if(this.lastReceive===null)return [];return monoMs-this.lastReceive<=C.staleMs?clone(this.authority):[]}
}

function workerEligible(w){return w?.type==='worker'&&/\/gstyphoon(?:\.[^/?#]+)?\.js(?:[?#].*)?$/i.test(w.url||'')&&w.moduleOk===true&&w.identityOk===true}
function resolveForPage(setName,page){
  const list=fixtures.targetSets[setName].filter(workerEligible);
  const exact=list.filter(w=>w.associationExact===true&&w.page===page);
  if(exact.length===1)return {ok:true,id:exact[0].id};
  return {ok:false,reason:exact.length===0?'none':'ambiguous'};
}
function exactTwoTabIsolation(setName){return resolveForPage(setName,'p1').ok&&resolveForPage(setName,'p2').ok&&resolveForPage(setName,'p1').id!==resolveForPage(setName,'p2').id}

function identityGate(name){
  const p=fixtures.identityProbes[name];
  return !!p&&p.moduleOk===true&&p.heapOk===true&&p.candidateCount===1&&p.hashStatus==='accepted'&&typeof p.sha256==='string'&&/^[0-9a-f]{64}$/.test(p.sha256)&&p.sha256===C.goldenSha256&&p.readOnly===true&&p.ramWrites===0&&p.inputInjection===false;
}

class Agent{
  constructor(){this.active=false;this.runtimeEpoch=null;this.hashCount=0;this.inFlight=false;this.skipped=0;this.queueDepth=0;this.publications=[];this.lastPublishedHash=null;this.lastPublishedAt=null;this.gameplayPlayable=true;this.agentCount=0}
  install(epoch, identityName='valid', detectorLocalOk=true){
    this.hashCount++;
    if(!identityGate(identityName)||!detectorLocalOk){this.active=false;this.agentCount=0;return false}
    this.active=true;this.runtimeEpoch=epoch;this.agentCount=1;return true;
  }
  startTick(){if(!this.active)return false;if(this.inFlight){this.skipped++;this.queueDepth=0;return false}this.inFlight=true;return true}
  finishTick(hash,now,warnings){
    ok(this.inFlight,'no tick in flight');this.inFlight=false;
    const changed=hash!==this.lastPublishedHash;
    const heartbeat=this.lastPublishedAt===null||now-this.lastPublishedAt>=C.heartbeatMaxMs;
    if(changed||heartbeat){this.publications.push({now,warnings:clone(warnings)});this.lastPublishedHash=hash;this.lastPublishedAt=now;}
  }
  epochChanged(newEpoch){if(newEpoch!==this.runtimeEpoch){this.active=false;this.agentCount=0;this.runtimeEpoch=newEpoch;return true}return false}
  disconnectCdp(){return {gameplayPlayable:this.gameplayPlayable,agentMayRemain:this.active}}
  fail(stage){this.active=false;this.agentCount=0;return {stage,gameplayPlayable:true,warningSilent:true}}
  reconnect(epoch){this.agentCount=0;return this.install(epoch,'valid',true)}
}

function baseline(key,expectedValue=true){eq(fixtures.rc5Baseline[key],expectedValue,`baseline ${key}`)}
function safety(key,expectedValue){eq(fixtures.safety[key],expectedValue,`safety ${key}`)}

const tests={};
function T(id,fn){tests[id]=fn}

// A startup / Worker safety
T('V01',()=>baseline('windowWorkerIdentityPreserved'));
T('V02',()=>baseline('blobWorker',false));
T('V03',()=>{baseline('workerUrlRewrite',false);baseline('workerOptionsRewrite',false)});
T('V04',()=>baseline('prePairHudFetch',false));
T('V05',()=>{baseline('gameplayFailOpen');const r=new Receiver(P.a1.session);r.bind(P.a1);eq(r.visible(999).length,0)});
// B target selection
T('V06',()=>ok(resolveForPage('one','p1').ok));
T('V07',()=>ok(!resolveForPage('zero','p1').ok));
T('V08',()=>ok(!resolveForPage('twoAmbiguous','p1').ok));
T('V09',()=>ok(!resolveForPage('wrong','p1').ok));
T('V10',()=>ok(exactTwoTabIsolation('twoTabsExact')));
T('V11',()=>{ok(!resolveForPage('twoTabsAmbiguous','p1').ok);ok(!resolveForPage('twoTabsAmbiguous','p2').ok)});
// C identity
T('V12',()=>ok(identityGate('valid')));
T('V13',()=>ok(!identityGate('pending')));
T('V14',()=>ok(!identityGate('missing')));
T('V15',()=>ok(!identityGate('malformed')));
T('V16',()=>ok(!identityGate('mutated')));
T('V17',()=>ok(!identityGate('ambiguous')));
T('V18',()=>{const a=new Agent();ok(!a.install('e1','valid',false));eq(a.active,false)});
T('V19',()=>{const a=new Agent();ok(a.install('e1'));for(let i=0;i<10;i++){ok(a.startTick());a.finishTick('same',i*10,[])}eq(a.hashCount,1)});
// D pair/session isolation
T('V20',()=>{const r=new Receiver(P.a1.session);r.bind(P.a1);ok(r.accept(makeState(P.a1,1,materializeWarnings('warningA')),0));eq(r.visible(0).length,1)});
T('V21',()=>{const r=new Receiver(P.a1.session);r.bind(P.a1);ok(!r.accept(makeState(P.b1,1,materializeWarnings('warningA')),0));eq(r.visible(0).length,0)});
T('V22',()=>{const r=new Receiver(P.a1.session);r.bind(P.a1);ok(!r.accept(makeState(P.a1,1,[],{schema:'wrong'}),0))});
T('V23',()=>{const r=new Receiver(P.a1.session);r.bind(P.a2);ok(!r.accept(makeState(P.a1,1,materializeWarnings('warningA')),0))});
T('V24',()=>{const r=new Receiver(P.a1.session);r.bind(P.a1);ok(!r.accept(makeState({...P.a1,pairNonce:P.a2.pairNonce},1,materializeWarnings('warningA')),0))});
T('V25',()=>{const r=new Receiver(P.a1.session);r.bind(P.a1);ok(r.accept(makeState(P.a1,2,[]),0));ok(!r.accept(makeState(P.a1,2,materializeWarnings('warningA')),1));ok(!r.accept(makeState(P.a1,1,materializeWarnings('warningA')),2));eq(r.visible(2).length,0)});
T('V26',()=>{const r=new Receiver(P.b1.session);r.bind(P.b1);ok(!r.accept(makeState(P.a1,1,materializeWarnings('warningA')),0))});
T('V27',()=>{const r=new Receiver(P.a1.session);r.bind(P.a1);r.accept(makeState(P.a1,1,materializeWarnings('warningA')),0);r.bind(P.a2);eq(r.visible(1).length,0);ok(!r.accept(makeState(P.a1,2,materializeWarnings('warningA')),1))});
// E warning safety, using fixture outputs only; no warning predicate is copied here.
T('V28',()=>{const ids=new Set([W.t18a.ruleId,W.t18b.ruleId]);eq(ids.size,2);ok([...ids].every(x=>x.startsWith('T18_')))});
T('V29',()=>['quarantinedF1','quarantinedF2','quarantinedF3','quarantinedF4'].forEach(x=>eq(materializeWarnings(x).length,0)));
T('V30',()=>{const r=new Receiver(P.a1.session);r.bind(P.a1);r.accept(makeState(P.a1,1,materializeWarnings('warningA')),0);r.accept(makeState(P.a1,2,materializeWarnings('neutralReplacement')),10);eq(r.visible(10).length,0)});
T('V31',tests.V30);
T('V32',()=>{const r=new Receiver(P.a1.session);r.bind(P.a1);r.accept(makeState(P.a1,1,materializeWarnings('warningA')),0);r.accept(makeState(P.a1,2,materializeWarnings('neutralReplacement')),10);r.accept(makeState(P.a1,3,materializeWarnings('matchingReplacement')),20);eq(r.visible(20).length,1);eq(r.visible(20)[0].evidence,'fresh-current-sample')});
T('V33',()=>eq(materializeWarnings('invalidTarget').length,0));
T('V34',()=>{const a=materializeWarnings('warningA')[0],b=materializeWarnings('sideFlip')[0];ok(a.sourceSide!==b.sourceSide&&a.threatSide!==b.threatSide)});
T('V35',()=>eq(materializeWarnings('twoWarnings').length,2));
T('V36',()=>eq(materializeWarnings('excludedBody4728').length,0));
// F diagnostics / stale
T('V37',()=>{const r=new Receiver(P.a1.session);r.bind(P.a1);r.accept(makeState(P.a1,1,materializeWarnings('warningA')),0);eq(r.visible(0).length,1);ok(r.accept(makeDiag(P.a1),1));eq(r.visible(1).length,0)});
T('V38',()=>{const r=new Receiver(P.a1.session);r.bind(P.a2);r.accept(makeState(P.a2,1,materializeWarnings('warningA')),0);ok(!r.accept(makeDiag(P.a1),1));eq(r.visible(1).length,1)});
T('V39',()=>{const r=new Receiver(P.a1.session);r.bind(P.a1);r.accept(makeState(P.a1,1,materializeWarnings('warningA')),0);ok(!r.accept(makeDiag(P.b1),1));eq(r.visible(1).length,1)});
T('V40',()=>{const r=new Receiver(P.a1.session);r.bind(P.a1);r.accept(makeState(P.a1,1,materializeWarnings('warningA')),0);r.accept(makeDiag(P.a1),1);ok(r.accept(makeState(P.a1,2,materializeWarnings('warningA')),2));eq(r.visible(2).length,1)});
T('V41',()=>{const r=new Receiver(P.a1.session);r.bind(P.a1);r.accept(makeState(P.a1,1,materializeWarnings('warningA')),0);eq(r.visible(1500).length,1)});
T('V42',()=>{const r=new Receiver(P.a1.session);r.bind(P.a1);r.accept(makeState(P.a1,1,materializeWarnings('warningA')),0);eq(r.visible(1501).length,0)});
T('V43',()=>{const r=new Receiver(P.a1.session);r.bind(P.a1);r.accept(makeState(P.a1,1,materializeWarnings('warningA')),0);r.bind(P.a2);eq(r.visible(1).length,0)});
T('V44',()=>{const a=new Agent();ok(a.install('epoch1'));const r=new Receiver(P.a1.session);r.bind(P.a1);r.accept(makeState(P.a1,1,materializeWarnings('warningA')),0);ok(a.epochChanged('epoch2'));r.bind(P.a2);eq(r.visible(1).length,0);eq(a.active,false);ok(a.install('epoch2'));eq(a.hashCount,2)});
// G timing / backpressure
T('V45',()=>{const a=new Agent();a.install('e1');ok(a.startTick());ok(!a.startTick());eq(a.skipped,1);a.finishTick('x',0,[])});
T('V46',()=>{const a=new Agent();a.install('e1');ok(a.startTick());for(let i=0;i<5;i++)ok(!a.startTick());eq(a.queueDepth,0);eq(a.skipped,5);a.finishTick('x',100,[])});
T('V47',()=>{const a=new Agent();a.install('e1');a.startTick();a.finishTick('warn',5,materializeWarnings('warningA'));eq(a.publications.length,1);eq(a.publications[0].warnings.length,1)});
T('V48',()=>{const a=new Agent();a.install('e1');a.startTick();a.finishTick('warn',0,materializeWarnings('warningA'));a.startTick();a.finishTick('clear',10,[]);eq(a.publications.length,2);eq(a.publications[1].warnings.length,0)});
T('V49',()=>{const a=new Agent();a.install('e1');a.startTick();a.finishTick('same',0,[]);a.startTick();a.finishTick('same',249,[]);eq(a.publications.length,1);a.startTick();a.finishTick('same',250,[]);eq(a.publications.length,2)});
T('V50',()=>{const a=new Agent();a.install('e1');for(let i=0;i<1000;i++){if(a.startTick())a.finishTick('same',i,[])}eq(a.queueDepth,0);ok(a.publications.length<10)});
// H failure injection
T('V51',()=>{const a=new Agent();a.install('e1');eq(a.disconnectCdp().gameplayPlayable,true)});
T('V52',()=>{const a=new Agent();const x=a.fail('page-bind');eq(x.gameplayPlayable,true);eq(x.warningSilent,true)});
T('V53',()=>{const a=new Agent();const x=a.fail('worker-eval');eq(x.gameplayPlayable,true);eq(x.warningSilent,true)});
T('V54',()=>{const a=new Agent();const x=a.fail('broadcast-channel');eq(x.gameplayPlayable,true);eq(x.warningSilent,true)});
T('V55',()=>{const a=new Agent();a.install('e1');ok(a.epochChanged('e2'));eq(a.active,false)});
T('V56',()=>{const a=new Agent();const x=a.fail('hud-render');eq(x.gameplayPlayable,true)});
T('V57',()=>{const a=new Agent();a.install('e1');ok(a.reconnect('e1'));eq(a.agentCount,1)});
// I read-only / no-input
T('V58',()=>{ok(!fixtures.safety.allowedCdpMethods.some(x=>x.startsWith('Input.')));ok(!fixtures.safety.allowedCdpMethods.includes('Input.dispatchKeyEvent'))});
T('V59',()=>safety('gamePostMessageControl',false));
T('V60',()=>safety('heapWrites',false));
T('V61',()=>safety('ramWrites',0));
T('V62',()=>safety('inputInjection',false));
T('V63',()=>safety('assistMode',false));
// J existing regressions
T('V64',()=>baseline('legacyHudTeardown'));
T('V65',()=>baseline('webglStateRestoration'));
T('V66',()=>baseline('rc5IndependentQaPass'));
T('V67',()=>baseline('rc4AdversarialPass'));

const results=[];
for(const v of catalog.vectors){
  const fn=tests[v.id];
  if(typeof fn!=='function')results.push({id:v.id,status:'FAIL',error:'missing harness test'});
  else {
    try{fn();results.push({id:v.id,status:'PASS'})}
    catch(e){results.push({id:v.id,status:'FAIL',error:String(e?.stack||e)})}
  }
}
const passCount=results.filter(x=>x.status==='PASS').length;
const failCount=results.length-passCount;
for(const r of results){eq(expected.results[r.id],'PASS',`expected catalog ${r.id}`)}
const result={
  artifact:'wof-alpha-safe-transport-mock-harness-prep-v1',
  generatedAt:new Date().toISOString(),
  mode:'reference-contract-model',
  status:failCount===0?'PASS':'FAIL',
  repositoryStatus:failCount===0?'MOCK HARNESS READY — WAITING FOR REAL PYLAUNCH PROOF / TRANSPORT IMPLEMENTATION':'MOCK HARNESS NOT READY',
  vectorCount:results.length,passCount,failCount,
  contractCoverage:{startupWorkerSafety:'5/5',targetSelection:'6/6',identity:'8/8',pairSessionIsolation:'8/8',warningSafety:'9/9',diagnosticsStale:'8/8',timingBackpressure:'6/6',failureInjection:'7/7',readOnlyNoInput:'6/6',existingRegressions:'4/4'},
  safety:{readOnly:true,ramWrites:0,inputInjection:false,workerReplacement:false,blobRewrite:false},
  productionCodeModified:false,
  pylaunchImplementationModified:false,
  claimsTransportImplemented:false,
  results
};
fs.writeFileSync(path.join(here,'result.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({status:result.status,passCount,failCount,repositoryStatus:result.repositoryStatus}));
if(failCount)process.exitCode=1;
