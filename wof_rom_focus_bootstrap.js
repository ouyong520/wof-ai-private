(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/';
const FOCUS='4e6f32865302d2ed390f129b5c66123fdf5f04d0/wof_rom_focus_probe.js';
const DEEP='5e0fa97eebccea900fd36ee81be6c1d44b6abb1c/wof_rom_focus_deep.js';
const load=async path=>{const r=await fetch(RAW+path+'?x='+Math.random());if(!r.ok)throw new Error('fetch failed '+r.status+' '+path);const s=await r.text();(0,eval)(s);};
try{
  console.log('🚀 WOF ROM focus bootstrap started');
  if(!self.WOFFOCUSROM||!self.WOFFOCUSROM.located){
    await load(FOCUS);
    console.log('1/4 focus probe loaded');
  }else console.log('1/4 reuse existing WOFFOCUSROM');
  if(!self.WOFFOCUSROM.located){
    const loc=await self.WOFFOCUSROM.locate();
    if(!loc)throw new Error('ROM locate failed');
  }
  console.log('2/4 ROM located');
  const base=await self.WOFFOCUSROM.result();
  if(!base?.helpers)throw new Error('focus result failed');
  console.log('3/4 player refs/common helpers ready');
  await load(DEEP);
  if(!self.WOFFOCUSDEEP?.run)throw new Error('deep module unavailable');
  const out=await self.WOFFOCUSDEEP.run();
  console.log('4/4 ✅ TARGET SELECTOR analysis complete');
  if(out?.strong?.length){
    console.log('🎯 strongest candidates');
    console.table(out.strong.slice(0,20));
  }else if(out?.top?.length){
    console.log('⚠️ no strict strong signature; showing top candidates');
    console.table(out.top.slice(0,20));
  }
  self.__WOF_ROM_FOCUS_BOOTSTRAP=out;
  return out;
}catch(e){
  console.error('❌ WOF ROM focus bootstrap failed',e);
  throw e;
}
})();