(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
if(!self.__WOF_ROM_LOC_CACHE)await load('wof_resume_dispatch_selector.js');
const C=self.__WOF_ROM_LOC_CACHE;if(!C)throw new Error('ROM cache missing');
const M=_0x515056.HEAPU8,base=C.base,SW=!!C.swap16;
const r8=o=>M[base+(SW?(o^1):o)]>>>0;
const r16=o=>((r8(o)<<8)|r8(o+1))>>>0;
const r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
const s8=v=>v&0x80?v-0x100:v,s16=v=>v&0x8000?v-0x10000:v;
const h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0');
const hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
const LO=0x010E50,HI=0x010FB0,START=0x010E66,TARGETS=new Set([0x010F48,0x010FA2]);
const raw=[];for(let p=LO;p<=HI;p+=2)raw.push({at:h(p),word:hw(r16(p)),mark:p===START?'SELECTOR':TARGETS.has(p)?'DISPATCH':''});
const controls=[];
for(let p=LO;p<=HI-4;p+=2){const w=r16(p),g=w>>>12,m=(w>>3)&7,r=w&7;let kind='',target=null,len=2;
 if(g===6){const cc=(w>>8)&15,d=w&255;len=d===0?4:2;const disp=d===0?s16(r16(p+2)):s8(d);target=(p+2+disp)>>>0;kind=cc===0?'BRA':cc===1?'BSR':'Bcc'+cc;}
 else if((w&0xFFC0)===0x4E80||(w&0xFFC0)===0x4EC0){kind=(w&0xFFC0)===0x4E80?'JSR':'JMP';if(m===7&&r===0){target=s16(r16(p+2))&0xffffff;len=4;}else if(m===7&&r===1){target=r32(p+2)&0xffffff;len=6;}else if(m===7&&r===2){target=(p+2+s16(r16(p+2)))>>>0;len=4;}else if(m===7&&r===3){len=4;}}
 if(kind)controls.push({at:h(p),word:hw(w),kind,len,target:target==null?'':h(target),targetInRange:target!=null&&target>=LO&&target<=HI,targetIsDispatch:target!=null&&TARGETS.has(target)});
}
const selector=[];for(let p=0x010E60;p<=0x010E90;p+=2)selector.push({at:h(p),word:hw(r16(p)),mark:p===0x010E66?'READ +7E':p===0x010E6E?'A1=PLAYER':p===0x010E72?'STORE 1FA':p===0x010E76?'CALL':''});
const dispatch48=[];for(let p=0x010F20;p<=0x010F5A;p+=2)dispatch48.push({at:h(p),word:hw(r16(p)),mark:p===0x010F46?'D0':p===0x010F48?'25C8':''});
const dispatchA2=[];for(let p=0x010F80;p<=0x010FAA;p+=2)dispatchA2.push({at:h(p),word:hw(r16(p)),mark:p===0x010FA0?'D0':p===0x010FA2?'25B6':''});
const verdict={range:h(LO)+'..'+h(HI),selectorAt:h(START),controls:controls.length,inRangeControls:controls.filter(x=>x.targetInRange).length,dispatchTargets:controls.filter(x=>x.targetIsDispatch).length,rawWords:raw.length};
const out={version:'wof-selector-10e66-dispatch-local-raw-v1',verdict,controls,selector,dispatch48,dispatchA2,raw};
self.__WOF_SELECTOR_10E66_DISPATCH_LOCAL_RAW=out;
console.log('=== SELECTOR 10E66 LOCAL BRIDGE VERDICT ===');console.table([verdict]);
console.log('=== LOCAL CONTROL CANDIDATES ===');console.table(controls);
console.log('=== SELECTOR 10E66 LOCAL BRIDGE JSON ===');console.log(JSON.stringify(out,null,2));
return out;
})().catch(e=>{console.error('WOF_SELECTOR_10E66_LOCAL_RAW_ERROR',e);throw e;});