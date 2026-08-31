(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
console.log('♻️ WOF resume: 1MiB selected-player -> action -> handler frontier');
if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}
if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
  version:'wof-resume-dispatch-selector-v8',
  selectorSolved:true,
  selectorField:'enemy+0x7E',
  playerIndexValues:'P1=0 / P2=4 / P3=8',
  playerPointerTable:'0x010CF8',
  selectedPointerCache:'enemy+0x6A low16 = BE1C/BEFC/BFDC',
  selectedPointerCacheRuntimeProof:'runtime matchPct=1.0 on latest valid live slot; live transitions mapped BFDC<->BEFC with target changes',
  state99Field:'enemy+0x99',
  action2AField:'enemy+0x2A',
  endToEndStructuralProofConfirmed:true,
  selectedPlayerActionBridgeConfirmed:true,
  strongestBridge:'0x006834 MOVEA.W 106(A0),A1 -> CMPI.B #4,41(A1) -> BEQ 0x006850 -> read enemy+0x2A -> indexed action JMP',
  secondaryBridge:'0x0065E2 MOVEA.W 106(A0),A1 -> CMPI.B #4,41(A1) -> BEQ 0x006630 -> enemy+0x2A action dispatch',
  priorHandlerMapBug:'v1 capped ROM at 0x30000, but type35 level2 table base is 0x081774; handlerTableHits=0 was not a negative result',
  handlerMapBoundaryCorrection:'v2.1 scans the known 1MiB live program ROM only (0x000000-0x0FFFFF); 0x081774 is covered without spilling into following HEAP data',
  sub112Correction:'0x0112D6 relative table stops by first relative target; first word 0x0006 implies exactly 3 word entries',
  causalFrontier:'map 0x65E2/0x6834 selected-player action bridge into 47 type-specific level2 tables; resolve type35 D0/action target and, if not direct, classify literal-pointer table context for the next narrow CFG step',
  nextScript:'wof_selector_6a_action_handler_map_v2.js',
  nextMarker:'=== SELECTOR 6A ACTION HANDLER MAP V2 JSON ===',
  note:'Do not restart selector search, Focus Multiroom, 44-edge scan, 0x0080F2, 0x11C26 bridge, or broad raw opcode sweeps. Current work is only the narrow table/CFG mapping exposed by the proven +0x6A bridge.'
};
self.__WOF_RESUME_FRONTIER=current;
console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);
console.log('NEXT: 1MiB type/D0 mapping for the proven selected-player action bridge.');
return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});
