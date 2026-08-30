(()=>{
'use strict';
try{self.WOFFOCUSTYPEDISPATCH?.stop?.();}catch(_){}
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let stopped=false;
const load=async f=>{const r=await fetch(RAW+f+'?x='+Math.random());if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);const s=await r.text();return await (0,eval)(s);};
async function ensure(){
  if(self.__WOF_ROM_LOC_CACHE&&self.__WOF_ROM_FOCUS_LAST?.types?.length)return;
  console.log('♻️ type-dispatch: ROM state missing，自动恢复…');
  await load('wof_rom_focus_inspect.js');
  if(!self.__WOF_ROM_LOC_CACHE||!self.__WOF_ROM_FOCUS_LAST?.types?.length)throw new Error('ROM state restore failed');
}
function env(){
  const MOD=_0x515056,C=self.__WOF_ROM_LOC_CACHE,L=self.__WOF_ROM_FOCUS_LAST,M=MOD.HEAPU8,base=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-base),DELTA=C.offlineDelta|0;
  const r8=o=>M[base+(SW?(o^1):o)]>>>0;
  const r16=o=>((r8(o)<<8)|r8(o+1))>>>0;
  const r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
  const s8=v=>v&0x80?v-0x100:v,s16=v=>v&0x8000?v-0x10000:v;
  const h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0'),off=x=>h((x-DELTA)>>>0),hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
  let dispatch=Number(C.dispatch);if(!Number.isFinite(dispatch))dispatch=parseInt(C.dispatch,16);if(!Number.isFinite(dispatch))dispatch=0x25DC;
  return{L,MAX,r8,r16,r32,s8,s16,h,off,hw,dispatch:dispatch>>>0};
}
function sizeFrom2(bits){return bits===0?'B':bits===1?'W':bits===2?'L':'W';}
function eaWords(mode,reg,size){if(mode<=4)return 0;if(mode===5||mode===6)return 1;if(mode===7){if(reg===0||reg===2||reg===3)return 1;if(reg===1)return 2;if(reg===4)return size==='L'?2:1;}return 0;}
function idx(E,p){const x=E.r16(p+2);return{ext:x,indexKind:(x&0x8000)?'A':'D',indexReg:(x>>12)&7,indexSize:(x&0x0800)?'L':'W',disp8:E.s8(x&255),pcBase:(p+2+E.s8(x&255))>>>0};}
function decode(E,p){
 const w=E.r16(p),g=w>>>12,mode=(w>>3)&7,reg=w&7;let words=1,kind='OP',target=null,fall=true,terminal=false,indirect=false;
 if(w===0x4E75||w===0x4E73||w===0x4E77){kind='RET';fall=false;terminal=true;}
 else if(w===0x4E72){kind='STOP';words=2;fall=false;terminal=true;}
 else if((w&0xFFC0)===0x4E80){words=1+eaWords(mode,reg,'L');kind=(mode===7&&reg<=2)?'JSR_DIRECT':'JSR_INDIRECT';indirect=kind==='JSR_INDIRECT';if(mode===7&&reg===0)target=E.s16(E.r16(p+2))>>>0;else if(mode===7&&reg===1)target=E.r32(p+2);else if(mode===7&&reg===2)target=p+2+E.s16(E.r16(p+2));}
 else if((w&0xFFC0)===0x4EC0){words=1+eaWords(mode,reg,'L');fall=false;kind=(mode===7&&reg<=2)?'JMP_DIRECT':'JMP_INDIRECT';indirect=kind==='JMP_INDIRECT';if(mode===7&&reg===0)target=E.s16(E.r16(p+2))>>>0;else if(mode===7&&reg===1)target=E.r32(p+2);else if(mode===7&&reg===2)target=p+2+E.s16(E.r16(p+2));}
 else if(g===6){const cc=(w>>8)&15,d=w&255;words=d===0?2:1;target=d===0?p+2+E.s16(E.r16(p+2)):p+2+E.s8(d);kind=cc===0?'BRA':cc===1?'BSR':'BCC';if(cc===0)fall=false;}
 else if(g===1||g===2||g===3){const size=g===1?'B':g===2?'L':'W',dm=(w>>6)&7,dr=(w>>9)&7;words=1+eaWords(mode,reg,size)+eaWords(dm,dr,size);kind='MOVE.'+size;}
 else if(g===5){const sz=(w>>6)&3;if(sz===3&&mode===1){kind='DBCC';words=2;target=p+2+E.s16(E.r16(p+2));}else{kind=sz===3?'SCC':'ADDQ/SUBQ';words=1+eaWords(mode,reg,sz===3?'B':sizeFrom2(sz));}}
 else if(g===7)kind='MOVEQ';
 else if(g===0){if([0x003C,0x007C,0x023C,0x027C,0x0A3C,0x0A7C].includes(w)){kind='IMM_SR';words=2;}else if((w&0xF138)===0x0108){kind='MOVEP';words=2;}else if((w&0xFF00)===0x0800){kind='BIT_IMM';words=2+eaWords(mode,reg,'B');}else if((w&0xF100)===0x0100){kind='BIT_DYN';words=1+eaWords(mode,reg,'B');}else{const op=(w>>8)&15,sz=(w>>6)&3;if([0,2,4,6,10,12].includes(op)){const size=sizeFrom2(sz);words=1+(size==='L'?2:1)+eaWords(mode,reg,size);kind='IMM';}else kind='G0';}}
 else if(g===4){const movem=((w&0xFB80)===0x4880)&&mode>=2;if(movem){kind='MOVEM';words=2+eaWords(mode,reg,(w&0x0040)?'L':'W');}else if((w&0xF1C0)===0x41C0){kind='LEA';words=1+eaWords(mode,reg,'L');}else if((w&0xFFC0)===0x4840&&mode!==0){kind='PEA';words=1+eaWords(mode,reg,'L');}else{kind='G4';words=1+eaWords(mode,reg,sizeFrom2((w>>6)&3));}}
 else if(g===8||g===9||g===11||g===12||g===13){kind='ALU';words=1+eaWords(mode,reg,((w>>6)&3)===2?'L':'W');}
 else if(g===10||g===15){kind='LINE';fall=false;terminal=true;}
 else if(g===14){kind='SHIFT';if(((w>>6)&3)===3)words=1+eaWords(mode,reg,'W');}
 const next=p+words*2;if(target!=null&&(target<0||target>=E.MAX))target=null;return{at:p,w,kind,words,len:words*2,next,target,fall,terminal,indirect,mode,reg};
}
function tableRefs(E){
 const T=E.dispatch,TE=T+47*4,out=[];
 const push=(p,kind,base,extra={})=>{if(p<0||p>=E.MAX)return;out.push({at:p&~1,kind,base:base>>>0,...extra});};
 for(let p=0;p+6<E.MAX;p+=2){
   const w=E.r16(p),g=w>>>12,mode=(w>>3)&7,reg=w&7;
   if((w&0xF1FF)===0x41F9&&E.r32(p+2)===T)push(p,'LEA abs.L table',T,{dst:'A'+((w>>9)&7)});
   if((w&0xF1FF)===0x41F8&&E.r16(p+2)===T)push(p,'LEA abs.W table',T,{dst:'A'+((w>>9)&7)});
   if((w&0xF1FF)===0x41FA){const b=(p+2+E.s16(E.r16(p+2)))>>>0;if(b===T)push(p,'LEA d16(PC) table',b,{dst:'A'+((w>>9)&7)});}
   if((w&0xF1FF)===0x41FB){const x=idx(E,p);if(x.pcBase>=T-8&&x.pcBase<TE+8)push(p,'LEA d8(PC,Xn) table',x.pcBase,{dst:'A'+((w>>9)&7),index:x.indexKind+x.indexReg+'.'+x.indexSize});}
   if(g===2||g===3){
     const size=g===2?'L':'W',dm=(w>>6)&7,dr=(w>>9)&7;
     if(mode===7&&reg===1&&E.r32(p+2)===T)push(p,'MOVE.'+size+' abs.L table',T,{dstMode:dm,dstReg:dr});
     if(mode===7&&reg===0&&E.r16(p+2)===T)push(p,'MOVE.'+size+' abs.W table',T,{dstMode:dm,dstReg:dr});
     if(mode===7&&reg===2){const b=(p+2+E.s16(E.r16(p+2)))>>>0;if(b===T)push(p,'MOVE.'+size+' d16(PC) table',b,{dstMode:dm,dstReg:dr});}
     if(mode===7&&reg===3){const x=idx(E,p);if(x.pcBase>=T-8&&x.pcBase<TE+8)push(p,'MOVE.'+size+' d8(PC,Xn) table',x.pcBase,{dstMode:dm,dstReg:dr,index:x.indexKind+x.indexReg+'.'+x.indexSize});}
   }
   // MOVEA.L/W sources use MOVE destination mode=1, caught above as MOVE groups; label them stronger.
   if((g===2||g===3)&&((w>>6)&7)===1){const size=g===2?'L':'W';if(mode===7&&reg===1&&E.r32(p+2)===T)push(p,'MOVEA.'+size+' abs.L table',T,{dst:'A'+((w>>9)&7)});if(mode===7&&reg===2){const b=(p+2+E.s16(E.r16(p+2)))>>>0;if(b===T)push(p,'MOVEA.'+size+' d16(PC) table',b,{dst:'A'+((w>>9)&7)});}if(mode===7&&reg===3){const x=idx(E,p);if(x.pcBase>=T-8&&x.pcBase<TE+8)push(p,'MOVEA.'+size+' d8(PC,Xn) table',x.pcBase,{dst:'A'+((w>>9)&7),index:x.indexKind+x.indexReg+'.'+x.indexSize});}}
   if(w===0x4879&&E.r32(p+2)===T)push(p,'PEA abs.L table',T);
   if(w===0x4878&&E.r16(p+2)===T)push(p,'PEA abs.W table',T);
   if(w===0x487A){const b=(p+2+E.s16(E.r16(p+2)))>>>0;if(b===T)push(p,'PEA d16(PC) table',b);}
 }
 return [...new Map(out.map(x=>[x.at+'|'+x.kind,x])).values()];
}
function localCfg(E,start,span=0x120){
 const lo=Math.max(0,start-0x20)&~1,hi=Math.min(E.MAX,start+span),q=[start&~1],seen=new Set(),ins=[],inds=[];
 while(q.length&&seen.size<500){const p=q.shift();if(p<lo||p>=hi||(p&1)||seen.has(p))continue;seen.add(p);const d=decode(E,p);ins.push(d);if(d.indirect)inds.push(d);
   if(d.kind==='BRA'){if(d.target!=null)q.push(d.target&~1);continue;}if(d.kind==='BCC'||d.kind==='DBCC'){if(d.target!=null)q.push(d.target&~1);if(d.fall)q.push(d.next);continue;}if(d.kind==='JMP_DIRECT'){if(d.target!=null&&d.target>=lo&&d.target<hi)q.push(d.target&~1);continue;}if(d.kind==='JMP_INDIRECT'||d.terminal)continue;if(d.fall)q.push(d.next);
 }
 return{ins,inds,seen};
}
function nearbyTypeSignals(E,p){
 let off20=0,off28=0,off2a=0,doubleOps=0,shiftOps=0;
 for(let q=Math.max(0,p-0x60)&~1;q<Math.min(E.MAX,p+0x80);q+=2){const w=E.r16(q);if(q+3<E.MAX){const e=E.r16(q+2);if(e===0x0020)off20++;if(e===0x0028)off28++;if(e===0x002A)off2a++;}
   if((w&0xF000)===0xD000){const d=(w>>9)&7,sm=(w>>3)&7,sr=w&7;if(sm===0&&sr===d)doubleOps++;}
   if((w&0xF000)===0xE000)shiftOps++;
 }
 return{off20,off28,off2a,doubleOps,shiftOps};
}
function refScore(r,sig,inds){let s=0;if(r.kind.includes('d8(PC,Xn)'))s+=60;if(r.kind.startsWith('MOVEA'))s+=35;if(r.kind.startsWith('LEA'))s+=25;if(inds.length)s+=80;s+=Math.min(3,sig.off20)*20+s.sig; s+=Math.min(3,sig.doubleOps)*8+Math.min(3,sig.shiftOps)*5;return s;}
async function run(){
 stopped=false;await ensure();const E=env(),T=E.dispatch,refs=tableRefs(E);
 console.log('🧭 WOF type-dispatch upstream v1 · find real users of 47×4 handler table');
 console.log('type dispatch table',E.h(T),'..',E.h(T+47*4));
 const rows=[];
 for(let i=0;i<refs.length;i++){const r=refs[i],cfg=localCfg(E,r.at),sig=nearbyTypeSignals(E,r.at),inds=cfg.inds.map(d=>({at:E.h(d.at),kind:d.kind,form:(d.mode===6?'indexed A'+d.reg:d.mode===2?'(A'+d.reg+')':'mode'+d.mode+'/reg'+d.reg)}));let score=0;if(r.kind.includes('d8(PC,Xn)'))score+=60;if(r.kind.startsWith('MOVEA'))score+=35;if(r.kind.startsWith('LEA'))score+=25;if(inds.length)score+=80;score+=Math.min(3,sig.off20)*20+Math.min(3,sig.doubleOps)*8+Math.min(3,sig.shiftOps)*5;rows.push({...r,score,sig,inds,cfgN:cfg.seen.size});if(i%40===39)await sleep(0);}
 rows.sort((a,b)=>b.score-a.score||a.at-b.at);
 console.log('=== TYPE TABLE REFERENCE CANDIDATES ===');console.table(rows.slice(0,100).map((r,i)=>({rank:i+1,at:E.h(r.at),offline:E.off(r.at),kind:r.kind,base:E.h(r.base),index:r.index||'',dst:r.dst||'',score:r.score,cfgN:r.cfgN,indirectN:r.inds.length,typeOff20:r.sig.off20,doubleOps:r.sig.doubleOps,shiftOps:r.sig.shiftOps})));
 const indRows=[];for(const r of rows){for(const z of r.inds)indRows.push({refAt:E.h(r.at),refKind:r.kind,refScore:r.score,site:z.at,kind:z.kind,form:z.form});}
 console.log('=== UPSTREAM INDIRECT SITES REACHED FROM TABLE USERS ===');console.table(indRows.slice(0,120));
 const top=rows[0]||null,verdict={dispatchTable:E.h(T),tableRefs:rows.length,refsWithIndirect:rows.filter(x=>x.inds.length).length,upstreamIndirectSites:indRows.length,topRef:top?E.h(top.at):'',topRefKind:top?.kind||'',topRefScore:top?.score||0,topRefIndex:top?.index||'',topIndirectSite:indRows[0]?.site||'',topIndirectKind:indRows[0]?.kind||'',topIndirectForm:indRows[0]?.form||''};
 console.log('=== TYPE DISPATCH VERDICT ===');console.table([verdict]);
 if(indRows.length)console.log('🎯 找到读取 0x25DC 后可达的真实 indirect transfer；下一步围绕 top table-user 还原 type index → handler call，并向上追 target selection。');
 else if(rows.length)console.warn('⚠️ 找到 0x25DC 的代码引用，但局部 CFG 没有 indirect；下一步检查这些引用是否通过 MOVE.L handler → stack/register → RTS/共享 trampoline，或扩大上游 CFG。');
 else console.warn('⚠️ ROM 内没有常见形式的 0x25DC 代码引用；可能使用复制后的 RAM handler table/相对 offset table，下一步扫描 47 handler 地址集合的表复制/装载模式。');
 const out={version:'rom-focus-type-dispatch-v1',verdict,refs:rows,indirect:indRows};self.__WOF_ROM_FOCUS_TYPE_DISPATCH=out;return out;
}
self.WOFFOCUSTYPEDISPATCH={version:'rom-focus-type-dispatch-v1',run,stop(){stopped=true;}};
console.log('✅ WOF type-dispatch upstream v1 loaded');console.log('执行 await WOFFOCUSTYPEDISPATCH.run()');
})();