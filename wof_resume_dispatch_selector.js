(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
console.log('♻️ WOF resume: live Future Danger shadow frontier');
if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}
if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
 version:'wof-resume-dispatch-selector-v24',
 selectorSolved:true,
 selectorField:'enemy+0x7E',
 playerIndexValues:'P1=0 / P2=4 / P3=8',
 selectedPointerCacheCorrection:'enemy+0x6A is supporting selected-player cache only when BE1C/BEFC/BFDC; +0x7E is authoritative target identity.',
 selectedPlayerActionBridgeConfirmed:true,
 strongestBridge:'0x006834 MOVEA.W 106(A0),A1 -> CMPI.B #4,41(A1) -> BEQ 0x006850 -> read enemy+0x2A -> indexed action JMP',
 d0Provenance:'0x006A10 MOVEQ #16,D0 -> JSR 0x25C8; 0x006A62 MOVEQ #20,D0 -> JSR 0x25C8',
 dispatcherSemantic:'0x25C8 selects type-specific action descriptors; 0x247C consumes descriptor stream; frameEnd pointers are data, not code.',
 activeAttackField:'enemy+0x70 U16; active start = 0 -> nonzero.',
 v12Totals:'V12 captured 9 fresh exact D0=20 episodes, all 9 reached active. Types: T34(1), T11(3), T33(2), T16(2), T30(1). No T21 episode appeared.',
 v12T33Correction:'T33 ENTRY_250 is not low-FP enough: fresh leads20/341ms =>1/2 <=250ms. Combined observed V9+V11+V12 T33 entry leads are20/22/60/61/140/199/341ms: 6/7 <=250ms but 7/7 <=500ms. Downgrade T33 from IMMINENT<=250 to DANGER_SOON<=500.',
 v12T30Correction:'T30 fresh independent episode lead340ms falsified ENTRY_250 as universal. Combined V11+V12 observed leads140/140/160/180/340ms: 4/5 <=250ms, 5/5 <=500ms. Use provisional DANGER_SOON<=500, not IMMINENT<=250.',
 v12T21Status:'No fresh T21 in V11 or V12. V10 evidence remains5/5 post-D0 exit leads38/40/81/120/219ms <=250ms. Keep T21 EXIT_250 as the only current IMMINENT rule, but mark provisional until fresh-room repetition.',
 v12OtherTypes:'T11 fresh entry leads139/239/280ms =3/3 <=500ms but only2/3 <=250ms; do not promote from one room. T16 fresh160/499ms and T34 fresh260ms support type-conditioned ATTACK_READY but not a new low-FP <=250ms rule.',
 retargetPolicy:'Keep target live from enemy+0x7E; never freeze warning target. +0x6A may be transitional/non-player and is only supporting evidence when valid.',
 futureDangerInterpretation:'Begin live shadow event output. ATTACK_READY=all exact D0=20 without a universal horizon. DANGER_SOON<=500=T33/T30 D0 entry. IMMINENT<=250=T21 D0 exit provisional. ACTIVE=enemy+0x70 nonzero. Runtime state must retarget immediately from +0x7E.',
 endToEndStructuralProofConfirmed:true,
 causalFrontier:'Validate the live warning stack itself rather than continue broad state mining. Measure T33/T30 <=500 precision, obtain fresh T21 EXIT<=250 repetition, record live retargets, and keep ATTACK_READY coverage by type. If stable, next integrate hazard direction/range and 0-1000ms Future Danger map.',
 nextScript:'wof_future_danger_live_shadow_v13.js',
 nextMarker:'=== FUTURE DANGER LIVE SHADOW V13 JSON ===',
 note:'Do not restart selector search, Focus Multiroom, 44-edge scan, 0x0080F2, 0x11C26 bridge, universal-next1 search, eventual-active scoring, universal D0 timer assumptions, T33 <=250 hard rule, T30 <=250 hard rule, or T24 AB32 candidate.'
};
self.__WOF_RESUME_FRONTIER=current;
console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);
console.log('NEXT: run live Future Danger shadow: READY -> DANGER_SOON<=500 -> IMMINENT<=250 -> ACTIVE, with live +0x7E retargeting.');
return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});