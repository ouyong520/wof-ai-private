(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
if(!self.__WOF_ROM_LOC_CACHE)await load('wof_resume_dispatch_selector.js');
const C=self.__WOF_ROM_LOC_CACHE;if(!C)throw new Error('ROM cache missing');
const MOD=_0x515056,M=MOD.HEAPU8,base=C.base,SW=!!C.swap16,MAX=Math.min(0x30000,M.length-base);
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
function add(rows,x){
 const around=[];for(let q=Math.max(0,x.at-16);q<=Math.min(MAX-2,x.at+20);q+=2)around.push(hw(r16(q)));
 const src=x.src||'';
 let score=0;
 if(/^D[0-7]$/.test(src))score+=8;
 if(/^#/.test(src))score+=7;
 if(/124\(A[0-7]\)/.test(src))score+=4;
 if(x.size==='W')score+=3;
 if(x.kind==='CLR')score+=2;
 if(/#0x000[048]$/i.test(src)||/^#(?:0|4|8)$/.test(src))score+=12;
 // nearby ADD/LSL/MUL-like words often build 0/4/8 index
 for(let q=Math.max(0,x.at-24);q<x.at;q+=2){const w=r16(q);if((w&0xF100)===0x5000)score+=0.25;if((w&0xF000)===0xE000)score+=0.15;}
 rows.push({...x,atHex:h(x.at),word:hw(x.word),score:+score.toFixed(2),window:around.join(' ')});
}
const rows=[];
for(let p=0;p<MAX-10;p+=2){
 const mi=moveInfo(p);
 if(mi&&mi.dm===5&&r16(mi.dep)===0x007E){
   add(rows,{at:p,word:mi.word,kind:'MOVE',size:mi.size,baseReg:'A'+mi.dr,src:mi.src,dst:'126(A'+mi.dr+')',text:'MOVE.'+mi.size+' '+mi.src+',126(A'+mi.dr+')'});
 }
 const w=r16(p),m=(w>>3)&7,r=w&7;
 // CLR d16(An)
 if((w&0xFF00)===0x4200&&m===5&&r16(p+2)===0x007E){
   const sz=(w>>6)&3,size=sz===0?'B':sz===1?'W':sz===2?'L':'?';
   add(rows,{at:p,word:w,kind:'CLR',size,baseReg:'A'+r,src:'#0',dst:'126(A'+r+')',text:'CLR.'+size+' 126(A'+r+')'});
 }
 // ADDQ/SUBQ d16(An)
 if((w>>>12)===5&&((w>>6)&3)!==3&&m===5&&r16(p+2)===0x007E){
   const sub=!!(w&0x0100),q=((w>>9)&7)||8,sz=(w>>6)&3,size=sz===0?'B':sz===1?'W':'L';
   add(rows,{at:p,word:w,kind:sub?'SUBQ':'ADDQ',size,baseReg:'A'+r,src:'#'+q,dst:'126(A'+r+')',text:(sub?'SUBQ':'ADDQ')+'.'+size+' #'+q+',126(A'+r+')'});
 }
 // immediate arithmetic/logical to d16(An)
 if((w>>>12)===0){
   const op=(w>>8)&15,sz=(w>>6)&3;
   if([0,2,4,6,10].includes(op)&&sz!==3&&m===5){
     const size=sz===2?'L':sz===1?'W':'B',ib=size==='L'?4:2,dep=p+2+ib;
     if(r16(dep)===0x007E){const nm={0:'ORI',2:'ANDI',4:'SUBI',6:'ADDI',10:'EORI'}[op],imm=size==='L'?r32(p+2):r16(p+2);add(rows,{at:p,word:w,kind:nm,size,baseReg:'A'+r,src:'#'+(size==='L'?h(imm):hw(imm)),dst:'126(A'+r+')',text:nm+'.'+size+' #'+(size==='L'?h(imm):hw(imm))+',126(A'+r+')'});}
   }
 }
}
const uniq=[...new Map(rows.map(x=>[x.atHex+'|'+x.text,x])).values()];
uniq.sort((a,b)=>b.score-a.score||a.at-b.at);
const regWrites=uniq.filter(x=>/^D[0-7]$/.test(x.src));
const immWrites=uniq.filter(x=>/^#/.test(x.src));
const copy7c=uniq.filter(x=>/124\(A[0-7]\)/.test(x.src));
const verdict={range:'0x000000..0x030000',writers:uniq.length,regWrites:regWrites.length,immWrites:immWrites.length,copy7cWrites:copy7c.length,topAt:uniq[0]?.atHex||'',topText:uniq[0]?.text||'',topScore:uniq[0]?.score||0};
const out={version:'wof-player-selector-7e-alias-writers-v1',verdict,top:uniq.slice(0,60),regWrites:regWrites.slice(0,60),immWrites:immWrites.slice(0,40),copy7c:copy7c.slice(0,60)};
self.__WOF_PLAYER_SELECTOR_7E_ALIAS_WRITERS=out;
console.log('=== 7E ALIAS WRITER VERDICT ===');console.table([verdict]);
console.log('=== 7E ALIAS WRITER TOP ===');console.table(out.top.map(x=>({at:x.atHex,base:x.baseReg,src:x.src,size:x.size,text:x.text,score:x.score})));
console.log('=== 7E ALIAS WRITER JSON ===');console.log(JSON.stringify(out,null,2));
return out;
})().catch(e=>{console.error('WOF_PLAYER_SELECTOR_7E_ALIAS_WRITER_ERROR',e);throw e;});