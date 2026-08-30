(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
if(!self.__WOF_ROM_LOC_CACHE)await load('wof_resume_dispatch_selector.js');
const C=self.__WOF_ROM_LOC_CACHE;if(!C)throw new Error('ROM cache missing');
const MOD=_0x515056,M=MOD.HEAPU8,base=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-base);
const r8=o=>M[base+(SW?(o^1):o)]>>>0;
const r16=o=>((r8(o)<<8)|r8(o+1))>>>0;
const r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
const s8=v=>v&0x80?v-0x100:v,s16=v=>v&0x8000?v-0x10000:v;
const h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0');
const hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
function eaWords(m,r,size){if(m<=4)return 0;if(m===5||m===6)return 1;if(m===7){if(r===0||r===2||r===3)return 1;if(r===1)return 2;if(r===4)return size==='L'?2:1;}return 0;}
function eaFmt(m,r,size,ep){
 if(m===0)return'D'+r;if(m===1)return'A'+r;if(m===2)return'(A'+r+')';if(m===3)return'(A'+r+')+';if(m===4)return'-(A'+r+')';
 if(m===5)return s16(r16(ep))+'(A'+r+')';
 if(m===6){const x=r16(ep),d=s8(x&255),ir=(x&0x8000?'A':'D')+((x>>12)&7)+(x&0x0800?'.L':'.W');return d+'(A'+r+','+ir+')';}
 if(m===7&&r===0)return hw(r16(ep))+'.W';if(m===7&&r===1)return h(r32(ep))+'.L';
 if(m===7&&r===2){const d=s16(r16(ep));return d+'(PC)->'+h((ep+d)>>>0);}
 if(m===7&&r===3){const x=r16(ep),d=s8(x&255),ir=(x&0x8000?'A':'D')+((x>>12)&7)+(x&0x0800?'.L':'.W');return d+'(PC,'+ir+')';}
 if(m===7&&r===4)return'#'+(size==='L'?h(r32(ep)):hw(r16(ep)));
 return'EA('+m+','+r+')';
}
function moveInfo(p){
 const w=r16(p),g=w>>>12;if(g!==1&&g!==2&&g!==3)return null;
 const size=g===1?'B':g===2?'L':'W',sm=(w>>3)&7,sr=w&7,dm=(w>>6)&7,dr=(w>>9)&7;
 const swd=eaWords(sm,sr,size),dwd=eaWords(dm,dr,size),sep=p+2,dep=p+2+swd*2,len=2+(swd+dwd)*2;
 return{at:p,word:w,size,sm,sr,dm,dr,sep,dep,len,src:eaFmt(sm,sr,size,sep),dst:eaFmt(dm,dr,size,dep)};
}
function fieldDisp(m,r,ep,baseReg,disp){return m===5&&r===baseReg&&r16(ep)===(disp&0xffff);}
const f7=[],g1=[];
for(let p=0;p<MAX-10;p+=2){
 const mi=moveInfo(p);
 if(mi){
   if(fieldDisp(mi.sm,mi.sr,mi.sep,0,0x007E))f7.push({at:h(p),kind:'MOVE.'+mi.size,mode:'read',text:'MOVE.'+mi.size+' '+mi.src+','+mi.dst,src:mi.src,dst:mi.dst});
   if(fieldDisp(mi.dm,mi.dr,mi.dep,0,0x007E))f7.push({at:h(p),kind:'MOVE.'+mi.size,mode:'write',text:'MOVE.'+mi.size+' '+mi.src+','+mi.dst,src:mi.src,dst:mi.dst});
   if(fieldDisp(mi.sm,mi.sr,mi.sep,5,0x01FA))g1.push({at:h(p),kind:'MOVE.'+mi.size,mode:'read',text:'MOVE.'+mi.size+' '+mi.src+','+mi.dst,src:mi.src,dst:mi.dst});
   if(fieldDisp(mi.dm,mi.dr,mi.dep,5,0x01FA))g1.push({at:h(p),kind:'MOVE.'+mi.size,mode:'write',text:'MOVE.'+mi.size+' '+mi.src+','+mi.dst,src:mi.src,dst:mi.dst});
 }
 const w=r16(p),m=(w>>3)&7,r=w&7;
 // CLR/TST d16(A0)
 if((w&0xFF00)===0x4200|| (w&0xFF00)===0x4A00){if(m===5&&r===0&&r16(p+2)===0x007E){const wr=(w&0xFF00)===0x4200;f7.push({at:h(p),kind:wr?'CLR':'TST',mode:wr?'write':'read',text:(wr?'CLR':'TST')+' 126(A0)',src:wr?'#0':'126(A0)',dst:wr?'126(A0)':''});}}
 // ADDQ/SUBQ d16(A0)
 if((w>>>12)===5&&((w>>6)&3)!==3&&m===5&&r===0&&r16(p+2)===0x007E){const sub=!!(w&0x0100),q=((w>>9)&7)||8;f7.push({at:h(p),kind:sub?'SUBQ':'ADDQ',mode:'readwrite',text:(sub?'SUBQ':'ADDQ')+' #'+q+',126(A0)',src:'126(A0)',dst:'126(A0)'});}
 // immediate ops d16(A0)
 if((w>>>12)===0){const op=(w>>8)&15,sz=(w>>6)&3;if([0,2,4,6,10,12].includes(op)&&sz!==3&&m===5&&r===0){const size=sz===2?'L':sz===1?'W':'B',ib=size==='L'?4:2,dep=p+2+ib;if(r16(dep)===0x007E){const nm={0:'ORI',2:'ANDI',4:'SUBI',6:'ADDI',10:'EORI',12:'CMPI'}[op];const imm=size==='L'?r32(p+2):r16(p+2);f7.push({at:h(p),kind:nm+'.'+size,mode:op===12?'read':'readwrite',text:nm+'.'+size+' #'+(size==='L'?h(imm):hw(imm))+',126(A0)',src:op===12?'126(A0)':'#'+(size==='L'?h(imm):hw(imm)),dst:op===12?'':'126(A0)'});}}}
}
function uniq(a){const m=new Map();for(const x of a)m.set(x.at+'|'+x.mode+'|'+x.text,x);return[...m.values()].sort((a,b)=>parseInt(a.at,16)-parseInt(b.at,16));}
const field7e=uniq(f7),slot1fa=uniq(g1);
const fWrites=field7e.filter(x=>x.mode==='write'||x.mode==='readwrite');
const fReads=field7e.filter(x=>x.mode==='read'||x.mode==='readwrite');
const gWrites=slot1fa.filter(x=>x.mode==='write'||x.mode==='readwrite');
const gReads=slot1fa.filter(x=>x.mode==='read'||x.mode==='readwrite');
const selectorSites=[0x010C86,0x010D30,0x010DDE,0x010E6A];
const near=(arr,at,n=12)=>arr.map(x=>({...x,dist:Math.abs(parseInt(x.at,16)-at)})).sort((a,b)=>a.dist-b.dist).slice(0,n);
const selectorRows=selectorSites.map(at=>({at:h(at),d1LoadAt:h(at-4),d1LoadWord:hw(r16(at-4)),d1LoadExt:hw(r16(at-2)),nearest7eWriters:near(fWrites,at,6),nearestSlotStores:near(gWrites,at,4)}));
const immSel=fWrites.filter(x=>/^#0x000[048]$/i.test(x.src)||/^#(?:0|4|8)$/i.test(x.src));
const verdict={tableBase:'0x010CF8',selectorSites:selectorSites.length,field7eReads:fReads.length,field7eWrites:fWrites.length,field7eImmediate048Writes:immSel.length,slot1faWrites:gWrites.length,slot1faReads:gReads.length,top7eWriter:fWrites[0]?.at||'',top7eWriterText:fWrites[0]?.text||'',topSlotReader:gReads[0]?.at||'',topSlotReaderText:gReads[0]?.text||''};
const out={version:'wof-player-selector-7e-1fa-flow-v1',verdict,selectorRows,field7eWrites:fWrites.slice(0,80),field7eReads:fReads.slice(0,80),slot1faWrites:gWrites.slice(0,80),slot1faReads:gReads.slice(0,80)};
self.__WOF_PLAYER_SELECTOR_7E_1FA=out;
console.log('=== PLAYER SELECTOR 7E / 1FA VERDICT ===');console.table([verdict]);
console.log('=== A0+0x7E WRITERS ===');console.table(out.field7eWrites);
console.log('=== A5+0x1FA READERS ===');console.table(out.slot1faReads);
console.log('=== PLAYER SELECTOR 7E / 1FA JSON ===');console.log(JSON.stringify(out,null,2));
return out;
})().catch(e=>{console.error('WOF_PLAYER_SELECTOR_7E_1FA_ERROR',e);throw e;});