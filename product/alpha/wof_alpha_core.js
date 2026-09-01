(function(root){
'use strict';
const VERSION='wof-alpha-core-rc2';
const SCHEMA='wof-alpha-v2';
const TARGETS={0:'P1',4:'P2',8:'P3'};
const ROM_IDENTITY={
  version:'browser-rom-fingerprint-v1',
  vectorSp:0x00FF62EE,
  vectorPc:0x0000754A,
  dispatchOffset:0x25DC,
  dispatchEntries:[0x06F4E4,0x07494C,0x071ADA,0x077B8E,0x07C6D2],
  maxUniformDelta:0x1000
};

const sourceSide=(enemyX,targetX)=>{
  if(!Number.isFinite(enemyX)||!Number.isFinite(targetX))return null;
  const dx=targetX-enemyX;return dx<-4?'LEFT':dx>4?'RIGHT':'CENTER';
};
const threatSide=(enemyX,targetX)=>{
  if(!Number.isFinite(enemyX)||!Number.isFinite(targetX))return null;
  const dx=enemyX-targetX;return dx<-4?'LEFT':dx>4?'RIGHT':'CENTER';
};
const entry=(base,s,p)=>!!(base(s)&&p&&p.type===s.type&&p.attack===0&&!base(p));
const t16b4=s=>!!(s&&s.type===16&&s.attack===0&&s.body===4856&&s.frameEnd===0x851ae&&s.next===0x84c44&&s.value30===0xffff&&s.timer34===1&&s.action2A===4&&s.b2B===4&&(s.state99===0||s.state99===2||s.state99===4));
const t20=(s,b)=>!!(s&&s.type===20&&s.attack===0&&s.state99===2&&s.action2A===4&&s.b2B===b&&s.body===0&&s.frameEnd===0x839c4&&s.next===0x82b0a&&s.value30===0x100000&&s.timer34===20&&s.payload6C===0);
const d867=s=>!!(s&&s.attack===0&&s.body===2872&&s.frameEnd===0x867ba&&s.next===0x85ece&&s.value30===0x100000&&s.payload6C===2784&&s.action2A===4&&s.b2B===2&&(s.state99===2||s.state99===4)&&s.timer34===6);
const d881=s=>!!(s&&s.attack===0&&s.body===2872&&s.frameEnd===0x8811e&&s.next===0x879e2&&s.value30===0x100000&&s.payload6C===2784&&s.action2A===4&&s.b2B===2&&(s.state99===2||s.state99===4)&&s.timer34===6);
const t18a=s=>!!(s&&s.type===18&&s.attack===0&&s.state99===2&&s.action2A===2&&s.b2B===4&&s.body===7512&&s.frameEnd===0x8bbb2&&s.next===0x8b290&&s.value30===0x180001&&s.timer34===4&&s.payload6C===0);
const t18b=s=>!!(s&&s.type===18&&s.attack===0&&s.state99===2&&s.action2A===2&&s.b2B===4&&s.body===7520&&s.frameEnd===0x8bbde&&s.next===0x8b2a4&&s.value30===0x180001&&s.timer34===4&&s.payload6C===0);

const RULES=[
  {id:'T16_B4_DANGER_40',freezeStatus:'freeze-candidate',releaseStatus:'alpha-rc2-browser-qa',trigger:'entry',horizonMs:40,auditTailMs:150,warningClass:'IMMINENT_DANGER',attackSpecific:false,attack:null,timingClass:'IMMINENT',validatedLeadLabel:'约 9–21 ms',predicateSource:'WOF-038 -> WOF-041R -> WOF-051 audit',base:t16b4,match:(s,p)=>entry(t16b4,s,p)},
  {id:'T20_5136_B0_TO_B255_1250',freezeStatus:'freeze-candidate',releaseStatus:'alpha-rc2-browser-qa',trigger:'transition',horizonMs:1250,auditTailMs:1500,warningClass:'ATTACK',attackSpecific:true,attack:5136,timingClass:'EARLY',validatedLeadLabel:'约 381–640 ms',predicateSource:'WOF-038 patched by WOF-043R; WOF-051 audit',base:s=>t20(s,255),match:(s,p)=>t20(s,255)&&t20(p,0)},
  {id:'D867BA_3232_TM6_220',freezeStatus:'freeze-candidate',releaseStatus:'alpha-rc2-browser-qa',trigger:'entry',horizonMs:220,auditTailMs:350,warningClass:'ATTACK',attackSpecific:true,attack:3232,timingClass:'SHORT',validatedLeadLabel:'约 99–109 ms',predicateSource:'WOF-038 patched by WOF-041R/WOF-043R; WOF-051 audit',base:d867,match:(s,p)=>entry(d867,s,p)},
  {id:'D8811E_3232_TM6_135',freezeStatus:'freeze-candidate',releaseStatus:'alpha-rc2-browser-qa',trigger:'entry',horizonMs:135,auditTailMs:350,warningClass:'ATTACK',attackSpecific:true,attack:3232,timingClass:'SHORT',validatedLeadLabel:'约 99–119 ms',predicateSource:'WOF-038 patched by WOF-043R; WOF-051 audit',base:d881,match:(s,p)=>entry(d881,s,p)},
  {id:'T18_5440_CYCLE_BODY7512_TM4_LEVEL_90',freezeStatus:'freeze-candidate',releaseStatus:'alpha-rc2-browser-qa',trigger:'cycle-level',horizonMs:90,auditTailMs:250,warningClass:'ATTACK',attackSpecific:true,attack:5440,timingClass:'IMMINENT',validatedLeadLabel:'约 62–71 ms',predicateSource:'WOF-045R -> production-shadow in WOF-046R; WOF-051 audit',base:t18a,match:s=>t18a(s)},
  {id:'T18_5424_CYCLE_BODY7520_TM4_LEVEL_90',freezeStatus:'freeze-candidate',releaseStatus:'alpha-rc2-browser-qa',trigger:'cycle-level',horizonMs:90,auditTailMs:250,warningClass:'ATTACK',attackSpecific:true,attack:5424,timingClass:'IMMINENT',validatedLeadLabel:'约 69–70 ms',predicateSource:'WOF-045R -> production-shadow in WOF-046R; WOF-051 audit',base:t18b,match:s=>t18b(s)}
];
const RULE_BY_ID=Object.fromEntries(RULES.map(r=>[r.id,r]));

function validateIdentityProbe(p){
  const reasons=[];
  if(!p||p.moduleOk!==true)reasons.push('WASM module identity missing');
  if(!Number.isInteger(p?.ramBase)||p.ramBase<=0)reasons.push('CPS RAM base missing');
  if(p?.ramWithinHeap!==true)reasons.push('CPS RAM window outside heap');
  const si=p?.selfIndexes;
  if(!Array.isArray(si)||si.length!==3||si[0]!==0||si[1]!==4||si[2]!==8)reasons.push('P1/P2/P3 self-index mismatch');

  const rom=p?.romFingerprint;
  if(!rom||rom.source!=='browser-wasm-rom')reasons.push('positive Browser ROM fingerprint missing');
  else{
    if(rom.vectorSp!==ROM_IDENTITY.vectorSp||rom.vectorPc!==ROM_IDENTITY.vectorPc)reasons.push('ROM reset-vector mismatch');
    if(rom.dispatchOffset!==ROM_IDENTITY.dispatchOffset)reasons.push('ROM dispatch-table offset mismatch');
    const vals=rom.dispatchEntries;
    if(!Array.isArray(vals)||vals.length!==ROM_IDENTITY.dispatchEntries.length)reasons.push('ROM dispatch fingerprint missing');
    else{
      const deltas=vals.map((v,i)=>(v-ROM_IDENTITY.dispatchEntries[i])|0);
      const d=deltas[0];
      if(!deltas.every(x=>x===d)||Math.abs(d)>ROM_IDENTITY.maxUniformDelta)reasons.push('ROM dispatch fingerprint mismatch');
      if(Number.isInteger(rom.uniformDelta)&&rom.uniformDelta!==d)reasons.push('ROM fingerprint delta mismatch');
    }
  }
  return{
    ok:reasons.length===0,
    reasons,
    signature:reasons.length===0?'wofr1-world-921002-browser-rom-v2':null,
    evidence:reasons.length===0?'Browser WASM ROM reset vectors + five-entry type-dispatch executable fingerprint + RAM/self-index layout':null
  };
}

function transportAccepts(message,session){
  return !!(message&&message.schema===SCHEMA&&typeof session==='string'&&session.length>=16&&message.session===session);
}

function normalizeSnapshot(s){
  if(!s)return null;
  const target=TARGETS[s.target7E]||s.target||null;
  return{...s,target,sourceSide:s.sourceSide??sourceSide(s.enemyX,s.targetX),threatSide:s.threatSide??threatSide(s.enemyX,s.targetX)};
}

function createEngine(){
  const prev=new Map(),current=new Map(),cycle=new Map(),armed=new Map(),watches=new Map();
  let nextWatchId=0,lastNow=0;
  const stats=Object.fromEntries(RULES.map(r=>[r.id,{signals:0,resolved:0,runtimeExpiredWithoutActive:0,slotClears:0,episodeDriftClears:0,attackDistribution:{}}]));

  const clearArmedForSlot=slot=>{
    const prefix=slot+'|';
    for(const k of [...armed.keys()])if(k.startsWith(prefix))armed.delete(k);
  };
  const clearSlot=(slot,reason)=>{
    for(const [id,w] of [...watches]){
      if(w.slot!==slot)continue;
      watches.delete(id);
      const st=stats[w.ruleId];
      if(reason==='slotGone'||reason==='typeChanged')st.slotClears++;
      if(reason==='episodeDrift')st.episodeDriftClears++;
    }
    clearArmedForSlot(slot);
  };
  const expire=now=>{
    for(const [id,w] of [...watches]){
      const r=RULE_BY_ID[w.ruleId];
      if(now-w.atMs>r.horizonMs){watches.delete(id);stats[w.ruleId].runtimeExpiredWithoutActive++;}
    }
  };
  const armRule=(r,s,slot,now)=>{
    const c=cycle.get(slot)||0,k=slot+'|'+r.id;
    if(armed.get(k)===c)return;
    armed.set(k,c);
    watches.set(++nextWatchId,{id:nextWatchId,ruleId:r.id,slot,type:s.type,cycle:c,atMs:now});
    stats[r.id].signals++;
  };
  const resolveSlot=(slot,s)=>{
    for(const [id,w] of [...watches]){
      if(w.slot!==slot||w.type!==s.type)continue;
      watches.delete(id);
      const st=stats[w.ruleId];st.resolved++;
      const k=String(s.attack);st.attackDistribution[k]=(st.attackDistribution[k]||0)+1;
    }
  };
  const watchedEpisodeDrift=(slot,s)=>{
    if(!s||s.attack!==0)return false;
    for(const w of watches.values()){
      if(w.slot!==slot||w.type!==s.type)continue;
      const r=RULE_BY_ID[w.ruleId];
      if(r&&!r.base(s))return true;
    }
    return false;
  };

  function step(snaps,nowMs){
    const now=Number.isFinite(+nowMs)?+nowMs:Date.now();lastNow=now;expire(now);
    const incoming=new Map();
    for(const raw of (snaps||[])){const s=normalizeSnapshot(raw);if(s&&Number.isInteger(s.slot))incoming.set(s.slot,s);}
    for(let slot=0;slot<20;slot++){
      const s=incoming.get(slot)||null,p=prev.get(slot)||null;
      if(!s){
        if(p){clearSlot(slot,'slotGone');cycle.set(slot,(cycle.get(slot)||0)+1);}
        prev.delete(slot);current.delete(slot);continue;
      }
      if(p&&p.type!==s.type){
        clearSlot(slot,'typeChanged');
        cycle.set(slot,(cycle.get(slot)||0)+1);
      }

      // ACTIVE edges resolve the currently observed episode before any conservative
      // zero-state continuity invalidation is considered.
      if(p&&p.type===s.type&&p.attack===0&&s.attack!==0){
        resolveSlot(slot,s);
        cycle.set(slot,(cycle.get(slot)||0)+1);
      }else{
        // Browser evidence does not expose a unique spawn/episode id. Therefore RC2
        // refuses to carry a warning through any zero-attack descriptor drift away
        // from the exact rule base. This may shorten coverage, but cannot transfer a
        // watch to a same-type replacement occupying the same slot.
        if(watchedEpisodeDrift(slot,s)){
          clearSlot(slot,'episodeDrift');
          cycle.set(slot,(cycle.get(slot)||0)+1);
        }
        if(s.attack===0&&(!p||p.type!==s.type||p.attack!==0))cycle.set(slot,(cycle.get(slot)||0)+1);
        if(s.attack===0){for(const r of RULES)if(r.match(s,p))armRule(r,s,slot,now);}
      }
      prev.set(slot,s);current.set(slot,s);
    }
    return state(now);
  }

  function warningRows(now){
    expire(now);
    const rows=[];
    for(const w of watches.values()){
      const r=RULE_BY_ID[w.ruleId],s=current.get(w.slot);
      if(!r||!s||s.type!==w.type||s.attack!==0||!r.base(s))continue;
      const target=TARGETS[s.target7E]||null;
      if(!target||!Number.isFinite(s.enemyX)||!Number.isFinite(s.targetX))continue;
      rows.push({
        ruleId:r.id,freezeStatus:r.freezeStatus,releaseStatus:r.releaseStatus,
        warningClass:r.warningClass,attackSpecific:r.attackSpecific,attack:r.attack,
        target,target7E:s.target7E,sourceSide:sourceSide(s.enemyX,s.targetX),
        threatSide:threatSide(s.enemyX,s.targetX),timingClass:r.timingClass,
        validatedLeadLabel:r.validatedLeadLabel,horizonMs:r.horizonMs,
        ageMs:Math.max(0,now-w.atMs),slot:w.slot,type:s.type
      });
    }
    const rank=x=>x.warningClass==='IMMINENT_DANGER'?4:x.timingClass==='IMMINENT'?3:x.timingClass==='SHORT'?2:1;
    rows.sort((a,b)=>rank(b)-rank(a)||a.horizonMs-b.horizonMs||a.slot-b.slot);
    return rows;
  }

  function state(nowMs=lastNow||Date.now()){
    const now=Number.isFinite(+nowMs)?+nowMs:Date.now();
    return{schema:SCHEMA,kind:'state',coreVersion:VERSION,sentAt:now,warnings:warningRows(now)};
  }
  function diagnostics(){return{version:VERSION,schema:SCHEMA,stats:JSON.parse(JSON.stringify(stats)),activeWatches:watches.size,slots:current.size};}
  return{step,state,diagnostics,reset(){prev.clear();current.clear();cycle.clear();armed.clear();watches.clear();}};
}

const api={VERSION,SCHEMA,TARGETS,ROM_IDENTITY,RULES,validateIdentityProbe,transportAccepts,sourceSide,threatSide,normalizeSnapshot,createEngine};
if(typeof module!=='undefined'&&module.exports)module.exports=api;
root.WOFAlphaCore=api;
})(typeof self!=='undefined'?self:globalThis);
