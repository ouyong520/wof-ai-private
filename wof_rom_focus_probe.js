(()=>{
'use strict';
try{self.WOFFOCUSROM?.stop?.();}catch(_){}
const MOD=_0x515056;if(!MOD?.HEAPU8)throw new Error('HEAPU8 unavailable');
const TBL=0x25DC,NT=47,ROM_LIMIT=0x100000;
const VEC=[0x00,0xFF,0x62,0xEE,0x00,0x00,0x75,0x4A];
const VEC_SWAP=[0xFF,0x00,0xEE,0x62,0x00,0x00,0x4A,0x75];
const DISP=[0x00,0x06,0xF4,0xE4,0x00,0x07,0x49,0x4C,0x00,0x07,0x1A,0xDA];
const DISP_SWAP=[0x06,0x00,0xE4,0xF4,0x07,0x00,0x4C,0x49,0x07,0x00,0xDA,0x1A];
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let stopped=false,LOC=null,base=-1,SWAP=false,MAX=0;
const heap=()=>MOD.HEAPU8;
const matchAt=(M,p,s)=>{if(p<0||p+s.length>M.length)return false;for(let i=0;i<s.length;i++)if(M[p+i]!==s[i])return false;return true;};
const mem8=(M,b,sw,o)=>M[b+(sw?(o^1):o)]>>>0;
const mem32=(M,b,sw,o)=>(mem8(M,b,sw,o)*0x1000000+mem8(M,b,sw,o+1)*0x10000+mem8(M,b,sw,o+2)*0x100+mem8(M,b,sw,o+3))>>>0;
function validate(M,b,sw,label){if(b<0||b+TBL+NT*4>=M.length)return null;let valid=0,even=0,inCode=0;for(let i=0;i<NT;i++){const e=mem32(M,b,sw,TBL+i*4);if((e&1)===0)even++;if(e>=0x1000&&e<ROM_LIMIT){valid++;if(e>=0x60000)inCode++;}}const sp=mem32(M,b,sw,0),pc=mem32(M,b,sw,4);const vec=sp===0x00FF62EE&&pc===0x0000754A;const score=valid*3+inCode+even*.2+(vec?100:0);return{base:b,swap16:sw,validDispatch:valid,codeDispatch:inCode,evenDispatch:even,sp,pc,vec,score,label};}
async function locate(opts={}){
  if(LOC)return LOC;stopped=false;
  const CHUNK=Math.max(0x10000,opts.chunkBytes||0x40000),PAUSE=Math.max(0,opts.pauseMs??4);
  let M=heap(),n=M.length,checked=0,t0=performance.now(),best=null;
  console.log('🔎 ROM安全扫描开始 · heap='+Math.round(n/1048576)+'MB · chunk='+Math.round(CHUNK/1024)+'KB');
  outer:for(let start=0;start<n;start+=CHUNK){
    if(stopped)throw new Error('ROM scan stopped');
    M=heap();n=M.length;const end=Math.min(n,start+CHUNK+16);
    for(let p=start;p<end-12;p++){
      const b0=M[p];let v=null;
      if(b0===VEC[0]&&matchAt(M,p,VEC))v=validate(M,p,false,'vectors-direct');
      if(!v&&b0===VEC_SWAP[0]&&matchAt(M,p,VEC_SWAP))v=validate(M,p,true,'vectors-swap16');
      if(!v&&b0===DISP[0]&&matchAt(M,p,DISP))v=validate(M,p-TBL,false,'dispatch-direct');
      if(!v&&b0===DISP_SWAP[0]&&matchAt(M,p,DISP_SWAP))v=validate(M,p-TBL,true,'dispatch-swap16');
      if(v){if(!best||v.score>best.score)best=v;if(v.validDispatch>=40&&v.vec){best=v;break outer;}if(v.validDispatch===47&&v.codeDispatch>=35){best=v;break outer;}}
    }
    checked=Math.min(n,start+CHUNK);
    if(((start/CHUNK)|0)%16===15)console.log('… ROM扫描 '+Math.round(checked/n*100)+'%');
    await sleep(PAUSE);
  }
  if(!best||best.validDispatch<40){console.error('❌ 没找到通过验证的 WOF ROM',{heapBytes:heap().length,best});return null;}
  LOC=best;base=best.base;SWAP=best.swap16;MAX=Math.min(ROM_LIMIT,heap().length-base);
  console.log('✅ ROM located','base=0x'+base.toString(16).toUpperCase(),'layout='+(SWAP?'swap16':'direct'),'via='+best.label,'valid='+best.validDispatch+'/47','time='+Math.round(performance.now()-t0)+'ms');
  return LOC;
}
function need(){if(!LOC)throw new Error('先执行 await WOFFOCUSROM.locate()');}
const r8=o=>{need();return mem8(heap(),base,SWAP,o);};
const r16=o=>((r8(o)<<8)|r8(o+1))>>>0;
const r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
const sx8=v=>v&0x80?v-0x100:v,sx16=v=>v&0x8000?v-0x10000:v;
const h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0');
const hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
const hex=(o,n=32)=>{need();let s='';const lim=Math.max(0,Math.min(n,MAX-o));for(let i=0;i<lim;i++)s+=(i?' ':'')+r8(o+i).toString(16).toUpperCase().padStart(2,'0');return s;};
function model(){need();const TYPES=Array.from({length:NT},(_,type)=>({type,entry:r32(TBL+type*4)}));const map=new Map();for(const x of TYPES){if(x.entry>=MAX)continue;let u=map.get(x.entry);if(!u){u={entry:x.entry,types:[]};map.set(x.entry,u);}u.types.push(x.type);}return{TYPES,unique:[...map.values()]};}
const PLAYER={P1:0x00FFBE1C,P2:0x00FFBEFC,P3:0x00FFBFDC};
function callsIn(start,span=0x700){const end=Math.min(MAX,start+span),out=[];for(let p=start&~1;p+2<end;p+=2){const w=r16(p);if(w===0x4EB9||w===0x4EF9){const t=r32(p+2);if(t<MAX)out.push({at:p,target:t,kind:w===0x4EB9?'JSR.L':'JMP.L'});}else if((w&0xFF00)===0x6100){const d8=w&255;let t;if(d8===0&&p+4<=end)t=p+2+sx16(r16(p+2));else t=p+2+sx8(d8);if(t>=0&&t<MAX)out.push({at:p,target:t,kind:'BSR'});}}return out;}
async function playerRefs(){need();const {unique}=model(),longRefs=[],wordRefs=[];const lows={P1:PLAYER.P1&0xffff,P2:PLAYER.P2&0xffff,P3:PLAYER.P3&0xffff};
  const nearest=off=>{let q=null;for(const u of unique){const d=Math.abs(off-u.entry);if(!q||d<q.d)q={types:u.types,d};}return q;};
  const e0=off=>{for(let p=Math.max(0,off-48)&~1;p+1<Math.min(MAX,off+48);p+=2)if(r16(p)===0x00E0)return true;return false;};
  for(let start=0;start<MAX;start+=0x8000){const end=Math.min(MAX,start+0x8000);for(let o=start+(start&1);o+4<=end;o+=2){const v=r32(o);for(const [name,a] of Object.entries(PLAYER))if(v===a){const q=nearest(o);longRefs.push({player:name,off:h(o),prev:hw(o>=2?r16(o-2):0),hasE0:e0(o),nearTypes:q?.types?.join('/')||'',distance:q?.d??null,ctx:hex(Math.max(0,o-8),24)});}const w=r16(o);for(const [name,a] of Object.entries(lows))if(w===a){const q=nearest(o);wordRefs.push({player:name,off:h(o),prev:hw(o>=2?r16(o-2):0),hasE0:e0(o),nearTypes:q?.types?.join('/')||'',distance:q?.d??null,ctx:hex(Math.max(0,o-8),20)});}}await sleep(0);}
  return{longRefs,wordRefs};
}
function commonHelpers(refs){const {unique}=model(),m=new Map();for(const u of unique){const seen=new Set();for(const c of callsIn(u.entry)){if(seen.has(c.target))continue;seen.add(c.target);let z=m.get(c.target);if(!z){z={target:c.target,callers:new Set(),kinds:new Set()};m.set(c.target,z);}z.callers.add(u.entry);z.kinds.add(c.kind);}}
 const rows=[];for(const z of m.values()){let l=0,w=0,e0=0;for(const x of refs.longRefs)if(Math.abs(parseInt(x.off,16)-z.target)<=0x300)l++;for(const x of refs.wordRefs)if(Math.abs(parseInt(x.off,16)-z.target)<=0x300)w++;for(let p=Math.max(0,z.target-0x100)&~1;p+1<Math.min(MAX,z.target+0x300);p+=2)if(r16(p)===0x00E0)e0++;const callerTypes=[];for(const e of z.callers){const u=unique.find(x=>x.entry===e);if(u)callerTypes.push(...u.types);}const score=z.callers.size*2+l*12+w*2+Math.min(4,e0);if(z.callers.size>=2||l||w>=2)rows.push({target:h(z.target),callerGroups:z.callers.size,types:[...new Set(callerTypes)].sort((a,b)=>a-b).join(','),kinds:[...z.kinds].join('/'),longHits:l,wordHits:w,strideHits:e0,score,ctx:hex(z.target,32)});}rows.sort((a,b)=>b.score-a.score||b.callerGroups-a.callerGroups);return rows;}
async function result(){need();console.log('🔎 分片扫描 ROM 引用…');const refs=await playerRefs(),helpers=commonHelpers(refs),{TYPES}=model();const vectors={sp:h(r32(0)),pc:h(r32(4)),romBaseHeap:'0x'+base.toString(16).toUpperCase(),romBytes:MAX,dispatchTable:h(TBL),locator:LOC.label,swap16:SWAP,validDispatch:LOC.validDispatch};const types=TYPES.map(x=>({type:x.type,entry:h(x.entry),valid:x.entry<MAX,sharedWith:TYPES.filter(y=>y.entry===x.entry&&y.type!==x.type).map(y=>y.type).join(',')}));console.log('=== ROM vectors / type table ===');console.log(vectors);console.table(types);console.log('=== direct 32-bit P1/P2/P3 refs ===');console.table(refs.longRefs.slice(0,80));console.log('=== low-16 P1/P2/P3 refs ===');console.table(refs.wordRefs.slice(0,120));console.log('=== common helper candidates ===');console.table(helpers.slice(0,50));const out={version:'rom-focus-probe-v3-safe',vectors,types,longRefs:refs.longRefs,wordRefs:refs.wordRefs,helpers:helpers.slice(0,100)};self.__WOF_ROM_FOCUS_LAST=out;return out;}
function routine(type,span=0x700){need();const {TYPES}=model(),x=TYPES[type];if(!x)return null;const cs=callsIn(x.entry,span).map(c=>({at:h(c.at),target:h(c.target),kind:c.kind}));console.table(cs);return{type,entry:h(x.entry),calls:cs,hex:hex(x.entry,96)};}
function dump(off,n=128){need();off=typeof off==='string'?parseInt(off,16):off;const row={off:h(off),hex:hex(off,n)};console.log(row.off,row.hex);return row;}
self.WOFFOCUSROM={version:'rom-focus-probe-v3-safe',found:false,get located(){return!!LOC;},locate:async o=>{const x=await locate(o);this.found=!!x;return x;},result,routine,dump,diagnose(){return{heapBytes:heap().length,located:!!LOC,locator:LOC};},stop(){stopped=true;console.log('⛔ ROM focus scan stop requested');}};
console.log('✅ WOF ROM focus probe v3 SAFE loaded · 当前没有扫描HEAP');
console.log('第一步: await WOFFOCUSROM.locate()');
})();