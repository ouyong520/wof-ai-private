(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return (0,eval)(await r.text());};
if(!self.__WOF_DISPATCH_EDGE_SELECTOR){await load('wof_resume_dispatch_selector.js');}
const S=self.__WOF_DISPATCH_EDGE_SELECTOR;
if(!S)throw new Error('dispatch edge selector missing');
const C=self.__WOF_ROM_LOC_CACHE,MOD=_0x515056,M=MOD.HEAPU8,base=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-base);
const r8=o=>M[base+(SW?(o^1):o)]>>>0;
const r16=o=>((r8(o)<<8)|r8(o+1))>>>0;
const r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
const s8=v=>v&0x80?v-0x100:v;
const s16=v=>v&0x8000?v-0x10000:v;
const h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0');
const hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
function eaWords(m,r,size){if(m<=4)return 0;if(m===5||m===6)return 1;if(m===7){if(r===0||r===2||r===3)return 1;if(r===1)return 2;if(r===4)return size==='L'?2:1;}return 0;}
function ctl(p){
  const w=r16(p),g=w>>>12,m=(w>>3)&7,r=w&7;
  if(g===6){const cc=(w>>8)&15,d=w&255,len=d===0?4:2,disp=d===0?s16(r16(p+2)):s8(d),target=(p+2+disp)>>>0;return{at:h(p),word:hw(w),kind:cc===0?'BRA':cc===1?'BSR':'BCC'+cc,len,target:h(target),ext:d===0?hw(r16(p+2)):''};}
  if((w&0xFFC0)===0x4E80||(w&0xFFC0)===0x4EC0){let target=null;const len=2+eaWords(m,r,'L')*2,kind=(w&0xFFC0)===0x4E80?'JSR':'JMP';if(m===7&&r===0)target=s16(r16(p+2))>>>0;else if(m===7&&r===1)target=r32(p+2);else if(m===7&&r===2)target=(p+2+s16(r16(p+2)))>>>0;return{at:h(p),word:hw(w),kind,len,target:target==null?'INDIRECT':h(target),ext:len>2?hw(r16(p+2)):''};}
  return{at:h(p),word:hw(w),kind:'NOT_CONTROL',len:2,target:'',ext:''};
}
const interesting=(S.rows||[]).filter(r=>r.cmp>0||(r.d0Root&&!String(r.d0Root).startsWith('#')));
const rows=[];
for(const r of interesting){
  const at=parseInt(r.at,16),d=ctl(at),claimed=String(r.target||'').toUpperCase(),actual=String(d.target||'').toUpperCase();
  rows.push({at:r.at,claimedTarget:r.target||'',claimedKind:r.kind||'',word:d.word,actualKind:d.kind,actualTarget:d.target,match:claimed===actual&&actual!=='',cmp:r.cmp,d0Root:r.d0Root||'',d0RootAt:r.d0RootAt||''});
}
console.log('=== FRONTIER EDGE STRICT VALIDATION ===');
console.table(rows);
for(const r of rows){
  const at=parseInt(r.at,16),raw=[];
  for(let p=Math.max(0,at-12)&~1;p<=Math.min(MAX-2,at+12);p+=2)raw.push({at:h(p),word:hw(r16(p)),mark:p===at?'<<< CLAIMED EDGE':''});
  console.log('=== RAW AROUND '+r.at+' ===');console.table(raw);
}
const good=rows.filter(r=>r.match),bad=rows.filter(r=>!r.match);
const verdict={interestingEdges:rows.length,strictValid:good.length,strictInvalid:bad.length,validAts:good.map(x=>x.at).join(' '),invalidAts:bad.map(x=>x.at).join(' ')};
console.log('=== FRONTIER VALIDATION VERDICT ===');console.table([verdict]);
console.log('=== FRONTIER VALIDATION JSON ===');console.log(JSON.stringify({verdict,rows},null,2));
if(bad.length)console.warn('⚠️ claimed dispatcher edge 与该地址当前真实 control target 不一致：这些 edge 不能继续作为 selector 主线，必须先从已知 dispatcher 入口按真实指令边界重建 incoming CFG。');
else console.log('✅ 当前 interesting edges 的 claimed target 与真实 opcode target 一致，可继续向上追。');
const out={version:'wof-dispatch-frontier-validate-v1',verdict,rows};self.__WOF_DISPATCH_FRONTIER_VALIDATION=out;return out;
})().catch(e=>{console.error('WOF_FRONTIER_VALIDATE_ERROR',e);throw e;});
