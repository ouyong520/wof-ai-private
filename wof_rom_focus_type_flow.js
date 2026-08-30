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
function eaInfo(E,p,mode,reg,size='L',extOff=2){
  let len=0,text='',baseReg=null,indexReg=null,indexKind=null,staticAddr=null;
  if(mode===0)text='D'+reg;
  else if(mode===1)text='A'+reg;
  else if(mode===2){text='(A'+reg+')';baseReg='A'+reg;}
  else if(mode===3){text='(A'+reg+')+';baseReg='A'+reg;}
  else if(mode===4){text='-(A'+reg+')';baseReg='A'+reg;}
  else if(mode===5){const d=E.s16(E.r16(p+extOff));len=2;text=d+'(A'+reg+')';baseReg='A'+reg;}
  else if(mode===6){const xw=E.r16(p+extOff),x={kind:(xw&0x8000)?'A':'D',reg:(xw>>12)&7,size:(xw&0x0800)?'L':'W',disp:E.s8(xw&255)};len=2;text=x.disp+'(A'+reg+','+x.kind+x.reg+'.'+x.size+')';baseReg='A'+reg;indexKind=x.kind;indexReg=x.kind+x.reg;}
  else if(mode===7&&reg===0){staticAddr=E.s16(E.r16(p+extOff))>>>0;len=2;text=E.h(staticAddr)+'.W';}
  else if(mode===7&&reg===1){staticAddr=E.r32(p+extOff);len=4;text=E.h(staticAddr)+'.L';}
  else if(mode===7&&reg===2){staticAddr=(p+2+E.s16(E.r16(p+extOff)))>>>0;len=2;text=E.h(staticAddr)+'(PC)';}
  else if(mode===7&&reg===3){const xw=E.r16(p+extOff),x={kind:(xw&0x8000)?'A':'D',reg:(xw>>12)&7,size:(xw&0x0800)?'L':'W',disp:E.s8(xw&255)};staticAddr=(p+2+x.disp)>>>0;len=2;text=x.disp+'(PC,'+x.kind+x.reg+'.'+x.size+')';indexKind=x.kind;indexReg=x.kind+x.reg;}
  else if(mode===7&&reg===4){len=size==='L'?4:2;text='#imm';}
  else text='EA('+mode+','+reg+')';
  return{mode,reg,len,text,baseReg,indexReg,indexKind,staticAddr};
}
function moveInfo(E,p){
  const w=E.r16(p),g=w>>>12;if(g!==1&&g!==2&&g!==3)return null;const size=g===1?'B':g===2?'L':'W',sm=(w>>3)&7,sr=w&7,dm=(w>>6)&7,dr=(w>>9)&7;
  const src=eaInfo(E,p,sm,sr,size,2),dstOff=2+src.len,dst=eaInfo(E,p,dm,dr,size,dstOff),len=2+src.len+dst.len;
  const kind=dm===1?'MOVEA.'+size:'MOVE.'+size;
  return{w,size,sm,sr,dm,dr,src,dst,len,kind,text:kind+' '+src.text+','+dst.text};
}
function directTarget(E,p,w){
  const mode=(w>>3)&7,reg=w&7;
  if(mode===7&&reg===0)return E.s16(E.r16(p+2))>>>0;
  if(mode===7&&reg===1)return E.r32(p+2)>>>0;
  if(mode===7&&reg===2)return (p+2+E.s16(E.r16(p+2)))>>>0;
  return null;
}
function decode(E,p){
  const w=E.r16(p),g=w>>>12,mode=(w>>3)&7,reg=w&7;let len=2,kind='OP',target=null,fall=true,terminal=false,text=E.hw(w),move=null,call=false,jump=false;
  if(w===0x4E75||w===0x4E73||w===0x4E77){kind=w===0x4E75?'RTS':w===0x4E73?'RTE':'RTR';fall=false;terminal=true;text=kind;}
  else if(w===0x4E72){kind='STOP';len=4;fall=false;terminal=true;text='STOP';}
  else if((w&0xFFC0)===0x4E80){len=2+eaWords(mode,reg,'L')*2;target=directTarget(E,p,w);kind=target==null?'JSR_INDIRECT':'JSR_DIRECT';call=true;text=kind+' '+eaInfo(E,p,mode,reg,'L').text;}
  else if((w&0xFFC0)===0x4EC0){len=2+eaWords(mode,reg,'L')*2;target=directTarget(E,p,w);kind=target==null?'JMP_INDIRECT':'JMP_DIRECT';jump=true;fall=false;text=kind+' '+eaInfo(E,p,mode,reg,'L').text;}
  else if(g===6){const cc=(w>>8)&15,d=w&255;len=d===0?4:2;target=d===0?p+2+E.s16(E.r16(p+2)):p+2+E.s8(d);kind=cc===0?'BRA':cc===1?'BSR':'BCC';if(cc===0)fall=false;if(cc===1)call=true;text=kind;}
  else if(g===1||g===2||g===3){move=moveInfo(E,p);len=move.len;kind=move.kind;text=move.text;}
  else if(g===5){const sz=(w>>6)&3;if(sz===3&&mode===1){kind='DBCC';len=4;target=p+2+E.s16(E.r16(p+2));}else{kind=sz===3?'SCC':'ADDQ/SUBQ';len=2+eaWords(mode,reg,sz===3?'B':sz===2?'L':sz===1?'W':'B')*2;}}
  else if(g===7){kind='MOVEQ';text='MOVEQ';}
  else if(g===0){
    if([0x003C,0x007C,0x023C,0x027C,0x0A3C,0x0A7C].includes(w)){kind='IMM_SR';len=4;}
    else if((w&0xF138)===0x0108){kind='MOVEP';len=4;}
    else if((w&0xFF00)===0x0800){kind='BIT_IMM';len=4+eaWords(mode,reg,'B')*2;}
    else if((w&0xF100)===0x0100){kind='BIT_DYN';len=2+eaWords(mode,reg,'B')*2;}
    else{const op=(w>>8)&15,sz=(w>>6)&3;if([0,2,4,6,10,12].includes(op)){const s=sz===2?'L':sz===1?'W':'B';kind='IMM';len=2+(s==='L'?4:2)+eaWords(mode,reg,s)*2;}else kind='G0';}
  }
  else if(g===4){
    if((w&0xFFF8)===0x4E50){kind='LINK';len=4;}
    else if((w&0xFFF8)===0x4E58){kind='UNLK';}
    else if((w&0xFB80)===0x4880&&mode>=2){kind='MOVEM';len=4+eaWords(mode,reg,(w&0x40)?'L':'W')*2;}
    else if((w&0xF1C0)===0x41C0){kind='LEA';len=2+eaWords(mode,reg,'L')*2;text='LEA '+eaInfo(E,p,mode,reg,'L').text+',A'+((w>>9)&7);}
    else if((w&0xFFC0)===0x4840&&mode!==0){kind='PEA';len=2+eaWords(mode,reg,'L')*2;text='PEA '+eaInfo(E,p,mode,reg,'L').text;}
    else if((w&0xF1F8)===0xC140||(w&0xF1F8)===0xC148||(w&0xF1F8)===0xC188){kind='EXG';}
    else{kind='G4';len=2+eaWords(mode,reg,((w>>6)&3)===2?'L':'W')*2;}
  }
  else if(g===8){kind=(w&0xF1F0)===0x8100?'SBCD':'OR';if(kind==='OR')len=2+eaWords(mode,reg,((w>>6)&3)===2?'L':'W')*2;}
  else if(g===9){kind=(w&0xF130)===0x9100?'SUBX':(((w>>6)&7)===3||((w>>6)&7)===7?'SUBA':'SUB');if(kind==='SUB')len=2+eaWords(mode,reg,((w>>6)&3)===2?'L':'W')*2;else if(kind==='SUBA')len=2+eaWords(mode,reg,((w>>6)&1)?'L':'W')*2;}
  else if(g===11){kind=(w&0xF138)===0xB108?'CMPM':(((w>>6)&7)===3||((w>>6)&7)===7?'CMPA':'CMP/EOR');if(kind==='CMP/EOR')len=2+eaWords(mode,reg,((w>>6)&3)===2?'L':'W')*2;else if(kind==='CMPA')len=2+eaWords(mode,reg,((w>>6)&1)?'L':'W')*2;}
  else if(g===12){const exg=(w&0xF1F8)===0xC140||(w&0xF1F8)===0xC148||(w&0xF1F8)===0xC188,abcd=(w&0xF1F0)===0xC100;kind=exg?'EXG':abcd?'ABCD':'AND/MUL';if(!exg&&!abcd)len=2+eaWords(mode,reg,((w>>6)&3)===2?'L':'W')*2;}
  else if(g===13){kind=(w&0xF130)===0xD100?'ADDX':(((w>>6)&7)===3||((w>>6)&7)===7?'ADDA':'ADD');if(kind==='ADD')len=2+eaWords(mode,reg,((w>>6)&3)===2?'L':'W')*2;else if(kind==='ADDA')len=2+eaWords(mode,reg,((w>>6)&1)?'L':'W')*2;}
  else if(g===14){kind='SHIFT';if(((w>>6)&3)===3)len=2+eaWords(mode,reg,'W')*2;}
  else if(g===10||g===15){kind='LINE';terminal=true;fall=false;}
  const next=p+len;if(target!=null&&(target<0||target>=E.MAX))target=null;return{at:p,w,len,next,kind,target,fall,terminal,text,mode,reg,move,call,jump};
}
function findStart(E,at){for(let p=at&~1;p>=Math.max(0,at-0x380);p-=2){const w=E.r16(p);if((w&0xFFF8)===0x4E50||w===0x48E7)return p;if(w===0x4E75||w===0x4E73||w===0x4E77)return p+2;}return Math.max(0,(at-0x120)&~1);}
function boundaryCFG(E,start,cap=0x1200){const hi=Math.min(E.MAX,start+cap),q=[start&~1],seen=new Set(),rows=[];while(q.length&&seen.size<7000){const p=q.shift();if(p<start||p>=hi||(p&1)||seen.has(p))continue;seen.add(p);const d=decode(E,p);rows.push(d);if(d.kind==='BRA'){if(d.target!=null)q.push(d.target&~1);continue;}if(d.kind==='BCC'||d.kind==='DBCC'){q.push(d.next);if(d.target!=null)q.push(d.target&~1);continue;}if(d.kind==='JMP_DIRECT'){if(d.target!=null&&d.target>=start&&d.target<hi)q.push(d.target&~1);continue;}if(d.kind==='JMP_INDIRECT'||d.terminal)continue;q.push(d.next);}return{seen,rows};}
function regName(mode,reg){return mode===0?'D'+reg:mode===1?'A'+reg:null;}
function eaTainted(ea,taint){return!!((ea.baseReg&&taint.has(ea.baseReg))||(ea.indexReg&&taint.has(ea.indexReg)));}
function stateKey(s){return s.pc+'|'+[...s.taint].sort().join(',')+'|'+(s.retSlot?1:0)+'|'+s.depth;}
function cloneState(s,patch={}){return{pc:patch.pc??s.pc,taint:new Set(patch.taint??s.taint),retSlot:patch.retSlot??s.retSlot,depth:patch.depth??s.depth,path:patch.path??s.path,origin:patch.origin??s.origin};}
function pathText(E,path){return path.slice(-14).map(E.h).join(' → ');}
function analyzeFrom(E,startPc,seedReg,origin,maxDepth=4){
  const q=[{pc:startPc&~1,taint:new Set([seedReg]),retSlot:false,depth:0,path:[startPc&~1],origin}],seen=new Set();
  const transfers=[],calls=[],stores=[],returns=[],aliases=[],kills=[],decoded=[];let states=0;
  const push=s=>{if(s.pc>=0&&s.pc<E.MAX&&(s.pc&1)===0&&s.path.length<260)q.push(s);};
  while(q.length&&states<18000){if(stopped)break;const s=q.shift(),key=stateKey(s);if(seen.has(key))continue;seen.add(key);states++;const d=decode(E,s.pc);decoded.push(d.at);const t=new Set(s.taint),path=[...s.path,d.at];
    const record=(arr,obj)=>arr.push({origin:E.h(origin),at:E.h(d.at),offline:E.off(d.at),depth:s.depth,taint:[...t].sort().join(','),path:pathText(E,path),...obj});
    // Control-transfer using tainted address/index register.
    if(d.kind==='JSR_INDIRECT'||d.kind==='JMP_INDIRECT'){
      const ea=eaInfo(E,d.at,d.mode,d.reg,'L'),hit=eaTainted(ea,t);
      if(hit){record(transfers,{kind:d.kind,text:d.text,form:ea.text,terminal:d.kind==='JMP_INDIRECT'});if(d.kind==='JMP_INDIRECT')continue;}
    }
    // Direct calls are important: a fixed shared executor may consume A4 inside the callee.
    if((d.kind==='JSR_DIRECT'||d.kind==='BSR')&&d.target!=null){
      if(t.size){record(calls,{kind:d.kind,target:E.h(d.target),text:'tainted regs passed to direct callee'});if(s.depth<maxDepth)push({pc:d.target&~1,taint:new Set(t),retSlot:false,depth:s.depth+1,path:[...path,d.target&~1],origin});}
      push({pc:d.next,taint:new Set(t),retSlot:s.retSlot,depth:s.depth,path,origin});continue;
    }
    if(d.kind==='JMP_DIRECT'&&d.target!=null){if(t.size&&s.depth<maxDepth){record(calls,{kind:'JMP_DIRECT_TAIL',target:E.h(d.target),text:'tainted regs passed to direct tail target'});push({pc:d.target&~1,taint:new Set(t),retSlot:s.retSlot,depth:s.depth+1,path:[...path,d.target&~1],origin});}continue;}
    if(d.kind==='RTS'||d.kind==='RTE'||d.kind==='RTR'){
      if(s.retSlot)record(transfers,{kind:'RTS_STACK_TRAMPOLINE',text:'tainted handler is on top of return stack',form:'A7 return slot',terminal:true});
      if(t.size)record(returns,{kind:d.kind,text:'tainted handler register(s) survive to return'});continue;
    }
    if(d.kind==='BRA'){if(d.target!=null)push({pc:d.target&~1,taint:t,retSlot:s.retSlot,depth:s.depth,path,origin});continue;}
    if(d.kind==='BCC'||d.kind==='DBCC'){push({pc:d.next,taint:new Set(t),retSlot:s.retSlot,depth:s.depth,path,origin});if(d.target!=null)push({pc:d.target&~1,taint:new Set(t),retSlot:s.retSlot,depth:s.depth,path,origin});continue;}
    if(d.terminal)continue;
    let retSlot=s.retSlot;
    // MOVE / MOVEA dataflow.
    if(d.move){const m=d.move,srcReg=regName(m.sm,m.sr),dstReg=regName(m.dm,m.dr),srcT=!!(srcReg&&t.has(srcReg));
      if(dstReg){const was=t.has(dstReg);if(srcT){t.add(dstReg);if(dstReg!==srcReg)record(aliases,{kind:'REG_ALIAS',text:m.text,from:srcReg,to:dstReg});}else{t.delete(dstReg);if(was)record(kills,{kind:'REG_KILL',text:m.text,reg:dstReg});}}
      else if(srcT){const stack=m.dr===7&&(m.dm===2||m.dm===4);record(stores,{kind:stack?'TAINT_TO_STACK':'TAINT_TO_MEMORY',text:m.text,source:srcReg,dest:m.dst.text});if(stack)retSlot=true;}
      if(!srcT&&eaTainted(m.src,t)&&dstReg)record(stores,{kind:'LOAD_THROUGH_TAINTED_PTR',text:m.text,source:m.src.text,dest:dstReg});
    }
    // LEA based on a tainted address register propagates a derived handler pointer.
    if(d.kind==='LEA'){const dst='A'+((d.w>>9)&7),ea=eaInfo(E,d.at,d.mode,d.reg,'L');const was=t.has(dst);if(eaTainted(ea,t)){t.add(dst);record(aliases,{kind:'LEA_ALIAS',text:d.text,from:ea.baseReg||ea.indexReg||'',to:dst});}else{t.delete(dst);if(was)record(kills,{kind:'REG_KILL',text:d.text,reg:dst});}}
    // PEA (A-tainted) pushes the effective address itself and can feed RTS trampoline.
    if(d.kind==='PEA'){const ea=eaInfo(E,d.at,d.mode,d.reg,'L');if(eaTainted(ea,t)){record(stores,{kind:'PEA_TAINT_TO_STACK',text:d.text,source:ea.text,dest:'-(A7)'});retSlot=true;}}
    // EXG propagates/switches taint exactly between the two participating registers.
    if(d.kind==='EXG'){
      const w=d.w,rx=(w>>9)&7,ry=w&7;let a=null,b=null;if((w&0xF1F8)===0xC140){a='D'+rx;b='D'+ry;}else if((w&0xF1F8)===0xC148){a='A'+rx;b='A'+ry;}else if((w&0xF1F8)===0xC188){a='D'+rx;b='A'+ry;}
      if(a&&b){const ta=t.has(a),tb=t.has(b);if(ta)t.add(b);else t.delete(b);if(tb)t.add(a);else t.delete(a);if(ta||tb)record(aliases,{kind:'EXG_TAINT',text:'EXG '+a+','+b,from:ta?a:b,to:ta?b:a});}
    }
    // MOVEM restore can kill a tainted register; MOVEM save reveals preserved function pointer state.
    if(d.kind==='MOVEM'){const w=d.w,mask=E.r16(d.at+2),memToRegs=!!(w&0x0400),regs=[];for(let i=0;i<16;i++)if(mask&(1<<i))regs.push(i<8?'D'+i:'A'+(i-8));if(memToRegs){for(const r of regs)if(t.has(r)){t.delete(r);record(kills,{kind:'MOVEM_RESTORE_KILL',text:'MOVEM restores '+r,reg:r});}}else{const hit=regs.filter(r=>t.has(r));if(hit.length)record(stores,{kind:'MOVEM_TAINT_SAVE',text:'MOVEM saves '+hit.join(','),source:hit.join(','),dest:eaInfo(E,d.at,d.mode,d.reg,(w&0x40)?'L':'W',4).text});}}
    // ADDA/SUBA keep a tainted address value derived; do not kill it.
    if(d.kind==='ADDA'||d.kind==='SUBA'){const dst='A'+((d.w>>9)&7),srcMode=(d.w>>3)&7,srcReg=d.w&7,srcName=regName(srcMode,srcReg);if(srcName&&t.has(srcName)&&!t.has(dst)){t.add(dst);record(aliases,{kind:d.kind+'_ALIAS',text:d.kind+' '+srcName+','+dst,from:srcName,to:dst});}}
    // MOVEQ fully replaces Dn.
    if(d.kind==='MOVEQ'){const dst='D'+((d.w>>9)&7);if(t.delete(dst))record(kills,{kind:'MOVEQ_KILL',text:'MOVEQ -> '+dst,reg:dst});}
    push({pc:d.next,taint:t,retSlot,depth:s.depth,path,origin});
  }
  const uniq=a=>[...new Map(a.map(x=>[(x.at||'')+'|'+(x.kind||'')+'|'+(x.target||'')+'|'+(x.text||''),x])).values()];
  return{states,transfers:uniq(transfers),calls:uniq(calls),stores:uniq(stores),returns:uniq(returns),aliases:uniq(aliases),kills:uniq(kills),decodedN:new Set(decoded).size};
}
async function run(){
  stopped=false;await ensure();const E=env(),TD=self.__WOF_ROM_FOCUS_TYPE_DISPATCH;
  const refs=[...new Map((TD.refs||[]).filter(x=>(x.dstMode===1&&x.dstReg===4)||x.dst==='A4').map(x=>[x.at,x])).values()];
  console.log('🧬 WOF type handler flow v2 · full CFG + direct-callee A4 taint');
  const reports=[];
  for(const r of refs){const at=Number(r.at),start=findStart(E,at),bcfg=boundaryCFG(E,start),onBoundary=bcfg.seen.has(at),d=decode(E,at),m=d.move;let tableLoad=false,index='',tableBase='';
    if(m&&m.dm===1&&m.dr===4&&m.sm===7&&m.sr===3&&m.src.staticAddr!=null){tableLoad=true;index=m.src.indexReg?m.src.indexReg+'.'+(idx(E,at).size):'';tableBase=E.h(m.src.staticAddr);}
    const flow=onBoundary&&m?analyzeFrom(E,d.next,'A4',at,4):{states:0,transfers:[],calls:[],stores:[],returns:[],aliases:[],kills:[],decodedN:0};
    const z={ref:E.h(at),offline:E.off(at),funcStart:E.h(start),onBoundary,decoded:d.text,tableLoad,tableBase,index,flow};reports.push(z);
    console.log('\n=== A4 TABLE LOAD '+E.h(at)+' ===');console.table([{ref:z.ref,offline:z.offline,funcStart:z.funcStart,onBoundary,decoded:z.decoded,tableBase,index,states:flow.states,decodedInstructions:flow.decodedN}]);
    console.log('=== TAINTED DIRECT CALLS / TAIL TARGETS ===');console.table(flow.calls.slice(0,120));
    console.log('=== A4/ALIAS CONTROL TRANSFERS ===');console.table(flow.transfers.slice(0,120));
    console.log('=== A4/ALIAS MEMORY OR STACK STORES ===');console.table(flow.stores.slice(0,120));
    console.log('=== A4/ALIAS REGISTER PROPAGATION ===');console.table(flow.aliases.slice(0,120));
    console.log('=== RETURNS WITH LIVE HANDLER ===');console.table(flow.returns.slice(0,80));
  }
  const valid=reports.filter(x=>x.onBoundary),transfers=valid.flatMap(x=>x.flow.transfers),calls=valid.flatMap(x=>x.flow.calls),stores=valid.flatMap(x=>x.flow.stores),returns=valid.flatMap(x=>x.flow.returns),aliases=valid.flatMap(x=>x.flow.aliases);
  const tramp=transfers.filter(x=>x.kind==='RTS_STACK_TRAMPOLINE'),indirect=transfers.filter(x=>x.kind==='JSR_INDIRECT'||x.kind==='JMP_INDIRECT');
  const verdict={dispatchTable:E.h(E.dispatch),a4Refs:refs.length,validBoundaryRefs:valid.length,falseRefs:refs.length-valid.length,taintedDirectCalls:calls.length,indirectHandlerTransfers:indirect.length,rtsStackTrampolines:tramp.length,handlerStores:stores.length,returnsLive:returns.length,aliasOps:aliases.length,topTransferAt:transfers[0]?.at||'',topTransferKind:transfers[0]?.kind||'',topTransferText:transfers[0]?.text||'',topCallTarget:calls[0]?.target||'',topStoreAt:stores[0]?.at||'',topStoreKind:stores[0]?.kind||''};
  console.log('=== TYPE HANDLER FLOW VERDICT V2 ===');console.table([verdict]);
  if(indirect.length||tramp.length)console.log('🎯 已找到 0x25DC handler 的真实控制转移：下一步固定 transfer path，并向前追 type/state/target selector。');
  else if(calls.length)console.warn('🧭 A4 handler 被带入固定 direct callees，但当前 4 层内未消费为 transfer；下一步只围绕 topCallTarget 扩大共享 executor 数据流。');
  else if(stores.length)console.warn('🧭 A4 handler 被写入 stack/RAM 而不是立即执行；下一步追 topStoreAt 的目标位置及后续读取/执行。');
  else if(returns.length)console.warn('🧭 A4 handler 沿完整 CFG 返回；下一步追 caller-of-caller 的 A4 live range。');
  else console.warn('⚠️ 两个真实 A4 load 在完整 CFG/4层 direct callee 内仍无消费；下一步重新判断 0x25DC 表是否是执行 handler 表，检查其 47 entries 的实际用途和引用语义。');
  const out={version:'rom-focus-type-flow-v2-cfg-callee-taint',verdict,reports};self.__WOF_ROM_FOCUS_TYPE_FLOW=out;return out;
}
self.WOFFOCUSTYPEFLOW={version:'rom-focus-type-flow-v2-cfg-callee-taint',run,stop(){stopped=true;}};
console.log('✅ WOF ROM focus type-flow v2 loaded · full CFG + direct-callee A4 taint');
console.log('执行 await WOFFOCUSTYPEFLOW.run()');
})();