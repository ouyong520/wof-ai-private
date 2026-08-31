(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
console.log('♻️ WOF resume: first Future Danger shadow predictor frontier');
if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}
if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
 version:'wof-resume-dispatch-selector-v22',
 selectorSolved:true,
 selectorField:'enemy+0x7E',
 playerIndexValues:'P1=0 / P2=4 / P3=8',
 selectedPointerCacheCorrection:'enemy+0x6A is supporting selected-player cache only when BE1C/BEFC/BFDC; +0x7E is authoritative target identity.',
 selectedPlayerActionBridgeConfirmed:true,
 strongestBridge:'0x006834 MOVEA.W 106(A0),A1 -> CMPI.B #4,41(A1) -> BEQ 0x006850 -> read enemy+0x2A -> indexed action JMP',
 d0Provenance:'0x006A10 MOVEQ #16,D0 -> JSR 0x25C8; 0x006A62 MOVEQ #20,D0 -> JSR 0x25C8',
 dispatcherSemantic:'0x25C8 selects type-specific action descriptors; 0x247C consumes descriptor stream; frameEnd pointers are data, not code.',
 activeAttackField:'enemy+0x70 U16; active start = 0 -> nonzero.',
 v10Totals:'V10 captured 30 exact D0=20 episodes: 22 active, 2 active before D0 exit, 20 active after exit, 4 horizonComplete misses, 4 slotGone/censored. Types observed: T18(9 entries/6 active), T21(6/6 active), T24(15/10 active).',
 v10T21Finding:'T21 is the first strong post-D0 IMMINENT type. Of 6 entries all 6 became active; 1 became active before D0 exit and the remaining 5 after-exit leads were 38,40,81,120,219ms. Thus a T21 D0 exit is a strong <=250ms candidate. Repeated post-state frameEnd9859A/next9807C/value0/S4/A10/B4 had2/2 <=250ms target correct2/2; B6 variant also2/2 <=250ms target correct2/2.',
 v10T24Finding:'T24 remains branch-complex. Repeated post states generally gave only about 0.5-0.67 precision <=250ms; examples include frameEnd8AAF4/next8A658/S2/A4/B10 with 3/5 <=250ms at timer4-6 and 3/6 <=250ms at timer7-12. Do not promote T24 to low-FP IMMINENT yet.',
 v10T18Finding:'T18 post-exit short-horizon states remain weak/variable. Exit-to-active leads were 240,760,859,938,940,941ms for active-after-exit events; several repeated post states predict <=1000ms better than <=250ms. Keep T18 ATTACK_READY plus provisional candidate rules only.',
 v9CarryForward:'T33 D0=20 ENTRY was2/2 active within100ms with leads22/60ms and target correct2/2. T18 in-D0 LE3+S0/A4/B0 was2/2 <=250ms in V9 but remains provisional.',
 retargetPolicy:'Keep target live from enemy+0x7E; do not freeze warning target at D0 entry. +0x6A may be transitional/non-player and is only supporting evidence when valid.',
 futureDangerInterpretation:'Begin first read-only Future Danger shadow predictor. ATTACK_READY=exact D0=20 type-conditioned feature. Conservative IMMINENT candidates: T33 D0 entry <=100ms and T21 D0 exit <=250ms. T18/T24 rules remain candidate-only and are evaluated separately. ACTIVE=enemy+0x70 nonzero.',
 endToEndStructuralProofConfirmed:true,
 causalFrontier:'Shadow-evaluate rule precision/coverage in fresh combat instead of continuing open-ended state mining. Measure each rule prospectively with its own horizon and live target correctness. Promote only rules that retain high precision across independent episodes.',
 nextScript:'wof_future_danger_shadow_v11.js',
 nextMarker:'=== FUTURE DANGER SHADOW V11 JSON ===',
 note:'Do not restart selector search, Focus Multiroom, 44-edge scan, 0x0080F2, 0x11C26 bridge, universal-next1 search, eventual-active scoring, or universal D0 timer assumptions.'
};
self.__WOF_RESUME_FRONTIER=current;
console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);
console.log('NEXT: run first Future Danger shadow predictor and validate conservative T21/T33 IMMINENT rules.');
return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});