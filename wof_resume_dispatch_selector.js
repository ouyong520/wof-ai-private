(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
console.log('♻️ WOF resume: first Future Danger Map shadow frontier');
if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}
if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
 version:'wof-resume-dispatch-selector-v27',
 selectorSolved:true,
 selectorField:'enemy+0x7E',
 playerIndexValues:'P1=0 / P2=4 / P3=8',
 selectedPointerCacheCorrection:'enemy+0x6A is supporting selected-player cache only when BE1C/BEFC/BFDC; +0x7E is authoritative target identity.',
 d0Provenance:'0x006A62 MOVEQ #20,D0 -> JSR 0x25C8; 0x25C8 selects type descriptor and 0x247C consumes it.',
 activeAttackField:'enemy+0x70 U16; active start = 0 -> nonzero.',
 xyFields:'object +4/+8 are confirmed X/Y 16.16 fixed-point. Z is still not confirmed.',
 v14CaptureValidation:'Robust structural D0=20 entry is validated; exact start-timer equality is not required for live capture.',
 v15Totals:'V15 geometry run captured23 D0=20 episodes,21 active,1 horizonComplete, and202 global +0x70 active edges with valid live targets. Types seen7/9/10/13/20/30.',
 v15Timing:'T13 was the strongest new timing result:14/14 D0 episodes became active with leads41..241ms, all <=250ms in this room. Treat T13 ENTRY_250 as provisional-high pending fresh validation. T9 fresh4/4 leads281/339/340/341ms reinforces <=500ms. T30 active leads80/340/380ms reinforces <=500ms when active. Prior T10 roughly398..420ms remains <=500 observed.',
 v15SideStability:'Within D0 episodes, entry->active target-relative side was stable T30 3/3, T9 4/4, T13 12/14 (0.857). Retargeting remains real, so side/target must still be recomputed from live +0x7E every tick.',
 v15Geometry:'Global ACTIVE-start target-relative geometry showed strong type/attack clustering. Type-level V15 P90 envelopes used only as shadow priors: T9 X378/Y59 (n39), T10 X275/Y29 (n37), T13 X321/Y26 (n53), T30 X203/Y6 (n22). These are empirical ACTIVE-start distances, NOT proven hitboxes or damage ranges.',
 v15AttackClusters:'Examples: T10 attack3232 n15 median absDx159/absDy13; T9 attack3232 n19 median198/12; T30 attack2536 n13 median63/2; T13 attack6888 n24 median192/12 and attack4280 n7 median80/1. Keep attack-specific clustering for later refinement.',
 timingRules:'Current shadow timing rules: T13 ENTRY<=250 provisional-high; T9/T10/T30/T33 ENTRY<=500 type-conditioned; T21 D0 EXIT<=250 provisional. T18/T24 remain branch-variable and should not receive universal short-horizon promotion.',
 retargetPolicy:'Keep target live from enemy+0x7E; never freeze target or geometry at warning entry.',
 futureDangerInterpretation:'Proceed to first 0-1000ms Future Danger Map shadow. Anchor an empirical warning rectangle to the live enemy, mirror toward current live target side, and update it every tick. Validate fresh timing precision, target/side stability, and new-room envelope containment before calling the rectangle a production danger zone.',
 endToEndStructuralProofConfirmed:true,
 causalFrontier:'Prospectively validate V15-derived type envelopes and timing rules in V16. If containment and timing remain stable, next split envelopes by attack/body/descriptor state and then derive safer path/avoidance scoring. Do not equate +0x70 ACTIVE geometry with exact hitbox onset.',
 nextScript:'wof_future_danger_map_shadow_v16.js',
 nextMarker:'=== FUTURE DANGER MAP SHADOW V16 JSON ===',
 note:'Do not restart selector search, Focus Multiroom, 44-edge scan, 0x0080F2, 0x11C26 bridge, universal-next1 search, universal D0 timer assumptions, exact-start-timer gating, or treat empirical geometry rectangles as proven hitboxes.'
};
self.__WOF_RESUME_FRONTIER=current;
console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);
console.log('NEXT: run first Future Danger Map shadow and prospectively validate timing + geometry containment.');
return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});