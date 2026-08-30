(()=>{
'use strict';
try{self.WOFTARGETXYWRITE?.stop?.();}catch(_){}
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));let stopped=false;
const load=async f=>{const r=await fetch(RAW+f+'?x='+Math.random());if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return (0,eval)(await r.text());};
async function ensure(){if(!self.__WOF_ROM_FOCUS_LEVEL2?.handlers?.length){await load('wof_rom_focus_level2_tables.js');await WOFFOCUSLEVEL2.run();}if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM state unavailable');}
function env(){const MOD=_0x515056,C=self.__WOF_ROM_LOC_CACHE,M=MOD.HEAPU8,base=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-base),DELTA=C.offlineDelta|0;
 const r8=o=>M[base+(SW?(o^1):o)]>>>0,r16=o=>((r8(o)<<8)|r8(o+1))>>>0,r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0,s8=v=>v&0x80?v-0x100:v,s16=v=>v&0x8000?v-0x10000:v,h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0'),off=x=>h((x-DELTA)>>>0),hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');return{MAX,r8,r16,r32,s8,s16,h,off,hw};}
function eaWords(m,r,size){if(m<=4)return 0;if(m===5||m===6)return 1;if(m===7){if(r===0||r===2||r===3)return 1;if(r===1)return 2;if(r===4)return size==='L'?2:1;}return 0;}
function regName(m,r){return m===0?'D'+r:m===1?'A'+r:null;}
function moveInfo(E,p,w){const g=w>>>12;if(g!==1&&g!==2&&g!==3)return null;const size=g===1?'B':g===2?'L':'W',sm=(w>>3)&7,sr=w&7,dm=(w>>6)&7,dr=(w>>9)&7,sw=eaWords(sm,sr,size),dw=eaWords(dm,dr,size),dstExt=p+2+sw*2;let disp=null;if(dm===5)disp=E.s16(E.r16(dstExt));return{size,sm,sr,dm,dr,sw,dw,dstExt,disp,srcReg:regName(sm,sr),dstReg:regName(dm,dr)};}
function singleEaWrite(E,p,w){const g=w>>>12,m=(w>>3)&7,r=w&7;let size='W',extBase=p+2,kind='';
 if(g===5&&((w>>6)&3)!==3){size=((w>>6)&3)===2?'L':((w>>6)&3)===1?'W':'B';kind='ADDQ/SUBQ';}
 else if(g===4&&(((w&0xff00)===0x4200)||((w&0xff00)===0x4400)||((w&0xff00)===0x4600))){size=((w>>6)&3)===2?'L':((w>>6)&3)===1?'W':'B';kind='CLR/NEG/NOT';}
 else if(g===0){const op=(w>>8)&15,sz=(w>>6)&3;if([0,2,4,6,10].includes(op)&&sz!==3){size=sz===2?'L':sz===1?'W':'B';extBase=p+2+(size==='L'?4:2);kind='IMM-EA';}else return null;}
 else return null;
 if(m!==5)return null;return{kind,size,baseReg:'A'+r,disp:E.s16(E.r16(extBase))};}
function decode(E,p){const w=E.r16(p),g=w>>>12,m=(w>>3)&7,r=w&7;let len=2,kind='OP',target=null,fall=true,terminal=false,call=false,branch=false,move=null;
 if(w===0x4E75||w===0x4E73||w===0x4E77){kind='RET';terminal=true;fall=false;}
 else if(w===0x4E72){kind='STOP';len=4;terminal=true;fall=false;}
 else if((w&0xFFC0)===0x4E80){kind='JSR';call=true;len=2+eaWords(m,r,'L')*2;if(m===7&&r===0)target=E.s16(E.r16(p+2))>>>0;else if(m===7&&r===1)target=E.r32(p+2);else if(m===7&&r===2)target=(p+2+E.s16(E.r16(p+2)))>>>0;}
 else if((w&0xFFC0)===0x4EC0){kind='JMP';fall=false;len=2+eaWords(m,r,'L')*2;if(m===7&&r===0)target=E.s16(E.r16(p+2))>>>0;else if(m===7&&r===1)target=E.r32(p+2);else if(m===7&&r===2)target=(p+2+E.s16(E.r16(p+2)))>>>0;}
 else if(g===6){const cc=(w>>8)&15,d=w&255;len=d===0?4:2;target=d===0?p+2+E.s16(E.r16(p+2)):p+2+E.s8(d);kind=cc===0?'BRA':cc===1?'BSR':'BCC';branch=true;if(cc===0)fall=false;if(cc===1)call=true;}
 else if(g===1||g===2||g===3){move=moveInfo(E,p,w);len=2+(move.sw+move.dw)*2;kind='MOVE';}
 else if(g===5){const sz=(w>>6)&3;if(sz===3&&m===1){kind='DBCC';len=4;target=(p+2+E.s16(E.r16(p+2)))>>>0;branch=true;}else len=2+eaWords(m,r,sz===3?'B':sz===2?'L':sz===1?'W':'B')*2;}
 else if(g===0){if([0x003C,0x007C,0x023C,0x027C,0x0A3C,0x0A7C].includes(w))len=4;else if((w&0xF138)===0x0108)len=4;else if((w&0xFF00)===0x0800)len=4+eaWords(m,r,'B')*2;else if((w&0xF100)===0x0100)len=2+eaWords(m,r,'B')*2;else{const op=(w>>8)&15,sz=(w>>6)&3;if([0,2,4,6,10,12].includes(op)){const s=sz===2?'L':sz===1?'W':'B';len=2+(s==='L'?4:2)+eaWords(m,r,s)*2;}}}
 else if(g===4){if((w&0xFFF8)===0x4E50)len=4;else if((w&0xFB80)===0x4880&&m>=2)len=4+eaWords(m,r,(w&0x40)?'L':'W')*2;else if((w&0xF1C0)===0x41C0)len=2+eaWords(m,r,'L')*2;else if((w&0xFFC0)===0x4840&&m!==0)len=2+eaWords(m,r,'L')*2;else len=2+eaWords(m,r,((w>>6)&3)===2?'L':'W')*2;}
 else if(g===8){if((w&0xF1F0)!==0x8100)len=2+eaWords(m,r,((w>>6)&3)===2?'L':'W')*2;}
 else if(g===9||g===13){const special=(w&0xF130)===(g===9?0x9100:0xD100),a=((w>>6)&7)===3||((w>>6)&7)===7;if(!special)len=2+eaWords(m,r,a?(((w>>6)&1)?'L':'W'):(((w>>6)&3)===2?'L':'W'))*2;}
 else if(g===11){const cmpm=(w&0xF138)===0xB108,a=((w>>6)&7)===3||((w>>6)&7)===7;if(!cmpm)len=2+eaWords(m,r,a?(((w>>6)&1)?'L':'W'):(((w>>6)&3)===2?'L':'W'))*2;}
 else if(g===12){const exg=(w&0xF1F8)===0xC140||(w&0xF1F8)===0xC148||(w&0xF1F8)===0xC188,abcd=(w&0xF1F0)===0xC100;if(!exg&&!abcd)len=2+eaWords(m,r,((w>>6)&3)===2?'L':'W')*2;}
 else if(g===14&&((w>>6)&3)===3)len=2+eaWords(m,r,'W')*2;
 else if(g===10||g===15){kind='LINE';terminal=true;fall=false;}
 len=Math.max(2,len);const next=p+len;if(target!=null&&(target<0||target>=E.MAX))target=null;return{at:p,w,len,next,kind,target,fall,terminal,call,branch,move};}
function routine(E,start,cap=0x1400){const hi=Math.min(E.MAX,start+cap),q=[start&~1],seen=new Set(),calls=[],writes=[];while(q.length&&seen.size<7000){const p=q.shift();if(p<start||p>=hi||(p&1)||seen.has(p))continue;seen.add(p);const d=decode(E,p),w=d.w;
  if(d.move&&d.move.dm===5&&(d.move.disp===0x3e||d.move.disp===0x42)){writes.push({at:p,kind:'MOVE.'+d.move.size,baseReg:'A'+d.move.dr,disp:d.move.disp,srcReg:d.move.srcReg||'',op:w});}
  const se=singleEaWrite(E,p,w);if(se&&(se.disp===0x3e||se.disp===0x42))writes.push({at:p,kind:se.kind+'.'+se.size,baseReg:se.baseReg,disp:se.disp,srcReg:'',op:w});
  if((d.kind==='JSR'||d.kind==='BSR')&&d.target!=null)calls.push({at:p,target:d.target&~1,kind:d.kind});
  if(d.kind==='BRA'){if(d.target!=null&&d.target>=start&&d.target<hi)q.push(d.target&~1);continue;}if(d.kind==='BCC'||d.kind==='DBCC'){if(d.next<hi)q.push(d.next);if(d.target!=null&&d.target>=start&&d.target<hi)q.push(d.target&~1);continue;}if(d.kind==='JMP'){if(d.target!=null&&d.target>=start&&d.target<hi)q.push(d.target&~1);continue;}if(d.terminal)continue;if(d.next<hi)q.push(d.next);
 }return{decoded:seen.size,calls:[...new Map(calls.map(x=>[x.at+'|'+x.target,x])).values()],writes:[...new Map(writes.map(x=>[x.at+'|'+x.disp,x])).values()]};}
function ctx(E,p){const out=[];for(let q=Math.max(0,p-0x10)&~1;q<=Math.min(E.MAX-2,p+0x14);q+=2)out.push({at:E.h(q),offline:E.off(q),word:E.hw(E.r16(q)),mark:q===p?'<<< WRITE':''});return out;}
async function run(){stopped=false;await ensure();const E=env(),L2=self.__WOF_ROM_FOCUS_LEVEL2;console.log('🧭 WOF target XY writer scan · real handler graph only');
 const raw=(L2.handlers||[]).map(x=>({addr:parseInt(x.target,16)&~1,type:x.type,d0:x.d0})).filter(x=>Number.isFinite(x.addr)),roots=[...new Map(raw.map(x=>[x.addr+'|'+x.type+'|'+x.d0,x])).values()],cache=new Map(),prov=new Map();const get=a=>{a&=~1;if(!cache.has(a))cache.set(a,routine(E,a));return cache.get(a);};
 for(let i=0;i<roots.length;i++){if(stopped)throw new Error('stopped');const root=roots[i],q=[{a:root.addr,d:0}],seen=new Set();while(q.length){const n=q.shift(),a=n.a&~1;if(seen.has(a)||n.d>7)continue;seen.add(a);let pr=prov.get(a);if(!pr)prov.set(a,pr={types:new Set(),states:new Set(),min:n.d});pr.types.add(root.type);pr.states.add(root.type+':'+root.d0);pr.min=Math.min(pr.min,n.d);for(const c of get(a).calls)if(n.d<7&&!seen.has(c.target))q.push({a:c.target,d:n.d+1});}if(i%24===23)await sleep(0);}
 const rows=[];for(const [a,r] of cache){if(!r.writes.length)continue;const pr=prov.get(a);const xs=r.writes.filter(x=>x.disp===0x3e),ys=r.writes.filter(x=>x.disp===0x42),bases=[...new Set(r.writes.map(x=>x.baseReg))],pair=bases.some(b=>xs.some(x=>x.baseReg===b)&&ys.some(y=>y.baseReg===b));const score=(pair?300:0)+r.writes.length*50+pr.types.size*3-Math.min(6,pr.min)*2;rows.push({routine:E.h(a),offline:E.off(a),score,pairXY:pair,writes:r.writes.length,xWrites:xs.length,yWrites:ys.length,baseRegs:bases.join(','),typeIds:[...pr.types].sort((x,y)=>x-y).join(','),states:pr.states.size,minDepth:pr.min,sites:r.writes.map(x=>E.h(x.at)+':'+E.h(x.disp).slice(-4)+'@'+x.baseReg+'<-'+(x.srcReg||x.kind)).join(' | ')});}rows.sort((a,b)=>b.score-a.score||b.pairXY-a.pairXY||b.writes-a.writes);
 console.log('=== TARGET XY WRITE ROUTINES ===');console.table(rows.slice(0,80));const top=rows[0]||null;if(top){const a=parseInt(top.routine,16),r=cache.get(a);console.log('=== TOP XY WRITE SITES ===');console.table(r.writes.map(x=>({at:E.h(x.at),offline:E.off(x.at),field:E.h(x.disp),kind:x.kind,baseReg:x.baseReg,srcReg:x.srcReg,op:E.hw(x.op)})));for(const x of r.writes.slice(0,6)){console.log('=== CONTEXT '+E.h(x.at)+' ===');console.table(ctx(E,x.at));}}
 const verdict={level2Pointers:(L2.handlers||[]).length,uniqueRootHandlers:new Set(raw.map(x=>x.addr)).size,reachableRoutines:cache.size,writerRoutines:rows.length,pairXYRoutines:rows.filter(x=>x.pairXY).length,topRoutine:top?.routine||'',topOffline:top?.offline||'',topPairXY:top?.pairXY??false,topWrites:top?.writes??0,topBaseRegs:top?.baseRegs||'',topTypeIds:top?.typeIds||'',topStates:top?.states??0,topSites:top?.sites||''};console.log('=== TARGET XY WRITE VERDICT ===');console.table([verdict]);
 if(top?.pairXY)console.log('🎯 找到同一真实 AI routine 写 enemy+0x3E / +0x42；下一步反向追这两个写入的 source register，找它们从玩家/路径逻辑哪里生成。');else if(top)console.warn('⚠️ 找到单字段写入但未在同一 routine 配对；下一步沿 caller/callee 组合两字段。');else console.warn('⚠️ 真实 handler graph 内没有直接 d16(An) 写 0x3E/0x42；下一步查基址偏移/LEA alias 与动态写时序。');
 const out={version:'wof-target-xy-write-v1',verdict,rows,top};self.__WOF_TARGET_XY_WRITE=out;return out;}
self.WOFTARGETXYWRITE={version:'wof-target-xy-write-v1',run,stop(){stopped=true;}};console.log('✅ WOF target XY write scanner loaded');console.log('执行 await WOFTARGETXYWRITE.run()');
})();