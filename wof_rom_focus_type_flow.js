(()=>{
'use strict';
try{self.WOFFOCUSTYPEFLOW?.stop?.();}catch(_){}
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let stopped=false;
const load=async f=>{const r=await fetch(RAW+f+'?x='+Math.random());if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);const s=await r.text();return await (0,eval)(s);};
async function ensure(){
  if(!self.__WOF_ROM_LOC_CACHE||!self.__WOF_ROM_FOCUS_LAST?.types?.length)await load('wof_rom_focus_inspect.js');
  if(!self.__WOF_ROM_FOCUS_TYPE_DISPATCH?.refs?.length){await load('wof_rom_focus_type_dispatch.js');await WOFFOCUSTYPEDISPATCH.run();}
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
function eaWords(mode,reg,size){if(mode<=4)return 0;if(mode===5||mode===6)return 1;if(mode===7){if(reg===0||reg===2||reg===3)return 1;if(reg===1)return 2;if(reg===4)return size==='L'?2:1;}return 0;}
function idx(E,p){const x=E.r16(p+2);return{ext:E.hw(x),kind:(x&0x8000)?'A':'D',reg:(x>>12)&7,size:(x&0x0800)?'L':'W',disp:E.s8(x&255),base:(p+2+E.s8(x&255))>>>0};}
function moveInfo(E,p){
  const w=E.r16(p),g=w>>>12;if(g!==1&&g!==2&&g!==3)return null;const size=g===1?'B':g===2?'L':'W',sm=(w>>3)&7,sr=w&7,dm=(w>>6)&7,dr=(w>>9)&7;
  const sw=eaWords(sm,sr,size),dw=eaWords(dm,dr,size),len=2+(sw+dw)*2;
  let src='',dst='',ix=null,srcBase=null;
  if(sm===0)src='D'+sr;else if(sm===1)src='A'+sr;else if(sm===2)src='(A'+sr+')';else if(sm===3)src='(A'+sr+')+';else if(sm===4)src='-(A'+sr+')';else if(sm===5)src=E.s16(E.r16(p+2))+'(A'+sr+')';else if(sm===6){ix=idx(E,p);src=ix.disp+'(A'+sr+','+ix.kind+ix.reg+'.'+ix.size+')';}else if(sm===7&&sr===0)src=E.h(E.s16(E.r16(p+2))>>>0)+'.W';else if(sm===7&&sr===1)src=E.h(E.r32(p+2))+'.L';else if(sm===7&&sr===2){srcBase=(p+2+E.s16(E.r16(p+2)))>>>0;src=E.h(srcBase)+'(PC)';}else if(sm===7&&sr===3){ix=idx(E,p);srcBase=ix.base;src=ix.disp+'(PC,'+ix.kind+ix.reg+'.'+ix.size+')';}else if(sm===7&&sr===4)src='#imm';else src='EA';
  if(dm===0)dst='D'+dr;else if(dm===1)dst='A'+dr;else if(dm===2)dst='(A'+dr+')';else if(dm===3)dst='(A'+dr+')+';else if(dm===4)dst='-(A'+dr+')';else if(dm===5)dst='d16(A'+dr+')';else if(dm===6)dst='idx(A'+dr+')';else dst='EA';
  const kind=dm===1?'MOVEA.'+size:'MOVE.'+size;
  return{w,size,sm,sr,dm,dr,sw,dw,len,src,dst,ix,srcBase,kind,text:kind+' '+src+','+dst};
}
function decode(E,p){
  const w=E.r16(p),g=w>>>12,mode=(w>>3)&7,reg=w&7;let len=2,kind='OP',target=null,fall=true,terminal=false,text=E.hw(w),move=null;
  if(w===0x4E75||w===0x4E73||w===0x4E77){kind=w===0x4E75?'RTS':w===0x4E73?'RTE':'RTR';fall=false;terminal=true;text=kind;}
  else if((w&0xFFC0)===0x4E80){len=2+eaWords(mode,reg,'L')*2;kind=(mode===7&&reg<=2)?'JSR_DIRECT':'JSR_INDIRECT';if(mode===7&&reg===0)target=E.s16(E.r16(p+2))>>>0;else if(mode===7&&reg===1)target=E.r32(p+2);else if(mode===7&&reg===2)target=p+2+E.s16(E.r16(p+2));text=kind;}
  else if((w&0xFFC0)===0x4EC0){len=2+eaWords(mode,reg,'L')*2;fall=false;kind=(mode===7&&reg<=2)?'JMP_DIRECT':'JMP_INDIRECT';if(mode===7&&reg===0)target=E.s16(E.r16(p+2))>>>0;else if(mode===7&&reg===1)target=E.r32(p+2);else if(mode===7&&reg===2)target=p+2+E.s16(E.r16(p+2));text=kind;}
  else if(g===6){const cc=(w>>8)&15,d=w&255;len=d===0?4:2;target=d===0?p+2+E.s16(E.r16(p+2)):p+2+E.s8(d);kind=cc===0?'BRA':cc===1?'BSR':'BCC';if(cc===0)fall=false;text=kind;}
  else if(g===1||g===2||g===3){move=moveInfo(E,p);len=move.len;kind=move.kind;text=move.text;}
  else if(g===5){const sz=(w>>6)&3;if(sz===3&&mode===1){kind='DBCC';len=4;target=p+2+E.s16(E.r16(p+2));}else len=2+eaWords(mode,reg,sz===3?'B':sz===2?'L':sz===1?'W':'B')*2;}
  else if(g===0){if([0x003C,0x007C,0x023C,0x027C,0x0A3C,0x0A7C].includes(w))len=4;else if((w&0xF138)===0x0108)len=4;else if((w&0xFF00)===0x0800)len=4+eaWords(mode,reg,'B')*2;else if((w&0xF100)===0x0100)len=2+eaWords(mode,reg,'B')*2;else{const op=(w>>8)&15,sz=(w>>6)&3;if([0,2,4,6,10,12].includes(op)){const s=sz===2?'L':sz===1?'W':'B';len=2+(s==='L'?4:2)+eaWords(mode,reg,s)*2;}}}
  else if(g===4){if((w&0xFFF8)===0x4E50)len=4;else if((w&0xFB80)===0x4880&&mode>=2)len=4+eaWords(mode,reg,(w&0x40)?'L':'W')*2;else if((w&0xF1C0)===0x41C0)len=2+eaWords(mode,reg,'L')*2;else if((w&0xFFC0)===0x4840&&mode!==0)len=2+eaWords(mode,reg,'L')*2;else len=2+eaWords(mode,reg,((w>>6)&3)===2?'L':'W')*2;}
  else if(g===8){if((w&0xF1F0)!==0x8100)len=2+eaWords(mode,reg,((w>>6)&3)===2?'L':'W')*2;}
  else if(g===9||g===13){if((w&0xF130)!==0x9100&&(w&0xF130)!==0xD100)len=2+eaWords(mode,reg,((w>>6)&3)===2?'L':'W')*2;}
  else if(g===11){if((w&0xF138)!==0xB108)len=2+eaWords(mode,reg,((w>>6)&3)===2?'L':'W')*2;}
  else if(g===12){const exg=(w&0xF1F8)===0xC140||(w&0xF1F8)===0xC148||(w&0xF1F8)===0xC188,abcd=(w&0xF1F0)===0xC100;if(!exg&&!abcd)len=2+eaWords(mode,reg,((w>>6)&3)===2?'L':'W')*2;}
  else if(g===14&&((w>>6)&3)===3)len=2+eaWords(mode,reg,'W')*2;
  else if(g===10||g===15){terminal=true;fall=false;kind='LINE';}
  const next=p+len;if(target!=null&&(target<0||target>=E.MAX))target=null;return{at:p,w,len,next,kind,target,fall,terminal,text,mode,reg,move};
}
function findStart(E,at){
  for(let p=at&~1;p>=Math.max(0,at-0x300);p-=2){const w=E.r16(p);if((w&0xFFF8)===0x4E50||w===0x48E7)return p;if(w===0x4E75||w===0x4E73||w===0x4E77)return p+2;}
  return Math.max(0,(at-0x100)&~1);
}
function cfg(E,start,cap=0x600){
  const hi=Math.min(E.MAX,start+cap),q=[start&~1],seen=new Set(),rows=[];
  while(q.length&&seen.size<3000){if(stopped)break;const p=q.shift();if(p<start||p>=hi||(p&1)||seen.has(p))continue;seen.add(p);const d=decode(E,p);rows.push(d);
    if(d.kind==='BRA'){if(d.target!=null)q.push(d.target&~1);continue;}if(d.kind==='BCC'||d.kind==='DBCC'){if(d.fall)q.push(d.next);if(d.target!=null)q.push(d.target&~1);continue;}if(d.kind==='JMP_DIRECT'){if(d.target!=null&&d.target>=start&&d.target<hi)q.push(d.target&~1);continue;}if(d.kind==='JMP_INDIRECT'||d.terminal)continue;if(d.fall)q.push(d.next);
  }
  return{rows,seen};
}
function a4Use(E,d){
  const w=d.w,mi=d.move;
  if((w&0xFFC0)===0x4E80|| (w&0xFFC0)===0x4EC0){const mode=(w>>3)&7,reg=w&7;if(reg===4&&mode>=2&&mode<=6)return{kind:d.kind,text:(d.kind.startsWith('JSR')?'JSR ':'JMP ')+(mode===2?'(A4)':mode===5?'d16(A4)':mode===6?'idx(A4)':'A4-EA'),terminalTransfer:true};}
  if(mi){
    if(mi.sm===1&&mi.sr===4){const stack=mi.dr===7&&(mi.dm===2||mi.dm===4);return{kind:stack?'A4_TO_STACK':'A4_READ',text:mi.text,terminalTransfer:false,stack};}
    if(mi.dm===1&&mi.dr===4)return{kind:'A4_WRITE',text:mi.text,write:true};
  }
  if((w&0xFFC0)===0x4840){const mode=(w>>3)&7,reg=w&7;if(mode===2&&reg===4)return{kind:'PEA_A4',text:'PEA (A4)',stack:true};}
  return null;
}
function linearAfter(E,from,maxBytes=0x100){const out=[];let p=from;for(let n=0;n<80&&p<E.MAX&&p<from+maxBytes;n++){const d=decode(E,p);out.push(d);if(d.terminal||d.kind==='JMP_DIRECT'||d.kind==='JMP_INDIRECT'||d.kind==='BRA')break;p=d.next;}return out;}
function directCallAt(E,p){const w=E.r16(p);if(w===0x4EB8){const t=E.s16(E.r16(p+2))>>>0;if(t<E.MAX)return{at:p,target:t&~1,kind:'JSR.W',len:4};}if(w===0x4EB9){const t=E.r32(p+2);if(t<E.MAX)return{at:p,target:t&~1,kind:'JSR.L',len:6};}if(w===0x4EBA){const t=p+2+E.s16(E.r16(p+2));if(t>=0&&t<E.MAX)return{at:p,target:t&~1,kind:'JSR.PC',len:4};}if((w&0xFF00)===0x6100){const d=w&255,t=d===0?p+2+E.s16(E.r16(p+2)):p+2+E.s8(d);if(t>=0&&t<E.MAX)return{at:p,target:t&~1,kind:'BSR',len:d===0?4:2};}return null;}
async function callersOf(E,start,end){const out=[];for(let b=0;b<E.MAX;b+=0x8000){const hi=Math.min(E.MAX,b+0x8000);for(let p=b;p+6<hi;p+=2){const c=directCallAt(E,p);if(c&&c.target>=start&&c.target<end)out.push(c);}if((b&0x1FFFF)===0x18000)await sleep(0);}return out;}
function d1History(E,rows,refAt){const out=[];for(const d of rows){if(d.at>=refAt)continue;const m=d.move;if(m&&m.dm===0&&m.dr===1)out.push({at:d.at,text:m.text,kind:'D1_WRITE'});const w=d.w;if((w&7)===1&&(w>>>12)===14)out.push({at:d.at,text:'SHIFT/ROT D1 '+E.hw(w),kind:'D1_SHIFT'});if((w>>>12)===13&&((w>>9)&7)===1&&((w>>3)&7)===0&&(w&7)===1)out.push({at:d.at,text:'ADD D1,D1 '+E.hw(w),kind:'D1_DOUBLE'});}return out.sort((a,b)=>b.at-a.at).slice(0,16);}
async function run(){
  stopped=false;await ensure();const E=env(),TD=self.__WOF_ROM_FOCUS_TYPE_DISPATCH;
  const refs=[...new Map((TD.refs||[]).filter(x=>(x.dstMode===1&&x.dstReg===4)||x.dst==='A4').map(x=>[x.at,x])).values()];
  console.log('🧬 WOF type handler flow v1 · 0x25DC[D1] → A4 → caller/transfer');
  console.log('=== A4 TYPE-TABLE LOAD REFS ===');console.table(refs.map(x=>({at:E.h(x.at),offline:E.off(x.at),kind:x.kind,index:x.index||'',dstMode:x.dstMode,dstReg:x.dstReg,score:x.score})));
  const reports=[];
  for(const r of refs){
    const at=r.at,start=findStart(E,at),C=cfg(E,start),onBoundary=C.seen.has(at),d=decode(E,at),m=d.move,ix=m?.ix||null;
    const base=ix&&m?.sm===7&&m?.sr===3?ix.base:null;
    const d1=d1History(E,C.rows,at);
    const after=linearAfter(E,d.next,0x140),uses=[];let firstOverwrite=null,returnsWithA4=false;
    for(const z of after){const u=a4Use(E,z);if(u){uses.push({at:E.h(z.at),offline:E.off(z.at),...u});if(u.write&&!firstOverwrite)firstOverwrite=z.at;}if(z.kind==='RTS'&&!firstOverwrite)returnsWithA4=true;}
    let callers=[];if(returnsWithA4){const cs=await callersOf(E,start,Math.min(E.MAX,start+2));for(const c of cs.slice(0,80)){const seq=linearAfter(E,c.at+c.len,0x80),cu=[];for(const z of seq){const u=a4Use(E,z);if(u)cu.push({at:E.h(z.at),offline:E.off(z.at),...u});if(u?.terminalTransfer||u?.write||z.kind==='RTS')break;}callers.push({callAt:E.h(c.at),offlineCall:E.off(c.at),kind:c.kind,callerStart:E.h(findStart(E,c.at)),a4Uses:cu});}}
    reports.push({ref:E.h(at),start:E.h(start),onBoundary,decoded:d.text,tableBase:base==null?'':E.h(base),index:ix?(ix.kind+ix.reg+'.'+ix.size):'',d1,uses,returnsWithA4,callers});
    console.log('\n=== REF '+E.h(at)+' BOUNDARY / DECODE ===');console.table([{ref:E.h(at),funcStart:E.h(start),onInstructionBoundary:onBoundary,decoded:d.text,tableBase:base==null?'':E.h(base),index:ix?(ix.kind+ix.reg+'.'+ix.size):'',returnsWithA4,localA4Uses:uses.length,callers:callers.length}]);
    console.log('=== D1 FLOW BEFORE TABLE LOAD ===');console.table(d1.map(x=>({at:E.h(x.at),offline:E.off(x.at),kind:x.kind,text:x.text})));
    console.log('=== A4 USES AFTER TABLE LOAD ===');console.table(uses);
    if(returnsWithA4){console.log('=== CALLERS CONSUMING RETURNED A4 ===');console.table(callers.flatMap(c=>c.a4Uses.map(u=>({callAt:c.callAt,caller:c.callerStart,callKind:c.kind,useAt:u.at,useKind:u.kind,text:u.text}))));}
  }
  const valid=reports.filter(x=>x.onBoundary),ret=valid.filter(x=>x.returnsWithA4),localTransfers=valid.reduce((n,x)=>n+x.uses.filter(u=>u.terminalTransfer||u.stack).length,0),callerTransfers=valid.reduce((n,x)=>n+x.callers.reduce((a,c)=>a+c.a4Uses.filter(u=>u.terminalTransfer||u.stack).length,0),0);
  const verdict={dispatchTable:E.h(E.dispatch),a4Refs:refs.length,validBoundaryRefs:valid.length,falseRefs:refs.length-valid.length,refsReturningA4:ret.length,localA4Transfers:localTransfers,callerA4Transfers:callerTransfers,topRef:valid[0]?.ref||'',topDecoded:valid[0]?.decoded||'',topTableBase:valid[0]?.tableBase||'',topIndex:valid[0]?.index||''};
  console.log('=== TYPE HANDLER FLOW VERDICT ===');console.table([verdict]);
  if(!valid.length)console.warn('❌ 0x25DC raw refs 也是非指令边界假阳性；下一步必须重新按上游真实 CFG 找 table user。');
  else if(localTransfers||callerTransfers)console.log('🎯 已找到 A4 handler 的真实控制转移消费点；下一步从该 transfer 向前追 enemy/type/state/target selection。');
  else if(ret.length)console.warn('⚠️ handler 确实通过 A4 返回，但当前 direct callers 未看到消费；下一步扩大 caller-of-caller / 保存 A4 数据流。');
  else console.warn('⚠️ A4 table load 是真实指令，但未在当前线性路径发现 transfer/return；下一步做完整分支数据流而不是继续猜 trampoline。');
  const out={version:'rom-focus-type-flow-v1',verdict,reports};self.__WOF_ROM_FOCUS_TYPE_FLOW=out;return out;
}
self.WOFFOCUSTYPEFLOW={version:'rom-focus-type-flow-v1',run,stop(){stopped=true;}};
console.log('✅ WOF ROM focus type-flow v1 loaded');console.log('执行 await WOFFOCUSTYPEFLOW.run()');
})();