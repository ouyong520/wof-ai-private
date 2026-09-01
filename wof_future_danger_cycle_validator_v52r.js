(async()=>{
'use strict';
const COPY_ID='WOF-052R';
const PROJECT='WOF-AI-PRIVATE';
const VERSION='wof-future-danger-cycle-validator-v52r';
const MARKER='=== WOF FUTURE DANGER CYCLE VALIDATOR V52R JSON ===';
const SRC='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/wof_future_danger_cycle_validator_v48r.js';
console.log(`[${COPY_ID}] ${PROJECT} ${VERSION}`);

const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);
async function ensureModule(){
  if(good(self._0x515056))return self._0x515056;
  const until=performance.now()+8000;
  while(performance.now()<until){
    for(const k of Object.getOwnPropertyNames(self)){
      let v;try{v=self[k]}catch(_){continue}
      if(good(v)){self._0x515056=v;self.__WOF_MODULE_GLOBAL_KEY=k;return v;}
    }
    await sleep(50);
  }
  throw new Error(`[${COPY_ID}] WASM module not found. Select a live gstyphoon.js Worker.`);
}
const MOD=await ensureModule(),M=MOD.HEAPU8,R=MOD.HEAPU32?.[0x2e39e4>>>2]>>>0;
if(!R)throw new Error(`[${COPY_ID}] CPS RAM base missing`);
const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0;
const U16=a=>((B(a)<<8)|B(a+1))>>>0;
const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
const S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v;};
const X=a=>Math.round(S32(a+4)/65536);
const ENEMY=0xFFC0BC,STRIDE=0xE0,SLOTS=20;
const PBASE={0:0xFFBE1C,4:0xFFBEFC,8:0xFFBFDC},PN={0:'P1',4:'P2',8:'P3'};
const side=dx=>dx==null?null:dx<-4?'LEFT':dx>4?'RIGHT':'CENTER';
function snap(i){
  const a=ENEMY+i*STRIDE,type=U16(a+0x20);
  if(type>=47)return null;
  const fe=U32(a+0x12),nx=U32(a+0x2C);
  if(!fe&&!nx)return null;
  const t=U16(a+0x7E),pb=PBASE[t],ex=X(a),tx=pb?X(pb):null,dx=tx==null?null:tx-ex;
  return{slot:i,type,target7E:t,target:PN[t]||null,side:side(dx),state99:B(a+0x99),action2A:B(a+0x2A),b2B:B(a+0x2B),body:U16(a+0x6E),attack:U16(a+0x70),frameEnd:fe,next:nx,value30:U32(a+0x30),timer34:U16(a+0x34),payload6C:U16(a+0x6C)};
}
const r1=x=>Math.round(x*10)/10,hx=n=>(n>>>0).toString(16);
const sig=s=>`S${s.state99}/A${s.action2A}/B${s.b2B}|BODY${s.body}|FE${hx(s.frameEnd)}|NX${hx(s.next)}|V${hx(s.value30)}|TM${s.timer34}|P6C${s.payload6C}`;
const CANDIDATE_SIG='S0/A4/B2|BODY4728|FE8b660|NX8b204|Vffff|TM1|P6C4736';
const isCandidate=s=>s&&s.type===18&&s.attack===0&&sig(s)===CANDIDATE_SIG;
const family=s=>String(s||'').replace(/\|TM[^|]*/,'|TM*');
const add=(m,k,n=1)=>{if(!k)return;m[k]=(m[k]||0)+n;};
const top=(m,n=50)=>Object.entries(m).sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0])).slice(0,n).map(([key,count])=>({key,count}));
const med=a=>{if(!a.length)return null;const b=[...a].sort((x,y)=>x-y),m=b.length>>1;return b.length%2?b[m]:+((b[m-1]+b[m])/2).toFixed(1);};

async function runT18CandidateTrace(){
  const DURATION=120000,INTERVAL=10,MAX_TRACES=160,MAX_STATES=64,start=performance.now();
  const prev=new Map(),cycles=new Map(),traces=[];
  const diag={polls:0,enemySamples:0,t18Samples:0,attackZeroStarts:0,activeEdges:0,resolvedCycles:0,droppedCycles:0,retargets:0,candidateSamples:0,candidateCycles:0,attackCounts:{},candidateAttackCounts:{}};
  const startCycle=(s,t,startedMidCycle)=>{cycles.set(s.slot,{slot:s.slot,startedAt:t,startedMidCycle:!!startedMidCycle,targetStart7E:s.target7E,targetStart:s.target,sideStart:s.side,lastTarget7E:s.target7E,retargets:[],states:[],candidateFirstAt:null,candidateLastAt:null});diag.attackZeroStarts++;};
  const observe=(c,s,t)=>{
    if(c.lastTarget7E!==s.target7E){c.retargets.push({relMs:r1(t-c.startedAt),from7E:c.lastTarget7E,to7E:s.target7E});c.lastTarget7E=s.target7E;diag.retargets++;}
    if(isCandidate(s)){diag.candidateSamples++;if(c.candidateFirstAt==null)c.candidateFirstAt=t;c.candidateLastAt=t;}
    const z=sig(s),last=c.states.at(-1);
    if(last&&last.signature===z){last.lastSeen=t;last.lastTarget7E=s.target7E;last.lastSide=s.side;return;}
    c.states.push({signature:z,firstSeen:t,lastSeen:t,firstTarget7E:s.target7E,lastTarget7E:s.target7E,firstSide:s.side,lastSide:s.side});
    if(c.states.length>MAX_STATES)c.states.shift();
  };
  const resolve=(c,s,t)=>{
    if(!c)return;
    if(c.lastTarget7E!==s.target7E){c.retargets.push({relMs:r1(t-c.startedAt),from7E:c.lastTarget7E,to7E:s.target7E,atActiveEdge:true});c.lastTarget7E=s.target7E;diag.retargets++;}
    diag.activeEdges++;diag.resolvedCycles++;diag.attackCounts['A'+s.attack]=(diag.attackCounts['A'+s.attack]||0)+1;
    const candidateSeen=c.candidateFirstAt!=null;
    if(candidateSeen){diag.candidateCycles++;diag.candidateAttackCounts['A'+s.attack]=(diag.candidateAttackCounts['A'+s.attack]||0)+1;}
    if(traces.length>=MAX_TRACES){diag.droppedCycles++;return;}
    const states=c.states.map(x=>({signature:x.signature,firstLeadMs:r1(t-x.firstSeen),lastLeadMs:r1(t-x.lastSeen),firstTarget7E:x.firstTarget7E,lastTarget7E:x.lastTarget7E,firstSide:x.firstSide,lastSide:x.lastSide}));
    const idx=[];for(let j=0;j<states.length;j++)if(states[j].signature===CANDIDATE_SIG)idx.push(j);
    traces.push({slot:c.slot,activeAttack:s.attack,cycleDurationMs:r1(t-c.startedAt),startedMidCycle:c.startedMidCycle,targetStart7E:c.targetStart7E,targetStart:c.targetStart,targetAtActive7E:s.target7E,targetAtActive:s.target,targetStable:c.targetStart7E===s.target7E,sideStart:c.sideStart,sideAtActive:s.side,sideStable:c.sideStart===s.side,retargets:c.retargets,candidateSeen,candidateFirstLeadMs:candidateSeen?r1(t-c.candidateFirstAt):null,candidateLastLeadMs:candidateSeen?r1(t-c.candidateLastAt):null,candidateStateIndexes:idx,distinctStates:states.length,finalPreActiveSignature:states.at(-1)?.signature||null,tail1:states.at(-1)?.signature||null,tail2:states.slice(-2).map(x=>x.signature),tail3:states.slice(-3).map(x=>x.signature),states});
  };
  await new Promise(done=>{const id=setInterval(()=>{
    const t=performance.now()-start;diag.polls++;
    for(let i=0;i<SLOTS;i++){
      const s=snap(i),p=prev.get(i)||null;
      if(s)diag.enemySamples++;
      if(!s||s.type!==18){
        if(cycles.has(i)){cycles.delete(i);diag.droppedCycles++;}
        if(s)prev.set(i,s);else prev.delete(i);
        continue;
      }
      diag.t18Samples++;
      if(s.attack===0){
        let c=cycles.get(i);
        if(!c||!p||p.type!==18||p.attack!==0){startCycle(s,t,!p||p.type!==18);c=cycles.get(i);}
        observe(c,s,t);
      }
      if(p&&p.type===18&&p.attack===0&&s.attack!==0){resolve(cycles.get(i),s,t);cycles.delete(i);}
      prev.set(i,s);
    }
    if(t>=DURATION){clearInterval(id);done();}
  },INTERVAL);});
  return{actualDurationMs:r1(performance.now()-start),diagnostics:diag,traces};
}

let code=await fetch(SRC+'?x='+Date.now(),{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error('WOF-052R base validator fetch '+r.status);return r.text();});
code=code
  .replaceAll('WOF-048','WOF-052')
  .replaceAll('V48','V52')
  .replaceAll('wof-future-danger-cycle-validator-v48r','wof-future-danger-cycle-validator-v52r')
  .replaceAll('__WOF_V48R_RESULT','__WOF_V52R_RESULT')
  .replaceAll('=== WOF FUTURE DANGER CYCLE VALIDATOR V48R JSON ===','=== WOF FUTURE DANGER CYCLE VALIDATOR V52R JSON ===');
const finalAnchor="self.__WOF_V52R_RESULT=base;\nconsole.log(MARKER);console.log(JSON.stringify(base,null,2));return base;";
if(!code.includes(finalAnchor))throw new Error(`[${COPY_ID}] base output suppression anchor not found`);
code=code.replace(finalAnchor,"self.__WOF_V52R_RESULT=base;return base;");
const [base,trace]=await Promise.all([(0,eval)(code),runT18CandidateTrace()]);
if(!base||base.copyId!==COPY_ID||base.project!==PROJECT||base.version!==VERSION||base.expectedMarker!==MARKER||base.readOnly!==true||base.ramWrites!==0)throw new Error(`[${COPY_ID}] embedded identity mismatch`);

const summary={candidateSignature:CANDIDATE_SIG,totalResolvedCycles:trace.diagnostics.resolvedCycles,candidateCycles:0,byAttack:{}};
for(const tr of trace.traces){
  if(!tr.candidateSeen)continue;
  summary.candidateCycles++;
  const attack=String(tr.activeAttack??'unknown');
  const s=summary.byAttack[attack]||(summary.byAttack[attack]={cycles:0,targetStable:0,sideStable:0,candidateFirstLeadSamples:[],candidateLastLeadSamples:[],finalExact:{},tail2Exact:{},tail3Exact:{},finalFamily:{},tail2Family:{},tail3Family:{},transitions:{},triples:{}});
  s.cycles++;if(tr.targetStable)s.targetStable++;if(tr.sideStable)s.sideStable++;
  if(tr.candidateFirstLeadMs!=null)s.candidateFirstLeadSamples.push(tr.candidateFirstLeadMs);
  if(tr.candidateLastLeadMs!=null)s.candidateLastLeadSamples.push(tr.candidateLastLeadMs);
  const exact=(tr.states||[]).map(x=>String(x.signature||'')).filter(Boolean);
  const firstIdx=(tr.candidateStateIndexes||[])[0];
  const post=(firstIdx==null?exact:exact.slice(firstIdx));
  const e1=post.at(-1)||null,e2=post.slice(-2),e3=post.slice(-3);
  add(s.finalExact,e1);if(e2.length===2)add(s.tail2Exact,e2.join(' -> '));if(e3.length===3)add(s.tail3Exact,e3.join(' -> '));
  const fam=[];for(const z of post){const f=family(z);if(!fam.length||fam.at(-1)!==f)fam.push(f);}
  const f1=fam.at(-1)||null,f2=fam.slice(-2),f3=fam.slice(-3);
  add(s.finalFamily,f1);if(f2.length===2)add(s.tail2Family,f2.join(' -> '));if(f3.length===3)add(s.tail3Family,f3.join(' -> '));
  for(let i=1;i<fam.length;i++)add(s.transitions,fam[i-1]+' -> '+fam[i]);
  for(let i=2;i<fam.length;i++)add(s.triples,fam[i-2]+' -> '+fam[i-1]+' -> '+fam[i]);
}
for(const s of Object.values(summary.byAttack)){
  s.targetStableRate=s.cycles?+(s.targetStable/s.cycles).toFixed(3):null;
  s.sideStableRate=s.cycles?+(s.sideStable/s.cycles).toFixed(3):null;
  s.candidateFirstLeadMin=s.candidateFirstLeadSamples.length?Math.min(...s.candidateFirstLeadSamples):null;
  s.candidateFirstLeadMedian=med(s.candidateFirstLeadSamples);
  s.candidateFirstLeadMax=s.candidateFirstLeadSamples.length?Math.max(...s.candidateFirstLeadSamples):null;
  s.candidateLastLeadMin=s.candidateLastLeadSamples.length?Math.min(...s.candidateLastLeadSamples):null;
  s.candidateLastLeadMedian=med(s.candidateLastLeadSamples);
  s.candidateLastLeadMax=s.candidateLastLeadSamples.length?Math.max(...s.candidateLastLeadSamples):null;
  s.finalExactTop=top(s.finalExact);s.tail2ExactTop=top(s.tail2Exact);s.tail3ExactTop=top(s.tail3Exact);
  s.finalFamilyTop=top(s.finalFamily);s.tail2FamilyTop=top(s.tail2Family);s.tail3FamilyTop=top(s.tail3Family);s.transitionTop=top(s.transitions,80);s.tripleTop=top(s.triples,80);
  delete s.finalExact;delete s.tail2Exact;delete s.tail3Exact;delete s.finalFamily;delete s.tail2Family;delete s.tail3Family;delete s.transitions;delete s.triples;
}
base.t18TraceDiagnostics=trace.diagnostics;
base.t18CycleTraces=trace.traces;
base.t18CandidateSequenceSummary=summary;
base.model.t18A4704Policy='WOF-051 direct prospective test proved the exact BODY4728/A4/B2/TM1 state is attack-ambiguous: 2 armed cycles resolved to A4704 at19.9ms and A4712 at100.4ms; target/side stayed2/2. Therefore the single-state A4704 candidate is NOT promoted and is removed as a predictor. WOF-052 traces ordered T18 states around every occurrence to seek a post-candidate sequence discriminator for A4704 versus A4712.';
base.model.t18Policy='Existing T18 A5440/A5424 production-shadows remain valid. WOF-051 reconfirmed both at4/4 strict with expected attack/target/side4/4.';
base.model.t18TracePolicy='t18CycleTraces records ordered T18 attack-zero cycles and marks exact BODY4728/A4/B2/TM1 candidate occurrences. t18CandidateSequenceSummary groups only candidate-containing cycles by eventual activeAttack and summarizes exact/TM* tails, transitions and triples after the candidate. Discovery only until a later prospective ordered-sequence validator is built.';
self.__WOF_V52R_RESULT=base;
console.log(MARKER);console.log(JSON.stringify(base,null,2));return base;
})().catch(e=>{console.error('[WOF-052R] ERROR',e);throw e;});
