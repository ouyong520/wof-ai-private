(async()=>{
'use strict';
try{self.WOFSTATELOCK?.stop?.();}catch(_){}
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Math.random());if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return (0,eval)(await r.text());};
if(!self.__WOF_WAYPOINT_STATE)throw new Error('WAYPOINT_STATE result missing; keep the room where the 45s probe finished');
if(!self.__WOF_ROM_FOCUS_LEVEL2?.handlers?.length){await load('wof_rom_focus_level2_tables.js');await WOFFOCUSLEVEL2.run();}
if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing');
const W=self.__WOF_WAYPOINT_STATE,L2=self.__WOF_ROM_FOCUS_LEVEL2;
const all=[...(W.byte||[]),...(W.word||[])].sort((a,b)=>b.score-a.score),top=all[0];
if(!top)throw new Error('no locked state candidate');
const FIELD=parseInt(top.offset,16),KIND=top.kind;
const MOD=_0x515056,C=self.__WOF_ROM_LOC_CACHE,M=MOD.HEAPU8,ROMBASE=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-ROMBASE),DELTA=C.offlineDelta|0;
const rr8=o=>M[ROMBASE+(SW?(o^1):o)]>>>0,rr16=o=>((rr8(o)<<8)|rr8(o+1))>>>0,s16=v=>v&0x8000?v-0x10000:v;
const hx=(v,n=6)=>'0x'+(v>>>0).toString(16).toUpperCase().padStart(n,'0'),off=a=>hx((a-DELTA)>>>0),hw=v=>'0x'+(v&0xffff).toString(16).toUpperCase().padStart(4,'0');
function eaWords(m,r,size){if(m<=4)return 0;if(m===5||m===6)return 1;if(m===7){if(r===0||r===2||r===3)return 1;if(r===1)return 2;if(r===4)return size==='L'?2:1;}return 0;}
function moveRead(p){const w=rr16(p),g=w>>>12;if(g!==1&&g!==2&&g!==3)return null;const size=g===1?'B':g===2?'L':'W',sm=(w>>3)&7,sr=w&7,dm=(w>>6)&7,dr=(w>>9)&7;if(sm!==5)return null;const disp=s16(rr16(p+2));if(disp!==FIELD)return null;const sw=1,dstExt=p+2+sw*2;return{at:p,size,srcBase:'A'+sr,dstMode:dm,dstReg:dr,dst:dm===0?'D'+dr:dm===1?'A'+dr:'EA',len:2+(sw+eaWords(dm,dr,size))*2,op:w};}
function rawWindow(center,b=0x50,a=0x18){const out=[];for(let p=Math.max(0,center-b)&~1;p<=Math.min(MAX-2,center+a);p+=2){const r=moveRead(p);out.push({at:hx(p),offline:off(p),word:hw(rr16(p)),mark:p===center?'<<< L2':r?'<<< FIELD READ':''});}return out;}
const dispatch=[0x0025C2,0x0025D4],near=[];
for(const site of dispatch){for(let p=Math.max(0,site-0x80)&~1;p<site;p+=2){const r=moveRead(p);if(r)near.push({...r,site,distance:site-p});}}
console.log('🔒 WOF state→dispatcher lock');
console.log(`LOCKED FIELD: ${top.offset} ${KIND} | handlerMapRate=${top.handlerMapRate} | lift=${top.lift} | semantics=${W.verdict.fieldSemantics}`);
console.log('=== LOCKED FIELD READS NEAR L2 DISPATCH ===');
console.table(near.map(x=>({dispatch:hx(x.site),readAt:hx(x.at),offline:off(x.at),distance:x.distance,size:x.size,srcBase:x.srcBase,dst:x.dst,op:hw(x.op)})));
for(const site of dispatch){console.log('=== DISPATCH WINDOW '+hx(site)+' ===');console.table(rawWindow(site));}

// Dynamic semantic classifier: does field contain stateIndex, or already-scaled D0?
const RAM=MOD?.HEAPU32?.[0x2e39e4>>>2]>>>0;if(!RAM)throw new Error('CPS RAM unavailable');
const POOL=0xFFC0BC,STRIDE=0xE0,N=20,TICK=40,DURATION=22000;
const B=a=>M[RAM+((((a-0xFF0000)&0xffff)^1))]>>>0,U16=a=>((B(a)<<8)|B(a+1))>>>0;
const readField=b=>KIND==='byte'?B(b+FIELD):U16(b+FIELD);
const map=new Map();for(const z of L2.handlers||[]){const t=Number(z.type),d=parseInt(z.d0,16);if(Number.isFinite(t)&&Number.isFinite(d))map.set(t+'|'+d,z);}
const valCounts=new Map(),mappingCounts=new Map();let running=true,timer=null,done=null,samples=0,actors=0,directOnly=0,indexOnly=0,both=0,none=0,directHit=0,indexHit=0;
function add(m,k){m.set(k,(m.get(k)||0)+1);}
function tick(){if(!running)return;for(let i=0;i<N;i++){const b=POOL+i*STRIDE;if(!B(b))continue;const type=U16(b+0x20),v=readField(b),dDirect=(v<=0xFC&&(v&3)===0)?v:null,dIndex=v<=0x3F?v*4:null,a=dDirect==null?null:map.get(type+'|'+dDirect),c=dIndex==null?null:map.get(type+'|'+dIndex);actors++;add(valCounts,hx(v,4));if(a)directHit++;if(c)indexHit++;if(a&&c)both++;else if(a)directOnly++;else if(c)indexOnly++;else none++;const z=a||c;if(z)add(mappingCounts,`${z.target}@${hx(parseInt(z.d0,16),2)}|T${type}`);}samples++;}
function finish(){if(!running)return self.__WOF_STATE_DISPATCH_LOCK;running=false;if(timer)clearInterval(timer);if(done)clearTimeout(done);const nonAmb=Math.max(1,directOnly+indexOnly),sem=directOnly>indexOnly*1.5?'field-is-D0':indexOnly>directOnly*1.5?'field-is-stateIndex':'ambiguous-zero-heavy';const vals=[...valCounts.entries()].sort((a,b)=>b[1]-a[1]).slice(0,20).map(([value,count])=>({value,count,directD0:(parseInt(value,16)<=0xFC&&(parseInt(value,16)&3)===0)?value:'',indexD0:parseInt(value,16)<=0x3F?hx(parseInt(value,16)*4,2):''}));const maps=[...mappingCounts.entries()].sort((a,b)=>b[1]-a[1]).slice(0,20).map(([mapping,count])=>({mapping,count}));
 console.log('=== LOCKED FIELD RAW VALUES ===');console.table(vals);console.log('=== LOCKED FIELD → HANDLER OBSERVATIONS ===');console.table(maps);
 const verdict={field:top.offset,kind:KIND,staticReadsNearDispatch:near.length,staticReadDsts:[...new Set(near.map(x=>x.dst))].join(','),seconds:22,samples,actorSamples:actors,directD0Hits:directHit,stateIndexHits:indexHit,directOnly,indexOnly,both,none,nonAmbiguous:nonAmb,fieldEncoding:sem,topMappings:maps.slice(0,5).map(x=>x.mapping+':'+x.count).join(' ')};
 console.log('=== STATE DISPATCH LOCK VERDICT ===');console.table([verdict]);
 if(sem==='field-is-D0')console.log('🎯 锁定：该字段直接保存已乘4的 D0/state offset。下一步全 ROM 反查谁写这个 field。');else if(sem==='field-is-stateIndex')console.log('🎯 锁定：该字段保存 stateIndex，dispatcher 再 ×4 生成 D0。下一步精确反查 stateIndex 写入点。');else console.warn('⚠️ 样本被 state=0 主导，编码仍歧义；但字段→handler 映射已锁定。下一步针对非0 state 做短采样。');
 const out={version:'wof-state-dispatch-lock-v1',top,near,verdict,values:vals,mappings:maps};self.__WOF_STATE_DISPATCH_LOCK=out;return out;}
timer=setInterval(tick,TICK);tick();done=setTimeout(finish,DURATION);self.WOFSTATELOCK={version:'wof-state-dispatch-lock-v1',finish,stop(){if(!running)return;running=false;if(timer)clearInterval(timer);if(done)clearTimeout(done);console.log('⛔ state lock stopped');},status(){return{running,samples,actors,directOnly,indexOnly,both,none}}};
console.log('✅ state-dispatch lock started · 22s auto-report');
})();