(async()=>{
'use strict';
const COPY_ID='WOF-031';
const PROJECT='WOF-AI-PRIVATE';
const VERSION='wof-future-danger-production-shadow-fingerprint-miner-v31';
const MARKER='=== WOF FUTURE DANGER PRODUCTION SHADOW FINGERPRINT MINER V31 JSON ===';
console.log(`[${COPY_ID}] ${PROJECT} ${VERSION}`);

const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);
if(!good(self._0x515056)){
  const until=performance.now()+8000;let hit=null;
  while(performance.now()<until&&!hit){
    for(const k of Object.getOwnPropertyNames(self)){let v;try{v=self[k]}catch(_){continue}if(good(v)){hit={k,v};break}}
    if(!hit)await new Promise(r=>setTimeout(r,50));
  }
  if(!hit)throw new Error(`[${COPY_ID}] WASM module not found. Select live gstyphoon.js Worker.`);
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

const RULES=[
  {id:'T16_6432_B4_40',status:'production-shadow',level:'IMMINENT',horizon:40,tail:150,expected:[6432],match:s=>s.type===16&&s.attack===0&&s.body===4856&&s.frameEnd===0x851ae&&s.next===0x84c44&&s.value30===0xffff&&s.timer34===1&&s.action2A===4&&s.b2B===4&&(s.state99===0||s.state99===2||s.state99===4)},
  {id:'T30_FAST_100',status:'production-shadow-candidate',level:'NEAR',horizon:100,tail:500,expected:null,match:s=>s.type===30&&s.attack===0&&s.body===1800&&s.state99===0&&s.action2A===0&&s.b2B===0}
];
const DURATION=120000,INTERVAL=10,JITTER_TOL=15,HISTORY_MS=600,LAGS=[20,50,100,250,500],start=performance.now();
const prev=new Map(),cycle=new Map(),armed=new Map(),history=new Map(),watches=[],events=[],activeEdgeEvents=[];let wid=0;
const diag={polls:0,enemySamples:0,activeEdges:0,signals:0,strictHits:0,jitterBandHits:0,realLateHits:0,hardMisses:0,censored:0,retargets:0,copyId:COPY_ID};
const typeSamples={},rawMatchSamples={},transitionEntries={};for(const r of RULES){rawMatchSamples[r.id]=0;transitionEntries[r.id]=0;}
const fpAgg=new Map();
const r1=x=>Math.round(x*10)/10,key=(slot,id)=>`${slot}|${id}`;
function fp(s){return `S${s.state99}/A${s.action2A}/B${s.b2B}|BODY${s.body}|FE${s.frameEnd.toString(16)}|NX${s.next.toString(16)}|V${s.value30.toString(16)}|TM${s.timer34}|P6C${s.payload6C}`;}
function addHist(s,t){let h=history.get(s.slot);if(!h){h=[];history.set(s.slot,h);}h.push({t,s:{...s}});while(h.length&&t-h[0].t>HISTORY_MS)h.shift();}
function nearestPast(slot,targetT){const h=history.get(slot)||[];let best=null,bestD=1e9;for(const x of h){const d=Math.abs(x.t-targetT);if(d<bestD){best=x;bestD=d;}}return bestD<=25?best:null;}
function mineActive(s,t){
  const rec={rel:r1(t),slot:s.slot,type:s.type,attack:s.attack,target:s.target,target7E:s.target7E,side:s.side,absDx:s.absDx,absDy:s.absDy,lags:{}};
  for(const lag of LAGS){const x=nearestPast(s.slot,t-lag);if(!x)continue;const ps=x.s,sig=fp(ps);rec.lags[String(lag)]={actualLagMs:r1(t-x.t),signature:sig,target:ps.target,side:ps.side,absDx:ps.absDx,absDy:ps.absDy};const k=`${lag}|T${s.type}|A${s.attack}|${sig}`;const q=fpAgg.get(k)||{lagMs:lag,type:s.type,activeAttack:s.attack,signature:sig,count:0,targetSame:0,targetTotal:0,sideSame:0,sideTotal:0,leadSamples:[]};q.count++;if(ps.target7E!=null){q.targetTotal++;if(ps.target7E===s.target7E)q.targetSame++;}if(ps.side!=null&&s.side!=null){q.sideTotal++;if(ps.side===s.side)q.sideSame++;}q.leadSamples.push(r1(t-x.t));fpAgg.set(k,q);}
  activeEdgeEvents.push(rec);if(activeEdgeEvents.length>220)activeEdgeEvents.shift();
}
function arm(r,s,t){
  const c=cycle.get(s.slot)||0,k=key(s.slot,r.id);if(armed.get(k)===c)return;armed.set(k,c);
  const w={id:++wid,rule:r.id,status:r.status,level:r.level,slot:s.slot,type:s.type,cycle:c,horizon:r.horizon,tail:r.tail,at:t,entryTarget7E:s.target7E,entryTarget:s.target,entrySide:s.side,entryState99:s.state99,entryAction2A:s.action2A,entryB2B:s.b2B,entryTimer34:s.timer34,entryEnemyX:s.enemyX,entryEnemyY:s.enemyY,entryTargetX:s.targetX,entryTargetY:s.targetY,entryAbsDx:s.absDx,entryAbsDy:s.absDy,resolved:false,outcome:null,leadMs:null,deltaMs:null,activeAttack:null,expectedAttack:null,targetSame:null,sideSame:null,retargets:[],censored:false};
  watches.push(w);diag.signals++;events.push({kind:'SIGNAL',rel:r1(t),rule:r.id,slot:s.slot,type:s.type,target:s.target,side:s.side,state99:s.state99,action2A:s.action2A,b2B:s.b2B,timer34:s.timer34});
}
function updateRetargets(s,t){
  for(const w of watches){if(w.resolved||w.slot!==s.slot||w.type!==s.type)continue;if(w.entryTarget7E!==s.target7E){const last=w.retargets.at(-1)?.to7E??w.entryTarget7E;if(last!==s.target7E){w.retargets.push({rel:r1(t-w.at),from7E:last,to7E:s.target7E,from:PLAYERS[last]||null,to:s.target});diag.retargets++;}}}
}
function resolveActive(s,t){
  diag.activeEdges++;mineActive(s,t);
  for(const w of watches){if(w.resolved||w.slot!==s.slot||w.type!==s.type)continue;const lead=t-w.at;if(lead<0||lead>w.tail)continue;const r=RULES.find(x=>x.id===w.rule);w.resolved=true;w.leadMs=r1(lead);w.deltaMs=r1(lead-w.horizon);w.activeAttack=s.attack;w.expectedAttack=r.expected?r.expected.includes(s.attack):null;w.targetSame=w.entryTarget7E===s.target7E;w.sideSame=w.entrySide===s.side;w.activeTarget=s.target;w.activeSide=s.side;w.activeAbsDx=s.absDx;w.activeAbsDy=s.absDy;if(lead<=w.horizon){w.outcome='strictHit';diag.strictHits++;}else if(lead<=w.horizon+JITTER_TOL){w.outcome='jitterBandHit';diag.jitterBandHits++;}else{w.outcome='realLateHit';diag.realLateHits++;}events.push({kind:w.outcome,rel:r1(t),rule:w.rule,slot:s.slot,leadMs:w.leadMs,deltaMs:w.deltaMs,attack:s.attack,target:s.target,side:s.side,expectedAttack:w.expectedAttack});}
  cycle.set(s.slot,(cycle.get(s.slot)||0)+1);
}
function deadlines(t){for(const w of watches){if(w.resolved)continue;const age=t-w.at;if(age>w.tail){w.resolved=true;w.outcome='hardMiss';diag.hardMisses++;events.push({kind:'HARD_MISS',rel:r1(t),rule:w.rule,slot:w.slot,ageMs:r1(age)});}}}
function publish(t){const entries=[];for(const w of watches){if(w.resolved)continue;const s=prev.get(w.slot);if(!s||s.type!==w.type)continue;entries.push({copyId:COPY_ID,rule:w.rule,status:w.status,level:w.level,slot:w.slot,target:s.target,target7E:s.target7E,remainingMs:Math.max(0,r1(w.horizon-(t-w.at))),side:s.side,enemyX:s.enemyX,enemyY:s.enemyY,targetX:s.targetX,targetY:s.targetY});}self.__WOF_FUTURE_DANGER_MAP_STATE={copyId:COPY_ID,project:PROJECT,version:VERSION,atMs:r1(t),entries};}
await new Promise(resolve=>{const id=setInterval(()=>{
  const t=performance.now()-start;diag.polls++;deadlines(t);
  for(let i=0;i<SLOTS;i++){
    const s=snap(i),p=prev.get(i)||null;
    if(!s){if(p){for(const w of watches)if(!w.resolved&&w.slot===i){w.resolved=true;w.censored=true;w.outcome='censored';diag.censored++;}}prev.delete(i);history.delete(i);continue;}
    diag.enemySamples++;typeSamples['T'+s.type]=(typeSamples['T'+s.type]||0)+1;
    if(p&&p.type!==s.type){for(const w of watches)if(!w.resolved&&w.slot===i){w.resolved=true;w.censored=true;w.outcome='censored';diag.censored++;}cycle.set(i,(cycle.get(i)||0)+1);history.delete(i);}
    addHist(s,t);
    for(const r of RULES){const m=r.match(s),pm=!!(p&&p.type===s.type&&r.match(p));if(m)rawMatchSamples[r.id]++;if(m&&!pm){transitionEntries[r.id]++;arm(r,s,t);}}
    updateRetargets(s,t);
    if(p&&p.attack===0&&s.attack!==0)resolveActive(s,t);
    prev.set(i,s);
  }
  publish(t);
  if(t>=DURATION){clearInterval(id);for(const w of watches)if(!w.resolved){w.resolved=true;w.censored=true;w.outcome='censored';diag.censored++;}publish(t);resolve();}
},INTERVAL);});
function blank(r){return{rule:r.id,status:r.status,horizonMs:r.horizon,tailMs:r.tail,jitterToleranceMs:JITTER_TOL,signals:0,evaluable:0,strictHit:0,jitterBandHit:0,realLateHit:0,hardMiss:0,censored:0,strictRate:null,jitterCorrectedRate:null,tailHitRate:null,expectedAttack:0,expectedAttackTotal:0,expectedAttackRate:null,targetSame:0,targetTotal:0,targetSameRate:null,sideSame:0,sideTotal:0,sideStableRate:null,entryTargets:{},entrySides:{},entryStates:{},leads:[],attackCounts:{}};}
const ruleStats={};for(const r of RULES)ruleStats[r.id]=blank(r);
for(const w of watches){const q=ruleStats[w.rule];q.signals++;q.entryTargets[w.entryTarget]=(q.entryTargets[w.entryTarget]||0)+1;q.entrySides[w.entrySide]=(q.entrySides[w.entrySide]||0)+1;q.entryStates[String(w.entryState99)]=(q.entryStates[String(w.entryState99)]||0)+1;if(w.censored){q.censored++;continue;}q.evaluable++;if(w.outcome==='strictHit')q.strictHit++;else if(w.outcome==='jitterBandHit')q.jitterBandHit++;else if(w.outcome==='realLateHit')q.realLateHit++;else if(w.outcome==='hardMiss')q.hardMiss++;if(w.leadMs!=null){q.leads.push(w.leadMs);q.attackCounts[String(w.activeAttack)]=(q.attackCounts[String(w.activeAttack)]||0)+1;if(w.expectedAttack!=null){q.expectedAttackTotal++;if(w.expectedAttack)q.expectedAttack++;}if(w.targetSame!=null){q.targetTotal++;if(w.targetSame)q.targetSame++;}if(w.sideSame!=null){q.sideTotal++;if(w.sideSame)q.sideSame++;}}}
for(const q of Object.values(ruleStats)){q.strictRate=q.evaluable?+(q.strictHit/q.evaluable).toFixed(3):null;q.jitterCorrectedRate=q.evaluable?+((q.strictHit+q.jitterBandHit)/q.evaluable).toFixed(3):null;q.tailHitRate=q.evaluable?+((q.strictHit+q.jitterBandHit+q.realLateHit)/q.evaluable).toFixed(3):null;q.expectedAttackRate=q.expectedAttackTotal?+(q.expectedAttack/q.expectedAttackTotal).toFixed(3):null;q.targetSameRate=q.targetTotal?+(q.targetSame/q.targetTotal).toFixed(3):null;q.sideStableRate=q.sideTotal?+(q.sideSame/q.sideTotal).toFixed(3):null;q.leads.sort((a,b)=>a-b);q.attackCounts=Object.entries(q.attackCounts).map(([attack,count])=>({attack:+attack,count})).sort((a,b)=>b.count-a.count);}
const fingerprintTop=[...fpAgg.values()].map(q=>({...q,targetSameRate:q.targetTotal?+(q.targetSame/q.targetTotal).toFixed(3):null,sideStableRate:q.sideTotal?+(q.sideSame/q.sideTotal).toFixed(3):null,leadMin:q.leadSamples.length?Math.min(...q.leadSamples):null,leadMax:q.leadSamples.length?Math.max(...q.leadSamples):null})).sort((a,b)=>b.count-a.count||a.lagMs-b.lagMs).slice(0,160);
const out={copyId:COPY_ID,project:PROJECT,version:VERSION,expectedMarker:MARKER,readOnly:true,ramWrites:0,durationRequestedMs:DURATION,actualDurationMs:r1(performance.now()-start),intervalMs:INTERVAL,jitterToleranceMs:JITTER_TOL,model:{purpose:'Integrate the first strong production-shadow warning while mining pre-active fingerprints for the next enemy/attack rules. T16 B4 is promoted to production-shadow after WOF-030 65/65 prospective strict hits; T30 remains production-shadow-candidate.',targetPolicy:'live enemy+0x7E authoritative',activeConvention:'enemy+0x70 U16 0->nonzero; not exact damage/hitbox onset',retargetFix:'Record target changes before resolving an active edge so a target change on the active poll is not lost.',fingerprintPolicy:'Discovery only. Fingerprints are correlations at approximate 20/50/100/250/500ms before ACTIVE and are not causal proof.'},diagnostics:{...diag,typeSamples,rawMatchSamples,transitionEntries},ruleStats,fingerprintTop,activeEdgeEvents,watches,events:events.slice(-320)};
self.__WOF_V31_RESULT=out;console.log(MARKER);console.log(JSON.stringify(out,null,2));return out;
})().catch(e=>{console.error('[WOF-031] ERROR',e);throw e;});