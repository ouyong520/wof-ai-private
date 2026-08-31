(async()=>{
'use strict';
const COPY_ID='WOF-026';
const PROJECT='WOF-AI-PRIVATE';
const VERSION='wof-future-danger-t16-timer-phase-discriminator-v26';
const MARKER='=== WOF FUTURE DANGER T16 TIMER PHASE DISCRIMINATOR V26 JSON ===';
console.log(`[${COPY_ID}] ${PROJECT} ${VERSION}`);
const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);
if(!good(self._0x515056)){
  const until=performance.now()+8000;let hit=null;
  while(performance.now()<until&&!hit){for(const k of Object.getOwnPropertyNames(self)){let v;try{v=self[k]}catch(_){continue}if(good(v)){hit={k,v};break}}if(!hit)await new Promise(r=>setTimeout(r,50));}
  if(!hit)throw new Error(`[${COPY_ID}] WASM module not found. Select the live gstyphoon.js Worker.`);
  self._0x515056=hit.v;self.__WOF_MODULE_GLOBAL_KEY=hit.k;
}
const MOD=self._0x515056,M=MOD.HEAPU8,R=MOD.HEAPU32?.[0x2e39e4>>>2]>>>0;if(!R)throw new Error(`[${COPY_ID}] CPS RAM base missing`);
const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0;
const U16=a=>((B(a)<<8)|B(a+1))>>>0;
const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
const ENEMY=0xFFC0BC,STRIDE=0xE0,SLOTS=20,PLAYERS={0:'P1',4:'P2',8:'P3'};
function objectHex(a){let s='';for(let i=0;i<STRIDE;i++)s+=B(a+i).toString(16).padStart(2,'0');return s;}
function snap(i){
  const a=ENEMY+i*STRIDE,type=U16(a+0x20);if(type>=47)return null;
  const fe=U32(a+0x12),nx=U32(a+0x2C);if(!fe&&!nx)return null;
  const t7=U16(a+0x7E);
  return{a,slot:i,type,target7E:t7,target:PLAYERS[t7]||null,state99:B(a+0x99),action2A:B(a+0x2A),b2B:B(a+0x2B),body:U16(a+0x6E),attack:U16(a+0x70),frameEnd:fe,next:nx,value30:U32(a+0x30),timer34:U16(a+0x34),timer36:U16(a+0x36),timer38:U16(a+0x38),callback64:U32(a+0x64),selectedPtr6A:U16(a+0x6A),payload6C:U16(a+0x6C),status82:U16(a+0x82)};
}
const FAST=new Set(['0/4/2','0/4/4','2/4/2','2/4/4','2/0/0','4/4/2','4/4/4','4/0/0']);
const RULES=[
{id:'T16_FAST_100',horizon:100,status:'demoted-discovery',match:s=>s.type===16&&s.attack===0&&s.body===4856&&s.frameEnd===0x851ae&&s.next===0x84c44&&s.value30===0xffff&&FAST.has(`${s.state99}/${s.action2A}/${s.b2B}`)},
{id:'T16_MID_250',horizon:250,status:'demoted-discovery',match:s=>s.type===16&&s.attack===0&&s.body===4856&&s.state99===2&&s.action2A===4&&s.b2B===2&&s.frameEnd===0x85240&&s.next===0x84c3a&&s.value30===0x100000}
];
const DURATION=120000,INTERVAL=10,JITTER_TOL=15,TAIL=1000,COVERAGE_CHECK=30000,start=performance.now();
const prev=new Map(),cycle=new Map(),armed=new Map(),watches=[],events=[];let wid=0,firstT16AtMs=null,stoppedForCoverage=false;
const diag={polls:0,enemySamples:0,type16Samples:0,type16ActiveEdges:0,signals:0,strictHits:0,jitterBandHits:0,realLateHits:0,hardMisses:0,warningExpired:0,retargets:0,traceUpdates:0,copyId:COPY_ID};
const rawMatchSamples={T16_FAST_100:0,T16_MID_250:0},transitionEntries={T16_FAST_100:0,T16_MID_250:0};
const rk=(slot,id)=>`${slot}|${id}`,r1=x=>Math.round(x*10)/10;
function phaseOf(s){return{timer34:s.timer34,timer36:s.timer36,timer38:s.timer38,callback64:s.callback64,selectedPtr6A:s.selectedPtr6A,payload6C:s.payload6C,status82:s.status82,state99:s.state99,action2A:s.action2A,b2B:s.b2B,body:s.body,frameEnd:s.frameEnd,next:s.next,value30:s.value30};}
function arm(r,s,t){
  const c=cycle.get(s.slot)||0,k=rk(s.slot,r.id);if(armed.get(k)===c)return;armed.set(k,c);
  const tuple=`S${s.state99}/A${s.action2A}/B${s.b2B}`,phase=phaseOf(s);
  watches.push({id:++wid,rule:r.id,status:r.status,type:16,slot:s.slot,cycle:c,horizon:r.horizon,tailHorizon:TAIL,at:t,tuple,entryTarget7E:s.target7E,entryTarget:s.target,entryPhase:phase,entryBytesHex:objectHex(s.a),trace:[{relMs:0,...phase}],resolved:false,warningExpired:false,outcome:null,leadMs:null,deltaMs:null,activeAttack:null,targetSame:null,retargets:[],censored:false});
  diag.signals++;events.push({kind:'SIGNAL',rel:r1(t),rule:r.id,slot:s.slot,tuple,target:s.target,timer34:s.timer34,status82:s.status82});
  console.log(`[WOF V26][${COPY_ID}] SIGNAL ${r.id} ${tuple} slot${s.slot} TM=${s.timer34} ST=${s.status82}`);
}
function updateTrace(s,t){
  for(const w of watches){if(w.resolved||w.slot!==s.slot)continue;const p=phaseOf(s),last=w.trace[w.trace.length-1];
    if(last.timer34!==p.timer34||last.timer36!==p.timer36||last.timer38!==p.timer38||last.status82!==p.status82||last.callback64!==p.callback64||last.payload6C!==p.payload6C||last.action2A!==p.action2A||last.b2B!==p.b2B||last.body!==p.body||last.frameEnd!==p.frameEnd||last.next!==p.next||last.value30!==p.value30){
      if(w.trace.length<80)w.trace.push({relMs:r1(t-w.at),...p});diag.traceUpdates++;
    }
  }
}
function deadlines(t){for(const w of watches){if(w.resolved)continue;const age=t-w.at;if(!w.warningExpired&&age>w.horizon){w.warningExpired=true;diag.warningExpired++;}if(age>TAIL){w.resolved=true;w.outcome='hardMiss';diag.hardMisses++;events.push({kind:'HARD_MISS',rel:r1(t),rule:w.rule,slot:w.slot,tuple:w.tuple,ageMs:r1(age),timer34:w.entryPhase.timer34});}}}
function resolveActive(s,t){if(s.type!==16)return;diag.type16ActiveEdges++;for(const w of watches){if(w.resolved||w.slot!==s.slot)continue;const lead=t-w.at;if(lead<0||lead>TAIL)continue;w.resolved=true;w.leadMs=r1(lead);w.deltaMs=r1(lead-w.horizon);w.activeAttack=s.attack;w.targetSame=w.entryTarget7E===s.target7E;w.activeTarget=s.target;w.activePhase=phaseOf(s);if(lead<=w.horizon){w.outcome='strictHit';diag.strictHits++;}else if(lead<=w.horizon+JITTER_TOL){w.outcome='jitterBandHit';diag.jitterBandHits++;}else{w.outcome='realLateHit';diag.realLateHits++;}events.push({kind:w.outcome,rel:r1(t),rule:w.rule,slot:s.slot,tuple:w.tuple,leadMs:w.leadMs,deltaMs:w.deltaMs,attack:s.attack,target:s.target,timer34:w.entryPhase.timer34});console.log(`[WOF V26][${COPY_ID}] ${w.outcome} ${w.rule} ${w.tuple} TM=${w.entryPhase.timer34} ${w.leadMs}ms A=${s.attack}`);}cycle.set(s.slot,(cycle.get(s.slot)||0)+1);}
await new Promise(resolve=>{const id=setInterval(()=>{const t=performance.now()-start;diag.polls++;deadlines(t);for(let i=0;i<SLOTS;i++){const s=snap(i),p=prev.get(i)||null;if(!s){if(p){for(const w of watches)if(!w.resolved&&w.slot===i){w.resolved=true;w.censored=true;w.outcome='censored';}}prev.delete(i);continue;}diag.enemySamples++;if(s.type===16){diag.type16Samples++;if(firstT16AtMs==null)firstT16AtMs=r1(t);}if(p&&p.type!==s.type){for(const w of watches)if(!w.resolved&&w.slot===i){w.resolved=true;w.censored=true;w.outcome='censored';}cycle.set(i,(cycle.get(i)||0)+1);}if(p&&p.attack===0&&s.attack!==0)resolveActive(s,t);if(s.type===16){for(const r of RULES){const m=r.match(s),pm=!!(p&&p.type===16&&r.match(p));if(m)rawMatchSamples[r.id]++;if(m&&!pm){transitionEntries[r.id]++;arm(r,s,t);}}updateTrace(s,t);for(const w of watches){if(w.resolved||w.slot!==i)continue;if(w.entryTarget7E!==s.target7E){const last=w.retargets.at(-1)?.to7E??w.entryTarget7E;if(last!==s.target7E){w.retargets.push({rel:r1(t-w.at),from7E:last,to7E:s.target7E,from:PLAYERS[last]||null,to:s.target});diag.retargets++;}}}}prev.set(i,s);}if(t>=COVERAGE_CHECK&&diag.type16Samples===0){stoppedForCoverage=true;clearInterval(id);resolve();return;}if(t>=DURATION){clearInterval(id);for(const w of watches)if(!w.resolved){w.resolved=true;w.censored=true;w.outcome='censored';}resolve();}},INTERVAL);});
const blank=(r,id=r.id)=>({rule:id,status:r.status,horizonMs:r.horizon,jitterToleranceMs:JITTER_TOL,tailHorizonMs:TAIL,signals:0,evaluable:0,strictHit:0,jitterBandHit:0,realLateHit:0,hardMiss:0,censored:0,strictRate:null,jitterCorrectedRate:null,tailHitRate:null,leads:[],attackCounts:{},targetSame:0,targetTotal:0});
const ruleStats={},tupleStats={},timerStats={};for(const r of RULES)ruleStats[r.id]=blank(r);
for(const w of watches){const r=RULES.find(x=>x.id===w.rule),tk=`${w.rule}|${w.tuple}`,tmk=`${tk}|TM${w.entryPhase.timer34}`;if(!tupleStats[tk])tupleStats[tk]=blank(r,tk);if(!timerStats[tmk])timerStats[tmk]={...blank(r,tmk),timer34:w.entryPhase.timer34};for(const q of [ruleStats[w.rule],tupleStats[tk],timerStats[tmk]]){q.signals++;if(w.censored){q.censored++;continue;}q.evaluable++;if(w.outcome==='strictHit')q.strictHit++;else if(w.outcome==='jitterBandHit')q.jitterBandHit++;else if(w.outcome==='realLateHit')q.realLateHit++;else if(w.outcome==='hardMiss')q.hardMiss++;if(w.leadMs!=null){q.leads.push(w.leadMs);q.attackCounts[String(w.activeAttack)]=(q.attackCounts[String(w.activeAttack)]||0)+1;if(w.targetSame!=null){q.targetTotal++;if(w.targetSame)q.targetSame++;}}}}
for(const q of [...Object.values(ruleStats),...Object.values(tupleStats),...Object.values(timerStats)]){q.strictRate=q.evaluable?+(q.strictHit/q.evaluable).toFixed(3):null;q.jitterCorrectedRate=q.evaluable?+((q.strictHit+q.jitterBandHit)/q.evaluable).toFixed(3):null;q.tailHitRate=q.evaluable?+((q.strictHit+q.jitterBandHit+q.realLateHit)/q.evaluable).toFixed(3):null;q.targetSameRate=q.targetTotal?+(q.targetSame/q.targetTotal).toFixed(3):null;q.leads.sort((a,b)=>a-b);q.attackCounts=Object.entries(q.attackCounts).map(([attack,count])=>({attack:+attack,count})).sort((a,b)=>b.count-a.count);}
const knownLabel=off=>{if(off>=4&&off<=11)return'XY_REGION';if(off===0x2A)return'ACTION2A';if(off===0x2B)return'B2B';if(off===0x34||off===0x35)return'TIMER34';if(off>=0x64&&off<=0x67)return'CALLBACK64';if(off===0x6A||off===0x6B)return'SELECTED_PTR_CACHE';if(off===0x6C||off===0x6D)return'PAYLOAD6C';if(off===0x6E||off===0x6F)return'BODY';if(off===0x70||off===0x71)return'ATTACK';if(off===0x7E||off===0x7F)return'TARGET_SELECTOR';if(off===0x82||off===0x83)return'STATUS82';if(off===0x99)return'STATE99';return null;};
function byteAt(hex,off){return parseInt(hex.slice(off*2,off*2+2),16);}
function byteDiscriminators(rows){
  const yes=rows.filter(w=>w.outcome==='strictHit'||w.outcome==='jitterBandHit'),no=rows.filter(w=>w.outcome==='realLateHit'||w.outcome==='hardMiss');if(yes.length<2||no.length<2)return[];
  const out=[];for(let off=0;off<STRIDE;off++){const ys=[...new Set(yes.map(w=>byteAt(w.entryBytesHex,off)))].sort((a,b)=>a-b),ns=[...new Set(no.map(w=>byteAt(w.entryBytesHex,off)))].sort((a,b)=>a-b);if(ys.some(v=>ns.includes(v)))continue;out.push({offset:`0x${off.toString(16).toUpperCase().padStart(2,'0')}`,known:knownLabel(off),deadlineHitValues:ys,deadlineMissValues:ns,deadlineHitN:yes.length,deadlineMissN:no.length});}
  return out.slice(0,48);
}
const discriminators={};for(const r of RULES){const rows=watches.filter(w=>w.rule===r.id&&!w.censored);discriminators[r.id]=byteDiscriminators(rows);for(const tk of [...new Set(rows.map(w=>w.tuple))]){const rr=rows.filter(w=>w.tuple===tk);const d=byteDiscriminators(rr);if(d.length)discriminators[`${r.id}|${tk}`]=d;}}
const coverageStatus=stoppedForCoverage?'NO_T16_IN_FIRST_30S':diag.type16Samples>0&&diag.signals===0?'T16_PRESENT_NO_RULE_ENTRY':'T16_RULE_COVERAGE';
const out={copyId:COPY_ID,project:PROJECT,version:VERSION,expectedMarker:MARKER,readOnly:true,ramWrites:0,durationRequestedMs:DURATION,actualDurationMs:r1(performance.now()-start),intervalMs:INTERVAL,jitterToleranceMs:JITTER_TOL,tailHorizonMs:TAIL,coverageCheckMs:COVERAGE_CHECK,coverageStatus,firstT16AtMs,model:{purpose:'V25 falsified broad T16 FAST<=100 and MID<=250 as universal production rules in a fresh room. V26 searches for a latent pre-active phase discriminator, prioritizing enemy+0x34 timer and nearby state while preserving exact known signatures.',targetPolicy:'live enemy+0x7E authoritative',activeConvention:'enemy+0x70 U16 0->nonzero; not exact damage/hitbox onset',byteDiscriminators:'Entry-object byte separation is hypothesis generation only. XY/geometry or unknown bytes are not causal proof; require prospective validation.'},diagnostics:{...diag,rawMatchSamples,transitionEntries},ruleStats,tupleStats:Object.values(tupleStats).sort((a,b)=>b.signals-a.signals),timerPhaseStats:Object.values(timerStats).sort((a,b)=>b.signals-a.signals),entryByteDiscriminators:discriminators,watches,events:events.slice(-300)};
self.__WOF_V26_RESULT=out;console.log(MARKER);console.log(JSON.stringify(out,null,2));return out;
})().catch(e=>{console.error('[WOF-026] ERROR',e);throw e;});
