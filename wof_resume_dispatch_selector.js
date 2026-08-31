(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
console.log('♻️ WOF resume: selected-player -> action2A -> D0 -> type35 handler frontier');
if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}
if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
  version:'wof-resume-dispatch-selector-v9',
  selectorSolved:true,
  selectorField:'enemy+0x7E',
  playerIndexValues:'P1=0 / P2=4 / P3=8',
  playerPointerTable:'0x010CF8',
  selectedPointerCache:'enemy+0x6A low16 = BE1C/BEFC/BFDC',
  selectedPointerCacheRuntimeProof:'runtime matchPct=1.0 on latest valid live slot; live transitions mapped BFDC<->BEFC with target changes',
  state99Field:'enemy+0x99',
  action2AField:'enemy+0x2A',
  selectedPlayerActionBridgeConfirmed:true,
  strongestBridge:'0x006834 MOVEA.W 106(A0),A1 -> CMPI.B #4,41(A1) -> BEQ 0x006850 -> read enemy+0x2A -> indexed action JMP',
  action68Exact:'0x006850 action2A dispatch has exactly 2 entries: action2A=0 -> 0x006862; action2A=2 -> 0x006904',
  d0Provenance:'0x006A10 MOVEQ #16,D0 -> 0x006A12 JSR 0x25C8; 0x006A62 MOVEQ #20,D0 -> 0x006A64 JSR 0x25C8',
  type35Table:'0x081774 shared by types 7 and 35; valid prefix D0=0,4,8,12,16,20,24 only',
  type35ExactHandlers:'D0=16 -> 0x081864; D0=20 -> 0x081856',
  type35BoundaryCorrection:'D0=28 entry at 0x081790 is 0x3C0014 and is not a valid handler pointer; do not overread beyond the 7-entry prefix',
  endToEndStructuralProofConfirmed:true,
  causalFrontier:'classify exact type35 final handlers 0x081864 and 0x081856 and map their attack/startup semantics; then merge handler identity with live target/action transitions for Future Danger',
  nextScript:'wof_type35_d0_16_20_handler_inspector.js',
  nextMarker:'=== TYPE35 D0 16/20 HANDLER INSPECTOR JSON ===',
  note:'Do not restart selector search, Focus Multiroom, 44-edge scan, 0x0080F2, 0x11C26 bridge, broad +0x7E/+0x7C scans, or raw-even-address opcode sweeping. Known handler entry addresses 0x81856/0x81864 are the next exact CFG roots.'
};
self.__WOF_RESUME_FRONTIER=current;
console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);
console.log('NEXT: classify type35 D0=16 and D0=20 final handlers.');
return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});
