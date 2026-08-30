(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return (0,eval)(await r.text());};
console.log('♻️ WOF resume: dispatcher selector frontier');
if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}
if(!self.__WOF_DISPATCH_EDGE_SELECTOR){await load('wof_dispatch_edge_selector_scan.js');await WOFDISPEDGE.run();}
const x=self.__WOF_DISPATCH_EDGE_SELECTOR;
if(!x)throw new Error('edge selector result missing after resume');
const interesting=(x.rows||[]).filter(r=>r.cmp>0||(r.d0Root&&!String(r.d0Root).startsWith('#')));
console.log('=== RESUME FRONTIER VERDICT ===');
console.table([x.verdict]);
console.log('=== ONLY INTERESTING EDGES ===');
console.table(interesting);
console.log('NEXT: inspect only these 1–2 edges; do not rescan the 44 edges or revive 0x0080F2.');
self.__WOF_RESUME_FRONTIER={version:'wof-resume-dispatch-selector-v1',verdict:x.verdict,interesting};
return self.__WOF_RESUME_FRONTIER;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});
