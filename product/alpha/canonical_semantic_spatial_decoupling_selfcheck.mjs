import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const adapter=require('./wof_alpha_field_adapter.js');

const epoch='0123456789abcdef0123456789abcdef';
const rows=[
  {slot:0,type:1,target7E:0,enemyWorldX:12,enemyY:34,enemyZ:5},
  {slot:1,type:2,target7E:4,enemyWorldX:22,enemyY:44,enemyZ:6},
  {slot:2,type:3,target7E:8,enemyWorldX:32,enemyY:54,enemyZ:7},
  {slot:3,type:4,target7E:12,enemyWorldX:42,enemyY:64,enemyZ:8}
];
const markers=adapter.buildEnemyTargetSemanticMarkers(rows,1234,epoch);
assert.deepEqual(markers.map(m=>[m.slot,m.target7E,m.target]),[
  [0,0,'P1'],[1,4,'P2'],[2,8,'P3']
]);
for(const marker of markers){
  for(const forbidden of ['enemyWorldX','enemyX','enemyY','enemyZ','x','y','head','projection']){
    assert.equal(Object.hasOwn(marker,forbidden),false,forbidden);
  }
  assert.equal(marker.epoch,epoch);
  assert.equal(marker.projectionEpoch,epoch);
  assert.equal(marker.confidence,1);
}
assert.equal(adapter.targetForField(0),'P1');
assert.equal(adapter.targetForField(4),'P2');
assert.equal(adapter.targetForField(8),'P3');
assert.equal(adapter.targetForField(12),null);
console.log('P15 SEMANTIC/SPATIAL DECOUPLING PASS');
