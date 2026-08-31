(async()=>{
'use strict';
const COPY_ID='WOF-036';
const PROJECT='WOF-AI-PRIVATE';
const VERSION='wof-future-danger-adaptive-terminal-miner-v36';
const MARKER='=== WOF FUTURE DANGER ADAPTIVE TERMINAL MINER V36 JSON ===';
console.log(`[${COPY_ID}] ${PROJECT} ${VERSION}`);

const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);
if(!good(self._0x515056)){
  const until=performance.now()+8000;let hit=null;
  while(performance.now()<until&&!hit){
    for(const k of Object.getOwnPropertyNames(self)){let v;try{v=self[k]}catch(_){continue}if(good(v)){hit={k,v};break}}
    if(!hit)await new Promise(r=>setTimeout(r,50));
  }
  if(!hit)throw new Error(`[${COPY_ID}] WASM module not found. Select the live gstyphoon.js Worker.`);
  self._0x515056=hit.v;self.__WOF_MODULE_GLOBAL_KEY=hit.k;
}
const MOD=self._0x515056,M=MOD.HEAPU8,R=MOD.HEAPU32?.[0x2e39e4>>>2]>>>0;
if(!R)throw new Error(`[${COPY_ID}] CPS RAM base missing`);
const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0;
const U16=a=>((B(a)<<8)|B(a+1))>>>0;
const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
const S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v;};
const X=a=>Math.round(S32(a+4)/65536),Y=a=>Math.round(S32(a+8)/65536);
const ENEMY=0xFFC0BC,STRIDE=0xE0,SLOTS=20,PLAYERS={0:'P1',4:'P2',8:'P3'},PBASE={0:0xFFBE1C,4:0xFFBEFC,8:0xFFBFDC};
const side=dx=>dx==null?null:dx<-4?'LEFT':dx>4?'RIGHT':'CENTER';
function snap(i){
  const a=ENEMY+i*STRIDE,type=U16(a+0x20);if(type>=47)return null;
  const fe=U32(a+0x12),nx=U32(a+0x2C);if(!fe&&!nx)return null;
  const t7=U16(a+0x7E),pb=PBASE[t7],ex=X(a),ey=Y(a),tx=pb?X(pb):null,ty=pb?Y(pb):null,dx=tx==null?null:tx-ex,dy=ty==null?null:ty-ey;
  return{slot:i,type,target7E:t7,target:PLAYERS[t7]||null,state99:B(a+0x99),action2A:B(a+0x2A),b2B:B(a+0x2B),body:U16(a+0x6E),attack:U16(a+0x70),frameEnd:fe,next:nx,value30:U32(a+0x30),timer34:U16(a+0x34),timer36:U16(a+0x36),payload6C:U16(a+0x6C),status82:U16(a+0x82),enemyX:ex,enemyY:ey,targetX:tx,targetY:ty,dx,dy,absDx:dx==null?null:Math.abs(dx),absDy:dy==null?null:Math.abs(dy),side:side(dx)};
}
const fp=s=>`S${s.state99}/A${s.action2A}/B${s.b2B}|BODY${s.body}|FE${s.frameEnd.toString(16)}|NX${s.next.toString(16)}|V${s.value30.toString(16)}|TM${s.timer34}|P6C${s.payload6C}`;

const RULES=[
  {id:'T16_6432_B4_40',status:'production-shadow',horizon:40,tail:150,expected:[6432],match:s=>s.type===16&&s.attack===0&&s.body===4856&&s.frameEnd===0x851ae&&s.next===0x84c44&&s.value30===0xffff&&s.timer34===1&&s.action2A===4&&s.b2B===4&&(s.state99===0||s.state99===2||s.state99===4)},
  {id:'T34_3232_TM6_120',status:'production-shadow-candidate',horizon:120,tail:350,expected:[3232],match:s=>s.type===34&&s.attack===0&&s.body===2872&&s.frameEnd===0x8811e&&s.next===0x879e2&&s.value30===0x100000&&s.payload6C===2784&&s.action2A===4&&s.b2B===2&&(s.state99===2||s.state99===4)&&s.timer34===6},
  {id:'T33_3232_TM6_120',status:'production-shadow-candidate',horizon:120,tail:350,expected:[3232],match:s=>s.type===33&&s.attack===0&&s.body===2872&&s.frameEnd===0x867ba&&s.next===0x85ece&&s.value30===0x100000&&s.payload6C===2784&&s.action2A===4&&s.b2B===2&&(s.state99===2||s.state99===4)&&s.timer34===6},
  {id:'T24_5440_V180_TM2_140',status:'prospective-candidate',horizon:140,tail:400,expected:[5440],match:s=>s.type===24&&s.attack===0&&s.state99===2&&s.action2A===2&&s.b2B===4&&s.body===5424&&s.frameEnd===0x8aeec&&s.next===0x8a6c6&&s.value30===0x180001&&s.timer34===2&&s.payload6C===0},
  {id:'T24_5424_V180_TM2_140',status:'prospective-candidate',horizon:140,tail:400,expected:[5424],match:s=>s.type===24&&s.attack===0&&s.state99===2&&s.action2A===2&&s.b2B===4&&s.body===5440&&s.frameEnd===0x8af28&&s.next===0x8a6da&&s.value30===0x180001&&s.timer34===2&&s.payload6C===0},
  {id:'T24_5424_V100_NX756_TM2_140',status:'prospective-candidate',horizon:140,tail:400,expected:[5424],match:s=>s.type===24&&s.attack===0&&s.state99===2&&s.action2A===2&&s.b2B===4&&s.body===5440&&s.frameEnd===0x8af28&&s.next===0x8a756&&s.value30===0x100001&&s.timer34===2&&s.payload6C===0},
  {id:'T24_5440_V100_NX76A_TM2_140',status:'prospective-candidate',horizon:140,tail:400,expected:[5440],match:s=>s.type===24&&s.attack===0&&s.state99===2&&s.action2A===2&&s.b2B===4&&s.body===5424&&s.frameEnd===0x8aeec&&s.next===0x8a76a&&s.value30===0x100001&&s.timer34===2&&s.payload6C===0}
];

const DURATION=120000,INTERVAL=10,JITTER_TOL=15,HISTORY_MS=700,LAGS=[20,50,100,150,250,500],start=performance.now();
const prev=new Map(),history=new Map(),transHist=new Map(),cycle=new Map(),armed=new Map();
const watches=[],events=[],activeEdgeEvents=[];let wid=0;
const diag={polls:0,enemySamples:0,activeEdges:0,knownSignals:0,knownStrictHits:0,knownJitterBandHits:0,knownRealLateHits:0,knownHardMisses:0,censored:0,retargets:0,copyId:COPY_ID};
const typeSamples={},attackTypeCounts={},rawMatchSamples={},transitionEntries={};for(const r of RULES){rawMatchSamples[r.id]=0;transitionEntries[r.id]=0;}
const fpAgg=new Map(),terminalAgg=new Map(),transitionAgg=new Map();
const r1=x=>Math.round(x*10)/10,key=(slot,id)=>`${slot}|${id}`;

function addHist(s,t){
  let h=history.get(s.slot);if(!h){h=[];history.set(s.slot,h);}h.push({t,s:{...s}});while(h.length&&t-h[0].t>HISTORY_MS)h.shift();
  let th=transHist.get(s.slot);if(!th){th=[];transHist.set(s.slot,th);}const sig=fp(s),last=th.at(-1);if(!last||last.sig!==sig||last.attack!==s.attack){th.push({t,sig,attack:s.attack,s:{...s}});}while(th.length&&t-th[0].t>HISTORY_MS)th.shift();
}
function nearestPast(slot,targetT){const h=history.get(slot)||[];let best=null,bestD=1e9;for(const x of h){const d=Math.abs(x.t-targetT);if(d<bestD){best=x;bestD=d;}}return bestD<=25?best:null;}
function addAgg(map,k,seed,lead,targetSame,sideSame){
  const q=map.get(k)||{...seed,count:0,targetSame:0,targetTotal:0,sideSame:0,sideTotal:0,leadSamples:[]};q.count++;
  if(targetSame!=null){q.targetTotal++;if(targetSame)q.targetSame++;}
  if(sideSame!=null){q.sideTotal++;if(sideSame)q.sideSame++;}
  if(lead!=null)q.leadSamples.push(r1(lead));map.set(k,q);
}
function mineActive(p,s,t){
  const atkKey=`T${s.type}|A${s.attack}`;attackTypeCounts[atkKey]=(attackTypeCounts[atkKey]||0)+1;
  const rec={rel:r1(t),slot:s.slot,type:s.type,attack:s.attack,target:s.target,target7E:s.target7E,side:s.side,absDx:s.absDx,absDy:s.absDy,lastZero:null,lags:{},transitions:[]};
  if(p&&p.attack===0){
    const ph=history.get(s.slot)||[];const prevHist=ph.length>=2?ph[ph.length-2]:null;const lead=prevHist?Math.max(0,t-prevHist.t):INTERVAL;
    rec.lastZero={leadMs:r1(lead),signature:fp(p),target:p.target,side:p.side,absDx:p.absDx,absDy:p.absDy};
    const k=`T${s.type}|A${s.attack}|${fp(p)}`;addAgg(terminalAgg,k,{type:s.type,activeAttack:s.attack,signature:fp(p)},lead,p.target7E===s.target7E,p.side!=null&&s.side!=null?p.side===s.side:null);
  }
  for(const lag of LAGS){
    const x=nearestPast(s.slot,t-lag);if(!x)continue;const ps=x.s,sig=fp(ps);
    rec.lags[String(lag)]={actualLagMs:r1(t-x.t),signature:sig,target:ps.target,side:ps.side,absDx:ps.absDx,absDy:ps.absDy};
    const k=`${lag}|T${s.type}|A${s.attack}|${sig}`;addAgg(fpAgg,k,{lagMs:lag,type:s.type,activeAttack:s.attack,signature:sig},t-x.t,ps.target7E===s.target7E,ps.side!=null&&s.side!=null?ps.side===s.side:null);
  }
  const th=(transHist.get(s.slot)||[]).filter(x=>x.t<t&&x.attack===0).slice(-8);
  for(const x of th)rec.transitions.push({ageMs:r1(t-x.t),signature:x.sig,target:x.s.target,side:x.s.side,absDx:x.s.absDx,absDy:x.s.absDy});
  for(let j=1;j<th.length;j++){
    const a=th[j-1],b=th[j],k=`T${s.type}|A${s.attack}|${a.sig}>>${b.sig}`;
    addAgg(transitionAgg,k,{type:s.type,activeAttack:s.attack,from:a.sig,to:b.sig},t-b.t,b.s.target7E===s.target7E,b.s.side!=null&&s.side!=null?b.s.side===s.side:null);
  }
  activeEdgeEvents.push(rec);if(activeEdgeEvents.length>220)activeEdgeEvents.shift();
}
function arm(r,s,t){
  const c=cycle.get(s.slot)||0,k=key(s.slot,r.id);if(armed.get(k)===c)return;armed.set(k,c);
  const w={id:++wid,rule:r.id,status:r.status,slot:s.slot,type:s.type,cycle:c,horizon:r.horizon,tail:r.tail,at:t,entryTarget7E:s.target7E,entryTarget:s.target,entrySide:s.side,entryAbsDx:s.absDx,entryAbsDy:s.absDy,resolved:false,outcome:null,leadMs:null,activeAttack:null,expectedAttack:null,targetSame:null,sideSame:null,retargets:[],censored:false};
  watches.push(w);diag.knownSignals++;events.push({kind:'SIGNAL',rel:r1(t),rule:r.id,slot:s.slot,type:s.type,target:s.target,side:s.side});
}
function updateRetargets(s,t){
  for(const w of watches){if(w.resolved||w.slot!==s.slot||w.type!==s.type)continue;if(w.entryTarget7E!==s.target7E){const last=w.retargets.at(-1)?.to7E??w.entryTarget7E;if(last!==s.target7E){w.retargets.push({rel:r1(t-w.at),from7E:last,to7E:s.target7E});diag.retargets++;}}}
}
function resolveKnown(s,t){
  for(const w of watches){
    if(w.resolved||w.slot!==s.slot||w.type!==s.type)continue;const lead=t-w.at;if(lead<0||lead>w.tail)continue;const r=RULES.find(x=>x.id===w.rule);
    w.resolved=true;w.leadMs=r1(lead);w.activeAttack=s.attack;w.expectedAttack=r.expected.includes(s.attack);w.targetSame=w.entryTarget7E===s.target7E;w.sideSame=w.entrySide!=null&&s.side!=null?w.entrySide===s.side:null;
    if(lead<=w.horizon){w.outcome='strictHit';diag.knownStrictHits++;}else if(lead<=w.horizon+JITTER_TOL){w.outcome='jitterBandHit';diag.knownJitterBandHits++;}else{w.outcome='realLateHit';diag.knownRealLateHits++;}
    events.push({kind:w.outcome,rel:r1(t),rule:w.rule,slot:s.slot,leadMs:w.leadMs,attack:s.attack,expectedAttack:w.expectedAttack});
  }
}
function deadlines(t){for(const w of watches){if(w.resolved)continue;const age=t-w.at;if(age>w.tail){w.resolved=true;w.outcome='hardMiss';diag.knownHardMisses++;events.push({kind:'HARD_MISS',rel:r1(t),rule:w.rule,slot:w.slot,ageMs:r1(age)});}}}
function censorSlot(i){for(const w of watches)if(!w.resolved&&w.slot===i){w.resolved=true;w.censored=true;w.outcome='censored';diag.censored++;}}
function publish(t){
  const entries=[];for(const w of watches){if(w.resolved)continue;const s=prev.get(w.slot);if(!s||s.type!==w.type)continue;entries.push({copyId:COPY_ID,rule:w.rule,status:w.status,slot:w.slot,target:s.target,target7E:s.target7E,remainingMs:Math.max(0,r1(w.horizon-(t-w.at))),side:s.side,enemyX:s.enemyX,enemyY:s.enemyY,targetX:s.targetX,targetY:s.targetY});}
  self.__WOF_FUTURE_DANGER_MAP_STATE={copyId:COPY_ID,project:PROJECT,version:VERSION,atMs:r1(t),entries};
}

await new Promise(resolve=>{
  const id=setInterval(()=>{
    const t=performance.now()-start;diag.polls++;deadlines(t);
    for(let i=0;i<SLOTS;i++){
      const s=snap(i),p=prev.get(i)||null;
      if(!s){if(p)censorSlot(i);prev.delete(i);history.delete(i);transHist.delete(i);continue;}
      diag.enemySamples++;typeSamples['T'+s.type]=(typeSamples['T'+s.type]||0)+1;
      if(p&&p.type!==s.type){censorSlot(i);cycle.set(i,(cycle.get(i)||0)+1);history.delete(i);transHist.delete(i);}
      addHist(s,t);
      for(const r of RULES){const m=r.match(s),pm=!!(p&&p.type===s.type&&r.match(p));if(m)rawMatchSamples[r.id]++;if(m&&!pm){transitionEntries[r.id]++;arm(r,s,t);}}
      updateRetargets(s,t);
      if(p&&p.attack===0&&s.attack!==0){diag.activeEdges++;mineActive(p,s,t);resolveKnown(s,t);cycle.set(s.slot,(cycle.get(s.slot)||0)+1);}
      prev.set(i,s);
    }
    publish(t);
    if(t>=DURATION){clearInterval(id);for(const w of watches)if(!w.resolved){w.resolved=true;w.censored=true;w.outcome='censored';diag.censored++;}resolve();}
  },INTERVAL);
});

const blank=r=>({rule:r.id,status:r.status,horizonMs:r.horizon,tailMs:r.tail,jitterToleranceMs:JITTER_TOL,signals:0,evaluable:0,strictHit:0,jitterBandHit:0,realLateHit:0,hardMiss:0,censored:0,strictRate:null,jitterCorrectedRate:null,tailHitRate:null,expectedAttack:0,expectedAttackTotal:0,expectedAttackRate:null,targetSame:0,targetTotal:0,targetSameRate:null,sideSame:0,sideTotal:0,sideStableRate:null,leads:[],attackCounts:{},entryTargetCounts:{},entrySideCounts:{}});
const knownRuleStats={};for(const r of RULES)knownRuleStats[r.id]=blank(r);
for(const w of watches){
  const q=knownRuleStats[w.rule];q.signals++;q.entryTargetCounts[w.entryTarget||String(w.entryTarget7E)]=(q.entryTargetCounts[w.entryTarget||String(w.entryTarget7E)]||0)+1;q.entrySideCounts[w.entrySide||'null']=(q.entrySideCounts[w.entrySide||'null']||0)+1;
  if(w.censored){q.censored++;continue;}q.evaluable++;
  if(w.outcome==='strictHit')q.strictHit++;else if(w.outcome==='jitterBandHit')q.jitterBandHit++;else if(w.outcome==='realLateHit')q.realLateHit++;else if(w.outcome==='hardMiss')q.hardMiss++;
  if(w.leadMs!=null){q.leads.push(w.leadMs);q.attackCounts[String(w.activeAttack)]=(q.attackCounts[String(w.activeAttack)]||0)+1;q.expectedAttackTotal++;if(w.expectedAttack)q.expectedAttack++;if(w.targetSame!=null){q.targetTotal++;if(w.targetSame)q.targetSame++;}if(w.sideSame!=null){q.sideTotal++;if(w.sideSame)q.sideSame++;}}
}
for(const q of Object.values(knownRuleStats)){
  q.strictRate=q.evaluable?+(q.strictHit/q.evaluable).toFixed(3):null;q.jitterCorrectedRate=q.evaluable?+((q.strictHit+q.jitterBandHit)/q.evaluable).toFixed(3):null;q.tailHitRate=q.evaluable?+((q.strictHit+q.jitterBandHit+q.realLateHit)/q.evaluable).toFixed(3):null;q.expectedAttackRate=q.expectedAttackTotal?+(q.expectedAttack/q.expectedAttackTotal).toFixed(3):null;q.targetSameRate=q.targetTotal?+(q.targetSame/q.targetTotal).toFixed(3):null;q.sideStableRate=q.sideTotal?+(q.sideSame/q.sideTotal).toFixed(3):null;q.leads.sort((a,b)=>a-b);q.attackCounts=Object.entries(q.attackCounts).map(([attack,count])=>({attack:+attack,count})).sort((a,b)=>b.count-a.count);
}
function finalizeAgg(map){
  const arr=[...map.values()];for(const q of arr){q.targetSameRate=q.targetTotal?+(q.targetSame/q.targetTotal).toFixed(3):null;q.sideStableRate=q.sideTotal?+(q.sideSame/q.sideTotal).toFixed(3):null;q.leadSamples.sort((a,b)=>a-b);q.leadMin=q.leadSamples.length?q.leadSamples[0]:null;q.leadMax=q.leadSamples.length?q.leadSamples.at(-1):null;}
  return arr.sort((a,b)=>b.count-a.count||((a.leadMax??1e9)-(b.leadMax??1e9)));
}
const terminalTop=finalizeAgg(terminalAgg).slice(0,120);
const fingerprintTop=finalizeAgg(fpAgg).slice(0,240);
const transitionTop=finalizeAgg(transitionAgg).slice(0,160);
const out={copyId:COPY_ID,project:PROJECT,version:VERSION,expectedMarker:MARKER,readOnly:true,ramWrites:0,durationRequestedMs:DURATION,actualDurationMs:r1(performance.now()-start),intervalMs:INTERVAL,jitterToleranceMs:JITTER_TOL,model:{purpose:'Coverage-adaptive mining after WOF-035 had194 ACTIVE edges but zero T24 coverage. Opportunistically validate known T16/T33/T34 and four exact T24 candidates while mining every actual ACTIVE edge in whatever room types appear.',targetPolicy:'live enemy+0x7E authoritative',activeConvention:'enemy+0x70 U16 0->nonzero; not exact damage/hitbox onset',miningPolicy:'Discovery/correlation only. New mined signatures require a later independent prospective validator before production-shadow.'},diagnostics:{...diag,typeSamples,attackTypeCounts,rawMatchSamples,transitionEntries},knownRuleStats,terminalTop,fingerprintTop,transitionTop,watches,events:events.slice(-400),activeEdgeEvents};
self.__WOF_V36_RESULT=out;console.log(MARKER);console.log(JSON.stringify(out,null,2));return out;
})().catch(e=>{console.error('[WOF-036] ERROR',e);throw e;});
