(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
console.log('♻️ WOF resume: causal-transition frontier');
if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}
if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
  version:'wof-resume-dispatch-selector-v3',
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
  structuralProofVerdict:'selectorStrict/playerTableOk/state99Strict/action2AStrict/bridgeStrict = true',
  staticSelectorSearchClosed:true,
  causalFrontier:'selected player -> target-dependent decision -> state99/action2A transition -> D0/handler',
  nextScript:'wof_selector_transition_causal_recorder.js',
  nextMarker:'=== SELECTOR TRANSITION CAUSAL JSON ===',
  note:'Do not restart selector search, 44-edge scan, Focus Multiroom, HUD, 0x0080F2, 0x11C26 bridge, or full-ROM raw opcode sweeps.'
};
self.__WOF_RESUME_FRONTIER=current;
console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);
console.log('NEXT: read-only single-enemy target-transition causal recording; static selector structure is closed.');
return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});
