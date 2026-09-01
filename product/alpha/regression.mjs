import fs from 'node:fs';import vm from 'node:vm';import assert from 'node:assert/strict';
const here=new URL('.',import.meta.url);vm.runInThisContext(fs.readFileSync(new URL('wof_alpha_core.js',here),'utf8'),{filename:'wof_alpha_core.js'});const C=globalThis.WOFAlphaCore;
const mk=(o={})=>({slot:0,type:1,target7E:0,target:'P1',state99:0,action2A:0,b2B:0,body:1,attack:0,frameEnd:1,next:1,value30:0,timer34:0,payload6C:0,enemyX:100,targetX:120,...o});
const neutral=(type=1)=>mk({type,state99:9,action2A:9,b2B:9,body:9,frameEnd:0x111,next:0x222,value30:9,timer34:9,payload6C:9});
const f1=()=>mk({type:16,state99:0,action2A:4,b2B:4,body:4856,frameEnd:0x851ae,next:0x84c44,value30:0xffff,timer34:1,payload6C:0});
const f1prev=()=>({...f1(),b2B:2});
const f2=(b)=>mk({type:20,state99:2,action2A:4,b2B:b,body:0,frameEnd:0x839c4,next:0x82b0a,value30:0x100000,timer34:20,payload6C:0});
const f3=()=>mk({type:33,state99:2,action2A:4,b2B:2,body:2872,frameEnd:0x867ba,next:0x85ece,value30:0x100000,timer34:6,payload6C:2784});
const f4=()=>mk({type:34,state99:4,action2A:4,b2B:2,body:2872,frameEnd:0x8811e,next:0x879e2,value30:0x100000,timer34:6,payload6C:2784});
const f5=()=>mk({type:18,state99:2,action2A:2,b2B:4,body:7512,frameEnd:0x8bbb2,next:0x8b290,value30:0x180001,timer34:4,payload6C:0});
const f6=()=>mk({type:18,state99:2,action2A:2,b2B:4,body:7520,frameEnd:0x8bbde,next:0x8b2a4,value30:0x180001,timer34:4,payload6C:0});
const active=(s,a)=>({...s,attack:a});
const exactCandidate=()=>mk({type:18,state99:0,action2A:4,b2B:2,body:4728,frameEnd:0x8b660,next:0x8b204,value30:0xffff,timer34:1,payload6C:4736});
assert.equal(C.validateIdentityProbe({moduleOk:true,ramBase:123,ramWithinHeap:true,selfIndexes:[0,4,8]}).ok,true);
assert.equal(C.validateIdentityProbe({moduleOk:true,ramBase:123,ramWithinHeap:true,selfIndexes:[0,8,4]}).ok,false);
{
 const e=C.createEngine();e.step([f1prev()],0);let s=e.step([f1()],10);assert.equal(s.warnings.length,1);assert.equal(s.warnings[0].attackSpecific,false);assert.equal(s.warnings[0].target,'P1');assert.equal(s.warnings[0].threatSide,'LEFT');s=e.step([active(f1(),4840)],20);assert.equal(s.warnings.length,0);assert.deepEqual(e.diagnostics().rules.T16_B4_DANGER_40.attackDistribution,{'4840':1});
}
{
 const e=C.createEngine();e.step([f2(0)],0);let s=e.step([f2(255)],10);assert.equal(s.warnings[0].attack,5136);e.step([active(f2(255),5136)],100);assert.equal(e.diagnostics().rules.T20_5136_B0_TO_B255_1250.resolved,1);
}
{
 const e=C.createEngine();e.step([{...f3(),timer34:5}],0);let s=e.step([f3()],10);assert.equal(s.warnings[0].attack,3232);e.step([active(f3(),3232)],100);e.step([{...f4(),timer34:5}],120);s=e.step([f4()],130);assert.equal(s.warnings[0].attack,3232);
}
{
 const e=C.createEngine();let s=e.step([f5()],0);assert.equal(s.warnings.length,1);s=e.step([f5()],10);assert.equal(e.diagnostics().rules.T18_5440_CYCLE_BODY7512_TM4_LEVEL_90.signals,1);e.step([active(f5(),5440)],60);e.step([f5()],100);assert.equal(e.diagnostics().rules.T18_5440_CYCLE_BODY7512_TM4_LEVEL_90.signals,2);
}
{
 const e=C.createEngine();let s=e.step([f6()],0);assert.equal(s.warnings[0].attack,5424);e.step([active(f6(),5424)],60);
}
{
 const e=C.createEngine();let s=e.step([exactCandidate()],0);assert.equal(s.warnings.length,0,'excluded BODY4728 candidate must stay silent');
}
{
 const e=C.createEngine();e.step([{...f3(),timer34:5}],0);let s=e.step([f3()],10);assert.equal(s.warnings[0].target,'P1');assert.equal(s.warnings[0].threatSide,'LEFT');s=e.step([{...f3(),target7E:8,target:'P3',targetX:80}],20);assert.equal(s.warnings[0].target,'P3');assert.equal(s.warnings[0].threatSide,'RIGHT');s=e.step([{...f3(),target7E:2,target:null,targetX:null}],30);assert.equal(s.warnings.length,0,'UNKNOWN target must be silent');
}
{
 const e=C.createEngine();e.step([f2(0)],0);let s=e.step([f2(255)],10);assert.equal(s.warnings.length,1);s=e.step([f2(255)],1300);assert.equal(s.warnings.length,0,'stale warning must expire');assert.equal(e.diagnostics().rules.T20_5136_B0_TO_B255_1250.runtimeExpiredWithoutActive,1);
}
function replayRule(ruleId,count,buildPrev,buildSignal,attackCode,typeChooser){
 const e=aggregateEngine;for(let i=0;i<count;i++){const t=clock;const p=buildPrev(i),s=buildSignal(i);e.step([p],t);e.step([s],t+5);const a=active(s,attackCode(i));if(typeChooser)a.type=typeChooser(i);e.step([a],t+15);clock+=30;}
}
const aggregateEngine=C.createEngine();let clock=0;
replayRule('T16_B4_DANGER_40',98,()=>f1prev(),()=>f1(),i=>i===97?4840:6432);
replayRule('T20_5136_B0_TO_B255_1250',5,()=>f2(0),()=>f2(255),()=>5136);
replayRule('D867BA_3232_TM6_220',10,i=>({...f3(),type:i<8?33:9,timer34:5}),i=>({...f3(),type:i<8?33:9}),()=>3232,i=>i<8?33:9);
replayRule('D8811E_3232_TM6_135',22,i=>({...f4(),type:i<15?34:11,timer34:5}),i=>({...f4(),type:i<15?34:11}),()=>3232,i=>i<15?34:11);
replayRule('T18_5440_CYCLE_BODY7512_TM4_LEVEL_90',4,()=>active(neutral(18),5440),()=>f5(),()=>5440);
replayRule('T18_5424_CYCLE_BODY7520_TM4_LEVEL_90',4,()=>active(neutral(18),5424),()=>f6(),()=>5424);
const d=aggregateEngine.diagnostics(),expected={T16_B4_DANGER_40:98,T20_5136_B0_TO_B255_1250:5,D867BA_3232_TM6_220:10,D8811E_3232_TM6_135:22,T18_5440_CYCLE_BODY7512_TM4_LEVEL_90:4,T18_5424_CYCLE_BODY7520_TM4_LEVEL_90:4};for(const [id,n] of Object.entries(expected)){assert.equal(d.rules[id].signals,n,id+' signal count');assert.equal(d.rules[id].resolved,n,id+' resolved count');assert.equal(d.rules[id].runtimeExpiredWithoutActive,0,id+' hard-miss equivalent');}
assert.deepEqual(d.rules.T16_B4_DANGER_40.attackDistribution,{'4840':1,'6432':97});assert.deepEqual(d.rules.T20_5136_B0_TO_B255_1250.attackDistribution,{'5136':5});assert.deepEqual(d.rules.D867BA_3232_TM6_220.attackDistribution,{'3232':10});assert.deepEqual(d.rules.D8811E_3232_TM6_135.attackDistribution,{'3232':22});assert.deepEqual(d.rules.T18_5440_CYCLE_BODY7512_TM4_LEVEL_90.attackDistribution,{'5440':4});assert.deepEqual(d.rules.T18_5424_CYCLE_BODY7520_TM4_LEVEL_90.attackDistribution,{'5424':4});
const files=['wof_alpha_core.js','wof_alpha_loader.js','wof_alpha_hud.js'].map(n=>[n,fs.readFileSync(new URL(n,here),'utf8')]);for(const [name,src] of files){assert.equal(/HEAPU(?:8|16|32)\s*\[[^\]]+\]\s*=/.test(src),false,name+' must not write HEAP');assert.equal(/new\s+KeyboardEvent|dispatchEvent\s*\(|\.click\s*\(/.test(src),false,name+' must not inject gameplay input');}
const hud=files.find(x=>x[0]==='wof_alpha_hud.js')[1];assert.match(hud,/function snapGL\(/);assert.match(hud,/function restoreGL\(/);assert.match(hud,/window\.__WOF_GL_HOOK/);
const result={artifact:'wof-alpha-rc1',tests:'PASS',productionFixtureSignals:98+5+10+22+4+4,productionFixtureResolved:143,hardMissEquivalent:0,excludedCandidateSilent:true,retargetLive:true,unknownSilent:true,staleCleanup:true,readOnlyStaticAudit:true,noInputInjectionStaticAudit:true,glStateRestoreStaticAudit:true,perRule:d.rules};console.log(JSON.stringify(result,null,2));
