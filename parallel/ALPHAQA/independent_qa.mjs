import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const root = new URL('../../', import.meta.url);
const alpha = new URL('product/alpha/', root);
const read = name => fs.readFileSync(new URL(name, alpha), 'utf8');

vm.runInThisContext(read('wof_alpha_core.js'), { filename: 'product/alpha/wof_alpha_core.js' });
const C = globalThis.WOFAlphaCore;

const results = [];
function test(id, severity, fn) {
  try {
    fn();
    results.push({ id, severity, status: 'PASS' });
  } catch (e) {
    results.push({ id, severity, status: 'FAIL', error: String(e?.message || e) });
  }
}

const mk = (o={}) => ({
  slot: 0,
  type: 1,
  target7E: 0,
  target: 'P1',
  state99: 0,
  action2A: 0,
  b2B: 0,
  body: 1,
  attack: 0,
  frameEnd: 1,
  next: 1,
  value30: 0,
  timer34: 0,
  payload6C: 0,
  enemyX: 100,
  targetX: 120,
  ...o
});

const neutral = (type=1, slot=0) => mk({
  slot,
  type,
  state99: 9,
  action2A: 9,
  b2B: 9,
  body: 9,
  frameEnd: 0x111,
  next: 0x222,
  value30: 9,
  timer34: 9,
  payload6C: 9
});

const f2 = (b, slot=0, target7E=0, targetX=120) => mk({
  slot,
  type: 20,
  target7E,
  target: target7E===0?'P1':target7E===4?'P2':target7E===8?'P3':null,
  targetX,
  state99: 2,
  action2A: 4,
  b2B: b,
  body: 0,
  frameEnd: 0x839c4,
  next: 0x82b0a,
  value30: 0x100000,
  timer34: 20,
  payload6C: 0
});

const f3 = (slot=0) => mk({
  slot,
  type: 33,
  state99: 2,
  action2A: 4,
  b2B: 2,
  body: 2872,
  frameEnd: 0x867ba,
  next: 0x85ece,
  value30: 0x100000,
  timer34: 6,
  payload6C: 2784
});

const f5 = (slot=0, target7E=0, targetX=120) => mk({
  slot,
  type: 18,
  target7E,
  target: target7E===0?'P1':target7E===4?'P2':target7E===8?'P3':null,
  targetX,
  state99: 2,
  action2A: 2,
  b2B: 4,
  body: 7512,
  frameEnd: 0x8bbb2,
  next: 0x8b290,
  value30: 0x180001,
  timer34: 4,
  payload6C: 0
});

const candidate4728 = () => mk({
  type: 18,
  state99: 0,
  action2A: 4,
  b2B: 2,
  body: 4728,
  frameEnd: 0x8b660,
  next: 0x8b204,
  value30: 0xffff,
  timer34: 1,
  payload6C: 4736
});

// Frozen rule inventory: independent of product regression's aggregate replay.
test('RULE-INVENTORY', 'P0', () => {
  const ids = C.RULES.map(r => r.id);
  assert.deepEqual(ids, [
    'T16_B4_DANGER_40',
    'T20_5136_B0_TO_B255_1250',
    'D867BA_3232_TM6_220',
    'D8811E_3232_TM6_135',
    'T18_5440_CYCLE_BODY7512_TM4_LEVEL_90',
    'T18_5424_CYCLE_BODY7520_TM4_LEVEL_90'
  ]);
  const t16 = C.RULES.find(r => r.id === 'T16_B4_DANGER_40');
  assert.equal(t16.attackSpecific, false);
  assert.equal(t16.attack, null);
  assert.equal(ids.some(x => /4704|4728/.test(x)), false);
});

test('BODY4728-EXCLUDED', 'P0', () => {
  const e = C.createEngine();
  const s = e.step([candidate4728()], 0);
  assert.equal(s.warnings.length, 0);
});

// ALPHAQA-001: a build guard must not identify a declared ROM/revision from layout-only facts.
test('IDENTITY-LOOKALIKE-FAIL-CLOSED', 'P0', () => {
  const q = C.validateIdentityProbe({
    moduleOk: true,
    ramBase: 123,
    ramWithinHeap: true,
    selfIndexes: [0,4,8]
  });
  assert.equal(q.ok, false, 'layout-only probe must not positively identify World 921002 / wofr1');
});

// Baseline retarget/unknown behavior should remain correct after fixes.
test('RETARGET-LIVE-UNKNOWN-SILENT', 'P0', () => {
  const e = C.createEngine();
  e.step([{...f3(), timer34:5}], 0);
  let s = e.step([f3()], 10);
  assert.equal(s.warnings.length, 1);
  assert.equal(s.warnings[0].target, 'P1');
  s = e.step([{...f3(), target7E:8, target:'P3', targetX:80}], 20);
  assert.equal(s.warnings.length, 1);
  assert.equal(s.warnings[0].target, 'P3');
  assert.equal(s.warnings[0].threatSide, 'RIGHT');
  s = e.step([{...f3(), target7E:2, target:null, targetX:null}], 30);
  assert.equal(s.warnings.length, 0);
});

// Slot-gone and type-changed cleanup are expected to pass.
test('SLOT-GONE-CLEARS', 'P1', () => {
  const e = C.createEngine();
  e.step([f2(0)], 0);
  let s = e.step([f2(255)], 10);
  assert.equal(s.warnings.length, 1);
  s = e.step([], 20);
  assert.equal(s.warnings.length, 0);
});

test('TYPE-CHANGE-CLEARS', 'P1', () => {
  const e = C.createEngine();
  e.step([f2(0)], 0);
  let s = e.step([f2(255)], 10);
  assert.equal(s.warnings.length, 1);
  s = e.step([neutral(21)], 20);
  assert.equal(s.warnings.length, 0);
});

// ALPHAQA-002: same type / same slot is not sufficient proof of same enemy episode.
test('SAME-TYPE-REPLACEMENT-CLEARS', 'P1', () => {
  const e = C.createEngine();
  e.step([f2(0)], 0);
  let s = e.step([f2(255)], 10);
  assert.equal(s.warnings.length, 1, 'fixture must arm T20');
  const replacement = neutral(20);
  replacement.target7E = 8;
  replacement.target = 'P3';
  replacement.enemyX = 50;
  replacement.targetX = 90;
  s = e.step([replacement], 20);
  assert.equal(s.warnings.length, 0, 'a replacement episode must not inherit the prior enemy watch');
});

// ALPHAQA-003: prove core can produce multiple warnings, then reject HUD code that silently selects only [0].
test('MULTI-THREAT-NOT-SILENTLY-DROPPED', 'P1', () => {
  const e = C.createEngine();
  const s = e.step([
    f5(0, 0, 120),
    f5(1, 4, 70)
  ], 0);
  assert.equal(s.warnings.length, 2, 'core fixture must contain two simultaneous valid warnings');
  const hud = read('wof_alpha_hud.js');
  assert.equal(/lastMsg\?\.warnings\?\.\[0\]/.test(hud), false,
    'HUD must not silently render only warnings[0] when more warnings are active');
});

// Current source-level read-only audit is stronger than product regression's HEAPU-only assignment regex.
test('READ-ONLY-STATIC', 'P0', () => {
  for (const name of ['wof_alpha_core.js','wof_alpha_loader.js','wof_alpha_hud.js']) {
    const src = read(name);
    assert.equal(/(?:HEAPU(?:8|16|32)|\bM)\s*\[[^\]]+\]\s*(?:=|\+=|-=|\*=|\/=|\+\+|--)/.test(src), false,
      name+' contains a direct heap/heap-alias assignment');
    assert.equal(/(?:HEAPU(?:8|16|32)|\bM)\s*\.set\s*\(/.test(src), false,
      name+' contains a heap/heap-alias .set write');
    assert.equal(/new\s+KeyboardEvent|dispatchEvent\s*\(|\.click\s*\(/.test(src), false,
      name+' contains gameplay input injection');
  }
});

// ALPHAQA-004: current documentation still requires manually selecting the live worker console.
test('NORMAL-USER-LOAD-PATH', 'P1', () => {
  const readme = read('README.md');
  assert.equal(/live `gstyphoon\.js` Worker console/i.test(readme), false,
    'supported user path must not require researcher-level manual Worker-console selection');
});

const blockers = results.filter(x => x.status === 'FAIL' && (x.severity === 'P0' || x.severity === 'P1'));
const out = {
  suite: 'wof-alpha-independent-qa-v1',
  artifact: C.VERSION,
  qaStatus: blockers.length ? 'BLOCKED' : 'PASS',
  blockers,
  results
};

console.log(JSON.stringify(out, null, 2));
if (blockers.length) process.exitCode = 1;
