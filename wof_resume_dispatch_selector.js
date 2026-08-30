(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
console.log('♻️ WOF resume: multi-transition causal frontier');
if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}
if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
  version:'wof-resume-dispatch-selector-v4',
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
  firstCausalTransitionObserved:'slot11 type35: P3->P2; nearest remained P1; state99 stayed 2; action2A 6->0 at transition, then 0->2 about 69ms later',
  firstLeadCandidate:'new target P2 changed +0x65/+0x66/+0x67/+0x7A/+0x7B/+0xA9 and +0x2A about 101ms before target switch; single-case hypothesis only',
  causalFrontier:'repeat target transitions -> rank new-target lead fields vs old/other players -> narrow ROM compare/helper path -> state/action/D0/handler',
  nextScript:'wof_selector_transition_causal_recorder_v2.js',
  nextMarker:'=== SELECTOR TRANSITION CAUSAL V2 JSON ===',
  note:'Do not restart selector search, 44-edge scan, Focus Multiroom, HUD, 0x0080F2, 0x11C26 bridge, broad +7C/+7E writer scans, or full-ROM raw opcode sweeps.'
};
self.__WOF_RESUME_FRONTIER=current;
console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);
console.log('NEXT: read-only multi-transition validation on one enemy slot; static selector structure remains closed.');
return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});
