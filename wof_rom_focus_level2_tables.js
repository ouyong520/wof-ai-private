(()=>{
'use strict';
try{self.WOFFOCUSLEVEL2?.stop?.();}catch(_){}
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let stopped=false;
const load=async f=>{const r=await fetch(RAW+f+'?x='+Math.random());if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return (0,eval)(await r.text());};
async function ensure(){
  if(!self.__WOF_ROM_LOC_CACHE||!self.__WOF_ROM_FOCUS_LAST?.types?.length)await load('wof_rom_focus_inspect.js');
  if(!self.__WOF_ROM_LOC_CACHE||!self.__WOF_ROM_FOCUS_LAST?.types?.length)throw new Error('ROM state unavailable');
}
function env(){
  const MOD=_0x515056,C=self.__WOF_ROM_LOC_CACHE,L=self.__WOF_ROM_FOCUS_LAST,M=MOD.HEAPU8,base=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-base),DELTA=C.offlineDelta|0;
  const r8=o=>M[base+(SW?(o^1):o)]>>>0;
  const r16=o=>((r8(o)<<8)|r8(o+1))>>>0;
  const r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
  const s8=v=>v&0x80?v-0x100:v,s16=v=>v&0x8000?v-0x10000:v;
  const h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0');
  const off=x=>h((x-DELTA)>>>0),hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
  return{C,L,MAX,r8,r16,r32,s8,s16,h,off,hw};
}
function validCode(E,t){if(!Number.isInteger(t)||t<0x40||t>=E.MAX||(t&1))return false;const w=E.r16(t);return w!==0&&w!==0xffff&&w!==0x4afc;}
function transferAt(E,p){
  const w=E.r16(p),m=(w>>3)&7,r=w&7;
  if((w&0xffc0)===0x4e80)return{at:p,word:w,kind:'JSR',mode:m,reg:r,usesA4:r===4&&m>=2&&m<=6};
  if((w&0xffc0)===0x4ec0)return{at:p,word:w,kind:'JMP',mode:m,reg:r,usesA4:r===4&&m>=2&&m<=6};
  return null;
}
function refEvidence(E,t,span=0x300){
  let refs=0;const ps=new Set();let nearest=0x7fffffff;
  for(const x of E.L.longRefs||[]){const a=parseInt(x.off,16);if(!Number.isFinite(a))continue;const d=Math.abs(a-t);if(d<nearest)nearest=d;if(a>=t&&a<t+span){refs++;ps.add(x.player);}}
  return{refs,players:[...ps].sort().join(','),nearest:nearest===0x7fffffff?'':nearest};
}
function rawCtx(E,p,b=0x12,a=0x18){const out=[];for(let q=Math.max(0,p-b)&~1;q<=Math.min(E.MAX-2,p+a);q+=2)out.push({at:E.h(q),offline:E.off(q),word:E.hw(E.r16(q)),mark:q===p?'<<< L2 LOAD':q===p+4?'<<< NEXT':''});return out;}
function d0Hints(E,p,back=0x24){const out=[];for(let q=Math.max(0,p-back)&~1;q<p;q+=2){const w=E.r16(q),g=w>>>12;let hint='';if((g===1||g===2||g===3)&&((w>>6)&7)===0&&((w>>9)&7)===0)hint='MOVE -> D0';if((w&0xf100)===0x7000&&((w>>9)&7)===0)hint='MOVEQ -> D0';if(g===13&&((w>>9)&7)===0&&((w>>3)&7)===0&&(w&7)===0)hint='ADD D0,D0';if(g===14&&(w&7)===0)hint='SHIFT/ROT D0';if(hint)out.push({at:E.h(q),offline:E.off(q),word:E.hw(w),hint,distance:p-q});}return out.sort((a,b)=>a.distance-b.distance);}
async function run(){
  stopped=false;await ensure();const E=env(),CAND=0x0080F2;
  console.log('🧱 WOF level2 enemy type tables v1');
  console.log('model: 0x25DC[type×4] -> A4(type table); 0(A4,D0.W) -> A4(handler)');
  const l2Sites=[0x0025C2,0x0025D4];
  const siteRows=[];
  for(const p of l2Sites){const w=E.r16(p),ext=E.r16(p+2),next=p+4,tr=transferAt(E,next);siteRows.push({site:E.h(p),offline:E.off(p),opcode:E.hw(w),extension:E.hw(ext),decoded:'MOVEA.L 0(A4,D0.W),A4',next:E.h(next),nextWord:E.hw(E.r16(next)),nextTransfer:tr?tr.kind:'',nextUsesA4:!!tr?.usesA4});console.log('\n=== L2 SITE '+E.h(p)+' RAW CONTEXT ===');console.table(rawCtx(E,p));console.log('=== D0 PRODUCER HINTS ===');console.table(d0Hints(E,p));}
  console.log('\n=== LEVEL2 DISPATCH SITES ===');console.table(siteRows);
  const types=(E.L.types||[]).map(x=>({type:Number(x.type),base:Number(x.entry??x.liveEntry??0)})).filter(x=>Number.isFinite(x.type)&&Number.isFinite(x.base)).sort((a,b)=>a.type-b.type);
  const rows=[],cand=[];let validPtrs=0,evidencePtrs=0;
  for(let ti=0;ti<types.length;ti++){
    if(stopped)throw new Error('stopped');const t=types[ti];let consecutiveBad=0,seenValid=false;
    for(let d0=0;d0<0x100;d0+=4){const a=t.base+d0;if(a+4>E.MAX)break;const target=E.r32(a),valid=validCode(E,target);if(valid){consecutiveBad=0;seenValid=true;validPtrs++;const pe=refEvidence(E,target);if(pe.refs||(+pe.nearest>=0&&+pe.nearest<0x300))evidencePtrs++;const z={type:t.type,typeTable:E.h(t.base),d0:E.h(d0),stateIndex:d0/4,entryAt:E.h(a),target:E.h(target),offlineTarget:E.off(target),firstOp:E.hw(E.r16(target)),playerRefs:pe.refs,players:pe.players,nearestPlayerRef:pe.nearest,is80F2:target===CAND};rows.push(z);if(target===CAND)cand.push(z);}else{consecutiveBad++;if(seenValid&&consecutiveBad>=4&&d0>=0x20)break;}
    }
    if(ti%8===7)await sleep(0);
  }
  console.log('\n=== SECOND-LEVEL HANDLER POINTERS (valid code targets) ===');console.table(rows.slice(0,260));
  console.log('\n=== 0x0080F2 SECOND-LEVEL REFERENCES ===');console.table(cand);
  const ev=rows.filter(x=>x.playerRefs>0||(+x.nearestPlayerRef>=0&&+x.nearestPlayerRef<0x300)).sort((a,b)=>(b.playerRefs-a.playerRefs)-((+a.nearestPlayerRef||999999)-(+b.nearestPlayerRef||999999)));
  console.log('\n=== LEVEL2 TARGETS WITH PLAYER-REF EVIDENCE ===');console.table(ev.slice(0,120));
  const verdict={types:types.length,l2Sites:l2Sites.length,l2SitesFollowedByA4Transfer:siteRows.filter(x=>x.nextUsesA4).length,validHandlerPointers:validPtrs,candidate80F2Hits:cand.length,candidate80F2Types:[...new Set(cand.map(x=>x.type))].join(','),candidate80F2D0:[...new Set(cand.map(x=>x.d0))].join(','),playerEvidencePointers:evidencePtrs,topEvidenceTarget:ev[0]?.target||'',topEvidenceType:ev[0]?.type??'',topEvidenceD0:ev[0]?.d0||''};
  console.log('\n=== LEVEL2 TABLE VERDICT ===');console.table([verdict]);
  if(cand.length)console.log('🎯 0x0080F2 通过二级 type/state pointer table 可达：它不是 direct-call target，而是 data-driven handler。下一步固定 type + D0/state，并反汇编 0x0080F2。');
  else if(ev.length)console.log('🧭 0x0080F2 不在已解析二级表中；转追 player-ref evidence 最高的真实 handler。');
  else console.warn('⚠️ 二级表有 handler pointers 但没有 player-ref evidence；下一步先解 D0 state 来源与实际执行 transfer。');
  const out={version:'rom-focus-level2-tables-v1',verdict,sites:siteRows,handlers:rows,candidate80F2:cand,evidence:ev};self.__WOF_ROM_FOCUS_LEVEL2=out;return out;
}
self.WOFFOCUSLEVEL2={version:'rom-focus-level2-tables-v1',run,stop(){stopped=true;}};
console.log('✅ WOF ROM focus level2 tables v1 loaded');console.log('执行 await WOFFOCUSLEVEL2.run()');
})();