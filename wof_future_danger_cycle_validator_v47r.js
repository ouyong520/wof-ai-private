(async()=>{
'use strict';
const COPY_ID='WOF-047R';
const PROJECT='WOF-AI-PRIVATE';
const VERSION='wof-future-danger-cycle-validator-v47r';
const MARKER='=== WOF FUTURE DANGER CYCLE VALIDATOR V47R JSON ===';
const BASE={copyId:'WOF-046R',project:'WOF-AI-PRIVATE',version:'wof-future-danger-cycle-validator-v46r',marker:'=== WOF FUTURE DANGER CYCLE VALIDATOR V46R JSON ==='};
const SRC='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/wof_future_danger_cycle_validator_v46r.js';
console.log(`[${COPY_ID}] ${PROJECT} ${VERSION}`);
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);
async function ensureModule(){if(good(self._0x515056))return self._0x515056;const until=performance.now()+8000;while(performance.now()<until){for(const k of Object.getOwnPropertyNames(self)){let v;try{v=self[k]}catch(_){continue}if(good(v)){self._0x515056=v;self.__WOF_MODULE_GLOBAL_KEY=k;return v;}}await sleep(50);}throw new Error(`[${COPY_ID}] WASM module not found. Select a live gstyphoon.js Worker.`);}
const MOD=await ensureModule(),M=MOD.HEAPU8,R=MOD.HEAPU32?.[0x2e39e4>>>2]>>>0;if(!R)throw new Error(`[${COPY_ID}] CPS RAM base missing`);
const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0,U16=a=>((B(a)<<8)|B(a+1))>>>0,U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0,S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v;},X=a=>Math.round(S32(a+4)/65536);
const ENEMY=0xFFC0BC,STRIDE=0xE0,SLOTS=20,PBASE={0:0xFFBE1C,4:0xFFBEFC,8:0xFFBFDC},PN={0:'P1',4:'P2',8:'P3'};
const side=dx=>dx==null?null:dx<-4?'LEFT':dx>4?'RIGHT':'CENTER';
function snap(i){const a=ENEMY+i*STRIDE,type=U16(a+0x20);if(type>=47)return null;const fe=U32(a+0x12),nx=U32(a+0x2C);if(!fe&&!nx)return null;const t=U16(a+0x7E),pb=PBASE[t],ex=X(a),tx=pb?X(pb):null,dx=tx==null?null:tx-ex;return{slot:i,type,target7E:t,target:PN[t]||null,side:side(dx),state99:B(a+0x99),action2A:B(a+0x2A),b2B:B(a+0x2B),body:U16(a+0x6E),attack:U16(a+0x70),frameEnd:fe,next:nx,value30:U32(a+0x30),timer34:U16(a+0x34),payload6C:U16(a+0x6C)};}
const r1=x=>Math.round(x*10)/10, hx=n=>(n>>>0).toString(16);
const sig=s=>`S${s.state99}/A${s.action2A}/B${s.b2B}|BODY${s.body}|FE${hx(s.frameEnd)}|NX${hx(s.next)}|V${hx(s.value30)}|TM${s.timer34}|P6C${s.payload6C}`;

async function runT23TraceProbe(){
  const DURATION=120000,INTERVAL=10,MAX_TRACES=120,MAX_STATES=48,start=performance.now();
  const prev=new Map(),cycles=new Map(),traces=[];
  const diag={polls:0,enemySamples:0,t23Samples:0,attackZeroStarts:0,activeEdges:0,resolvedCycles:0,droppedCycles:0,retargets:0,attackCounts:{}};
  const startCycle=(s,t,startedMidCycle)=>{cycles.set(s.slot,{slot:s.slot,startedAt:t,startedMidCycle:!!startedMidCycle,targetStart7E:s.target7E,targetStart:s.target,sideStart:s.side,lastTarget7E:s.target7E,retargets:[],states:[]});diag.attackZeroStarts++;};
  const observe=(c,s,t)=>{if(c.lastTarget7E!==s.target7E){c.retargets.push({relMs:r1(t-c.startedAt),from7E:c.lastTarget7E,to7E:s.target7E});c.lastTarget7E=s.target7E;diag.retargets++;}const z=sig(s),last=c.states.at(-1);if(last&&last.signature===z){last.lastSeen=t;last.lastTarget7E=s.target7E;last.lastSide=s.side;return;}c.states.push({signature:z,firstSeen:t,lastSeen:t,firstTarget7E:s.target7E,lastTarget7E:s.target7E,firstSide:s.side,lastSide:s.side});if(c.states.length>MAX_STATES)c.states.shift();};
  const resolve=(c,s,t)=>{if(!c)return;diag.activeEdges++;diag.resolvedCycles++;diag.attackCounts['A'+s.attack]=(diag.attackCounts['A'+s.attack]||0)+1;if(traces.length>=MAX_TRACES){diag.droppedCycles++;return;}const states=c.states.map(x=>({signature:x.signature,firstLeadMs:r1(t-x.firstSeen),lastLeadMs:r1(t-x.lastSeen),firstTarget7E:x.firstTarget7E,lastTarget7E:x.lastTarget7E,firstSide:x.firstSide,lastSide:x.lastSide}));const tails=states.slice(-3).map(x=>x.signature);traces.push({slot:c.slot,activeAttack:s.attack,cycleDurationMs:r1(t-c.startedAt),startedMidCycle:c.startedMidCycle,targetStart7E:c.targetStart7E,targetStart:c.targetStart,targetAtActive7E:s.target7E,targetAtActive:s.target,targetStable:c.targetStart7E===s.target7E,sideStart:c.sideStart,sideAtActive:s.side,sideStable:c.sideStart===s.side,retargets:c.retargets,distinctStates:states.length,finalPreActiveSignature:states.at(-1)?.signature||null,tail1:tails.at(-1)||null,tail2:tails.length>=2?tails.slice(-2):tails,tail3:tails,states});};
  await new Promise(resolveDone=>{const id=setInterval(()=>{const t=performance.now()-start;diag.polls++;for(let i=0;i<SLOTS;i++){const s=snap(i),p=prev.get(i)||null;if(s)diag.enemySamples++;if(!s||s.type!==23){if(cycles.has(i)){cycles.delete(i);diag.droppedCycles++;}if(s)prev.set(i,s);else prev.delete(i);continue;}diag.t23Samples++;if(s.attack===0){let c=cycles.get(i);if(!c||!p||p.type!==23||p.attack!==0){startCycle(s,t,!p||p.type!==23);c=cycles.get(i);}observe(c,s,t);}if(p&&p.type===23&&p.attack===0&&s.attack!==0){resolve(cycles.get(i),s,t);cycles.delete(i);}prev.set(i,s);}if(t>=DURATION){clearInterval(id);resolveDone();}},INTERVAL);});
  return{actualDurationMs:r1(performance.now()-start),diagnostics:diag,t23CycleTraces:traces};
}

let code=await fetch(SRC+'?x='+Date.now(),{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error('WOF-047R base validator fetch '+r.status);return r.text();});
code=code.replace("self.__WOF_V46R_RESULT=base;console.log(MARKER);console.log(JSON.stringify(base,null,2));return base;","self.__WOF_V46R_RESULT=base;return base;");
const [base,trace]=await Promise.all([(0,eval)(code),runT23TraceProbe()]);
if(!base||base.copyId!==BASE.copyId||base.project!==BASE.project||base.version!==BASE.version||base.expectedMarker!==BASE.marker||base.readOnly!==true||base.ramWrites!==0)throw new Error(`[${COPY_ID}] embedded WOF-046R identity mismatch`);
base.copyId=COPY_ID;base.project=PROJECT;base.version=VERSION;base.expectedMarker=MARKER;base.readOnly=true;base.ramWrites=0;
base.t23TraceDiagnostics=trace.diagnostics;base.t23CycleTraces=trace.t23CycleTraces;
base.model.t23Policy='WOF-046 gave zero raw coverage for the WOF-045 short T23 BODY4976/A6/B4/TM5 candidate in two fresh batches despite new T23 activity, so this is zero coverage, not a failure. Common WOF-046 T23 single-state signatures were shared by A4792/A4920/A5848 and therefore are not attack-specific. WOF-047 keeps the prior candidate audit and adds per-cycle ordered T23 state traces to discover discriminating transition sequences rather than promoting ambiguous single states.';
base.model.tracePolicy='t23CycleTraces records up to120 resolved T23 zero->ACTIVE cycles per room, preserving the last48 distinct states in chronological order with first/last lead to ACTIVE, target/side evolution, retargets and tail1/tail2/tail3. This is discovery evidence only until a later prospective validator is built.';
self.__WOF_V47R_RESULT=base;console.log(MARKER);console.log(JSON.stringify(base,null,2));return base;
})().catch(e=>{console.error('[WOF-047R] ERROR',e);throw e;});
