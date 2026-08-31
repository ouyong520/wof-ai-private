(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
if(!self.__WOF_ROM_LOC_CACHE)await load('wof_resume_dispatch_selector.js');
const C=self.__WOF_ROM_LOC_CACHE;if(!C)throw new Error('ROM cache missing');
const M=_0x515056.HEAPU8,romBase=C.base,SW=!!C.swap16,ROMMAX=Math.min(0x100000,M.length-romBase);
const r8=o=>M[romBase+(SW?(o^1):o)]>>>0;
const r16=o=>((r8(o)<<8)|r8(o+1))>>>0;
const r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
const validRom=v=>v>=0x2000&&v<ROMMAX&&(v&1)===0;
const h=(x,n=6)=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(n,'0');
const gate={dispatcher25C8:r16(0x25C8)===0x3228&&r16(0x25D0)===0x287B&&r16(0x25D4)===0x2874,handoff247C:r16(0x247C)===0x2C5C&&r16(0x247E)===0x215C&&r16(0x2482)===0x321C,d0_20Source:r16(0x6A62)===0x7014&&r16(0x6A64)===0x4EB8&&r16(0x6A66)===0x25C8,attackField:true};
function parseDescriptor(at){if(!validRom(at)||at+14>ROMMAX)return null;const frameEnd=r32(at)>>>0,value30=r32(at+4)>>>0,timerRaw=r16(at+8)>>>0;if(!validRom(frameEnd))return null;const flagged=!!(timerRaw&0x8000),timer=flagged?(timerRaw&0x7fff):timerRaw,next=flagged?(r32(at+10)>>>0):((at+10)>>>0);if(!validRom(next))return null;return{at,frameEnd,value30,timerRaw,flagged,timer,next};}
function typeMap(type){if(type<0||type>=47)return null;const table=r32(0x25DC+type*4)>>>0;if(!validRom(table))return null;const p=r32(table+20)>>>0;return{type,table,d20:parseDescriptor(p)};}
const R=_0x515056?.HEAPU32?.[0x2e39e4>>>2]>>>0;if(!R)throw new Error('CPS RAM base missing');
const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0;
const U16=a=>((B(a)<<8)|B(a+1))>>>0;
const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
const ENEMY=0xFFC0BC,STRIDE=0xE0,SLOTS=20,PLAYERS={0:'P1',4:'P2',8:'P3'};
const maps=new Map(),getMap=t=>{if(!maps.has(t))maps.set(t,typeMap(t));return maps.get(t);};
function descMatches(s,d){return!!d&&s.frameEnd===d.frameEnd&&s.value30===d.value30&&s.next===d.next&&s.timer<=d.timer;}
function snap(slot){const a=ENEMY+slot*STRIDE,type=U16(a+0x20);if(type>=47)return null;const frameEnd=U32(a+0x12),next=U32(a+0x2C);if(frameEnd===0&&next===0)return null;const target7E=U16(a+0x7E),s={slot,type,target7E,target:PLAYERS[target7E]||null,state99:B(a+0x99),action2A:B(a+0x2A),b2B:B(a+0x2B),timer:U16(a+0x34),attack:U16(a+0x70),body:U16(a+0x6E),frameEnd,next,value30:U32(a+0x30)};const d20=getMap(type)?.d20;s.inD20=descMatches(s,d20);s.d20Exact=!!(s.inD20&&d20&&s.timer===d20.timer);return s;}
const mini=s=>({type:s.type,target:s.target,target7E:s.target7E,state99:s.state99,action2A:s.action2A,b2B:s.b2B,timer:s.timer,attack:s.attack,body:s.body,frameEnd:h(s.frameEnd,8),next:h(s.next,8),value30:h(s.value30,8)});
const DURATION=120000,INTERVAL=20,MAX_EPISODES=40,POST_ACTIVE=60,start=performance.now();
const prev=new Map(),episodes=new Map(),done=[],signals=[];let epSeq=0,signalSeq=0;
const RULES={
 T33_ENTRY_100:{horizon:100,level:'IMMINENT',evidence:'V9 T33 D0=20 ENTRY 2/2 <=100ms'},
 T21_EXIT_250:{horizon:250,level:'IMMINENT',evidence:'V10 T21 D0=20 exit -> active leads 38/40/81/120/219ms'},
 T18_LE3_S0_A4_B0_250:{horizon:250,level:'CANDIDATE',evidence:'V9 2/2 <=250ms; retain as provisional until repeated'},
 T24_AB32_S2_A4_B10_250:{horizon:250,level:'CANDIDATE',evidence:'V10 structural state about 2/3 <=250ms; not low-FP yet'}
};
function finishEp(ep,t,reason){if(ep.done)return;ep.done=true;ep.endRel=t-ep.startAt;ep.endReason=reason;done.push(ep);episodes.delete(ep.slot);}
function emit(ep,s,t,rule){if(ep.ruleSeen.has(rule))return;ep.ruleSeen.add(rule);const cfg=RULES[rule],sig={id:++signalSeq,epId:ep.id,slot:ep.slot,type:ep.type,rule,level:cfg.level,horizonMs:cfg.horizon,atRel:t-ep.startAt,targetAtSignal:s.target,target7EAtSignal:s.target7E,state:mini(s),resolved:false,hit:null,leadToActiveMs:null,activeTarget:null,targetSameAtActive:null};signals.push(sig);ep.signals.push(sig);}
function startEp(s,t){const old=episodes.get(s.slot);if(old)finishEp(old,t,'retrigger');const ep={id:++epSeq,slot:s.slot,type:s.type,startAt:t,entryTarget:s.target,exitRel:null,firstAttack:null,last:s,ruleSeen:new Set(),signals:[],done:false};episodes.set(s.slot,ep);if(s.type===33)emit(ep,s,t,'T33_ENTRY_100');}
function updateEp(ep,s,t){const rel=t-ep.startAt,p=ep.last;if(s.type!==ep.type){finishEp(ep,t,'typeChanged');return;}
 if(ep.exitRel==null&&p.inD20&&!s.inD20&&s.attack===0){ep.exitRel=rel;if(s.type===21)emit(ep,s,t,'T21_EXIT_250');}
 if(s.type===18&&s.inD20&&s.attack===0&&s.timer<=3&&s.state99===0&&s.action2A===4&&s.b2B===0)emit(ep,s,t,'T18_LE3_S0_A4_B0_250');
 if(s.type===24&&ep.exitRel!=null&&s.attack===0&&s.frameEnd===0x0008AB32&&s.next===0x0008A662&&s.value30===0&&s.state99===2&&s.action2A===4&&s.b2B===10)emit(ep,s,t,'T24_AB32_S2_A4_B10_250');
 if(!ep.firstAttack&&p.attack===0&&s.attack!==0){ep.firstAttack={rel,attack:s.attack,target:s.target,target7E:s.target7E,state:mini(s)};for(const q of ep.signals){if(q.resolved)continue;const lead=rel-q.atRel;q.leadToActiveMs=lead;q.activeTarget=s.target;q.targetSameAtActive=q.target7EAtSignal===s.target7E;q.hit=lead>=0&&lead<=q.horizonMs;q.resolved=true;}}
 ep.last=s;if(ep.firstAttack&&rel>=ep.firstAttack.rel+POST_ACTIVE)finishEp(ep,t,'activeConfirmed');else if(rel>=1200)finishEp(ep,t,'horizonComplete');}
await new Promise(resolve=>{const id=setInterval(()=>{const t=Math.round(performance.now()-start);for(let i=0;i<SLOTS;i++){const s=snap(i),p=prev.get(i)||null;if(!s){const ep=episodes.get(i);if(ep)finishEp(ep,t,'slotGone');prev.delete(i);continue;}if(s.d20Exact&&(!p||!p.inD20))startEp(s,t);const ep=episodes.get(i);if(ep)updateEp(ep,s,t);prev.set(i,s);}if(t>=DURATION||(epSeq>=MAX_EPISODES&&episodes.size===0)){clearInterval(id);for(const ep of [...episodes.values()])finishEp(ep,t,'captureEnd');resolve();}},INTERVAL);});
for(const q of signals){if(q.resolved)continue;const ep=done.find(x=>x.id===q.epId);if(!ep)continue;const follow=ep.endRel-q.atRel;if(follow>=q.horizonMs){q.resolved=true;q.hit=false;}}
const ruleStats={};for(const q of signals){const r=(ruleStats[q.rule]??={rule:q.rule,level:q.level,horizonMs:q.horizonMs,signals:0,evaluable:0,hit:0,miss:0,censored:0,targetSameHits:0,targetSameTotal:0,leads:[]});r.signals++;if(!q.resolved){r.censored++;continue;}r.evaluable++;if(q.hit){r.hit++;r.leads.push(q.leadToActiveMs);r.targetSameTotal++;if(q.targetSameAtActive)r.targetSameHits++;}else r.miss++;}
for(const r of Object.values(ruleStats)){r.precision=r.evaluable?+(r.hit/r.evaluable).toFixed(3):null;r.targetSameRate=r.targetSameTotal?+(r.targetSameHits/r.targetSameTotal).toFixed(3):null;r.leads.sort((a,b)=>a-b);}
const rows=done.map(ep=>({id:ep.id,slot:ep.slot,type:ep.type,entryTarget:ep.entryTarget,exitRel:ep.exitRel,outcome:ep.firstAttack?'active':ep.endReason,leadToActiveMs:ep.firstAttack?.rel??null,activeTarget:ep.firstAttack?.target??null,signals:ep.signals.map(q=>({id:q.id,rule:q.rule,level:q.level,horizonMs:q.horizonMs,atRel:q.atRel,targetAtSignal:q.targetAtSignal,resolved:q.resolved,hit:q.hit,leadToActiveMs:q.leadToActiveMs,activeTarget:q.activeTarget,targetSameAtActive:q.targetSameAtActive}))}));
const out={version:'wof-future-danger-shadow-v11',readOnly:true,ramWrites:0,gate,gateStrict:Object.values(gate).every(Boolean),durationRequestedMs:DURATION,intervalMs:INTERVAL,maxEpisodes:MAX_EPISODES,model:{ATTACK_READY:'exact D0=20 remains a type-conditioned early-warning feature',IMMINENT:'first conservative rule set: T33 D0 entry <=100ms candidate and T21 D0 exit <=250ms candidate',ACTIVE:'enemy+0x70 0->nonzero',targetPolicy:'always display/retarget from live enemy+0x7E; targetAtSignal is only for validation, not a frozen target'},rules:RULES,totals:{episodes:done.length,active:done.filter(e=>e.firstAttack).length,horizonComplete:done.filter(e=>e.endReason==='horizonComplete'&&!e.firstAttack).length,signals:signals.length},ruleStats,rows,note:'First read-only Future Danger shadow predictor. T21/T33 are conservative IMMINENT rules; T18/T24 are explicitly candidate-only and must not be treated as production low-false-positive rules until this shadow run confirms them.'};
self.__WOF_FUTURE_DANGER_SHADOW_V11=out;console.log('=== FUTURE DANGER SHADOW V11 JSON ===');console.log(JSON.stringify(out,null,2));return out;
})().catch(e=>{console.error('WOF_FUTURE_DANGER_SHADOW_V11_ERROR',e);throw e;});