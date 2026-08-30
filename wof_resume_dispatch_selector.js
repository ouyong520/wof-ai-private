(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
console.log('♻️ WOF resume: +0x6A selected-player pointer bridge frontier');
if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}
if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
  version:'wof-resume-dispatch-selector-v5',
  selectorSolved:true,
  selectorField:'enemy+0x7E',
  playerSelfIndexField:'player+0x7C',
  playerIndexValues:'P1=0 / P2=4 / P3=8',
  playerPointerTable:'0x010CF8',
  selectedPointerScratch:'506(A5)',
  state99Field:'enemy+0x99',
  action2AField:'enemy+0x2A',
  provenDispatchRoute:'state99=0 + action2A=2 -> 0x010EC6 -> MOVEQ #24,D0 -> 0x010F48 -> 0x0025C8',
  endToEndStructuralProofConfirmed:true,
  staticSelectorSearchClosed:true,
  v2CasesCaptured:3,
  v2CaseQuality:'case1 P2->P1 was object/slot lifecycle reset and must be excluded; cases2/3 are live transitions',
  liveTransitionPattern:'valid live transitions P1->P2 and P2->P3 both changed action2A on target-transition frame; state99 did not need to change',
  nearestRule:'not sufficient: V1 P3->P2 occurred while nearest remained P1; V2 two live transitions happened to move to nearest',
  selectedPointerCandidate:'enemy+0x6A/+0x6B tracks selected player low16 pointer on observed live transitions: BFDC->BEFC for P3->P2, BEFC->BFDC for P2->P3, and 0000->BEFC for P1->P2',
  causalFrontier:'prove +0x6A as selected-player pointer cache -> find ROM +0x6A readers/writers -> target-dependent compare/helper -> action2A -> D0/handler',
  nextScript:'wof_selector_6a_pointer_bridge.js',
  nextMarker:'=== SELECTOR 6A POINTER BRIDGE JSON ===',
  note:'Do not restart selector search, 44-edge scan, Focus Multiroom, HUD, 0x0080F2, 0x11C26 bridge, broad +7C/+7E writer scans, or full-ROM raw opcode sweeps. +0x6A is being reclassified from old correlation candidate to low16 selected-player pointer cache based on transition evidence, not revived as selector index.'
};
self.__WOF_RESUME_FRONTIER=current;
console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);
console.log('NEXT: focused read-only +0x6A pointer-cache validation and ROM bridge scan.');
return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});
