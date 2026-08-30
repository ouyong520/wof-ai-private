(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
if(!self.__WOF_ROM_LOC_CACHE){await load('wof_resume_dispatch_selector.js');}
const C=self.__WOF_ROM_LOC_CACHE;if(!C)throw new Error('ROM cache unavailable');
const MOD=_0x515056,M=MOD.HEAPU8,base=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-base);
const r8=o=>M[base+(SW?(o^1):o)]>>>0;
const r16=o=>((r8(o)<<8)|r8(o+1))>>>0;
const r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
const s8=v=>v&0x80?v-0x100:v,s16=v=>v&0x8000?v-0x10000:v;
const h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0');
const hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
const TABLE=0x010CF8, ENTRIES=[0x010CF8,0x010CFC,0x010D00], PLAYERS=[0x00FFBE1C,0x00FFBEFC,0x00FFBFDC], EDGES=[0x010F48,0x010FA2];
function eaWords(m,r,size){if(m<=4)return 0;if(m===5||m===6)return 1;if(m===7){if(r===0||r===2||r===3)return 1;if(r===1)return 2;if(r===4)return size==='L'?2:1;}return 0;}
function ea(p,m,r,size,extBase=p+2){
 if(m===0)return{text:'D'+r,regs:['D'+r],mode:m,reg:r};
 if(m===1)return{text:'A'+r,regs:['A'+r],mode:m,reg:r};
 if(m===2)return{text:'(A'+r+')',regs:['A'+r],baseReg:'A'+r,mode:m,reg:r};
 if(m===3)return{text:'(A'+r+')+',regs:['A'+r],baseReg:'A'+r,mode:m,reg:r};
 if(m===4)return{text:'-(A'+r+')',regs:['A'+r],baseReg:'A'+r,mode:m,reg:r};
 if(m===5){const d=s16(r16(extBase));return{text:d+'(A'+r+')',regs:['A'+r],baseReg:'A'+r,disp:d,mode:m,reg:r};}
 if(m===6){const x=r16(extBase),d=s8(x&255),ir=(x&0x8000?'A':'D')+((x>>12)&7),isz=x&0x0800?'.L':'.W';return{text:d+'(A'+r+','+ir+isz+')',regs:['A'+r,ir],baseReg:'A'+r,indexReg:ir,indexSize:isz,disp:d,ext:hw(x),mode:m,reg:r};}
 if(m===7&&r===0){const raw=r16(extBase),t=s16(raw)>>>0;return{text:hw(raw)+'.W',regs:[],target:t,abs:true,mode:m,reg:r};}
 if(m===7&&r===1){const t=r32(extBase)>>>0;return{text:h(t)+'.L',regs:[],target:t,abs:true,mode:m,reg:r};}
 if(m===7&&r===2){const d=s16(r16(extBase)),t=(p+2+d)>>>0;return{text:d+'(PC)->'+h(t),regs:[],target:t,pcBase:t,disp:d,mode:m,reg:r};}
 if(m===7&&r===3){const x=r16(extBase),d=s8(x&255),ir=(x&0x8000?'A':'D')+((x>>12)&7),isz=x&0x0800?'.L':'.W',t=(p+2+d)>>>0;return{text:d+'(PC,'+ir+isz+')->base '+h(t),regs:[ir],target:t,pcBase:t,indexReg:ir,indexSize:isz,disp:d,ext:hw(x),mode:m,reg:r};}
 if(m===7&&r===4){const v=size==='L'?r32(extBase):r16(extBase);return{text:'#'+(size==='L'?h(v):hw(v)),regs:[],imm:v,mode:m,reg:r};}
 return{text:'EA('+m+','+r+')',regs:[],mode:m,reg:r};
}
function dec(p){
 const w=r16(p),g=w>>>12,m=(w>>3)&7,r=w&7;let len=2,kind='OP',text=hw(w),target=null,terminal=false,call=false,cmp=false,reads=[],writes=[],srcEA=null,dstEA=null,size='';
 if(w===0x4E75||w===0x4E73||w===0x4E77)return{at:p,len:2,kind:'RET',text:w===0x4E75?'RTS':'RET',terminal:true,call:false,cmp:false,reads:[],writes:[]};
 if((w&0xFFC0)===0x4E80||(w&0xFFC0)===0x4EC0){kind=(w&0xFFC0)===0x4E80?'JSR':'JMP';call=kind==='JSR';len=2+eaWords(m,r,'L')*2;const z=ea(p,m,r,'L');target=z.target??null;text=kind+' '+(target!=null?h(target):z.text);reads=z.regs.slice();return{at:p,len,kind,text,target,terminal:kind==='JMP',call,cmp:false,reads,writes:[],srcEA:z};}
 if(g===6){const cc=(w>>8)&15,d=w&255;len=d===0?4:2;const disp=d===0?s16(r16(p+2)):s8(d);target=(p+2+disp)>>>0;kind=cc===0?'BRA':cc===1?'BSR':'Bcc'+cc;call=cc===1;text=kind+' '+h(target);return{at:p,len,kind,text,target,terminal:cc===0,call,cmp:false,reads:[],writes:[]};}
 if((w&0xF100)===0x7000){const dr=(w>>9)&7,v=s8(w&255);return{at:p,len:2,kind:'MOVEQ',text:'MOVEQ #'+v+',D'+dr,target:null,terminal:false,call:false,cmp:false,reads:[],writes:['D'+dr]};}
 if(g===1||g===2||g===3){size=g===1?'B':g===2?'L':'W';const sm=(w>>3)&7,sr=w&7,dm=(w>>6)&7,dr=(w>>9)&7,swd=eaWords(sm,sr,size);srcEA=ea(p,sm,sr,size,p+2);const dp=p+2+swd*2;dstEA=dm===0?{text:'D'+dr,regs:[],mode:0,reg:dr}:dm===1?{text:'A'+dr,regs:[],mode:1,reg:dr}:ea(p,dm,dr,size,dp);len=2+(swd+eaWords(dm,dr,size))*2;kind=dm===1&&size!=='B'?'MOVEA.'+size:'MOVE.'+size;text=kind+' '+srcEA.text+','+dstEA.text;reads=srcEA.regs.slice();writes=dm===0?['D'+dr]:dm===1?['A'+dr]:[];return{at:p,len,kind,text,target:null,terminal:false,call:false,cmp:false,reads,writes,srcEA,dstEA,size};}
 if((w&0xF1C0)===0x41C0){const ar=(w>>9)&7;srcEA=ea(p,m,r,'L');len=2+eaWords(m,r,'L')*2;kind='LEA';text='LEA '+srcEA.text+',A'+ar;reads=srcEA.regs.slice();writes=['A'+ar];return{at:p,len,kind,text,target:null,terminal:false,call:false,cmp:false,reads,writes,srcEA,dstEA:{text:'A'+ar,mode:1,reg:ar},size:'L'};}
 if(g===11){const sz=(w>>6)&3;size=sz===2?'L':sz===1?'W':'B';const dr=(w>>9)&7;srcEA=ea(p,m,r,size);len=2+eaWords(m,r,size)*2;kind='CMP.'+size;text=kind+' '+srcEA.text+',D'+dr;reads=srcEA.regs.concat('D'+dr);return{at:p,len,kind,text,target:null,terminal:false,call:false,cmp:true,reads,writes:[],srcEA,size};}
 if(g===5&&((w>>6)&3)===3&&m===1){const cc=(w>>8)&15,disp=s16(r16(p+2)),t=(p+2+disp)>>>0;return{at:p,len:4,kind:'DBcc'+cc,text:'DBcc'+cc+' D'+r+','+h(t),target:t,terminal:false,call:false,cmp:false,reads:['D'+r],writes:['D'+r]};}
 if(g===4&&(w&0xFFC0)===0x4A00){const sz=(w>>6)&3;size=sz===2?'L':sz===1?'W':'B';srcEA=ea(p,m,r,size);len=2+eaWords(m,r,size)*2;return{at:p,len,kind:'TST.'+size,text:'TST.'+size+' '+srcEA.text,target:null,terminal:false,call:false,cmp:true,reads:srcEA.regs.slice(),writes:[],srcEA,size};}
 if(g===5&&((w>>6)&3)!==3){const sz=(w>>6)&3;size=sz===2?'L':sz===1?'W':'B';const v=((w>>9)&7)||8;dstEA=ea(p,m,r,size);len=2+eaWords(m,r,size)*2;kind=(w&0x0100?'SUBQ.':'ADDQ.')+size;text=kind+' #'+v+','+dstEA.text;reads=dstEA.regs.slice();writes=m===0?['D'+r]:m===1?['A'+r]:[];return{at:p,len,kind,text,target:null,terminal:false,call:false,cmp:false,reads,writes,dstEA,size};}
 return{at:p,len,kind,text,target:null,terminal:false,call:false,cmp:false,reads,writes};
}
function refType(d){
 const z=d.srcEA;if(!z)return null;
 const exact=ENTRIES.includes(z.target)||ENTRIES.includes(z.pcBase);
 const base=(z.pcBase===TABLE||z.target===TABLE);
 const imm=z.imm===TABLE;
 if(!(exact||base||imm))return null;
 const indexed=!!z.indexReg;
 return{refBase:z.pcBase??z.target??z.imm,indexed,indexReg:z.indexReg||'',kind:imm?'address-immediate':(indexed?'indexed-table':'direct-table'),dst:(d.writes||[]).join(',')};
}
const table=ENTRIES.map((a,i)=>({slot:i+1,at:h(a),value:h(r32(a)),expected:h(PLAYERS[i]),match:r32(a)===PLAYERS[i]}));
console.log('=== 010CF8 PLAYER TABLE VERIFY ===');console.table(table);
const xrefs=[];
for(let p=0;p<MAX-6;p+=2){const d=dec(p),rf=refType(d);if(rf)xrefs.push({at:p,offline:(p-(C.offlineDelta|0))>>>0,text:d.text,len:d.len,...rf});}
function forward(start,cap=0x500){const hi=Math.min(MAX,start+cap),q=[start],seen=new Set(),parent=new Map(),rows=new Map();while(q.length&&seen.size<1200){const p=q.shift();if(p<0||p>=hi||(p&1)||seen.has(p))continue;seen.add(p);const d=dec(p);rows.set(p,d);if(EDGES.includes(p))continue;const n=p+Math.max(2,d.len);const push=t=>{if(t==null||t<start||t>=hi||(t&1)||seen.has(t))return;if(!parent.has(t))parent.set(t,p);q.push(t);};if(d.kind==='BRA'||d.kind==='JMP'){push(d.target);continue;}if(d.kind.startsWith('Bcc')){push(n);push(d.target);continue;}if(d.kind.startsWith('DBcc')){push(n);push(d.target);continue;}if(d.kind==='BSR'||d.kind==='JSR'){push(n);continue;}if(d.terminal)continue;push(n);}return{seen,parent,rows};}
function pathTo(F,start,t){if(!F.seen.has(t))return[];const a=[t];let cur=t,guard=0;while(cur!==start&&guard++<500){cur=F.parent.get(cur);if(cur==null)return[];a.push(cur);}return a.reverse();}
const results=[];
for(const x of xrefs){const d=dec(x.at),F=forward(x.at,0x600);const p1=pathTo(F,x.at,EDGES[0]),p2=pathTo(F,x.at,EDGES[1]);const dst=(d.writes||[])[0]||'';const uses=[];if(dst){for(const [at,z] of [...F.rows.entries()].sort((a,b)=>a[0]-b[0])){if(at===x.at)continue;if((z.reads||[]).includes(dst)||(z.writes||[]).includes(dst))uses.push({at:h(at),text:z.text,reads:(z.reads||[]).join(' '),writes:(z.writes||[]).join(' ')});if(uses.length>=40)break;}}
 results.push({at:h(x.at),offline:h(x.offline),text:x.text,kind:x.kind,refBase:h(x.refBase),indexed:x.indexed,indexReg:x.indexReg,dst:x.dst,reaches010F48:p1.length>0,reaches010FA2:p2.length>0,path010F48:p1.map(h),path010FA2:p2.map(h),uses});
}
console.log('=== 010CF8 REAL CODE XREF CANDIDATES ===');console.table(results.map(r=>({at:r.at,offline:r.offline,text:r.text,kind:r.kind,refBase:r.refBase,indexed:r.indexed,indexReg:r.indexReg,dst:r.dst,F48:r.reaches010F48,FA2:r.reaches010FA2})));
for(const r of results){if(!(r.reaches010F48||r.reaches010FA2||r.indexed))continue;console.log('=== XREF DETAIL '+r.at+' ===');console.log('PATH 010F48',r.path010F48.join(' -> '));console.log('PATH 010FA2',r.path010FA2.join(' -> '));console.table(r.uses);}
const local=results.filter(r=>{const a=parseInt(r.at,16);return a>=0x010B00&&a<=0x011100;});
const strong=results.filter(r=>r.indexed&&(r.reaches010F48||r.reaches010FA2));
const verdict={tableBase:h(TABLE),tableValid:table.every(x=>x.match),xrefCount:results.length,localXrefCount:local.length,indexedXrefs:results.filter(x=>x.indexed).length,reaches010F48:results.filter(x=>x.reaches010F48).length,reaches010FA2:results.filter(x=>x.reaches010FA2).length,strongTableToEdge:strong.length,topAt:(strong[0]||local[0]||results[0])?.at||'',topText:(strong[0]||local[0]||results[0])?.text||'',topDst:(strong[0]||local[0]||results[0])?.dst||''};
console.log('=== 010CF8 TABLE→EDGE VERDICT ===');console.table([verdict]);
const out={version:'wof-player-table-010cf8-trace-v1',verdict,table,xrefs:results};self.__WOF_PLAYER_TABLE_010CF8_TRACE=out;return out;
})().catch(e=>{console.error('WOF_PLAYER_TABLE_010CF8_TRACE_ERROR',e);throw e;});