(async()=>{
'use strict';
const SRC='https://raw.githubusercontent.com/ouyong520/wof-ai-private/e91b751bfc45e00f115fa27049837c7227f01bce/wof_state_writer_alias_v2.js?x='+Date.now();
let s=await fetch(SRC,{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error('fetch v2 failed '+r.status);return r.text();});
// Fix v2 EXG destructuring syntax bug.
s=s.replace("const x=(w>>9)&7,y=w&7,[n[x],n[y]]=[a[y],a[x]];return n;","const x=(w>>9)&7,y=w&7;const tmp=n[x];n[x]=a[y];n[y]=tmp;return n;");
// Byte state fields may be updated by a W/L store that starts 1-3 bytes earlier.
s=s.replace("if(eff===FIELD){const im=typeof wr.imm==='number'?wr.imm:null;hits.push({at:p,seedReg:'A'+seed,eff,kind:wr.kind,baseReg:'A'+wr.areg,srcReg:wr.srcReg||'',imm:im,matchObserved:im!=null&&observed.has(im)});}","const width=wr.kind.includes('.L')?4:wr.kind.includes('.W')?2:1;if(eff<=FIELD&&FIELD<eff+width){const im=typeof wr.imm==='number'?wr.imm:null;hits.push({at:p,seedReg:'A'+seed,eff,kind:wr.kind,baseReg:'A'+wr.areg,srcReg:wr.srcReg||'',imm:im,matchObserved:im!=null&&observed.has(im),overlapStart:eff,width});}");
s=s.replace("🧬 WOF stateIndex alias writer scan v2","🧬 WOF stateIndex overlap/alias writer scan v4");
s=s.replace("=== STATE ALIAS WRITER VERDICT ===","=== STATE OVERLAP WRITER VERDICT ===");
new Function(s); // syntax check before execution
console.log('✅ WOF state writer overlap v4 loaded');
(0,eval)(s);
await WOFSTATEALIAS.run();
})();