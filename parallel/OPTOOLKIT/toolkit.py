import argparse,json,os,platform,shutil,subprocess,sys,time,zipfile
from datetime import datetime
from pathlib import Path

VERSION='wof-windows-operator-toolkit-v1'
SAFETY={'readOnly':True,'ramWrites':0,'inputInjection':False}

def stamp(): return datetime.now().strftime('%Y%m%d_%H%M%S')
def rr():
    if os.getenv('WOF_RESULTS_DIR'): return Path(os.environ['WOF_RESULTS_DIR']).expanduser()
    h=Path.home(); d=h/'Documents'; return (d if d.exists() else h)/'WOF_RESULTS'
def run(a,cwd,t=180):
    return subprocess.run(a,cwd=str(cwd),text=True,encoding='utf-8',errors='replace',capture_output=True,timeout=t,check=False)
def wt(p,s): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(s,encoding='utf-8')
def wj(p,x): wt(p,json.dumps(x,ensure_ascii=False,indent=2)+'\n')

class Toolkit:
    def __init__(self,root):
        self.root=Path(root).resolve(); self.results=rr().resolve(); self.results.mkdir(parents=True,exist_ok=True)
        os.environ['WOF_PROJECT_ROOT']=str(self.root); os.environ['WOF_RESULTS_DIR']=str(self.results)
        self.logfile=self.results/'toolkit.log'
    def log(self,s):
        try:
            with self.logfile.open('a',encoding='utf-8') as f:f.write(f'[{datetime.now().isoformat(timespec="seconds")}] {s}\n')
        except OSError: pass
    def comp(self,k):
        xs={'recorder':['parallel/WOF052L_RECORDER/recorder.py','parallel/WOF052L_RECORDER/RUN_WOF052L_RECORDER.cmd'],
            'fleet':['parallel/BROWSER_FLEET/RUN_WOF_FLEET.cmd','parallel/BROWSER_FLEET/fleet_manager.py']}[k]
        for x in xs:
            p=self.root/x
            if p.is_file(): return p
        return None
    def menu(self):
        os.system('cls' if os.name=='nt' else 'clear')
        print('='*66,'\n WOF Windows Operator Toolkit\n',VERSION,'\n'+'='*66,sep='')
        print('Project :',self.root); print('Results :',self.results)
        print('READ ONLY / RAM writes: 0 / input injection: 0')
        print('Recorder:', 'READY' if self.comp('recorder') else 'MISSING','| Fleet:','READY' if self.comp('fleet') else 'MISSING')
        print('-'*66)
        for s in ['1 Update Project','2 Start Python Launcher','3 Start Multi-Room Recorder','4 Start Browser Fleet','5 Run Regression','6 Run Live Proof','7 Collect Diagnostics','8 Package Results','9 Open Results Folder','0 Exit']: print(s)
        print('='*66)
    def update(self):
        print('\n[Update Project]'); g=shutil.which('git')
        if not g: print('Git was not found. Install Git for Windows, then reopen Toolkit.'); return
        if not (self.root/'.git').exists(): print('This is not a Git checkout. Open Toolkit from the WOF project folder.'); return
        dirty=[x for x in run([g,'status','--porcelain'],self.root,30).stdout.splitlines() if x.strip()]
        if dirty:
            print('Local changes exist, so Toolkit will not pull over them. Your work is preserved.')
            for x in dirty[:10]: print(' ',x)
            return
        before=run([g,'rev-parse','--short','HEAD'],self.root,15).stdout.strip()
        f=run([g,'fetch','--prune','origin'],self.root,120)
        if f.returncode: print('Git fetch failed. Check network/login.\n'+(f.stderr or f.stdout)[-1000:]); return
        b=run([g,'branch','--show-current'],self.root,15).stdout.strip()
        if not b: print('Detached Git commit detected. Fetch succeeded; auto-pull was skipped safely.'); return
        p=run([g,'pull','--ff-only','origin',b],self.root,120); d=self.results/f'update_{stamp()}'
        wt(d/'git_pull.txt',p.stdout+('\n'+p.stderr if p.stderr else ''))
        if p.returncode: print('Fast-forward update was not possible. No local file was overwritten.\n'+(p.stderr or p.stdout)[-1000:]); return
        after=run([g,'rev-parse','--short','HEAD'],self.root,15).stdout.strip(); print(f'Project updated: {before or "?"} -> {after or "?"}')
        if before!=after: print('Reopen WOF_TOOLKIT.cmd after this session so pulled Toolkit/dependency updates are loaded.')
    def spawn(self,p,args=None):
        args=args or []; e=p.suffix.lower(); env=os.environ.copy()
        try:
            if e in('.cmd','.bat'):
                tail=' '.join(f'"{x}"' for x in args); c=['cmd.exe','/d','/c',f'call "{p}" {tail}'.rstrip()]
            elif e=='.py': c=[sys.executable,str(p),*args]
            elif e=='.exe': c=[str(p),*args]
            else: return False,'Unsupported component: '+p.name
            kw={'cwd':str(p.parent),'env':env}
            if os.name=='nt': kw['creationflags']=getattr(subprocess,'CREATE_NEW_CONSOLE',0)
            subprocess.Popen(c,**kw); return True,str(p)
        except Exception as x:return False,str(x)
    def launcher(self):
        print('\n[Start Python Launcher]'); p=self.root/'parallel/PYLAUNCH/launcher.py'
        if not p.is_file(): print('PYLAUNCH is missing. Use 1 Update Project first.'); return
        pyw=Path(sys.executable).with_name('pythonw.exe'); exe=pyw if os.name=='nt' and pyw.exists() else Path(sys.executable)
        subprocess.Popen([str(exe),str(p)],cwd=str(p.parent),env=os.environ.copy()); print('Python Launcher started. Look for the WOF tray icon.')
    def component(self,k):
        label='Multi-Room Recorder' if k=='recorder' else 'Browser Fleet'; print(f'\n[Start {label}]')
        p=self.comp(k)
        if not p: print(label+' is missing. Use 1 Update Project first.'); return
        if k=='recorder':
            rp=self.root/'parallel/WOF052L_RECORDER/recorder.py'; out=self.results/'recorder'; out.mkdir(parents=True,exist_ok=True)
            ok,x=self.spawn(rp,['--output-dir',str(out)]); print(('Started: ' if ok else 'Could not start: ')+x)
            if ok: print('Recorder output:',out)
        else:
            ok,x=self.spawn(p); print(('Started: ' if ok else 'Could not start: ')+x)
    def regression(self):
        print('\n[Run Regression]'); d=self.results/f'regression_{stamp()}'; d.mkdir(parents=True,exist_ok=True); checks=[]
        def rec(n,cp):
            wt(d/f'{n}.stdout.txt',cp.stdout); wt(d/f'{n}.stderr.txt',cp.stderr); s='PASS' if cp.returncode==0 else 'FAIL'; checks.append({'name':n,'status':s,'returnCode':cp.returncode}); print(n+':',s)
        node=shutil.which('node')
        for n,p in [('alpha_product',self.root/'product/alpha/regression.mjs'),('rc5_independent_bootstrap',self.root/'parallel/ALPHAQA_RC5/independent_bootstrap_retest.mjs')]:
            if not p.is_file(): checks.append({'name':n,'status':'MISSING'}); print(n+': MISSING')
            elif not node: checks.append({'name':n,'status':'BLOCKED','reason':'Node.js not found'}); print(n+': BLOCKED (Node.js not found)')
            else: rec(n,run([node,str(p)],p.parent))
        r=self.root/'parallel/WOF052L_RECORDER/recorder.py'
        if r.is_file(): rec('wof052l_self_test',run([sys.executable,str(r),'--self-test'],r.parent))
        for n,td in [('pylaunch_unittest',self.root/'parallel/PYLAUNCH/tests'),('browser_fleet_unittest',self.root/'parallel/BROWSER_FLEET/tests'),('toolkit_unittest',self.root/'parallel/OPTOOLKIT/tests')]:
            if td.is_dir(): rec(n,run([sys.executable,'-m','unittest','discover','-s',str(td),'-p','test_*.py'],self.root))
        overall='PASS' if checks and all(x['status']=='PASS' for x in checks) else 'ATTENTION'; wj(d/'regression_summary.json',{'toolkit':VERSION,'overall':overall,'safety':SAFETY,'checks':checks}); print('Overall:',overall,'\nSaved:',d)
    def proof(self):
        print('\n[Run Live Proof]'); p=self.root/'parallel/PYLAUNCH/launcher.py'
        if not p.is_file(): print('PYLAUNCH is missing. Use 1 Update Project first.'); return
        d=self.results/f'live_proof_{stamp()}'; d.mkdir(parents=True,exist_ok=True); out=d/'WINDOWS_PROOF_STATUS.json'
        pyw=Path(sys.executable).with_name('pythonw.exe'); exe=pyw if os.name=='nt' and pyw.exists() else Path(sys.executable)
        subprocess.Popen([str(exe),str(p),'--proof-json',str(out)],cwd=str(p.parent),env=os.environ.copy())
        print('Live Proof started using existing PYLAUNCH. Enter WOF normally; no DevTools/JS paste.\nProof JSON:',out)
    def latest(self,prefix):
        a=[p for p in self.results.glob(prefix+'*') if p.is_dir()]; return max(a,key=lambda p:p.stat().st_mtime) if a else None
    def diagnostics(self):
        print('\n[Collect Diagnostics]'); d=self.results/f'diagnostics_{stamp()}'; k=d/'known_status'; copied=[]
        for rel in ['parallel/PYLAUNCH/WINDOWS_PROOF_STATUS.json','parallel/PYLAUNCH/RESULT.md','parallel/ALPHAQA_RC5/result.json','parallel/ALPHAQA_RC5/AUDIT_STATUS.md','parallel/ALPHAQA_RC5/FINDINGS.md','product/alpha/regression_result.json','parallel/PM/ACTIVE_PRIORITIES.md','parallel/PM/RELEASE_READINESS.md']:
            s=self.root/rel
            if s.is_file(): k.mkdir(parents=True,exist_ok=True); q=k/(Path(rel).parent.name+'_'+s.name); shutil.copy2(s,q); copied.append(str(q))
        lp=self.latest('live_proof_')
        if lp and (lp/'WINDOWS_PROOF_STATUS.json').is_file(): (d/'live_proof').mkdir(parents=True); shutil.copy2(lp/'WINDOWS_PROOF_STATUS.json',d/'live_proof/WINDOWS_PROOF_STATUS.json')
        fm=Path(os.getenv('LOCALAPPDATA',str(Path.home())))/'WOF Future Danger/Fleet/instances.json'
        if fm.is_file(): (d/'browser_fleet').mkdir(parents=True); shutil.copy2(fm,d/'browser_fleet/instances.json')
        runs=self.results/'recorder/runs'
        if runs.is_dir():
            a=list(runs.glob('*.json'))
            if a: q=max(a,key=lambda p:p.stat().st_mtime); (d/'recorder').mkdir(parents=True); shutil.copy2(q,d/'recorder'/q.name)
        g=shutil.which('git'); gs={'available':bool(g)}
        if g and (self.root/'.git').exists():
            for n,a in [('head',[g,'rev-parse','HEAD']),('branch',[g,'branch','--show-current']),('status',[g,'status','--short'])]: gs[n]=run(a,self.root,30).stdout.strip()
        wj(d/'diagnostics_summary.json',{'toolkit':VERSION,'time':datetime.now().isoformat(timespec='seconds'),'projectRoot':str(self.root),'resultsRoot':str(self.results),'platform':platform.platform(),'python':sys.version,'node':shutil.which('node'),'git':gs,'safety':SAFETY,'components':{'pythonLauncher':str(self.root/'parallel/PYLAUNCH/launcher.py'),'recorder':str(self.comp('recorder')) if self.comp('recorder') else None,'browserFleet':str(self.comp('fleet')) if self.comp('fleet') else None},'copiedFiles':copied})
        if self.logfile.is_file(): shutil.copy2(self.logfile,d/'toolkit.log')
        print('Diagnostics saved:',d); return d
    def package(self):
        print('\n[Package Results]'); sel=[p for q in('diagnostics_','regression_','live_proof_') if (p:=self.latest(q))]
        if not sel: sel=[self.diagnostics()]
        runs=self.results/'recorder/runs'; rf=max(list(runs.glob('*.json')),key=lambda p:p.stat().st_mtime) if runs.is_dir() and list(runs.glob('*.json')) else None
        pd=self.results/'packages'; pd.mkdir(parents=True,exist_ok=True); z=pd/f'WOF_RESULTS_{stamp()}.zip'; m={'toolkit':VERSION,'created':datetime.now().isoformat(timespec='seconds'),'safety':SAFETY,'included':[p.name for p in sel]+([rf.name] if rf else [])}
        with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as f:
            f.writestr('PACKAGE_MANIFEST.json',json.dumps(m,ensure_ascii=False,indent=2)+'\n')
            for s in sel:
                for p in s.rglob('*'):
                    if p.is_file(): f.write(p,arcname=f'{s.name}/{p.relative_to(s)}')
            if rf:f.write(rf,arcname='recorder/'+rf.name)
        print('Package ready:',z)
    def open_results(self):
        print('\n[Open Results Folder]')
        if os.name=='nt': os.startfile(str(self.results))
        else:
            x=shutil.which('xdg-open') or shutil.which('open')
            if x: subprocess.Popen([x,str(self.results)])
        print('Opened:',self.results)
    def loop(self):
        acts={'1':self.update,'2':self.launcher,'3':lambda:self.component('recorder'),'4':lambda:self.component('fleet'),'5':self.regression,'6':self.proof,'7':self.diagnostics,'8':self.package,'9':self.open_results}; self.log('start '+str(self.root))
        while 1:
            self.menu(); c=input('Choose 0-9: ').strip()
            if c=='0': return 0
            if c not in acts: print('Please choose a number from 0 to 9.'); time.sleep(1); continue
            try: acts[c](); self.log('action '+c+' completed')
            except subprocess.TimeoutExpired: print('This action timed out. No game RAM write or gameplay input was sent.'); self.log('action '+c+' timeout')
            except Exception as e: print('Toolkit could not complete this action:',e); print('No game RAM write or gameplay input was attempted by Toolkit.'); self.log('action '+c+' error='+repr(e))
            input('\nPress Enter to return to WOF Toolkit...')

def main():
    a=argparse.ArgumentParser(); a.add_argument('--root',required=True); root=Path(a.parse_args().root)
    if not (root/'parallel/PYLAUNCH').is_dir() or not (root/'product/alpha').is_dir(): print('WOF Toolkit could not validate project root:',root); return 2
    return Toolkit(root).loop()
if __name__=='__main__': raise SystemExit(main())
