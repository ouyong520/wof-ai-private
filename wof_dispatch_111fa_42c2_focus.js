(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return (0,eval)(await r.text());};
if(!self.__WOF_ROM_LOC_CACHE)await load('wof_resume_low4_chain.js');
const C=self.__WOF_ROM_LOC_CACHE;if(!C)throw new Error('ROM cache unavailable');
const MOD=_0x515056,M=MOD.HEAPU8,base=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-base);
const r8=o=>M[base+(SW?(o^1):o)]>>>0;
const r16=o=>((r8(o)<<8)|r8(o+1))>>>0;
const r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
const s8=v=>v&0x80?v-0x100:v,s16=v=>v&0x8000?v-0x10000:v;
const h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0');
const hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
function eaWords(m,r,size){if(m<=4)return 0;if(m===5||m===6)return 1;if(m===7){if(r===0||r===2||r===3)return 1;if(r===1)return 2;if(r===4)return size==='L'?2:1;}return 0;}
function ea(p,m,r,size,extBase=p+2){
 if(m===0)return{text:'D'+r,regs:['D'+r]};if(m===1)return{text:'A'+r,regs:['A'+r]};if(m===2)return{text:'(A'+r+')',regs:['A'+r]};if(m===3)return{text:'(A'+r+')+',regs:['A'+r]};if(m===4)return{text:'-(A'+r+')',regs:['A'+r]};
 if(m===5){const d=s16(r16(extBase));return{text:d+'(A'+r+')',regs:['A'+r],disp:d};}
 if(m===6){const x=r16(extBase),d=s8(x&255),ir=(x&0x8000?'A':'D')+((x>>12)&7)+(x&0x0800?'.L':'.W');return{text:d+'(A'+r+','+ir+')',regs:['A'+r,ir.replace(/\.[WL]$/,'')],disp:d,ext:hw(x)};}
 if(m===7&&r===0)return{text:hw(r16(extBase))+'.W',regs:[]};
 if(m===7&&r===1)return{text:h(r32(extBase))+'.L',regs:[]};
 if(m===7&&r===2){const d=s16(r16(extBase)),t=(p+2+d)>>>0;return{text:d+'(PC)->'+h(t),regs:[],target:t};}
 if(m===7&&r===3){const x=r16(extBase),d=s8(x&255),ir=(x&0x8000?'A':'D')+((x>>12)&7)+(x&0x0800?'.L':'.W'),t=(p+2+d)>>>0;return{text:d+'(PC,'+ir+')->'+h(t),regs:[ir.replace(/\.[WL]$/,'')],target:t,ext:hw(x)};}
 if(m===7&&r===4){const v=size==='L'?r32(extBase):r16(extBase);return{text:'#'+(size==='L'?h(v):hw(v)),regs:[],imm:v};}
 return{text:'EA('+m+','+r+')',regs:[]};
}
function dec(p){
 const w=r16(p),g=w>>>12,m=(w>>3)&7,r=w&7;let len=2,kind='OP',text=hw(w),target=null,terminal=false,cmp=false,call=false,reads=[],writes=[];
 if(w===0x4E75){return{at:h(p),word:hw(w),len:2,kind:'RTS',text:'RTS',terminal:true,cmp:false,call:false,reads:[],writes:[]};}
 if((w&0xFFC0)===0x4E80||(w&0xFFC0)===0x4EC0){kind=(w&0xFFC0)===0x4E80?'JSR':'JMP';call=kind==='JSR';len=2+eaWords(m,r,'L')*2;const z=ea(p,m,r,'L');target=z.target??(m===7&&r===1?r32(p+2):null);text=kind+' '+(target!=null?h(target):z.text);reads=z.regs;return{at:h(p),word:hw(w),len,kind,text,target:target!=null?h(target):'',terminal:kind==='JMP',cmp:false,call,reads,writes:[]};}
 if(g===6){const cc=(w>>8)&15,d=w&255;len=d===0?4:2;const disp=d===0?s16(r16(p+2)):s8(d);target=(p+2+disp)>>>0;kind=cc===0?'BRA':cc===1?'BSR':'Bcc'+cc;call=cc===1;text=kind+' '+h(target);return{at:h(p),word:hw(w),len,kind,text,target:h(target),terminal:cc===0,cmp:false,call,reads:[],writes:[]};}
 if((w&0xF100)===0x7000){const dr=(w>>9)&7,v=s8(w&255);kind='MOVEQ';text='MOVEQ #'+v+',D'+dr;writes=['D'+dr];return{at:h(p),word:hw(w),len:2,kind,text,terminal:false,cmp:false,call:false,reads:[],writes};}
 if(g===1||g===2||g===3){const size=g===1?'B':g===2?'L':'W',sm=(w>>3)&7,sr=w&7,dm=(w>>6)&7,dr=(w>>9)&7;const swd=eaWords(sm,sr,size),src=ea(p,sm,sr,size,p+2),dp=p+2+swd*2,dst=dm===0?{text:'D'+dr,regs:[]}:(dm===1?{text:'A'+dr,regs:[]}:ea(p,dm,dr,size,dp));len=2+(swd+eaWords(dm,dr,size))*2;kind='MOVE.'+size;text=kind+' '+src.text+','+dst.text;reads=src.regs.slice();writes=dm===0?['D'+dr]:dm===1?['A'+dr]:[];return{at:h(p),word:hw(w),len,kind,text,terminal:false,cmp:false,call:false,reads,writes,src:src.text,dst:dst.text};}
 if((w&0xF1C0)===0x41C0){const ar=(w>>9)&7,z=ea(p,m,r,'L');len=2+eaWords(m,r,'L')*2;kind='LEA';text='LEA '+z.text+',A'+ar;reads=z.regs;writes=['A'+ar];return{at:h(p),word:hw(w),len,kind,text,terminal:false,cmp:false,call:false,reads,writes};}
 if(g===11){const sz=(w>>6)&3,size=sz===2?'L':sz===1?'W':'B',dr=(w>>9)&7,z=ea(p,m,r,size);len=2+eaWords(m,r,size)*2;kind='CMP.'+size;text=kind+' '+z.text+',D'+dr;cmp=true;reads=z.regs.concat('D'+dr);return{at:h(p),word:hw(w),len,kind,text,terminal:false,cmp,call:false,reads,writes:[]};}
 if(g===0){const op=(w>>8)&15,sz=(w>>6)&3;if([0,2,4,6,10,12].includes(op)&&sz!==3){const size=sz===2?'L':sz===1?'W':'B',ib=size==='L'?4:2,imm=size==='L'?r32(p+2):r16(p+2),z=ea(p,m,r,size,p+2+ib),names={0:'ORI',2:'ANDI',4:'SUBI',6:'ADDI',10:'EORI',12:'CMPI'};len=2+ib+eaWords(m,r,size)*2;kind=names[op]+'.'+size;text=kind+' #'+(size==='L'?h(imm):hw(imm))+','+z.text;cmp=op===12;reads=z.regs.slice();return{at:h(p),word:hw(w),len,kind,text,terminal:false,cmp,call:false,reads,writes:[]};}}
 if(g===5&&((w>>6)&3)!==3){const size=((w>>6)&3)===2?'L':((w>>6)&3)===1?'W':'B',v=((w>>9)&7)||8,z=ea(p,m,r,size);len=2+eaWords(m,r,size)*2;kind=(w&0x0100?'SUBQ':'ADDQ')+'.'+size;text=kind+' #'+v+','+z.text;reads=z.regs.slice();writes=m===0?['D'+r]:m===1?['A'+r]:[];return{at:h(p),word:hw(w),len,kind,text,terminal:false,cmp:false,call:false,reads,writes};}
 if(g===4&&(w&0xFFC0)===0x4A00){const sz=(w>>6)&3,size=sz===2?'L':sz===1?'W':'B',z=ea(p,m,r,size);len=2+eaWords(m,r,size)*2;kind='TST.'+size;text=kind+' '+z.text;reads=z.regs;return{at:h(p),word:hw(w),len,kind,text,terminal:false,cmp:true,call:false,reads,writes:[]};}
 return{at:h(p),word:hw(w),len,kind,text,terminal:false,cmp:false,call:false,reads,writes};
}
function linear(start,end,max=160){const out=[];let p=start;for(let i=0;i<max&&p<end;){const d=dec(p);out.push(d);p+=Math.max(2,d.len);i++;if(d.terminal)break;}return out;}
function cfg(start,cap=0x240){const hi=Math.min(MAX,start+cap),q=[start],seen=new Set(),rows=[];while(q.length&&seen.size<300){const p=q.shift();if(p<start||p>=hi||(p&1)||seen.has(p))continue;seen.add(p);const d=dec(p);rows.push(d);const next=p+d.len;const t=d.target?parseInt(d.target,16):null;if(d.kind==='BRA'){if(t!=null)q.push(t);continue;}if(d.kind.startsWith('Bcc')){if(next<hi)q.push(next);if(t!=null)q.push(t);continue;}if(d.kind==='BSR'){if(next<hi)q.push(next);continue;}if(d.kind==='JMP'||d.terminal)continue;if(next<hi)q.push(next);}rows.sort((a,b)=>parseInt(a.at,16)-parseInt(b.at,16));return rows;}
const caller=linear(0x0111A0,0x011200,96);
const helper=cfg(0x0042C2,0x300);
const cmpRows=helper.filter(x=>x.cmp||x.kind.startsWith('Bcc'));
const memRegs=[...new Set(helper.flatMap(x=>x.reads||[]).filter(x=>/^A[0-7]$/.test(x)))];
const helperWrites=[...new Set(helper.flatMap(x=>x.writes||[]))];
const helperCalls=helper.filter(x=>x.call);
const directCall=caller.find(x=>x.target==='0x0042C2')||null;
const before=directCall?caller.filter(x=>parseInt(x.at,16)<parseInt(directCall.at,16)).slice(-12):caller.slice(-12);
console.log('=== 0x0111FA CALLER STRICT ===');console.table(caller);
console.log('=== BEFORE 0x0042C2 CALL ===');console.table(before);
console.log('=== 0x0042C2 HELPER CFG ===');console.table(helper);
console.log('=== 0x0042C2 CMP / BRANCH ===');console.table(cmpRows);
const verdict={edgeAt:'0x0111FA',helper:'0x0042C2',helperInstructions:helper.length,helperCmp:helper.filter(x=>x.cmp).length,helperBranches:helper.filter(x=>x.kind.startsWith('Bcc')).length,helperCalls:helperCalls.map(x=>x.target||x.text).join(' '),helperAddrRegsRead:memRegs.join(' '),helperRegsWritten:helperWrites.join(' '),callAt:directCall?.at||'',callText:directCall?.text||'',beforeCall:before.map(x=>x.text).join(' | ')};
const out={version:'wof-dispatch-111fa-42c2-focus-v1',verdict,before,caller,helper,cmpRows};self.__WOF_111FA_42C2_FOCUS=out;
console.log('=== 111FA 42C2 FOCUS JSON ===');console.log(JSON.stringify({verdict,before,cmpRows,helperCalls},null,2));
return out;
})().catch(e=>{console.error('WOF_111FA_42C2_FOCUS_ERROR',e);throw e;});
