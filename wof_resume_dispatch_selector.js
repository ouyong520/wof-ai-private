(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
console.log('♻️ WOF resume: robust live Future Danger capture frontier');
if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}
if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
 version:'wof-resume-dispatch-selector-v25',
 selectorSolved:true,
 selectorField:'enemy+0x7E',
 playerIndexValues:'P1=0 / P2=4 / P3=8',
 selectedPointerCacheCorrection:'enemy+0x6A is supporting selected-player cache only when BE1C/BEFC/BFDC; +0x7E is authoritative target identity.',
 d0Provenance:'0x006A62 MOVEQ #20,D0 -> JSR 0x25C8; 0x25C8 selects type descriptor and 0x247C consumes it.',
 activeAttackField:'enemy+0x70 U16; active start = 0 -> nonzero.',
 v12TimingFrontier:'T33 and T30 are DANGER_SOON<=500 rather than <=250 hard rules. T21 D0 exit remains provisional IMMINENT<=250. Target stays live from +0x7E.',
 v13ZeroEpisodeDiagnosis:'V13 completed with gates strict/readOnly but episodes=0/events=0. This is not negative prediction evidence. The live entry detector required d20Exact: structural descriptor match plus timer equal to the static start timer on the first sampled frame. At 20ms polling, a real D0=20 entry can first be observed one or more ticks late and then the whole episode is skipped.',
 captureCorrection:'For live prediction, start on structural D0=20 transition (descriptor frameEnd/value30/next match and timer<=static start timer), not timer equality. Preserve exact-vs-late metadata. A later first observation is conservative for remaining-horizon warnings.',
 v14Diagnostics:'V14 also counts enemy samples, structural D0 samples/entries, exact-vs-late entries, bootstrap entries, global +0x70 active edges, and typesSeen so any future zero-episode run can be diagnosed instead of being misread as a model miss.',
 futureDangerInterpretation:'ATTACK_READY=observed structural D0=20. DANGER_SOON<=500=T33/T30 observed D0 entry. IMMINENT<=250=T21 D0 exit provisional. ACTIVE=+0x70 nonzero. Runtime target always live +0x7E.',
 endToEndStructuralProofConfirmed:true,
 causalFrontier:'Validate the robust structural-entry live shadow. If V14 captures episodes normally, use it as the runtime event layer and proceed toward attack direction/range plus 0-1000ms Future Danger map. Do not treat V13 zero episodes as false negatives.',
 nextScript:'wof_future_danger_live_shadow_v14.js',
 nextMarker:'=== FUTURE DANGER LIVE SHADOW V14 JSON ===',
 note:'Do not restart selector search, Focus Multiroom, 44-edge scan, 0x0080F2, 0x11C26 bridge, universal-next1 search, universal D0 timer assumptions, or exact-start-timer as a required live capture gate.'
};
self.__WOF_RESUME_FRONTIER=current;
console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);
console.log('NEXT: run V14 robust structural-entry live Future Danger shadow.');
return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});