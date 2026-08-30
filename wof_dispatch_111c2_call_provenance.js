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
function eaText(p,m,r,size){
 if(m===0)return'D'+r;if(m===1)return'A'+r;if(m===2)return'(A'+r+')';if(m===3)return'(A'+r+')+';if(m===4)return'-(A'+r+')';
 if(m===5)return s16(r16(p+2))+'(A'+r+')';
 if(m===6){const x=r16(p+2),d=s8(x&255),ir=(x&0x8000?'A':'D')+((x>>12)&7)+(x&0x0800?'.L':'.W');return d+'(A'+r+','+ir+')';}
 if(m===7&&r===0)return hw(r16(p+2))+'.W';if(m===7&&r===1)return h(r32(p+2))+'.L';
 if(m===7&&r===2){const d=s16(r16(p+2));return d+'(PC)->'+h((p+2+d)>>>0);}
 if(m===7&&r===3){const x=r16(p+2),d=s8(x&255),ir=(x&0x8000?'A':'D')+((x>>12)&7)+(x&0x0800?'.L':'.W');return d+'(PC,'+ir+')->'+h((p+2+d)>>>0);}
 if(m===7&&r===4)return'#'+(size==='L'?h(r32(p+2)):hw(r16(p+2)));
 return'EA('+m+','+r+')';
}
function dec(p){
 if(p<0||p+1>=MAX)return null;const w=r16(p),g=w>>>12,m=(w>>3)&7,r=w&7;let len=2,kind='OP',text=hw(w),target=null,fall=true,terminal=false,call=false,reads=[],writes=[];
 if(w===0x4E75||w===0x4E73||w===0x4E77){kind='RTS';text='RTS';terminal=true;fall=false;}
 else if((w&0xFFC0)===0x4E80||(w&0xFFC0)===0x4EC0){kind=(w&0xFFC0)===0x4E80?'JSR':'JMP';call=kind==='JSR';fall=call;len=2+eaWords(m,r,'L')*2;if(m===7&&r===0)target=s16(r16(p+2))&0xFFFFFF;else if(m===7&&r===1)target=r32(p+2)&0xFFFFFF;else if(m===7&&r===2)target=(p+2+s16(r16(p+2)))>>>0;text=kind+' '+(target!=null?h(target):eaText(p,m,r,'L'));}
 else if(g===6){const cc=(w>>8)&15,d=w&255;len=d===0?4:2;const disp=d===0?s16(r16(p+2)):s8(d);target=(p+2+disp)>>>0;kind=cc===0?'BRA':cc===1?'BSR':'Bcc'+cc;call=cc===1;fall=cc!==0;text=kind+' '+h(target);}
 else if((w&0xF100)===0x7000){const dr=(w>>9)&7,v=s8(w&255);kind='MOVEQ';text='MOVEQ #'+v+',D'+dr;writes=['D'+dr];}
 else if(g===1||g===2||g===3){const size=g===1?'B':g===2?'L':'W',sm=(w>>3)&7,sr=w&7,dm=(w>>6)&7,dr=(w>>9)&7;const swd=eaWords(sm,sr,size),dp=p+2+swd*2;len=2+(swd+eaWords(dm,dr,size))*2;const src=eaText(p,sm,sr,size),dst=dm===0?'D'+dr:dm===1?'A'+dr:eaText(dp,dm,dr,size);kind='MOVE.'+size;text=kind+' '+src+','+dst;if(sm===0)reads.push('D'+sr);if(sm===1)reads.push('A'+sr);if(sm>=2&&sm<=6)reads.push('A'+sr);if(dm===0)writes.push('D'+dr);if(dm===1)writes.push('A'+dr);if(dm>=2&&dm<=6)reads.push('A'+dr);}
 else if((w&0xF1C0)===0x41C0){const ar=(w>>9)&7;len=2+eaWords(m,r,'L')*2;kind='LEA';text='LEA '+eaText(p,m,r,'L')+',A'+ar;writes=['A'+ar];if(m>=2&&m<=6)reads.push('A'+r);}
 else if(g===0){const op=(w>>8)&15,sz=(w>>6)&3;if([0,2,4,6,10,12].includes(op)&&sz!==3){const size=sz===2?'L':sz===1?'W':'B',immBytes=size==='L'?4:2,imm=size==='L'?r32(p+2):r16(p+2);len=2+immBytes+eaWords(m,r,size)*2;const names={0:'ORI',2:'ANDI',4:'SUBI',6:'ADDI',10:'EORI',12:'CMPI'};kind=names[op]+'.'+size;text=kind+' #'+(size==='L'?h(imm):hw(imm))+','+eaText(p+immBytes,m,r,size);if(m===0){reads.push('D'+r);if(op!==12)writes.push('D'+r);}if(m>=2&&m<=6)reads.push('A'+r);}}
 else if(g===5){const sz=(w>>6)&3;if(sz!==3){const size=sz===2?'L':sz===1?'W':'B',v=((w>>9)&7)||8,sub=!!(w&0x0100);len=2+eaWords(m,r,size)*2;kind=(sub?'SUBQ':'ADDQ')+'.'+size;text=kind+' #'+v+','+eaText(p,m,r,size);if(m===0){reads.push('D'+r);writes.push('D'+r);}if(m===1){reads.push('A'+r);writes.push('A'+r);}if(m>=2&&m<=6)reads.push('A'+r);}}
 else if(g===11){const sz=(w>>6)&3,size=sz===2?'L':sz===1?'W':'B',dr=(w>>9)&7;len=2+eaWords(m,r,size)*2;kind='CMP.'+size;text=kind+' '+eaText(p,m,r,size)+',D'+dr;reads.push('D'+dr);if(m===0)reads.push('D'+r);if(m===1)reads.push('A'+r);if(m>=2&&m<=6)reads.push('A'+r);}
 len=Math.max(2,len);return{at:p,atHex:h(p),word:hw(w),len,next:p+len,kind,text,target:target==null?'':h(target),fall,terminal,call,reads:[...new Set(reads)],writes:[...new Set(writes)]};
}
function linear(start,end,max=96){const out=[];let p=start;for(let i=0;i<max&&p<end;){const d=dec(p);if(!d)break;out.push(d);p=d.next;i++;if(d.terminal||d.kind==='JMP'||d.kind==='BRA')break;}return out;}
function prevFall(cur,lo){const a=[];for(let p=Math.max(lo,cur-10)&~1;p<cur;p+=2){const d=dec(p);if(d&&d.fall&&d.next===cur)a.push(d);}return a;}
function controlPreds(target,lo,hi){const a=[];for(let p=lo&~1;p<hi-6;p+=2){const d=dec(p);if(!d||!d.target)continue;const t=parseInt(d.target,16);if(t===target&&['BRA','BSR','JSR','JMP'].includes(d.kind)||t===target&&d.kind.startsWith('Bcc'))a.push(d);}return a;}
function reversePaths(start,lo,limit=160){const q=[{cur:start,path:[],steps:0}],out=[],seen=new Set();let qi=0;while(qi<q.length&&qi<4000){const s=q[qi++];if(s.steps>=limit||s.cur<=lo){out.push(s);continue;}const preds=[...prevFall(s.cur,lo),...controlPreds(s.cur,lo,start+2)];if(!preds.length){out.push(s);continue;}for(const d of preds){const k=d.at+'|'+s.cur+'|'+s.steps;if(seen.has(k))continue;seen.add(k);q.push({cur:d.at,path:[d,...s.path],steps:s.steps+1});}}return out.sort((a,b)=>b.path.length-a.path.length).slice(0,12);}
const CALL=0x0111C2,EDGE=0x0111FA,HELPER=0x0042C2;
const call=dec(CALL);
const after=linear(CALL,EDGE+8,64);
const incoming=controlPreds(CALL,0x010F00,0x011400).map(d=>({at:d.atHex,text:d.text,target:d.target}));
const paths=reversePaths(CALL,Math.max(0,CALL-0x900),80);
const prov=[];
for(const p of paths){const rel=p.path.filter(d=>d.writes.some(x=>['A0','A1','A2','A4','D0'].includes(x))||d.call||d.kind.startsWith('CMP')||d.kind.startsWith('Bcc')).slice(-32);prov.push({start:h(p.cur),steps:p.steps,ops:rel.map(d=>({at:d.atHex,text:d.text,reads:d.reads.join(','),writes:d.writes.join(',')}))});}
const exactIsHelper=!!(call&&call.call&&call.target===h(HELPER));
const postCalls=after.filter(x=>x.call).map(x=>({at:x.atHex,text:x.text,target:x.target}));
const postD0=after.filter(x=>x.reads.includes('D0')||x.writes.includes('D0')||x.kind.startsWith('Bcc')).map(x=>({at:x.atHex,text:x.text,reads:x.reads.join(','),writes:x.writes.join(',')}));
const verdict={callAt:h(CALL),callWord:call?.word||'',callText:call?.text||'',exactIs42C2:exactIsHelper,edgeAt:h(EDGE),incomingToCall:incoming.length,reversePaths:paths.length,postCalls:postCalls.map(x=>x.text).join(' | '),postD0Ops:postD0.length};
const out={version:'wof-dispatch-111c2-call-provenance-v1',verdict,call,incoming,after:after.map(x=>({at:x.atHex,text:x.text,reads:x.reads.join(','),writes:x.writes.join(',')})),postD0,provenance:prov};self.__WOF_111C2_PROVENANCE=out;
console.log('=== 111C2 CALL PROVENANCE VERDICT ===');console.table([verdict]);
console.log('=== 111C2 -> 111FA STRICT PATH ===');console.table(out.after);
console.log('=== 111C2 INCOMING CONTROL ===');console.table(incoming);
console.log('=== 111C2 REGISTER PROVENANCE ===');console.dir(prov,{depth:null});
console.log('=== 111C2 CALL PROVENANCE JSON ===');console.log(JSON.stringify(out,null,2));
return out;
})().catch(e=>{console.error('WOF_111C2_PROVENANCE_ERROR',e);throw e;});