(()=>{
'use strict';
try{self.WOFFOCUSRTSDISPATCH?.stop?.();}catch(_){}
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
function idx(E,p){const x=E.r16(p+2);return{ext:E.hw(x),kind:(x&0x8000)?'A':'D',reg:(x>>12)&7,size:(x&0x0800)?'L':'W',disp:E.s8(x&255)};}
function validTarget(E,t){return Number.isInteger(t)&&t>=0x40&&t<E.MAX&&(t&1)===0&&![0,0xFFFF,0x4AFC].includes(E.r16(t));}
function playerEvidence(E,t,span=0x500){let n=0;const ps=new Set();let near=0x7fffffff;for(const r of E.L.longRefs||[]){const a=parseInt(r.off,16);if(!Number.isFinite(a))continue;near=Math.min(near,Math.abs(a-t));if(a>=t&&a<t+span){n++;ps.add(r.player);}}return{refs:n,players:[...ps].join(','),nearest:near===0x7fffffff?'':near};}
function tableQuality(E,base,stride=4,count=64){
  const rows=[];let valid=0,all3=0,near=0;
  for(let i=0;i<count;i++){
    const a=base+i*stride;if(a+4>E.MAX)break;const t=E.r32(a);if(!validTarget(E,t))continue;valid++;const pe=playerEvidence(E,t);if(pe.refs)near++;if(pe.players.includes('P1')&&pe.players.includes('P2')&&pe.players.includes('P3'))all3++;
    rows.push({i,tableAt:E.h(a),target:E.h(t),offlineTarget:E.off(t),op:E.hw(E.r16(t)),playerRefs:pe.refs,players:pe.players,nearestPlayerRef:pe.nearest});
  }
  return{base,stride,valid,all3,near,rows};
}
function findBaseForAn(E,p,areg,back=0x60){
  const out=[];
  for(let q=Math.max(0,p-back)&~1;q<p;q+=2){const w=E.r16(q),dst=(w>>9)&7;if(dst!==areg)continue;
    if((w&0xF1FF)===0x41F9){const v=E.r32(q+2);if(v<E.MAX)out.push({at:q,value:v,why:'LEA abs.L'});}
    else if((w&0xF1FF)===0x41FA){const v=(q+2+E.s16(E.r16(q+2)))>>>0;if(v<E.MAX)out.push({at:q,value:v,why:'LEA d16(PC)'});}
    else if((w&0xF1FF)===0x207C){const v=E.r32(q+2);if(v<E.MAX)out.push({at:q,value:v,why:'MOVEA.L #imm'});}
  }
  return out.sort((a,b)=>b.at-a.at);
}
function sourceInfo(E,p){
  const w=E.r16(p),sm=(w>>3)&7,sr=w&7;
  if((w>>>12)!==2)return null;
  if(sm===7&&sr===3){const x=idx(E,p),base=(p+2+x.disp)>>>0;return{form:'PC_INDEX',base,index:x.kind+x.reg+'.'+x.size,indexKind:x.kind,indexReg:x.reg,indexSize:x.size,disp:x.disp,len:4,why:'d8(PC,Xn)'};}
  if(sm===6){const x=idx(E,p),bs=findBaseForAn(E,p,sr),b=bs[0];return{form:'A_INDEX',base:b?((b.value+x.disp)>>>0):null,index:x.kind+x.reg+'.'+x.size,indexKind:x.kind,indexReg:x.reg,indexSize:x.size,disp:x.disp,len:4,areg:sr,baseWriter:b?E.h(b.at):'',why:b?(x.disp+'(A'+sr+',Xn) <- '+b.why):('A'+sr+' unresolved')};}
  if(sm===7&&sr===1)return{form:'ABS_L',base:E.r32(p+2),index:'',len:6,why:'abs.L'};
  if(sm===7&&sr===2)return{form:'PC_D16',base:(p+2+E.s16(E.r16(p+2)))>>>0,index:'',len:4,why:'d16(PC)'};
  return null;
}
function stackDest(w){const dm=(w>>6)&7,dr=(w>>9)&7;if(dr!==7)return null;if(dm===4)return'-(A7)';if(dm===2)return'(A7)';if(dm===5)return'd16(A7)';return null;}
function directStackDispatch(E,p){
  const w=E.r16(p);if((w>>>12)!==2)return null;const dst=stackDest(w);if(!dst)return null;const src=sourceInfo(E,p);if(!src||!src.index)return null;
  // indexed source has one extension word; destination -(A7)/(A7) has no extension. d16(A7) needs one extra word and is not treated as direct return-slot here.
  if(dst==='d16(A7)')return null;const next=p+src.len;
  let rtsAt=-1;for(let q=next;q<=Math.min(E.MAX-2,next+8);q+=2){const x=E.r16(q);if(x===0x4E75){rtsAt=q;break;}if(x===0x4E71)continue;break;}
  if(rtsAt<0)return null;
  return{at:p,op:w,dst,src,rtsAt,pattern:dst==='-(A7)'?'PUSH_HANDLER_RTS':'REPLACE_RETURN_RTS'};
}
function regThenStack(E,p){
  const w=E.r16(p);if((w>>>12)!==2)return null;const dm=(w>>6)&7,dr=(w>>9)&7;if(dm!==0)return null;const src=sourceInfo(E,p);if(!src||!src.index)return null;
  // Look for MOVE.L Ddr,-(A7)/(A7), then RTS, allowing up to 3 simple 2-byte ops in between.
  for(let q=p+src.len;q<=Math.min(E.MAX-4,p+src.len+12);q+=2){const w2=E.r16(q);if((w2>>>12)===2&&((w2>>3)&7)===0&&(w2&7)===dr){const dst=stackDest(w2);if(dst==='-(A7)'||dst==='(A7)'){for(let z=q+2;z<=Math.min(E.MAX-2,q+8);z+=2){const wz=E.r16(z);if(wz===0x4E75)return{at:p,op:w,dst,src,rtsAt:z,viaReg:'D'+dr,stackAt:q,pattern:dst==='-(A7)'?'REG_PUSH_RTS':'REG_REPLACE_RETURN_RTS'};if(wz===0x4E71)continue;break;}}}
    if(w2===0x4E75||w2===0x4E73||w2===0x4E77)break;
  }
  return null;
}
function scanAll(E){
  const hits=[];
  for(let b=0;b<E.MAX;b+=0x8000){const end=Math.min(E.MAX,b+0x8000);for(let p=b&~1;p+8<end;p+=2){const a=directStackDispatch(E,p)||regThenStack(E,p);if(a)hits.push(a);} }
  return hits;
}
function classify(E,h){
  const src=h.src,bases=[];if(src.base!=null&&src.base<E.MAX){for(const stride of [4,2]){const q=tableQuality(E,src.base,stride,64);bases.push(q);}}
  bases.sort((a,b)=>b.valid-a.valid||b.near-a.near);const best=bases[0]||{valid:0,near:0,all3:0,rows:[]};
  const known=Math.abs((src.base??-999999)-E.dispatch)<=8;
  let score=best.valid*5+best.near*15+best.all3*30+(known?150:0)+(h.pattern.includes('PUSH')?25:10);
  if(src.indexSize==='W')score+=8;
  return{...h,knownTypeTable:known,bestTable:best,score};
}
function nearestType(E,p){let z=null;for(const x of E.L.types||[]){const a=Number(x.entry??x.liveEntry??0),d=Math.abs(a-p);if(!z||d<z.d)z={type:x.type,entry:a,d};}return z;}
async function run(){
  stopped=false;await ensure();const E=env();console.log('🪜 WOF RTS trampoline dispatch scanner v1');
  const old=self.__WOF_ROM_FOCUS_TYPE_DISPATCH;
  console.log('=== RAW 0x25DC REFS FROM PREVIOUS STEP (dedup by address) ===');
  const ded=[...new Map((old?.refs||[]).map(x=>[x.at,x])).values()];console.table(ded.map(x=>({at:E.h(x.at),offline:E.off(x.at),kind:x.kind,index:x.index||'',dst:x.dst||'',dstMode:x.dstMode??'',dstReg:x.dstReg??'',score:x.score})));
  const raw=scanAll(E),hits=raw.map(x=>classify(E,x)).sort((a,b)=>b.score-a.score||a.at-b.at);
  const rows=hits.map((x,i)=>{const nt=nearestType(E,x.at),q=x.bestTable;return{rank:i+1,site:E.h(x.at),offline:E.off(x.at),pattern:x.pattern,source:x.src.why,index:x.src.index,tableBase:x.src.base==null?'':E.h(x.src.base),known25DC:x.knownTypeTable,rtsAt:E.h(x.rtsAt),validPtr:q.valid,playerTargets:q.near,all3Targets:q.all3,nearestType:nt?.type,nearestTypeDist:nt?.d,score:x.score};});
  console.log('=== RTS TRAMPOLINE DISPATCH SITES ===');console.table(rows.slice(0,120));
  const knownHits=hits.filter(x=>x.knownTypeTable);console.log('=== CONFIRMED 0x25DC TYPE-DISPATCH TRAMPOLINES ===');console.table(knownHits.map(x=>({site:E.h(x.at),pattern:x.pattern,index:x.src.index,base:E.h(x.src.base),rtsAt:E.h(x.rtsAt),validPtr:x.bestTable.valid,score:x.score})));
  const state=hits.filter(x=>!x.knownTypeTable&&x.bestTable.valid>=4);console.log('=== OTHER POINTER-TABLE RTS DISPATCH CANDIDATES ===');console.table(state.slice(0,80).map(x=>({site:E.h(x.at),offline:E.off(x.at),pattern:x.pattern,index:x.src.index,tableBase:E.h(x.src.base),validPtr:x.bestTable.valid,playerTargets:x.bestTable.near,all3Targets:x.bestTable.all3,score:x.score})));
  const evidence=[];for(const x of state.slice(0,40)){for(const r of x.bestTable.rows.filter(r=>r.playerRefs>0||(+r.nearestPlayerRef>=0&&+r.nearestPlayerRef<0x500)))evidence.push({dispatchSite:E.h(x.at),tableBase:E.h(x.src.base),index:x.src.index,entry:r.i,target:r.target,offlineTarget:r.offlineTarget,playerRefs:r.playerRefs,players:r.players,nearestPlayerRef:r.nearestPlayerRef});}
  console.log('=== RTS-DISPATCH TARGETS WITH PLAYER-REF EVIDENCE ===');console.table(evidence.slice(0,160));
  const verdict={typeTable:E.h(E.dispatch),rawTypeRefs:ded.length,rtsDispatchSites:hits.length,confirmedTypeDispatch:knownHits.length,otherPointerDispatch:state.length,playerEvidenceTargets:evidence.length,topOtherSite:state[0]?E.h(state[0].at):'',topOtherTable:state[0]?E.h(state[0].src.base):'',topOtherIndex:state[0]?.src.index||'',topOtherValidPtrs:state[0]?.bestTable.valid||0,topOtherPlayerTargets:state[0]?.bestTable.near||0};
  console.log('=== RTS DISPATCH VERDICT ===');console.table([verdict]);
  if(knownHits.length)console.log('✅ 已证实 0x25DC 使用 RTS trampoline 分发；indirect JSR/JMP=0 不再是障碍。');
  if(evidence.length)console.log('🎯 找到其他 RTS pointer-table dispatch 且 targets 接近/包含 P1/P2/P3 refs；下一步沿这些 state tables 追 selector。');
  else if(state.length)console.log('🧭 找到其他 pointer-table RTS dispatch；下一步逐表解析 handler graph，再反向找 player refs。');
  else console.warn('⚠️ 未发现其他高密度 pointer-table RTS dispatch；下一步扩展到 offset-table + BRA/RTS trampoline 变体。');
  const out={version:'rom-focus-rts-dispatch-v1',verdict,typeRefs:ded,sites:rows,known:knownHits.map(x=>({at:E.h(x.at),base:E.h(x.src.base),index:x.src.index,pattern:x.pattern})),state:state.map(x=>({at:E.h(x.at),base:E.h(x.src.base),index:x.src.index,pattern:x.pattern,valid:x.bestTable.valid,near:x.bestTable.near,rows:x.bestTable.rows})),evidence};self.__WOF_ROM_FOCUS_RTS_DISPATCH=out;return out;
}
self.WOFFOCUSRTSDISPATCH={version:'rom-focus-rts-dispatch-v1',run,stop(){stopped=true;}};
console.log('✅ WOF ROM focus RTS-dispatch v1 loaded');console.log('执行 await WOFFOCUSRTSDISPATCH.run()');
})();