export const ROM='5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62';
export const HEX={sessionA:'1'.repeat(32),sessionB:'2'.repeat(32),runtimeA:'a'.repeat(32),runtimeB:'b'.repeat(32),pairNonceA:'c'.repeat(32),pairNonceB:'d'.repeat(32)};
export const authorityA=Object.freeze({session:HEX.sessionA,workerGeneration:7,runtimeEpoch:HEX.runtimeA,pairGeneration:11,pairNonce:HEX.pairNonceA,launcherIdentitySha:ROM,channel:'WOF_ALPHA_'+HEX.sessionA});
export const authorityMutations=Object.freeze([
  {...authorityA,workerGeneration:8},
  {...authorityA,runtimeEpoch:HEX.runtimeB},
  {...authorityA,pairGeneration:12},
  {...authorityA,pairNonce:HEX.pairNonceB},
  {...authorityA,session:HEX.sessionB,channel:'WOF_ALPHA_'+HEX.sessionB}
]);
export const malformedEpochs=Object.freeze([null,undefined,0,1,true,false,{},[],new String(HEX.runtimeA),{toString(){return HEX.runtimeA}},NaN,Infinity,-Infinity]);
export const malformedWarningSampleAt=Object.freeze([null,undefined,'1000',new Number(1000),{valueOf(){return 1000}},NaN,Infinity,-Infinity,{},[]]);
export const malformedTargets=Object.freeze(['0','4','8',new Number(0),new Number(4),new Number(8),{valueOf(){return 4}},[0],[4],[8],true,false,NaN,Infinity,-Infinity,0.5,4.5,8.5,null,undefined]);
export const lifecycle=Object.freeze({
  playerOld:{id:'P1@g41',generation:41},playerNew:{id:'P1@g42',generation:42},
  enemyOld:{slot:3,type:18,id:'enemy-slot-3@g91',generation:91},
  enemyNew:{slot:3,type:18,id:'enemy-slot-3@g92',generation:92}
});
export const mapping=Object.freeze({current:'db:384x224|map-v9|epoch-a',stale:'db:384x224|map-v8|epoch-old'});
