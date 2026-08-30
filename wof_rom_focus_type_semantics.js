(()=>{
'use strict';
try{self.WOFFOCUSTYPESEM?.stop?.();}catch(_){}
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let stopped=false;
const load=async f=>{const r=await fetch(RAW+f+'?x='+Math.random());if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);const s=await r.text();return await (0,eval)(s);};
async function ensure(){
  if(!self.__WOF_ROM_LOC_CACHE||!self.__WOF_ROM_FOCUS_LAST?.types?.length)await load('wof_rom_focus_inspect.js');
  if(!self.__WOF_ROM_FOCUS_TYPE_DISPATCH?.refs?.length){await load('wof_rom_focus_type_dispatch.js');await WOFFOCUSTYPEDISPATCH.run();}
  if(!self.__WOF_ROM_FOCUS_TYPE_FLOW?.reports?.length){await load('wof_rom_focus_type_flow.js');await WOFFOCUSTYPEFLOW.run();}
  if(!self.__WOF_ROM_LOC_CACHE||!self.__WOF_ROM_FOCUS_LAST?.types?.length)throw new Error('ROM state unavailable');
}
function env(){
  const MOD=_0x515056,C=self.__WOF_ROM_LOC_CACHE,L=self.__WOF_ROM_FOCUS_LAST,M=MOD.HEAPU8,base=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-base),DELTA=C.offlineDelta|0;
  const r8=o=>M[base+(SW?(o^1):o)]>>>0,r16=o=>((r8(o)<<8)|r8(o+1))>>>0,r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
  const s8=v=>v&0x80?v-0x100:v,s16=v=>v&0x8000?v-0x10000:v;
  const h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0'),off=x=>h((x-DELTA)>>>0),hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
  let dispatch=Number(C.dispatch);if(!Number.isFinite(dispatch))dispatch=parseInt(C.dispatch,16);if(!Number.isFinite(dispatch))dispatch=0x25DC;
  return{L,MAX,r8,r16,r32,s8,s16,h,off,hw,dispatch:dispatch>>>0};
}
function extInfo(E,p){
  const x=E.r16(p+2),isA=!!(x&0x8000),reg=(x>>12)&7,isLong=!!(x&0x0800),scaleBits=(x>>9)&3,disp8=E.s8(x&255),pcBase=(p+2)>>>0,effectiveZero=(p+2+disp8)>>>0;
  return{raw:x,ext:E.hw(x),index:(isA?'A':'D')+reg,indexKind:isA?'A':'D',indexReg:reg,indexSize:isLong?'L':'W',scaleBits,effective68000Scale:1,disp8,pcBase,effectiveZero};
}
function exactMoveA4(E,p){
  const w=E.r16(p),g=w>>>12,sm=(w>>3)&7,sr=w&7,dm=(w>>6)&7,dr=(w>>9)&7;
  const x=extInfo(E,p);
  const ok=g===2&&sm===7&&sr===3&&dm===1&&dr===4;
  return{ok,opcode:E.hw(w),group:g,size:g===2?'L':g===3?'W':g===1?'B':'?',srcMode:sm,srcReg:sr,dstMode:dm,dstReg:dr,...x};
}
function tableMatches(E,base){
  const types=(E.L.types||[]).map(x=>({type:Number(x.type),entry:Number(x.entry??x.liveEntry??0)})).filter(x=>Number.isFinite(x.type)&&Number.isFinite(x.entry)).sort((a,b)=>a.type-b.type);
  const rows=[];let exact=0,validCode=0;
  for(const t of types){const a=(base+t.type*4)>>>0,v=a+4<=E.MAX?E.r32(a):0,match=v===t.entry;if(match)exact++;const op=v+2<=E.MAX?E.r16(v):0,codeish=v<E.MAX&&(v&1)===0&&op!==0&&op!==0xffff&&op!==0x4afc;if(codeish)validCode++;rows.push({type:t.type,tableAt:E.h(a),loaded:E.h(v),expected:E.h(t.entry),match,firstOp:codeish?E.hw(op):''});}
  return{rows,exact,validCode,total:types.length};
}
function rawContext(E,p,before=0x18,after=0x20){const rows=[];for(let q=Math.max(0,p-before)&~1;q<=Math.min(E.MAX-2,p+after);q+=2)rows.push({at:E.h(q),offline:E.off(q),word:E.hw(E.r16(q)),mark:q===p?'<<< REF':q===p+2?'<<< EXT':''});return rows;}
function d1Hints(E,p,back=0x50){
  const out=[];
  for(let q=Math.max(0,p-back)&~1;q<p;q+=2){const w=E.r16(q),g=w>>>12;let hint='';
    if(g===1||g===2||g===3){const dm=(w>>6)&7,dr=(w>>9)&7;if(dm===0&&dr===1)hint='MOVE -> D1';}
    if((w&0xF100)===0x7000&&((w>>9)&7)===1)hint='MOVEQ -> D1';
    if(g===13&&((w>>9)&7)===1&&((w>>3)&7)===0&&(w&7)===1)hint='ADD D1,D1';
    if(g===14&&(w&7)===1)hint='SHIFT/ROT D1';
    if(g===12&&(((w>>9)&7)===1||((w&7)===1)))hint=hint||'AND/MUL involving D1';
    if(g===11&&(((w>>9)&7)===1||((w&7)===1)))hint=hint||'CMP/EOR involving D1';
    if(hint)out.push({at:E.h(q),offline:E.off(q),op:E.hw(w),hint,distance:p-q,near:[-2,0,2,4].map(d=>q+d>=0&&q+d+2<=E.MAX?E.hw(E.r16(q+d)):'').join(' ')});
  }
  return out.sort((a,b)=>a.distance-b.distance);
}
function rawDirectCallers(E,target,slack=0){
  const out=[];
  for(let p=0;p+6<E.MAX;p+=2){const w=E.r16(p);let t=null,k='';if(w===0x4eb9){t=E.r32(p+2);k='JSR.L';}else if(w===0x4eba){t=p+2+E.s16(E.r16(p+2));k='JSR.PC';}else if((w&0xff00)===0x6100){const d=w&255;t=d===0?p+2+E.s16(E.r16(p+2)):p+2+E.s8(d);k='BSR';}if(t!=null&&Math.abs((t&~1)-(target&~1))<=slack)out.push({at:E.h(p),offline:E.off(p),kind:k,target:E.h(t&~1)});}
  return out.slice(0,80);
}
async function run(){
  stopped=false;await ensure();const E=env(),TD=self.__WOF_ROM_FOCUS_TYPE_DISPATCH,TF=self.__WOF_ROM_FOCUS_TYPE_FLOW;
  const refs=[...new Map((TD.refs||[]).filter(x=>(x.dstMode===1&&x.dstReg===4)||x.dst==='A4').map(x=>[Number(x.at),x])).values()].sort((a,b)=>Number(a.at)-Number(b.at));
  console.log('🔬 WOF type-table semantics verifier v1');
  const reports=[];
  for(const r of refs){
    const p=Number(r.at),m=exactMoveA4(E,p),match=tableMatches(E,m.effectiveZero),flow=(TF.reports||[]).find(x=>parseInt(x.ref,16)===p),funcStart=flow?parseInt(flow.funcStart,16):NaN;
    const exactBase=m.effectiveZero===E.dispatch,delta=(m.effectiveZero-E.dispatch)|0;
    const z={ref:E.h(p),offline:E.off(p),opcode:m.opcode,extension:m.ext,exactMoveA4:m.ok,index:m.index,indexSize:m.indexSize,disp8:m.disp8,pcBase:E.h(m.pcBase),effectiveZero:E.h(m.effectiveZero),dispatch:E.h(E.dispatch),baseDelta:delta,baseExact:exactBase,tableExact:match.exact,tableTotal:match.total,codeish:match.validCode,onBoundary:!!flow?.onBoundary,funcStart:Number.isFinite(funcStart)?E.h(funcStart):'',rawCallers:Number.isFinite(funcStart)?rawDirectCallers(E,funcStart).length:0};
    reports.push({...z,tableRows:match.rows,d1Hints:d1Hints(E,p),callers:Number.isFinite(funcStart)?rawDirectCallers(E,funcStart):[]});
    console.log('\n=== EXACT TYPE REF '+E.h(p)+' ===');console.table([z]);
    console.log('=== D1 PRODUCER / SCALE HINTS ===');console.table(d1Hints(E,p));
    console.log('=== 47 ENTRY EFFECTIVE-ADDRESS MATCH ===');console.table(match.rows);
    console.log('=== RAW WORD CONTEXT ===');console.table(rawContext(E,p));
    if(Number.isFinite(funcStart)){console.log('=== RAW DIRECT CALLERS OF CONTAINING ROUTINE ===');console.table(rawDirectCallers(E,funcStart));}
  }
  const exactMove=reports.filter(x=>x.exactMoveA4).length,exactBase=reports.filter(x=>x.baseExact).length,full47=reports.filter(x=>x.tableExact===x.tableTotal&&x.tableTotal===47).length,reachableish=reports.filter(x=>x.rawCallers>0).length;
  const verdict={refs:reports.length,exactMoveA4:exactMove,exactDispatchBase:exactBase,full47TableMatch:full47,refsWithRawDirectCallers:reachableish,topRef:reports[0]?.ref||'',topFunc:reports[0]?.funcStart||'',topIndex:reports[0]?.index||'',topBase:reports[0]?.effectiveZero||'',top47Match:reports[0]?.tableExact||0};
  console.log('\n=== TYPE REF SEMANTICS VERDICT ===');console.table([verdict]);
  if(full47===reports.length&&reports.length)console.log('✅ 这两条确实是 0x25DC[type×4] → A4 的真实 handler load；下一步不再质疑表语义，改查 A4 load 所在 routine 的真正入口/调用协议或动态执行。');
  else if(exactMove&&exactBase)console.warn('⚠️ MOVEA/基址成立但 47-entry 对照不完整；检查 D1 stride/live table 映射。');
  else console.warn('❌ 之前把 ref 解释为 0x25DC[type] → A4 有误；应停止 A4 handler-flow 路线，重新定位真实 type dispatcher。');
  const out={version:'rom-focus-type-semantics-v1',verdict,reports};self.__WOF_ROM_FOCUS_TYPE_SEM=out;return out;
}
self.WOFFOCUSTYPESEM={version:'rom-focus-type-semantics-v1',run,stop(){stopped=true;}};
console.log('✅ WOF ROM focus type semantics v1 loaded');console.log('执行 await WOFFOCUSTYPESEM.run()');
})();