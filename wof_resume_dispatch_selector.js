(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
console.log('♻️ WOF resume: selected-player -> action2A -> D0 -> descriptor startup frontier');
if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}
if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
  version:'wof-resume-dispatch-selector-v12',
  selectorSolved:true,
  selectorField:'enemy+0x7E',
  playerIndexValues:'P1=0 / P2=4 / P3=8',
  playerPointerTable:'0x010CF8',
  selectedPointerCache:'enemy+0x6A low16 = BE1C/BEFC/BFDC',
  selectedPlayerActionBridgeConfirmed:true,
  strongestBridge:'0x006834 MOVEA.W 106(A0),A1 -> CMPI.B #4,41(A1) -> BEQ 0x006850 -> read enemy+0x2A -> indexed action JMP',
  action68Exact:'0x006850 action2A dispatch has exactly 2 entries: action2A=0 -> 0x006862; action2A=2 -> 0x006904',
  d0Provenance:'0x006A10 MOVEQ #16,D0 -> 0x006A12 JSR 0x25C8; 0x006A62 MOVEQ #20,D0 -> 0x006A64 JSR 0x25C8',
  dispatcherSemanticCorrection:'0x25C8 selects type-specific action descriptors, not direct executable handlers; it BRA 0x247C where A4 is consumed as a descriptor stream.',
  descriptor247CExact:'0x247C MOVEA.L (A4)+,A6; 0x247E MOVE.L (A4)+,0x30(A0); 0x2482 MOVE.W (A4)+,D1. bit15 timer flag selects explicit-next pointer at +0x0A; otherwise next descriptor is inline.',
  payloadCopyExact:'A6 is a frame/payload end pointer. 0x2490 stores it to enemy+0x12; 0x2498/0x249A copy the last 6 payload bytes into enemy+0x6C..+0x71.',
  type35Table:'0x081774 shared by types 7 and 35; valid D0 prefix 0,4,8,12,16,20,24 only; D0=28 is not a descriptor pointer.',
  type35D0_20:'descriptor 0x81856: frameEnd=0x825D0, timer=16, explicit next=0x817CC. Chain: 0x817CC timer1 -> 0x817D6/E0/EA/F4/FE/0x81808 each timer5 -> loop back 0x817D6. First pass total about 47 ticks, then about 30-tick loop.',
  type35D0_16:'descriptor 0x81864: frameEnd=0x825D0, timer=0x7FFF, explicit next=self. Long-hold state.',
  historicalRuntimeCorrelation:'Old multiroom captures independently show type35 frames 531402,531464,531690 with attack=0 and startupTop T35_F01/T35_F02; frame531620 also attack=0. These frame addresses are in the D0=20 descriptor chain, strongly classifying D0=20 as pre-active/startup rather than active/recovery.',
  latestRuntimeGap:'The dedicated 10s type35 descriptor runtime probe saw no type35 slots in the current room, so it produced no live fingerprint events; this does not contradict the static chain.',
  endToEndStructuralProofConfirmed:true,
  causalFrontier:'Use an all-type runtime probe so the current multiplayer room can validate D0=16/D0=20 descriptor fingerprints without waiting for type35. Correlate selectedPlayer+0x29, target7E, action2A, state99 and descriptor entry changes on the same live enemy. After runtime order is confirmed, convert D0=20 descriptor entry into a Future Danger startup signal and measure lead-to-active/damage.',
  nextScript:'wof_d016_20_descriptor_runtime_alltypes_v1.js',
  nextMarker:'=== D0 16/20 DESCRIPTOR RUNTIME ALLTYPES V1 JSON ===',
  note:'Do not call descriptor pointers code handlers; do not treat frameEnd as code. Do not restart selector search, Focus Multiroom, 44-edge scan, 0x0080F2, 0x11C26 bridge, broad +0x7E/+0x7C scans, or raw-even-address opcode sweeping.'
};
self.__WOF_RESUME_FRONTIER=current;
console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);
console.log('NEXT: all-type live D0=16/20 descriptor correlation in the current room.');
return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});