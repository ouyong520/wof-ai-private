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
const PLAYERS=[{id:'P1',a:0xFFBE1C},{id:'P2',a:0xFFBEFC},{id:'P3',a:0xFFBFDC}];
function eaWords(m,r,size){if(m<=4)return 0;if(m===5||m===6)return 1;if(m===7){if(r===0||r===2||r===3)return 1;if(r===1)return 2;if(r===4)return size==='L'?2:1;}return 0;}
function ea(p,m,r,size,ext=p+2){
 if(m===0)return{text:'D'+r,reg:'D'+r};
 if(m===1)return{text:'A'+r,reg:'A'+r};
 if(m===2)return{text:'(A'+r+')',base:'A'+r};
 if(m===3)return{text:'(A'+r+')+',base:'A'+r};
 if(m===4)return{text:'-(A'+r+')',base:'A'+r};
 if(m===5){const d=s16(r16(ext));return{text:d+'(A'+r+')',base:'A'+r,disp:d};}
 if(m===6){const x=r16(ext),d=s8(x&255),ir=(x&0x8000?'A':'D')+((x>>12)&7);return{text:d+'(A'+r+','+ir+(x&0x0800?'.L':'.W')+')',base:'A'+r,index:ir,disp:d,ext:hw(x)};}
 if(m===7&&r===0){const v=s16(r16(ext))&0xFFFFFF;return{text:h(v)+'.W',abs:v};}
 if(m===7&&r===1){const v=r32(ext)&0xFFFFFF;return{text:h(v)+'.L',abs:v};}
 if(m===7&&r===2){const d=s16(r16(ext)),t=(p+2+d)>>>0;return{text:d+'(PC)->'+h(t),pc:t};}
 if(m===7&&r===3){const x=r16(ext),d=s8(x&255),ir=(x&0x8000?'A':'D')+((x>>12)&7),t=(p+2+d)>>>0;return{text:d+'(PC,'+ir+(x&0x0800?'.L':'.W')+')->'+h(t),index:ir,pc:t,ext:hw(x)};}
 if(m===7&&r===4){const v=size==='L'?r32(ext):(size==='B'?r16(ext)&255:r16(ext));return{text:'#'+(size==='L'?h(v):hw(v)),imm:v};}
 return{text:'EA('+m+','+r+')'};
}
function decode(p){
 if(p<0||p+1>=MAX)return null;
 const w=r16(p),g=w>>>12,m=(w>>3)&7,r=w&7;let len=2,kind='OP',target=null,fall=true,terminal=false,call=false;
 if(w===0x4E75||w===0x4E73||w===0x4E77){kind='RET';terminal=true;fall=false;}
 else if(w===0x4E72){kind='STOP';len=4;terminal=true;fall=false;}
 else if((w&0xFFC0)===0x4E80){kind='JSR';call=true;len=2+eaWords(m,r,'L')*2;if(m===7&&r===0)target=s16(r16(p+2))&0xFFFFFF;else if(m===7&&r===1)target=r32(p+2)&0xFFFFFF;else if(m===7&&r===2)target=(p+2+s16(r16(p+2)))>>>0;}
 else if((w&0xFFC0)===0x4EC0){kind='JMP';fall=false;len=2+eaWords(m,r,'L')*2;if(m===7&&r===0)target=s16(r16(p+2))&0xFFFFFF;else if(m===7&&r===1)target=r32(p+2)&0xFFFFFF;else if(m===7&&r===2)target=(p+2+s16(r16(p+2)))>>>0;}
 else if(g===6){const cc=(w>>8)&15,d=w&255;len=d===0?4:2;target=(p+2+(d===0?s16(r16(p+2)):s8(d)))>>>0;kind=cc===0?'BRA':cc===1?'BSR':'BCC';if(cc===0)fall=false;if(cc===1)call=true;}
 else if(g===1||g===2||g===3){const size=g===1?'B':g===2?'L':'W',sm=(w>>3)&7,sr=w&7,dm=(w>>6)&7,dr=(w>>9)&7;len=2+(eaWords(sm,sr,size)+eaWords(dm,dr,size))*2;}
 else if(g===5){const sz=(w>>6)&3;if(sz===3&&m===1){kind='DBCC';len=4;target=(p+2+s16(r16(p+2)))>>>0;}else len=2+eaWords(m,r,sz===2?'L':sz===1?'W':'B')*2;}
 else if(g===0){if([0x003C,0x007C,0x023C,0x027C,0x0A3C,0x0A7C].includes(w))len=4;else if((w&0xF138)===0x0108)len=4;else if((w&0xFF00)===0x0800)len=4+eaWords(m,r,'B')*2;else if((w&0xF100)===0x0100)len=2+eaWords(m,r,'B')*2;else{const op=(w>>8)&15,sz=(w>>6)&3;if([0,2,4,6,10,12].includes(op)&&sz!==3){const s=sz===2?'L':sz===1?'W':'B';len=2+(s==='L'?4:2)+eaWords(m,r,s)*2;}}}
 else if(g===4){if((w&0xFFF8)===0x4E50)len=4;else if((w&0xFB80)===0x4880&&m>=2)len=4+eaWords(m,r,(w&0x40)?'L':'W')*2;else if((w&0xF1C0)===0x41C0)len=2+eaWords(m,r,'L')*2;else if((w&0xFFC0)===0x4840&&m!==0)len=2+eaWords(m,r,'L')*2;else len=2+eaWords(m,r,((w>>6)&3)===2?'L':'W')*2;}
 else if(g===8){if((w&0xF1F0)!==0x8100)len=2+eaWords(m,r,((w>>6)&3)===2?'L':'W')*2;}
 else if(g===9||g===13){const special=(w&0xF130)===(g===9?0x9100:0xD100),a=((w>>6)&7)===3||((w>>6)&7)===7;if(!special)len=2+eaWords(m,r,a?(((w>>6)&1)?'L':'W'):(((w>>6)&3)===2?'L':'W'))*2;}
 else if(g===11){const cmpm=(w&0xF138)===0xB108,a=((w>>6)&7)===3||((w>>6)&7)===7;if(!cmpm)len=2+eaWords(m,r,a?(((w>>6)&1)?'L':'W'):(((w>>6)&3)===2?'L':'W'))*2;}
 else if(g===12){const exg=(w&0xF1F8)===0xC140||(w&0xF1F8)===0xC148||(w&0xF1F8)===0xC188,abcd=(w&0xF1F0)===0xC100;if(!exg&&!abcd)len=2+eaWords(m,r,((w>>6)&3)===2?'L':'W')*2;}
 else if(g===14&&((w>>6)&3)===3)len=2+eaWords(m,r,'W')*2;
 else if(g===10||g===15){kind='LINE';terminal=true;fall=false;}
 len=Math.max(2,len);const next=p+len;if(target!=null&&(target<0||target>=MAX))target=null;return{at:p,w,len,next,kind,target,fall,terminal,call};
}
function playerTag(v){if(v==null)return'';v&=0xFFFFFF;const x=PLAYERS.find(p=>p.a===v);return x?x.id:'';}
function writerA5(p){
 const w=r16(p),g=w>>>12,m=(w>>3)&7,r=w&7;
 if(g===2||g===3){const size=g===2?'L':'W',sm=(w>>3)&7,sr=w&7,dm=(w>>6)&7,dr=(w>>9)&7;if(dm===1&&dr===5){const z=ea(p,sm,sr,size);return{kind:'MOVEA.'+size,source:z.text,sourceReg:z.reg||z.base||'',abs:z.abs??null,imm:z.imm??null,disp:z.disp??null};}}
 if((w&0xF1C0)===0x41C0&&((w>>9)&7)===5){const z=ea(p,m,r,'L');return{kind:'LEA',source:z.text,sourceReg:z.reg||z.base||'',abs:z.abs??null,imm:null,disp:z.disp??null};}
 if((g===9||g===13)&&((w>>9)&7)===5){const opm=(w>>6)&7;if(opm===3||opm===7){const size=opm===7?'L':'W',z=ea(p,m,r,size);return{kind:(g===13?'ADDA.':'SUBA.')+size,source:z.text,sourceReg:z.reg||z.base||'',abs:z.abs??null,imm:z.imm??null,disp:z.disp??null};}}
 if(g===5&&m===1&&r===5&&((w>>6)&3)!==3){const q=((w>>9)&7)||8;return{kind:(w&0x0100?'SUBQ':'ADDQ')+'.A5',source:'#'+q,sourceReg:'A5',abs:null,imm:q,disp:null};}
 if((w&0xF1F8)===0xC148){const x=(w>>9)&7,y=w&7;if(x===5||y===5)return{kind:'EXG.A',source:'A'+(x===5?y:x),sourceReg:'A'+(x===5?y:x),abs:null,imm:null,disp:null};}
 if((w&0xF1F8)===0xC188){const d=(w>>9)&7,a=w&7;if(a===5)return{kind:'EXG.DA',source:'D'+d,sourceReg:'D'+d,abs:null,imm:null,disp:null};}
 if((w&0xFB80)===0x4880&&(w&0x0400)){const mask=r16(p+2);if(mask&(1<<(8+5)))return{kind:'MOVEM->A5',source:'memory',sourceReg:m>=2&&m<=6?'A'+r:'',abs:null,imm:null,disp:m===5?s16(r16(p+4)):null};}
 if((w&0xFFF8)===0x4E50&&(w&7)===5)return{kind:'LINK A5',source:'A7',sourceReg:'A7',abs:null,imm:s16(r16(p+2)),disp:null};
 return null;
}
function evidence(p,d,wri){
 let player='',stride=0,ramHi=0;const vals=[];
 if(wri){player=playerTag(wri.abs)||playerTag(wri.imm);if(wri.imm===0xE0||wri.disp===0xE0||wri.disp===-0xE0)stride++;}
 for(let q=p;q<Math.min(d.next,MAX-1);q+=2){const v=r16(q);vals.push(hw(v));if(v===0x00E0)stride++;if(v===0xFFBE||v===0xFFBF)ramHi++;}
 return{player,stride,ramHi,words:vals.join(' ')};
}
function prevFall(cur,lo){const out=[];for(let p=Math.max(lo,cur-10)&~1;p<cur;p+=2){const d=decode(p);if(d&&d.fall&&d.next===cur)out.push(d);}return out;}
function controlMap(lo,hi){const m=new Map();for(let p=lo&~1;p<hi-6;p+=2){const d=decode(p);if(!d||d.target==null)continue;if(!['BRA','BCC','JMP','DBCC'].includes(d.kind))continue;if(d.target<lo||d.target>hi)continue;let a=m.get(d.target);if(!a){a=[];m.set(d.target,a);}a.push(d);}return m;}
function helperA5(start,cache){start&=~1;if(cache.has(start))return cache.get(start);const hi=Math.min(MAX,start+0x600),q=[start],seen=new Set(),hits=[];while(q.length&&seen.size<500){const p=q.shift();if(p<start||p>=hi||(p&1)||seen.has(p))continue;seen.add(p);const d=decode(p);if(!d)continue;const w=writerA5(p);if(w){const ev=evidence(p,d,w);hits.push({at:h(p),kind:w.kind,source:w.source,sourceReg:w.sourceReg,player:ev.player,stride:ev.stride,ramHi:ev.ramHi});}if(d.kind==='BRA'){if(d.target!=null&&d.target>=start&&d.target<hi)q.push(d.target&~1);continue;}if(d.kind==='BCC'||d.kind==='DBCC'){if(d.next<hi)q.push(d.next);if(d.target!=null&&d.target>=start&&d.target<hi)q.push(d.target&~1);continue;}if(d.kind==='JMP'){if(d.target!=null&&d.target>=start&&d.target<hi)q.push(d.target&~1);continue;}if(d.terminal)continue;if(d.next<hi)q.push(d.next);}const z={start:h(start),instructions:seen.size,hits};cache.set(start,z);return z;}
const CMP=0x0111B4,LO=Math.max(0,CMP-0x5000),CTRL=controlMap(LO,CMP+2),helperCache=new Map();
const q=[{cur:CMP,steps:0,anchors:0,path:[h(CMP)]}],seen=new Set(),writers=[],helperWrites=[],dead=[];let qi=0,states=0;
while(qi<q.length&&states<16000){const s=q[qi++];states++;if(s.steps>=180||s.cur<=LO){dead.push({at:h(s.cur),steps:s.steps,path:s.path.join(' <- ')});continue;}const preds=[];for(const d of prevFall(s.cur,LO))preds.push({d,ctl:false});for(const d of CTRL.get(s.cur)||[])preds.push({d,ctl:true});if(!preds.length){dead.push({at:h(s.cur),steps:s.steps,path:s.path.join(' <- ')});continue;}for(const x of preds){const d=x.d,np=[h(d.at),...s.path].slice(-24);const wri=writerA5(d.at);if(wri){const ev=evidence(d.at,d,wri),score=(ev.player?2000:0)+(ev.stride?700:0)+(ev.ramHi?300:0)+(wri.sourceReg?120:0)+Math.max(0,400-(CMP-d.at)/8)+s.anchors*20;writers.push({at:h(d.at),word:hw(d.w),kind:wri.kind,source:wri.source,sourceReg:wri.sourceReg||'',player:ev.player,stride:ev.stride,ramHi:ev.ramHi,distance:CMP-d.at,steps:s.steps+1,anchors:s.anchors+(x.ctl?1:0),score,path:np.join(' <- ')});continue;}
 if(d.call&&d.target!=null&&d.target!==0x25B6&&d.target!==0x25C8){const he=helperA5(d.target,helperCache);if(he.hits.length){for(const z of he.hits)helperWrites.push({callAt:h(d.at),helper:h(d.target),helperWriteAt:z.at,kind:z.kind,source:z.source,sourceReg:z.sourceReg,player:z.player,stride:z.stride,ramHi:z.ramHi,path:np.join(' <- ')});}}
 const key=d.at+'|'+s.cur+'|'+Math.min(s.anchors+(x.ctl?1:0),4);if(seen.has(key))continue;seen.add(key);q.push({cur:d.at,steps:s.steps+1,anchors:s.anchors+(x.ctl?1:0),path:np});}}
const uniq=[];const sig=new Set();for(const r of writers.sort((a,b)=>b.score-a.score||a.distance-b.distance)){const k=r.at+'|'+r.kind+'|'+r.source;if(sig.has(k))continue;sig.add(k);uniq.push(r);}
const hu=[];const hs=new Set();for(const r of helperWrites){const k=r.callAt+'|'+r.helper+'|'+r.helperWriteAt;if(hs.has(k))continue;hs.add(k);hu.push(r);}
const cmpWord=hw(r16(CMP));const cmpExt=hw(r16(CMP+2));const top=uniq[0]||null;
const verdict={cmpAt:h(CMP),cmpWord,cmpExt,cmpExpected:'CMP.B 422(A5),D0',reverseStates:states,a5Writers:uniq.length,helperA5Writers:hu.length,playerDirect:uniq.filter(x=>x.player).length,playerViaHelper:hu.filter(x=>x.player).length,strideEvidence:uniq.filter(x=>x.stride).length+hu.filter(x=>x.stride).length,deadEnds:dead.length,topA5At:top?.at||'',topA5Kind:top?.kind||'',topA5Source:top?.source||'',topA5SourceReg:top?.sourceReg||'',topPlayer:top?.player||'',topPath:top?.path||''};
const out={version:'wof-dispatch-111b4-a5-provenance-v1',verdict,writers:uniq.slice(0,32),helperWrites:hu.slice(0,24),deadEnds:dead.slice(0,16)};self.__WOF_111B4_A5_PROVENANCE=out;
console.log('=== 111B4 A5 PROVENANCE VERDICT ===');console.table([verdict]);
console.log('=== A5 DIRECT WRITERS ===');console.table(out.writers);
if(out.helperWrites.length){console.log('=== A5 HELPER-SIDE-EFFECT WRITERS ===');console.table(out.helperWrites);}
console.log('=== 111B4 A5 PROVENANCE JSON ===');console.log(JSON.stringify(out,null,2));
return out;
})().catch(e=>{console.error('WOF_111B4_A5_PROVENANCE_ERROR',e);throw e;});
