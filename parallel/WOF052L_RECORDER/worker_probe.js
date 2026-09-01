(async()=>{
'use strict';
const VERSION='wof-052l-event-recorder-probe-v1';
const EXPECTED_SHA='5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62';
const CANDIDATE_SIG='S0/A4/B2|BODY4728|FE8b660|NX8b204|Vffff|TM1|P6C4736';
const INTERVAL_MS=10, MAX_STATES=64, EVENT_QUEUE_MAX=512, RECENT_CANDIDATES_MAX=64, RARE_MAX=256;
const old=globalThis.__WOF052L_RECORDER;
if(old&&old.version===VERSION&&old.running)return old.status();
if(old&&typeof old.stop==='function'){try{old.stop();}catch(_){}}

const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);
async function ensureModule(){
  if(good(globalThis._0x515056))return globalThis._0x515056;
  const until=performance.now()+8000;
  while(performance.now()<until){
    for(const k of Object.getOwnPropertyNames(globalThis)){
      let v; try{v=globalThis[k];}catch(_){continue;}
      if(good(v)){globalThis._0x515056=v;globalThis.__WOF_MODULE_GLOBAL_KEY=k;return v;}
    }
    await sleep(50);
  }
  return null;
}
const MOD=await ensureModule();
if(!MOD)return {ok:false,reason:'WASM module not ready',version:VERSION,readOnly:true,ramWrites:0,inputInjection:false};
const M=MOD.HEAPU8;
const RAM=MOD.HEAPU32?.[0x2e39e4>>>2]>>>0;
if(!RAM||RAM+0x10000>M.length)return {ok:false,reason:'CPS RAM base missing/outside heap',version:VERSION,readOnly:true,ramWrites:0,inputInjection:false};

async function verifyWorld(){
  const LOGICAL_BYTES=0x100000,VECTOR_SP=0x00FF62EE,VECTOR_PC=0x0000754A,DISPATCH_OFFSET=0x25DC;
  const DISPATCH=[0x06F4E4,0x07494C,0x071ADA,0x077B8E,0x07C6D2],MAX_DELTA=0x1000;
  const rawAt=p=>M[p]>>>0;
  const m8=(b,s,o)=>M[b+(s?(o^1):o)]>>>0;
  const m32=(b,s,o)=>(m8(b,s,o)*0x1000000+m8(b,s,o+1)*0x10000+m8(b,s,o+2)*0x100+m8(b,s,o+3))>>>0;
  const direct=[0x00,0xFF,0x62,0xEE,0x00,0x00,0x75,0x4A],swapped=[0xFF,0x00,0xEE,0x62,0x00,0x00,0x4A,0x75];
  const match=(p,a)=>{if(p<0||p+a.length>M.length)return false;for(let i=0;i<a.length;i++)if(rawAt(p+i)!==a[i])return false;return true;};
  const verify=(base,swap)=>{
    if(base<0||base+LOGICAL_BYTES>M.length)return null;
    if(m32(base,swap,0)!==VECTOR_SP||m32(base,swap,4)!==VECTOR_PC)return null;
    const vals=DISPATCH.map((_,i)=>m32(base,swap,DISPATCH_OFFSET+i*4));
    const ds=vals.map((v,i)=>(v-DISPATCH[i])|0),d=ds[0];
    if(!ds.every(x=>x===d)||Math.abs(d)>MAX_DELTA)return null;
    return {base,swap,delta:d,vals};
  };
  const found=[],seen=new Set(),add=z=>{if(!z)return;const k=z.base+'|'+z.swap;if(!seen.has(k)){seen.add(k);found.push(z);}};
  const chunk=0x40000;
  for(let start=0;start<M.length;start+=chunk){
    const end=Math.min(M.length-8,start+chunk+8);
    for(let p=start;p<end;p++){
      if(rawAt(p)===direct[0]&&match(p,direct))add(verify(p,false));
      if(rawAt(p)===swapped[0]&&match(p,swapped))add(verify(p,true));
    }
    if(start&&start%(chunk*16)===0)await sleep(0);
  }
  found.sort((a,b)=>a.base-b.base||Number(a.swap)-Number(b.swap));
  if(found.length!==1)return {ok:false,reason:'ROM locator candidate count '+found.length,candidateCount:found.length};
  if(!globalThis.crypto?.subtle?.digest)return {ok:false,reason:'Web Crypto SHA-256 unavailable',candidateCount:1};
  const c=found[0],logical=new Uint8Array(LOGICAL_BYTES);
  for(let i=0;i<LOGICAL_BYTES;i++)logical[i]=M[c.base+(c.swap?(i^1):i)]>>>0;
  const digest=await globalThis.crypto.subtle.digest('SHA-256',logical);
  const sha256=[...new Uint8Array(digest)].map(x=>x.toString(16).padStart(2,'0')).join('');
  return {
    ok:sha256===EXPECTED_SHA,
    reason:sha256===EXPECTED_SHA?'exact World 921031 full CPU-logical SHA-256':'full CPU-logical SHA-256 mismatch',
    sha256,expectedSha256:EXPECTED_SHA,description:'Warriors of Fate (World 921031)',
    locator:{heapBase:c.base,swap16:c.swap,uniformDelta:c.delta,dispatchEntries:c.vals}
  };
}
const identity=await verifyWorld();
if(!identity.ok)return {ok:false,reason:identity.reason,identity,version:VERSION,readOnly:true,ramWrites:0,inputInjection:false};

const B=a=>M[RAM+((((a-0xFF0000)&0xffff)^1))]>>>0;
const U16=a=>((B(a)<<8)|B(a+1))>>>0;
const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
const S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v;};
const X=a=>Math.round(S32(a+4)/65536);
const Y=a=>Math.round(S32(a+8)/65536);
const ENEMY=0xFFC0BC,STRIDE=0xE0,SLOTS=20;
const PBASE={0:0xFFBE1C,4:0xFFBEFC,8:0xFFBFDC},PN={0:'P1',4:'P2',8:'P3'};
const side=dx=>dx==null?null:dx<-4?'LEFT':dx>4?'RIGHT':'CENTER';
const hx=n=>(n>>>0).toString(16);
const r1=x=>Math.round(x*10)/10;
const fam=z=>String(z||'').replace(/\|TM[^|]*/,'|TM*');
const add=(m,k,n=1)=>{if(k==null||k==='')return;m[k]=(m[k]||0)+n;};
const addCapped=(m,k,cap=512,n=1)=>{if(k==null||k==='')return;if(Object.prototype.hasOwnProperty.call(m,k)||Object.keys(m).length<cap){m[k]=(m[k]||0)+n;return true;}return false;};
function snap(i){
  const a=ENEMY+i*STRIDE,type=U16(a+0x20);
  if(type>=47)return null;
  const fe=U32(a+0x12),nx=U32(a+0x2C);
  if(!fe&&!nx)return null;
  const t=U16(a+0x7E),pb=PBASE[t],ex=X(a),ey=Y(a),tx=pb?X(pb):null,dx=tx==null?null:tx-ex;
  return {slot:i,type,target7E:t,target:PN[t]||null,side:side(dx),x:ex,y:ey,state99:B(a+0x99),action2A:B(a+0x2A),
    b2B:B(a+0x2B),body:U16(a+0x6E),attack:U16(a+0x70),frameEnd:fe,next:nx,value30:U32(a+0x30),
    timer34:U16(a+0x34),payload6C:U16(a+0x6C)};
}
const sig=s=>`S${s.state99}/A${s.action2A}/B${s.b2B}|BODY${s.body}|FE${hx(s.frameEnd)}|NX${hx(s.next)}|V${hx(s.value30)}|TM${s.timer34}|P6C${s.payload6C}`;
const isCandidate=s=>s&&s.type===18&&s.attack===0&&sig(s)===CANDIDATE_SIG;

const startedEpoch=Date.now(),startedPerf=performance.now();
const prev=new Map(),cycles18=new Map(),cycles23=new Map();
const queue=[],recentCandidates=[],rareSeen=new Set();
let running=true,timer=null,eventSeq=0,lastContextAt=0;
const d={
  polls:0,enemySamples:0,activeEdges:0,retargets:0,typeSamples:{},activeAttackFrequency:{},targetSamples:{P1:0,P2:0,P3:0,other:0},
  playerCountHist:[0,0,0,0],playerPresence:{P1:0,P2:0,P3:0},sceneTypeSets:{},
  t18:{samples:0,attackZeroStarts:0,activeEdges:0,resolvedCycles:0,droppedCycles:0,candidateSamples:0,candidateCycles:0,candidateAttackCounts:{}},
  t23:{samples:0,attackZeroStarts:0,activeEdges:0,resolvedCycles:0,droppedCycles:0,attackCounts:{},a5888Cycles:0},
  rareDescriptorAttack:{},mapOverflow:{rareDescriptorAttack:0,sceneTypeSets:0},eventQueueDrops:0
};
function emit(kind,payload){
  const ev={id:++eventSeq,kind,atEpoch:Date.now(),...payload};
  queue.push(ev); if(queue.length>EVENT_QUEUE_MAX){queue.shift();d.eventQueueDrops++;}
  return ev;
}
function startCycle(map,s,t,kind,startedMidCycle){
  const c={slot:s.slot,type:s.type,startedAt:t,startedMidCycle:!!startedMidCycle,targetStart7E:s.target7E,targetStart:s.target,sideStart:s.side,
    xStart:s.x,yStart:s.y,lastTarget7E:s.target7E,retargets:[],states:[],candidateFirstAt:null,candidateLastAt:null};
  map.set(s.slot,c);
  d[kind].attackZeroStarts++;
  return c;
}
function observe(c,s,t,kind){
  if(c.lastTarget7E!==s.target7E){
    c.retargets.push({relMs:r1(t-c.startedAt),from7E:c.lastTarget7E,to7E:s.target7E});
    c.lastTarget7E=s.target7E; d.retargets++;
  }
  if(kind==='t18'&&isCandidate(s)){
    d.t18.candidateSamples++; if(c.candidateFirstAt==null)c.candidateFirstAt=t;c.candidateLastAt=t;
  }
  const z=sig(s),last=c.states[c.states.length-1];
  if(last&&last.signature===z){
    last.lastSeen=t;last.lastTarget7E=s.target7E;last.lastSide=s.side;last.x=s.x;last.y=s.y;return;
  }
  c.states.push({signature:z,family:fam(z),firstSeen:t,lastSeen:t,firstTarget7E:s.target7E,lastTarget7E:s.target7E,firstSide:s.side,lastSide:s.side,x:s.x,y:s.y});
  if(c.states.length>MAX_STATES)c.states.shift();
}
function resolve(map,c,s,t,kind){
  if(!c)return;
  if(c.lastTarget7E!==s.target7E){
    c.retargets.push({relMs:r1(t-c.startedAt),from7E:c.lastTarget7E,to7E:s.target7E,atActiveEdge:true});
    c.lastTarget7E=s.target7E; d.retargets++;
  }
  d[kind].activeEdges++;d[kind].resolvedCycles++;
  const states=c.states.map(x=>({signature:x.signature,family:x.family,firstLeadMs:r1(t-x.firstSeen),lastLeadMs:r1(t-x.lastSeen),
    firstTarget7E:x.firstTarget7E,lastTarget7E:x.lastTarget7E,firstSide:x.firstSide,lastSide:x.lastSide,x:x.x,y:x.y}));
  const candidateIndexes=[]; if(kind==='t18')for(let j=0;j<states.length;j++)if(states[j].signature===CANDIDATE_SIG)candidateIndexes.push(j);
  const candidateSeen=kind==='t18'&&c.candidateFirstAt!=null;
  const tr={slot:c.slot,type:c.type,activeAttack:s.attack,cycleDurationMs:r1(t-c.startedAt),startedMidCycle:c.startedMidCycle,
    targetStart7E:c.targetStart7E,targetStart:c.targetStart,targetAtActive7E:s.target7E,targetAtActive:s.target,
    targetStable:c.targetStart7E===s.target7E,sideStart:c.sideStart,sideAtActive:s.side,sideStable:c.sideStart===s.side,
    retargets:c.retargets,distinctStates:states.length,finalPreActiveSignature:states.length?states[states.length-1].signature:null,
    tail1:states.length?states[states.length-1].signature:null,tail2:states.slice(-2).map(x=>x.signature),tail3:states.slice(-3).map(x=>x.signature),states};
  if(kind==='t18'){
    tr.candidateSeen=candidateSeen;tr.candidateStateIndexes=candidateIndexes;
    tr.candidateFirstLeadMs=candidateSeen?r1(t-c.candidateFirstAt):null;tr.candidateLastLeadMs=candidateSeen?r1(t-c.candidateLastAt):null;
    if(candidateSeen){
      d.t18.candidateCycles++;add(d.t18.candidateAttackCounts,'A'+s.attack);
      const ev=emit('t18_candidate_cycle',tr);recentCandidates.push(ev);if(recentCandidates.length>RECENT_CANDIDATES_MAX)recentCandidates.shift();
    }else emit('t18_cycle',tr);
  }else{
    add(d.t23.attackCounts,'A'+s.attack);if(s.attack===5888)d.t23.a5888Cycles++;
    emit(s.attack===5888?'t23_a5888_cycle':'t23_cycle',tr);
  }
}
function sampleContext(now){
  if(now-lastContextAt<250)return;
  lastContextAt=now;
  const ps=[];for(const [idx,a] of [[0,0xFFBE1C],[1,0xFFBEFC],[2,0xFFBFDC]])if(B(a)){ps.push(idx);d.playerPresence['P'+(idx+1)]++;}
  d.playerCountHist[Math.min(3,ps.length)]++;
  const types=[];
  for(let i=0;i<SLOTS;i++){const s=snap(i);if(s)types.push(s.type);}
  const key=[...new Set(types)].sort((a,b)=>a-b).map(x=>'T'+x).join('+')||'NONE';
  if(!addCapped(d.sceneTypeSets,key,256))d.mapOverflow.sceneTypeSets++;
}
function tick(){
  if(!running)return;
  const t=performance.now()-startedPerf;d.polls++;sampleContext(t);
  for(let i=0;i<SLOTS;i++){
    const s=snap(i),p=prev.get(i)||null;
    if(s){
      d.enemySamples++;add(d.typeSamples,'T'+s.type);
      if(s.target==='P1')d.targetSamples.P1++;else if(s.target==='P2')d.targetSamples.P2++;else if(s.target==='P3')d.targetSamples.P3++;else d.targetSamples.other++;
    }
    if(p&&s&&p.type===s.type&&p.attack===0&&s.attack!==0){
      d.activeEdges++;add(d.activeAttackFrequency,`T${s.type}|A${s.attack}`);
      const rz=`T${s.type}|${sig(p)}->A${s.attack}`;if(!addCapped(d.rareDescriptorAttack,rz,512))d.mapOverflow.rareDescriptorAttack++;
      if(rareSeen.size<RARE_MAX&&!rareSeen.has(rz)){rareSeen.add(rz);emit('descriptor_attack_edge',{type:s.type,attack:s.attack,preActiveSignature:sig(p),target7E:s.target7E,target:s.target,side:s.side});}
    }
    for(const [kind,type,map] of [['t18',18,cycles18],['t23',23,cycles23]]){
      if(!s||s.type!==type){
        if(map.has(i)){map.delete(i);d[kind].droppedCycles++;}
        continue;
      }
      d[kind].samples++;
      if(s.attack===0){
        let c=map.get(i);
        const discontinuity=!!(p&&p.type===type&&p.attack===0&&Math.abs((p.x??0)-(s.x??0))>160);
        if(!c||!p||p.type!==type||p.attack!==0||discontinuity){
          if(c&&discontinuity){map.delete(i);d[kind].droppedCycles++;}
          c=startCycle(map,s,t,kind,!p||p.type!==type);
        }
        observe(c,s,t,kind);
      }
      if(p&&p.type===type&&p.attack===0&&s.attack!==0){resolve(map,map.get(i),s,t,kind);map.delete(i);}
    }
    if(s)prev.set(i,s);else prev.delete(i);
  }
}
function status(){
  return {ok:true,version:VERSION,running,startedEpoch,durationMs:r1(performance.now()-startedPerf),identity,
    readOnly:true,ramWrites:0,inputInjection:false,candidateSignature:CANDIDATE_SIG,queueDepth:queue.length,eventSeq,
    diagnostics:JSON.parse(JSON.stringify(d)),recentCandidates:JSON.parse(JSON.stringify(recentCandidates))};
}
function drain(){
  const events=queue.splice(0,queue.length);
  return {ok:true,version:VERSION,events,status:status()};
}
function stop(){
  if(!running)return status();
  running=false;if(timer!=null){clearInterval(timer);timer=null;}
  for(const [kind,map] of [['t18',cycles18],['t23',cycles23]]){for(const _ of map.values())d[kind].droppedCycles+=1;map.clear();}
  return status();
}
const api={version:VERSION,get running(){return running;},status,drain,stop};
globalThis.__WOF052L_RECORDER=api;
timer=setInterval(tick,INTERVAL_MS);
return status();
})()