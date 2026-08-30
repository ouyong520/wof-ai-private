(()=>{
'use strict';
try{self.WOFFOCUSINDIRECT?.stop?.();}catch(_){}
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let stopped=false;
const load=async f=>{const r=await fetch(RAW+f+'?x='+Math.random());if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);const s=await r.text();(0,eval)(s);};
async function ensure(){
  if(!self.__WOF_ROM_FOCUS_TRACE?.candidate){await load('wof_rom_focus_trace.js');await self.WOFFOCUSTRACE.run();}
  if(!self.__WOF_ROM_LOC_CACHE||!self.__WOF_ROM_FOCUS_LAST)throw new Error('ROM focus state unavailable');
}
function env(){
  const MOD=_0x515056,C=self.__WOF_ROM_LOC_CACHE,L=self.__WOF_ROM_FOCUS_LAST;
  const M=MOD.HEAPU8,base=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-base),DELTA=C.offlineDelta|0;
  const r8=o=>M[base+(SW?(o^1):o)]>>>0;
  const r16=o=>((r8(o)<<8)|r8(o+1))>>>0;
  const r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
  const s8=v=>v&0x80?v-0x100:v,s16=v=>v&0x8000?v-0x10000:v;
  const h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0');
  const off=x=>h((x-DELTA)>>>0);
  const hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
  return{M,base,SW,MAX,DELTA,L,r8,r16,r32,s8,s16,h,off,hw};
}
function extInfo(E,site){
  const ext=E.r16(site+2),isA=!!(ext&0x8000),reg=(ext>>12)&7,isLong=!!(ext&0x0800),scale=1<<((ext>>9)&3),disp=E.s8(ext&255);
  return{ext:E.hw(ext),index:(isA?'A':'D')+reg,indexReg:reg,indexKind:isA?'A':'D',indexSize:isLong?'L':'W',scale,disp8:disp};
}
function decode(E,p){
  const{r16,r32,s8,s16,h,hw,MAX}=E,w=r16(p);let text='',len=2,target=null;
  if(w===0x4E75)text='RTS';
  else if(w===0x4E71)text='NOP';
  else if(w===0x4EB9){target=r32(p+2);text='JSR '+h(target);len=6;}
  else if(w===0x4EF9){target=r32(p+2);text='JMP '+h(target);len=6;}
  else if(w===0x4EB8){target=s16(r16(p+2))>>>0;text='JSR '+h(target)+' (abs.W)';len=4;}
  else if(w===0x4EF8){target=s16(r16(p+2))>>>0;text='JMP '+h(target)+' (abs.W)';len=4;}
  else if(w===0x4EBA){target=p+2+s16(r16(p+2));text='JSR '+h(target)+' (PC)';len=4;}
  else if(w===0x4EFA){target=p+2+s16(r16(p+2));text='JMP '+h(target)+' (PC)';len=4;}
  else if((w&0xFFF8)===0x4E90)text='JSR (A'+(w&7)+')';
  else if((w&0xFFF8)===0x4ED0)text='JMP (A'+(w&7)+')';
  else if((w&0xFFF8)===0x4EA8){text='JSR '+s16(r16(p+2))+'(A'+(w&7)+')';len=4;}
  else if((w&0xFFF8)===0x4EE8){text='JMP '+s16(r16(p+2))+'(A'+(w&7)+')';len=4;}
  else if((w&0xFFF8)===0x4EB0){const x=extInfo(E,p);text='JSR '+x.disp8+'(A'+(w&7)+','+x.index+'.'+x.indexSize+'*'+x.scale+')';len=4;}
  else if((w&0xFFF8)===0x4EF0){const x=extInfo(E,p);text='JMP '+x.disp8+'(A'+(w&7)+','+x.index+'.'+x.indexSize+'*'+x.scale+')';len=4;}
  else if(w===0x4EBB){const x=extInfo(E,p);text='JSR '+x.disp8+'(PC,'+x.index+'.'+x.indexSize+'*'+x.scale+')';len=4;}
  else if(w===0x4EFB){const x=extInfo(E,p);text='JMP '+x.disp8+'(PC,'+x.index+'.'+x.indexSize+'*'+x.scale+')';len=4;}
  else if((w&0xF1FF)===0x41F9){const a=(w>>9)&7,target=r32(p+2);text='LEA '+h(target)+',A'+a;len=6;}
  else if((w&0xF1FF)===0x41FA){const a=(w>>9)&7,d=s16(r16(p+2)),t=p+2+d;text='LEA '+h(t)+'(PC),A'+a;target=t;len=4;}
  else if((w&0xF1FF)===0x207C){const a=(w>>9)&7,target=r32(p+2);text='MOVEA.L #'+h(target)+',A'+a;len=6;}
  else if((w&0xFF00)===0x7000){const d=(w>>9)&7;text='MOVEQ #'+s8(w&255)+',D'+d;}
  else if((w&0xFF00)===0x6000){const cc=(w>>8)&15,d=w&255,t=d===0?p+2+s16(r16(p+2)):p+2+s8(d);target=t;text=(cc===0?'BRA':cc===1?'BSR':'Bcc'+cc)+' '+h(t);len=d===0?4:2;}
  else text=hw(w);
  if(target!=null&&(target<0||target>=MAX))target=null;
  return{at:p,word:w,text,len,target};
}
function context(E,site,before=0x90,after=0x30){
  const rows=[];for(let p=Math.max(0,site-before)&~1;p<Math.min(E.MAX,site+after);p+=2){const d=decode(E,p);rows.push({at:E.h(p),offline:E.off(p),op:E.hw(d.word),text:d.text,mark:p===site?'<<< INDIRECT':''});}
  return rows;
}
function scanA2Sources(E,site,back=0x120){
  const out=[];for(let p=Math.max(0,site-back)&~1;p<site;p+=2){const w=E.r16(p);let kind='',value=null,len=2;
    if((w&0xF1FF)===0x41F9&&((w>>9)&7)===2){value=E.r32(p+2);kind='LEA abs.L -> A2';len=6;}
    else if((w&0xF1FF)===0x41FA&&((w>>9)&7)===2){value=p+2+E.s16(E.r16(p+2));kind='LEA d16(PC) -> A2';len=4;}
    else if((w&0xF1FF)===0x207C&&((w>>9)&7)===2){value=E.r32(p+2);kind='MOVEA.L #imm -> A2';len=6;}
    if(kind)out.push({at:E.h(p),offline:E.off(p),op:E.hw(w),kind,value:value==null?'':E.h(value),distance:site-p,len});
  }
  return out.sort((a,b)=>a.distance-b.distance);
}
function writesIndexHeuristic(E,site,x,back=0x100){
  const out=[],want=x.indexReg,isA=x.indexKind==='A';
  for(let p=Math.max(0,site-back)&~1;p<site;p+=2){const w=E.r16(p);let hint='';
    if(!isA&&((w&0xF100)===0x7000)&&((w>>9)&7)===want)hint='MOVEQ -> D'+want;
    if(!isA&&((w&0xF1C0)===0x3000)&&((w>>9)&7)===want)hint='MOVE.W <ea> -> D'+want;
    if(!isA&&((w&0xF1C0)===0x2000)&&((w>>9)&7)===want)hint='MOVE.L <ea> -> D'+want;
    if(isA&&((w&0xF1C0)===0x2040)&&((w>>9)&7)===want)hint='MOVEA.L <ea> -> A'+want;
    if(hint)out.push({at:E.h(p),offline:E.off(p),op:E.hw(w),hint,distance:site-p,near:[-4,-2,0,2,4].map(d=>E.hw(E.r16(p+d))).join(' ')});
  }
  return out.sort((a,b)=>a.distance-b.distance).slice(0,30);
}
function candidateBases(E,site,x,a2src){
  const bases=[];
  for(const s of a2src){if(!s.value)continue;const b=parseInt(s.value,16);if(Number.isFinite(b)&&b<E.MAX)bases.push({sourceAt:s.at,base:E.h(b),effectiveZero:E.h((b+x.disp8)>>>0),kind:s.kind});}
  // 若没静态 A2 载入，附近绝对地址常量也作为弱候选。
  if(!bases.length){for(let p=Math.max(0,site-0x100)&~1;p<site;p+=2){const v=E.r32(p);if(v<E.MAX&&v>0x1000)bases.push({sourceAt:E.h(p),base:E.h(v),effectiveZero:E.h((v+x.disp8)>>>0),kind:'nearby long constant (weak)'});}}
  return [...new Map(bases.map(z=>[z.base+'|'+z.sourceAt,z])).values()].slice(0,40);
}
function nearbyOffsetTables(E,site,bases){
  const rows=[];
  for(const b0 of bases.slice(0,8)){
    const base=parseInt(b0.base,16),eff=parseInt(b0.effectiveZero,16);
    for(const anchor of [base,eff]){
      if(!(anchor>=0&&anchor<E.MAX))continue;
      const vals=[];for(let i=0;i<24;i++){const a=anchor+i*2,v=E.s16(E.r16(a)),t=(anchor+v)&~1;if(t>=0&&t<E.MAX)vals.push(E.h(t));else vals.push('');}
      rows.push({base:b0.base,anchor:E.h(anchor),source:b0.sourceAt,targets:vals.filter(Boolean).slice(0,16).join(' ')});
    }
  }
  return rows;
}
async function run(){
  stopped=false;await ensure();const E=env(),T=self.__WOF_ROM_FOCUS_TRACE;
  if((T.candidate?.directTypePaths??-1)!==0)console.warn('当前 directTypePaths 不是 0；本脚本仍可检查 indirect，但主线条件已变化');
  const z=(T.indirectReachable||[])[0];if(!z)throw new Error('trace 没有 reachable indirect site');
  const site=parseInt(z.at,16),w=E.r16(site),baseA=w&7,x=extInfo(E,site);
  console.log('🧩 ROM indirect dispatch probe v1');
  console.log('=== INDIRECT SITE ===');console.table([{func:z.func,site:E.h(site),offline:E.off(site),opcode:E.hw(w),base:'A'+baseA,index:x.index,indexSize:x.indexSize,scale:x.scale,disp8:x.disp8,extension:x.ext,kind:z.kind}]);
  const a2=scanA2Sources(E,site);console.log('=== A2 STATIC SOURCES BEFORE JMP ===');console.table(a2);
  const iw=writesIndexHeuristic(E,site,x);console.log('=== INDEX REGISTER PRODUCER HINTS ===');console.table(iw);
  const bases=candidateBases(E,site,x,a2);console.log('=== CANDIDATE DISPATCH BASES ===');console.table(bases);
  const tables=nearbyOffsetTables(E,site,bases);console.log('=== POSSIBLE OFFSET/JUMP TABLE TARGETS ===');console.table(tables);
  console.log('=== LOCAL OPCODE CONTEXT ===');console.table(context(E,site));
  const out={version:'rom-focus-indirect-v1',site:{func:z.func,at:E.h(site),offline:E.off(site),opcode:E.hw(w),base:'A'+baseA,...x},a2Sources:a2,indexHints:iw,bases,tables};self.__WOF_ROM_FOCUS_INDIRECT=out;return out;
}
self.WOFFOCUSINDIRECT={version:'rom-focus-indirect-v1',run,stop(){stopped=true;}};
console.log('✅ WOF ROM focus indirect v1 loaded');
console.log('执行 await WOFFOCUSINDIRECT.run()');
})();