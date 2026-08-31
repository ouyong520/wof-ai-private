(async()=>{
'use strict';
const COPY_ID='WOF-038';
const PROJECT='WOF-AI-PRIVATE';
const VERSION='wof-future-danger-descriptor-family-validator-v38';
const MARKER='=== WOF FUTURE DANGER DESCRIPTOR FAMILY VALIDATOR V38 JSON ===';
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
  return{slot:i,type,target7E:t7,target:PLAYERS[t7]||null,state99:B(a+0x99),action2A:B(a+0x2A),b2B:B(a+0x2B),body:U16(a+0x6E),attack:U16(a+0x70),frameEnd:fe,next:nx,value30:U32(a+0x30),timer34:U16(a+0x34),payload6C:U16(a+0x6C),enemyX:ex,enemyY:ey,targetX:tx,targetY:ty,dx,dy,absDx:dx==null?null:Math.abs(dx),absDy:dy==null?null:Math.abs(dy),side:side(dx)};
}
const fp=s=>`S${s.state99}/A${s.action2A}/B${s.b2B}|BODY${s.body}|FE${s.frameEnd.toString(16)}|NX${s.next.toString(16)}|V${s.value30.toString(16)}|TM${s.timer34}|P6C${s.payload6C}`;

const t16b4=s=>s&&s.type===16&&s.attack===0&&s.body===4856&&s.frameEnd===0x851ae&&s.next===0x84c44&&s.value30===0xffff&&s.timer34===1&&s.action2A===4&&s.b2B===4&&(s.state99===0||s.state99===2||s.state99===4);
const t20_5136=(s,b)=>s&&s.type===20&&s.attack===0&&s.state99===2&&s.action2A===4&&s.b2B===b&&s.body===0&&s.frameEnd===0x839c4&&s.next===0x82b0a&&s.value30===0x100000&&s.timer34===20&&s.payload6C===0;
const d867=s=>s&&s.attack===0&&s.body===2872&&s.frameEnd===0x867ba&&s.next===0x85ece&&s.value30===0x100000&&s.payload6C===2784&&s.action2A===4&&s.b2B===2&&(s.state99===2||s.state99===4)&&s.timer34===6;
const d881=s=>s&&s.attack===0&&s.body===2872&&s.frameEnd===0x8811e&&s.next===0x879e2&&s.value30===0x100000&&s.payload6C===2784&&s.action2A===4&&s.b2B===2&&(s.state99===2||s.state99===4)&&s.timer34===6;
const t23b0=s=>s&&s.type===23&&s.attack===0&&s.state99===0&&s.action2A===0&&s.b2B===0&&s.body===4920&&s.frameEnd===0x848e2&&s.next===0x83c56&&s.value30===0x140000&&s.timer34===1&&s.payload6C===7904;
const t24a=s=>s&&s.type===24&&s.attack===0&&s.state99===2&&s.action2A===2&&s.b2B===4&&s.body===5424&&s.frameEnd===0x8aeec&&s.next===0x8a6c6&&s.value30===0x180001&&s.timer34===2&&s.payload6C===0;
const t24b=s=>s&&s.type===24&&s.attack===0&&s.state99===2&&s.action2A===2&&s.b2B===4&&s.body===5440&&s.frameEnd===0x8af28&&s.next===0x8a6da&&s.value30===0x180001&&s.timer34===2&&s.payload6C===0;
const t24c=s=>s&&s.type===24&&s.attack===0&&s.state99===2&&s.action2A===2&&s.b2B===4&&s.body===5440&&s.frameEnd===0x8af28&&s.next===0x8a756&&s.value30===0x100001&&s.timer34===2&&s.payload6C===0;
const t24d=s=>s&&s.type===24&&s.attack===0&&s.state99===2&&s.action2A===2&&s.b2B===4&&s.body===5424&&s.frameEnd===0x8aeec&&s.next===0x8a76a&&s.value30===0x100001&&s.timer34===2&&s.payload6C===0;
const entry=(base,s,p)=>base(s)&&!!p&&p.type===s.type&&p.attack===0&&!base(p);

const RULES=[
  {id:'T16_6432_B4_40',status:'production-shadow',horizon:40,tail:150,expected:[6432],base:t16b4,match:(s,p)=>entry(t16b4,s,p)},
  {id:'T20_5136_B0_TO_B255_700',status:'production-shadow-candidate',horizon:700,tail:1100,expected:[5136],base:s=>t20_5136(s,255),match:(s,p)=>t20_5136(s,255)&&t20_5136(p,0)},
  {id:'D867BA_3232_TM6_120',status:'prospective-descriptor-family',horizon:120,tail:350,expected:[3232],base:d867,match:(s,p)=>entry(d867,s,p)},
  {id:'D8811E_3232_TM6_120',status:'prospective-descriptor-family',horizon:120,tail:350,expected:[3232],base:d881,match:(s,p)=>entry(d881,s,p)},
  {id:'T23_4792_BODY4920_B0_ENTRY_180',status:'prospective-candidate',horizon:180,tail:500,expected:[4792],base:t23b0,match:(s,p)=>entry(t23b0,s,p)},
  {id:'T24_5440_V180_TM2_140',status:'prospective-candidate',horizon:140,tail:400,expected:[5440],base:t24a,match:(s,p)=>entry(t24a,s,p)},
  {id:'T24_5424_V180_TM2_140',status:'prospective-candidate',horizon:140,tail:400,expected:[5424],base:t24b,match:(s,p)=>entry(t24b,s,p)},
  {id:'T24_5424_V100_NX756_TM2_140',status:'prospective-candidate',horizon:140,tail:400,expected:[5424],base:t24c,match:(s,p)=>entry(t24c,s,p)},
  {id:'T24_5440_V100_NX76A_TM2_140',status:'prospective-candidate',horizon:140,tail:400,expected:[5440],base:t24d,match:(s,p)=>entry(t24d,s,p)}
];

const DURATION=120000,INTERVAL=10,JITTER_TOL=15,HISTORY_MS=550,LAGS=[50,100,150,250,500],start=performance.now();
const prev=new Map(),history=new Map(),cycle=new Map(),armed=new Map(),watches=[],events=[];let wid=0;
const typeSamples={},attackTypeCounts={},rawMatchSamples={},transitionEntries={};for(const r of RULES){rawMatchSamples[r.id]=0;transitionEntries[r.id]=0;}
const terminalAgg=new Map(),lagAgg=new Map();
const diag={polls:0,enemySamples:0,activeEdges:0,signals:0,strictHits:0,jitterBandHits:0,realLateHits:0,hardMisses:0,censored:0,retargets:0,copyId:COPY_ID};
const r1=x=>Math.round(x*10)/10,key=(slot,id)=>`${slot}|${id}`;
function addHist(s,t){let h=history.get(s.slot);if(!h){h=[];history.set(s.slot,h);}h.push({t,s:{...s}});while(h.length&&t-h[0].t>HISTORY_MS)h.shift();}
function nearestPast(slot,targetT){const h=history.get(slot)||[];let best=null,d0=1e9;for(const x of h){const d=Math.abs(x.t-targetT);if(d<d0){best=x;d0=d;}}return d0<=25?best:null;}
function addAgg(map,k,seed,lead,targetSame,sideSame){const q=map.get(k)||{...seed,count:0,targetSame:0,targetTotal:0,sideSame:0,sideTotal:0,leadSamples:[]};q.count++;if(targetSame!=null){q.targetTotal++;if(targetSame)q.targetSame++;}if(sideSame!=null){q.sideTotal++;if(sideSame)q.sideSame++;}q.leadSamples.push(r1(lead));map.set(k,q);}
function mineActive(p,s,t){
  attackTypeCounts[`T${s.type}|A${s.attack}`]=(attackTypeCounts[`T${s.type}|A${s.attack}`]||0)+1;
  if(p&&p.attack===0){const k=`T${s.type}|A${s.attack}|${fp(p)}`;addAgg(terminalAgg,k,{type:s.type,activeAttack:s.attack,signature:fp(p)},INTERVAL,p.target7E===s.target7E,p.side!=null&&s.side!=null?p.side===s.side:null);}
  for(const lag of LAGS){const x=nearestPast(s.slot,t-lag);if(!x)continue;const ps=x.s,k=`${lag}|T${s.type}|A${s.attack}|${fp(ps)}`;addAgg(lagAgg,k,{lagMs:lag,type:s.type,activeAttack:s.attack,signature:fp(ps)},t-x.t,ps.target7E===s.target7E,ps.side!=null&&s.side!=null?ps.side===s.side:null);}
}
function arm(r,s,t){
  const c=cycle.get(s.slot)||0,k=key(s.slot,r.id);if(armed.get(k)===c)return;armed.set(k,c);
  const w={id:++wid,rule:r.id,status:r.status,slot:s.slot,type:s.type,cycle:c,horizon:r.horizon,tail:r.tail,at:t,entryTarget7E:s.target7E,entryTarget:s.target,entrySide:s.side,entryAbsDx:s.absDx,entryAbsDy:s.absDy,resolved:false,outcome:null,leadMs:null,activeAttack:null,expectedAttack:null,targetSame:null,sideSame:null,retargets:[],censored:false};
  watches.push(w);diag.signals++;events.push({kind:'SIGNAL',rel:r1(t),rule:r.id,slot:s.slot,type:s.type,target:s.target,side:s.side,signature:fp(s)});
}
function updateRetargets(s,t){for(const w of watches){if(w.resolved||w.slot!==s.slot||w.type!==s.type)continue;if(w.entryTarget7E!==s.target7E){const last=w.retargets.at(-1)?.to7E??w.entryTarget7E;if(last!==s.target7E){w.retargets.push({rel:r1(t-w.at),from7E:last,to7E:s.target7E});diag.retargets++;}}}}
function resolveActive(s,t){
  diag.activeEdges++;mineActive(prev.get(s.slot),s,t);
  for(const w of watches){
    if(w.resolved||w.slot!==s.slot||w.type!==s.type)continue;const lead=t-w.at;if(lead<0||lead>w.tail)continue;const r=RULES.find(x=>x.id===w.rule);
    w.resolved=true;w.leadMs=r1(lead);w.activeAttack=s.attack;w.expectedAttack=r.expected.includes(s.attack);w.targetSame=w.entryTarget7E===s.target7E;w.sideSame=w.entrySide!=null&&s.side!=null?w.entrySide===s.side:null;w.activeTarget=s.target;w.activeSide=s.side;
    if(lead<=w.horizon){w.outcome='strictHit';diag.strictHits++;}else if(lead<=w.horizon+JITTER_TOL){w.outcome='jitterBandHit';diag.jitterBandHits++;}else{w.outcome='realLateHit';diag.realLateHits++;}
    events.push({kind:w.outcome,rel:r1(t),rule:w.rule,slot:s.slot,type:s.type,leadMs:w.leadMs,attack:s.attack,expectedAttack:w.expectedAttack,target:s.target,side:s.side});
  }
  cycle.set(s.slot,(cycle.get(s.slot)||0)+1);
}
function deadlines(t){for(const w of watches){if(w.resolved)continue;if(t-w.at>w.tail){w.resolved=true;w.outcome='hardMiss';diag.hardMisses++;events.push({kind:'HARD_MISS',rel:r1(t),rule:w.rule,slot:w.slot,type:w.type,ageMs:r1(t-w.at)});}}}
function censor(i){for(const w of watches)if(!w.resolved&&w.slot===i){w.resolved=true;w.censored=true;w.outcome='censored';diag.censored++;}}

await new Promise(resolve=>{
  const id=setInterval(()=>{
    const t=performance.now()-start;diag.polls++;deadlines(t);
    for(let i=0;i<SLOTS;i++){
      const s=snap(i),p=prev.get(i)||null;
      if(!s){if(p)censor(i);prev.delete(i);history.delete(i);continue;}
      diag.enemySamples++;typeSamples['T'+s.type]=(typeSamples['T'+s.type]||0)+1;
      if(p&&p.type!==s.type){censor(i);cycle.set(i,(cycle.get(i)||0)+1);history.delete(i);}
      addHist(s,t);
      for(const r of RULES){if(r.base(s))rawMatchSamples[r.id]++;if(r.match(s,p)){transitionEntries[r.id]++;arm(r,s,t);}}
      updateRetargets(s,t);
      if(p&&p.attack===0&&s.attack!==0)resolveActive(s,t);
      prev.set(i,s);
    }
    if(t>=DURATION){clearInterval(id);for(const w of watches)if(!w.resolved){w.resolved=true;w.censored=true;w.outcome='censored';diag.censored++;}resolve();}
  },INTERVAL);
});

const blank=r=>({rule:r.id,status:r.status,horizonMs:r.horizon,tailMs:r.tail,jitterToleranceMs:JITTER_TOL,signals:0,evaluable:0,strictHit:0,jitterBandHit:0,realLateHit:0,hardMiss:0,censored:0,strictRate:null,jitterCorrectedRate:null,tailHitRate:null,expectedAttack:0,expectedAttackTotal:0,expectedAttackRate:null,targetSame:0,targetTotal:0,targetSameRate:null,sideSame:0,sideTotal:0,sideStableRate:null,leads:[],attackCounts:{},entryTargetCounts:{},entrySideCounts:{},entryTypeCounts:{}});
const ruleStats={};for(const r of RULES)ruleStats[r.id]=blank(r);
for(const w of watches){
  const q=ruleStats[w.rule];q.signals++;q.entryTargetCounts[w.entryTarget||String(w.entryTarget7E)]=(q.entryTargetCounts[w.entryTarget||String(w.entryTarget7E)]||0)+1;q.entrySideCounts[w.entrySide||'null']=(q.entrySideCounts[w.entrySide||'null']||0)+1;q.entryTypeCounts['T'+w.type]=(q.entryTypeCounts['T'+w.type]||0)+1;
  if(w.censored){q.censored++;continue;}q.evaluable++;
  if(w.outcome==='strictHit')q.strictHit++;else if(w.outcome==='jitterBandHit')q.jitterBandHit++;else if(w.outcome==='realLateHit')q.realLateHit++;else if(w.outcome==='hardMiss')q.hardMiss++;
  if(w.leadMs!=null){q.leads.push(w.leadMs);q.attackCounts[String(w.activeAttack)]=(q.attackCounts[String(w.activeAttack)]||0)+1;q.expectedAttackTotal++;if(w.expectedAttack)q.expectedAttack++;if(w.targetSame!=null){q.targetTotal++;if(w.targetSame)q.targetSame++;}if(w.sideSame!=null){q.sideTotal++;if(w.sideSame)q.sideSame++;}}
}
for(const q of Object.values(ruleStats)){
  q.strictRate=q.evaluable?+(q.strictHit/q.evaluable).toFixed(3):null;
  q.jitterCorrectedRate=q.evaluable?+((q.strictHit+q.jitterBandHit)/q.evaluable).toFixed(3):null;
  q.tailHitRate=q.evaluable?+((q.strictHit+q.jitterBandHit+q.realLateHit)/q.evaluable).toFixed(3):null;
  q.expectedAttackRate=q.expectedAttackTotal?+(q.expectedAttack/q.expectedAttackTotal).toFixed(3):null;
  q.targetSameRate=q.targetTotal?+(q.targetSame/q.targetTotal).toFixed(3):null;
  q.sideStableRate=q.sideTotal?+(q.sideSame/q.sideTotal).toFixed(3):null;
  q.leads.sort((a,b)=>a-b);q.attackCounts=Object.entries(q.attackCounts).map(([attack,count])=>({attack:+attack,count})).sort((a,b)=>b.count-a.count);
}
const finalize=a=>a.map(q=>{q.leadSamples.sort((x,y)=>x-y);q.targetSameRate=q.targetTotal?+(q.targetSame/q.targetTotal).toFixed(3):null;q.sideStableRate=q.sideTotal?+(q.sideSame/q.sideTotal).toFixed(3):null;q.leadMin=q.leadSamples.length?q.leadSamples[0]:null;q.leadMax=q.leadSamples.length?q.leadSamples.at(-1):null;return q;}).sort((a,b)=>b.count-a.count||((a.leadMax??1e9)-(b.leadMax??1e9))).slice(0,100);
const terminalTop=finalize([...terminalAgg.values()]),fingerprintTop=finalize([...lagAgg.values()]);
const out={copyId:COPY_ID,project:PROJECT,version:VERSION,expectedMarker:MARKER,readOnly:true,ramWrites:0,durationRequestedMs:DURATION,actualDurationMs:r1(performance.now()-start),intervalMs:INTERVAL,jitterToleranceMs:JITTER_TOL,model:{purpose:'Forward prospective validation of descriptor-family 3232 TM6 rules plus independent reconfirmation of the T20 A5136 early-warning transition. Opportunistic T16/T23/T24 validation and fallback mining prevent room changes from being wasted.',candidatePolicy:'Descriptor-family rules are type-agnostic but exact on descriptor/body/value/action/b2/timer/payload. Signals arm only on live forward entry. entryTypeCounts measures cross-type generalization.',t20Policy:'T20 B0->B255 is an early-warning rule with broad 400-700ms lead, not an exact countdown.',targetPolicy:'live enemy+0x7E authoritative',activeConvention:'enemy+0x70 U16 0->nonzero; not exact damage/hitbox onset',miningPolicy:'terminal/fixed-lag fallback remains discovery/correlation only.'},diagnostics:{...diag,typeSamples,attackTypeCounts,rawMatchSamples,transitionEntries},ruleStats,terminalTop,fingerprintTop,watches,events:events.slice(-500)};
self.__WOF_V38_RESULT=out;console.log(MARKER);console.log(JSON.stringify(out,null,2));return out;
})().catch(e=>{console.error('[WOF-038] ERROR',e);throw e;});
