(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
console.log('♻️ WOF resume: branch-aware Future Danger frontier');
if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}
if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
 version:'wof-resume-dispatch-selector-v28',
 selectorSolved:true,
 selectorField:'enemy+0x7E',
 playerIndexValues:'P1=0 / P2=4 / P3=8',
 selectedPointerCacheCorrection:'enemy+0x6A is supporting selected-player cache only when BE1C/BEFC/BFDC; +0x7E is authoritative target identity.',
 d0Provenance:'0x006A62 MOVEQ #20,D0 -> JSR 0x25C8; 0x25C8 selects type descriptor and 0x247C consumes it.',
 activeAttackField:'enemy+0x70 U16; active start = 0 -> nonzero.',
 xyFields:'object +4/+8 are confirmed X/Y 16.16 fixed-point. Z is still not confirmed.',
 v16Totals:'V16 captured27 D0=20 episodes,19 active,7 horizonComplete,7 timing signals,222 global +0x70 active edges and58 edges for seeded type envelopes.',
 v16TimingCorrection:'T30 ENTRY<=500 is no longer a low-false-positive DANGER_SOON rule: fresh V16 had4 evaluable signals with2 hits (61/481ms) and2 complete misses, precision0.5. Remove T30 from live <=500 warning; keep T30 as ATTACK_READY plus branch-learning only.',
 v16StableTiming:'T9 had1 fresh evaluable hit at241ms plus1 censored end-of-capture; T10 had1 fresh hit at402ms. Keep T9/T10 <=500. T13, T21 and T33 had no fresh exposure in V16, so their prior rules remain provisional/observed rather than newly validated.',
 v16Geometry:'V15 type-level P90 envelopes prospectively generalized unevenly: T9 11/11 ACTIVE edges inside (1.0), T30 31/40 (0.775), T10 3/7 (0.429). Therefore type-only rectangles are not production-safe for T10/T30; move to attack-specific and entry-branch-specific geometry.',
 v16Retarget:'V16 observed1 target retarget. Continue live +0x7E every tick; never freeze target/side at warning entry.',
 liveExpiryCorrection:'Earlier live shadows could leave DANGER_SOON/IMMINENT state stale beyond its nominal horizon until ACTIVE/episode finish. V17 explicitly expires unresolved horizon warnings and downgrades back to ATTACK_READY.',
 geometryFrontier:'Use V15 attack-specific ACTIVE clusters as fresh-room priors only. V17 validates common type+attack envelopes and groups D0 entry signatures (type/state99/action2A/b2B/body plus descriptor identity) against active probability, horizon, eventual attack id and geometry.',
 timingRules:'Current live warnings: T13 ENTRY<=250 provisional-high; T9/T10/T33 ENTRY<=500; T21 EXIT<=250 provisional. T30 fixed <=500 removed after V16 2/4 fresh precision. T18/T24 remain branch-variable.',
 futureDangerInterpretation:'The next bottleneck is branch discrimination, not more global type timing. Learn which pre-active state/body/descriptor signatures imply which attack family and distance envelope, then use those signatures for lower-FP danger rectangles and Safe Path scoring.',
 endToEndStructuralProofConfirmed:true,
 causalFrontier:'Run V17 branch-aware geometry calibrator. Promote only signatures and attack envelopes that repeat across rooms. Do not treat type-level P90 rectangles or +0x70 ACTIVE distance as exact hitboxes.',
 nextScript:'wof_future_danger_branch_geometry_v17.js',
 nextMarker:'=== FUTURE DANGER BRANCH GEOMETRY V17 JSON ===',
 note:'Do not restart selector search, Focus Multiroom, 44-edge scan, 0x0080F2, 0x11C26 bridge, universal-next1 search, universal timer assumptions, exact-start-timer gating, T30 <=500 hard warning, or type-only geometry for T10/T30.'
};
self.__WOF_RESUME_FRONTIER=current;
console.log('=== CURRENT SELECTOR FRONTIER ===');
console.table([current]);
console.log('NEXT: run V17 branch-aware timing/geometry calibrator with horizon expiry.');
return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});