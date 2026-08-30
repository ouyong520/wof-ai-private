(()=>{
'use strict';
try{self.WOFFOCUSINDIRECT?.stop?.();}catch(_){}
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
let stopped=false;
const load=async f=>{const r=await fetch(RAW+f+'?x='+Math.random());if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);const s=await r.text();(0,eval)(s);};
async function ensure(){
  if(!self.__WOF_ROM_FOCUS_TRACE?.candidate){await load('wof_rom_focus_trace.js');await self.WOFFOCUSTRACE.run();}
  if(!self.__WOF_ROM_LOC_CACHE||!self.__WOF_ROM_FOCUS_LAST)throw new Error('ROM focus state unavailable');
}
function env(){
  const MOD=_0x515056,C=self.__WOF_ROM_LOC_CACHE,M=MOD.HEAPU8,base=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-base),DELTA=C.offlineDelta|0;
  const r8=o=>M[base+(SW?(o^1):o)]>>>0;
  const r16=o=>((r8(o)<<8)|r8(o+1))>>>0;
  const r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
  const s8=v=>v&0x80?v-0x100:v,s16=v=>v&0x8000?v-0x10000:v;
  const h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0'),off=x=>h((x-DELTA)>>>0),hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
  return{M,base,SW,MAX,DELTA,r8,r16,r32,s8,s16,h,off,hw};
}
function idxExt(E,p){
  const ext=E.r16(p+2),isA=!!(ext&0x8000),reg=(ext>>12)&7,isLong=!!(ext&0x0800),scaleBits=(ext>>9)&3,disp8=E.s8(ext&255);
  return{ext:E.hw(ext),index:(isA?'A':'D')+reg,indexKind:isA?'A':'D',indexReg:reg,indexSize:isLong?'L':'W',scaleBits,effectiveScale:1,disp8};
}
function ea(E,p,mode,reg,size='W'){
  let len=0,text='',staticAddr=null,index=null;
  if(mode===0)text='D'+reg;
  else if(mode===1)text='A'+reg;
  else if(mode===2)text='(A'+reg+')';
  else if(mode===3)text='(A'+reg+')+';
  else if(mode===4)text='-(A'+reg+')';
  else if(mode===5){const d=E.s16(E.r16(p+2));len=2;text=d+'(A'+reg+')';}
  else if(mode===6){const x=idxExt(E,p);len=2;index=x;text=x.disp8+'(A'+reg+','+x.index+'.'+x.indexSize+')';}
  else if(mode===7&&reg===0){const a=E.s16(E.r16(p+2))>>>0;len=2;staticAddr=a;text=E.h(a)+'.W';}
  else if(mode===7&&reg===1){const a=E.r32(p+2);len=4;staticAddr=a;text=E.h(a)+'.L';}
  else if(mode===7&&reg===2){const d=E.s16(E.r16(p+2)),a=p+2+d;len=2;staticAddr=a;text=E.h(a)+'(PC)';}
  else if(mode===7&&reg===3){const x=idxExt(E,p);len=2;index=x;staticAddr=p+2+x.disp8;text=x.disp8+'(PC,'+x.index+'.'+x.indexSize+')';}
  else if(mode===7&&reg===4){len=size==='L'?4:2;text='#imm';}
  else text='EA('+mode+','+reg+')';
  return{mode,reg,len,text,staticAddr,index};
}
function moveWriter(E,p,targetD){
  const w=E.r16(p),nib=w>>>12;if(nib!==1&&nib!==2&&nib!==3)return null;
  const size=nib===1?'B':nib===2?'L':'W',dstReg=(w>>9)&7,dstMode=(w>>6)&7;if(dstMode!==0||dstReg!==targetD)return null;
  const sm=(w>>3)&7,sr=w&7,src=ea(E,p,sm,sr,size),len=2+src.len;
  let imm=null;if(sm===7&&sr===4){imm=size==='L'?E.r32(p+2):E.r16(p+2);if(size==='B')imm&=255;}
  return{at:p,len,kind:'MOVE.'+size,src,text:'MOVE.'+size+' '+src.text+',D'+targetD,imm};
}
function staticAWriterAt(E,p,targetA){
  const w=E.r16(p),dst=(w>>9)&7;
  if((w&0xF1C0)===0x41C0&&dst===targetA){const sm=(w>>3)&7,sr=w&7,src=ea(E,p,sm,sr,'L');return{at:p,len:2+src.len,kind:'LEA',src,value:src.staticAddr,text:'LEA '+src.text+',A'+targetA};}
  const nib=w>>>12,dm=(w>>6)&7;if((nib===2||nib===3)&&dm===1&&dst===targetA){const size=nib===2?'L':'W',sm=(w>>3)&7,sr=w&7,src=ea(E,p,sm,sr,size);let value=null;if(sm===7&&sr===4)value=size==='L'?E.r32(p+2):(E.s16(E.r16(p+2))>>>0);return{at:p,len:2+src.len,kind:'MOVEA.'+size,src,value,text:'MOVEA.'+size+' '+src.text+',A'+targetA};}
  return null;
}
function staticAValueBefore(E,site,reg,back=0x180){
  const rows=[];for(let p=Math.max(0,site-back)&~1;p<site;p+=2){const z=staticAWriterAt(E,p,reg);if(z)rows.push(z);}
  rows.sort((a,b)=>b.at-a.at);return rows;
}
function indexOps(E,site,x,back=0x120){
  if(x.indexKind!=='D')return[];const d=x.indexReg,out=[];
  for(let p=Math.max(0,site-back)&~1;p<site;p+=2){const w=E.r16(p),m=moveWriter(E,p,d);if(m){out.push({...m,distance:site-p});continue;}
    if((w&0xF100)===0x7000&&((w>>9)&7)===d)out.push({at:p,len:2,kind:'MOVEQ',text:'MOVEQ #'+E.s8(w&255)+',D'+d,imm:E.s8(w&255),distance:site-p});
    else if((w&0xFFC0)===(0x4200|(d&7))){out.push({at:p,len:2,kind:'CLR?',text:'CLR D'+d,distance:site-p});}
    else if((w&0xFFF8)===(0x4880|d))out.push({at:p,len:2,kind:'EXT.W',text:'EXT.W D'+d,distance:site-p});
    else if((w&0xFFF8)===(0x48C0|d))out.push({at:p,len:2,kind:'EXT.L',text:'EXT.L D'+d,distance:site-p});
    else if((w&0xFFF8)===(0x4840|d))out.push({at:p,len:2,kind:'SWAP',text:'SWAP D'+d,distance:site-p});
    else if((w&0xF000)===0xD000&&((w>>9)&7)===d&&((w>>6)&7)<=2){const sm=(w>>3)&7,sr=w&7;if(sm===0)out.push({at:p,len:2,kind:'ADD',text:'ADD '+('D'+sr)+',D'+d,double:sr===d,distance:site-p});}
    else if((w&0xF000)===0x9000&&((w>>9)&7)===d&&((w>>6)&7)<=2){const sm=(w>>3)&7,sr=w&7;if(sm===0)out.push({at:p,len:2,kind:'SUB',text:'SUB D'+sr+',D'+d,distance:site-p});}
    else if((w&0xF000)===0xE000&&(w&7)===d&&((w>>6)&3)!==3)out.push({at:p,len:2,kind:'SHIFT/ROT',text:'SHIFT/ROT D'+d+' op='+E.hw(w),distance:site-p});
  }
  return out.sort((a,b)=>a.distance-b.distance);
}
function resolveIndexedMoveTable(E,site,jx,a2value,ops){
  if(jx.indexKind!=='D'||a2value==null)return null;
  const jumpBase=(a2value+jx.disp8)>>>0;
  const lastMove=ops.find(z=>z.kind==='MOVE.W'&&z.src?.index);
  if(!lastMove)return{jumpBase:E.h(jumpBase),reason:'index D register last writer is not an indexed MOVE.W',rows:[]};
  const src=lastMove.src,ix=src.index;let tableBase=null,baseWhy='';
  if(src.mode===7&&src.reg===3){tableBase=src.staticAddr>>>0;baseWhy='PC indexed';}
  else if(src.mode===6){const ar=src.reg,av=staticAValueBefore(E,lastMove.at,ar).find(z=>z.value!=null);if(av){tableBase=(av.value+ix.disp8)>>>0;baseWhy='A'+ar+' indexed from '+E.h(av.value);}}
  if(tableBase==null)return{jumpBase:E.h(jumpBase),writer:E.h(lastMove.at),writerText:lastMove.text,reason:'indexed MOVE.W table base is dynamic/unresolved',rows:[]};
  const rows=[];for(let i=0;i<64;i++){const a=tableBase+i*2,raw=E.r16(a),ofs=E.s16(raw),t=(jumpBase+ofs)>>>0;if(t<E.MAX&&(t&1)===0)rows.push({i,tableAt:E.h(a),raw:E.hw(raw),offset:ofs,target:E.h(t),offlineTarget:E.off(t),firstOp:E.hw(E.r16(t))});}
  return{jumpBase:E.h(jumpBase),writer:E.h(lastMove.at),writerText:lastMove.text,tableBase:E.h(tableBase),baseWhy,sourceIndex:ix.index+'.'+ix.indexSize,rows};
}
function rawWindow(E,site,before=0x50,after=0x10){const rows=[];for(let p=Math.max(0,site-before)&~1;p<Math.min(E.MAX,site+after);p+=2)rows.push({at:E.h(p),offline:E.off(p),word:E.hw(E.r16(p)),mark:p===site?'<<< JMP':''});return rows;}
async function run(){
  stopped=false;await ensure();const E=env(),T=self.__WOF_ROM_FOCUS_TRACE;
  if((T.candidate?.directTypePaths??-1)!==0)console.warn('directTypePaths != 0；当前间接路线条件发生变化');
  const sites=T.indirectReachable||[];if(!sites.length)throw new Error('trace 没有 reachable indirect site');
  const reports=[];
  for(const z of sites){
    const site=parseInt(z.at,16),op=E.r16(site),baseReg=op&7,jx=idxExt(E,site),aRows=staticAValueBefore(E,site,baseReg),aStatic=aRows.find(q=>q.value!=null)||null,ops=indexOps(E,site,jx),resolved=resolveIndexedMoveTable(E,site,jx,aStatic?.value??null,ops);
    console.log('🧩 ROM indirect dispatch dataflow v2');
    console.log('=== INDIRECT SITE ===');console.table([{func:z.func,site:E.h(site),offline:E.off(site),opcode:E.hw(op),base:'A'+baseReg,index:jx.index,indexSize:jx.indexSize,disp8:jx.disp8,extension:jx.ext,scaleBits:jx.scaleBits,effective68000Scale:1}]);
    console.log('=== BASE REGISTER WRITERS (nearest first) ===');console.table(aRows.slice(0,30).map(q=>({at:E.h(q.at),offline:E.off(q.at),kind:q.kind,text:q.text,value:q.value==null?'dynamic':E.h(q.value),distance:site-q.at})));
    console.log('=== INDEX REGISTER DATAFLOW HINTS (nearest first) ===');console.table(ops.slice(0,40).map(q=>({at:E.h(q.at),offline:E.off(q.at),kind:q.kind,text:q.text,distance:q.distance})));
    console.log('=== DISPATCH RESOLUTION ===');console.table([{jumpBase:resolved?.jumpBase||'',tableBase:resolved?.tableBase||'',writer:resolved?.writer||'',writerText:resolved?.writerText||'',baseWhy:resolved?.baseWhy||'',reason:resolved?.reason||'',targetCount:resolved?.rows?.length||0}]);
    console.log('=== RESOLVED JUMP TABLE TARGETS ===');console.table((resolved?.rows||[]).slice(0,64));
    console.log('=== RAW WORD WINDOW ===');console.table(rawWindow(E,site));
    reports.push({site:E.h(site),func:z.func,baseReg:'A'+baseReg,index:jx,aWriters:aRows.map(q=>({...q,at:E.h(q.at),value:q.value==null?null:E.h(q.value)})),indexOps:ops.map(q=>({...q,at:E.h(q.at)})),resolved});
  }
  const out={version:'rom-focus-indirect-v2-dataflow',reports};self.__WOF_ROM_FOCUS_INDIRECT=out;return out;
}
self.WOFFOCUSINDIRECT={version:'rom-focus-indirect-v2-dataflow',run,stop(){stopped=true;}};
console.log('✅ WOF ROM focus indirect v2 loaded · A-base/index dataflow + jump-table resolution');
console.log('执行 await WOFFOCUSINDIRECT.run()');
})();