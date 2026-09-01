import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
function run(script) {
  const x = spawnSync(process.execPath, [path.join(here, script)], { cwd: here, env: process.env, encoding: 'utf8' });
  if (x.stdout) process.stdout.write(x.stdout);
  if (x.stderr) process.stderr.write(x.stderr);
  if (x.status !== 0) process.exit(x.status || 1);
}
run('selftest.mjs');
run('acceptance_adapter.mjs');
const selftest = JSON.parse(fs.readFileSync(path.join(here, 'selftest_result.json'), 'utf8'));
const resultPath = path.join(here, 'result.json');
const result = JSON.parse(fs.readFileSync(resultPath, 'utf8'));
result.selftest = { status: selftest.status, passCount: selftest.passCount, failCount: selftest.failCount };
result.status = selftest.status === 'PASS' && result.failCount === 0 ? 'PASS' : 'FAIL';
result.repositoryStatus = result.status === 'PASS' ? 'ALPHA TRANSPORT REFERENCE IMPLEMENTATION READY FOR INTEGRATION' : 'ALPHA TRANSPORT REFERENCE IMPLEMENTATION NOT READY';
fs.writeFileSync(resultPath, JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify({ status: result.status, selftest: result.selftest.status, contract: `${result.passCount}/${result.vectorCount}`, repositoryStatus: result.repositoryStatus }));
