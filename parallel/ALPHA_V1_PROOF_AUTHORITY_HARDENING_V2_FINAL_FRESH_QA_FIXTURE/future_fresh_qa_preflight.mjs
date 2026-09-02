import fs from 'node:fs';
import {spawnSync} from 'node:child_process';
const a=process.argv.slice(2),arg=n=>{const i=a.indexOf(n);return i>=0?a[i+1]:null};
const result=arg('--hardening-result'),manifestPath=arg('--manifest'),fixed=arg('--fixed-commit');
const die=m=>{console.error('FAIL-CLOSED — '+m);process.exit(2)};
if(!result||!manifestPath||!/^[0-9a-f]{40}$/i.test(fixed||''))die('required --hardening-result/--manifest/--fixed-commit');
if(!fs.existsSync(result)||!fs.existsSync(manifestPath))die('required fixed files missing');
const rt=fs.readFileSync(result,'utf8');
if(!/COMPLETE\s+—\s+ALPHA V1 PROOF-AUTHORITY HARDENING INTEGRATION FIX V4 RECOVERY V5\s+—\s+AUTHORITY-V2 RUNNABLE PATH \/ TRUST ROOT \/ LIFECYCLE \/ MANIFEST COHERENT\s+—\s+READY FOR THE ONE FINAL FRESH QA/i.test(rt))die('Recovery V5 authoritative COMPLETE marker absent');
const cat=JSON.parse(fs.readFileSync(new URL('./fixture_catalog.json',import.meta.url),'utf8'));
if(cat.currentSutVerdictIssued!==false||cat.futureExecution.requiresExactFixedBlobPins!==true)die('fixture contract mutated');
const m=JSON.parse(fs.readFileSync(manifestPath,'utf8'));
const groups=['productBlobs','proofToolBlobs','authorityRootBlobs','attestationBlobs'];
const entries=groups.flatMap(k=>Object.values(m[k]||{})).filter(x=>x?.path&&x?.sha);
const required=['proof_core.js','wof_alpha_v1_dual_live_proof_top.js','wof_alpha_v1_dual_live_proof_worker.js','wof_alpha_v1_dual_live_proof.js','wof_alpha_player_head_warning.js','wof_alpha_enemy_target_labels.js','wof_alpha_real_worker.js'];
for(const r of required)if(!entries.some(x=>x.path.endsWith(r)))die('manifest missing required pin '+r);
for(const e of entries){
  if(!/^[0-9a-f]{40}$/i.test(e.sha))die('bad blob sha '+e.path);
  const q=spawnSync('git',['hash-object','--',e.path],{encoding:'utf8'});
  if(q.status!==0)die('cannot hash '+e.path);
  if(q.stdout.trim()!==e.sha)die('blob mismatch '+e.path);
}
const head=spawnSync('git',['rev-parse','HEAD'],{encoding:'utf8'});
if(head.status!==0||head.stdout.trim()!==fixed)die('working tree HEAD is not exact fixed commit');
console.log('PRECONDITION PASS — exact post-Hardening fixed tree pinned — READY TO EXECUTE 17 QA-OWNED CASES — no QA verdict emitted by this preflight');
