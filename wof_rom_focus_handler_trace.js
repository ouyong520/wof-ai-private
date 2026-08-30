(()=>{
'use strict';
try{self.WOFFOCUSHANDLERTRACE?.stop?.();}catch(_){}
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));let stopped=false;
const load=async f=>{const r=await fetch(RAW+f+'?x='+Math.random());if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return (0,eval)(await r.text());};
async function ensure(){if(!self.__WOF_ROM_FOCUS_LEVEL2?.handlers?.length){await load('wof_rom_focus_level2_tables.js');await WOFFOCUSLEVEL2.run();}if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM state unavailable');}
function env(){const MOD=_0x515056,C=self.__WOF_ROM_LOC_CACHE,M=MOD.HEAPU8,base=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-base),DELTA=C.offlineDelta|0;const r8=o=>M[base+(SW?(o^1):o)]>>>0,r16=o=>((r8(o)<<8)|r8(o+1))>>>0,r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0,s8=v=>v&0x80?v-0x100:v,s16=v=>v&0x8000?v-0x10000:v,h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0'),off=x=>h((x-DELTA)>>>0);return{MAX,r8,r16,r32,s8,s16,h,off};}
function eaWords(mode,reg,size){if(mode<=4)return 0;if(mode===5||mode===6)return 1;if(mode===7){if(reg===0||reg===2||reg===3)return 1;if(reg===1)return 2;if(reg===4)return size==='L'?2:1;}return 0;}
function decode(E,p){const w=E.r16(p),g=w>>>12,mode=(w>>3)&7,reg=w&7;let len=2,kind='OP',target=null,fall=true,terminal=false,call=false;
 if(w===0x4E75||w===0x4E73||w===0x4E77){terminal=true;fall=false;kind='RET';}
 else if(w===0x4E72){len=4;terminal=true;fall=false;kind='STOP';}
 else if((w&0xFFC0)===0x4E80){len=2+eaWords(mode,reg,'L')*2;kind='JSR';call=true;if(mode===7&&reg===0)target=E.s16(E.r16(p+2))>>>0;else if(mode===7&&reg===1)target=E.r32(p+2);else if(mode===7&&reg===2)target=(p+2+E.s16(E.r16(p+2)))>>>0;}
 else if((w&0xFFC0)===0x4EC0){len=2+eaWords(mode,reg,'L')*2;kind='JMP';fall=false;if(mode===7&&reg===0)target=E.s16(E.r16(p+2))>>>0;else if(mode===7&&reg===1)target=E.r32(p+2);else if(mode===7&&reg===2)target=(p+2+E.s16(E.r16(p+2)))>>>0;}
 else if(g===6){const cc=(w>>8)&15,d=w&255;len=d===0?4:2;target=d===0?p+2+E.s16(E.r16(p+2)):p+2+E.s8(d);kind=cc===0?'BRA':cc===1?'BSR':'BCC';if(cc===0)fall=false;if(cc===1)call=true;}
 else if(g===1||g===2||g===3){const size=g===1?'B':g===2?'L':'W',sm=(w>>3)&7,sr=w&7,dm=(w>>6)&7,dr=(w>>9)&7;len=2+(eaWords(sm,sr,size)+eaWords(dm,dr,size))*2;kind='MOVE';}
 else if(g===5){const sz=(w>>6)&3;if(sz===3&&mode===1){len=4;kind='DBCC';target=(p+2+E.s16(E.r16(p+2)))>>>0;}else len=2+eaWords(mode,reg,sz===3?'B':sz===2?'L':sz===1?'W':'B')*2;}
 else if(g===0){if([0x003C,0x007C,0x023C,0x027C,0x0A3C,0x0A7C].includes(w))len=4;else if((w&0xF138)===0x0108)len=4;else if((w&0xFF00)===0x0800)len=4+eaWords(mode,reg,'B')*2;else if((w&0xF100)===0x0100)len=2+eaWords(mode,reg,'B')*2;else{const op=(w>>8)&15,sz=(w>>6)&3;if([0,2,4,6,10,12].includes(op)){const s=sz===2?'L':sz===1?'W':'B';len=2+(s==='L'?4:2)+eaWords(mode,reg,s)*2;}}}
 else if(g===4){if((w&0xFFF8)===0x4E50)len=4;else if((w&0xFB80)===0x4880&&mode>=2)len=4+eaWords(mode,reg,(w&0x40)?'L':'W')*2;else if((w&0xF1C0)===0x41C0)len=2+eaWords(mode,reg,'L')*2;else if((w&0xFFC0)===0x4840&&mode!==0)len=2+eaWords(mode,reg,'L')*2;else len=2+eaWords(mode,reg,((w>>6)&3)===2?'L':'W')*2;}
 else if(g===8){if((w&0xF1F0)!==0x8100)len=2+eaWords(mode,reg,((w>>6)&3)===2?'L':'W')*2;}
 else if(g===9||g===13){const special=(w&0xF130)===(g===9?0x9100:0xD100);const a=((w>>6)&7)===3||((w>>6)&7)===7;if(!special)len=2+eaWords(mode,reg,a?(((w>>6)&1)?'L':'W'):(((w>>6)&3)===2?'L':'W'))*2;}
 else if(g===11){const cmpm=(w&0xF138)===0xB108,a=((w>>6)&7)===3||((w>>6)&7)===7;if(!cmpm)len=2+eaWords(mode,reg,a?(((w>>6)&1)?'L':'W'):(((w>>6)&3)===2?'L':'W'))*2;}
 else if(g===12){const exg=(w&0xF1F8)===0xC140||(w&0xF1F8)===0xC148||(w&0xF1F8)===0xC188,abcd=(w&0xF1F0)===0xC100;if(!exg&&!abcd)len=2+eaWords(mode,reg,((w>>6)&3)===2?'L':'W')*2;}
 else if(g===14&&((w>>6)&3)===3)len=2+eaWords(mode,reg,'W')*2;
 else if(g===10||g===15){terminal=true;fall=false;kind='LINE';}
 const next=p+len;if(target!=null&&(target<0||target>=E.MAX))target=null;return{at:p,len,next,kind,target,fall,terminal,call};}
function routineCalls(E,start,cap=0x1400){const hi=Math.min(E.MAX,start+cap),q=[start&~1],seen=new Set(),calls=[];while(q.length&&seen.size<6000){const p=q.shift();if(p<start||p>=hi||(p&1)||seen.has(p))continue;seen.add(p);const d=decode(E,p);
  if((d.kind==='JSR'||d.kind==='BSR')&&d.target!=null)calls.push({at:p,target:d.target&~1,kind:d.kind});
  if(d.kind==='BRA'){if(d.target!=null&&d.target>=start&&d.target<hi)q.push(d.target&~1);continue;}
  if(d.kind==='BCC'||d.kind==='DBCC'){if(d.next<hi)q.push(d.next);if(d.target!=null&&d.target>=start&&d.target<hi)q.push(d.target&~1);continue;}
  if(d.kind==='JMP'){if(d.target!=null&&d.target>=start&&d.target<hi)q.push(d.target&~1);continue;}
  if(d.terminal)continue;if(d.next<hi)q.push(d.next);
 }return{calls:[...new Map(calls.map(x=>[x.at+'|'+x.target,x])).values()],decoded:seen.size};}
async function run(){stopped=false;await ensure();const E=env(),L2=self.__WOF_ROM_FOCUS_LEVEL2,CAND=0x0080F2;
 console.log('🧬 WOF real-handler → 0x0080F2 direct trace v1');
 const roots=[...new Map((L2.handlers||[]).map(x=>[parseInt(x.target,16),x])).entries()].filter(([a])=>Number.isFinite(a)).map(([a,x])=>({addr:a&~1,type:x.type,d0:x.d0,stateIndex:x.stateIndex}));
 const cache=new Map(),paths=[];let expandedTotal=0;
 const get=a=>{a&=~1;if(cache.has(a))return cache.get(a);const r=routineCalls(E,a);cache.set(a,r);return r;};
 for(let i=0;i<roots.length;i++){if(stopped)throw new Error('stopped');const root=roots[i],q=[{addr:root.addr,path:[root.addr],edges:[]}],seen=new Set();let expanded=0,hit=null;
   while(q.length&&expanded<2500){const n=q.shift(),a=n.addr&~1;if(seen.has(a)||n.edges.length>7)continue;seen.add(a);expanded++;expandedTotal++;if(a===CAND){hit=n;break;}const r=get(a);for(const c of r.calls){const edge={from:a,at:c.at,target:c.target,kind:c.kind};if(c.target===CAND){hit={addr:CAND,path:[...n.path,CAND],edges:[...n.edges,edge]};q.length=0;break;}if(n.edges.length<7&&!seen.has(c.target))q.push({addr:c.target,path:[...n.path,c.target],edges:[...n.edges,edge]});}}
   if(hit)paths.push({root:E.h(root.addr),type:root.type,d0:root.d0,stateIndex:root.stateIndex,depth:hit.edges.length,path:hit.path.map(E.h).join(' → '),callSites:hit.edges.map(e=>E.h(e.at)).join(' → '),kinds:hit.edges.map(e=>e.kind).join(' → ')});
   if(i%20===19)await sleep(0);
 }
 console.log('=== REAL HANDLER → 0x0080F2 PATHS ===');console.table(paths.slice(0,160));
 const byType=[...new Set(paths.map(x=>x.type))],byRoot=[...new Set(paths.map(x=>x.root))];
 const verdict={level2Pointers:(L2.handlers||[]).length,uniqueRealHandlers:roots.length,decodedRoutines:cache.size,expandedRoutines:expandedTotal,handlerPaths:paths.length,handlerRoots:byRoot.length,typesReaching80F2:byType.length,typeIds:byType.join(','),minDepth:paths.length?Math.min(...paths.map(x=>x.depth)):'',topRoot:paths[0]?.root||'',topType:paths[0]?.type??'',topD0:paths[0]?.d0||'',topPath:paths[0]?.path||''};
 console.log('=== REAL HANDLER TRACE VERDICT ===');console.table([verdict]);
 if(paths.length)console.log('🎯 handlerPaths > 0：0x0080F2 仍可从真实二级 handler 沿 direct call graph 到达；下一步固定最短 type/state/path，反汇编 0x0080F2 的 P1/P2/P3 比较与最终 target 寄存器。');
 else console.warn('❌ handlerPaths == 0：在 625 二级表指针对应的真实 handler roots 上仍无法 direct-call 到 0x0080F2；可正式排除它作为 direct selector，转筛 625 handlers/callees 的 P1/P2/P3 selector evidence。');
 const out={version:'rom-focus-handler-trace-v1',verdict,paths};self.__WOF_ROM_FOCUS_HANDLER_TRACE=out;return out;}
self.WOFFOCUSHANDLERTRACE={version:'rom-focus-handler-trace-v1',run,stop(){stopped=true;}};
console.log('✅ WOF real-handler trace v1 loaded');console.log('执行 await WOFFOCUSHANDLERTRACE.run()');
})();