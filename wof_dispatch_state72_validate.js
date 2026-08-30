(()=>{
'use strict';
try{self.WOFSTATE72?.stop?.();}catch(_){}
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return (0,eval)(await r.text());};
async function run(){
 if(!self.__WOF_ROM_FOCUS_LEVEL2?.handlers?.length){await load('wof_rom_focus_level2_tables.js');await WOFFOCUSLEVEL2.run();}
 const MOD=_0x515056,M=MOD?.HEAPU8,R=MOD?.HEAPU32?.[0x2e39e4>>>2]>>>0;if(!M||!R)throw new Error('CPS RAM unavailable');
 const L2=self.__WOF_ROM_FOCUS_LEVEL2,POOL=0xFFC0BC,STRIDE=0xE0,N=20,FIELD=0x72,TICK=40,DUR=20000;
 const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0,U16=a=>((B(a)<<8)|B(a+1))>>>0,h=(v,n=2)=>'0x'+(v>>>0).toString(16).toUpperCase().padStart(n,'0');
 const by=new Map();for(const z of L2.handlers||[]){const t=Number(z.type),d=parseInt(z.d0,16);if(Number.isFinite(t)&&Number.isFinite(d))by.set(t+'|'+d,z);}
 let running=true,timer=null,done=null,samples=0,actorSamples=0,indexHits=0,directHits=0,none=0,changes=0;const prev=Array(N).fill(null),vals=new Map(),maps=new Map();
 const add=(m,k)=>m.set(k,(m.get(k)||0)+1);
 function tick(){if(!running)return;for(let i=0;i<N;i++){const b=POOL+i*STRIDE;if(!B(b))continue;const type=U16(b+0x20),v=B(b+FIELD),dIndex=(v*4)>>>0,dDirect=v,a=by.get(type+'|'+dIndex),c=by.get(type+'|'+dDirect);actorSamples++;add(vals,`${type}|${v}`);if(a){indexHits++;add(maps,`${a.target}@${h(dIndex)}|T${type}`,1);}if(c)directHits++;if(!a&&!c)none++;if(prev[i]!=null&&prev[i]!==v)changes++;prev[i]=v;}samples++;}
 function finish(){if(!running)return self.__WOF_STATE72;running=false;clearInterval(timer);clearTimeout(done);const rate=(a,b)=>b?a/b:0;const topVals=[...vals.entries()].sort((a,b)=>b[1]-a[1]).slice(0,20).map(([k,count])=>{const [type,v]=k.split('|').map(Number),z=by.get(type+'|'+(v*4));return{type,stateIndex:v,d0:h(v*4),handler:z?.target||'',count};});const topMaps=[...maps.entries()].sort((a,b)=>b[1]-a[1]).slice(0,20).map(([mapping,count])=>({mapping,count}));console.log('=== STATE72 TOP VALUES ===');console.table(topVals);console.log('=== STATE72 TOP HANDLERS ===');console.table(topMaps);const verdict={field:'+0x72',source:'MOVE.B 114(A0),D0',seconds:20,samples,actorSamples,stateChanges:changes,indexTimes4Hits:indexHits,indexTimes4Rate:+rate(indexHits,actorSamples).toFixed(4),directD0Hits:directHits,directD0Rate:+rate(directHits,actorSamples).toFixed(4),none,locked:indexHits>actorSamples*.9&&indexHits>directHits*1.5};console.log('=== DISPATCH STATE72 VERDICT ===');console.table([verdict]);if(verdict.locked)console.log('🎯 LOCKED: enemy+0x72 is the real stateIndex byte; dispatcher uses stateIndex×4 as D0.');else console.warn('⚠️ +0x72 is not yet a clean >90% stateIndex mapping; inspect top values/handler coverage before locking.');const out={version:'wof-dispatch-state72-validate-v1',verdict,values:topVals,mappings:topMaps};self.__WOF_STATE72=out;return out;}
 timer=setInterval(tick,TICK);tick();done=setTimeout(finish,DUR);self.WOFSTATE72={finish,stop(){if(!running)return;running=false;clearInterval(timer);clearTimeout(done);console.log('⛔ state72 validator stopped');}};console.log('✅ state72 validator started · 20s auto-report');
}
self.WOFSTATE72={run};console.log('✅ WOF dispatch state72 validator loaded');console.log('执行 await WOFSTATE72.run()');
})();