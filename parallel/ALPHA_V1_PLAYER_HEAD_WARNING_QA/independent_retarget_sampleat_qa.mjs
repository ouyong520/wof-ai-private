import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const A=require('../../product/alpha/wof_alpha_player_head_warning.js');
const E='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa';
const projection=(sampleAt=1000)=>({schema:A.PROFILE_SCHEMA,status:'PROVED',proofId:'fresh-qa-proof-v1',version:'fresh-qa-proj-v1',projectionKind:A.PROJECTION_KIND,source:'FRESH_QA_SYNTHETIC_NOT_BROWSER_PROOF',epoch:E,projectionEpoch:E,sampleAt,confidence:1,nativeWidth:384,nativeHeight:224,cameraX:0,worldXScale:1,xBias:80,floorYScale:1,zScale:-1,yBias:120,headClearanceNative:24,validationBounds:{minX:0,maxX:383,minY:0,maxY:223}});
const db=(sampleAt=1010)=>({width:768,height:448,contentRect:{x:0,y:0,width:768,height:448},sampleAt,confidence:1,epoch:E,projectionEpoch:E,mappingVersion:'768:448:0:0:768:448',fullscreen:false});
const player=(sampleAt=1000)=>({present:true,x:180,y:50,z:0,sampleAt,confidence:1,epoch:E,projectionEpoch:E});
const warning={target:'P2',slot:0,ruleId:'FRESH_QA',threatSide:'LEFT',attack:5440};
const run=value=>A.buildPlan({warnings:[warning],players:{P2:player(1000)},projection:projection(1000),drawingBufferState:db(1010),nowMs:1020,warningEpoch:E,warningSampleAt:value});
const cases=[];
function expect(name,fn){try{cases.push({name,pass:true,detail:fn()});}catch(e){cases.push({name,pass:false,error:String(e?.message||e)});}}
function fixed(p){if(p.anchored.length!==0||p.fixed.length!==1)throw new Error(`expected fixed fallback, anchored=${p.anchored.length}, fixed=${p.fixed.length}`);return p.fixed[0].reason;}
expect('control: finite retarget sampleAt rejects older spatial',()=>{const p=run(1010);const r=fixed(p);if(r!=='SPATIAL_BEFORE_WARNING_SAMPLE')throw new Error(r);return r;});
expect('control: malformed warningEpoch fails closed',()=>{const p=A.buildPlan({warnings:[warning],players:{P2:player()},projection:projection(),drawingBufferState:db(),nowMs:1020,warningEpoch:'bad',warningSampleAt:1010});return fixed(p);});
expect('control: stale player still fails closed',()=>{const p=A.buildPlan({warnings:[warning],players:{P2:player(900)},projection:projection(1000),drawingBufferState:db(),nowMs:1020,warningEpoch:E,warningSampleAt:890});return fixed(p);});
expect('malformed warningSampleAt: missing must fail closed',()=>{const p=A.buildPlan({warnings:[warning],players:{P2:player(1000)},projection:projection(1000),drawingBufferState:db(1010),nowMs:1020,warningEpoch:E});return fixed(p);});
for(const [name,value] of [['null',null],['numeric-string','1010'],['boxed-number',new Number(1010)],['NaN',NaN],['Infinity',Infinity]]){
  expect(`malformed warningSampleAt: ${name} must fail closed`,()=>fixed(run(value)));
}
const passed=cases.filter(x=>x.pass).length,failed=cases.length-passed;
console.log(JSON.stringify({status:failed?'BLOCKED':'PASS',fixture:'FRESH_INDEPENDENT_RETARGET_SAMPLEAT_REPOSITORY_QA_NOT_BROWSER_WOF_PROOF',helperBlob:'43b54e361f9bffcc4be278549692d0fb229aae7e',passed,failed,total:cases.length,failures:cases.filter(x=>!x.pass),cases},null,2));
process.exitCode=failed?1:0;
