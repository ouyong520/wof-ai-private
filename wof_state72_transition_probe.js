(()=>{
'use strict';
try{self.WOFSTATE72TRANS?.stop?.();}catch(_){}
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return (0,eval)(await r.text());};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function run(){
 if(!self.__WOF_ROM_FOCUS_LEVEL2?.handlers?.length){await load('wof_rom_focus_level2_tables.js');await WOFFOCUSLEVEL2.run();}
 const MOD=_0x515056,M=MOD?.HEAPU8,R=MOD?.HEAPU32?.[0x2e39e4>>>2]>>>0;if(!M||!R)throw new Error('CPS RAM unavailable');
 const L2=self.__WOF_ROM_FOCUS_LEVEL2,POOL=0xFFC0BC,STRIDE=0xE0,N=20,TICK=16,DUR=45000;
 const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0,U16=a=>((B(a)<<8)|B(a+1))>>>0,S16=a=>{const v=U16(a);return v&0x8000?v-0x10000:v;};
 const H=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0'),HW=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
 const by=new Map();for(const z of L2.handlers||[]){const t=Number(z.type),d=parseInt(z.d0,16);if(Number.isFinite(t)&&Number.isFinite(d))by.set(t+'|'+d,z);}
 const PLOW={0xBE1C:'P1',0xBEFC:'P2',0xBFDC:'P3'};const pname=v=>PLOW[v]||'';
 let running=true,timer=null,done=null,samples=0,actorSamples=0;const prev=Array(N).fill(null),events=[],counts=new Map();
 const add=(k,e)=>{let x=counts.get(k);if(!x)counts.set(k,x={type:e.type,oldState:e.oldState,newState:e.newState,oldHandler:e.oldHandler,newHandler:e.newHandler,count:0,ref3AChanges:0,ref6AChanges:0,vecChanges:0,old3A:{},new3A:{},old6A:{},new6A:{}});x.count++;if(e.ref3AChanged)x.ref3AChanges++;if(e.ref6AChanged)x.ref6AChanges++;if(e.vecChanged)x.vecChanges++;if(e.old3AName)x.old3A[e.old3AName]=(x.old3A[e.old3AName]||0)+1;if(e.new3AName)x.new3A[e.new3AName]=(x.new3A[e.new3AName]||0)+1;if(e.old6AName)x.old6A[e.old6AName]=(x.old6A[e.old6AName]||0)+1;if(e.new6AName)x.new6A[e.new6AName]=(x.new6A[e.new6AName]||0)+1;};
 function snap(i){const b=POOL+i*STRIDE;if(!B(b))return null;const type=U16(b+0x20),state=B(b+0x72),r3=U16(b+0x3A),r6=U16(b+0x6A),vx=S16(b+0x3E),vy=S16(b+0x42),h=by.get(type+'|'+(state*4));return{slot:i,base:b,type,state,handler:h?.target||'',r3,r6,r3n:pname(r3),r6n:pname(r6),vx,vy};}
 function tick(){if(!running)return;for(let i=0;i<N;i++){const n=snap(i);if(!n){prev[i]=null;continue;}actorSamples++;const p=prev[i];if(p&&p.type===n.type&&p.state!==n.state){const e={slot:i,type:n.type,oldState:p.state,newState:n.state,oldD0:HW(p.state*4),newD0:HW(n.state*4),oldHandler:p.handler,newHandler:n.handler,old3A:HW(p.r3),new3A:HW(n.r3),old3AName:p.r3n,new3AName:n.r3n,old6A:HW(p.r6),new6A:HW(n.r6),old6AName:p.r6n,new6AName:n.r6n,ref3AChanged:p.r3!==n.r3,ref6AChanged:p.r6!==n.r6,oldVec:`${p.vx},${p.vy}`,newVec:`${n.vx},${n.vy}`,vecChanged:p.vx!==n.vx||p.vy!==n.vy};events.push(e);add(`${n.type}|${p.state}>${n.state}`,e);}prev[i]=n;}samples++;}
 function finish(){if(!running)return self.__WOF_STATE72_TRANSITION;running=false;clearInterval(timer);clearTimeout(done);
   const rows=[...counts.values()].map(x=>({type:x.type,oldState:x.oldState,newState:x.newState,oldD0:HW(x.oldState*4),newD0:HW(x.newState*4),oldHandler:x.oldHandler,newHandler:x.newHandler,count:x.count,ref3AChangeRate:+(x.ref3AChanges/x.count).toFixed(3),ref6AChangeRate:+(x.ref6AChanges/x.count).toFixed(3),vecChangeRate:+(x.vecChanges/x.count).toFixed(3),old3A:Object.entries(x.old3A).sort((a,b)=>b[1]-a[1]).map(z=>z.join(':')).join(' '),new3A:Object.entries(x.new3A).sort((a,b)=>b[1]-a[1]).map(z=>z.join(':')).join(' '),old6A:Object.entries(x.old6A).sort((a,b)=>b[1]-a[1]).map(z=>z.join(':')).join(' '),new6A:Object.entries(x.new6A).sort((a,b)=>b[1]-a[1]).map(z=>z.join(':')).join(' ')})).sort((a,b)=>b.count-a.count||b.vecChangeRate-a.vecChangeRate);
   console.log('=== STATE72 TRANSITIONS ===');console.table(rows.slice(0,40));
   const targetish=[...rows].sort((a,b)=>((b.ref3AChangeRate+b.ref6AChangeRate+b.vecChangeRate)*Math.log2(b.count+1))-((a.ref3AChangeRate+a.ref6AChangeRate+a.vecChangeRate)*Math.log2(a.count+1)))[0]||null;
   const top=rows[0]||null;const verdict={seconds:45,samples,actorSamples,stateChangeEvents:events.length,uniqueTransitions:rows.length,topType:top?.type??'',topOldState:top?.oldState??'',topNewState:top?.newState??'',topOldHandler:top?.oldHandler||'',topNewHandler:top?.newHandler||'',topCount:top?.count??0,targetishType:targetish?.type??'',targetishOldState:targetish?.oldState??'',targetishNewState:targetish?.newState??'',targetishOldHandler:targetish?.oldHandler||'',targetishNewHandler:targetish?.newHandler||'',targetishCount:targetish?.count??0,targetish3AChange:targetish?.ref3AChangeRate??0,targetish6AChange:targetish?.ref6AChangeRate??0,targetishVecChange:targetish?.vecChangeRate??0};
   console.log('=== STATE72 TRANSITION VERDICT ===');console.table([verdict]);
   if(events.length)console.log('🎯 state72 transition 已锁定；下一步只针对 top/targetish transition 的 newState 做全 ROM 精确 writer 验证。');else console.warn('⚠️ 45 秒内没有 state72 变化；需要让敌人发生更多移动/攻击/转向。');
   const out={version:'state72-transition-probe-v1',verdict,transitions:rows,events:events.slice(-200)};self.__WOF_STATE72_TRANSITION=out;return out;
 }
 timer=setInterval(tick,TICK);tick();done=setTimeout(finish,DUR);self.WOFSTATE72TRANS={finish,stop(){if(!running)return;running=false;clearInterval(timer);clearTimeout(done);console.log('⛔ state72 transition probe stopped');}};console.log('✅ WOF state72 transition probe started · 45s auto-report');
}
self.WOFSTATE72TRANS={run};console.log('✅ WOF state72 transition probe loaded');console.log('执行 await WOFSTATE72TRANS.run()');
})();