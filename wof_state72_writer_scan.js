(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return (0,eval)(await r.text());};
if(!self.__WOF_ROM_LOC_CACHE){await load('wof_rom_focus_inspect.js');for(let i=0;i<300&&!self.__WOF_ROM_LOC_CACHE;i++)await sleep(50);}
if(!self.__WOF_ROM_FOCUS_LEVEL2?.handlers?.length){await load('wof_rom_focus_level2_tables.js');await WOFFOCUSLEVEL2.run();}
if(!self.__WOF_STATE72?.verdict?.locked){console.warn('STATE72 locked result missing; using proven +0x72 stateIndex field from dispatcher trace.');}
const oldLock=self.__WOF_STATE_DISPATCH_LOCK;
self.__WOF_STATE_DISPATCH_LOCK={verdict:{field:'0x72',kind:'byte',fieldEncoding:'field-is-stateIndex'},mappings:(self.__WOF_STATE72?.mappings||[])};
const SRC='https://raw.githubusercontent.com/ouyong520/wof-ai-private/e91b751bfc45e00f115fa27049837c7227f01bce/wof_state_writer_alias_v2.js?x='+Date.now();
let s=await fetch(SRC,{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error('fetch alias v2 failed '+r.status);return r.text();});
s=s.replace("const x=(w>>9)&7,y=w&7,[n[x],n[y]]=[a[y],a[x]];return n;","const x=(w>>9)&7,y=w&7;const tmp=n[x];n[x]=a[y];n[y]=tmp;return n;");
s=s.replace("if(eff===FIELD){const im=typeof wr.imm==='number'?wr.imm:null;hits.push({at:p,seedReg:'A'+seed,eff,kind:wr.kind,baseReg:'A'+wr.areg,srcReg:wr.srcReg||'',imm:im,matchObserved:im!=null&&observed.has(im)});}","const width=wr.kind.includes('.L')?4:wr.kind.includes('.W')?2:1;if(eff<=FIELD&&FIELD<eff+width){const im=typeof wr.imm==='number'?wr.imm:null;hits.push({at:p,seedReg:'A'+seed,eff,kind:wr.kind,baseReg:'A'+wr.areg,srcReg:wr.srcReg||'',imm:im,matchObserved:im!=null&&observed.has(im),overlapStart:eff,width});}");
s=s.replaceAll('stateIndex alias writer scan v2','STATE72 true-state writer scan');
s=s.replaceAll('=== STATE ALIAS WRITER VERDICT ===','=== STATE72 WRITER VERDICT ===');
s=s.replace("console.log('FIELD',S.verdict.field,'KIND',KIND,'observed',[...observed].sort((a,b)=>a-b));","console.log('LOCKED TRUE FIELD +0x72 | KIND byte | observed states',[...observed].sort((a,b)=>a-b));");
new Function(s);
console.log('✅ WOF TRUE stateIndex +0x72 writer scanner loaded');
(0,eval)(s);
const out=await WOFSTATEALIAS.run();
self.__WOF_STATE72_WRITER=out;
if(oldLock)self.__WOF_STATE_DISPATCH_LOCK=oldLock;
else delete self.__WOF_STATE_DISPATCH_LOCK;
console.log('=== TRUE STATE72 WRITER SUMMARY ===');
const v=out?.verdict||{};console.table([{field:'+0x72',reachableRoutines:v.reachableRoutines??'',aliasWriteSites:v.aliasWriteSites??0,observedAliasWrites:v.observedAliasWrites??0,topAt:v.topAt||'',topRoutine:v.topRoutine||'',topSeedReg:v.topSeedReg||'',topBaseReg:v.topBaseReg||'',topKind:v.topKind||'',topSrcReg:v.topSrcReg||'',topImm:v.topImm||'',topMatchesObserved:v.topMatchesObserved??false}]);
})();