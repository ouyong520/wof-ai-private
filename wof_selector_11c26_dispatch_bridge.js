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
function eaText(ep,m,r,size){
 if(m===0)return'D'+r;if(m===1)return'A'+r;if(m===2)return'(A'+r+')';if(m===3)return'(A'+r+')+';if(m===4)return'-(A'+r+')';
 if(m===5)return s16(r16(ep))+'(A'+r+')';
 if(m===6){const x=r16(ep),d=s8(x&255),ir=(x&0x8000?'A':'D')+((x>>12)&7)+(x&0x0800?'.L':'.W');return d+'(A'+r+','+ir+')';}
 if(m===7&&r===0)return hw(r16(ep))+'.W';if(m===7&&r===1)return h(r32(ep))+'.L';
 if(m===7&&r===2){const d=s16(r16(ep));return d+'(PC)->'+h((ep+d)>>>0);}
 if(m===7&&r===3){const x=r16(ep),d=s8(x&255),ir=(x&0x8000?'A':'D')+((x>>12)&7)+(x&0x0800?'.L':'.W');return d+'(PC,'+ir+')->'+h((ep+d)>>>0);}
 if(m===7&&r===4)return'#'+(size==='L'?h(r32(ep)):hw(r16(ep)));
 return'EA('+m+','+r+')';
}
function dec(p){
 if(p<0||p+1>=MAX)return null;
 const w=r16(p),g=w>>>12,m=(w>>3)&7,r=w&7;let len=2,kind='OP',text=hw(w),target=null,fall=true,terminal=false,call=false,reads=[],writes=[];
 if(w===0x4E75||w===0x4E73||w===0x4E77){kind='RTS';text='RTS';terminal=true;fall=false;}
 else if((w&0xFFF8)===0x4E50){kind='LINK';len=4;text='LINK A'+(w&7)+',#'+s16(r16(p+2));reads.push('A'+(w&7));writes.push('A'+(w&7));}
 else if((w&0xFFF8)===0x4E58){kind='UNLK';text='UNLK A'+(w&7);reads.push('A'+(w&7));writes.push('A'+(w&7));}
 else if((w&0xFFC0)===0x4E80||(w&0xFFC0)===0x4EC0){kind=(w&0xFFC0)===0x4E80?'JSR':'JMP';call=kind==='JSR';fall=call;len=2+eaWords(m,r,'L')*2;if(m===7&&r===0)target=s16(r16(p+2))&0xFFFFFF;else if(m===7&&r===1)target=r32(p+2)&0xFFFFFF;else if(m===7&&r===2)target=(p+2+s16(r16(p+2)))>>>0;text=kind+' '+(target!=null?h(target):eaText(p+2,m,r,'L'));}
 else if(g===6){const cc=(w>>8)&15,d=w&255;len=d===0?4:2;const disp=d===0?s16(r16(p+2)):s8(d);target=(p+2+disp)>>>0;kind=cc===0?'BRA':cc===1?'BSR':'Bcc'+cc;call=cc===1;fall=cc!==0;text=kind+' '+h(target);}
 else if((w&0xF0F8)===0x50C8){len=4;target=(p+2+s16(r16(p+2)))>>>0;kind='DBcc';text='DBcc D'+(w&7)+','+h(target);reads.push('D'+(w&7));writes.push('D'+(w&7));}
 else if((w&0xF100)===0x7000){const dr=(w>>9)&7,v=s8(w&255);kind='MOVEQ';text='MOVEQ #'+v+',D'+dr;writes.push('D'+dr);}
 else if(g===1||g===2||g===3){const size=g===1?'B':g===2?'L':'W',sm=(w>>3)&7,sr=w&7,dm=(w>>6)&7,dr=(w>>9)&7;const swd=eaWords(sm,sr,size),sep=p+2,dep=sep+swd*2;len=2+(swd+eaWords(dm,dr,size))*2;const src=eaText(sep,sm,sr,size),dst=dm===0?'D'+dr:dm===1?'A'+dr:eaText(dep,dm,dr,size);kind='MOVE.'+size;text=kind+' '+src+','+dst;if(sm===0)reads.push('D'+sr);if(sm===1)reads.push('A'+sr);if(sm>=2&&sm<=6)reads.push('A'+sr);if(dm===0)writes.push('D'+dr);if(dm===1)writes.push('A'+dr);if(dm>=2&&dm<=6)reads.push('A'+dr);}
 else if((w&0xF1C0)===0x41C0){const ar=(w>>9)&7;len=2+eaWords(m,r,'L')*2;kind='LEA';text='LEA '+eaText(p+2,m,r,'L')+',A'+ar;writes.push('A'+ar);if(m>=2&&m<=6)reads.push('A'+r);}
 else if((w&0xFB80)===0x4880){const size=(w&0x0040)?'L':'W';len=4+eaWords(m,r,size)*2;kind='MOVEM.'+size;text=kind+' mask='+hw(r16(p+2))+','+eaText(p+4,m,r,size);if(m>=2&&m<=6)reads.push('A'+r);}
 else if((w&0xFF00)===0x4A00||(w&0xFF00)===0x4200||(w&0xFF00)===0x4400||(w&0xFF00)===0x4600){const sz=(w>>6)&3,size=sz===0?'B':sz===1?'W':sz===2?'L':'?';len=2+eaWords(m,r,size)*2;const nm=(w&0xFF00)===0x4A00?'TST':(w&0xFF00)===0x4200?'CLR':(w&0xFF00)===0x4400?'NEG':'NOT';kind=nm+'.'+size;text=kind+' '+eaText(p+2,m,r,size);if(m===0){if(nm!=='CLR')reads.push('D'+r);if(nm!=='TST')writes.push('D'+r);}if(m>=2&&m<=6)reads.push('A'+r);}
 else if(g===0){const op=(w>>8)&15,sz=(w>>6)&3;if([0,2,4,6,10,12].includes(op)&&sz!==3){const size=sz===2?'L':sz===1?'W':'B',ib=size==='L'?4:2,imm=size==='L'?r32(p+2):r16(p+2),dep=p+2+ib;len=2+ib+eaWords(m,r,size)*2;const names={0:'ORI',2:'ANDI',4:'SUBI',6:'ADDI',10:'EORI',12:'CMPI'};kind=names[op]+'.'+size;text=kind+' #'+(size==='L'?h(imm):hw(imm))+','+eaText(dep,m,r,size);if(m===0){reads.push('D'+r);if(op!==12)writes.push('D'+r);}if(m>=2&&m<=6)reads.push('A'+r);}}
 else if(g===5){const sz=(w>>6)&3;if(sz!==3){const size=sz===2?'L':sz===1?'W':'B',v=((w>>9)&7)||8,sub=!!(w&0x0100);len=2+eaWords(m,r,size)*2;kind=(sub?'SUBQ':'ADDQ')+'.'+size;text=kind+' #'+v+','+eaText(p+2,m,r,size);if(m===0){reads.push('D'+r);writes.push('D'+r);}if(m===1){reads.push('A'+r);writes.push('A'+r);}if(m>=2&&m<=6)reads.push('A'+r);}}
 else if(g===11){const opm=(w>>6)&7,dr=(w>>9)&7,size=(opm===0||opm===4)?'B':(opm===1||opm===3||opm===5||opm===7)?'W':'L';len=2+eaWords(m,r,size)*2;kind=(opm===3||opm===7)?'CMPA.'+size:'CMP.'+size;text=kind+' '+eaText(p+2,m,r,size)+','+(opm===3||opm===7?'A':'D')+dr;reads.push((opm===3||opm===7?'A':'D')+dr);if(m===0)reads.push('D'+r);if(m===1)reads.push('A'+r);if(m>=2&&m<=6)reads.push('A'+r);}
 else if(g===9||g===13||g===8||g===12){const opm=(w>>6)&7,dr=(w>>9)&7,size=(opm===0||opm===4)?'B':(opm===1||opm===3||opm===5||opm===7)?'W':'L';len=2+eaWords(m,r,size)*2;const nm=g===9?'SUB':g===13?'ADD':g===8?'OR':'AND';kind=nm+'.'+size;text=kind+' '+eaText(p+2,m,r,size)+',D'+dr;reads.push('D'+dr);writes.push('D'+dr);if(m===0)reads.push('D'+r);if(m===1)reads.push('A'+r);if(m>=2&&m<=6)reads.push('A'+r);}
 else if(g===14){kind='SHIFT';text='SHIFT '+hw(w);}
 return{at:p,atHex:h(p),word:hw(w),len,next:p+Math.max(2,len),kind,text,target:target==null?'':h(target),targetNum:target,fall,terminal,call,reads:[...new Set(reads)],writes:[...new Set(writes)]};
}
function raw(lo,hi,marks={}){const a=[];for(let p=lo;p<hi;p+=2)a.push({at:h(p),word:hw(r16(p)),mark:marks[p]||''});return a;}
function ctlTarget(p){const d=dec(p);return d&&d.targetNum!=null?d:null;}
function succ(d,lo,hi){const a=[];if(!d||d.terminal)return a;if(d.kind==='BRA'||d.kind==='JMP'){if(d.targetNum>=lo&&d.targetNum<hi)a.push(d.targetNum);return a;}if(d.kind.startsWith('Bcc')||d.kind==='DBcc'){if(d.targetNum>=lo&&d.targetNum<hi)a.push(d.targetNum);if(d.next>=lo&&d.next<hi)a.push(d.next);return a;}if(d.next>=lo&&d.next<hi)a.push(d.next);return a;}
function pathBfs(start,targets,lo,hi,maxNodes=1200){const q=[{p:start,path:[]}],seen=new Set();let qi=0;while(qi<q.length&&qi<maxNodes){const s=q[qi++];if(seen.has(s.p))continue;seen.add(s.p);const d=dec(s.p);if(!d)continue;const np=[...s.path,d];if(targets.has(s.p))return np;for(const n of succ(d,lo,hi))if(!seen.has(n))q.push({p:n,path:np});}return[];}
const TABLE=0x010CF8,SEL=0x010E66,SELLOAD=0x010E6E,CALL1=0x010E76,HELP=0x011C26,CALL2=0x010F98,EDGE=0x010FA2;
const selectorStrict=[0x010E66,0x010E6A,0x010E6E,0x010E72,0x010E76].map(dec);
const helperCallRefs=[];for(let p=0x010C00;p<0x011000;p+=2){const d=ctlTarget(p);if(d&&d.targetNum===HELP)helperCallRefs.push({at:d.atHex,text:d.text,target:d.target});}
const a1Writes=[];for(let p=0x010E00;p<CALL2;p+=2){const d=dec(p);if(d&&d.writes.includes('A1'))a1Writes.push({at:d.atHex,text:d.text,word:d.word,len:d.len});}
const bridge1=pathBfs(SEL,new Set([CALL1]),0x010E00,0x010F60,500);
const bridge2=pathBfs(SEL,new Set([CALL2,EDGE]),0x010E00,0x010FA6,1600);
const helperCfg=[];{
 const lo=HELP,hi=HELP+0x140,q=[HELP],seen=new Set();let qi=0;while(qi<q.length&&qi<400){const p=q[qi++];if(seen.has(p)||p<lo||p>=hi)continue;seen.add(p);const d=dec(p);if(!d)continue;helperCfg.push(d);for(const n of succ(d,lo,hi))if(!seen.has(n))q.push(n);}helperCfg.sort((a,b)=>a.at-b.at);
}
const helperA1=helperCfg.filter(d=>d.reads.includes('A1')||d.writes.includes('A1')||/\(A1/.test(d.text));
const helperD0=helperCfg.filter(d=>d.reads.includes('D0')||d.writes.includes('D0'));
const marks={};marks[SEL]='SEL +7E';marks[SELLOAD]='A1=player';marks[CALL1]='CALL 11C26';marks[CALL2]='CALL 11C26';marks[EDGE]='DISPATCH';marks[HELP]='HELP';
const edgeDec=dec(EDGE),preD0=dec(0x010FA0),call2Dec=dec(CALL2),call1Dec=dec(CALL1);
const verdict={
 selectorAt:h(SEL),selectorText:selectorStrict[0]?.text||'',playerLoadAt:h(SELLOAD),playerLoadText:selectorStrict[2]?.text||'',
 first11C26Call:call1Dec?.text||'',second11C26Call:call2Dec?.text||'',helperRefsLocal:helperCallRefs.length,
 edgeAt:h(EDGE),edgeText:edgeDec?.text||'',preD0:preD0?.text||'',
 pathSelectorToFirstCall:bridge1.length,pathSelectorToSecondCallOrEdge:bridge2.length,
 a1WritesBetweenSelectorAndSecondCall:a1Writes.length,helperInstructions:helperCfg.length,helperA1Ops:helperA1.length,helperD0Ops:helperD0.length
};
const slim=x=>({at:x.atHex,text:x.text,word:x.word,len:x.len,target:x.target,reads:x.reads.join(','),writes:x.writes.join(',')});
const out={version:'wof-selector-11c26-dispatch-bridge-v1',verdict,
 selectorStrict:selectorStrict.map(slim),helperCallRefs,a1Writes,
 bridgeToFirstCall:bridge1.map(slim),bridgeToSecondCallOrEdge:bridge2.map(slim),
 helperCfg:helperCfg.map(slim),helperA1:helperA1.map(slim),helperD0:helperD0.map(slim),
 rawSelector:raw(0x010E5C,0x010E90,marks),rawDispatch:raw(0x010F80,0x010FAA,marks),rawHelper:raw(HELP,HELP+0x90,marks)};
self.__WOF_SELECTOR_11C26_BRIDGE=out;
console.log('=== SELECTOR -> 11C26 -> DISPATCH VERDICT ===');console.table([verdict]);
console.log('=== SELECTOR STRICT ===');console.table(out.selectorStrict);
console.log('=== 11C26 LOCAL CALL REFS ===');console.table(helperCallRefs);
console.log('=== A1 WRITES BEFORE SECOND 11C26 CALL ===');console.table(a1Writes);
console.log('=== 11C26 A1 OPS ===');console.table(out.helperA1);
console.log('=== 11C26 D0 OPS ===');console.table(out.helperD0);
console.log('=== SELECTOR 11C26 DISPATCH BRIDGE JSON ===');console.log(JSON.stringify(out,null,2));
return out;
})().catch(e=>{console.error('WOF_SELECTOR_11C26_BRIDGE_ERROR',e);throw e;});