(function(root){
'use strict';
const VERSION='wof-alpha-core-rc3';
const SCHEMA='wof-alpha-v2';
const TARGETS={0:'P1',4:'P2',8:'P3'};
const ROM_IDENTITY={
  version:'maincpu-logical-sha256-v1',
  game:'wof',
  set:'wof',
  description:'Warriors of Fate (World 921031)',
  logicalBytes:0x100000,
  expectedSha256:'5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62',
  canonicalHalfSha1:['10b8cb53a4600e3e76f471a3eee8a600e93096fc','52c2d05279623d93b27856e6b76830796a089eae'],
  vectorSp:0x00FF62EE,
  vectorPc:0x0000754A,
  dispatchOffset:0x25DC,
  dispatchEntries:[0x06F4E4,0x07494C,0x071ADA,0x077B8E,0x07C6D2],
  maxUniformDelta:0x1000
};
const SHA256_RE=/^[0-9a-f]{64}$/;

const sourceSide=(enemyX,targetX)=>{
  if(!Number.isFinite(enemyX)||!Number.isFinite(targetX))return null;
  const dx=targetX-enemyX;return dx<-4?'LEFT':dx>4?'RIGHT':'CENTER';
};
const threatSide=(enemyX,targetX)=>{
  if(!Number.isFinite(enemyX)||!Number.isFinite(targetX))return null;
  const dx=enemyX-targetX;return dx<-4?'LEFT':dx>4?'RIGHT':'CENTER';
};
const t16b4=s=>!!(s&&s.type===16&&s.attack===0&&s.body===4856&&s.frameEnd===0x851ae&&s.next===0x84c44&&s.value30===0xffff&&s.timer34===1&&s.action2A===4&&s.b2B===4&&(s.state99===0||s.state99===2||s.state99===4));
const t20=(s,b)=>!!(s&&s.type===20&&s.attack===0&&s.state99===2&&s.action2A===4&&s.b2B===b&&s.body===0&&s.frameEnd===0x839c4&&s.next===0x82b0a&&s.value30===0x100000&&s.timer34===20&&s.payload6C===0);
const d867=s=>!!(s&&s.attack===0&&s.body===2872&&s.frameEnd===0x867ba&&s.next===0x85ece&&s.value30===0x100000&&s.payload6C===2784&&s.action2A===4&&s.b2B===2&&(s.state99===2||s.state99===4)&&s.timer34===6);
const d881=s=>!!(s&&s.attack===0&&s.body===2872&&s.frameEnd===0x8811e&&s.next===0x879e2&&s.value30===0x100000&&s.payload6C===2784&&s.action2A===4&&s.b2B===2&&(s.state99===2||s.state99===4)&&s.timer34===6);
const t18a=s=>!!(s&&s.type===18&&s.attack===0&&s.state99===2&&s.action2A===2&&s.b2B===4&&s.body===7512&&s.frameEnd===0x8bbb2&&s.next===0x8b290&&s.value30===0x180001&&s.timer34===4&&s.payload6C===0);
const t18b=s=>!!(s&&s.type===18&&s.attack===0&&s.state99===2&&s.action2A===2&&s.b2B===4&&s.body===7520&&s.frameEnd===0x8bbde&&s.next===0x8b2a4&&s.value30===0x180001&&s.timer34===4&&s.payload6C===0);

const FROZEN_RULES=[
  {id:'T16_B4_DANGER_40',freezeStatus:'freeze-candidate',releaseStatus:'quarantined-rc3-lifecycle',production:false,trigger:'entry',researchHorizonMs:40,warningClass:'IMMINENT_DANGER',attackSpecific:false,attack:null,timingClass:'IMMINENT',validatedLeadLabel:'约 9–21 ms',predicateSource:'WOF-038 -> WOF-041R -> WOF-051 audit',base:t16b4},
  {id:'T20_5136_B0_TO_B255_1250',freezeStatus:'freeze-candidate',releaseStatus:'quarantined-rc3-lifecycle',production:false,trigger:'transition',researchHorizonMs:1250,warningClass:'ATTACK',attackSpecific:true,attack:5136,timingClass:'EARLY',validatedLeadLabel:'约 381–640 ms',predicateSource:'WOF-038 patched by WOF-043R; WOF-051 audit',base:s=>t20(s,255)},
  {id:'D867BA_3232_TM6_220',freezeStatus:'freeze-candidate',releaseStatus:'quarantined-rc3-lifecycle',production:false,trigger:'entry',researchHorizonMs:220,warningClass:'ATTACK',attackSpecific:true,attack:3232,timingClass:'SHORT',validatedLeadLabel:'约 99–109 ms',predicateSource:'WOF-038 patched by WOF-041R/WOF-043R; WOF-051 audit',base:d867},
  {id:'D8811E_3232_TM6_135',freezeStatus:'freeze-candidate',releaseStatus:'quarantined-rc3-lifecycle',production:false,trigger:'entry',researchHorizonMs:135,warningClass:'ATTACK',attackSpecific:true,attack:3232,timingClass:'SHORT',validatedLeadLabel:'约 99–119 ms',predicateSource:'WOF-038 patched by WOF-043R; WOF-051 audit',base:d881},
  {id:'T18_5440_CYCLE_BODY7512_TM4_LEVEL_90',freezeStatus:'freeze-candidate',releaseStatus:'alpha-rc3-current-level',production:true,trigger:'current-level',researchHorizonMs:90,warningClass:'ATTACK',attackSpecific:true,attack:5440,timingClass:'IMMINENT',validatedLeadLabel:'约 62–71 ms',predicateSource:'WOF-045R -> production-shadow in WOF-046R; WOF-051 audit',base:t18a,match:t18a},
  {id:'T18_5424_CYCLE_BODY7520_TM4_LEVEL_90',freezeStatus:'freeze-candidate',releaseStatus:'alpha-rc3-current-level',production:true,trigger:'current-level',researchHorizonMs:90,warningClass:'ATTACK',attackSpecific:true,attack:5424,timingClass:'IMMINENT',validatedLeadLabel:'约 69–70 ms',predicateSource:'WOF-045R -> production-shadow in WOF-046R; WOF-051 audit',base:t18b,match:t18b}
];
const RULES=FROZEN_RULES.filter(r=>r.production);
const QUARANTINED_RULES=FROZEN_RULES.filter(r=>!r.production);

function validateIdentityProbe(p){
  const reasons=[];
  if(!p||p.moduleOk!==true)reasons.push('WASM module identity missing');
  if(!Number.isInteger(p?.ramBase)||p.ramBase<=0)reasons.push('CPS RAM base missing');
  if(p?.ramWithinHeap!==true)reasons.push('CPS RAM window outside heap');
  const si=p?.selfIndexes;
  if(!Array.isArray(si)||si.length!==3||si[0]!==0||si[1]!==4||si[2]!==8)reasons.push('P1/P2/P3 self-index mismatch');

  const loc=p?.romLocator;
  if(!loc||loc.source!=='browser-wasm-rom')reasons.push('Browser ROM locator missing');
  else{
    if(loc.candidateCount!==1)reasons.push('ROM locator must identify exactly one candidate');
    if(loc.vectorSp!==ROM_IDENTITY.vectorSp||loc.vectorPc!==ROM_IDENTITY.vectorPc)reasons.push('ROM locator reset-vector mismatch');
    if(loc.dispatchOffset!==ROM_IDENTITY.dispatchOffset)reasons.push('ROM locator dispatch offset mismatch');
    const vals=loc.dispatchEntries;
    if(!Array.isArray(vals)||vals.length!==ROM_IDENTITY.dispatchEntries.length)reasons.push('ROM locator dispatch entries missing');
    else{
      const deltas=vals.map((v,i)=>(v-ROM_IDENTITY.dispatchEntries[i])|0),d=deltas[0];
      if(!deltas.every(x=>x===d)||Math.abs(d)>ROM_IDENTITY.maxUniformDelta)reasons.push('ROM locator dispatch sanity mismatch');
      if(Number.isInteger(loc.uniformDelta)&&loc.uniformDelta!==d)reasons.push('ROM locator delta mismatch');
    }
  }

  const rom=p?.romIdentity;
  if(!rom)reasons.push('full CPU-logical SHA-256 missing');
  else{
    if(rom.hashStatus!=='accepted')reasons.push('full CPU-logical SHA-256 not accepted: '+String(rom.hashStatus||'missing'));
    if(rom.source!=='browser-wasm-rom')reasons.push('full hash source mismatch');
    if(rom.logicalBytes!==ROM_IDENTITY.logicalBytes)reasons.push('full hash logical length mismatch');
    const sha=typeof rom.sha256==='string'?rom.sha256:'';
    if(!SHA256_RE.test(sha))reasons.push('full SHA-256 malformed');
    else if(sha!==ROM_IDENTITY.expectedSha256)reasons.push('full SHA-256 mismatch');
  }

  return{
    ok:reasons.length===0,
    reasons,
    signature:reasons.length===0?'wof-world-921031-maincpu-sha256-v1:'+ROM_IDENTITY.expectedSha256.slice(0,16):null,
    evidence:reasons.length===0?'exact 1 MiB CPU-logical SHA-256 equality for wof / World 921031; layout/vector/dispatch used only as locator/sanity evidence':null,
    identity:reasons.length===0?{
      game:ROM_IDENTITY.game,set:ROM_IDENTITY.set,description:ROM_IDENTITY.description,kind:ROM_IDENTITY.version,
      logicalBytes:ROM_IDENTITY.logicalBytes,sha256:ROM_IDENTITY.expectedSha256,canonicalHalfSha1:[...ROM_IDENTITY.canonicalHalfSha1]
    }:null
  };
}

function transportAccepts(message,session){
  return !!(message&&message.schema===SCHEMA&&typeof session==='string'&&session.length>=16&&message.session===session);
}

function normalizeSnapshot(s){
  if(!s)return null;
  const target=TARGETS[s.target7E]||null;
  return{...s,target,sourceSide:s.sourceSide??sourceSide(s.enemyX,s.targetX),threatSide:s.threatSide??threatSide(s.enemyX,s.targetX)};
}

function createEngine(){
  const current=new Map();
  let lastNow=0;
  const stats=Object.fromEntries(RULES.map(r=>[r.id,{matchingSamples:0}]));

  function step(snaps,nowMs){
    const now=Number.isFinite(+nowMs)?+nowMs:Date.now();lastNow=now;
    current.clear();
    for(const raw of (snaps||[])){
      const s=normalizeSnapshot(raw);
      if(s&&Number.isInteger(s.slot))current.set(s.slot,s);
    }
    for(const s of current.values())for(const r of RULES)if(r.match(s))stats[r.id].matchingSamples++;
    return state(now);
  }

  function warningRows(){
    const rows=[];
    for(const [slot,s] of current){
      for(const r of RULES){
        if(!r.match(s))continue;
        const target=TARGETS[s.target7E]||null;
        if(!target||!Number.isFinite(s.enemyX)||!Number.isFinite(s.targetX))continue;
        rows.push({
          ruleId:r.id,freezeStatus:r.freezeStatus,releaseStatus:r.releaseStatus,
          warningClass:r.warningClass,attackSpecific:r.attackSpecific,attack:r.attack,
          target,target7E:s.target7E,sourceSide:sourceSide(s.enemyX,s.targetX),threatSide:threatSide(s.enemyX,s.targetX),
          timingClass:r.timingClass,validatedLeadLabel:r.validatedLeadLabel,publication:'hold-only-current-level',
          evidence:'fresh-current-sample',slot,type:s.type
        });
      }
    }
    const rank=x=>x.timingClass==='IMMINENT'?3:x.timingClass==='SHORT'?2:1;
    rows.sort((a,b)=>rank(b)-rank(a)||a.slot-b.slot||String(a.ruleId).localeCompare(String(b.ruleId)));
    return rows;
  }

  function state(nowMs=lastNow||Date.now()){
    const now=Number.isFinite(+nowMs)?+nowMs:Date.now();
    return{schema:SCHEMA,kind:'state',coreVersion:VERSION,sentAt:now,warnings:warningRows()};
  }
  function diagnostics(){return{
    version:VERSION,schema:SCHEMA,stats:JSON.parse(JSON.stringify(stats)),activeWatches:0,historyWarningRulesEnabled:false,
    productionRules:RULES.map(r=>r.id),quarantinedRules:QUARANTINED_RULES.map(r=>r.id),slots:current.size
  };}
  return{step,state,diagnostics,reset(){current.clear();}};
}

const api={VERSION,SCHEMA,TARGETS,ROM_IDENTITY,FROZEN_RULES,RULES,QUARANTINED_RULES,validateIdentityProbe,transportAccepts,sourceSide,threatSide,normalizeSnapshot,createEngine};
if(typeof module!=='undefined'&&module.exports)module.exports=api;
root.WOFAlphaCore=api;
})(typeof self!=='undefined'?self:globalThis);
