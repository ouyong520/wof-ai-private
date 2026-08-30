(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
console.log('♻️ WOF resume: selected-player -> action causal bridge frontier');
if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}
if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
  version:'wof-resume-dispatch-selector-v6',
  selectorSolved:true,
  selectorField:'enemy+0x7E',
  playerSelfIndexField:'player+0x7C',
  playerIndexValues:'P1=0 / P2=4 / P3=8',
  playerPointerTable:'0x010CF8',
  selectedPointerScratch:'506(A5)',
  selectedPointerCache:'enemy+0x6A low16 = BE1C/BEFC/BFDC',
  selectedPointerCacheRuntimeProof:'latest +0x6A probe: active valid slot matchPct=1.0; live transitions mapped BFDC<->BEFC with target changes',
  state99Field:'enemy+0x99',
  action2AField:'enemy+0x2A',
  provenDispatchRoute:'state99=0 + action2A=2 -> 0x010EC6 -> MOVEQ #24,D0 -> 0x010F48 -> 0x0025C8',
  endToEndStructuralProofConfirmed:true,
  staticSelectorSearchClosed:true,
  liveTransitionPattern:'clean live transitions changed action2A on target-transition frame; state99 need not change',
  selectedPlayerReaderProof:'ROM has MOVEA.W 106(A0),A1 at 0x0112AA,0x0065E2,0x006834',
  strongestBridge:'0x006834 MOVEA.W 106(A0),A1 -> CMPI.B #4,41(A1) -> BEQ 0x006850 -> read enemy+0x2A action dispatch',
  secondaryBridge:'0x0065E2 MOVEA.W 106(A0),A1 -> CMPI.B #4,41(A1) -> conditional branch',
  actionTargetContext:'0x0112C2 is one of known state99/action2A targets and immediately performs enemy+0x2B subdispatch; 0x0112AA selected-player reader is adjacent helper code',
  causalFrontier:'exact CFG/table proof for +0x6A -> selectedPlayer+0x29 compare -> action dispatch; map 0x65E2/0x6834 into 25B6/25C8 type-specific handler tables',
  nextScript:'wof_selector_6a_action_causal_proof.js',
  nextMarker:'=== SELECTOR 6A ACTION CAUSAL PROOF JSON ===',
  note:'Do not restart selector search, 44-edge scan, Focus Multiroom, HUD, 0x0080F2, 0x11C26 bridge, broad +7C/+7E scans, or raw full-ROM sweeps. +0x6A is a selected-player pointer cache, not the 0/4/8 selector index.'
};
self.__WOF_RESUME_FRONTIER=current;
console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);
console.log('NEXT: exact structural proof of selected-player pointer consumption into action decision.');
return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});
