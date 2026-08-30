(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return (0,eval)(await r.text());};
console.log('♻️ WOF resume: current LOW4 frontier');
if(!self.__WOF_ROM_LOC_CACHE){
  await load('wof_resume_dispatch_selector.js');
}
if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache unavailable after resume');
await load('wof_dispatch_low4_chain.js');
if(!self.__WOF_DISPATCH_LOW4_CHAIN)throw new Error('LOW4 result missing');
console.log('=== RESUMED CURRENT FRONTIER ===');
console.log('Current line: D0 low4 -> 0x01AD5A class table -> CMPI.B #8 -> D0=-16 -> 0x25C8');
console.log('Please send === LOW4 CHAIN JSON === only.');
return self.__WOF_DISPATCH_LOW4_CHAIN;
})().catch(e=>{console.error('WOF_RESUME_LOW4_ERROR',e);throw e;});
