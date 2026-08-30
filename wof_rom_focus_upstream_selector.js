(()=>{
'use strict';
try{self.WOFFOCUSUPSTREAM?.stop?.();}catch(_){}
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));let stopped=false;
const load=async f=>{const r=await fetch(RAW+f+'?x='+Math.random());if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return (0,eval)(await r.text());};
async function ensure(){
  if(!self.__WOF_ROM_FOCUS_TYPE_FLOW?.reports?.length){await load('wof_rom_focus_type_flow.js');await WOFFOCUSTYPEFLOW.run();}
  if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM state unavailable');
}
function env(){
  const MOD=_0x515056,C=self.__WOF_ROM_LOC_CACHE,M=MOD.HEAPU8,base=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-base),DELTA=C.offlineDelta|0,R=MOD.HEAPU32?.[0x2e39e4>>>2]>>>0;
  if(!R)throw new Error('CPS RAM pointer unavailable');
  const r8=o=>M[base+(SW?(o^1):o)]>>>0,r16=o=>((r8(o)<<8)|r8(o+1))>>>0,r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
  const s8=v=>v&0x80?v-0x100:v,s16=v=>v&0x8000?v-0x10000:v;
  const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0,U16=a=>((B(a)<<8)|B(a+1))>>>0,U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
  const h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0'),off=x=>h((x-DELTA)>>>0),hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
  return{MAX,r8,r16,r32,s8,s16,B,U16,U32,h,off,hw,P:{P1:0xFFBE1C,P2:0xFFBEFC,P3:0xFFBFDC}};
}
function eaWords(m,r,size){if(m<=4)return 0;if(m===5||m===6)return 1;if(m===7){if(r===0||r===2||r===3)return 1;if(r===1)return 2;if(r===4)return size==='L'?2:1;}return 0;}
function decode(E,p){
  const w=E.r16(p),g=w>>>12,m=(w>>3)&7,r=w&7;let len=2,kind='OP',target=null,fall=true,terminal=false,call=false,branch=false,cmp=false,indirect=false;
  if(w===0x4E75||w===0x4E73||w===0x4E77){kind='RET';terminal=true;fall=false;}
  else if(w===0x4E72){kind='STOP';len=4;terminal=true;fall=false;}
  else if((w&0xFFC0)===0x4E80){kind='JSR';call=true;len=2+eaWords(m,r,'L')*2;if(m===7&&r===0)target=E.s16(E.r16(p+2))>>>0;else if(m===7&&r===1)target=E.r32(p+2);else if(m===7&&r===2)target=(p+2+E.s16(E.r16(p+2)))>>>0;else indirect=true;}
  else if((w&0xFFC0)===0x4EC0){kind='JMP';fall=false;len=2+eaWords(m,r,'L')*2;if(m===7&&r===0)target=E.s16(E.r16(p+2))>>>0;else if(m===7&&r===1)target=E.r32(p+2);else if(m===7&&r===2)target=(p+2+E.s16(E.r16(p+2)))>>>0;else indirect=true;}
  else if(g===6){const cc=(w>>8)&15,d=w&255;len=d===0?4:2;target=d===0?p+2+E.s16(E.r16(p+2)):p+2+E.s8(d);kind=cc===0?'BRA':cc===1?'BSR':'BCC';branch=true;if(cc===0)fall=false;if(cc===1)call=true;}
  else if(g===1||g===2||g===3){const size=g===1?'B':g===2?'L':'W',sm=(w>>3)&7,sr=w&7,dm=(w>>6)&7,dr=(w>>9)&7;kind='MOVE';len=2+(eaWords(sm,sr,size)+eaWords(dm,dr,size))*2;}
  else if(g===5){const sz=(w>>6)&3;if(sz===3&&m===1){kind='DBCC';len=4;target=(p+2+E.s16(E.r16(p+2)))>>>0;branch=true;}else len=2+eaWords(m,r,sz===3?'B':sz===2?'L':sz===1?'W':'B')*2;}
  else if(g===0){if([0x003C,0x007C,0x023C,0x027C,0x0A3C,0x0A7C].includes(w))len=4;else if((w&0xF138)===0x0108)len=4;else if((w&0xFF00)===0x0800)len=4+eaWords(m,r,'B')*2;else if((w&0xF100)===0x0100)len=2+eaWords(m,r,'B')*2;else{const op=(w>>8)&15,sz=(w>>6)&3;if([0,2,4,6,10,12].includes(op)){const s=sz===2?'L':sz===1?'W':'B';len=2+(s==='L'?4:2)+eaWords(m,r,s)*2;}}}
  else if(g===4){if((w&0xFFF8)===0x4E50)len=4;else if((w&0xFB80)===0x4880&&m>=2)len=4+eaWords(m,r,(w&0x40)?'L':'W')*2;else if((w&0xF1C0)===0x41C0)len=2+eaWords(m,r,'L')*2;else if((w&0xFFC0)===0x4840&&m!==0)len=2+eaWords(m,r,'L')*2;else len=2+eaWords(m,r,((w>>6)&3)===2?'L':'W')*2;}
  else if(g===8){if((w&0xF1F0)!==0x8100)len=2+eaWords(m,r,((w>>6)&3)===2?'L':'W')*2;}
  else if(g===9||g===13){const special=(w&0xF130)===(g===9?0x9100:0xD100),a=((w>>6)&7)===3||((w>>6)&7)===7;if(!special)len=2+eaWords(m,r,a?(((w>>6)&1)?'L':'W'):(((w>>6)&3)===2?'L':'W'))*2;}
  else if(g===11){const cmpm=(w&0xF138)===0xB108,a=((w>>6)&7)===3||((w>>6)&7)===7;cmp=true;kind='CMP';if(!cmpm)len=2+eaWords(m,r,a?(((w>>6)&1)?'L':'W'):(((w>>6)&3)===2?'L':'W'))*2;}
  else if(g===12){const exg=(w&0xF1F8)===0xC140||(w&0xF1F8)===0xC148||(w&0xF1F8)===0xC188,abcd=(w&0xF1F0)===0xC100;if(!exg&&!abcd)len=2+eaWords(m,r,((w>>6)&3)===2?'L':'W')*2;}
  else if(g===14&&((w>>6)&3)===3)len=2+eaWords(m,r,'W')*2;
  else if(g===10||g===15){kind='LINE';terminal=true;fall=false;}
  len=Math.max(2,len);const next=p+len;if(target!=null&&(target<0||target>=E.MAX))target=null;return{at:p,w,len,next,kind,target,fall,terminal,call,branch,cmp,indirect,m,r};
}
function findStart(E,at){for(let p=at&~1;p>=Math.max(0,at-0x500);p-=2){const w=E.r16(p);if((w&0xFFF8)===0x4E50||w===0x48E7)return p;if(w===0x4E75||w===0x4E73||w===0x4E77)return p+2;}return Math.max(0,(at-0x180)&~1);}
function routine(E,start,cap=0x1800){
  const hi=Math.min(E.MAX,start+cap),q=[start&~1],seen=new Set(),calls=[],ramRefs=[],prefs=[],indirect=[];let cmp=0,branches=0;
  while(q.length&&seen.size<9000){const p=q.shift();if(p<start||p>=hi||(p&1)||seen.has(p))continue;seen.add(p);const d=decode(E,p);if(d.cmp)cmp++;if(d.branch)branches++;if(d.indirect)indirect.push({at:p,kind:d.kind,m:d.m,r:d.r});
    for(let x=d.at+2;x+1<d.next;x+=2){const w=E.r16(x),a16=(w&0x8000)?(0xFF0000|w):w;if(a16>=0xFF0000&&a16<=0xFFFFFC)ramRefs.push({insn:p,at:x,addr:a16,enc:'W'});if(x+3<d.next){const v=E.r32(x);if(v>=0xFF0000&&v<=0xFFFFFC)ramRefs.push({insn:p,at:x,addr:v,enc:'L'});}for(const [name,a] of Object.entries(E.P)){if(a16===a)prefs.push({player:name,insn:p,at:x,enc:'W'});if(x+3<d.next&&E.r32(x)===a)prefs.push({player:name,insn:p,at:x,enc:'L'});}}
    if((d.kind==='JSR'||d.kind==='BSR')&&d.target!=null)calls.push({at:p,target:d.target&~1,kind:d.kind});
    if(d.kind==='BRA'){if(d.target!=null&&d.target>=start&&d.target<hi)q.push(d.target&~1);continue;}if(d.kind==='BCC'||d.kind==='DBCC'){if(d.next<hi)q.push(d.next);if(d.target!=null&&d.target>=start&&d.target<hi)q.push(d.target&~1);continue;}if(d.kind==='JMP'){if(!d.indirect&&d.target!=null&&d.target>=start&&d.target<hi)q.push(d.target&~1);continue;}if(d.terminal)continue;if(d.next<hi)q.push(d.next);
  }
  return{seen,calls:[...new Map(calls.map(x=>[x.at+'|'+x.target,x])).values()],ramRefs:[...new Map(ramRefs.map(x=>[x.insn+'|'+x.addr+'|'+x.enc,x])).values()],prefs,indirect:[...new Map(indirect.map(x=>[x.at+'|'+x.kind,x])).values()],cmp,branches,decoded:seen.size};
}
function rawEdges(E){const map=new Map();const add=(t,e)=>{t&=~1;if(t<0||t>=E.MAX)return;let a=map.get(t);if(!a)map.set(t,a=[]);a.push(e);};for(let p=0;p+6<E.MAX;p+=2){const w=E.r16(p),d=w&255;let t=null,k='';if(w===0x4EB8){t=E.s16(E.r16(p+2))>>>0;k='JSR.W';}else if(w===0x4EB9){t=E.r32(p+2);k='JSR.L';}else if(w===0x4EBA){t=(p+2+E.s16(E.r16(p+2)))>>>0;k='JSR.PC';}else if((w&0xFF00)===0x6100){t=d===0?(p+2+E.s16(E.r16(p+2)))>>>0:(p+2+E.s8(d))>>>0;k=d===0?'BSR.W':'BSR.S';}if(t!=null)add(t,{at:p,kind:k});}return map;}
function pointerEvidence(E,addr){const players=new Set(),hits=[];for(let d=0;d<=0x20;d+=2){const a=(addr+d)>>>0;if(a>0xFFFFFC)break;const v=E.U32(a);for(const [name,p] of Object.entries(E.P))if(v===p){players.add(name);hits.push({slot:a,player:name,value:v,kind:'U32'});}const w=E.U16(a);for(const [name,p] of Object.entries(E.P))if(w===(p&0xffff)){players.add(name);hits.push({slot:a,player:name,value:w,kind:'U16'});}}return{players:[...players].sort(),hits};}
async function run(){
  stopped=false;await ensure();const E=env(),TF=self.__WOF_ROM_FOCUS_TYPE_FLOW;
  const dispatchers=[...new Set((TF.reports||[]).map(x=>parseInt(x.funcStart,16)).filter(Number.isFinite).map(x=>x&~1))];
  console.log('🔙 WOF upstream selector scan v1 · dispatcher callers + live player-pointer RAM');
  console.log('dispatch roots:',dispatchers.map(E.h).join(', '));
  const edgeIndex=rawEdges(E),cache=new Map(),up=new Map();const get=a=>{a&=~1;if(!cache.has(a))cache.set(a,routine(E,a));return cache.get(a);};
  const q=dispatchers.map(a=>({a,depth:0,via:''}));for(const a of dispatchers)up.set(a,{depth:0,via:'dispatch'});
  while(q.length){if(stopped)throw new Error('stopped');const n=q.shift();if(n.depth>=5)continue;for(const e of edgeIndex.get(n.a)||[]){const fs=findStart(E,e.at),r=get(fs);if(!r.seen.has(e.at))continue;const d=decode(E,e.at);if(d.target==null||((d.target&~1)!==(n.a&~1)))continue;const old=up.get(fs);if(!old||n.depth+1<old.depth){up.set(fs,{depth:n.depth+1,via:E.h(e.at)+' '+e.kind+' -> '+E.h(n.a)});q.push({a:fs,depth:n.depth+1,via:e.kind});}}}
  const rows=[];for(const [a,meta] of up){const r=get(a),ptrRows=[];const directPlayers=[...new Set(r.prefs.map(x=>x.player))].sort();for(const rr of r.ramRefs){const pe=pointerEvidence(E,rr.addr);if(pe.players.length)ptrRows.push({insn:E.h(rr.insn),offlineInsn:E.off(rr.insn),ref:E.h(rr.addr),enc:rr.enc,players:pe.players.join(','),hits:pe.hits.length,slots:pe.hits.slice(0,12).map(h=>E.h(h.slot)+':'+h.player+':'+h.kind).join(' ')});}const ptrPlayers=[...new Set(ptrRows.flatMap(x=>x.players.split(',').filter(Boolean)))].sort();const all3Direct=['P1','P2','P3'].every(x=>directPlayers.includes(x)),all3Ptr=['P1','P2','P3'].every(x=>ptrPlayers.includes(x));const score=directPlayers.length*220+ptrPlayers.length*260+(all3Direct?700:0)+(all3Ptr?850:0)+Math.min(30,r.cmp)*10+Math.min(30,r.branches)*2+r.indirect.length*45-Math.min(meta.depth,5)*8;if(directPlayers.length||ptrPlayers.length||r.cmp>=4||r.indirect.length)rows.push({routine:E.h(a),offline:E.off(a),depth:meta.depth,score,directPlayers:directPlayers.join(','),ptrPlayers:ptrPlayers.join(','),ptrRefs:ptrRows.length,all3Direct,all3Ptr,cmp:r.cmp,branches:r.branches,indirect:r.indirect.length,decoded:r.decoded,via:meta.via,ptrRows});}
  rows.sort((a,b)=>b.score-a.score||b.all3Ptr-a.all3Ptr||b.all3Direct-a.all3Direct||b.ptrRefs-a.ptrRefs||b.cmp-a.cmp);const strong=rows.filter(x=>(x.all3Direct||x.all3Ptr)&&x.cmp>=2),top=strong[0]||rows[0]||null;
  console.log('=== UPSTREAM SELECTOR CANDIDATES ===');console.table(rows.slice(0,80).map(({ptrRows,...x})=>x));
  if(top){console.log('=== TOP SHARED PLAYER-POINTER RAM REFS ===');console.table(top.ptrRows);const r=get(parseInt(top.routine,16));console.log('=== TOP DIRECT PLAYER REFS ===');console.table(r.prefs.map(x=>({player:x.player,insn:E.h(x.insn),offline:E.off(x.insn),at:E.h(x.at),enc:x.enc})));console.log('=== TOP REAL INDIRECT SITES ===');console.table(r.indirect.map(x=>({at:E.h(x.at),offline:E.off(x.at),kind:x.kind,mode:x.m,reg:x.r})));}
  const verdict={dispatcherFunctions:dispatchers.length,upstreamRoutines:up.size,candidateRoutines:rows.length,strongCandidates:strong.length,topRoutine:top?.routine||'',topDepth:top?.depth??'',topDirectPlayers:top?.directPlayers||'',topPtrPlayers:top?.ptrPlayers||'',topPtrRefs:top?.ptrRefs??0,topAll3Direct:top?.all3Direct??false,topAll3Ptr:top?.all3Ptr??false,topCmp:top?.cmp??0,topBranches:top?.branches??0,topIndirect:top?.indirect??0,topVia:top?.via||''};
  console.log('=== UPSTREAM SELECTOR VERDICT ===');console.table([verdict]);
  if(strong.length)console.log('🎯 上游发现覆盖 P1/P2/P3 的 selector evidence；下一步只反汇编 topRoutine，解最终 target 寄存器/写回字段。');else if(top?.ptrRefs)console.warn('⚠️ 找到共享 player-pointer RAM evidence，但未同时覆盖三人；下一步沿该 RAM 表的数据流/索引继续。');else console.warn('⚠️ dispatcher 上游仍没有玩家指针 evidence；下一步转动态扫描 enemy struct 中 target handle/target XY 写入点。');
  const out={version:'rom-focus-upstream-selector-v1',verdict,candidates:rows,top};self.__WOF_ROM_FOCUS_UPSTREAM=out;return out;
}
self.WOFFOCUSUPSTREAM={version:'rom-focus-upstream-selector-v1',run,stop(){stopped=true;}};
console.log('✅ WOF upstream selector scan v1 loaded');console.log('执行 await WOFFOCUSUPSTREAM.run()');
})();