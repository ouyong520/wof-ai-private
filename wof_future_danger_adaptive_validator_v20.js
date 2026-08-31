(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);
if(!good(self._0x515056)){
  const until=performance.now()+8000;let hit=null;
  while(performance.now()<until&&!hit){for(const k of Object.getOwnPropertyNames(self)){let v;try{v=self[k]}catch(_){continue}if(good(v)){hit={k,v};break}}if(!hit)await new Promise(r=>setTimeout(r,50));}
  if(!hit)throw new Error('WOF WASM module not found. Select the live gstyphoon.js Worker after game is running.');
  self._0x515056=hit.v;self.__WOF_MODULE_GLOBAL_KEY=hit.k;console.log('✅ WOF WASM module resolved:',hit.k,'→ _0x515056');
}
if(!self.__WOF_ROM_LOC_CACHE)await load('wof_resume_dispatch_selector.js');
const C=self.__WOF_ROM_LOC_CACHE;if(!C)throw new Error('ROM cache missing');
const M=self._0x515056.HEAPU8,romBase=C.base,SW=!!C.swap16,ROMMAX=Math.min(0x100000,M.length-romBase);
const r8=o=>M[romBase+(SW?(o^1):o)]>>>0;
const r16=o=>((r8(o)<<8)|r8(o+1))>>>0;
const r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
const validRom=v=>v>=0x2000&&v<ROMMAX&&(v&1)===0;
const gate={dispatcher25C8:r16(0x25C8)===0x3228&&r16(0x25D0)===0x287B&&r16(0x25D4)===0x2874,handoff247C:r16(0x247C)===0x2C5C&&r16(0x247E)===0x215C&&r16(0x2482)===0x321C,d0_20Source:r16(0x6A62)===0x7014&&r16(0x6A64)===0x4EB8&&r16(0x6A66)===0x25C8,attackField:true,xyFields:true};
const gateStrict=Object.values(gate).every(Boolean);if(!gateStrict)throw new Error('V20 strict gate failed '+JSON.stringify(gate));
function parseDescriptor(at){if(!validRom(at)||at+14>ROMMAX)return null;const frameEnd=r32(at)>>>0,value30=r32(at+4)>>>0,timerRaw=r16(at+8)>>>0;if(!validRom(frameEnd))return null;const flagged=!!(timerRaw&0x8000),timer=flagged?(timerRaw&0x7fff):timerRaw,next=flagged?(r32(at+10)>>>0):((at+10)>>>0);if(!validRom(next))return null;return{at,frameEnd,value30,timer,next};}
function typeMap(type){if(type<0||type>=47)return null;const table=r32(0x25DC+type*4)>>>0;if(!validRom(table))return null;const p=r32(table+20)>>>0;return{type,d20:parseDescriptor(p)};}
const maps=new Map(),getMap=t=>{if(!maps.has(t))maps.set(t,typeMap(t));return maps.get(t);};
const R=self._0x515056?.HEAPU32?.[0x2e39e4>>>2]>>>0;if(!R)throw new Error('CPS RAM base missing');
const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0;
const U16=a=>((B(a)<<8)|B(a+1))>>>0;
const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
const S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v;};
const PX=a=>Math.round(S32(a+4)/65536),PY=a=>Math.round(S32(a+8)/65536);
const ENEMY=0xFFC0BC,STRIDE=0xE0,SLOTS=20,PLAYERS={0:'P1',4:'P2',8:'P3'},PBASE={0:0xFFBE1C,4:0xFFBEFC,8:0xFFBFDC};
const side=dx=>dx<-4?'LEFT':dx>4?'RIGHT':'CENTER',lane=dy=>dy<-4?'UP':dy>4?'DOWN':'SAME';
function geom(a,target7E){const ex=PX(a),ey=PY(a),pb=PBASE[target7E];if(!pb)return{enemyX:ex,enemyY:ey,targetX:null,targetY:null,dx:null,dy:null,absDx:null,absDy:null,side:null,lane:null};const tx=PX(pb),ty=PY(pb),dx=tx-ex,dy=ty-ey;return{enemyX:ex,enemyY:ey,targetX:tx,targetY:ty,dx,dy,absDx:Math.abs(dx),absDy:Math.abs(dy),side:side(dx),lane:lane(dy)};}
function snap(slot){const a=ENEMY+slot*STRIDE,type=U16(a+0x20);if(type>=47)return null;const frameEnd=U32(a+0x12),next=U32(a+0x2C);if(frameEnd===0&&next===0)return null;const target7E=U16(a+0x7E),value30=U32(a+0x30),timer=U16(a+0x34),d20=getMap(type)?.d20||null;const s={slot,a,type,target7E,target:PLAYERS[target7E]||null,state99:B(a+0x99),action2A:B(a+0x2A),b2B:B(a+0x2B),timer,attack:U16(a+0x70),body:U16(a+0x6E),frameEnd,next,value30,...geom(a,target7E)};s.inD20=!!(d20&&frameEnd===d20.frameEnd&&value30===d20.value30&&next===d20.next&&timer<=d20.timer);s.d20=d20;return s;}
const T16_FAST_TUPLES=new Set(['0/4/2','0/4/4','2/4/2','2/4/4','2/0/0','4/4/2','4/4/4','4/0/0']);
const RULES=[
{id:'T16_FAST_100',type:16,horizon:100,expected:[6432],match:s=>s.type===16&&!s.inD20&&s.attack===0&&s.body===4856&&s.frameEnd===0x851ae&&s.next===0x84c44&&s.value30===0xffff&&T16_FAST_TUPLES.has(`${s.state99}/${s.action2A}/${s.b2B}`)},
{id:'T16_MID_250',type:16,horizon:250,expected:[6432],match:s=>s.type===16&&!s.inD20&&s.attack===0&&s.body===4856&&s.state99===2&&s.action2A===4&&s.b2B===2&&s.frameEnd===0x85240&&s.next===0x84c3a&&s.value30===0x100000},
{id:'T7_817FE_250',type:7,horizon:250,expected:[2528,2536],match:s=>s.type===7&&!s.inD20&&s.attack===0&&s.body===1800&&s.state99===0&&s.action2A===6&&s.b2B===4&&s.frameEnd===0x81c5e&&s.next===0x817fe&&s.value30===0},
{id:'T7_81808_250',type:7,horizon:250,expected:[2528,2536],match:s=>s.type===7&&!s.inD20&&s.attack===0&&s.body===1800&&s.state99===0&&s.action2A===6&&s.b2B===4&&s.frameEnd===0x81ca4&&s.next===0x81808&&s.value30===0},
{id:'T30_FAST_100',type:30,horizon:100,expected:[2528,2536],match:s=>s.type===30&&!s.inD20&&s.attack===0&&s.body===1800&&s.state99===0&&s.action2A===0&&s.b2B===0}
];
const DURATION=120000,INTERVAL=20,D20_WATCH=1200,start=performance.now();
const prev=new Map(),cycle=new Map(),armedCycle=new Map(),branchWatches=[],d20Open=new Map(),d20Rows=[],activeEdges=[];let wid=0,did=0,aid=0;
const typesSeen=new Set();
const diag={polls:0,enemySamples:0,activeEdges:0,validTargetActiveEdges:0,d20Samples:0,d20Entries:0,d20ExactEntries:0,d20LateEntries:0,branchSignals:0};
const coverage={};for(const r of RULES)coverage[r.id]={type:r.type,typeSamples:0,rawMatchSamples:0,transitionEntries:0,signals:0};
const keyArm=(slot,rule)=>slot+'|'+rule;
function armBranch(rule,s,t){const c=cycle.get(s.slot)||0,ak=keyArm(s.slot,rule.id);if(armedCycle.get(ak)===c)return;armedCycle.set(ak,c);branchWatches.push({id:++wid,rule:rule.id,type:s.type,slot:s.slot,cycle:c,horizon:rule.horizon,expected:rule.expected,at:t,target7E:s.target7E,target:s.target,side:s.side,resolved:false,censored:false,hit:false,leadMs:null,attack:null,attackExpected:null,targetSame:null,sideSame:null,activeAbsDx:null,activeAbsDy:null});diag.branchSignals++;coverage[rule.id].signals++;console.log(`[WOF V20] BRANCH SIGNAL ${rule.id} T${s.type} slot${s.slot} -> ${s.target||'?'} `);}
function startD20(s,t){const old=d20Open.get(s.slot);if(old&&!old.resolved){old.resolved=true;old.outcome='retrigger';old.censored=true;d20Rows.push(old);}const exact=s.d20&&s.timer===s.d20.timer;const e={id:++did,slot:s.slot,type:s.type,entryRel:t,entryTarget:s.target,entryTarget7E:s.target7E,entryExact:!!exact,staticStartTimer:s.d20?.timer??null,seenEntryTimer:s.timer,observedLagTicks:s.d20?Math.max(0,s.d20.timer-s.timer):null,state99:s.state99,action2A:s.action2A,b2B:s.b2B,body:s.body,frameEnd:s.frameEnd,next:s.next,value30:s.value30,entryAbsDx:s.absDx,entryAbsDy:s.absDy,entrySide:s.side,exitRel:null,outcome:null,leadToActiveMs:null,activeAttack:null,activeTarget:null,targetSame:null,sideSame:null,activeAbsDx:null,activeAbsDy:null,targetSwitches:[],resolved:false,censored:false};d20Open.set(s.slot,e);diag.d20Entries++;if(exact)diag.d20ExactEntries++;else diag.d20LateEntries++;console.log(`[WOF V20] D20 ENTRY T${s.type} slot${s.slot} -> ${s.target||'?'} timer ${s.timer}/${s.d20?.timer??'?'} `);}
function censorSlot(slot,reason,t){for(const w of branchWatches){if(!w.resolved&&w.slot===slot){w.resolved=true;w.censored=true;w.censorReason=reason;}}const e=d20Open.get(slot);if(e&&!e.resolved){e.resolved=true;e.censored=true;e.outcome=reason;e.endRel=t;d20Rows.push(e);d20Open.delete(slot);}}
function activeEdge(s,t){activeEdges.push({id:++aid,rel:t,slot:s.slot,type:s.type,target:s.target,target7E:s.target7E,attack:s.attack,body:s.body,absDx:s.absDx,absDy:s.absDy,side:s.side,lane:s.lane});diag.activeEdges++;if(s.target)diag.validTargetActiveEdges++;
 for(const w of branchWatches){if(w.resolved||w.slot!==s.slot||w.type!==s.type)continue;const lead=t-w.at;if(lead<0||lead>w.horizon)continue;w.resolved=true;w.hit=true;w.leadMs=lead;w.attack=s.attack;w.attackExpected=w.expected.includes(s.attack);w.targetSame=w.target7E===s.target7E;w.sideSame=w.side===s.side;w.activeAbsDx=s.absDx;w.activeAbsDy=s.absDy;console.log(`[WOF V20] BRANCH HIT ${w.rule} ${lead}ms attack=${s.attack}`);}
 const e=d20Open.get(s.slot);if(e&&!e.resolved&&e.type===s.type){const lead=t-e.entryRel;if(lead<=D20_WATCH){e.resolved=true;e.outcome='active';e.leadToActiveMs=lead;e.activeAttack=s.attack;e.activeTarget=s.target;e.targetSame=e.entryTarget7E===s.target7E;e.sideSame=e.entrySide===s.side;e.activeAbsDx=s.absDx;e.activeAbsDy=s.absDy;d20Rows.push(e);d20Open.delete(s.slot);console.log(`[WOF V20] D20 ACTIVE T${s.type} ${lead}ms attack=${s.attack}`);}}
 cycle.set(s.slot,(cycle.get(s.slot)||0)+1);
}
function expire(t){for(const w of branchWatches){if(!w.resolved&&t-w.at>w.horizon){w.resolved=true;w.hit=false;}}
 for(const [slot,e] of d20Open){if(!e.resolved&&t-e.entryRel>D20_WATCH){e.resolved=true;e.outcome='horizonComplete';e.endRel=t;d20Rows.push(e);d20Open.delete(slot);}}
}
await new Promise(resolve=>{const id=setInterval(()=>{const t=Math.round(performance.now()-start);diag.polls++;
 for(let i=0;i<SLOTS;i++){
  const s=snap(i),p=prev.get(i)||null;
  if(!s){if(p)censorSlot(i,'slotGone',t);prev.delete(i);continue;}
  typesSeen.add(s.type);diag.enemySamples++;if(s.inD20)diag.d20Samples++;
  if(p&&p.type!==s.type){censorSlot(i,'typeChange',t);cycle.set(i,(cycle.get(i)||0)+1);}
  const open=d20Open.get(i);if(open&&!open.resolved&&p&&p.target7E!==s.target7E)open.targetSwitches.push({rel:t-open.entryRel,from:PLAYERS[p.target7E]||p.target7E,to:s.target});
  if(s.inD20&&(!p||p.type!==s.type||!p.inD20))startD20(s,t);
  if(p&&p.inD20&&!s.inD20){const e=d20Open.get(i);if(e&&!e.resolved&&e.exitRel==null)e.exitRel=t-e.entryRel;}
  if(p&&p.attack===0&&s.attack!==0)activeEdge(s,t);
  for(const rule of RULES){if(rule.type!==s.type)continue;const c=coverage[rule.id];c.typeSamples++;const m=rule.match(s),pm=!!(p&&p.type===s.type&&rule.match(p));if(m)c.rawMatchSamples++;if(m&&!pm){c.transitionEntries++;armBranch(rule,s,t);}}
  prev.set(i,s);
 }
 expire(t);
 if(t>=DURATION){clearInterval(id);for(const w of branchWatches){if(!w.resolved){w.resolved=true;w.censored=true;w.censorReason='captureEnd';}}for(const [slot,e] of d20Open){if(!e.resolved){e.resolved=true;e.censored=true;e.outcome='captureEnd';d20Rows.push(e);}d20Open.delete(slot);}resolve();}
 },INTERVAL);});
const median=a=>{if(!a.length)return null;const b=[...a].sort((x,y)=>x-y),m=Math.floor(b.length/2);return b.length%2?b[m]:Math.round((b[m-1]+b[m])/2);};
const pct=(a,p)=>{if(!a.length)return null;const b=[...a].sort((x,y)=>x-y),i=Math.ceil(p*b.length)-1;return b[Math.max(0,Math.min(b.length-1,i))];};
const branchStats={};for(const r of RULES)branchStats[r.id]={rule:r.id,type:r.type,horizonMs:r.horizon,...coverage[r.id],evaluable:0,hit:0,miss:0,censored:0,leads:[],attackExpected:0,attackTotal:0,targetSame:0,targetTotal:0,sideSame:0,sideTotal:0};
for(const w of branchWatches){const q=branchStats[w.rule];if(w.censored){q.censored++;continue;}q.evaluable++;if(w.hit){q.hit++;q.leads.push(w.leadMs);q.attackTotal++;if(w.attackExpected)q.attackExpected++;if(w.targetSame!=null){q.targetTotal++;if(w.targetSame)q.targetSame++;}if(w.sideSame!=null){q.sideTotal++;if(w.sideSame)q.sideSame++;}}else q.miss++;}
for(const q of Object.values(branchStats)){q.precision=q.evaluable?+(q.hit/q.evaluable).toFixed(3):null;q.attackExpectedRate=q.attackTotal?+(q.attackExpected/q.attackTotal).toFixed(3):null;q.targetSameRate=q.targetTotal?+(q.targetSame/q.targetTotal).toFixed(3):null;q.sideStableRate=q.sideTotal?+(q.sideSame/q.sideTotal).toFixed(3):null;q.leads.sort((a,b)=>a-b);}
const byType={};for(const e of d20Rows){const k='T'+e.type;if(!byType[k])byType[k]={type:e.type,episodes:0,active:0,horizonComplete:0,censored:0,le250:0,le500:0,le1000:0,leads:[],targetSame:0,targetTotal:0,sideSame:0,sideTotal:0};const q=byType[k];q.episodes++;if(e.outcome==='active'){q.active++;q.leads.push(e.leadToActiveMs);if(e.leadToActiveMs<=250)q.le250++;if(e.leadToActiveMs<=500)q.le500++;if(e.leadToActiveMs<=1000)q.le1000++;if(e.targetSame!=null){q.targetTotal++;if(e.targetSame)q.targetSame++;}if(e.sideSame!=null){q.sideTotal++;if(e.sideSame)q.sideSame++;}}else if(e.outcome==='horizonComplete')q.horizonComplete++;else q.censored++;}
for(const q of Object.values(byType)){q.p250=q.episodes?+(q.le250/q.episodes).toFixed(3):null;q.p500=q.episodes?+(q.le500/q.episodes).toFixed(3):null;q.p1000=q.episodes?+(q.le1000/q.episodes).toFixed(3):null;q.targetSameRate=q.targetTotal?+(q.targetSame/q.targetTotal).toFixed(3):null;q.sideStableRate=q.sideTotal?+(q.sideSame/q.sideTotal).toFixed(3):null;q.leads.sort((a,b)=>a-b);}
const cl=new Map();for(const e of activeEdges){const k=`T${e.type}|A${e.attack}`;let g=cl.get(k);if(!g){g={key:k,type:e.type,attack:e.attack,count:0,absDx:[],absDy:[]};cl.set(k,g);}g.count++;if(e.absDx!=null)g.absDx.push(e.absDx);if(e.absDy!=null)g.absDy.push(e.absDy);}
const attackClusters=[...cl.values()].map(g=>({key:g.key,type:g.type,attack:g.attack,count:g.count,absDxMedian:median(g.absDx),absDxP90:pct(g.absDx,.9),absDxP95:pct(g.absDx,.95),absDyMedian:median(g.absDy),absDyP90:pct(g.absDy,.9),absDyP95:pct(g.absDy,.95)})).sort((a,b)=>b.count-a.count);
const out={version:'wof-future-danger-adaptive-validator-v20',readOnly:true,ramWrites:0,gate,gateStrict,durationRequestedMs:DURATION,intervalMs:INTERVAL,model:{purpose:'make every room useful: opportunistically validate V18 branch rules while also calibrating structural D0=20 timing for every enemy type seen',branchDedupe:'at most one signal per rule/slot/attack-cycle',d20Capture:'structural D0=20 transition, timer<=static start accepted; 1200ms watch',targetPolicy:'live enemy+0x7E authoritative',geometry:'ACTIVE-start distances are empirical, not exact hitboxes'},diagnostics:{...diag,typesSeen:[...typesSeen].sort((a,b)=>a-b)},totals:{branchSignals:branchWatches.length,d20Episodes:d20Rows.length,activeEdges:activeEdges.length},branchStats,byType,d20Rows:d20Rows.slice(0,120),attackClusters:attackClusters.slice(0,80),note:'Zero branch signals are interpretable from typeSamples/rawMatchSamples/transitionEntries. D0 rows are generic calibration, not a claim that D0=20 has one universal horizon.'};
self.__WOF_FUTURE_DANGER_ADAPTIVE_V20=out;console.log('=== FUTURE DANGER ADAPTIVE VALIDATOR V20 JSON ===');console.log(JSON.stringify(out,null,2));return out;
})().catch(e=>{console.error('WOF_V20_ERROR',e);throw e;});
