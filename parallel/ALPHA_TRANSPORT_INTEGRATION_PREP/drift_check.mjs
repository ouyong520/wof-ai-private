import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, '../..');
const baselinePath = path.join(here, 'DRIFT_BASELINE.json');

export function gitBlobSha(buffer) {
  const body = Buffer.isBuffer(buffer) ? buffer : Buffer.from(buffer);
  const header = Buffer.from(`blob ${body.length}\0`);
  return crypto.createHash('sha1').update(header).update(body).digest('hex');
}

export function verifyDriftBaseline() {
  const baseline = JSON.parse(fs.readFileSync(baselinePath, 'utf8'));
  const rows = [];
  for (const [relativePath, expected] of Object.entries(baseline.files || {})) {
    const absolutePath = path.join(repoRoot, relativePath);
    if (!fs.existsSync(absolutePath)) {
      rows.push({ path: relativePath, expected, actual: null, ok: false, reason: 'missing' });
      continue;
    }
    const actual = gitBlobSha(fs.readFileSync(absolutePath));
    rows.push({ path: relativePath, expected, actual, ok: actual === expected, reason: actual === expected ? null : 'blob-drift' });
  }
  return {
    ok: rows.every(row => row.ok),
    baselineHead: baseline.capturedAtHead,
    checked: rows.length,
    drift: rows.filter(row => !row.ok),
    rows
  };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const result = verifyDriftBaseline();
  console.log(JSON.stringify({ ok: result.ok, baselineHead: result.baselineHead, checked: result.checked, drift: result.drift }, null, 2));
  if (!result.ok) process.exitCode = 1;
}
