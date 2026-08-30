(()=>{
'use strict';
try{self.WOFFOCUSINDIRECTCFG?.stop?.();}catch(_){}
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let stopped=false;
const load=async f=>{const r=await fetch(RAW+f+'?x='+Math.random());if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);const s=await r.text();return await (0,eval)(s);};
async function ensure(){
  if(self.__WOF_ROM_LOC_CACHE&&self.__WOF_ROM_FOCUS_LAST?.types?.length)return;
  console.log('♻️ indirect-cfg: ROM state missing，自动恢复 inspect/probe…');
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
  return{L,MAX,r8,r16,r32,s8,s16,h,off,hw};
}
function sizeFrom2(bits){return bits===0?'B':bits===1?'W':bits===2?'L':'W';}
function eaWords(mode,reg,size){
  if(mode<=4)return 0;
  if(mode===5||mode===6)return 1;
  if(mode===7){if(reg===0||reg===2||reg===3)return 1;if(reg===1)return 2;if(reg===4)return size==='L'?2:1;}
  return 0;
}
function indexExt(E,p){const x=E.r16(p+2);return{ext:E.hw(x),indexKind:(x&0x8000)?'A':'D',indexReg:(x>>12)&7,indexSize:(x&0x0800)?'L':'W',disp8:E.s8(x&255)};}
function eaText(E,p,mode,reg,size='L'){
  if(mode===0)return'D'+reg;if(mode===1)return'A'+reg;if(mode===2)return'(A'+reg+')';if(mode===3)return'(A'+reg+')+';if(mode===4)return'-(A'+reg+')';
  if(mode===5)return E.s16(E.r16(p+2))+'(A'+reg+')';
  if(mode===6){const x=indexExt(E,p);return x.disp8+'(A'+reg+','+x.indexKind+x.indexReg+'.'+x.indexSize+')';}
  if(mode===7&&reg===0)return E.h(E.s16(E.r16(p+2))>>>0)+'.W';
  if(mode===7&&reg===1)return E.h(E.r32(p+2))+'.L';
  if(mode===7&&reg===2)return E.h((p+2+E.s16(E.r16(p+2)))>>>0)+'(PC)';
  if(mode===7&&reg===3){const x=indexExt(E,p);return x.disp8+'(PC,'+x.indexKind+x.indexReg+'.'+x.indexSize+')';}
  if(mode===7&&reg===4)return'#imm';return'EA('+mode+','+reg+')';
}
function decode(E,p){
  const w=E.r16(p),g=w>>>12,mode=(w>>3)&7,reg=w&7;let words=1,kind='OP',target=null,fall=true,terminal=false,call=false,indirect=false,text='';
  if(w===0x4E75||w===0x4E73||w===0x4E77){kind=w===0x4E75?'RTS':w===0x4E73?'RTE':'RTR';terminal=true;fall=false;text=kind;}
  else if(w===0x4E72){kind='STOP';words=2;terminal=true;fall=false;text='STOP';}
  else if((w&0xFFF0)===0x4E40){kind='TRAP';text='TRAP';}
  else if((w&0xFFF8)===0x4E50){kind='LINK';words=2;text='LINK';}
  else if((w&0xFFF8)===0x4E58){kind='UNLK';text='UNLK';}
  else if((w&0xFFC0)===0x4E80){
    words=1+eaWords(mode,reg,'L');call=true;
    if(mode===7&&reg===0){target=E.s16(E.r16(p+2))>>>0;kind='JSR_DIRECT';}
    else if(mode===7&&reg===1){target=E.r32(p+2);kind='JSR_DIRECT';}
    else if(mode===7&&reg===2){target=p+2+E.s16(E.r16(p+2));kind='JSR_DIRECT';}
    else{kind='JSR_INDIRECT';indirect=true;}
    text='JSR '+eaText(E,p,mode,reg,'L');
  }
  else if((w&0xFFC0)===0x4EC0){
    words=1+eaWords(mode,reg,'L');fall=false;
    if(mode===7&&reg===0){target=E.s16(E.r16(p+2))>>>0;kind='JMP_DIRECT';}
    else if(mode===7&&reg===1){target=E.r32(p+2);kind='JMP_DIRECT';}
    else if(mode===7&&reg===2){target=p+2+E.s16(E.r16(p+2));kind='JMP_DIRECT';}
    else{kind='JMP_INDIRECT';indirect=true;}
    text='JMP '+eaText(E,p,mode,reg,'L');
  }
  else if(g===6){const cc=(w>>8)&15,d=w&255;words=d===0?2:1;target=d===0?p+2+E.s16(E.r16(p+2)):p+2+E.s8(d);kind=cc===0?'BRA':cc===1?'BSR':'BCC';call=cc===1;if(cc===0)fall=false;text=kind;}
  else if(g===1||g===2||g===3){const size=g===1?'B':g===2?'L':'W',dm=(w>>6)&7,dr=(w>>9)&7;words=1+eaWords(mode,reg,size)+eaWords(dm,dr,size);kind='MOVE.'+size;text=kind;}
  else if(g===5){const sz=(w>>6)&3;if(sz===3&&mode===1){kind='DBCC';words=2;target=p+2+E.s16(E.r16(p+2));text='DBCC';}else{kind=sz===3?'SCC':'ADDQ/SUBQ';words=1+eaWords(mode,reg,sz===3?'B':sizeFrom2(sz));text=kind;}}
  else if(g===7){kind='MOVEQ';text='MOVEQ';}
  else if(g===0){
    if([0x003C,0x007C,0x023C,0x027C,0x0A3C,0x0A7C].includes(w)){kind='IMM_SR_CCR';words=2;text=kind;}
    else if((w&0xF138)===0x0108){kind='MOVEP';words=2;text=kind;}
    else if((w&0xFF00)===0x0800){kind='BIT_IMM';words=2+eaWords(mode,reg,'B');text=kind;}
    else if((w&0xF100)===0x0100){kind='BIT_DYN';words=1+eaWords(mode,reg,'B');text=kind;}
    else{const op=(w>>8)&15,sz=(w>>6)&3;if([0,2,4,6,10,12].includes(op)){const size=sizeFrom2(sz),imm=size==='L'?2:1;kind='IMM';words=1+imm+eaWords(mode,reg,size);text=kind;}else{kind='G0';text=kind;}}
  }
  else if(g===4){
    const movem=((w&0xFB80)===0x4880)&&mode>=2;
    if(movem){kind='MOVEM';words=2+eaWords(mode,reg,(w&0x0040)?'L':'W');text=kind;}
    else if((w&0xFFF8)===0x4880||(w&0xFFF8)===0x48C0||(w&0xFFF8)===0x4840){kind='EXT/SWAP';text=kind;}
    else if((w&0xF1C0)===0x41C0){kind='LEA';words=1+eaWords(mode,reg,'L');text=kind;}
    else if((w&0xFFC0)===0x4840){kind='PEA';words=1+eaWords(mode,reg,'L');text=kind;}
    else{const sz=(w>>6)&3,size=sizeFrom2(sz);kind='G4_EA';words=1+eaWords(mode,reg,size);text=kind;}
  }
  else if(g===8||g===9||g===11||g===12||g===13){let size=((w>>6)&3)===2?'L':'W';kind='ALU';words=1+eaWords(mode,reg,size);text=kind;}
  else if(g===10){kind='LINEA';terminal=true;fall=false;text=kind;}
  else if(g===14){const sz=(w>>6)&3;kind='SHIFT';if(sz===3)words=1+eaWords(mode,reg,'W');text=kind;}
  else if(g===15){kind='LINEF';terminal=true;fall=false;text=kind;}
  const len=words*2,next=p+len;
  if(target!=null&&(target<0||target>=E.MAX))target=null;
  return{at:p,w,words,len,next,kind,target,fall,terminal,call,indirect,mode,reg,text};
}
function scanRoutine(E,entry){
  const q=[entry&~1],seen=new Set(),ins=[],calls=[],inds=[];let min=entry&~1,max=min,decodeErrors=0;
  while(q.length&&seen.size<2600){
    if(stopped)throw new Error('stopped');const p=q.shift();
    if(p<0||p>=E.MAX||(p&1)||seen.has(p))continue;
    if(Math.abs(p-entry)>0x2800)continue;
    seen.add(p);min=Math.min(min,p);max=Math.max(max,p);
    let d;try{d=decode(E,p);}catch(_){decodeErrors++;continue;}ins.push(d);
    if(d.indirect)inds.push(d);
    if(d.kind==='JSR_DIRECT'||d.kind==='BSR'){if(d.target!=null)calls.push({at:p,target:d.target&~1,kind:d.kind});if(d.fall)q.push(d.next);continue;}
    if(d.kind==='JMP_DIRECT'){if(d.target!=null)calls.push({at:p,target:d.target&~1,kind:d.kind});continue;}
    if(d.kind==='BRA'){if(d.target!=null)q.push(d.target&~1);continue;}
    if(d.kind==='BCC'||d.kind==='DBCC'){if(d.fall)q.push(d.next);if(d.target!=null)q.push(d.target&~1);continue;}
    if(d.kind==='JMP_INDIRECT'||d.terminal)continue;
    if(d.fall)q.push(d.next);
  }
  return{entry:entry&~1,seen,ins,calls,inds,min,max,decodeErrors};
}
function indirectDetail(E,d){
  let form='';if(d.mode===2)form='(A'+d.reg+')';else if(d.mode===3)form='(A'+d.reg+')+';else if(d.mode===4)form='-(A'+d.reg+')';else if(d.mode===5)form=E.s16(E.r16(d.at+2))+'(A'+d.reg+')';else if(d.mode===6){const x=indexExt(E,d.at);form=x.disp8+'(A'+d.reg+','+x.indexKind+x.indexReg+'.'+x.indexSize+')';}else if(d.mode===7&&d.reg===3){const x=indexExt(E,d.at);form=x.disp8+'(PC,'+x.indexKind+x.indexReg+'.'+x.indexSize+')';}else form='mode'+d.mode+'/reg'+d.reg;
  return{form};
}
async function run(){
  stopped=false;await ensure();const E=env(),types=(E.L.types||[]).map(x=>({type:x.type,entry:Number(x.entry??x.liveEntry??0)})).filter(x=>Number.isFinite(x.entry)&&x.entry<E.MAX);
  console.log('🧭 WOF real indirect CFG scan v1 · only decoded 68000 instruction boundaries');
  const routineCache=new Map(),siteMap=new Map(),typeStats=[];
  const getRoutine=a=>{a&=~1;if(!routineCache.has(a))routineCache.set(a,scanRoutine(E,a));return routineCache.get(a);};
  for(let ti=0;ti<types.length;ti++){
    const t=types[ti],q=[{addr:t.entry,depth:0,path:[t.entry]}],seenR=new Set();let expanded=0,indHits=0;
    while(q.length&&expanded<2200){const n=q.shift(),a=n.addr&~1;if(seenR.has(a)||n.depth>8)continue;seenR.add(a);expanded++;const r=getRoutine(a);
      for(const d of r.inds){indHits++;const key=d.at+'|'+d.kind;let z=siteMap.get(key);if(!z)siteMap.set(key,z={at:d.at,kind:d.kind,op:d.w,mode:d.mode,reg:d.reg,types:new Set(),paths:new Map(),routine:a});z.types.add(t.type);if(!z.paths.has(t.type))z.paths.set(t.type,[...n.path,a]);}
      if(n.depth<8){for(const c of r.calls){if(c.target>=0&&c.target<E.MAX&&!seenR.has(c.target))q.push({addr:c.target,depth:n.depth+1,path:[...n.path,c.target]});}}
    }
    typeStats.push({type:t.type,entry:E.h(t.entry),routines:seenR.size,indirectHits:indHits});
    if(ti%4===3)await sleep(0);
  }
  const rows=[...siteMap.values()].map(z=>{const det=indirectDetail(E,{at:z.at,mode:z.mode,reg:z.reg});const ids=[...z.types].sort((a,b)=>a-b);return{site:E.h(z.at),offline:E.off(z.at),routine:E.h(z.routine),kind:z.kind,opcode:E.hw(z.op),form:det.form,typeCount:ids.length,typeIds:ids.join(','),samplePath:z.paths.size?[...z.paths.values()][0].map(E.h).join(' → '):''};}).sort((a,b)=>b.typeCount-a.typeCount||parseInt(a.site,16)-parseInt(b.site,16));
  console.log('=== REAL INDIRECT DISPATCH SITES ===');console.table(rows.slice(0,160));
  console.log('=== TYPE CFG COVERAGE ===');console.table(typeStats);
  const old=rows.find(x=>x.site==='0x094F1C');
  const verdict={types:types.length,decodedRoutines:routineCache.size,realIndirectSites:rows.length,typesWithIndirect:typeStats.filter(x=>x.indirectHits>0).length,oldFalseSitePresent:!!old,topSite:rows[0]?.site||'',topKind:rows[0]?.kind||'',topTypeCount:rows[0]?.typeCount||0,topTypeIds:rows[0]?.typeIds||''};
  console.log('=== REAL INDIRECT VERDICT ===');console.table([verdict]);
  if(old)console.warn('⚠️ 0x094F1C unexpectedly appears on boundary-aware CFG; inspect decoder disagreement before using it.');
  else if(rows.length)console.log('🎯 已排除 0x094F1C 假阳性，并找到真实可达 indirect sites；下一步只追这些真实站点的 state/function-pointer 数据流。');
  else console.warn('⚠️ 47 types 的已解码 CFG 暂未发现真实 indirect JSR/JMP；下一步应检查 decoder coverage / data-driven state handlers，而不是回到 0x0080F2。');
  const out={version:'rom-focus-indirect-cfg-v1',verdict,sites:rows,typeStats};self.__WOF_ROM_FOCUS_INDIRECT_CFG=out;return out;
}
self.WOFFOCUSINDIRECTCFG={version:'rom-focus-indirect-cfg-v1',run,stop(){stopped=true;}};
console.log('✅ WOF ROM focus indirect CFG v1 loaded');console.log('执行 await WOFFOCUSINDIRECTCFG.run()');
})();