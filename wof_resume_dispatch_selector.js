(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
console.log('♻️ WOF resume: selected-player -> action2A -> D0 -> A4 structure -> 0x247C frontier');
if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}
if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
  version:'wof-resume-dispatch-selector-v10',
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
  type35SelectedA4:'D0=16 -> A4=0x081864; D0=20 -> A4=0x081856',
  type35BoundaryCorrection:'D0=28 entry at 0x081790 is 0x3C0014 and is not a valid pointer; do not overread beyond the 7-entry prefix',
  a4SemanticCorrection:'0x081856/0x081864 raw bytes do not look like direct 68000 routine entries; both begin with pointer-like 0x000825D0. Treat them as A4-selected structures until 0x247C consumption semantics are decoded.',
  endToEndStructuralProofConfirmed:true,
  causalFrontier:'decode exact 0x247C handoff semantics after 0x25C8 sets A4=0x081856/0x081864; establish whether first long 0x000825D0 is the executable routine pointer and identify which structure fields distinguish D0=16 vs D0=20. Then classify attack/startup semantics and merge with live target transitions.',
  nextScript:'wof_dispatch_247c_a4_structure_probe.js',
  nextMarker:'=== DISPATCH 247C A4 STRUCTURE PROBE JSON ===',
  note:'Do not call 0x81856/0x81864 final handlers yet. Do not restart selector search, Focus Multiroom, 44-edge scan, 0x0080F2, 0x11C26 bridge, broad +0x7E/+0x7C scans, or raw-even-address opcode sweeping.'
};
self.__WOF_RESUME_FRONTIER=current;
console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);
console.log('NEXT: decode 0x247C A4 structure consumption.');
return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});
