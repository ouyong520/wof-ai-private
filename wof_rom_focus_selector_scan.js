(()=>{
'use strict';
try{self.WOFFOCUSSELECTORSCAN?.stop?.();}catch(_){}
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));let stopped=false;
const load=async f=>{const r=await fetch(RAW+f+'?x='+Math.random());if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return (0,eval)(await r.text());};
async function ensure(){
  if(!self.__WOF_ROM_FOCUS_LEVEL2?.handlers?.length){await load('wof_rom_focus_level2_tables.js');await WOFFOCUSLEVEL2.run();}
  if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM state unavailable');
}
function env(){
  const MOD=_0x515056,C=self.__WOF_ROM_LOC_CACHE,M=MOD.HEAPU8,base=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-base),DELTA=C.offlineDelta|0;
  const r8=o=>M[base+(SW?(o^1):o)]>>>0,r16=o=>((r8(o)<<8)|r8(o+1))>>>0,r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
  const s8=v=>v&0x80?v-0x100:v,s16=v=>v&0x8000?v-0x10000:v;
  const h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0'),off=x=>h((x-DELTA)>>>0),hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
  return{MAX,r8,r16,r32,s8,s16,h,off,hw,P:{P1:0x00FFBE1C,P2:0x00FFBEFC,P3:0x00FFBFDC}};
}
function eaWords(mode,reg,size){if(mode<=4)return 0;if(mode===5||mode===6)return 1;if(mode===7){if(reg===0||reg===2||reg===3)return 1;if(reg===1)return 2;if(reg===4)return size==='L'?2:1;}return 0;}
function decode(E,p){
  const w=E.r16(p),g=w>>>12,mode=(w>>3)&7,reg=w&7;let len=2,kind='OP',target=null,fall=true,terminal=false,call=false,branch=false,cmp=false,indirect=false,text=E.hw(w);
  if(w===0x4E75||w===0x4E73||w===0x4E77){terminal=true;fall=false;kind='RET';text=kind;}
  else if(w===0x4E72){len=4;terminal=true;fall=false;kind='STOP';}
  else if((w&0xFFC0)===0x4E80){len=2+eaWords(mode,reg,'L')*2;kind='JSR';call=true;if(mode===7&&reg===0)target=E.s16(E.r16(p+2))>>>0;else if(mode===7&&reg===1)target=E.r32(p+2);else if(mode===7&&reg===2)target=(p+2+E.s16(E.r16(p+2)))>>>0;else indirect=true;text=indirect?'JSR indirect':'JSR direct';}
  else if((w&0xFFC0)===0x4EC0){len=2+eaWords(mode,reg,'L')*2;kind='JMP';fall=false;if(mode===7&&reg===0)target=E.s16(E.r16(p+2))>>>0;else if(mode===7&&reg===1)target=E.r32(p+2);else if(mode===7&&reg===2)target=(p+2+E.s16(E.r16(p+2)))>>>0;else indirect=true;text=indirect?'JMP indirect':'JMP direct';}
  else if(g===6){const cc=(w>>8)&15,d=w&255;len=d===0?4:2;target=d===0?p+2+E.s16(E.r16(p+2)):p+2+E.s8(d);kind=cc===0?'BRA':cc===1?'BSR':'BCC';branch=true;if(cc===0)fall=false;if(cc===1)call=true;text=kind;}
  else if(g===1||g===2||g===3){const size=g===1?'B':g===2?'L':'W',sm=(w>>3)&7,sr=w&7,dm=(w>>6)&7,dr=(w>>9)&7;len=2+(eaWords(sm,sr,size)+eaWords(dm,dr,size))*2;kind='MOVE';}
  else if(g===5){const sz=(w>>6)&3;if(sz===3&&mode===1){len=4;kind='DBCC';target=(p+2+E.s16(E.r16(p+2)))>>>0;branch=true;}else len=2+eaWords(mode,reg,sz===3?'B':sz===2?'L':sz===1?'W':'B')*2;}
  else if(g===0){if([0x003C,0x007C,0x023C,0x027C,0x0A3C,0x0A7C].includes(w))len=4;else if((w&0xF138)===0x0108)len=4;else if((w&0xFF00)===0x0800)len=4+eaWords(mode,reg,'B')*2;else if((w&0xF100)===0x0100)len=2+eaWords(mode,reg,'B')*2;else{const op=(w>>8)&15,sz=(w>>6)&3;if([0,2,4,6,10,12].includes(op)){const s=sz===2?'L':sz===1?'W':'B';len=2+(s==='L'?4:2)+eaWords(mode,reg,s)*2;}}}
  else if(g===4){if((w&0xFFF8)===0x4E50)len=4;else if((w&0xFB80)===0x4880&&mode>=2)len=4+eaWords(mode,reg,(w&0x40)?'L':'W')*2;else if((w&0xF1C0)===0x41C0)len=2+eaWords(mode,reg,'L')*2;else if((w&0xFFC0)===0x4840&&mode!==0)len=2+eaWords(mode,reg,'L')*2;else len=2+eaWords(mode,reg,((w>>6)&3)===2?'L':'W')*2;}
  else if(g===8){if((w&0xF1F0)!==0x8100)len=2+eaWords(mode,reg,((w>>6)&3)===2?'L':'W')*2;}
  else if(g===9||g===13){const special=(w&0xF130)===(g===9?0x9100:0xD100),a=((w>>6)&7)===3||((w>>6)&7)===7;if(!special)len=2+eaWords(mode,reg,a?(((w>>6)&1)?'L':'W'):(((w>>6)&3)===2?'L':'W'))*2;}
  else if(g===11){const cmpm=(w&0xF138)===0xB108,a=((w>>6)&7)===3||((w>>6)&7)===7;cmp=true;kind='CMP';if(!cmpm)len=2+eaWords(mode,reg,a?(((w>>6)&1)?'L':'W'):(((w>>6)&3)===2?'L':'W'))*2;}
  else if(g===12){const exg=(w&0xF1F8)===0xC140||(w&0xF1F8)===0xC148||(w&0xF1F8)===0xC188,abcd=(w&0xF1F0)===0xC100;if(!exg&&!abcd)len=2+eaWords(mode,reg,((w>>6)&3)===2?'L':'W')*2;}
  else if(g===14&&((w>>6)&3)===3)len=2+eaWords(mode,reg,'W')*2;
  else if(g===10||g===15){terminal=true;fall=false;kind='LINE';}
  const next=p+Math.max(2,len);if(target!=null&&(target<0||target>=E.MAX))target=null;return{at:p,w,len:Math.max(2,len),next,kind,target,fall,terminal,call,branch,cmp,indirect,mode,reg,text};
}
function playerRefsInInsn(E,d){
  const out=[];for(let q=d.at+2;q+3<d.next;q+=2){const v=E.r32(q);for(const [name,a] of Object.entries(E.P))if(v===a)out.push({player:name,at:q});}return out;
}
function routine(E,start,cap=0x1400){
  const hi=Math.min(E.MAX,start+cap),q=[start&~1],seen=new Set(),rows=[],calls=[],indirect=[];let cmp=0,branches=0;const prefs=[];
  while(q.length&&seen.size<7000){const p=q.shift();if(p<start||p>=hi||(p&1)||seen.has(p))continue;seen.add(p);const d=decode(E,p);rows.push(d);if(d.cmp)cmp++;if(d.branch)branches++;
    for(const z of playerRefsInInsn(E,d))prefs.push({player:z.player,insn:p,immAt:z.at,word:d.w,kind:d.kind});
    if((d.kind==='JSR'||d.kind==='BSR')&&d.target!=null)calls.push({at:p,target:d.target&~1,kind:d.kind});if(d.indirect)indirect.push({at:p,kind:d.kind,mode:d.mode,reg:d.reg});
    if(d.kind==='BRA'){if(d.target!=null&&d.target>=start&&d.target<hi)q.push(d.target&~1);continue;}
    if(d.kind==='BCC'||d.kind==='DBCC'){if(d.next<hi)q.push(d.next);if(d.target!=null&&d.target>=start&&d.target<hi)q.push(d.target&~1);continue;}
    if(d.kind==='JMP'){if(!d.indirect&&d.target!=null&&d.target>=start&&d.target<hi)q.push(d.target&~1);continue;}
    if(d.terminal)continue;if(d.next<hi)q.push(d.next);
  }
  const players=[...new Set(prefs.map(x=>x.player))].sort();
  return{start,decoded:seen.size,calls:[...new Map(calls.map(x=>[x.at+'|'+x.target,x])).values()],indirect:[...new Map(indirect.map(x=>[x.at+'|'+x.kind,x])).values()],prefs,players,cmp,branches};
}
async function run(){
  stopped=false;await ensure();const E=env(),L2=self.__WOF_ROM_FOCUS_LEVEL2;
  console.log('🎯 WOF selector scan v1 · real level2 handler graph only');
  const rawRoots=(L2.handlers||[]).map(x=>({addr:parseInt(x.target,16)&~1,type:x.type,d0:x.d0,stateIndex:x.stateIndex})).filter(x=>Number.isFinite(x.addr));
  const roots=[...new Map(rawRoots.map(x=>[x.addr+'|'+x.type+'|'+x.d0,x])).values()];
  const cache=new Map(),prov=new Map(),edges=[];
  const get=a=>{a&=~1;if(cache.has(a))return cache.get(a);const r=routine(E,a);cache.set(a,r);return r;};
  for(let i=0;i<roots.length;i++){
    if(stopped)throw new Error('stopped');const root=roots[i],q=[{addr:root.addr,depth:0}],seen=new Set();
    while(q.length){const n=q.shift(),a=n.addr&~1;if(seen.has(a)||n.depth>7)continue;seen.add(a);let pr=prov.get(a);if(!pr)prov.set(a,pr={types:new Set(),states:new Set(),roots:new Set(),minDepth:n.depth});pr.types.add(root.type);pr.states.add(root.type+':'+root.d0);pr.roots.add(root.addr);pr.minDepth=Math.min(pr.minDepth,n.depth);
      const r=get(a);for(const c of r.calls){edges.push({from:a,at:c.at,to:c.target,kind:c.kind});if(n.depth<7&&!seen.has(c.target))q.push({addr:c.target,depth:n.depth+1});}
    }
    if(i%24===23)await sleep(0);
  }
  const candidates=[];
  for(const [a,r] of cache){const pr=prov.get(a);if(!pr)continue;const pset=new Set(r.players),pN=pset.size,all3=['P1','P2','P3'].every(x=>pset.has(x));const score=pN*120+(all3?300:0)+Math.min(20,r.cmp)*10+Math.min(30,r.branches)*2+r.indirect.length*35+Math.min(20,pr.types.size)*3-Math.min(6,pr.minDepth)*2;
    if(pN||r.indirect.length||r.cmp>=4)candidates.push({routine:E.h(a),offline:E.off(a),score,players:r.players.join(','),playerRefCount:r.prefs.length,p1:r.prefs.filter(x=>x.player==='P1').length,p2:r.prefs.filter(x=>x.player==='P2').length,p3:r.prefs.filter(x=>x.player==='P3').length,all3,cmp:r.cmp,branches:r.branches,indirect:r.indirect.length,types:pr.types.size,typeIds:[...pr.types].sort((x,y)=>x-y).join(','),states:pr.states.size,minDepth:pr.minDepth,decoded:r.decoded});}
  candidates.sort((a,b)=>b.score-a.score||b.all3-a.all3||b.playerRefCount-a.playerRefCount||b.cmp-a.cmp);
  console.log('=== REAL HANDLER GRAPH SELECTOR CANDIDATES ===');console.table(candidates.slice(0,120));
  const strong=candidates.filter(x=>x.all3&&x.cmp>=2),top=strong[0]||candidates[0]||null;
  if(top){const a=parseInt(top.routine,16),r=cache.get(a),pr=prov.get(a);console.log('=== TOP CANDIDATE PLAYER REF INSTRUCTIONS ===');console.table(r.prefs.map(x=>({player:x.player,insn:E.h(x.insn),offlineInsn:E.off(x.insn),immAt:E.h(x.immAt),op:E.hw(x.word),kind:x.kind})));console.log('=== TOP CANDIDATE REAL INDIRECT SITES ===');console.table(r.indirect.map(x=>({at:E.h(x.at),offline:E.off(x.at),kind:x.kind,mode:x.mode,reg:x.reg})));console.log('=== TOP CANDIDATE PROVENANCE ===');console.table([{routine:top.routine,typeIds:[...pr.types].sort((x,y)=>x-y).join(','),statePairs:[...pr.states].slice(0,80).join(' '),rootCount:pr.roots.size,minDepth:pr.minDepth}]);}
  const verdict={level2Pointers:(L2.handlers||[]).length,uniqueRootHandlers:new Set(rawRoots.map(x=>x.addr)).size,reachableRoutines:cache.size,candidates:candidates.length,strongAll3Candidates:strong.length,topRoutine:top?.routine||'',topOffline:top?.offline||'',topPlayers:top?.players||'',topCmp:top?.cmp??0,topBranches:top?.branches??0,topIndirect:top?.indirect??0,topTypeIds:top?.typeIds||'',topStates:top?.states??0,topMinDepth:top?.minDepth??''};
  console.log('=== SELECTOR SCAN VERDICT ===');console.table([verdict]);
  if(strong.length)console.log('🎯 找到真实 handler graph 内同时引用 P1/P2/P3 的 selector 候选；下一步只反汇编 topRoutine，解比较顺序和最终 target 寄存器。');
  else if(top&&top.players)console.warn('⚠️ 没有 all3 候选，但已有玩家引用 routine；下一步沿其 direct/indirect 数据流扩展一层。');
  else console.warn('⚠️ 真实 handler graph 内没有直接 P1/P2/P3 指令引用；下一步转查 RAM/结构间接玩家指针与上游 shared selector。');
  const out={version:'rom-focus-selector-scan-v1',verdict,candidates,top:top?{...top,detail:cache.get(parseInt(top.routine,16))}:null};self.__WOF_ROM_FOCUS_SELECTOR_SCAN=out;return out;
}
self.WOFFOCUSSELECTORSCAN={version:'rom-focus-selector-scan-v1',run,stop(){stopped=true;}};
console.log('✅ WOF selector scan v1 loaded');console.log('执行 await WOFFOCUSSELECTORSCAN.run()');
})();