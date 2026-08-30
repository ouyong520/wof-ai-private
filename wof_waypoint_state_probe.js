(async()=>{
'use strict';
try{self.WOFWAYSTATE?.stop?.();}catch(_){}
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Math.random());if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return (0,eval)(await r.text());};
if(!self.__WOF_ROM_FOCUS_LEVEL2?.handlers?.length){await load('wof_rom_focus_level2_tables.js');await WOFFOCUSLEVEL2.run();}
const L2=self.__WOF_ROM_FOCUS_LEVEL2;
const MOD=_0x515056,M=MOD?.HEAPU8,R=MOD?.HEAPU32?.[0x2e39e4>>>2]>>>0;
if(!M||!R)throw new Error('CPS RAM unavailable');
const POOL=0xFFC0BC,STRIDE=0xE0,N=20,TICK=40,DURATION=45000;
const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0;
const U16=a=>((B(a)<<8)|B(a+1))>>>0;
const S16=a=>{const v=U16(a);return v&0x8000?v-0x10000:v;};
const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
const S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v;};
const F=v=>v/65536,hx=(v,n=4)=>'0x'+(v>>>0).toString(16).toUpperCase().padStart(n,'0');
const actor=i=>{const base=POOL+i*STRIDE;if(!B(base))return null;return{slot:i,base,type:U16(base+0x20),x:F(S32(base+4)),y:F(S32(base+8)),fx:S16(base+0x3E),fy:S16(base+0x42)};};
const snap=base=>{const a=new Uint8Array(STRIDE);for(let i=0;i<STRIDE;i++)a[i]=B(base+i);return a;};
const rdW=(a,o)=>((a[o]<<8)|a[o+1])>>>0;
const excluded=o=>(o<0x10)||(o===0x20||o===0x21)||(o>=0x3E&&o<=0x43);
const byteStat=Array.from({length:STRIDE},()=>({n:0,ch:0,ev:0,evCh:0,map:0,targets:new Map()}));
const wordStat=Array.from({length:STRIDE-1},()=>({n:0,ch:0,ev:0,evCh:0,map:0,targets:new Map()}));
const byTypeD0=new Map();
for(const z of L2.handlers||[]){const type=Number(z.type),d0=parseInt(z.d0,16),target=z.target;if(Number.isFinite(type)&&Number.isFinite(d0))byTypeD0.set(type+'|'+d0,{target,stateIndex:z.stateIndex});}
const H=Array.from({length:N},()=>({prev:null,hist:[],lastEvent:0,pending:[]}));
let running=true,timer=null,finishTimer=null,samples=0,events=0,evaluated=0,absN=0,absSum=0,vecN=0,vecSum=0,started=Date.now();
const cos=(ax,ay,bx,by)=>{const a=Math.hypot(ax,ay),b=Math.hypot(bx,by);return a>.05&&b>.05?(ax*bx+ay*by)/(a*b):null;};
function mapCandidates(type,kind,val){const out=[];if(kind==='byte'){const d=val*4;if(d<=0xFC)out.push(d);}else{if(val<=0x3F)out.push(val*4);if(val<=0xFC&&(val&3)===0)out.push(val);}return [...new Set(out)].map(d=>({d0:d,hit:byTypeD0.get(type+'|'+d)})).filter(x=>x.hit);}
function addMap(r,hits){if(!hits.length)return;r.map++;for(const x of hits){const k=x.hit.target+'@'+hx(x.d0,2);r.targets.set(k,(r.targets.get(k)||0)+1);}}
function baseline(prev,cur){for(let o=0x10;o<STRIDE;o++){if(excluded(o))continue;const r=byteStat[o];r.n++;if(prev[o]!==cur[o])r.ch++;}for(let o=0x10;o<STRIDE-1;o+=2){if(excluded(o)||excluded(o+1))continue;const r=wordStat[o];r.n++;if(rdW(prev,o)!==rdW(cur,o))r.ch++;}}
function evalEvent(e,cur,type){evaluated++;for(let o=0x10;o<STRIDE;o++){if(excluded(o))continue;const r=byteStat[o],v=cur[o];r.ev++;if(e.pre[o]!==v)r.evCh++;addMap(r,mapCandidates(type,'byte',v));}for(let o=0x10;o<STRIDE-1;o+=2){if(excluded(o)||excluded(o+1))continue;const r=wordStat[o],v=rdW(cur,o);r.ev++;if(rdW(e.pre,o)!==v)r.evCh++;addMap(r,mapCandidates(type,'word',v));}}
function tick(){if(!running)return;const now=Date.now();for(let i=0;i<N;i++){
 const o=actor(i),h=H[i];if(!o){H[i]={prev:null,hist:[],lastEvent:0,pending:[]};continue;}const s=snap(o.base);
 if(h.prev){baseline(h.prev.s,s);const mx=o.x-h.prev.x,my=o.y-h.prev.y;
   const ca=cos(mx,my,h.prev.fx-h.prev.x,h.prev.fy-h.prev.y);if(ca!=null){absN++;absSum+=ca;}
   const cv=cos(mx,my,h.prev.fx,h.prev.fy);if(cv!=null){vecN++;vecSum+=cv;}
   const rawJump=Math.hypot(o.fx-h.prev.fx,o.fy-h.prev.fy);
   const va={x:h.prev.fx-h.prev.x,y:h.prev.fy-h.prev.y},vb={x:o.fx-o.x,y:o.fy-o.y};
   const dir=cos(va.x,va.y,vb.x,vb.y),turn=dir==null?0:1-dir;
   if((rawJump>=4||turn>.08)&&now-h.lastEvent>=160){const pre=(h.hist[0]?.s||h.prev.s).slice();h.pending.push({due:now+160,pre,type:o.type});h.lastEvent=now;events++;}
 }
 while(h.pending.length&&h.pending[0].due<=now){const e=h.pending.shift();evalEvent(e,s,o.type);}
 h.hist.push({s:s.slice()});if(h.hist.length>4)h.hist.shift();h.prev={s,x:o.x,y:o.y,fx:o.fx,fy:o.fy};
 }samples++;}
const rate=(a,b)=>b?a/b:0;
function rows(stats,kind,step){const out=[];for(let o=0;o<stats.length;o+=step){if(o<0x10||excluded(o))continue;const r=stats[o];if(r.ev<8)continue;const er=rate(r.evCh,r.ev),br=rate(r.ch,r.n),lift=er-br,mr=rate(r.map,r.ev);if(lift<.05&&mr<.5)continue;const tops=[...r.targets.entries()].sort((a,b)=>b[1]-a[1]).slice(0,4);const score=lift*3+mr*2+Math.min(1,er)*.5-Math.min(.8,br)*.4;out.push({offset:hx(o),kind,eventN:r.ev,eventChangeRate:+er.toFixed(3),baselineChangeRate:+br.toFixed(3),lift:+lift.toFixed(3),handlerMapRate:+mr.toFixed(3),topMappings:tops.map(x=>x[0]+':'+x[1]).join(' '),score:+score.toFixed(3)});}return out.sort((a,b)=>b.score-a.score);}
function finish(){if(!running)return self.__WOF_WAYPOINT_STATE;running=false;if(timer)clearInterval(timer);if(finishTimer)clearTimeout(finishTimer);const rb=rows(byteStat,'byte',1),rw=rows(wordStat,'word',2),all=[...rb,...rw].sort((a,b)=>b.score-a.score);console.log('=== WAYPOINT/STATE BYTE CANDIDATES ===');console.table(rb.slice(0,30));console.log('=== WAYPOINT/STATE WORD CANDIDATES ===');console.table(rw.slice(0,30));const top=all[0]||null,absAlign=rate(absSum,absN),vecAlign=rate(vecSum,vecN),semantics=absAlign>vecAlign+.08?'absolute-waypoint':vecAlign>absAlign+.08?'movement-vector':'ambiguous';const verdict={seconds:+((Date.now()-started)/1000).toFixed(1),samples,waypointChangeEvents:events,evaluatedEvents:evaluated,absWaypointAlign:+absAlign.toFixed(3),vectorAlign:+vecAlign.toFixed(3),fieldSemantics:semantics,candidates:all.length,topKind:top?.kind||'',topOffset:top?.offset||'',topScore:top?.score??'',topEventChangeRate:top?.eventChangeRate??'',topBaselineRate:top?.baselineChangeRate??'',topLift:top?.lift??'',topHandlerMapRate:top?.handlerMapRate??'',topMappings:top?.topMappings||''};console.log('=== WAYPOINT → STATE VERDICT ===');console.table([verdict]);if(top&&top.handlerMapRate>=.6&&top.lift>.15)console.log('🎯 找到 waypoint/方向切换时同步变化、且能映射到 type 二级 handler 的 state/action 字段；下一步固定 topOffset 和 topMappings 反查对应 handler。');else if(top)console.warn('⚠️ 有同步字段但 state→handler 映射还不够强；下一步对 top 3 offset 做单敌人时序验证。');else console.warn('⚠️ waypoint/方向变化没有暴露稳定 state 字段；下一步改抓 handler dispatch 的 D0 值本身。');const out={version:'wof-waypoint-state-v1',verdict,byte:rb,word:rw};self.__WOF_WAYPOINT_STATE=out;return out;}
timer=setInterval(tick,TICK);tick();finishTimer=setTimeout(finish,DURATION);self.WOFWAYSTATE={version:'wof-waypoint-state-v1',finish,stop(){if(!running)return;running=false;if(timer)clearInterval(timer);if(finishTimer)clearTimeout(finishTimer);console.log('⛔ waypoint/state probe stopped');},status(){return{running,seconds:+((Date.now()-started)/1000).toFixed(1),samples,events,evaluated}}};console.log('✅ WOF waypoint→state dynamic probe started · 45s auto-report');console.log('期间让敌人多走动、转向、切换追击/攻击行为；45 秒后自动输出 WAYPOINT → STATE VERDICT');
})();