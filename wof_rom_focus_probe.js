(()=>{
'use strict';
const OLD=self.WOFFOCUSROM;
let oldLoc=self.__WOF_ROM_LOC_CACHE||null;
try{oldLoc=oldLoc||OLD?.diagnose?.()?.locator||null;}catch(_){}
try{OLD?.stop?.();}catch(_){}
const MOD=_0x515056;if(!MOD?.HEAPU8)throw new Error('HEAPU8 unavailable');
const ROM_LIMIT=0x100000,NT=47,DEFAULT_DISPATCH=0x25DC;
const VEC=[0x00,0xFF,0x62,0xEE,0x00,0x00,0x75,0x4A],VEC_SWAP=[0xFF,0x00,0xEE,0x62,0x00,0x00,0x4A,0x75];
const EXPECT=[0x06F4E4,0x07494C,0x071ADA,0x077B8E,0x07C6D2];
const PLAYER={P1:0x00FFBE1C,P2:0x00FFBEFC,P3:0x00FFBFDC};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let stopped=false,LOC=null,base=-1,SWAP=false,MAX=0,DISPATCH=null,OFFLINE_DELTA=0;
const heap=()=>MOD.HEAPU8;
const match=(M,p,a)=>{if(p<0||p+a.length>M.length)return false;for(let i=0;i<a.length;i++)if(M[p+i]!==a[i])return false;return true;};
const m8=(M,b,sw,o)=>M[b+(sw?(o^1):o)]>>>0;
const m32=(M,b,sw,o)=>(m8(M,b,sw,o)*0x1000000+m8(M,b,sw,o+1)*0x10000+m8(M,b,sw,o+2)*0x100+m8(M,b,sw,o+3))>>>0;
const h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0');
const hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
function vecOK(M,b,sw){return b>=0&&b+8<M.length&&m32(M,b,sw,0)===0x00FF62EE&&m32(M,b,sw,4)===0x0000754A;}
function r8(o){if(!LOC)throw new Error('先执行 await WOFFOCUSROM.locate()');return m8(heap(),base,SWAP,o);}
const r16=o=>((r8(o)<<8)|r8(o+1))>>>0;
const r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
const sx8=v=>v&0x80?v-0x100:v,sx16=v=>v&0x8000?v-0x10000:v;
function calibrateDispatch(){
  let best=null;
  for(let o=0x2400;o<=0x2700;o+=2){let n=0;for(let i=0;i<EXPECT.length;i++){if(r32(o+i*4)===EXPECT[i])n++;else break;}if(n>=3&&(!best||n>best.n))best={o,n};}
  if(best){OFFLINE_DELTA=0;console.log('🎯 dispatch exact',h(best.o),'matched '+best.n+'/'+EXPECT.length);return best.o;}
  const o=DEFAULT_DISPATCH,vals=EXPECT.map((_,i)=>r32(o+i*4)),d=(vals[0]-EXPECT[0])|0,same=vals.every((v,i)=>((v-EXPECT[i])|0)===d);
  if(same&&Math.abs(d)<=0x1000){OFFLINE_DELTA=d;console.log('🎯 dispatch accepted by uniform live-ROM delta',h(o),'delta='+(d>=0?'+':'-')+'0x'+Math.abs(d).toString(16).toUpperCase(),'matched '+EXPECT.length+'/'+EXPECT.length);return o;}
  console.warn('⚠️ dispatch validation failed',{at25DC:vals.map(h),uniformDelta:same?h(d):null});return null;
}
function setLoc(b,sw,label){base=b;SWAP=sw;MAX=Math.min(ROM_LIMIT,heap().length-base);LOC={base,swap16:SWAP,label,sp:0x00FF62EE,pc:0x0000754A};DISPATCH=calibrateDispatch();if(DISPATCH==null)throw new Error('ROM found but type dispatch validation failed');LOC.dispatch=DISPATCH;LOC.offlineDelta=OFFLINE_DELTA;self.__WOF_ROM_LOC_CACHE={...LOC};console.log('✅ ROM ready','base=0x'+base.toString(16).toUpperCase(),'layout='+(SWAP?'swap16':'direct'),'dispatch='+h(DISPATCH),'offlineDelta='+(OFFLINE_DELTA>=0?'+':'-')+'0x'+Math.abs(OFFLINE_DELTA).toString(16).toUpperCase());return LOC;}
async function locate(opts={}){
  if(LOC)return LOC;stopped=false;const M=heap();
  if(oldLoc&&Number.isInteger(oldLoc.base)&&vecOK(M,oldLoc.base,!!oldLoc.swap16)){console.log('♻️ reuse cached ROM location');return setLoc(oldLoc.base,!!oldLoc.swap16,'reused-cache');}
  const CHUNK=Math.max(0x10000,opts.chunkBytes||0x40000),PAUSE=Math.max(0,opts.pauseMs??4),n=M.length;console.log('🔎 ROM安全扫描开始 · '+Math.round(n/1048576)+'MB');
  for(let start=0;start<n;start+=CHUNK){if(stopped)throw new Error('ROM scan stopped');const end=Math.min(n,start+CHUNK+8);for(let p=start;p<end-8;p++){const b=M[p];if(b===VEC[0]&&match(M,p,VEC)&&vecOK(M,p,false))return setLoc(p,false,'vectors-direct');if(b===VEC_SWAP[0]&&match(M,p,VEC_SWAP)&&vecOK(M,p,true))return setLoc(p,true,'vectors-swap16');}if(((start/CHUNK)|0)%16===15)console.log('… ROM扫描 '+Math.round(Math.min(n,start+CHUNK)/n*100)+'%');await sleep(PAUSE);}
  console.error('❌ WOF ROM not found');return null;
}
function model(){if(DISPATCH==null)throw new Error('dispatch not calibrated');const TYPES=Array.from({length:NT},(_,type)=>({type,entry:r32(DISPATCH+type*4)}));const mp=new Map();for(const x of TYPES){if(x.entry>=MAX)continue;let u=mp.get(x.entry);if(!u)mp.set(x.entry,u={entry:x.entry,types:[]});u.types.push(x.type);}return{TYPES,unique:[...mp.values()]};}
function hex(o,n=32){let s='';for(let i=0;i<Math.max(0,Math.min(n,MAX-o));i++)s+=(i?' ':'')+r8(o+i).toString(16).toUpperCase().padStart(2,'0');return s;}
function callsIn(start,span=0x700){const end=Math.min(MAX,start+span),out=[];for(let p=start&~1;p+2<end;p+=2){const w=r16(p);if(w===0x4EB9||w===0x4EF9){const t=r32(p+2);if(t<MAX)out.push({at:p,target:t,kind:w===0x4EB9?'JSR.L':'JMP.L'});}else if((w&0xFF00)===0x6100){const d8=w&255;let t;if(d8===0&&p+4<=end)t=p+2+sx16(r16(p+2));else t=p+2+sx8(d8);if(t>=0&&t<MAX)out.push({at:p,target:t,kind:'BSR'});}}return out;}
async function playerRefs(){const {unique}=model(),longRefs=[],wordRefs=[],lows={P1:PLAYER.P1&0xffff,P2:PLAYER.P2&0xffff,P3:PLAYER.P3&0xffff};const nearest=o=>{let q=null;for(const u of unique){const d=Math.abs(o-u.entry);if(!q||d<q.d)q={types:u.types,d};}return q;};const hasE0=o=>{for(let p=Math.max(0,o-48)&~1;p+1<Math.min(MAX,o+48);p+=2)if(r16(p)===0x00E0)return true;return false;};
  for(let start=0;start<MAX;start+=0x8000){const end=Math.min(MAX,start+0x8000);for(let o=start;o+4<=end;o+=2){const v=r32(o);for(const [name,a] of Object.entries(PLAYER))if(v===a){const q=nearest(o);longRefs.push({player:name,off:h(o),offlineOff:h((o-OFFLINE_DELTA)>>>0),prev:hw(o>=2?r16(o-2):0),hasE0:hasE0(o),nearTypes:q?.types?.join('/')||'',distance:q?.d??null,ctx:hex(Math.max(0,o-8),24)});}const w=r16(o);for(const [name,a] of Object.entries(lows))if(w===a){const q=nearest(o);wordRefs.push({player:name,off:h(o),offlineOff:h((o-OFFLINE_DELTA)>>>0),prev:hw(o>=2?r16(o-2):0),hasE0:hasE0(o),nearTypes:q?.types?.join('/')||'',distance:q?.d??null,ctx:hex(Math.max(0,o-8),20)});}}await sleep(0);}return{longRefs,wordRefs};}
function commonHelpers(refs){const {unique}=model(),m=new Map();for(const u of unique){const seen=new Set();for(const c of callsIn(u.entry)){if(seen.has(c.target))continue;seen.add(c.target);let z=m.get(c.target);if(!z)m.set(c.target,z={target:c.target,callers:new Set(),kinds:new Set()});z.callers.add(u.entry);z.kinds.add(c.kind);}}
  const rows=[];for(const z of m.values()){let l=0,w=0,e0=0;for(const x of refs.longRefs)if(Math.abs(parseInt(x.off,16)-z.target)<=0x300)l++;for(const x of refs.wordRefs)if(Math.abs(parseInt(x.off,16)-z.target)<=0x300)w++;for(let p=Math.max(0,z.target-0x100)&~1;p+1<Math.min(MAX,z.target+0x300);p+=2)if(r16(p)===0x00E0)e0++;const callerTypes=[];for(const e of z.callers){const u=unique.find(x=>x.entry===e);if(u)callerTypes.push(...u.types);}const score=z.callers.size*2+l*12+w*2+Math.min(4,e0);if(z.callers.size>=2||l||w>=2)rows.push({target:h(z.target),offlineTarget:h((z.target-OFFLINE_DELTA)>>>0),callerGroups:z.callers.size,types:[...new Set(callerTypes)].sort((a,b)=>a-b).join(','),kinds:[...z.kinds].join('/'),longHits:l,wordHits:w,strideHits:e0,score,ctx:hex(z.target,32)});}rows.sort((a,b)=>b.score-a.score||b.callerGroups-a.callerGroups);return rows;}
async function result(){if(!LOC)throw new Error('先执行 await WOFFOCUSROM.locate()');const {TYPES}=model();console.log('=== live type table ===');console.table(TYPES.map(x=>({type:x.type,liveEntry:h(x.entry),offlineEntry:h((x.entry-OFFLINE_DELTA)>>>0),valid:x.entry<MAX,sharedWith:TYPES.filter(y=>y.entry===x.entry&&y.type!==x.type).map(y=>y.type).join(',')})));console.log('🔎 分片扫描玩家引用…');const refs=await playerRefs();console.log('=== direct 32-bit P1/P2/P3 refs ===');console.table(refs.longRefs);console.log('=== low-16 P1/P2/P3 refs ===');console.table(refs.wordRefs.slice(0,120));const helpers=commonHelpers(refs);console.log('=== common helper candidates ===');console.table(helpers.slice(0,50));const out={version:'rom-focus-probe-v5-live-delta',vectors:{sp:h(r32(0)),pc:h(r32(4)),romBaseHeap:'0x'+base.toString(16).toUpperCase(),dispatchTable:h(DISPATCH),swap16:SWAP,offlineDelta:OFFLINE_DELTA},types:TYPES,longRefs:refs.longRefs,wordRefs:refs.wordRefs,helpers:helpers.slice(0,100)};self.__WOF_ROM_FOCUS_LAST=out;return out;}
function routine(type,span=0x700){const x=model().TYPES[type];const calls=callsIn(x.entry,span).map(c=>({at:h(c.at),offlineAt:h((c.at-OFFLINE_DELTA)>>>0),target:h(c.target),offlineTarget:h((c.target-OFFLINE_DELTA)>>>0),kind:c.kind}));console.table(calls);return{type,liveEntry:h(x.entry),offlineEntry:h((x.entry-OFFLINE_DELTA)>>>0),calls,hex:hex(x.entry,96)};}
function dump(off,n=128){off=typeof off==='string'?parseInt(off,16):off;const z={off:h(off),hex:hex(off,n)};console.log(z.off,z.hex);return z;}
self.WOFFOCUSROM={version:'rom-focus-probe-v5-live-delta',get located(){return!!LOC;},locate,result,routine,dump,diagnose(){return{heapBytes:heap().length,located:!!LOC,locator:LOC,dispatch:DISPATCH==null?null:h(DISPATCH),offlineDelta:OFFLINE_DELTA};},stop(){stopped=true;}};
console.log('✅ WOF ROM focus probe v5 loaded · 接受 live ROM 固定地址差');
console.log('执行 await WOFFOCUSROM.locate()');
})();