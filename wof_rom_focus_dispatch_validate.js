(()=>{
'use strict';
try{self.WOFFOCUSDISPATCHVALIDATE?.stop?.();}catch(_){}
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
let stopped=false;
const load=async f=>{const r=await fetch(RAW+f+'?x='+Math.random());if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);const s=await r.text();(0,eval)(s);};
async function ensure(){if(!self.__WOF_ROM_FOCUS_TRACE?.candidate){await load('wof_rom_focus_trace.js');await WOFFOCUSTRACE.run();}if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM state missing');}
function env(){const MOD=_0x515056,C=self.__WOF_ROM_LOC_CACHE,M=MOD.HEAPU8,base=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-base),DELTA=C.offlineDelta|0;const r8=o=>M[base+(SW?(o^1):o)]>>>0,r16=o=>((r8(o)<<8)|r8(o+1))>>>0,r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0,s8=v=>v&0x80?v-0x100:v,s16=v=>v&0x8000?v-0x10000:v,h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0'),off=x=>h((x-DELTA)>>>0),hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');return{MAX,r8,r16,r32,s8,s16,h,off,hw};}
function eaWords(mode,reg,size){if(mode<=4)return 0;if(mode===5||mode===6)return 1;if(mode===7){if(reg===0||reg===2||reg===3)return 1;if(reg===1)return 2;if(reg===4)return size==='L'?2:1;}return 0;}
function sizeFrom2(bits){return bits===0?'B':bits===1?'W':bits===2?'L':'W';}
function decode(E,p){
 const w=E.r16(p),g=w>>>12,mode=(w>>3)&7,reg=w&7;let words=1,kind='OP',target=null,fall=true,terminal=false;
 if(w===0x4E75||w===0x4E73||w===0x4E77){kind=w===0x4E75?'RTS':w===0x4E73?'RTE':'RTR';terminal=true;fall=false;}
 else if(w===0x4E72){kind='STOP';words=2;terminal=true;fall=false;}
 else if((w&0xFFF0)===0x4E40){kind='TRAP';}
 else if((w&0xFFF8)===0x4E50){kind='LINK';words=2;}
 else if((w&0xFFF8)===0x4E58){kind='UNLK';}
 else if((w&0xFFC0)===0x4E80){kind='JSR';words=1+eaWords(mode,reg,'L');if(mode===7&&reg===0)target=E.s16(E.r16(p+2))>>>0;else if(mode===7&&reg===1)target=E.r32(p+2);else if(mode===7&&reg===2)target=p+2+E.s16(E.r16(p+2));}
 else if((w&0xFFC0)===0x4EC0){kind='JMP';words=1+eaWords(mode,reg,'L');fall=false;if(mode===7&&reg===0)target=E.s16(E.r16(p+2))>>>0;else if(mode===7&&reg===1)target=E.r32(p+2);else if(mode===7&&reg===2)target=p+2+E.s16(E.r16(p+2));else kind='JMP_INDIRECT';}
 else if(g===6){const cc=(w>>8)&15,d=w&255;words=d===0?2:1;target=d===0?p+2+E.s16(E.r16(p+2)):p+2+E.s8(d);kind=cc===0?'BRA':cc===1?'BSR':'BCC';if(cc===0)fall=false;}
 else if(g===1||g===2||g===3){const size=g===1?'B':g===2?'L':'W',sm=mode,sr=reg,dm=(w>>6)&7,dr=(w>>9)&7;words=1+eaWords(sm,sr,size)+eaWords(dm,dr,size);kind='MOVE.'+size;}
 else if(g===5){const sz=(w>>6)&3;if(sz===3&&mode===1){kind='DBCC';words=2;target=p+2+E.s16(E.r16(p+2));}else{kind=sz===3?'SCC':'ADDQ/SUBQ';words=1+eaWords(mode,reg,sz===3?'B':sizeFrom2(sz));}}
 else if(g===7){kind='MOVEQ';}
 else if(g===0){
   if((w&0xF138)===0x0108){kind='MOVEP';words=2;}
   else if((w&0xFF00)===0x0800){kind='BIT_IMM';words=2+eaWords(mode,reg,'B');}
   else if((w&0xF100)===0x0100){kind='BIT_DYN';words=1+eaWords(mode,reg,'B');}
   else {const op=(w>>8)&15,sz=(w>>6)&3;if([0,2,4,6,10,12].includes(op)){const size=sizeFrom2(sz),imm=size==='L'?2:1;kind='IMM';words=1+imm+eaWords(mode,reg,size);}else kind='G0';}
 }
 else if(g===4){
   if((w&0xFB80)===0x4880){const m=(w&0x0400)!==0;kind=m?'MOVEM':'EXT/SWAP';if(m)words=2+eaWords(mode,reg,(w&0x0040)?'L':'W');}
   else if((w&0xF1C0)===0x41C0){kind='LEA';words=1+eaWords(mode,reg,'L');}
   else if((w&0xFFC0)===0x4840){kind='PEA/SWAP';if(mode!==0)words=1+eaWords(mode,reg,'L');}
   else if((w&0xF000)===0x4000){let size=sizeFrom2((w>>6)&3);kind='G4_EA';words=1+eaWords(mode,reg,size);}
 }
 else if(g===8||g===9||g===11||g===12||g===13){kind='ALU';words=1+eaWords(mode,reg,((w>>6)&3)===2?'L':'W');}
 else if(g===14){const sz=(w>>6)&3;kind='SHIFT';if(sz===3)words=1+eaWords(mode,reg,'W');}
 return{at:p,w,words,len:words*2,kind,target,fall,terminal,next:p+words*2};
}
function cfg(E,start,site,cap=0x900){const limit=Math.min(E.MAX,start+cap),q=[start&~1],seen=new Set(),rows=[],hit=false;while(q.length&&seen.size<6000){if(stopped)break;const p=q.shift();if(p<start||p>=limit||(p&1)||seen.has(p))continue;seen.add(p);const d=decode(E,p);rows.push(d);if(p===site)hit=true;if(d.kind==='BSR'){if(d.fall)q.push(d.next);}else if(d.kind==='BRA'){if(d.target!=null)q.push(d.target&~1);}else if(d.kind==='BCC'||d.kind==='DBCC'){if(d.fall)q.push(d.next);if(d.target!=null)q.push(d.target&~1);}else if(d.kind==='JMP'){if(d.target!=null)q.push(d.target&~1);}else if(d.kind==='JMP_INDIRECT'||d.terminal){}else if(d.fall)q.push(d.next);}return{hit,rows,seen};}
function raw(E,site){const a=[];for(let p=site-0x20;p<=site+0x20;p+=2)if(p>=0&&p+2<=E.MAX)a.push({at:E.h(p),offline:E.off(p),word:E.hw(E.r16(p)),mark:p===site?'<<< candidate':''});return a;}
async function run(){stopped=false;await ensure();const E=env(),T=self.__WOF_ROM_FOCUS_TRACE,z=(T.indirectReachable||[])[0];if(!z)throw new Error('no indirect candidate');const site=parseInt(z.at,16),start=parseInt(z.func,16),c=cfg(E,start,site),atSite=c.rows.find(x=>x.at===site)||decode(E,site);const containing=c.rows.filter(x=>x.at<site&&x.next>site).map(x=>({start:E.h(x.at),op:E.hw(x.w),kind:x.kind,len:x.len,next:E.h(x.next)}));const verdict={func:E.h(start),site:E.h(site),word:E.hw(E.r16(site)),decodedAs:atSite.kind,onInstructionBoundary:c.hit,reachableDecodedInstructions:c.seen.size,siteConsumedInsidePriorInstruction:containing.length>0,priorInstruction:containing[0]?.start||'',priorKind:containing[0]?.kind||''};console.log('🧪 68000 indirect-site boundary validator v1');console.log('=== INDIRECT BOUNDARY VERDICT ===');console.table([verdict]);console.log('=== INSTRUCTIONS THAT CONSUME CANDIDATE WORD ===');console.table(containing);console.log('=== RAW WORDS AROUND SITE ===');console.table(raw(E,site));const near=c.rows.filter(x=>Math.abs(x.at-site)<=0x40).map(x=>({at:E.h(x.at),offline:E.off(x.at),op:E.hw(x.w),kind:x.kind,len:x.len,next:E.h(x.next),target:x.target==null?'':E.h(x.target),mark:x.at===site?'<<<':''}));console.log('=== CFG-DECODED INSTRUCTIONS NEAR SITE ===');console.table(near);if(!c.hit)console.warn('❌ 0x094F1C is NOT a reachable instruction boundary from the decoded function CFG; treat prior indirect hit as false positive and rescan indirect opcodes on real instruction boundaries.');else console.log('✅ 0x094F1C is a reachable instruction boundary; dynamic A2/D0 capture is justified.');const out={version:'rom-focus-dispatch-validate-v1',verdict,containing,near};self.__WOF_ROM_FOCUS_DISPATCH_VALIDATE=out;return out;}
self.WOFFOCUSDISPATCHVALIDATE={version:'rom-focus-dispatch-validate-v1',run,stop(){stopped=true;}};console.log('✅ WOF dispatch boundary validator loaded');console.log('执行 await WOFFOCUSDISPATCHVALIDATE.run()');
})();