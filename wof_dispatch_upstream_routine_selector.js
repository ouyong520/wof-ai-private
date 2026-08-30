(()=>{
'use strict';
try{self.WOFDISPUP?.stop?.();}catch(_){}
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let stopped=false;
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return (0,eval)(await r.text());};
async function quiet(fn){const L=console.log,T=console.table,W=console.warn;try{console.log=()=>{};console.table=()=>{};console.warn=()=>{};return await fn();}finally{console.log=L;console.table=T;console.warn=W;}}
async function ensure(){
  await quiet(async()=>{
    if(!self.__WOF_DISPATCH_INCOMING)await load('wof_resume_dispatch_selector.js');
    if(!self.__WOF_ROM_FOCUS_LEVEL2?.handlers?.length){await load('wof_rom_focus_level2_tables.js');await WOFFOCUSLEVEL2.run();}
  });
  if(!self.__WOF_DISPATCH_INCOMING?.edges?.length)throw new Error('dispatcher incoming edges unavailable');
  if(!self.__WOF_ROM_FOCUS_LEVEL2?.handlers?.length)throw new Error('level2 handler roots unavailable');
  if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache unavailable');
}
function env(){
  const MOD=_0x515056,C=self.__WOF_ROM_LOC_CACHE,M=MOD.HEAPU8,base=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-base),DELTA=C.offlineDelta|0;
  const r8=o=>M[base+(SW?(o^1):o)]>>>0;
  const r16=o=>((r8(o)<<8)|r8(o+1))>>>0;
  const r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
  const s8=v=>v&0x80?v-0x100:v,s16=v=>v&0x8000?v-0x10000:v;
  const h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0');
  const hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
  const off=x=>h((x-DELTA)>>>0);
  return{MAX,r8,r16,r32,s8,s16,h,hw,off};
}
function eaWords(m,r,size){if(m<=4)return 0;if(m===5||m===6)return 1;if(m===7){if(r===0||r===2||r===3)return 1;if(r===1)return 2;if(r===4)return size==='L'?2:1;}return 0;}
function decode(E,p){
  const w=E.r16(p),g=w>>>12,m=(w>>3)&7,r=w&7;let len=2,kind='OP',target=null,fall=true,terminal=false,call=false,cmp=false,bcc=false;
  if(w===0x4E75||w===0x4E73||w===0x4E77){kind='RET';terminal=true;fall=false;}
  else if(w===0x4E72){kind='STOP';len=4;terminal=true;fall=false;}
  else if((w&0xFFC0)===0x4E80){kind='JSR';call=true;len=2+eaWords(m,r,'L')*2;if(m===7&&r===0)target=E.s16(E.r16(p+2))>>>0;else if(m===7&&r===1)target=E.r32(p+2);else if(m===7&&r===2)target=(p+2+E.s16(E.r16(p+2)))>>>0;}
  else if((w&0xFFC0)===0x4EC0){kind='JMP';fall=false;len=2+eaWords(m,r,'L')*2;if(m===7&&r===0)target=E.s16(E.r16(p+2))>>>0;else if(m===7&&r===1)target=E.r32(p+2);else if(m===7&&r===2)target=(p+2+E.s16(E.r16(p+2)))>>>0;}
  else if(g===6){const cc=(w>>8)&15,d=w&255;len=d===0?4:2;target=d===0?p+2+E.s16(E.r16(p+2)):p+2+E.s8(d);kind=cc===0?'BRA':cc===1?'BSR':'BCC';bcc=cc>=2;if(cc===0)fall=false;if(cc===1)call=true;}
  else if(g===1||g===2||g===3){const size=g===1?'B':g===2?'L':'W',sm=(w>>3)&7,sr=w&7,dm=(w>>6)&7,dr=(w>>9)&7;len=2+(eaWords(sm,sr,size)+eaWords(dm,dr,size))*2;}
  else if(g===5){const sz=(w>>6)&3;if(sz===3&&m===1){kind='DBCC';bcc=true;len=4;target=(p+2+E.s16(E.r16(p+2)))>>>0;}else len=2+eaWords(m,r,sz===3?'B':sz===2?'L':sz===1?'W':'B')*2;}
  else if(g===0){if([0x003C,0x007C,0x023C,0x027C,0x0A3C,0x0A7C].includes(w))len=4;else if((w&0xF138)===0x0108)len=4;else if((w&0xFF00)===0x0800)len=4+eaWords(m,r,'B')*2;else if((w&0xF100)===0x0100)len=2+eaWords(m,r,'B')*2;else{const op=(w>>8)&15,sz=(w>>6)&3;if([0,2,4,6,10,12].includes(op)){const s=sz===2?'L':sz===1?'W':'B';len=2+(s==='L'?4:2)+eaWords(m,r,s)*2;if(op===12)cmp=true;}}}
  else if(g===4){if((w&0xFFF8)===0x4E50)len=4;else if((w&0xFB80)===0x4880&&m>=2)len=4+eaWords(m,r,(w&0x40)?'L':'W')*2;else if((w&0xF1C0)===0x41C0)len=2+eaWords(m,r,'L')*2;else if((w&0xFFC0)===0x4840&&m!==0)len=2+eaWords(m,r,'L')*2;else len=2+eaWords(m,r,((w>>6)&3)===2?'L':'W')*2;}
  else if(g===8){if((w&0xF1F0)!==0x8100)len=2+eaWords(m,r,((w>>6)&3)===2?'L':'W')*2;}
  else if(g===9||g===13){const special=(w&0xF130)===(g===9?0x9100:0xD100),a=((w>>6)&7)===3||((w>>6)&7)===7;if(!special)len=2+eaWords(m,r,a?(((w>>6)&1)?'L':'W'):(((w>>6)&3)===2?'L':'W'))*2;}
  else if(g===11){cmp=true;const cmpm=(w&0xF138)===0xB108,a=((w>>6)&7)===3||((w>>6)&7)===7;if(!cmpm)len=2+eaWords(m,r,a?(((w>>6)&1)?'L':'W'):(((w>>6)&3)===2?'L':'W'))*2;}
  else if(g===12){const exg=(w&0xF1F8)===0xC140||(w&0xF1F8)===0xC148||(w&0xF1F8)===0xC188,abcd=(w&0xF1F0)===0xC100;if(!exg&&!abcd)len=2+eaWords(m,r,((w>>6)&3)===2?'L':'W')*2;}
  else if(g===14&&((w>>6)&3)===3)len=2+eaWords(m,r,'W')*2;
  else if(g===10||g===15){kind='LINE';terminal=true;fall=false;}
  len=Math.max(2,len);const next=p+len;if(target!=null&&(target<0||target>=E.MAX))target=null;return{at:p,w,len,next,kind,target,fall,terminal,call,cmp,bcc};
}
function cfg(E,start,cap=0x1800){
  const hi=Math.min(E.MAX,start+cap),q=[start&~1],seen=new Set(),calls=[];
  while(q.length&&seen.size<9000){const p=q.shift();if(p<0||p>=hi||(p&1)||seen.has(p))continue;seen.add(p);const d=decode(E,p);if((d.kind==='JSR'||d.kind==='BSR')&&d.target!=null)calls.push({at:p,target:d.target&~1,kind:d.kind});if(d.kind==='BRA'){if(d.target!=null&&d.target<hi)q.push(d.target&~1);continue;}if(d.kind==='BCC'||d.kind==='DBCC'){if(d.next<hi)q.push(d.next);if(d.target!=null&&d.target<hi)q.push(d.target&~1);continue;}if(d.kind==='JMP'){if(d.target!=null&&d.target<hi)q.push(d.target&~1);continue;}if(d.terminal)continue;if(d.next<hi)q.push(d.next);}
  return{seen,calls};
}
const PLAYERS=[{id:'P1',l:0x00FFBE1C,w:0xBE1C},{id:'P2',l:0x00FFBEFC,w:0xBEFC},{id:'P3',l:0x00FFBFDC,w:0xBFDC}];
function evidence(E,C){
  const long=new Set(),word=new Set(),refs=[],stride=[],ramHi=[],cmp=[],bcc=[],count3=[];
  const ps=[...C.seen].sort((a,b)=>a-b);
  for(const p of ps){const d=decode(E,p);if(d.cmp)cmp.push(E.h(p));if(d.bcc)bcc.push(E.h(p));for(let q=p;q<Math.min(d.next,E.MAX-3);q+=2){const v32=E.r32(q),v16=E.r16(q);for(const x of PLAYERS){if(v32===x.l){long.add(x.id);refs.push(x.id+'.L@'+E.h(p));}if(v16===x.w){word.add(x.id);refs.push(x.id+'.W@'+E.h(p));}}if(v16===0x00E0)stride.push(E.h(p));if(v16===0xFFBE||v16===0xFFBF)ramHi.push(E.h(p));if(v16===0x0003)count3.push(E.h(p));}}
  const players=[...new Set([...long,...word])];
  const score=long.size*700+word.size*420+(stride.length?300:0)+(ramHi.length?180:0)+(players.length&&stride.length?500:0)+Math.min(cmp.length,8)*18+Math.min(bcc.length,12)*8+(count3.length&&stride.length?120:0);
  return{players:players.join(','),longPlayers:[...long].join(','),wordPlayers:[...word].join(','),refs:[...new Set(refs)].slice(0,12).join(' '),stride:[...new Set(stride)].slice(0,8).join(' '),ramHi:[...new Set(ramHi)].slice(0,8).join(' '),cmp:cmp.length,bcc:bcc.length,count3:count3.length,score};
}
async function run(){
  stopped=false;await ensure();const E=env(),IN=self.__WOF_DISPATCH_INCOMING,L2=self.__WOF_ROM_FOCUS_LEVEL2;
  const roots=[...new Set((L2.handlers||[]).map(x=>parseInt(x.target,16)&~1).filter(Number.isFinite))];
  const routines=new Map(),queue=roots.map(a=>({a,d:0})),seenR=new Set();
  while(queue.length){if(stopped)throw new Error('stopped');const n=queue.shift(),a=n.a&~1;if(seenR.has(a)||n.d>8)continue;seenR.add(a);const C=cfg(E,a);routines.set(a,{...C,depth:n.d});for(const c of C.calls)if(n.d<8&&!seenR.has(c.target))queue.push({a:c.target,d:n.d+1});if((seenR.size&31)===0)await sleep(0);}
  const ev=new Map();for(const [a,C] of routines)ev.set(a,evidence(E,C));
  const callers=new Map();for(const [a,C] of routines){for(const c of C.calls){if(!callers.has(c.target))callers.set(c.target,[]);callers.get(c.target).push({routine:a,at:c.at});}}
  const rows=[];
  for(const edge of IN.edges||[]){const edgeAt=parseInt(edge.at,16);const owners=[];for(const [a,C] of routines)if(C.seen.has(edgeAt))owners.push(a);if(!owners.length){rows.push({edgeAt:edge.at,target:edge.target,kind:edge.kind,prevD0:edge.prevD0||'',owner:'',ownerPlayers:'',ownerStride:'',beforeHelper:'',helperPlayers:'',helperStride:'',caller:'',callerPlayers:'',callerStride:'',score:0});continue;}
    for(const owner of owners){const C=routines.get(owner),oe=ev.get(owner);const before=C.calls.filter(c=>c.at<edgeAt&&routines.has(c.target)).map(c=>({c,e:ev.get(c.target)})).sort((x,y)=>(y.e?.score||0)-(x.e?.score||0));const bestH=before[0]||null;const ups=(callers.get(owner)||[]).filter(x=>routines.has(x.routine)).map(x=>({...x,e:ev.get(x.routine)})).sort((x,y)=>(y.e?.score||0)-(x.e?.score||0));const bestU=ups[0]||null;const score=(oe?.score||0)+Math.round((bestH?.e?.score||0)*0.85)+Math.round((bestU?.e?.score||0)*0.70);
      rows.push({edgeAt:edge.at,target:edge.target,kind:edge.kind,prevD0:edge.prevD0||'',owner:E.h(owner),ownerPlayers:oe?.players||'',ownerRefs:oe?.refs||'',ownerStride:oe?.stride||'',ownerCmp:oe?.cmp||0,ownerBcc:oe?.bcc||0,beforeHelper:bestH?E.h(bestH.c.target):'',helperCallAt:bestH?E.h(bestH.c.at):'',helperPlayers:bestH?.e?.players||'',helperRefs:bestH?.e?.refs||'',helperStride:bestH?.e?.stride||'',helperCmp:bestH?.e?.cmp||0,caller:bestU?E.h(bestU.routine):'',callerAt:bestU?E.h(bestU.at):'',callerPlayers:bestU?.e?.players||'',callerRefs:bestU?.e?.refs||'',callerStride:bestU?.e?.stride||'',callerCmp:bestU?.e?.cmp||0,score});
    }
  }
  rows.sort((a,b)=>b.score-a.score||a.edgeAt.localeCompare(b.edgeAt));
  const signal=rows.filter(r=>r.ownerPlayers||r.ownerStride||r.helperPlayers||r.helperStride||r.callerPlayers||r.callerStride);
  const playerSignal=rows.filter(r=>r.ownerPlayers||r.helperPlayers||r.callerPlayers);
  const strideSignal=rows.filter(r=>r.ownerStride||r.helperStride||r.callerStride);
  const top=signal[0]||rows[0]||null;
  console.log('=== DISPATCH UPSTREAM ROUTINE SELECTOR TOP 20 ===');console.table(rows.slice(0,20));
  const verdict={incomingEdges:(IN.edges||[]).length,reachableRoutines:routines.size,edgesOwnedByRealCfg:rows.filter(r=>r.owner).length,edgesWithPlayerEvidence:playerSignal.length,edgesWithStrideEvidence:strideSignal.length,edgesWithAnyUpstreamSignal:signal.length,topEdgeAt:top?.edgeAt||'',topOwner:top?.owner||'',topBeforeHelper:top?.beforeHelper||'',topCaller:top?.caller||'',topOwnerPlayers:top?.ownerPlayers||'',topHelperPlayers:top?.helperPlayers||'',topCallerPlayers:top?.callerPlayers||'',topOwnerStride:top?.ownerStride||'',topHelperStride:top?.helperStride||'',topCallerStride:top?.callerStride||'',topScore:top?.score||0};
  console.log('=== DISPATCH UPSTREAM ROUTINE VERDICT ===');console.table([verdict]);
  console.log('=== DISPATCH UPSTREAM ROUTINE JSON ===');console.log(JSON.stringify({verdict,rows:rows.slice(0,20)},null,2));
  if(playerSignal.length)console.log('🎯 上游 routine/helper/caller 出现真实 P1/P2/P3 引用；下一步只追 top candidate 的 player compare/branch。');
  else if(strideSignal.length)console.log('🎯 上游出现 0xE0 player-stride 证据；下一步只追 top candidate 的 player loop/base。');
  else console.warn('⚠️ 356-routine 一层邻域仍无 player/stride；下一步转查 dispatcher edge 的 indirect predecessor / shared player-table helper，不回裸 ROM。');
  const out={version:'wof-dispatch-upstream-routine-selector-v1',verdict,rows};self.__WOF_DISPATCH_UPSTREAM_ROUTINE=out;return out;
}
self.WOFDISPUP={version:'wof-dispatch-upstream-routine-selector-v1',run,stop(){stopped=true;}};
console.log('✅ WOF dispatcher upstream routine selector loaded');console.log('执行 await WOFDISPUP.run()');
})();