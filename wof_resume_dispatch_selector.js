(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
console.log('♻️ WOF resume: full-ROM selected-player -> action -> handler frontier');
if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}
if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
  version:'wof-resume-dispatch-selector-v7',
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
  sub112Correction:'0x0112D6 relative table must stop at first target; first word 0x0006 implies 3 word entries, not 16',
  causalFrontier:'full-ROM map 0x65E2/0x6834 action bridge into 47 type-specific level2 tables; resolve type35 D0 offset and action target -> dispatcher/handler',
  nextScript:'wof_selector_6a_action_handler_map_v2.js',
  nextMarker:'=== SELECTOR 6A ACTION HANDLER MAP V2 JSON ===',
  note:'Do not restart selector search, Focus Multiroom, 44-edge scan, 0x0080F2, 0x11C26 bridge, or broad raw opcode sweeps. The current work is only the narrow full-ROM table mapping exposed by the proven +0x6A bridge.'
};
self.__WOF_RESUME_FRONTIER=current;
console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);
console.log('NEXT: full-ROM type/D0 mapping for the proven selected-player action bridge.');
return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});
