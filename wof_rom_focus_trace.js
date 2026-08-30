(()=>{
'use strict';
try{self.WOFFOCUSTRACE?.stop?.();}catch(_){}
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/';
const INSPECT='2b6956fbcfe5df7f21bcd1a70f69ce72ee4d6b06/wof_rom_focus_inspect.js';
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
function findFuncStart(E,addr){const{r16}=E;addr=Math.max(0,addr&~1);let term=-1;for(let p=addr;p>=Math.max(0,addr-0x220);p-=2){const w=r16(p);if((w&0xFFF8)===0x4E50||w===0x48E7)return p;if(w===0x4E75||w===0x4E73||w===0x4E77){term=p+2;break;}}return term>=0?term:Math.max(0,(addr-0x100)&~1);}
function funcEnd(E,start,cap=0xA00){const{r16,MAX}=E;for(let p=start;p<Math.min(MAX,start+cap);p+=2){const w=r16(p);if(w===0x4E75||w===0x4E73||w===0x4E77)return p+2;}return Math.min(MAX,start+cap);}
function callAt(E,p){const{r16,r32,s8,s16,MAX}=E,w=r16(p);if(w===0x4EB9||w===0x4EF9){const t=r32(p+2);if(t<MAX)return{at:p,target:t,kind:w===0x4EB9?'JSR.L':'JMP.L'};}if((w&0xFF00)===0x6100){const d=w&255,t=d===0?p+2+s16(r16(p+2)):p+2+s8(d);if(t>=0&&t<MAX)return{at:p,target:t,kind:'BSR'};}return null;}
function decodePlayerRefs(E,start,end){const{L,r16,r32,h,off,hw,P}=E,rows=[];for(const x of L.longRefs||[]){const at=parseInt(x.off,16);if(!(at>=start&&at<end))continue;let hint='',opAt=at-2,op=r16(opAt);if((op&0xF1FF)===0x41F9)hint='LEA abs.L,A'+((op>>9)&7);else if((op&0xF1FF)===0x207C)hint='MOVEA.L #imm,A'+((op>>9)&7);else if(op===0x4879)hint='PEA abs.L';else{opAt=at-4;op=r16(opAt);if((op&0xF1FF)===0x41F9)hint='LEA abs.L,A'+((op>>9)&7)+' (?)';}
    const words=[];for(let p=Math.max(start,at-10);p<=Math.min(end-2,at+8);p+=2)words.push(hw(r16(p)));
    rows.push({player:x.player,at:h(at),offlineAt:off(at),opAt:h(opAt),op:hw(op),hint,imm:h(r32(at)),context:words.join(' ')});
  }return rows;}
function cmpBranchMap(E,start,end){const{r16,s8,s16,h,off,hw}=E,rows=[];for(let p=start&~1;p+1<end;p+=2){const w=r16(p);let kind='',target='';if((w&0xF000)===0xB000)kind='CMP/EOR-family';else if((w&0xF0F8)===0x50C8)kind='DBcc';else if((w&0xF000)===0x6000){kind='Bcc/BSR';const d=w&255,t=d===0?p+2+s16(r16(p+2)):d===0xFF?null:p+2+s8(d);if(t!=null)target=h(t);}else continue;rows.push({at:h(p),offlineAt:off(p),op:hw(w),kind,target});}return rows;}
async function directCallers(E,start,end){const{MAX,h,off}=E,out=[];for(let b=0;b<MAX;b+=0x8000){const e=Math.min(MAX,b+0x8000);for(let p=b;p+6<e;p+=2){const c=callAt(E,p);if(c&&c.target>=start&&c.target<end){const fs=findFuncStart(E,p);out.push({at:h(p),offlineAt:off(p),callerFunc:h(fs),offlineCaller:off(fs),target:h(c.target),kind:c.kind});}}if((b&0x1FFFF)===0x18000)await sleep(0);}return out;}
function scanCalls(E,start){const end=funcEnd(E,start),out=[];for(let p=start;p+6<end;p+=2){const c=callAt(E,p);if(c)out.push(c);}return out;}
async function pathsFromTypes(E,cStart,cEnd,maxDepth=6){const{L,h,off}=E,cache=new Map(),rows=[];const TYPES=(L.types||[]).map(x=>({type:x.type,entry:Number(x.entry??x.liveEntry??0)})).filter(x=>Number.isFinite(x.entry));
  const callsCached=a=>{a=a&~1;if(cache.has(a))return cache.get(a);const v=scanCalls(E,a);cache.set(a,v);return v;};
  for(let ti=0;ti<TYPES.length;ti++){
    if(stopped)throw new Error('trace stopped');const t=TYPES[ti],q=[{addr:t.entry,path:[t.entry]}],seen=new Set(),hits=[];let expanded=0;
    while(q.length&&expanded<1400){const n=q.shift(),key=n.addr&~1;if(seen.has(key)||n.path.length-1>maxDepth)continue;seen.add(key);expanded++;
      if(key>=cStart&&key<cEnd){hits.push(n.path);break;}
      for(const c of callsCached(key)){
        if(c.target>=cStart&&c.target<cEnd){hits.push([...n.path,c.target]);q.length=0;break;}
        if(n.path.length-1<maxDepth&&!seen.has(c.target&~1))q.push({addr:c.target,path:[...n.path,c.target]});
      }
    }
    if(hits.length){const p=hits[0];rows.push({type:t.type,entry:h(t.entry),offlineEntry:off(t.entry),depth:p.length-1,path:p.map(h).join(' → '),offlinePath:p.map(off).join(' → ')});}
    if(ti%6===5)await sleep(0);
  }
  return rows;
}
async function run(){await ensure();const E=env(),{I,h,off}=E;const strong=I.strong||self.__WOF_ROM_FOCUS_DEEP?.strong?.[0]||self.__WOF_ROM_FOCUS_DEEP?.top?.[0];if(!strong)throw new Error('no candidate');const id=strong.cluster??1,rep=I.reports.find(x=>x.id===id)||I.reports[0],start=parseInt(rep.start,16),end=start+(rep.size||0);
  console.log('🧬 Target selector trace v1 · candidate',h(start),'..',h(end));
  console.log('=== CANDIDATE CORE ===');console.table([{cluster:id,liveStart:h(start),offlineStart:off(start),end:h(end),size:end-start,p1:rep.features?.p1,p2:rep.features?.p2,p3:rep.features?.p3,cmp:rep.features?.cmp,E0:rep.features?.e0,callers:rep.callers?.length,pointers:rep.pointerRefs?.length,externalBranches:rep.branchEntrants?.length}]);
  const refs=decodePlayerRefs(E,start,end);console.log('=== PLAYER REFS + OPCODE CONTEXT ===');console.table(refs);
  const cmps=cmpBranchMap(E,start,end);console.log('=== CMP / BRANCH MAP ===');console.table(cmps);
  const callers=await directCallers(E,start,end);console.log('=== DIRECT CALLERS (exact) ===');console.table(callers.slice(0,80));
  console.log('🧭 反查 47 个 enemy type 是否能沿 direct JSR/BSR 到达候选…');const paths=await pathsFromTypes(E,start,end,6);console.log('=== ENEMY TYPE → CANDIDATE PATHS ===');console.table(paths);
  const verdict={candidate:h(start),offline:off(start),directTypePaths:paths.length,typeIds:paths.map(x=>x.type).join(','),directCallers:callers.length,playerRefs:refs.length,cmpBranchOps:cmps.length};
  console.log('=== TRACE VERDICT INPUT ===');console.table([verdict]);
  if(paths.length)console.log('🎯 有 enemy type direct-call path：候选值得继续做动态寄存器验证');else console.warn('⚠️ 47 个 enemy type 在 6 层 direct JSR/BSR 内都到不了该候选；它更可能是其他多人系统逻辑，需转向间接跳转/表驱动路径');
  const out={version:'rom-focus-trace-v1',candidate:verdict,refs,cmps,callers,paths};self.__WOF_ROM_FOCUS_TRACE=out;return out;}
self.WOFFOCUSTRACE={version:'rom-focus-trace-v1',run,stop(){stopped=true;}};
console.log('✅ WOF ROM focus trace v1 loaded');console.log('执行 await WOFFOCUSTRACE.run()');
})();