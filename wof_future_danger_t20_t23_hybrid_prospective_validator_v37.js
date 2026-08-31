(async()=>{
'use strict';
const COPY_ID='WOF-037';
const PROJECT='WOF-AI-PRIVATE';
const VERSION='wof-future-danger-t20-t23-hybrid-prospective-validator-v37';
const MARKER='=== WOF FUTURE DANGER T20 T23 HYBRID PROSPECTIVE VALIDATOR V37 JSON ===';
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
const MOD=self._0x515056,M=MOD.HEAPU8,R=MOD.HEAPU32?.[0x2e39e4>>>2]>>>0;if(!R)throw new Error(`[${COPY_ID}] CPS RAM base missing`);
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
const t20_5136_core=(s,b)=>s&&s.type===20&&s.attack===0&&s.state99===2&&s.action2A===4&&s.b2B===b&&s.body===0&&s.frameEnd===0x839c4&&s.next===0x82b0a&&s.value30===0x100000&&s.timer34===20&&s.payload6C===0;
const t23_4792_b0=s=>s&&s.type===23&&s.attack===0&&s.state99===0&&s.action2A===0&&s.b2B===0&&s.body===4920&&s.frameEnd===0x848e2&&s.next===0x83c56&&s.value30===0x140000&&s.timer34===1&&s.payload6C===7904;
const t20_4792_tm=(s,tm)=>s&&s.type===20&&s.attack===0&&s.state99===0&&s.action2A===6&&s.b2B===4&&s.body===4976&&s.frameEnd===0x83824&&s.next===0x82d38&&s.value30===0&&s.timer34===tm&&s.payload6C===0;
const t16b4=s=>s&&s.type===16&&s.attack===0&&s.body===4856&&s.frameEnd===0x851ae&&s.next===0x84c44&&s.value30===0xffff&&s.timer34===1&&s.action2A===4&&s.b2B===4&&(s.state99===0||s.state99===2||s.state99===4);
const RULES=[
 {id:'T16_6432_B4_40',status:'production-shadow',horizon:40,tail:150,expected:[6432],match:(s,p)=>t16b4(s)&&!(p&&p.type===16&&t16b4(p))},
 {id:'T20_5136_B0_TO_B255_700',status:'prospective-candidate',horizon:700,tail:1100,expected:[5136],match:(s,p)=>t20_5136_core(s,255)&&t20_5136_core(p,0)},
 {id:'T23_4792_BODY4920_B0_ENTRY_180',status:'prospective-candidate',horizon:180,tail:500,expected:[4792],match:(s,p)=>t23_4792_b0(s)&&p&&p.type===23&&p.attack===0&&!t23_4792_b0(p)},
 {id:'T20_4792_TM6_TO_TM5_110',status:'prospective-candidate',horizon:110,tail:300,expected:[4792],match:(s,p)=>t20_4792_tm(s,5)&&t20_4792_tm(p,6)},
 {id:'T20_4792_TM3_TO_TM2_60',status:'prospective-candidate',horizon:60,tail:220,expected:[4792],match:(s,p)=>t20_4792_tm(s,2)&&t20_4792_tm(p,3)}
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
function arm(r,s,t){const c=cycle.get(s.slot)||0,k=key(s.slot,r.id);if(armed.get(k)===c)return;armed.set(k,c);const w={id:++wid,rule:r.id,status:r.status,slot:s.slot,type:s.type,cycle:c,horizon:r.horizon,tail:r.tail,at:t,entryTarget7E:s.target7E,entryTarget:s.target,entrySide:s.side,entryAbsDx:s.absDx,entryAbsDy:s.absDy,resolved:false,outcome:null,leadMs:null,activeAttack:null,expectedAttack:null,targetSame:null,sideSame:null,retargets:[],censored:false};watches.push(w);diag.signals++;events.push({kind:'SIGNAL',rel:r1(t),rule:r.id,slot:s.slot,type:s.type,target:s.target,side:s.side,signature:fp(s)});}
function updateRetargets(s,t){for(const w of watches){if(w.resolved||w.slot!==s.slot||w.type!==s.type)continue;if(w.entryTarget7E!==s.target7E){const last=w.retargets.at(-1)?.to7E??w.entryTarget7E;if(last!==s.target7E){w.retargets.push({rel:r1(t-w.at),from7E:last,to7E:s.target7E});diag.retargets++;}}}}
function resolveActive(s,t){diag.activeEdges++;mineActive(prev.get(s.slot),s,t);for(const w of watches){if(w.resolved||w.slot!==s.slot||w.type!==s.type)continue;const lead=t-w.at;if(lead<0||lead>w.tail)continue;const r=RULES.find(x=>x.id===w.rule);w.resolved=true;w.leadMs=r1(lead);w.activeAttack=s.attack;w.expectedAttack=r.expected.includes(s.attack);w.targetSame=w.entryTarget7E===s.target7E;w.sideSame=w.entrySide!=null&&s.side!=null?w.entrySide===s.side:null;if(lead<=w.horizon){w.outcome='strictHit';diag.strictHits++;}else if(lead<=w.horizon+JITTER_TOL){w.outcome='jitterBandHit';diag.jitterBandHits++;}else{w.outcome='realLateHit';diag.realLateHits++;}events.push({kind:w.outcome,rel:r1(t),rule:w.rule,slot:s.slot,leadMs:w.leadMs,attack:s.attack,expectedAttack:w.expectedAttack,target:s.target,side:s.side});}cycle.set(s.slot,(cycle.get(s.slot)||0)+1);}
function deadlines(t){for(const w of watches){if(w.resolved)continue;if(t-w.at>w.tail){w.resolved=true;w.outcome='hardMiss';diag.hardMisses++;events.push({kind:'HARD_MISS',rel:r1(t),rule:w.rule,slot:w.slot,ageMs:r1(t-w.at)});}}}
function censor(i){for(const w of watches)if(!w.resolved&&w.slot===i){w.resolved=true;w.censored=true;w.outcome='censored';diag.censored++;}}
await new Promise(resolve=>{const id=setInterval(()=>{const t=performance.now()-start;diag.polls++;deadlines(t);for(let i=0;i<SLOTS;i++){const s=snap(i),p=prev.get(i)||null;if(!s){if(p)censor(i);prev.delete(i);history.delete(i);continue;}diag.enemySamples++;typeSamples['T'+s.type]=(typeSamples['T'+s.type]||0)+1;if(p&&p.type!==s.type){censor(i);cycle.set(i,(cycle.get(i)||0)+1);history.delete(i);}addHist(s,t);for(const r of RULES){const currentBase=(r.id==='T16_6432_B4_40'?t16b4(s):r.id==='T20_5136_B0_TO_B255_700'?t20_5136_core(s,255):r.id==='T23_4792_BODY4920_B0_ENTRY_180'?t23_4792_b0(s):r.id==='T20_4792_TM6_TO_TM5_110'?t20_4792_tm(s,5):t20_4792_tm(s,2));if(currentBase)rawMatchSamples[r.id]++;if(r.match(s,p)){transitionEntries[r.id]++;arm(r,s,t);}}updateRetargets(s,t);if(p&&p.attack===0&&s.attack!==0)resolveActive(s,t);prev.set(i,s);}if(t>=DURATION){clearInterval(id);for(const w of watches)if(!w.resolved){w.resolved=true;w.censored=true;w.outcome='censored';diag.censored++;}resolve();}},INTERVAL);});
const blank=r=>({rule:r.id,status:r.status,horizonMs:r.horizon,tailMs:r.tail,jitterToleranceMs:JITTER_TOL,signals:0,evaluable:0,strictHit:0,jitterBandHit:0,realLateHit:0,hardMiss:0,censored:0,strictRate:null,jitterCorrectedRate:null,tailHitRate:null,expectedAttack:0,expectedAttackTotal:0,expectedAttackRate:null,targetSame:0,targetTotal:0,targetSameRate:null,sideSame:0,sideTotal:0,sideStableRate:null,leads:[],attackCounts:{},entryTargetCounts:{},entrySideCounts:{}});
const ruleStats={};for(const r of RULES)ruleStats[r.id]=blank(r);
for(const w of watches){const q=ruleStats[w.rule];q.signals++;q.entryTargetCounts[w.entryTarget||String(w.entryTarget7E)]=(q.entryTargetCounts[w.entryTarget||String(w.entryTarget7E)]||0)+1;q.entrySideCounts[w.entrySide||'null']=(q.entrySideCounts[w.entrySide||'null']||0)+1;if(w.censored){q.censored++;continue;}q.evaluable++;if(w.outcome==='strictHit')q.strictHit++;else if(w.outcome==='jitterBandHit')q.jitterBandHit++;else if(w.outcome==='realLateHit')q.realLateHit++;else if(w.outcome==='hardMiss')q.hardMiss++;if(w.leadMs!=null){q.leads.push(w.leadMs);q.attackCounts[String(w.activeAttack)]=(q.attackCounts[String(w.activeAttack)]||0)+1;q.expectedAttackTotal++;if(w.expectedAttack)q.expectedAttack++;if(w.targetSame!=null){q.targetTotal++;if(w.targetSame)q.targetSame++;}if(w.sideSame!=null){q.sideTotal++;if(w.sideSame)q.sideSame++;}}}
for(const q of Object.values(ruleStats)){q.strictRate=q.evaluable?+(q.strictHit/q.evaluable).toFixed(3):null;q.jitterCorrectedRate=q.evaluable?+((q.strictHit+q.jitterBandHit)/q.evaluable).toFixed(3):null;q.tailHitRate=q.evaluable?+((q.strictHit+q.jitterBandHit+q.realLateHit)/q.evaluable).toFixed(3):null;q.expectedAttackRate=q.expectedAttackTotal?+(q.expectedAttack/q.expectedAttackTotal).toFixed(3):null;q.targetSameRate=q.targetTotal?+(q.targetSame/q.targetTotal).toFixed(3):null;q.sideStableRate=q.sideTotal?+(q.sideSame/q.sideTotal).toFixed(3):null;q.leads.sort((a,b)=>a-b);q.attackCounts=Object.entries(q.attackCounts).map(([attack,count])=>({attack:+attack,count})).sort((a,b)=>b.count-a.count);}
const finishAgg=map=>[...map.values()].map(q=>{q.targetSameRate=q.targetTotal?+(q.targetSame/q.targetTotal).toFixed(3):null;q.sideStableRate=q.sideTotal?+(q.sideSame/q.sideTotal).toFixed(3):null;q.leadMin=Math.min(...q.leadSamples);q.leadMax=Math.max(...q.leadSamples);return q;}).sort((a,b)=>b.count-a.count||((a.leadMax-a.leadMin)-(b.leadMax-b.leadMin))).slice(0,80);
const out={copyId:COPY_ID,project:PROJECT,version:VERSION,expectedMarker:MARKER,readOnly:true,ramWrites:0,durationRequestedMs:DURATION,actualDurationMs:r1(performance.now()-start),intervalMs:INTERVAL,jitterToleranceMs:JITTER_TOL,model:{purpose:'Independent prospective validation of WOF-036 T20/T23 discoveries, with fallback adaptive mining so room changes still produce evidence.',candidatePolicy:'Signals arm only on live forward entry/transition; no rule is triggered merely because a state was observed at a fixed retrospective lag.',targetPolicy:'live enemy+0x7E authoritative',activeConvention:'enemy+0x70 U16 0->nonzero; not exact damage/hitbox onset',miningPolicy:'Fallback terminal/fixed-lag fingerprints remain discovery/correlation only.'},diagnostics:{...diag,typeSamples,attackTypeCounts,rawMatchSamples,transitionEntries},ruleStats,terminalTop:finishAgg(terminalAgg),fingerprintTop:finishAgg(lagAgg),watches,events:events.slice(-400)};self.__WOF_V37_RESULT=out;console.log(MARKER);console.log(JSON.stringify(out,null,2));return out;
})().catch(e=>{console.error('[WOF-037] ERROR',e);throw e;});
