(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
console.log('♻️ WOF resume: type-conditioned D0=20 + prospective timer-hazard frontier');
if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}
if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
 version:'wof-resume-dispatch-selector-v20',
 selectorSolved:true,
 selectorField:'enemy+0x7E',
 playerIndexValues:'P1=0 / P2=4 / P3=8',
 selectedPointerCacheCorrection:'enemy+0x6A is supporting selected-player cache only when BE1C/BEFC/BFDC; +0x7E is authoritative target identity.',
 selectedPlayerActionBridgeConfirmed:true,
 strongestBridge:'0x006834 MOVEA.W 106(A0),A1 -> CMPI.B #4,41(A1) -> BEQ 0x006850 -> read enemy+0x2A -> indexed action JMP',
 d0Provenance:'0x006A10 MOVEQ #16,D0 -> JSR 0x25C8; 0x006A62 MOVEQ #20,D0 -> JSR 0x25C8',
 dispatcherSemantic:'0x25C8 selects type-specific action descriptors; 0x247C consumes descriptor stream; frameEnd pointers are data, not code.',
 activeAttackField:'enemy+0x70 U16; active start = 0 -> nonzero.',
 v8Proof:'V8 captured 5/5 exact D0=20 watches reaching active: T34 lead279ms; T23 leads120/479ms; T16 leads240/400ms. Stage1 remains useful but type-conditioned. T23 and T16 D0=20 descriptor-level precision was 2/2 within500ms but only1/2 within250ms. T34 was1/1 within500ms.',
 v8TimerFinding:'The strongest new signal is remaining D0=20 timer, not a universal successor descriptor. In near-active traces: T34 timer6->active100ms, timer2->40ms, timer1->20ms; T23 timer6->99ms and timer3->39ms; T16 timer6->79ms, timer3->59/20ms depending branch, timer1->20ms. These are still small samples and must be prospectively repeated before promotion.',
 v8ControlCandidate:'T23 control signature S0/A6/B4 with timer bucket7-12 appeared in two independent watches and was 2/2 active within250ms with target correct2/2. Treat as candidate evidence only, not yet a hard-coded rule.',
 horizonCorrection:'Project target is Future Danger 0-1000ms. A D0 watch with no active for >=1000ms is already a valid miss for that horizon; there is no need to wait 2-3 seconds to learn eventual attack. Later attacks are irrelevant to the requested prediction window.',
 retargetPolicy:'Keep target live from enemy+0x7E. +0x6A may be transitional/non-player and is only supporting evidence when valid.',
 futureDangerInterpretation:'Use D0=20 as ATTACK_READY and test timer-threshold hazard as Stage2. Prefer high-precision short-horizon triggers such as D0=20 timer<=6/3/1, conditioned by type/control state when needed. Do not assume timer countdown is universal because preemption branches exist.',
 endToEndStructuralProofConfirmed:true,
 causalFrontier:'Prospectively validate one exposure per D0 episode when timer first reaches <=12/6/3/1, plus D0 exit/control-change events. Measure P(active<=100/250/500/1000ms) globally, per type, and per type+control signature with proper censoring. If timer<=6 or a type/control refinement repeats with high <=100/250ms precision, promote it to IMMINENT and begin integrating into Future Danger AI.',
 nextScript:'wof_d020_timer_hazard_shadow_v9.js',
 nextMarker:'=== D0=20 TIMER HAZARD SHADOW V9 JSON ===',
 note:'Do not restart selector search, Focus Multiroom, 44-edge scan, 0x0080F2, 0x11C26 bridge, universal-next1 search, or eventual-active scoring. Do not hard-code V8 timer examples until V9 prospective repetition confirms them.'
};
self.__WOF_RESUME_FRONTIER=current;
console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);
console.log('NEXT: validate D0=20 timer-threshold hazard for 0-1000ms Future Danger.');
return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});