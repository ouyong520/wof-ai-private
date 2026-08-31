(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
console.log('♻️ WOF resume: Future Danger 250ms rule-validation frontier');
if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}
if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
 version:'wof-resume-dispatch-selector-v23',
 selectorSolved:true,
 selectorField:'enemy+0x7E',
 playerIndexValues:'P1=0 / P2=4 / P3=8',
 selectedPointerCacheCorrection:'enemy+0x6A is supporting selected-player cache only when BE1C/BEFC/BFDC; +0x7E is authoritative target identity.',
 selectedPlayerActionBridgeConfirmed:true,
 strongestBridge:'0x006834 MOVEA.W 106(A0),A1 -> CMPI.B #4,41(A1) -> BEQ 0x006850 -> read enemy+0x2A -> indexed action JMP',
 d0Provenance:'0x006A10 MOVEQ #16,D0 -> JSR 0x25C8; 0x006A62 MOVEQ #20,D0 -> JSR 0x25C8',
 dispatcherSemantic:'0x25C8 selects type-specific action descriptors; 0x247C consumes descriptor stream; frameEnd pointers are data, not code.',
 activeAttackField:'enemy+0x70 U16; active start = 0 -> nonzero.',
 v11Totals:'V11 fresh-room shadow captured 26 exact D0=20 episodes: 22 active, 4 horizonComplete, 6 rule signals. Gates strict/read-only. T24 candidate fired3 times and was only1/3 <=250ms, so reject it as low-FP IMMINENT.',
 v11T33Correction:'T33_ENTRY_100 was falsified as a 100ms rule: fresh leads were61,140,199ms, only1/3 <=100ms. However all3/3 were <=250ms with target stable, and combined with V9 leads22/60ms gives observed5/5 T33 D0-entry <=250ms. Reframe T33 as provisional ENTRY_250, not ENTRY_100.',
 v11T30Finding:'New T30 evidence: four independent exact D0=20 entries led active in140,180,160,140ms, all <=250ms and entry/active target remained P3. Promote only to candidate pending independent repetition.',
 v11T21Status:'No T21 episode appeared in V11, so V10 evidence remains unchallenged: five post-D0 exit leads38/40/81/120/219ms, all <=250ms. Needs fresh-room repetition before production promotion.',
 v11RetargetEvidence:'T18 again showed entry target can differ from active target in some episodes; live enemy+0x7E retargeting remains mandatory. Never freeze target at ATTACK_READY/IMMINENT signal time.',
 retargetPolicy:'Keep target live from enemy+0x7E. +0x6A may be transitional/non-player and is only supporting evidence when valid.',
 futureDangerInterpretation:'ATTACK_READY remains exact D0=20 type-conditioned. IMMINENT validation frontier is now 250ms: T33 ENTRY_250 and T21 EXIT_250 as provisional strong rules; T30 ENTRY_250 as candidate. Reject T24_AB32 candidate. T18 remains too branch-variable for a production short-horizon rule.',
 endToEndStructuralProofConfirmed:true,
 causalFrontier:'Prospectively validate T33_ENTRY_250, T21_EXIT_250 and T30_ENTRY_250 in fresh combat; measure precision, live-target accuracy and coverage. If T33/T21 retain high precision and T30 independently repeats, begin real-time Future Danger event output rather than further broad mining.',
 nextScript:'wof_future_danger_rule_validator_v12.js',
 nextMarker:'=== FUTURE DANGER RULE VALIDATOR V12 JSON ===',
 note:'Do not restart selector search, Focus Multiroom, 44-edge scan, 0x0080F2, 0x11C26 bridge, universal-next1 search, eventual-active scoring, universal D0 timer assumptions, T33 100ms rule, or T24 AB32 IMMINENT candidate.'
};
self.__WOF_RESUME_FRONTIER=current;
console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);
console.log('NEXT: validate T33/T21/T30 250ms Future Danger rules prospectively.');
return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});