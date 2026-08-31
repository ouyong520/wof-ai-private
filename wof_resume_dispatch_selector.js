(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
console.log('♻️ WOF resume: pre-active signature frontier');
if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}
if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
 version:'wof-resume-dispatch-selector-v29',
 selectorSolved:true,
 selectorField:'enemy+0x7E',
 playerIndexValues:'P1=0 / P2=4 / P3=8',
 selectedPointerCacheCorrection:'enemy+0x6A is supporting selected-player cache only when BE1C/BEFC/BFDC; +0x7E is authoritative target identity.',
 d0Provenance:'0x006A62 MOVEQ #20,D0 -> JSR 0x25C8; 0x25C8 selects type descriptor and 0x247C consumes it.',
 activeAttackField:'enemy+0x70 U16; active start = 0 -> nonzero.',
 xyFields:'object +4/+8 are confirmed X/Y 16.16 fixed-point. Z is still not confirmed.',
 v17Totals:'V17 captured5 D0 episodes, all5 active, only1 timing-rule exposure, plus209 global ACTIVE edges and28 fresh type+attack geometry clusters.',
 v17Timing:'Fresh T10 ENTRY_500 hit at261ms. T20 showed strong branch divergence inside the same type: signature T20|S0|A4|B0|BODY4976 led to attack4920 at81ms, while T20|S4|A6|B4|BODY4976 led to attack5888 at701ms. T22 S0/A6/B6/BODY10168 led979ms. This supports branch-aware state signatures rather than type-only timing.',
 v17T30:'T30 fixed <=500 remains removed. One fresh T30 S0/A6/B6/BODY1800 episode became attack2536 at340ms but retargeted P1->P3 at ACTIVE; target and side must remain live.',
 v17GeometryCorrection:'Attack-specific envelopes from V15 also vary by room. Fresh V17 containment: T30 A2528 0/13, T30 A2536 7/11, T10 A3232 0/6, T10 A5336 0/5, T9 A3232 4/5, T9 A2808 3/3, T9 A5336 0/3. Therefore even attack-specific P90 seeds are not yet production-safe; pool repeated rooms and condition geometry on pre-active branch/state.',
 currentTimingRules:'Keep T9/T10/T33 ENTRY<=500; T13 ENTRY<=250 provisional; T21 EXIT<=250 provisional. T30 fixed <=500 remains removed. T18/T24 and now T20/T22 clearly show branch-variable horizons.',
 liveExpiry:'Horizon expiry is fixed from V17 onward; expired warnings must downgrade rather than remain stale.',
 newFrontier:'D0 entry alone is too sparse for fast branch learning. V18 prospectively watches every pre-active signature entry while attack==0 at three levels: coarse(type/inD20/state99/action2A/b2B/body), descriptor(+frameEnd/next/value30), and fine(+timer). Each exposure is scored against the next +0x70 ACTIVE edge within100/250/500ms and against the resulting attack family, live target and side.',
 geometryFrontier:'V18 also rebuilds fresh type+attack ACTIVE geometry with P50/P90/P95/max instead of trusting a single-room seed envelope. Geometry remains an empirical ACTIVE-start distribution, not a hitbox proof.',
 retargetPolicy:'Always use live enemy+0x7E. Never freeze target or side from an earlier warning state.',
 endToEndStructuralProofConfirmed:true,
 causalFrontier:'Use V18 to discover repeated low-false-positive pre-active state signatures with stable resulting attack family. Promote only signatures that repeat across independent rooms. Then attach pooled attack/branch geometry and begin Safe Path scoring.',
 nextScript:'wof_future_danger_preactive_signature_v18.js',
 nextMarker:'=== FUTURE DANGER PREACTIVE SIGNATURE V18 JSON ===',
 note:'Do not restart selector search, Focus Multiroom, 44-edge scan, 0x0080F2, 0x11C26 bridge, universal-next1 search, universal timer assumptions, exact-start-timer gating, T30 <=500 hard warning, or treat type/attack P90 rectangles as proven hitboxes.'
};
self.__WOF_RESUME_FRONTIER=current;
console.log('=== CURRENT SELECTOR FRONTIER ===');
console.table([current]);
console.log('NEXT: run V18 prospective pre-active signature learner.');
return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});