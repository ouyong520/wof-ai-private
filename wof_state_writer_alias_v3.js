(async()=>{
'use strict';
const SRC='https://raw.githubusercontent.com/ouyong520/wof-ai-private/e91b751bfc45e00f115fa27049837c7227f01bce/wof_state_writer_alias_v2.js';
let s=await fetch(SRC+'?x='+Date.now(),{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error('fetch v2 failed '+r.status);return r.text();});
const bad="const x=(w>>9)&7,y=w&7,[n[x],n[y]]=[a[y],a[x]];return n;";
const good="const rx=(w>>9)&7,ry=w&7;n[rx]=a[ry];n[ry]=a[rx];return n;";
if(!s.includes(bad))throw new Error('v2 patch target not found');
s=s.replace(bad,good);
new Function(s);
(0,eval)(s);
if(!self.WOFSTATEALIAS?.run)throw new Error('WOFSTATEALIAS did not load');
console.log('✅ state writer alias v3 syntax patch loaded');
await self.WOFSTATEALIAS.run();
})();