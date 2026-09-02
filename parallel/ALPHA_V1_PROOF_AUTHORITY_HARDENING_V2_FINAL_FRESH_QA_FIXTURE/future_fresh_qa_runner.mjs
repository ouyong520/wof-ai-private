import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const argv=process.argv.slice(2),arg=n=>{const i=argv.indexOf(n);return i>=0?argv[i+1]:null};
const adapterPath=arg('--adapter');
const die=m=>{console.error('FRESH-QA FAIL-CLOSED — '+m);process.exit(2)};
if(!adapterPath)die('missing --adapter <QA-owned post-Hardening SUT adapter>');
const catalog=JSON.parse(fs.readFileSync(new URL('./fixture_catalog.json',import.meta.url),'utf8'));
const vectors=await import(new URL('./fixture_vectors.mjs',import.meta.url));
const adapter=await import(pathToFileURL(path.resolve(adapterPath)).href);
if(adapter.ADAPTER_SCHEMA!=='wof-alpha-v1-proof-authority-hardening-v2-qa-adapter-v1'||typeof adapter.runCase!=='function')die('adapter contract mismatch');
let passed=0;
for(const c of catalog.cases){
  let r;
  try{r=await adapter.runCase(Object.freeze(JSON.parse(JSON.stringify(c))),vectors)}catch(e){die(`${c.id} adapter threw: ${e?.stack||e}`)}
  if(!r||r.caseId!==c.id||r.expected!==c.expected)die(`${c.id} result identity/expected mismatch`);
  if(r.pass!==true)die(`${c.id} ${c.domain}: ${r.reason||'assertion failed'}`);
  if(!r.assertions||typeof r.assertions!=='object')die(`${c.id} missing assertions`);
  for(const a of c.asserts)if(r.assertions[a]!==true)die(`${c.id} assertion not proven: ${a}`);
  if(!Array.isArray(r.evidence)||r.evidence.length===0)die(`${c.id} missing independent evidence refs`);
  console.log(`PASS ${c.id} ${c.domain}`);passed++;
}
if(passed!==17)die(`case count ${passed}/17`);
console.log('PASS — 17/17 QA-OWNED FINAL FRESH-QA AUTHORITY CASES');
