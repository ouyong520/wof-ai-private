(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
console.log('♻️ WOF resume: type-conditioned ATTACK_READY; post-D0 Stage2 horizon frontier');
if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}
if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
 version:'wof-resume-dispatch-selector-v21',
 selectorSolved:true,
 selectorField:'enemy+0x7E',
 playerIndexValues:'P1=0 / P2=4 / P3=8',
 selectedPointerCacheCorrection:'enemy+0x6A is supporting selected-player cache only when BE1C/BEFC/BFDC; +0x7E is authoritative target identity.',
 selectedPlayerActionBridgeConfirmed:true,
 strongestBridge:'0x006834 MOVEA.W 106(A0),A1 -> CMPI.B #4,41(A1) -> BEQ 0x006850 -> read enemy+0x2A -> indexed action JMP',
 d0Provenance:'0x006A10 MOVEQ #16,D0 -> JSR 0x25C8; 0x006A62 MOVEQ #20,D0 -> JSR 0x25C8',
 dispatcherSemantic:'0x25C8 selects type-specific action descriptors; 0x247C consumes descriptor stream; frameEnd pointers are data, not code.',
 activeAttackField:'enemy+0x70 U16; active start = 0 -> nonzero.',
 v9Totals:'V9 captured 29 exact D0=20 episodes: 19 active within the 1200ms follow window and 10 horizonComplete misses; no retriggers/slotGone. ENTRY precision was 4/29 <=100ms, 6/29 <=250ms, 13/29 <=500ms, 18/29 <=1000ms. Thus D0=20 is useful ATTACK_READY but not itself a short-horizon IMMINENT rule.',
 v9UniversalTimerFalsified:'Global low-timer thresholds are not universal IMMINENT. LE6 was only2/25 <=100ms and6/25 <=250ms; LE3 was3/25 <=100ms and6/25 <=250ms. T24 is the clearest counterexample: 11 episodes, LE6 and LE3 were0/11 within250ms; D20 exit also0/11 within250ms.',
 v9TypeFindings:'T33 is strong in current sample: D0=20 ENTRY 2/2 active within100ms with leads22/60ms and target correct2/2. T18 requires control conditioning: LE3+S0/A4/B0 was2/2 within250ms with leads20/178ms, but only1/2 within100ms; LE6+S0/A4/B0 likewise2/2 within250ms. T24 needs later post-D0 states rather than D0 timer. T35 sample showed target mismatch on its one active episode, reinforcing live +0x7E retargeting and caution with target-specific prediction for sparse types.',
 retargetPolicy:'Keep target live from enemy+0x7E; do not freeze warning target at D0 entry. +0x6A may be transitional/non-player and is only supporting evidence when valid.',
 futureDangerInterpretation:'Use type-conditioned rules. Promote T33 ENTRY only as a promising provisional IMMINENT candidate until more repetition. For T18 use type+control+timer signatures. For T24 and other poor-timer types, search post-D0 exit structural/control states prospectively. Avoid universal timer or universal next1 rules.',
 endToEndStructuralProofConfirmed:true,
 causalFrontier:'After actual D0=20 exit, capture structural/control/timer state transitions and score P(active<=100/250/500/1000ms) with proper censoring. Rank repeated per-type exact/coarse/control signatures; promote only repeated high-precision short-horizon states.',
 nextScript:'wof_post_d020_horizon_stage2_v10.js',
 nextMarker:'=== POST D0=20 HORIZON STAGE2 V10 JSON ===',
 note:'Do not restart selector search, Focus Multiroom, 44-edge scan, 0x0080F2, 0x11C26 bridge, universal-next1 search, eventual-active scoring, or universal D0 timer threshold assumptions.'
};
self.__WOF_RESUME_FRONTIER=current;
console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);
console.log('NEXT: prospectively calibrate post-D0 exit states, especially T24/T18, for <=100/250ms IMMINENT prediction.');
return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});