(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
console.log('♻️ WOF resume: Future Danger geometry frontier');
if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}
if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
 version:'wof-resume-dispatch-selector-v26',
 selectorSolved:true,
 selectorField:'enemy+0x7E',
 playerIndexValues:'P1=0 / P2=4 / P3=8',
 selectedPointerCacheCorrection:'enemy+0x6A is supporting selected-player cache only when BE1C/BEFC/BFDC; +0x7E is authoritative target identity.',
 d0Provenance:'0x006A62 MOVEQ #20,D0 -> JSR 0x25C8; 0x25C8 selects type descriptor and 0x247C consumes it.',
 activeAttackField:'enemy+0x70 U16; active start = 0 -> nonzero.',
 xyFields:'object +4/+8 are confirmed X/Y 16.16 fixed-point. Z is still not confirmed.',
 v14CaptureValidation:'V14 robust structural entry worked: 20 D0=20 episodes, 17 exact-start captures and 3 late captures, so timer equality is not required for live capture. Diagnostics saw203 D0 samples and225 global +0x70 active edges.',
 v14TypeTiming:'T9 5/5 active with entry leads19/19/339/340/340ms; combined with prior V3 T9 leads219/339/340 gives at least8/8 observed <=500ms. T15 fresh4/4 active178/260/340/463ms, provisional <=500 candidate. T10 fresh420ms adds to prior roughly398/400/419ms evidence, supporting <=500 observed. T18 was weak this room:6 episodes, only1 active at1041ms and4 horizonComplete; T24 also branch-variable:4 episodes, active460/1159ms plus a horizonComplete. D0=20 remains strongly type-conditioned.',
 v14Signals:'No T21/T30/T33 D0 episode occurred in this room, so zero rule signals are absence of exposure, not rule failure. Keep T33/T30 <=500 and T21 EXIT<=250 as prior provisional rules until fresh exposures occur.',
 retargetPolicy:'Keep target live from enemy+0x7E; V14 observed3 retargets. Never freeze warning target.',
 geometryFrontier:'Begin empirical attack geometry. At every +0x70 active edge, sample enemy and live-target X/Y, dx/dy, absDx/absDy, side/lane, type and attack value. For D0 episodes also retain entry geometry and near-active checkpoints. These are target-relative geometry observations, not yet exact hitbox/facing/damage boundaries.',
 futureDangerInterpretation:'Timing layer is usable enough to proceed in parallel. ATTACK_READY is structural D0=20; type-conditioned <=500 evidence is strongest for T9/T10/T33/T30 and provisional T15; T21 EXIT<=250 remains provisional IMMINENT. Next build directional/range envelopes, then 0-1000ms Future Danger Map.',
 endToEndStructuralProofConfirmed:true,
 causalFrontier:'Use V15 to map target-relative geometry at ACTIVE and compare entry->active side stability and distances by enemy type/attack value. Do not infer exact hitboxes until repeated geometry clusters support an envelope.',
 nextScript:'wof_future_danger_geometry_v15.js',
 nextMarker:'=== FUTURE DANGER GEOMETRY V15 JSON ===',
 note:'Do not restart selector search, Focus Multiroom, 44-edge scan, 0x0080F2, 0x11C26 bridge, universal-next1 search, universal timer assumptions, exact-start-timer gating, or treat +0x70 ACTIVE distance as a proven hitbox boundary.'
};
self.__WOF_RESUME_FRONTIER=current;
console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);
console.log('NEXT: build ACTIVE target-relative geometry atlas for direction/range inference.');
return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});