(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
console.log('♻️ WOF resume: selected-player -> action2A -> D0 -> descriptor-chain frontier');
if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}
if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
  version:'wof-resume-dispatch-selector-v11',
  selectorSolved:true,
  selectorField:'enemy+0x7E',
  playerIndexValues:'P1=0 / P2=4 / P3=8',
  playerPointerTable:'0x010CF8',
  selectedPointerCache:'enemy+0x6A low16 = BE1C/BEFC/BFDC',
  selectedPlayerActionBridgeConfirmed:true,
  strongestBridge:'0x006834 MOVEA.W 106(A0),A1 -> CMPI.B #4,41(A1) -> BEQ 0x006850 -> read enemy+0x2A -> indexed action JMP',
  action68Exact:'0x006850 action2A dispatch has exactly 2 entries: action2A=0 -> 0x006862; action2A=2 -> 0x006904',
  d0Provenance:'0x006A10 MOVEQ #16,D0 -> 0x006A12 JSR 0x25C8; 0x006A62 MOVEQ #20,D0 -> 0x006A64 JSR 0x25C8',
  type35Table:'0x081774 shared by types 7 and 35; valid prefix D0=0,4,8,12,16,20,24 only',
  type35SelectedDescriptors:'D0=16 -> A4 descriptor 0x081864; D0=20 -> A4 descriptor 0x081856',
  descriptorSemanticCorrection:'0x25C8 selects action descriptors, not direct code handlers. 0x247C consumes A4 as a descriptor stream.',
  descriptor247CExact:'0x247C MOVEA.L (A4)+,A6; 0x247E MOVE.L (A4)+,0x30(A0); 0x2482 MOVE.W (A4)+,D1. If D1 bit15 is set, 0x249E masks it with 0x7FFF, stores timer at enemy+0x34, and 0x24A6 loads an explicit next-descriptor pointer. Otherwise next descriptor is inline after the 10-byte record.',
  payloadCopyExact:'0x2490 stores A6 to enemy+0x12; 0x2494 LEA enemy+0x6C,A4; 0x2498 MOVE.W -(A6),(A4)+; 0x249A MOVE.L -(A6),(A4)+. Therefore the descriptor first long is a payload/frame end pointer, not an executable function pointer.',
  d0_20Descriptor:'0x81856: frameEnd=0x825D0, value30=0, rawTimer=0x8010 => timer 16, explicit next=0x817CC',
  d0_16Descriptor:'0x81864: frameEnd=0x825D0, value30=0, rawTimer=0xFFFF => timer 0x7FFF, explicit next=0x81864 self-loop',
  currentInference:'D0=20 is a 16-tick transitional descriptor; D0=16 is a long-hold/self-loop descriptor sharing the same frame/payload endpoint. This is structurally strong; exact attack/startup semantics still require descriptor-chain + live runtime correlation.',
  endToEndStructuralProofConfirmed:true,
  causalFrontier:'follow the D0=20 descriptor chain from 0x81856 -> 0x817CC and correlate live type35 enemy+0x12/+0x2C/+0x30/+0x34/+0x6C..+0x71 fingerprints with action2A/target transitions. Then classify which descriptor phase is attack startup/active/recovery for Future Danger.',
  nextScript:'wof_type35_descriptor_chain_runtime_v1.js',
  nextMarker:'=== TYPE35 DESCRIPTOR CHAIN RUNTIME V1 JSON ===',
  note:'Do not call 0x81856/0x81864 code handlers. Do not treat 0x825D0 as executable code. Do not restart selector search, Focus Multiroom, 44-edge scan, 0x0080F2, 0x11C26 bridge, broad +0x7E/+0x7C scans, or raw-even-address opcode sweeping.'
};
self.__WOF_RESUME_FRONTIER=current;
console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);
console.log('NEXT: descriptor-chain + live type35 fingerprint correlation.');
return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});