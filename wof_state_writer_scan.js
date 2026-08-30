(()=>{
'use strict';
try{self.WOFSTATEWRITER?.stop?.();}catch(_){}
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));let stopped=false;
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return (0,eval)(await r.text());};
async function ensure(){
 if(!self.__WOF_STATE_DISPATCH_LOCK)throw new Error('STATE_DISPATCH_LOCK missing; keep this room/result and rerun the previous state lock if needed');
 if(!self.__WOF_ROM_FOCUS_LEVEL2?.handlers?.length){await load('wof_rom_focus_level2_tables.js');await WOFFOCUSLEVEL2.run();}
 if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing');
}
function env(){const MOD=_0x515056,C=self.__WOF_ROM_LOC_CACHE,M=MOD.HEAPU8,base=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-base),DELTA=C.offlineDelta|0;
 const r8=o=>M[base+(SW?(o^1):o)]>>>0,r16=o=>((r8(o)<<8)|r8(o+1))>>>0,r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0,s8=v=>v&0x80?v-0x100:v,s16=v=>v&0x8000?v-0x10000:v,h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0'),off=x=>h((x-DELTA)>>>0),hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');return{MAX,r8,r16,r32,s8,s16,h,off,hw};}
function eaWords(m,r,size){if(m<=4)return 0;if(m===5||m===6)return 1;if(m===7){if(r===0||r===2||r===3)return 1;if(r===1)return 2;if(r===4)return size==='L'?2:1;}return 0;}
function regName(m,r){return m===0?'D'+r:m===1?'A'+r:'';}
function decode(E,p){const w=E.r16(p),g=w>>>12,m=(w>>3)&7,r=w&7;let len=2,kind='OP',target=null,fall=true,terminal=false,call=false,branch=false;
 if(w===0x4E75||w===0x4E73||w===0x4E77){kind='RET';terminal=true;fall=false;}
 else if(w===0x4E72){kind='STOP';len=4;terminal=true;fall=false;}
 else if((w&0xFFC0)===0x4E80){kind='JSR';call=true;len=2+eaWords(m,r,'L')*2;if(m===7&&r===0)target=E.s16(E.r16(p+2))>>>0;else if(m===7&&r===1)target=E.r32(p+2);else if(m===7&&r===2)target=(p+2+E.s16(E.r16(p+2)))>>>0;}
 else if((w&0xFFC0)===0x4EC0){kind='JMP';fall=false;len=2+eaWords(m,r,'L')*2;if(m===7&&r===0)target=E.s16(E.r16(p+2))>>>0;else if(m===7&&r===1)target=E.r32(p+2);else if(m===7&&r===2)target=(p+2+E.s16(E.r16(p+2)))>>>0;}
 else if(g===6){const cc=(w>>8)&15,d=w&255;len=d===0?4:2;target=d===0?p+2+E.s16(E.r16(p+2)):p+2+E.s8(d);kind=cc===0?'BRA':cc===1?'BSR':'BCC';branch=true;if(cc===0)fall=false;if(cc===1)call=true;}
 else if(g===1||g===2||g===3){const size=g===1?'B':g===2?'L':'W',sm=(w>>3)&7,sr=w&7,dm=(w>>6)&7,dr=(w>>9)&7;len=2+(eaWords(sm,sr,size)+eaWords(dm,dr,size))*2;}
 else if(g===5){const sz=(w>>6)&3;if(sz===3&&m===1){kind='DBCC';len=4;target=(p+2+E.s16(E.r16(p+2)))>>>0;branch=true;}else len=2+eaWords(m,r,sz===3?'B':sz===2?'L':sz===1?'W':'B')*2;}
 else if(g===0){if([0x003C,0x007C,0x023C,0x027C,0x0A3C,0x0A7C].includes(w))len=4;else if((w&0xF138)===0x0108)len=4;else if((w&0xFF00)===0x0800)len=4+eaWords(m,r,'B')*2;else if((w&0xF100)===0x0100)len=2+eaWords(m,r,'B')*2;else{const op=(w>>8)&15,sz=(w>>6)&3;if([0,2,4,6,10,12].includes(op)){const s=sz===2?'L':sz===1?'W':'B';len=2+(s==='L'?4:2)+eaWords(m,r,s)*2;}}}
 else if(g===4){if((w&0xFFF8)===0x4E50)len=4;else if((w&0xFB80)===0x4880&&m>=2)len=4+eaWords(m,r,(w&0x40)?'L':'W')*2;else if((w&0xF1C0)===0x41C0)len=2+eaWords(m,r,'L')*2;else if((w&0xFFC0)===0x4840&&m!==0)len=2+eaWords(m,r,'L')*2;else len=2+eaWords(m,r,((w>>6)&3)===2?'L':'W')*2;}
 else if(g===8){if((w&0xF1F0)!==0x8100)len=2+eaWords(m,r,((w>>6)&3)===2?'L':'W')*2;}
 else if(g===9||g===13){const special=(w&0xF130)===(g===9?0x9100:0xD100),a=((w>>6)&7)===3||((w>>6)&7)===7;if(!special)len=2+eaWords(m,r,a?(((w>>6)&1)?'L':'W'):(((w>>6)&3)===2?'L':'W'))*2;}
 else if(g===11){const cmpm=(w&0xF138)===0xB108,a=((w>>6)&7)===3||((w>>6)&7)===7;if(!cmpm)len=2+eaWords(m,r,a?(((w>>6)&1)?'L':'W'):(((w>>6)&3)===2?'L':'W'))*2;}
 else if(g===12){const exg=(w&0xF1F8)===0xC140||(w&0xF1F8)===0xC148||(w&0xF1F8)===0xC188,abcd=(w&0xF1F0)===0xC100;if(!exg&&!abcd)len=2+eaWords(m,r,((w>>6)&3)===2?'L':'W')*2;}
 else if(g===14&&((w>>6)&3)===3)len=2+eaWords(m,r,'W')*2;
 else if(g===10||g===15){kind='LINE';terminal=true;fall=false;}
 len=Math.max(2,len);const next=p+len;if(target!=null&&(target<0||target>=E.MAX))target=null;return{at:p,w,len,next,kind,target,fall,terminal,call,branch};}
function moveWrite(E,p,FIELD){const w=E.r16(p),g=w>>>12;if(g!==1&&g!==2&&g!==3)return null;const size=g===1?'B':g===2?'L':'W',sm=(w>>3)&7,sr=w&7,dm=(w>>6)&7,dr=(w>>9)&7;if(dm!==5)return null;const sw=eaWords(sm,sr,size),dstExt=p+2+sw*2;if(dstExt+1>=E.MAX)return null;const disp=E.s16(E.r16(dstExt));if(disp!==FIELD)return null;let imm='';if(sm===7&&sr===4){imm=size==='L'?E.r32(p+2):E.r16(p+2);if(size==='B')imm&=0xff;}return{at:p,kind:'MOVE.'+size,baseReg:'A'+dr,srcReg:regName(sm,sr),imm,op:w};}
function singleWrite(E,p,FIELD){const w=E.r16(p),g=w>>>12,m=(w>>3)&7,r=w&7;if(m!==5)return null;let size='W',ext=p+2,kind='',imm='';
 if(g===5&&((w>>6)&3)!==3){size=((w>>6)&3)===2?'L':((w>>6)&3)===1?'W':'B';kind=(w&0x0100)?'SUBQ':'ADDQ';imm=(w>>9)&7;if(!imm)imm=8;}
 else if(g===4&&(((w&0xff00)===0x4200)||((w&0xff00)===0x4400)||((w&0xff00)===0x4600))){size=((w>>6)&3)===2?'L':((w>>6)&3)===1?'W':'B';kind=(w&0xff00)===0x4200?'CLR':(w&0xff00)===0x4400?'NEG':'NOT';}
 else if(g===0){const op=(w>>8)&15,sz=(w>>6)&3;if(![0,2,4,6,10].includes(op)||sz===3)return null;size=sz===2?'L':sz===1?'W':'B';kind=['ORI','','ANDI','','SUBI','','ADDI','','','','EORI'][op]||'IMM';imm=size==='L'?E.r32(p+2):E.r16(p+2);if(size==='B')imm&=0xff;ext=p+2+(size==='L'?4:2);}
 else return null;if(ext+1>=E.MAX)return null;const disp=E.s16(E.r16(ext));if(disp!==FIELD)return null;return{at:p,kind:kind+'.'+size,baseReg:'A'+r,srcReg:'',imm,op:w};}
function routine(E,start,cap=0x1800){const hi=Math.min(E.MAX,start+cap),q=[start&~1],seen=new Set(),calls=[];while(q.length&&seen.size<8000){const p=q.shift();if(p<0||p>=hi||(p&1)||seen.has(p))continue;seen.add(p);const d=decode(E,p);if((d.kind==='JSR'||d.kind==='BSR')&&d.target!=null)calls.push(d.target&~1);if(d.kind==='BRA'){if(d.target!=null&&d.target<hi)q.push(d.target&~1);continue;}if(d.kind==='BCC'||d.kind==='DBCC'){if(d.next<hi)q.push(d.next);if(d.target!=null&&d.target<hi)q.push(d.target&~1);continue;}if(d.kind==='JMP'){if(d.target!=null&&d.target<hi)q.push(d.target&~1);continue;}if(d.terminal)continue;if(d.next<hi)q.push(d.next);}return{seen,calls:[...new Set(calls)]};}
function ctx(E,p){const out=[];for(let q=Math.max(0,p-0x18)&~1;q<=Math.min(E.MAX-2,p+0x18);q+=2)out.push({at:E.h(q),offline:E.off(q),word:E.hw(E.r16(q)),mark:q===p?'<<< STATE WRITE':''});return out;}
async function run(){stopped=false;await ensure();const E=env(),S=self.__WOF_STATE_DISPATCH_LOCK,L2=self.__WOF_ROM_FOCUS_LEVEL2,FIELD=parseInt(S.verdict.field,16),KIND=S.verdict.kind;
 console.log('🧠 WOF locked stateIndex writer scan');console.log('FIELD',S.verdict.field,'KIND',KIND,'ENCODING',S.verdict.fieldEncoding);
 const observed=new Set([0]);for(const m of S.mappings||[]){const s=String(m.mapping||''),z=s.match(/@(0x[0-9A-Fa-f]+)/);if(z){const d=parseInt(z[1],16);if(Number.isFinite(d))observed.add(d/4);}}
 console.log('observed stateIndex values:',[...observed].sort((a,b)=>a-b));
 const raw=[];for(let p=0;p+10<E.MAX;p+=2){const z=moveWrite(E,p,FIELD)||singleWrite(E,p,FIELD);if(z)raw.push(z);if((p&0x1ffff)===0x1fffe)await sleep(0);}const ded=[...new Map(raw.map(x=>[x.at,x])).values()];
 const roots=[...new Set((L2.handlers||[]).map(x=>parseInt(x.target,16)&~1).filter(Number.isFinite))],cache=new Map(),owner=new Map(),reachable=new Set();const q=roots.map(a=>({a,d:0})),seenR=new Set();while(q.length){const n=q.shift(),a=n.a&~1;if(seenR.has(a)||n.d>8)continue;seenR.add(a);const r=routine(E,a);cache.set(a,r);for(const p of r.seen){reachable.add(p);if(!owner.has(p))owner.set(p,a);}for(const c of r.calls)if(n.d<8&&!seenR.has(c))q.push({a:c,d:n.d+1});if((seenR.size&31)===0)await sleep(0);}
 const rows=ded.map(x=>{const real=reachable.has(x.at),own=owner.get(x.at),immNum=typeof x.imm==='number'?x.imm:null,matchObs=immNum!=null&&observed.has(immNum),small=immNum!=null&&immNum<=0x3f;let score=(real?500:0)+(matchObs?220:0)+(small?60:0)+(x.srcReg?35:0)+(x.kind.startsWith('MOVE')?25:0);return{at:E.h(x.at),offline:E.off(x.at),realCFG:real,routine:own!=null?E.h(own):'',kind:x.kind,baseReg:x.baseReg,srcReg:x.srcReg||'',imm:immNum==null?'':E.h(immNum).slice(-4),matchesObserved:matchObs,score};}).sort((a,b)=>b.score-a.score||a.at.localeCompare(b.at));
 console.log('=== LOCKED STATE WRITE CANDIDATES ===');console.table(rows.slice(0,120));const realRows=rows.filter(x=>x.realCFG),obsRows=realRows.filter(x=>x.matchesObserved),top=obsRows[0]||realRows[0]||rows[0]||null;
 if(top){console.log('=== TOP STATE WRITE CONTEXT ===');console.table(ctx(E,parseInt(top.at,16)));}
 const verdict={field:S.verdict.field,kind:KIND,encoding:S.verdict.fieldEncoding,observedStates:[...observed].sort((a,b)=>a-b).join(','),rawWriteSites:rows.length,realCFGWriteSites:realRows.length,observedImmediateWrites:obsRows.length,topAt:top?.at||'',topOffline:top?.offline||'',topRoutine:top?.routine||'',topKind:top?.kind||'',topBaseReg:top?.baseReg||'',topSrcReg:top?.srcReg||'',topImm:top?.imm||'',topMatchesObserved:top?.matchesObserved??false};
 console.log('=== STATE WRITER VERDICT ===');console.table([verdict]);
 if(obsRows.length)console.log('🎯 找到真实 AI CFG 内直接写已观测 stateIndex 的指令；下一步只追 top write 的 source/caller/player evidence。');else if(realRows.length)console.warn('⚠️ 找到真实 CFG state 写入，但没有直接 immediate 命中已观测状态；下一步追 srcReg 数据流。');else if(rows.length)console.warn('⚠️ 全 ROM 有 raw state 写入但不在当前 handler direct-call CFG；下一步验证这些 raw site 的真实函数边界/上游共享 routine。');else console.warn('⚠️ 未找到直接 d16(An) state 写入；下一步查基址 alias/indexed 写法。');
 const out={version:'wof-state-writer-v1',verdict,rows,realRows,observedImmediate:obsRows};self.__WOF_STATE_WRITER=out;return out;}
self.WOFSTATEWRITER={version:'wof-state-writer-v1',run,stop(){stopped=true;}};console.log('✅ WOF stateIndex writer scan loaded');console.log('执行 await WOFSTATEWRITER.run()');
})();