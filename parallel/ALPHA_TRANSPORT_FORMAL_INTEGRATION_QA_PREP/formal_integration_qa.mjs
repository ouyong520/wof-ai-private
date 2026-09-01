import { readFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { strict as assert } from 'node:assert';

const here = dirname(fileURLToPath(import.meta.url));
const expectedPath = resolve(here, 'expected_outcomes.json');
const expected = JSON.parse(await readFile(expectedPath, 'utf8'));
const args = process.argv.slice(2);
const argValue = name => {
  const i = args.indexOf(name);
  return i >= 0 ? args[i + 1] : null;
};
const has = name => args.includes(name);

function get(obj, path) {
  return path.split('.').reduce((v, key) => (v == null ? undefined : v[key]), obj);
}

function validateObservation(spec, observation) {
  const failures = [];
  for (const [path, value] of Object.entries(spec.success || {})) {
    try { assert.deepEqual(get(observation, path), value); }
    catch { failures.push(`${path}: expected ${JSON.stringify(value)}, got ${JSON.stringify(get(observation, path))}`); }
  }
  for (const [path, needles] of Object.entries(spec.contains || {})) {
    const actual = get(observation, path);
    for (const needle of needles) {
      if (typeof actual !== 'string' || !actual.includes(needle)) failures.push(`${path}: expected to contain ${JSON.stringify(needle)}, got ${JSON.stringify(actual)}`);
    }
  }
  for (const rule of spec.forbidden || []) {
    const actual = get(observation, rule.path);
    if ('equals' in rule && Object.is(actual, rule.equals)) failures.push(`${rule.path}: forbidden value ${JSON.stringify(rule.equals)}`);
    if ('gt' in rule && typeof actual === 'number' && actual > rule.gt) failures.push(`${rule.path}: forbidden > ${rule.gt}, got ${actual}`);
  }
  return failures;
}

function selftestObservation(spec) {
  const out = {};
  const set = (path, value) => {
    const parts = path.split('.');
    let cur = out;
    for (let i = 0; i < parts.length - 1; i++) cur = cur[parts[i]] ||= {};
    cur[parts.at(-1)] = value;
  };
  for (const [path, value] of Object.entries(spec.success || {})) set(path, value);
  for (const [path, needles] of Object.entries(spec.contains || {})) set(path, needles.join(' / '));
  return out;
}

async function loadDriver(sutPath) {
  if (!sutPath) return { status: 'WAITING_SUT', reason: 'No --sut module was supplied.' };
  const mod = await import(pathToFileURL(resolve(process.cwd(), sutPath)).href);
  const seam = mod[expected.sutSeam.export];
  if (!seam || seam.schema !== expected.sutSeam.schema || typeof seam.createScenarioDriver !== 'function') {
    return { status: 'SEAM_DRIFT', reason: `Expected export ${expected.sutSeam.export} with schema ${expected.sutSeam.schema}.` };
  }
  const driver = await seam.createScenarioDriver();
  for (const fn of expected.sutSeam.driverFunctions) {
    if (typeof driver?.[fn] !== 'function') return { status: 'SEAM_DRIFT', reason: `Scenario driver missing function ${fn}().` };
  }
  return { status: 'READY', driver, seam };
}

async function runWithDriver(driver, mode) {
  const results = [];
  for (const spec of expected.cases) {
    let observation;
    let failures = [];
    try {
      await driver.reset();
      observation = await driver.runScenario(structuredClone(spec));
      failures = validateObservation(spec, observation);
    } catch (error) {
      failures = [String(error?.stack || error)];
    }
    results.push({ id: spec.id, requirement: spec.requirement, status: failures.length ? 'FAIL' : 'PASS', failures, observation });
  }
  const passCount = results.filter(r => r.status === 'PASS').length;
  const failCount = results.length - passCount;
  return {
    schema: 'wof-alpha-formal-integration-qa-run-v1',
    mode,
    status: failCount === 0 ? (mode === 'SELFTEST' ? 'SELFTEST_PASS' : 'PASS') : 'FAIL',
    caseCount: results.length,
    passCount,
    failCount,
    results
  };
}

if (has('--selftest')) {
  const driver = { async reset() {}, async runScenario(spec) { return selftestObservation(spec); } };
  const report = await runWithDriver(driver, 'SELFTEST');
  const stale = expected.cases.find(c => c.id === 'FIQA-03-old-unresolved-after-rebind');
  const bad = selftestObservation(stale);
  bad.oldCompletion.published = true;
  const negativeControlFailures = validateObservation(stale, bad);
  report.negativeControl = {
    injectedViolation: 'oldCompletion.published=true',
    detected: negativeControlFailures.length > 0,
    failures: negativeControlFailures
  };
  if (!report.negativeControl.detected) {
    report.status = 'FAIL';
    report.failCount += 1;
  }
  console.log(JSON.stringify(report, null, 2));
  if (report.status !== 'SELFTEST_PASS') process.exitCode = 1;
} else {
  const sutPath = argValue('--sut');
  let loaded;
  try { loaded = await loadDriver(sutPath); }
  catch (error) { loaded = { status: 'SUT_LOAD_ERROR', reason: String(error?.stack || error) }; }
  if (loaded.status !== 'READY') {
    console.log(JSON.stringify({
      schema: 'wof-alpha-formal-integration-qa-run-v1',
      mode: 'FORMAL_SUT',
      status: loaded.status,
      reason: loaded.reason,
      passClaimed: false,
      expectedSeam: expected.sutSeam
    }, null, 2));
    process.exitCode = loaded.status === 'WAITING_SUT' ? 3 : 4;
  } else {
    const report = await runWithDriver(loaded.driver, 'FORMAL_SUT');
    report.passClaimed = report.status === 'PASS';
    console.log(JSON.stringify(report, null, 2));
    if (report.status !== 'PASS') process.exitCode = 1;
  }
}
