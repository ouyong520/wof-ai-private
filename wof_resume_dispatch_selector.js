(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
console.log('♻️ WOF resume: D0=20 type-conditioned ATTACK_READY + prospective horizon calibration frontier');
if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}
if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
 version:'wof-resume-dispatch-selector-v19',
 selectorSolved:true,
 selectorField:'enemy+0x7E',
 playerIndexValues:'P1=0 / P2=4 / P3=8',
 selectedPointerCacheCorrection:'enemy+0x6A is supporting selected-player cache only when BE1C/BEFC/BFDC; +0x7E is authoritative target identity.',
 selectedPlayerActionBridgeConfirmed:true,
 strongestBridge:'0x006834 MOVEA.W 106(A0),A1 -> CMPI.B #4,41(A1) -> BEQ 0x006850 -> read enemy+0x2A -> indexed action JMP',
 d0Provenance:'0x006A10 MOVEQ #16,D0 -> JSR 0x25C8; 0x006A62 MOVEQ #20,D0 -> JSR 0x25C8',
 dispatcherSemantic:'0x25C8 selects type-specific action descriptors; 0x247C consumes descriptor stream; frameEnd pointers are data, not code.',
 activeAttackField:'enemy+0x70 U16; active start = 0 -> nonzero.',
 v6Conclusion:'D0=20.next is not universal IMMINENT. next1->active median was ~740ms and attacks can become active before next1.',
 v7Proof:'V7 captured 11 exact D0=20 watches: 9 active, 1 timeout, 1 slotGone/censored; 5 active within1000ms. Per type: T14 2/2 active at79/181ms and 2/2 within1000; T24 active leads60/561/1560ms plus one slotGone; T18 active leads481/1218/1762/2122ms plus one timeout. Therefore D0=20 must be calibrated by type and state for the 0-1000ms horizon.',
 v7BranchFinding:'Repeated post-D0 signatures often had eventual active rate1.0 but long/variable leads (e.g. ~680-1442ms), proving eventual-active rate is a biased Stage2 criterion. Several T18 near-active signatures appeared 38/41/60/80ms before active but only once each, so they require prospective repetition before promotion.',
 retargetPolicy:'Keep target live from enemy+0x7E; V7 again captured an active event whose target changed from P1 to P2 at active time.',
 futureDangerInterpretation:'Use prospective horizon probabilities, not eventual-active labels. For each per-type state exposure evaluate P(active<=100/250/500/1000ms), with retrigger/slotGone/typeChanged/captureEnd censored when follow-up is insufficient.',
 endToEndStructuralProofConfirmed:true,
 causalFrontier:'Prospectively calibrate exact+timer, descriptor-only, and control+timer signatures. Promote only repeated high-precision <=100/250ms signatures to IMMINENT; retain D0=20 as type-conditioned ATTACK_READY.',
 nextScript:'wof_future_horizon_calibrator_v8.js',
 nextMarker:'=== FUTURE HORIZON CALIBRATOR V8 JSON ===',
 note:'Do not restart selector search, Focus Multiroom, 44-edge scan, 0x0080F2, 0x11C26 bridge, or universal-next1 search. Do not count censored watches as false positives and do not use eventual-active rate as short-horizon precision.'
};
self.__WOF_RESUME_FRONTIER=current;
console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);
console.log('NEXT: prospective 100/250/500/1000ms horizon calibration by enemy type/state.');
return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});