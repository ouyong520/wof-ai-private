from __future__ import annotations
import argparse, hashlib, json, os, socket, subprocess, sys, tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Callable
from urllib.parse import urlparse

class HandoffBlocked(RuntimeError): pass
SRC='82b0b09ecd902f502ae5509bcb3ee5a713f43fee'
META='107850cb8409dd3f2f1135022375114f96469035'
P43='parallel/OWNER_DIAGNOSTIC/WOF_ALPHA_P43_BOUNDED_DIAGNOSTIC.cmd'
PTR='parallel/OWNER_ONECLICK/CANDIDATES/P38_ACCEPTED_REPAIR_INTEGRATED_POINTER.json'
PROV='parallel/OWNER_ONECLICK/CANDIDATES/P38_ACCEPTED_REPAIR_INTEGRATED_PROVENANCE.json'
PERMIT='parallel/OWNER_DIAGNOSTIC/P49_OWNER_WINDOWS_ONE_RUN_PERMIT.json'
RECEIPT='P43_DIAGNOSTIC_RECEIPT.json'; OUTMARK='P49_RUN_STARTED.json'; IMPORT='P49_ONE_RUN_HANDOFF_IMPORT.json'

def canon(v): return (json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode()
def sha(b): return hashlib.sha256(b).hexdigest()
def blob(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def load(p):
    try: v=json.loads(p.read_text(encoding='utf-8-sig'))
    except Exception as e: raise HandoffBlocked(f'INVALID_JSON:{p}:{e}') from e
    if not isinstance(v,dict): raise HandoffBlocked(f'JSON_ROOT_NOT_OBJECT:{p}')
    return v

def git(repo,*a):
    cp=subprocess.run(['git',*a],cwd=repo,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
    if cp.returncode: raise HandoffBlocked(f"GIT_FAILED:{' '.join(a)}:{cp.stderr.strip() or cp.stdout.strip()}")
    return cp.stdout.strip()

def pin(repo,rel,expect):
    p=repo/rel
    if not p.is_file(): raise HandoffBlocked(f'AUTHORITY_FILE_MISSING:{rel}')
    got=blob(p.read_bytes())
    if got!=expect: raise HandoffBlocked(f'AUTHORITY_FILE_STALE:{rel}:{got}')

def budget(r,c,s):
    for n,v in [('P48_RESULT',r),('P48_CANONICAL',c),('P48_STAGE',s)]:
        if v.get('runStarted') is not False: raise HandoffBlocked(f'{n}_RUN_STARTED')
        if v.get('runBudgetConsumed') is not False: raise HandoffBlocked(f'{n}_BUDGET_CONSUMED')
        if v.get('remainingRunBudget')!=1: raise HandoffBlocked(f'{n}_REMAINING_BUDGET_NOT_ONE')
    if r.get('retryAttempted') is not False: raise HandoffBlocked('P48_RETRY_ALREADY_ATTEMPTED')

def permit_id(p):
    if p.get('schema')!='wof-alpha-p49-one-run-permit-v1' or p.get('version')!=1: raise HandoffBlocked('PERMIT_SCHEMA_MISMATCH')
    b=p.get('identityBinding')
    if not isinstance(b,dict): raise HandoffBlocked('PERMIT_BINDING_MISSING')
    ident=sha(canon(b))
    if p.get('permitIdentity')!=ident: raise HandoffBlocked('PERMIT_IDENTITY_MISMATCH')
    if b.get('remainingRunBudget')!=1 or b.get('p48RunStarted') is not False or b.get('p48RunBudgetConsumed') is not False: raise HandoffBlocked('PERMIT_BUDGET_INVALID')
    if b.get('sourceCommit')!=SRC or b.get('metadataCommit')!=META or p.get('automaticRetry') is not False: raise HandoffBlocked('PERMIT_AUTHORITY_INVALID')
    return ident

def verify_bundle(repo,p):
    files=(p.get('identityBinding') or {}).get('bundleFileSha256')
    if not isinstance(files,dict) or not files: raise HandoffBlocked('BUNDLE_BYTE_BINDING_MISSING')
    for rel,expect in sorted(files.items()):
        q=repo/rel
        if not q.is_file(): raise HandoffBlocked(f'BUNDLE_FILE_MISSING:{rel}')
        if sha(q.read_bytes())!=expect: raise HandoffBlocked(f'BUNDLE_FILE_SHA256_MISMATCH:{rel}')

def authority(repo,p):
    pins=p.get('authorityFilePins')
    if not isinstance(pins,dict): raise HandoffBlocked('AUTHORITY_PINS_MISSING')
    for rel,expect in sorted(pins.items()): pin(repo,rel,expect)
    r47=load(repo/'parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P47_BOUNDED_OWNER_DIAGNOSTIC_READINESS_GATE_RESULT.json')
    c47=load(repo/'parallel/PM/DEDUP_CLAIMS/alpha.v1.product-takeover.bounded-owner-diagnostic-readiness-gate-v1.json')
    s47=load(repo/'parallel/PM/STAGE_CLAIMS/ALPHA_V1_PRODUCT_TAKEOVER_P47_BOUNDED_OWNER_DIAGNOSTIC_READINESS_GATE.json')
    if r47.get('state')!='COMPLETE' or r47.get('readinessDecision')!='READY_FOR_ONE_BOUNDED_OWNER_DIAGNOSTIC' or c47.get('state')!='COMPLETE' or s47.get('state')!='COMPLETE': raise HandoffBlocked('P47_NOT_TERMINAL_READY')
    r48=load(repo/'parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P48_ONE_BOUNDED_OWNER_LIVE_DIAGNOSTIC_EXECUTION_RESULT.json')
    c48=load(repo/'parallel/PM/DEDUP_CLAIMS/alpha.v1.product-takeover.one-bounded-owner-live-diagnostic-execution-v1.json')
    s48=load(repo/'parallel/PM/STAGE_CLAIMS/ALPHA_V1_PRODUCT_TAKEOVER_P48_ONE_BOUNDED_OWNER_LIVE_DIAGNOSTIC_EXECUTION.json')
    if r48.get('state')!='COMPLETE' or r48.get('outcome')!='BLOCKED_PRE_RUN' or c48.get('state')!='COMPLETE' or s48.get('state')!='COMPLETE': raise HandoffBlocked('P48_TERMINAL_TRUTH_MISMATCH')
    budget(r48,c48,s48)
    dep=load(repo/'parallel/OWNER_DIAGNOSTIC/P43_POST_P45_P46_INTEGRATED_CANDIDATE.json').get('dependencies') or {}; b=p['identityBinding']
    if dep.get('p45TestedCommit')!=b.get('p45TestedCommit') or dep.get('p46TestedCommit')!=b.get('p46TestedCommit'): raise HandoffBlocked('P43_DEPENDENCY_DRIFT')
    ptr,prov=load(repo/PTR),load(repo/PROV)
    if ptr.get('state')!='READY' or ptr.get('sourceCommit')!=SRC or any(ptr.get(x) is not False for x in ('alphaLiveMoved','alphaLivePromoted','promotionPerformed')): raise HandoffBlocked('P38_POINTER_UNSAFE')
    if prov.get('sourceCommit')!=SRC or prov.get('alphaLiveMoved') is not False or prov.get('promotionPerformed') is not False or prov.get('pointerSha256')!=sha((repo/PTR).read_bytes()): raise HandoffBlocked('P38_PROVENANCE_UNSAFE')
    for commit in (META,b['p43TestedCommit'],b['p45TestedCommit'],b['p46TestedCommit']):
        cp=subprocess.run(['git','cat-file','-e',commit+'^{commit}'],cwd=repo,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        if cp.returncode: raise HandoffBlocked(f'REQUIRED_COMMIT_MISSING:{commit}')

def source_ok(src, call:Callable|None=None):
    if call: rc,h=call(src,'head'); rc2,st=call(src,'status');
    else: rc=rc2=0; h=git(src,'rev-parse','HEAD'); st=git(src,'status','--porcelain=v1','--untracked-files=all')
    if rc: raise HandoffBlocked('SOURCE_HEAD_UNREADABLE')
    if rc2: raise HandoffBlocked('SOURCE_STATUS_UNREADABLE')
    if h.strip().lower()!=SRC: raise HandoffBlocked(f'SOURCE_HEAD_MISMATCH:{h.strip()}')
    if st.strip(): raise HandoffBlocked('SOURCE_CHECKOUT_DIRTY')

def managed(env=None,match=True):
    env=os.environ if env is None else env; root=env.get('LOCALAPPDATA')
    if not root: raise HandoffBlocked('LOCALAPPDATA_NOT_SET')
    p=(Path(root)/'WOF Alpha Current Main'/'venv'/'Scripts'/'python.exe').resolve()
    if not p.is_file(): raise HandoffBlocked(f'MANAGED_INTERPRETER_MISSING:{p}')
    if match and os.path.normcase(str(Path(sys.executable).resolve()))!=os.path.normcase(str(p)): raise HandoffBlocked('WRONG_INTERPRETER')
    return p

def debugger(url,connect=None):
    if not url or not url.strip(): raise HandoffBlocked('MISSING_EXPLICIT_INPUT:browser-websocket-url')
    u=urlparse(url.strip())
    if u.scheme not in ('ws','wss') or not u.hostname: raise HandoffBlocked('BROWSER_WEBSOCKET_URL_INVALID')
    fn=socket.create_connection if connect is None else connect
    try: c=fn((u.hostname,u.port or (443 if u.scheme=='wss' else 80)),2.0); getattr(c,'close',lambda:None)()
    except Exception as e: raise HandoffBlocked(f'BROWSER_WEBSOCKET_UNREACHABLE:{e}') from e

def out_ok(out):
    out.mkdir(parents=True,exist_ok=True)
    for n in (OUTMARK,RECEIPT,IMPORT):
        if (out/n).exists(): raise HandoffBlocked(f'OUTPUT_ALREADY_CONTAINS_PRIOR_RUN_ARTIFACT:{n}')
    try: fd,n=tempfile.mkstemp(prefix='.p49-',dir=out); os.close(fd); os.unlink(n)
    except Exception as e: raise HandoffBlocked(f'OUTPUT_NOT_WRITABLE:{e}') from e

def marker_path(ident,env=None):
    env=os.environ if env is None else env; root=env.get('LOCALAPPDATA')
    if not root: raise HandoffBlocked('LOCALAPPDATA_NOT_SET')
    return Path(root)/'WOF Alpha Current Main'/'owner-diagnostic-permits'/ident/'RUN_STARTED.json'

def mark(path,record):
    path.parent.mkdir(parents=True,exist_ok=True)
    try: fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    except FileExistsError as e: raise HandoffBlocked(f'PERMIT_ALREADY_CONSUMED:{path}') from e
    try:
        with os.fdopen(fd,'wb') as f: f.write(canon(record)); f.flush(); os.fsync(f.fileno())
    except Exception:
        try:path.unlink(missing_ok=True)
        except Exception:pass
        raise

def preflight(repo,src,ws,out,p,*,env=None,connect=None,check_python=True):
    ident=permit_id(p); verify_bundle(repo,p); authority(repo,p); source_ok(src)
    if check_python: managed(env)
    debugger(ws,connect); out_ok(out); m=marker_path(ident,env)
    if m.exists(): raise HandoffBlocked(f'PERMIT_ALREADY_CONSUMED:{m}')
    return ident,m

def p43cmd(repo,src,ws,out):
    q=repo/P43
    if not q.is_file(): raise HandoffBlocked('P43_ENTRYPOINT_MISSING')
    args=[str(q),str(repo),str(src),SRC,META,PTR,PROV,ws,str(out)]
    return [os.environ.get('COMSPEC') or 'cmd.exe','/d','/s','/c',subprocess.list2cmdline(args)]

def receipt(out):
    q=out/RECEIPT
    if not q.is_file(): return None,None,None
    b=q.read_bytes(); first=None
    try:
        r=json.loads(b.decode('utf-8-sig')); f=r.get('firstFailingGate') if isinstance(r,dict) else None
        if isinstance(f,dict): first=str(f.get('gate') or f.get('code') or 'UNKNOWN')
    except Exception:first='P43_RECEIPT_INVALID_JSON'
    return str(q),sha(b),first

def run_once(repo,src,ws,out,p,*,timeout=90,pre=preflight,invoke=subprocess.run,env=None):
    ident,m=pre(repo,src,ws,out,p,env=env); rec={'schema':'wof-alpha-p49-one-run-started-v1','permitIdentity':ident,'runStarted':True,'runBudgetConsumed':True,'remainingRunBudget':0,'retryAllowed':False,'sourceCommit':SRC,'metadataCommit':META,'outputDirectory':str(out),'startedAtUtc':datetime.now(timezone.utc).isoformat()}
    mark(m,rec)
    rc=70; timed=False; err=None; so=out/'P49_P43_STDOUT.txt'; se=out/'P49_P43_STDERR.txt'
    try:
        with so.open('wb') as a,se.open('wb') as b: rc=int(invoke(p43cmd(repo,src,ws,out),cwd=repo,stdout=a,stderr=b,timeout=timeout,check=False).returncode)
    except subprocess.TimeoutExpired as e: timed=True;err=f'P43_TIMEOUT:{e}';rc=124
    except Exception as e: err=f'P43_INVOCATION_ERROR:{type(e).__name__}:{e}';rc=70
    rp,rh,first=receipt(out)
    if first is None: first='P49_P43_SUBPROCESS_TIMEOUT' if timed else ('P49_P43_INVOCATION_ERROR' if err else ('P43_NONZERO_WITHOUT_RECEIPT_GATE' if rc else None))
    (out/IMPORT).write_bytes(canon({'schema':'wof-alpha-p49-owner-windows-one-run-import-v1','version':1,'permitIdentity':ident,'runStarted':True,'runBudgetConsumed':True,'remainingRunBudget':0,'automaticRetry':False,'p43ExitCode':rc,'timeout':timed,'invocationError':err,'p43ReceiptPath':rp,'p43ReceiptSha256':rh,'firstFailingGate':first,'outputDirectory':str(out),'authority':p['identityBinding'],'stdoutPath':str(so),'stderrPath':str(se)}))
    return rc

def main(argv=None):
    ap=argparse.ArgumentParser(); ap.add_argument('--metadata-repo-root',required=True);ap.add_argument('--source-checkout',required=True);ap.add_argument('--browser-websocket-url',required=True);ap.add_argument('--output-directory',required=True);ap.add_argument('--timeout-seconds',type=float,default=90); a=ap.parse_args(argv)
    try:
        repo=Path(a.metadata_repo_root).expanduser().resolve();src=Path(a.source_checkout).expanduser().resolve();out=Path(a.output_directory).expanduser().resolve()
        if not repo.is_dir() or not src.is_dir(): raise HandoffBlocked('EXPLICIT_REPOSITORY_PATH_NOT_DIRECTORY')
        if not 1<=a.timeout_seconds<=180: raise HandoffBlocked('TIMEOUT_SECONDS_OUT_OF_RANGE')
        return run_once(repo,src,a.browser_websocket_url,out,load(repo/PERMIT),timeout=a.timeout_seconds)
    except HandoffBlocked as e: print(f'P49_BLOCKED_PRE_RUN: {e}',file=sys.stderr);return 78
if __name__=='__main__': raise SystemExit(main())
