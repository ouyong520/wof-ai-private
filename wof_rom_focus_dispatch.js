(()=>{
'use strict';
try{self.WOFFOCUSDISPATCH?.stop?.();}catch(_){}
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let stopped=false;
const load=async f=>{const r=await fetch(RAW+f+'?x='+Math.random());if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);const s=await r.text();(0,eval)(s);};
async function ensure(){
  if(!self.__WOF_ROM_FOCUS_TRACE?.candidate){await load('wof_rom_focus_trace.js');await self.WOFFOCUSTRACE.run();}
  if(!self.__WOF_ROM_LOC_CACHE||!self.__WOF_ROM_FOCUS_LAST)throw new Error('ROM focus state unavailable');
}
function env(){
  const MOD=_0x515056,C=self.__WOF_ROM_LOC_CACHE,L=self.__WOF_ROM_FOCUS_LAST,M=MOD.HEAPU8,base=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-base),DELTA=C.offlineDelta|0;
  const r8=o=>M[base+(SW?(o^1):o)]>>>0;
  const r16=o=>((r8(o)<<8)|r8(o+1))>>>0;
  const r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
  const s8=v=>v&0x80?v-0x100:v,s16=v=>v&0x8000?v-0x10000:v;
  const h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0'),off=x=>h((x-DELTA)>>>0),hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
  return{L,M,base,SW,MAX,DELTA,r8,r16,r32,s8,s16,h,off,hw};
}
function idxExt(E,p){const x=E.r16(p+2);return{ext:E.hw(x),indexKind:(x&0x8000)?'A':'D',indexReg:(x>>12)&7,indexSize:(x&0x0800)?'L':'W',disp8:E.s8(x&255)};}
function ea(E,p,mode,reg,size='L'){
  let len=0,text='',staticAddr=null,index=null;
  if(mode===0)text='D'+reg;else if(mode===1)text='A'+reg;else if(mode===2)text='(A'+reg+')';else if(mode===3)text='(A'+reg+')+';else if(mode===4)text='-(A'+reg+')';
  else if(mode===5){const d=E.s16(E.r16(p+2));len=2;text=d+'(A'+reg+')';}
  else if(mode===6){index=idxExt(E,p);len=2;text=index.disp8+'(A'+reg+','+index.indexKind+index.indexReg+'.'+index.indexSize+')';}
  else if(mode===7&&reg===0){staticAddr=E.s16(E.r16(p+2))>>>0;len=2;text=E.h(staticAddr)+'.W';}
  else if(mode===7&&reg===1){staticAddr=E.r32(p+2);len=4;text=E.h(staticAddr)+'.L';}
  else if(mode===7&&reg===2){const d=E.s16(E.r16(p+2));staticAddr=p+2+d;len=2;text=E.h(staticAddr)+'(PC)';}
  else if(mode===7&&reg===3){index=idxExt(E,p);staticAddr=p+2+index.disp8;len=2;text=index.disp8+'(PC,'+index.indexKind+index.indexReg+'.'+index.indexSize+')';}
  else if(mode===7&&reg===4){len=size==='L'?4:2;text='#imm';}
  else text='EA('+mode+','+reg+')';
  return{mode,reg,len,text,staticAddr,index};
}
function directAt(E,p){const w=E.r16(p);let t=null,k='',len=2;if(w===0x4EB8){t=E.s16(E.r16(p+2))>>>0;k='JSR abs.W';len=4;}else if(w===0x4EB9){t=E.r32(p+2);k='JSR abs.L';len=6;}else if(w===0x4EBA){t=p+2+E.s16(E.r16(p+2));k='JSR PC';len=4;}else if(w===0x4EF8){t=E.s16(E.r16(p+2))>>>0;k='JMP abs.W';len=4;}else if(w===0x4EF9){t=E.r32(p+2);k='JMP abs.L';len=6;}else if(w===0x4EFA){t=p+2+E.s16(E.r16(p+2));k='JMP PC';len=4;}else if((w&0xFF00)===0x6100){const d=w&255;t=d===0?p+2+E.s16(E.r16(p+2)):p+2+E.s8(d);k='BSR';len=d===0?4:2;}if(t==null||t<0||t>=E.MAX)return null;return{at:p,target:t&~1,kind:k,len};}
function isRet(w){return w===0x4E75||w===0x4E73||w===0x4E77;}
function findFuncStart(E,addr){addr&=~1;for(let p=addr;p>=Math.max(0,addr-0x280);p-=2){const w=E.r16(p);if((w&0xFFF8)===0x4E50||w===0x48E7)return p;if(isRet(w))return p+2;}return Math.max(0,(addr-0x100)&~1);}
function findFuncEnd(E,start){for(let p=start;p<Math.min(E.MAX,start+0xA00);p+=2)if(isRet(E.r16(p)))return p+2;return Math.min(E.MAX,start+0x800);}
function aWriterAt(E,p,targetA){
  const w=E.r16(p),dst=(w>>9)&7;
  if((w&0xF1C0)===0x41C0&&dst===targetA){const sm=(w>>3)&7,sr=w&7,src=ea(E,p,sm,sr,'L');return{at:p,kind:'LEA',src,text:'LEA '+src.text+',A'+targetA};}
  const nib=w>>>12,dm=(w>>6)&7;if((nib===2||nib===3)&&dm===1&&dst===targetA){const size=nib===2?'L':'W',sm=(w>>3)&7,sr=w&7,src=ea(E,p,sm,sr,size);return{at:p,kind:'MOVEA.'+size,size,src,text:'MOVEA.'+size+' '+src.text+',A'+targetA};}
  return null;
}
function nearestAWriter(E,start,site,reg){const a=[];for(let p=start&~1;p<site;p+=2){const z=aWriterAt(E,p,reg);if(z)a.push(z);}return a.sort((x,y)=>y.at-x.at)[0]||null;}
function dWriterAt(E,p,d){const w=E.r16(p),n=w>>>12;if(n===1||n===2||n===3){const dm=(w>>6)&7,dr=(w>>9)&7;if(dm===0&&dr===d){const size=n===1?'B':n===2?'L':'W',sm=(w>>3)&7,sr=w&7,src=ea(E,p,sm,sr,size);return{at:p,kind:'MOVE.'+size,size,src,text:'MOVE.'+size+' '+src.text+',D'+d};}}
  if((w&0xF100)===0x7000&&((w>>9)&7)===d)return{at:p,kind:'MOVEQ',imm:E.s8(w&255),text:'MOVEQ #'+E.s8(w&255)+',D'+d};
  if((w&0xF000)===0xD000&&((w>>9)&7)===d){const sm=(w>>3)&7,sr=w&7;if(sm===0)return{at:p,kind:'ADD',srcReg:sr,double:sr===d,text:'ADD D'+sr+',D'+d};}
  if((w&0xF000)===0xE000&&(w&7)===d)return{at:p,kind:'SHIFT/ROT',text:'SHIFT/ROT '+E.hw(w)+' D'+d};
  return null;
}
function dHistory(E,start,site,d){const a=[];for(let p=start&~1;p<site;p+=2){const z=dWriterAt(E,p,d);if(z)a.push(z);}return a.sort((x,y)=>y.at-x.at);}
async function buildReverse(E){const rev=new Map();for(let b=0;b<E.MAX;b+=0x8000){const end=Math.min(E.MAX,b+0x8000);for(let p=b;p+2<end;p+=2){const c=directAt(E,p);if(!c)continue;let a=rev.get(c.target);if(!a)rev.set(c.target,a=[]);a.push(c);}if((b&0x1FFFF)===0x18000)await sleep(0);}return rev;}
function readMoveAValue(E,z,resolveA,depth){
  const s=z.src;if(z.kind==='LEA'){
    if(s.staticAddr!=null&&!s.index)return[{value:s.staticAddr>>>0,why:z.text}];
    if((s.mode===5||s.mode===6)&&depth>0){const bases=resolveA(s.reg,z.at,depth-1);const disp=s.mode===5?E.s16(E.r16(z.at+2)):s.index.disp8;return bases.map(b=>({value:(b.value+disp)>>>0,why:z.text+' <- '+b.why}));}
    return[];
  }
  if(z.kind.startsWith('MOVEA')){
    if(s.mode===7&&s.reg===4){const v=z.size==='L'?E.r32(z.at+2):(E.s16(E.r16(z.at+2))>>>0);return[{value:v,why:z.text}];}
    if(s.mode===1&&depth>0)return resolveA(s.reg,z.at,depth-1).map(b=>({value:b.value,why:z.text+' <- '+b.why}));
    let addrs=[];
    if(s.staticAddr!=null&&!s.index)addrs=[{addr:s.staticAddr,why:s.text}];
    else if((s.mode===2||s.mode===5)&&depth>0){const bs=resolveA(s.reg,z.at,depth-1),disp=s.mode===5?E.s16(E.r16(z.at+2)):0;addrs=bs.map(b=>({addr:(b.value+disp)>>>0,why:b.why}));}
    const out=[];for(const a of addrs){if(a.addr<0||a.addr+(z.size==='L'?4:2)>E.MAX)continue;const v=z.size==='L'?E.r32(a.addr):(E.s16(E.r16(a.addr))>>>0);if(v<E.MAX)out.push({value:v>>>0,why:z.text+' mem['+E.h(a.addr)+'] <- '+a.why});}return out;
  }
  return[];
}
function resolveAFactory(E,rev,rootFunc,chains){
  const memo=new Map(),active=new Set();
  function resolveA(reg,site,depth=3){
    const fs=findFuncStart(E,site),key=reg+'|'+fs+'|'+site+'|'+depth;if(memo.has(key))return memo.get(key);if(active.has(key)||depth<0)return[];active.add(key);
    const w=nearestAWriter(E,fs,site,reg);let out=[];
    if(w){out=readMoveAValue(E,w,resolveA,depth);chains.push({level:3-depth,func:E.h(fs),site:E.h(site),reg:'A'+reg,writer:E.h(w.at),writerText:w.text,values:out.map(x=>E.h(x.value)).join(' ')});}
    else if(depth>0){const callers=[];for(let d=0;d<=0x20;d+=2){const a=rev.get((fs+d)&~1);if(a)callers.push(...a);}for(const c of callers.slice(0,80)){const cf=findFuncStart(E,c.at),vals=resolveA(reg,c.at,depth-1);chains.push({level:3-depth,func:E.h(fs),site:E.h(site),reg:'A'+reg,writer:'incoming',writerText:'caller '+E.h(cf)+' @ '+E.h(c.at)+' '+c.kind,values:vals.map(x=>E.h(x.value)).join(' ')});out.push(...vals);}}
    active.delete(key);out=[...new Map(out.filter(x=>x.value>=0&&x.value<E.MAX).map(x=>[x.value,x])).values()];memo.set(key,out);return out;
  }
  return resolveA;
}
function indexTableBase(E,idxWriter,resolveA){
  if(!idxWriter?.src?.index)return[];const s=idxWriter.src,x=s.index;
  if(s.mode===7&&s.reg===3)return[{base:s.staticAddr>>>0,why:'PC indexed '+idxWriter.text,index:x}];
  if(s.mode===6){const bs=resolveA(s.reg,idxWriter.at,2);return bs.map(b=>({base:(b.value+x.disp8)>>>0,why:'A'+s.reg+' indexed '+idxWriter.text+' <- '+b.why,index:x}));}
  return[];
}
function execish(E,t){if(t<0||t+2>E.MAX||(t&1))return false;const w=E.r16(t);return w!==0&&w!==0xFFFF&&w!==0x4AFC;}
function playerEvidence(E,t,span=0x500){const refs=E.L.longRefs||[];let n=0,players=new Set(),nearest=1e9;for(const r of refs){const a=parseInt(r.off,16);nearest=Math.min(nearest,Math.abs(a-t));if(a>=t&&a<t+span){n++;players.add(r.player);}}return{refs:n,players:[...players].join(','),nearestRef:nearest===1e9?'':nearest};}
function offsetTargets(E,jumpBase,tableBase,count=64){const out=[];for(let i=0;i<count;i++){const a=tableBase+i*2;if(a+2>E.MAX)break;const raw=E.r16(a),ofs=E.s16(raw),t=(jumpBase+ofs)>>>0;if(!execish(E,t))continue;const pe=playerEvidence(E,t);out.push({i,tableAt:E.h(a),raw:E.hw(raw),offset:ofs,target:E.h(t),offlineTarget:E.off(t),firstOp:E.hw(E.r16(t)),playerRefs:pe.refs,players:pe.players,nearestPlayerRef:pe.nearestRef});}return out;}
function directIndexTargets(E,jumpBase,count=64){const out=[];for(let i=0;i<count;i++){const ix=i*2,t=(jumpBase+ix)>>>0;if(!execish(E,t))continue;const w=E.r16(t),isBranch=(w&0xF000)===0x6000;out.push({indexValue:ix,at:E.h(t),op:E.hw(w),branchLike:isBranch});}return out;}
async function run(){
  stopped=false;await ensure();const E=env(),T=self.__WOF_ROM_FOCUS_TRACE,sites=T.indirectReachable||[];if(!sites.length)throw new Error('no reachable indirect sites');
  const z=sites[0],site=parseInt(z.at,16),func=parseInt(z.func,16),op=E.r16(site),baseReg=op&7,jx=idxExt(E,site);
  console.log('🧭 WOF indirect dispatch resolver v3 · cross-caller A-reg dataflow');
  console.log('=== DISPATCH SITE ===');console.table([{func:E.h(func),site:E.h(site),offline:E.off(site),opcode:E.hw(op),base:'A'+baseReg,index:jx.indexKind+jx.indexReg,indexSize:jx.indexSize,disp8:jx.disp8,extension:jx.ext}]);
  const rev=await buildReverse(E),chains=[],resolveA=resolveAFactory(E,rev,func,chains),aVals=resolveA(baseReg,site,3);
  console.log('=== A'+baseReg+' CROSS-CALL SOURCE CHAINS ===');console.table(chains.slice(0,120));
  console.log('=== A'+baseReg+' CANDIDATE VALUES ===');console.table(aVals.map((x,i)=>({i,value:E.h(x.value),offline:E.off(x.value),why:x.why})));
  const dh=dHistory(E,func,site,jx.indexReg),idxWriter=dh[0]||null;
  console.log('=== INDEX REGISTER HISTORY ===');console.table(dh.slice(0,40).map(q=>({at:E.h(q.at),offline:E.off(q.at),kind:q.kind,text:q.text})));
  const tableBases=indexTableBase(E,idxWriter,resolveA);
  console.log('=== INDEX OFFSET TABLE BASE CANDIDATES ===');console.table(tableBases.map((x,i)=>({i,base:E.h(x.base),offline:E.off(x.base),why:x.why,index:x.index.indexKind+x.index.indexReg+'.'+x.index.indexSize})));
  const all=[];for(const av of aVals){const jumpBase=(av.value+jx.disp8)>>>0;for(const tb of tableBases){for(const r of offsetTargets(E,jumpBase,tb.base,64))all.push({...r,jumpBase:E.h(jumpBase),tableBase:E.h(tb.base)});}}
  const uniq=[...new Map(all.map(x=>[x.jumpBase+'|'+x.tableBase+'|'+x.i+'|'+x.target,x])).values()];
  console.log('=== RESOLVED OFFSET-TABLE TARGETS ===');console.table(uniq.slice(0,160));
  const direct=[];for(const av of aVals){const jb=(av.value+jx.disp8)>>>0;for(const r of directIndexTargets(E,jb,64))direct.push({jumpBase:E.h(jb),...r});}
  console.log('=== DIRECT-INDEX / BRANCH-TABLE SHAPE ===');console.table(direct.filter(x=>x.branchLike).slice(0,120));
  const pe=uniq.filter(x=>x.playerRefs>0||(+x.nearestPlayerRef>=0&&+x.nearestPlayerRef<0x800)).sort((a,b)=>(b.playerRefs-a.playerRefs)-((a.nearestPlayerRef||999999)-(b.nearestPlayerRef||999999)));
  console.log('=== TARGETS WITH PLAYER-REF EVIDENCE ===');console.table(pe.slice(0,80));
  const verdict={site:E.h(site),baseReg:'A'+baseReg,index:jx.indexKind+jx.indexReg+'.'+jx.indexSize,a2Candidates:aVals.length,indexWriter:idxWriter?E.h(idxWriter.at):'',indexWriterKind:idxWriter?.kind||'',tableBaseCandidates:tableBases.length,resolvedTargets:uniq.length,playerEvidenceTargets:pe.length,branchTableEntries:direct.filter(x=>x.branchLike).length};
  console.log('=== DISPATCH VERDICT INPUT ===');console.table([verdict]);
  if(!aVals.length)console.warn('⚠️ A-base 仍未静态解析：下一步应动态抓 0x094F1C 执行时 A2/index，或继续追非 direct caller/state pointer。');
  else if(tableBases.length&&uniq.length)console.log('🎯 已解析出间接 dispatch targets；下一步从 player-evidence targets 反向/正向追真实 selector。');
  else console.warn('⚠️ A-base 已有候选，但 index 不是标准 MOVE.W offset-table；下一步按 direct-index/branch-table 或动态寄存器验证。');
  const out={version:'rom-focus-dispatch-v3-cross-caller',site:verdict,aCandidates:aVals.map(x=>({...x,value:E.h(x.value)})),chains,indexHistory:dh.map(x=>({...x,at:E.h(x.at)})),tableBases:tableBases.map(x=>({...x,base:E.h(x.base)})),targets:uniq,playerEvidence:pe,directIndex:direct};self.__WOF_ROM_FOCUS_DISPATCH=out;return out;
}
self.WOFFOCUSDISPATCH={version:'rom-focus-dispatch-v3-cross-caller',run,stop(){stopped=true;}};
console.log('✅ WOF ROM focus dispatch v3 loaded · cross-caller A-reg + indexed table resolver');
console.log('执行 await WOFFOCUSDISPATCH.run()');
})();