(()=>{
'use strict';
try{self.WOFCPUCAP?.stop?.();}catch(_){}
function safeKeys(o){try{return Object.getOwnPropertyNames(o||{});}catch(_){return[];}}
function desc(o,k){try{return Object.getOwnPropertyDescriptor(o,k)||{};}catch(_){return{};}}
function typ(o,k){try{return typeof o[k];}catch(_){return'getter-throw';}}
function src(o,k){try{const v=o[k];if(typeof v!=='function')return'';return Function.prototype.toString.call(v).slice(0,500);}catch(_){return'';}}
function run(){
 const MOD=self._0x515056||self.Module||null;
 if(!MOD)throw new Error('emulator Module not found');
 const re=/(m68|68k|sek|musashi|cpu|\bpc\b|programcounter|register|\breg\b|break|debug|trace|watch|hook|memory|memwrite|write8|write16|write32)/i;
 const exact=/(^|_)(m68k|sek|cpu|pc|reg|break|debug|trace|watch|hook)/i;
 const rows=[];
 for(const k of safeKeys(MOD)){
   if(!re.test(k))continue;
   rows.push({scope:'Module',name:k,type:typ(MOD,k),semantic:exact.test(k),preview:src(MOD,k).replace(/\s+/g,' ').slice(0,180)});
 }
 const globals=[];
 for(const k of safeKeys(self)){
   if(!re.test(k))continue;
   if(['performance','onbeforematch','onpointercancel','onpointercapture','onpointerdown','onpointerenter','onpointerleave','onpointermove','onpointerout','onpointerover','onpointerrawupdate','onpointerup'].includes(k))continue;
   globals.push({scope:'global',name:k,type:typ(self,k),semantic:exact.test(k),preview:src(self,k).replace(/\s+/g,' ').slice(0,180)});
 }
 const containers=[];
 for(const k of ['asm','wasmExports','exports','instance','wasmInstance']){
   let o=null;try{o=MOD[k];}catch(_){}
   if(!o)continue;
   const keys=safeKeys(o),hits=keys.filter(x=>re.test(x));
   containers.push({container:k,totalKeys:keys.length,semanticHits:hits.length,hitNames:hits.slice(0,40).join(',')});
   for(const x of hits.slice(0,80))rows.push({scope:'Module.'+k,name:x,type:typ(o,x),semantic:exact.test(x),preview:src(o,x).replace(/\s+/g,' ').slice(0,180)});
 }
 rows.sort((a,b)=>(b.semantic-a.semantic)||a.scope.localeCompare(b.scope)||a.name.localeCompare(b.name));
 globals.sort((a,b)=>(b.semantic-a.semantic)||a.name.localeCompare(b.name));
 console.log('=== MODULE CPU-LIKE EXPORTS ===');console.table(rows.slice(0,120));
 console.log('=== GLOBAL CPU-LIKE SYMBOLS ===');console.table(globals.slice(0,120));
 console.log('=== WASM/ASM CONTAINERS ===');console.table(containers);
 const known=['_m68k_get_reg','m68k_get_reg','_m68k_set_reg','m68k_set_reg','_m68k_get_pc','m68k_get_pc','_SekGetPC','SekGetPC','_SekDbgGetRegister','SekDbgGetRegister','_sek_get_pc','sek_get_pc'];
 const knownRows=[];
 for(const n of known){
   let where='',type='';
   if(n in MOD){where='Module';type=typ(MOD,n);}else if(n in self){where='global';type=typ(self,n);}else for(const c of ['asm','wasmExports','exports']){try{if(MOD[c]&&n in MOD[c]){where='Module.'+c;type=typ(MOD[c],n);break;}}catch(_){}
   knownRows.push({name:n,present:!!where,where,type});
 }
 console.log('=== KNOWN 68K API NAMES ===');console.table(knownRows);
 const verdict={moduleKeys:safeKeys(MOD).length,moduleSemanticHits:rows.filter(x=>x.scope==='Module'&&x.semantic).length,allModuleHits:rows.length,globalSemanticHits:globals.filter(x=>x.semantic).length,knownApiHits:knownRows.filter(x=>x.present).length,hasCcall:typeof MOD.ccall==='function',hasCwrap:typeof MOD.cwrap==='function',hasAsm:!!MOD.asm,hasWasmExports:!!MOD.wasmExports,topModuleNames:rows.slice(0,12).map(x=>x.scope+':'+x.name).join(' | '),topGlobalNames:globals.slice(0,12).map(x=>x.name).join(' | ')};
 console.log('=== RUNTIME CPU CAP VERDICT ===');console.table([verdict]);
 if(verdict.knownApiHits||verdict.moduleSemanticHits)console.log('🎯 发现可疑 68K/CPU API；下一步验证 PC/register 读取，不先做 indexed writer 猜测。');
 else if(verdict.hasCcall||verdict.hasCwrap)console.log('🧭 没有直接导出的 68K 名称，但存在 ccall/cwrap；下一步从 wasm/export table 识别 CPU getter。');
 else console.warn('⚠️ 未发现可直接使用的 CPU/PC API；下一步转 indexed destination / indirect trampoline 静态验证。');
 const out={version:'wof-runtime-cpu-cap-probe-v1',verdict,moduleRows:rows,globalRows:globals,containers,known:knownRows};self.__WOF_CPU_CAP=out;return out;
}
self.WOFCPUCAP={run,stop(){}};console.log('✅ WOF runtime CPU capability probe loaded');console.log('执行 WOFCPUCAP.run()');
})();