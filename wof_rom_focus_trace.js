(()=>{
'use strict';
try{self.WOFFOCUSTRACE?.stop?.();}catch(_){}
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/';
const INSPECT='main/wof_rom_focus_inspect.js';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let stopped=false;
const load=async path=>{const r=await fetch(RAW+path+'?x='+Math.random());if(!r.ok)throw new Error('fetch failed '+r.status);const s=await r.text();(0,eval)(s);};
async function ensure(){
  if(self.__WOF_ROM_FOCUS_INSPECT?.reports?.length)return;
  console.log('♻️ trace: inspect 状态不存在，自动恢复完整 ROM 分析…');
  await load(INSPECT);
  for(let i=0;i<600;i++){
    if(self.__WOF_ROM_FOCUS_INSPECT?.reports?.length)return;
    await sleep(100);
  }
  throw new Error('inspect 自动恢复超时');
}
function env(){
  const MOD=_0x515056,C=self.__WOF_ROM_LOC_CACHE,L=self.__WOF_ROM_FOCUS_LAST,I=self.__WOF_ROM_FOCUS_INSPECT;
  if(!MOD?.HEAPU8||!C||!L?.longRefs||!I?.reports)throw new Error('ROM focus state unavailable');
  const M=MOD.HEAPU8,base=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-base),DELTA=C.offlineDelta|0;
  const r8=o=>M[base+(SW?(o^1):o)]>>>0;
  const r16=o=>((r8(o)<<8)|r8(o+1))>>>0;
  const r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
  const s8=v=>v&0x80?v-0x100:v,s16=v=>v&0x8000?v-0x10000:v;
  const h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0');
  const off=x=>h((x-DELTA)>>>0);
  const hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
  const P={P1:0x00FFBE1C,P2:0x00FFBEFC,P3:0x00FFBFDC};
  return{MOD,C,L,I,M,base,SW,MAX,DELTA,r8,r16,r32,s8,s16,h,off,hw,P};
}
function isReturn(w){return w===0x4E75||w===0x4E73||w===0x4E77;}
function branchTarget(E,p){
  const{r16,s8,s16,MAX}=E,w=r16(p);
  if((w&0xF000)!==0x6000||((w>>8)&0xF)===1)return null; // BSR 不是本函数控制流分支
  const d=w&255,t=d===0?p+2+s16(r16(p+2)):p+2+s8(d);
  return t>=0&&t<MAX?t:null;
}
function firstReturnAfter(E,p,limit){
  const{r16}=E;
  for(let q=p&~1;q<limit;q+=2)if(isReturn(r16(q)))return q+2;
  return limit;
}
function funcEnd(E,start,cap=0xA00){
  const{r16,MAX}=E,start0=start&~1,limit=Math.min(MAX,start0+cap);
  let end=firstReturnAfter(E,start0,limit);
  // 多出口函数：若前半段 Bcc/BRA 跨过第一个 RTS，则把被跳到的后半段也纳入扫描。
  for(let pass=0;pass<6&&end<limit;pass++){
    let extended=end;
    for(let p=start0;p<end;p+=2){
      const t=branchTarget(E,p);
      if(t!=null&&t>=end&&t<limit)extended=Math.max(extended,firstReturnAfter(E,t,limit));
    }
    if(extended===end)break;
    end=extended;
  }
  return end;
}
function findFuncStart(E,addr){const{r16}=E;addr=Math.max(0,addr&~1);let term=-1;for(let p=addr;p>=Math.max(0,addr-0x220);p-=2){const w=r16(p);if((w&0xFFF8)===0x4E50||w===0x48E7)return p;if(isReturn(w)){term=p+2;break;}}return term>=0?term:Math.max(0,(addr-0x100)&~1);}
function directAt(E,p){
  const{r16,r32,s8,s16,MAX}=E,w=r16(p);
  let t=null,kind='',len=0;
  // JSR <ea> direct forms
  if(w===0x4EB8){t=s16(r16(p+2))>>>0;kind='JSR abs.W';len=4;}
  else if(w===0x4EB9){t=r32(p+2);kind='JSR abs.L';len=6;}
  else if(w===0x4EBA){t=p+2+s16(r16(p+2));kind='JSR d16(PC)';len=4;}
  // JMP <ea> direct forms (tail dispatch)
  else if(w===0x4EF8){t=s16(r16(p+2))>>>0;kind='JMP abs.W';len=4;}
  else if(w===0x4EF9){t=r32(p+2);kind='JMP abs.L';len=6;}
  else if(w===0x4EFA){t=p+2+s16(r16(p+2));kind='JMP d16(PC)';len=4;}
  // 68000 BSR: d8=0 means 16-bit extension; 0xFF is ordinary -1 displacement on 68000.
  else if((w&0xFF00)===0x6100){const d=w&255;t=d===0?p+2+s16(r16(p+2)):p+2+s8(d);kind=d===0?'BSR.W':'BSR.S';len=d===0?4:2;}
  if(t==null||t<0||t>=MAX)return null;
  return{at:p,target:t&~1,kind,len};
}
function indirectAt(E,p){
  const w=E.r16(p);
  // JSR/JMP (An), d16(An), d8(An,Xn), d8(PC,Xn): 执行时才能完全确定目标。
  if((w&0xFFF8)===0x4E90)return{at:p,kind:'JSR (An)',reg:w&7};
  if((w&0xFFF8)===0x4EA8)return{at:p,kind:'JSR d16(An)',reg:w&7};
  if((w&0xFFF8)===0x4EB0)return{at:p,kind:'JSR d8(An,Xn)',reg:w&7};
  if(w===0x4EBB)return{at:p,kind:'JSR d8(PC,Xn)',reg:null};
  if((w&0xFFF8)===0x4ED0)return{at:p,kind:'JMP (An)',reg:w&7};
  if((w&0xFFF8)===0x4EE8)return{at:p,kind:'JMP d16(An)',reg:w&7};
  if((w&0xFFF8)===0x4EF0)return{at:p,kind:'JMP d8(An,Xn)',reg:w&7};
  if(w===0x4EFB)return{at:p,kind:'JMP d8(PC,Xn)',reg:null};
  return null;
}
function decodePlayerRefs(E,start,end){const{L,r16,r32,h,off,hw}=E,rows=[];for(const x of L.longRefs||[]){const at=parseInt(x.off,16);if(!(at>=start&&at<end))continue;let hint='',opAt=at-2,op=r16(opAt);if((op&0xF1FF)===0x41F9)hint='LEA abs.L,A'+((op>>9)&7);else if((op&0xF1FF)===0x207C)hint='MOVEA.L #imm,A'+((op>>9)&7);else if(op===0x4879)hint='PEA abs.L';else{opAt=at-4;op=r16(opAt);if((op&0xF1FF)===0x41F9)hint='LEA abs.L,A'+((op>>9)&7)+' (?)';}
    const words=[];for(let p=Math.max(start,at-10);p<=Math.min(end-2,at+8);p+=2)words.push(hw(r16(p)));
    rows.push({player:x.player,at:h(at),offlineAt:off(at),opAt:h(opAt),op:hw(op),hint,imm:h(r32(at)),context:words.join(' ')});
  }return rows;}
function cmpBranchMap(E,start,end){const{r16,s8,s16,h,off,hw}=E,rows=[];for(let p=start&~1;p+1<end;p+=2){const w=r16(p);let kind='',target='';if((w&0xF000)===0xB000)kind='CMP/EOR-family';else if((w&0xF0F8)===0x50C8)kind='DBcc';else if((w&0xF000)===0x6000){kind='Bcc/BSR';const d=w&255,t=d===0?p+2+s16(r16(p+2)):p+2+s8(d);target=h(t);}else continue;rows.push({at:h(p),offlineAt:off(p),op:hw(w),kind,target});}return rows;}
async function directCallers(E,start,end){const{MAX,h,off}=E,out=[];for(let b=0;b<MAX;b+=0x8000){const e=Math.min(MAX,b+0x8000);for(let p=b;p+2<e;p+=2){const c=directAt(E,p);if(c&&c.target>=start&&c.target<end){const fs=findFuncStart(E,p);out.push({at:h(p),offlineAt:off(p),callerFunc:h(fs),offlineCaller:off(fs),target:h(c.target),kind:c.kind});}}if((b&0x1FFFF)===0x18000)await sleep(0);}return out;}
function scanRoutine(E,start){
  start&=~1;const end=funcEnd(E,start),calls=[],indirect=[];
  for(let p=start;p+1<end;p+=2){const c=directAt(E,p);if(c)calls.push(c);const z=indirectAt(E,p);if(z)indirect.push(z);}
  return{start,end,calls,indirect};
}
async function pathsFromTypes(E,cStart,cEnd,maxDepth=6){
  const{L,h,off}=E,cache=new Map(),rows=[],visitedRoutines=new Map();
  const TYPES=(L.types||[]).map(x=>({type:x.type,entry:Number(x.entry??x.liveEntry??0)})).filter(x=>Number.isFinite(x.entry));
  const cached=a=>{a=a&~1;if(cache.has(a))return cache.get(a);const v=scanRoutine(E,a);cache.set(a,v);return v;};
  for(let ti=0;ti<TYPES.length;ti++){
    if(stopped)throw new Error('trace stopped');
    const t=TYPES[ti],q=[{addr:t.entry,path:[t.entry],edges:[]}],seen=new Set(),hits=[];let expanded=0;
    while(q.length&&expanded<1800){
      const n=q.shift(),key=n.addr&~1;if(seen.has(key)||n.edges.length>maxDepth)continue;seen.add(key);expanded++;
      if(key>=cStart&&key<cEnd){hits.push(n);break;}
      const r=cached(key);visitedRoutines.set(key,r);
      for(const c of r.calls){
        const edge={from:key,at:c.at,target:c.target,kind:c.kind};
        if(c.target>=cStart&&c.target<cEnd){hits.push({addr:c.target,path:[...n.path,c.target],edges:[...n.edges,edge]});q.length=0;break;}
        if(n.edges.length<maxDepth&&!seen.has(c.target&~1))q.push({addr:c.target,path:[...n.path,c.target],edges:[...n.edges,edge]});
      }
    }
    if(hits.length){const z=hits[0];rows.push({type:t.type,entry:h(t.entry),offlineEntry:off(t.entry),depth:z.edges.length,path:z.path.map(h).join(' → '),kinds:z.edges.map(e=>e.kind).join(' → '),callSites:z.edges.map(e=>h(e.at)).join(' → '),offlinePath:z.path.map(off).join(' → ')});}
    if(ti%6===5)await sleep(0);
  }
  const indirect=[];
  for(const [func,r] of visitedRoutines){for(const z of r.indirect)indirect.push({func:h(func),at:h(z.at),offlineAt:off(z.at),kind:z.kind,reg:z.reg==null?'':('A'+z.reg)});}
  const uniqIndirect=[...new Map(indirect.map(x=>[x.at+'|'+x.kind,x])).values()];
  return{rows,indirect:uniqIndirect,visited:visitedRoutines.size};
}
async function run(){
  stopped=false;await ensure();const E=env(),{I,h,off}=E;
  const strong=I.strong||self.__WOF_ROM_FOCUS_DEEP?.strong?.[0]||self.__WOF_ROM_FOCUS_DEEP?.top?.[0];if(!strong)throw new Error('no candidate');
  const id=strong.cluster??1,rep=I.reports.find(x=>x.id===id)||I.reports[0],start=parseInt(rep.start,16),end=start+(rep.size||0);
  console.log('🧬 Target selector trace v2 · candidate',h(start),'..',h(end));
  console.log('=== CANDIDATE CORE ===');console.table([{cluster:id,liveStart:h(start),offlineStart:off(start),end:h(end),size:end-start,p1:rep.features?.p1,p2:rep.features?.p2,p3:rep.features?.p3,cmp:rep.features?.cmp,E0:rep.features?.e0,callers:rep.callers?.length,pointers:rep.pointerRefs?.length,externalBranches:rep.branchEntrants?.length}]);
  const refs=decodePlayerRefs(E,start,end);console.log('=== PLAYER REFS + OPCODE CONTEXT ===');console.table(refs);
  const cmps=cmpBranchMap(E,start,end);console.log('=== CMP / BRANCH MAP ===');console.table(cmps);
  const callers=await directCallers(E,start,end);console.log('=== DIRECT CALLERS (all 68000 direct forms) ===');console.table(callers.slice(0,100));
  console.log('🧭 反查 47 个 enemy type 是否能沿 direct JSR/BSR/JMP 到达候选…');
  const traced=await pathsFromTypes(E,start,end,6),paths=traced.rows;
  console.log('=== ENEMY TYPE → CANDIDATE PATHS ===');console.table(paths);
  const verdict={candidate:h(start),offline:off(start),directTypePaths:paths.length,typeIds:paths.map(x=>x.type).join(','),directCallers:callers.length,playerRefs:refs.length,cmpBranchOps:cmps.length,reachableRoutines:traced.visited,reachableIndirectOps:traced.indirect.length};
  console.log('=== TRACE VERDICT INPUT ===');console.table([verdict]);
  if(paths.length)console.log('🎯 directTypePaths > 0：固定具体 type/call path，下一步反汇编 0x0080F2 找最终 target 寄存器');
  else{console.warn('⚠️ directTypePaths == 0：已覆盖 JSR abs.W/L、JSR d16(PC)、BSR.S/W、JMP abs.W/L、JMP d16(PC)；应立即转间接 JSR/JMP、state dispatch、function pointer、jump table');console.log('=== REACHABLE INDIRECT JSR/JMP SITES (next branch input) ===');console.table(traced.indirect.slice(0,120));}
  const out={version:'rom-focus-trace-v2-direct-68000',candidate:verdict,refs,cmps,callers,paths,indirectReachable:traced.indirect};self.__WOF_ROM_FOCUS_TRACE=out;return out;
}
self.WOFFOCUSTRACE={version:'rom-focus-trace-v2-direct-68000',run,stop(){stopped=true;}};
console.log('✅ WOF ROM focus trace v2 loaded · direct 68000 forms hardened');
console.log('执行 await WOFFOCUSTRACE.run()');
})();