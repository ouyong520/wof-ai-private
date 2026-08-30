(()=>{
'use strict';
try{self.WOFTARGETXYALIAS?.stop?.();}catch(_){}
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));let stopped=false;
const load=async f=>{const r=await fetch(RAW+f+'?x='+Math.random());if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
async function ensure(){if(!self.__WOF_ROM_FOCUS_LEVEL2?.handlers?.length){await load('wof_rom_focus_level2_tables.js');await WOFFOCUSLEVEL2.run();}if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM state unavailable');}
function env(){const MOD=_0x515056,C=self.__WOF_ROM_LOC_CACHE,M=MOD.HEAPU8,base=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-base),DELTA=C.offlineDelta|0;const r8=o=>M[base+(SW?(o^1):o)]>>>0,r16=o=>((r8(o)<<8)|r8(o+1))>>>0,r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0,s8=v=>v&0x80?v-0x100:v,s16=v=>v&0x8000?v-0x10000:v,h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0'),off=x=>h((x-DELTA)>>>0),hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');return{MAX,r8,r16,r32,s8,s16,h,off,hw};}
function eaWords(m,r,size){if(m<=4)return 0;if(m===5||m===6)return 1;if(m===7){if(r===0||r===2||r===3)return 1;if(r===1)return 2;if(r===4)return size==='L'?2:1;}return 0;}
function moveInfo(E,p,w){const g=w>>>12;if(g!==1&&g!==2&&g!==3)return null;const size=g===1?'B':g===2?'L':'W',sm=(w>>3)&7,sr=w&7,dm=(w>>6)&7,dr=(w>>9)&7,sw=eaWords(sm,sr,size),dw=eaWords(dm,dr,size),dstExt=p+2+sw*2;let disp=0;if(dm===5)disp=E.s16(E.r16(dstExt));return{size,sm,sr,dm,dr,sw,dw,dstExt,disp};}
function decode(E,p){const w=E.r16(p),g=w>>>12,m=(w>>3)&7,r=w&7;let len=2,kind='OP',target=null,fall=true,terminal=false,call=false,branch=false,move=null;
 if(w===0x4E75||w===0x4E73||w===0x4E77){kind='RET';terminal=true;fall=false;}
 else if(w===0x4E72){kind='STOP';len=4;terminal=true;fall=false;}
 else if((w&0xFFC0)===0x4E80){kind='JSR';call=true;len=2+eaWords(m,r,'L')*2;if(m===7&&r===0)target=E.s16(E.r16(p+2))>>>0;else if(m===7&&r===1)target=E.r32(p+2);else if(m===7&&r===2)target=(p+2+E.s16(E.r16(p+2)))>>>0;}
 else if((w&0xFFC0)===0x4EC0){kind='JMP';fall=false;len=2+eaWords(m,r,'L')*2;if(m===7&&r===0)target=E.s16(E.r16(p+2))>>>0;else if(m===7&&r===1)target=E.r32(p+2);else if(m===7&&r===2)target=(p+2+E.s16(E.r16(p+2)))>>>0;}
 else if(g===6){const cc=(w>>8)&15,d=w&255;len=d===0?4:2;target=d===0?p+2+E.s16(E.r16(p+2)):p+2+E.s8(d);kind=cc===0?'BRA':cc===1?'BSR':'BCC';branch=true;if(cc===0)fall=false;if(cc===1)call=true;}
 else if(g===1||g===2||g===3){move=moveInfo(E,p,w);len=2+(move.sw+move.dw)*2;kind='MOVE';}
 else if(g===5){const sz=(w>>6)&3;if(sz===3&&m===1){kind='DBCC';len=4;target=(p+2+E.s16(E.r16(p+2)))>>>0;branch=true;}else{kind='QUICK';len=2+eaWords(m,r,sz===2?'L':sz===1?'W':'B')*2;}}
 else if(g===0){if([0x003C,0x007C,0x023C,0x027C,0x0A3C,0x0A7C].includes(w))len=4;else if((w&0xF138)===0x0108)len=4;else if((w&0xFF00)===0x0800)len=4+eaWords(m,r,'B')*2;else if((w&0xF100)===0x0100)len=2+eaWords(m,r,'B')*2;else{const op=(w>>8)&15,sz=(w>>6)&3;if([0,2,4,6,10,12].includes(op)){const s=sz===2?'L':sz===1?'W':'B';len=2+(s==='L'?4:2)+eaWords(m,r,s)*2;}}}
 else if(g===4){if((w&0xFFF8)===0x4E50)len=4;else if((w&0xFB80)===0x4880&&m>=2)len=4+eaWords(m,r,(w&0x40)?'L':'W')*2;else if((w&0xF1C0)===0x41C0){kind='LEA';len=2+eaWords(m,r,'L')*2;}else if((w&0xFFC0)===0x4840&&m!==0)len=2+eaWords(m,r,'L')*2;else len=2+eaWords(m,r,((w>>6)&3)===2?'L':'W')*2;}
 else if(g===8){if((w&0xF1F0)!==0x8100)len=2+eaWords(m,r,((w>>6)&3)===2?'L':'W')*2;}
 else if(g===9||g===13){const special=(w&0xF130)===(g===9?0x9100:0xD100),a=((w>>6)&7)===3||((w>>6)&7)===7;if(!special){kind=a?(g===9?'SUBA':'ADDA'):'ARITH';len=2+eaWords(m,r,a?(((w>>6)&1)?'L':'W'):(((w>>6)&3)===2?'L':'W'))*2;}}
 else if(g===11){const cmpm=(w&0xF138)===0xB108,a=((w>>6)&7)===3||((w>>6)&7)===7;if(!cmpm)len=2+eaWords(m,r,a?(((w>>6)&1)?'L':'W'):(((w>>6)&3)===2?'L':'W'))*2;}
 else if(g===12){const exg=(w&0xF1F8)===0xC140||(w&0xF1F8)===0xC148||(w&0xF1F8)===0xC188,abcd=(w&0xF1F0)===0xC100;if(exg)kind='EXG';else if(!abcd)len=2+eaWords(m,r,((w>>6)&3)===2?'L':'W')*2;}
 else if(g===14&&((w>>6)&3)===3)len=2+eaWords(m,r,'W')*2;else if(g===10||g===15){kind='LINE';terminal=true;fall=false;}
 len=Math.max(2,len);const next=p+len;if(target!=null&&(target<0||target>=E.MAX))target=null;return{at:p,w,g,m,r,len,next,kind,target,fall,terminal,call,branch,move};}
const initState=()=>Array.from({length:7},(_,i)=>new Set(['A'+i+':0']));
const clone=s=>s.map(x=>new Set(x));
function parseTok(t){const k=t.indexOf(':');return{root:t.slice(0,k),off:+t.slice(k+1)};}
function tok(root,off){if(off<-0x400||off>0x400)return null;return root+':'+off;}
function shifted(set,d){const o=new Set();for(const t of set){const z=parseTok(t),n=tok(z.root,z.off+d);if(n)o.add(n);}return o;}
function merge(dst,src){let ch=false;for(let i=0;i<7;i++)for(const t of src[i])if(!dst[i].has(t)&&dst[i].size<24){dst[i].add(t);ch=true;}return ch;}
function sig(s){return s.map(x=>[...x].sort().join(',')).join('|');}
function srcName(m){return m.sm===0?'D'+m.sr:m.sm===1?'A'+m.sr:'';}
function writeFromMove(E,d,state,out){const m=d.move;if(!m)return;let base=null,disp=null;if(m.dm===2||m.dm===3){base=m.dr;disp=0;}else if(m.dm===5){base=m.dr;disp=m.disp;}else return;if(base>6)return;for(const t of state[base]){const z=parseTok(t),field=z.off+disp;if(field===0x3E||field===0x42)out.push({at:d.at,field,seed:z.root,baseReg:'A'+base,aliasOffset:z.off,disp,kind:'MOVE.'+m.size,srcReg:srcName(m),op:d.w});}}
function apply(E,d,state){const s=clone(state),w=d.w;
 if(d.move&&d.move.dm===1&&d.move.dr<=6){const m=d.move;if(m.sm===1&&m.sr<=6)s[m.dr]=new Set(s[m.sr]);else s[m.dr]=new Set();}
 if(d.kind==='LEA'){const dst=(w>>9)&7,m=(w>>3)&7,r=w&7;if(dst<=6){if(m===2&&r<=6)s[dst]=new Set(s[r]);else if(m===5&&r<=6)s[dst]=shifted(s[r],E.s16(E.r16(d.at+2)));else s[dst]=new Set();}}
 if((d.kind==='ADDA'||d.kind==='SUBA')){const dst=(w>>9)&7,m=(w>>3)&7,r=w&7;if(dst<=6){if(m===7&&r===4){const isLong=!!((w>>8)&1),imm=isLong?(E.r32(d.at+2)|0):E.s16(E.r16(d.at+2)),delta=d.kind==='SUBA'?-imm:imm;s[dst]=shifted(s[dst],delta);}else s[dst]=new Set();}}
 if(d.kind==='QUICK'&&((w>>3)&7)===1){const dst=w&7;if(dst<=6){let q=(w>>9)&7;if(q===0)q=8;if(w&0x0100)q=-q;s[dst]=shifted(s[dst],q);}}
 if(d.kind==='EXG'&&(w&0xF1F8)===0xC148){const a=(w>>9)&7,b=w&7;if(a<=6&&b<=6){const t=s[a];s[a]=s[b];s[b]=t;}}
 if(d.move&&d.move.dm===1&&d.move.dr===7){} // ignore A7
 return s;}
function routine(E,start,cap=0x1400){const hi=Math.min(E.MAX,start+cap),entry=start&~1,inMap=new Map([[entry,initState()]]),q=[entry],queued=new Set([entry]),calls=[],writes=[];let steps=0;
 while(q.length&&steps<18000){const p=q.shift();queued.delete(p);const st=inMap.get(p);if(!st||p<entry||p>=hi||(p&1))continue;steps++;const d=decode(E,p);writeFromMove(E,d,st,writes);const ns=apply(E,d,st);if((d.kind==='JSR'||d.kind==='BSR')&&d.target!=null)calls.push({at:p,target:d.target&~1,kind:d.kind});
  const succ=[];if(d.kind==='BRA'){if(d.target!=null&&d.target>=entry&&d.target<hi)succ.push(d.target&~1);}else if(d.kind==='BCC'||d.kind==='DBCC'){if(d.next<hi)succ.push(d.next);if(d.target!=null&&d.target>=entry&&d.target<hi)succ.push(d.target&~1);}else if(d.kind==='JMP'){if(d.target!=null&&d.target>=entry&&d.target<hi)succ.push(d.target&~1);}else if(!d.terminal&&d.next<hi)succ.push(d.next);
  for(const n of succ){if(!inMap.has(n)){inMap.set(n,clone(ns));if(!queued.has(n)){q.push(n);queued.add(n);}}else if(merge(inMap.get(n),ns)&&!queued.has(n)){q.push(n);queued.add(n);}}
 }
 return{calls:[...new Map(calls.map(x=>[x.at+'|'+x.target,x])).values()],writes:[...new Map(writes.map(x=>[x.at+'|'+x.field+'|'+x.seed,x])).values()],states:inMap.size,steps};}
async function run(){stopped=false;await ensure();const E=env(),L2=self.__WOF_ROM_FOCUS_LEVEL2;console.log('🧭 WOF target XY alias-writer scan v2 · A-register symbolic offsets');
 const raw=(L2.handlers||[]).map(x=>({addr:parseInt(x.target,16)&~1,type:x.type,d0:x.d0})).filter(x=>Number.isFinite(x.addr)),roots=[...new Map(raw.map(x=>[x.addr+'|'+x.type+'|'+x.d0,x])).values()],cache=new Map(),prov=new Map();const get=a=>{a&=~1;if(!cache.has(a))cache.set(a,routine(E,a));return cache.get(a);};
 for(let i=0;i<roots.length;i++){if(stopped)throw new Error('stopped');const root=roots[i],q=[{a:root.addr,d:0}],seen=new Set();while(q.length){const n=q.shift(),a=n.a&~1;if(seen.has(a)||n.d>8)continue;seen.add(a);let pr=prov.get(a);if(!pr)prov.set(a,pr={types:new Set(),states:new Set(),min:n.d});pr.types.add(root.type);pr.states.add(root.type+':'+root.d0);pr.min=Math.min(pr.min,n.d);for(const c of get(a).calls)if(n.d<8&&!seen.has(c.target))q.push({a:c.target,d:n.d+1});}if(i%20===19)await sleep(0);}
 const rows=[];for(const[a,r]of cache){if(!r.writes.length)continue;const pr=prov.get(a);if(!pr)continue;const groups=new Map();for(const w of r.writes){if(!groups.has(w.seed))groups.set(w.seed,[]);groups.get(w.seed).push(w);}for(const[seed,ws]of groups){const xs=ws.filter(x=>x.field===0x3E),ys=ws.filter(x=>x.field===0x42),pair=!!(xs.length&&ys.length),score=(pair?500:0)+ws.length*60+pr.types.size*3-Math.min(8,pr.min)*2;rows.push({routine:E.h(a),offline:E.off(a),seedReg:seed,score,pairXY:pair,writes:ws.length,xWrites:xs.length,yWrites:ys.length,typeIds:[...pr.types].sort((x,y)=>x-y).join(','),states:pr.states.size,minDepth:pr.min,sites:ws.map(x=>E.h(x.at)+' '+E.h(x.field).slice(-4)+' via '+x.baseReg+(x.aliasOffset?(' alias'+(x.aliasOffset>=0?'+':'')+x.aliasOffset):'')+' <- '+(x.srcReg||x.kind)).join(' | ')});}}
 rows.sort((a,b)=>b.score-a.score||b.pairXY-a.pairXY||b.writes-a.writes);console.log('=== ALIAS-RESOLVED TARGET XY WRITERS ===');console.table(rows.slice(0,100));const top=rows[0]||null;
 if(top){const a=parseInt(top.routine,16),r=cache.get(a),ws=r.writes.filter(x=>x.seed===top.seedReg);console.log('=== TOP ALIAS WRITE SITES ===');console.table(ws.map(x=>({at:E.h(x.at),offline:E.off(x.at),field:'0x'+x.field.toString(16).toUpperCase(),seedReg:x.seed,baseReg:x.baseReg,aliasOffset:x.aliasOffset,disp:x.disp,kind:x.kind,srcReg:x.srcReg,op:E.hw(x.op)})));}
 const verdict={level2Pointers:(L2.handlers||[]).length,uniqueRootHandlers:new Set(raw.map(x=>x.addr)).size,reachableRoutines:cache.size,writerGroups:rows.length,pairXYGroups:rows.filter(x=>x.pairXY).length,topRoutine:top?.routine||'',topSeedReg:top?.seedReg||'',topPairXY:top?.pairXY??false,topWrites:top?.writes??0,topTypeIds:top?.typeIds||'',topStates:top?.states??0,topSites:top?.sites||''};console.log('=== TARGET XY ALIAS VERDICT ===');console.table([verdict]);
 if(top?.pairXY)console.log('🎯 alias dataflow 找到同一入口 A 寄存器最终写 +0x3E/+0x42；下一步追 top write 的 srcReg 来源，定位 waypoint 生成 routine。');else if(top)console.warn('⚠️ 只恢复到单字段 alias writer；下一步把 paired writer 扩到 caller/callee 间。');else console.warn('⚠️ 连 A-register alias 后仍无静态 writer；下一步不再扩大静态扫描，直接做 0x3E/0x42 变化事件与 AI state/type 的动态关联。');
 const out={version:'wof-target-xy-alias-v2',verdict,rows,top};self.__WOF_TARGET_XY_ALIAS=out;return out;}
self.WOFTARGETXYALIAS={version:'wof-target-xy-alias-v2',run,stop(){stopped=true;}};console.log('✅ WOF target XY alias writer v2 loaded');console.log('执行 await WOFTARGETXYALIAS.run()');
})();