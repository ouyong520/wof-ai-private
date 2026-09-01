import argparse,json,os,platform,shutil,subprocess,sys,time,zipfile
from datetime import datetime
from pathlib import Path

VERSION='wof-windows-operator-toolkit-v2-cn'
SAFETY={'readOnly':True,'ramWrites':0,'inputInjection':False}

def stamp(): return datetime.now().strftime('%Y%m%d_%H%M%S')
def rr():
    if os.getenv('WOF_RESULTS_DIR'): return Path(os.environ['WOF_RESULTS_DIR']).expanduser()
    h=Path.home(); d=h/'Documents'; return (d if d.exists() else h)/'WOF_RESULTS'
def run(a,cwd,t=180):
    return subprocess.run(a,cwd=str(cwd),text=True,encoding='utf-8',errors='replace',capture_output=True,timeout=t,check=False)
def wt(p,s): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(s,encoding='utf-8')
def wj(p,x): wt(p,json.dumps(x,ensure_ascii=False,indent=2)+'\n')

def _package_version(root: Path) -> str:
    v=os.getenv('WOF_PACKAGE_VERSION','').strip()
    if v:return v
    p=root/'PACKAGE_MANIFEST.json'
    if p.is_file():
        try:return str(json.loads(p.read_text(encoding='utf-8-sig')).get('packageVersion') or '')
        except Exception:return ''
    return ''

class Toolkit:
    def __init__(self,root):
        self.root=Path(root).resolve(); self.results=rr().resolve(); self.results.mkdir(parents=True,exist_ok=True)
        os.environ['WOF_PROJECT_ROOT']=str(self.root); os.environ['WOF_RESULTS_DIR']=str(self.results)
        self.logfile=self.results/'toolkit.log'
        self.packaged=os.getenv('WOF_PACKAGED_MODE')=='1' or (self.root/'PACKAGE_MANIFEST.json').is_file()
        self.package_version=_package_version(self.root)
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
        print('='*66)
        print(' WOF 中文工具箱')
        print(' 版本：'+VERSION+(f' / 安装包 {self.package_version}' if self.package_version else ''))
        print('='*66)
        print('工具目录：',self.root)
        print('结果目录：',self.results)
        print('安全状态：只读开启 / 游戏内存写入 0 / 游戏输入注入 0')
        print('多房间采集器：', '已就绪' if self.comp('recorder') else '缺失','| 浏览器批量管理：','已就绪' if self.comp('fleet') else '缺失')
        print('-'*66)
        for s in ['1 更新 WOF 工具','2 启动 Python Launcher','3 启动多房间采集器','4 启动浏览器批量管理','5 运行回归检查','6 运行真人浏览器验证','7 收集诊断信息','8 打包结果','9 打开结果目录','0 退出']: print(s)
        print('='*66)
    def update(self):
        print('\n[更新 WOF 工具]')
        if self.packaged:
            p=Path(os.getenv('WOF_BOOTSTRAP_PATH','')) if os.getenv('WOF_BOOTSTRAP_PATH') else self.root/'WOF_一键工具.cmd'
            if not p.is_file():
                print('未找到一键更新入口。请重新下载 WOF_一键工具.cmd 后双击。')
                return
            try:
                cp=run(['cmd.exe','/d','/c',f'call "{p}" --update-only'],self.root,600)
                if cp.stdout: print(cp.stdout.rstrip())
                if cp.returncode:
                    print('更新没有完成。旧版本仍然保留，游戏本身没有受到影响。')
                    if cp.stderr: print('技术详情：'+cp.stderr[-1000:])
                else:
                    print('更新检查完成。若安装了新版本，请退出工具箱后重新双击 WOF_一键工具.cmd。')
            except Exception as e:
                print('更新没有完成。旧版本仍然保留，游戏本身没有受到影响。')
                print('技术详情：',e)
            return
        g=shutil.which('git')
        if not g:
            print('当前是仓库模式，但没有找到 Git。建议改用 WOF_一键工具.cmd，以后无需 Git。'); return
        if not (self.root/'.git').exists(): print('当前目录不是 Git 仓库。建议改用 WOF_一键工具.cmd。'); return
        dirty=[x for x in run([g,'status','--porcelain'],self.root,30).stdout.splitlines() if x.strip()]
        if dirty:
            print('检测到本地修改，为避免覆盖，已停止自动更新。你的文件没有被改动。')
            for x in dirty[:10]: print(' ',x)
            return
        before=run([g,'rev-parse','--short','HEAD'],self.root,15).stdout.strip()
        f=run([g,'fetch','--prune','origin'],self.root,120)
        if f.returncode: print('Git 更新失败，请检查网络。\n'+(f.stderr or f.stdout)[-1000:]); return
        b=run([g,'branch','--show-current'],self.root,15).stdout.strip()
        if not b: print('当前是 detached commit，已安全跳过自动 pull。'); return
        p=run([g,'pull','--ff-only','origin',b],self.root,120); d=self.results/f'update_{stamp()}'
        wt(d/'git_pull.txt',p.stdout+('\n'+p.stderr if p.stderr else ''))
        if p.returncode: print('无法 fast-forward 更新，未覆盖任何本地文件。\n'+(p.stderr or p.stdout)[-1000:]); return
        after=run([g,'rev-parse','--short','HEAD'],self.root,15).stdout.strip(); print(f'项目已更新：{before or "?"} -> {after or "?"}')
        if before!=after: print('请退出后重新打开工具箱，以加载新版本。')
    def spawn(self,p,args=None):
        args=args or []; e=p.suffix.lower(); env=os.environ.copy()
        try:
            if e in('.cmd','.bat'):
                tail=' '.join(f'"{x}"' for x in args); c=['cmd.exe','/d','/c',f'call "{p}" {tail}'.rstrip()]
            elif e=='.py': c=[sys.executable,str(p),*args]
            elif e=='.exe': c=[str(p),*args]
            else: return False,'不支持的组件：'+p.name
            kw={'cwd':str(p.parent),'env':env}
            if os.name=='nt': kw['creationflags']=getattr(subprocess,'CREATE_NEW_CONSOLE',0)
            subprocess.Popen(c,**kw); return True,str(p)
        except Exception as x:return False,str(x)
    def launcher(self):
        print('\n[启动 Python Launcher]'); p=self.root/'parallel/PYLAUNCH/launcher.py'
        if not p.is_file(): print('PYLAUNCH 缺失。请先选择 1 更新 WOF 工具。'); return
        pyw=Path(sys.executable).with_name('pythonw.exe'); exe=pyw if os.name=='nt' and pyw.exists() else Path(sys.executable)
        subprocess.Popen([str(exe),str(p)],cwd=str(p.parent),env=os.environ.copy()); print('Python Launcher 已启动，请查看 Windows 右下角 WOF 托盘图标。')
    def component(self,k):
        label='多房间采集器' if k=='recorder' else '浏览器批量管理'; print(f'\n[启动{label}]')
        p=self.comp(k)
        if not p: print(label+'缺失。请先选择 1 更新 WOF 工具。'); return
        if k=='recorder':
            rp=self.root/'parallel/WOF052L_RECORDER/recorder.py'; out=self.results/'recorder'; out.mkdir(parents=True,exist_ok=True)
            ok,x=self.spawn(rp,['--output-dir',str(out)]); print(('已启动：' if ok else '启动失败：')+x)
            if ok: print('采集结果目录：',out)
        else:
            ok,x=self.spawn(p); print(('已启动：' if ok else '启动失败：')+x)
    def regression(self):
        print('\n[运行回归检查]'); d=self.results/f'regression_{stamp()}'; d.mkdir(parents=True,exist_ok=True); checks=[]
        def rec(n,cp):
            wt(d/f'{n}.stdout.txt',cp.stdout); wt(d/f'{n}.stderr.txt',cp.stderr); s='PASS' if cp.returncode==0 else 'FAIL'; checks.append({'name':n,'status':s,'returnCode':cp.returncode}); print(n+':',s)
        node=shutil.which('node')
        for n,p in [('alpha_product',self.root/'product/alpha/regression.mjs'),('rc5_independent_bootstrap',self.root/'parallel/ALPHAQA_RC5/independent_bootstrap_retest.mjs')]:
            if not p.is_file(): checks.append({'name':n,'status':'MISSING'}); print(n+': 缺失')
            elif not node: checks.append({'name':n,'status':'BLOCKED','reason':'Node.js not found'}); print(n+': 暂无法运行（未安装 Node.js）')
            else: rec(n,run([node,str(p)],p.parent))
        r=self.root/'parallel/WOF052L_RECORDER/recorder.py'
        if r.is_file(): rec('wof052l_self_test',run([sys.executable,str(r),'--self-test'],r.parent))
        for n,td in [('pylaunch_unittest',self.root/'parallel/PYLAUNCH/tests'),('browser_fleet_unittest',self.root/'parallel/BROWSER_FLEET/tests'),('toolkit_unittest',self.root/'parallel/OPTOOLKIT/tests')]:
            if td.is_dir(): rec(n,run([sys.executable,'-m','unittest','discover','-s',str(td),'-p','test_*.py'],self.root))
        overall='PASS' if checks and all(x['status']=='PASS' for x in checks) else 'ATTENTION'; wj(d/'regression_summary.json',{'toolkit':VERSION,'overall':overall,'safety':SAFETY,'checks':checks}); print('总体结果：',overall,'\n保存位置：',d)
    def proof(self):
        print('\n[运行真人浏览器验证]'); p=self.root/'parallel/PYLAUNCH/launcher.py'
        if not p.is_file(): print('PYLAUNCH 缺失。请先选择 1 更新 WOF 工具。'); return
        d=self.results/f'live_proof_{stamp()}'; d.mkdir(parents=True,exist_ok=True); out=d/'WINDOWS_PROOF_STATUS.json'
        pyw=Path(sys.executable).with_name('pythonw.exe'); exe=pyw if os.name=='nt' and pyw.exists() else Path(sys.executable)
        subprocess.Popen([str(exe),str(p),'--proof-json',str(out)],cwd=str(p.parent),env=os.environ.copy())
        print('已启动现有 PYLAUNCH 真人验证。正常进入 WOF 即可，不需要打开 DevTools 或粘贴 JS。\n验证 JSON：',out)
    def latest(self,prefix):
        a=[p for p in self.results.glob(prefix+'*') if p.is_dir()]; return max(a,key=lambda p:p.stat().st_mtime) if a else None
    def diagnostics(self):
        print('\n[收集诊断信息]'); d=self.results/f'diagnostics_{stamp()}'; k=d/'known_status'; copied=[]
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
        wj(d/'diagnostics_summary.json',{'toolkit':VERSION,'packageVersion':self.package_version or None,'time':datetime.now().isoformat(timespec='seconds'),'projectRoot':str(self.root),'resultsRoot':str(self.results),'platform':platform.platform(),'python':sys.version,'node':shutil.which('node'),'git':gs,'safety':SAFETY,'components':{'pythonLauncher':str(self.root/'parallel/PYLAUNCH/launcher.py'),'recorder':str(self.comp('recorder')) if self.comp('recorder') else None,'browserFleet':str(self.comp('fleet')) if self.comp('fleet') else None},'copiedFiles':copied})
        if self.logfile.is_file(): shutil.copy2(self.logfile,d/'toolkit.log')
        print('诊断信息已保存：',d); return d
    def package(self):
        print('\n[打包结果]'); sel=[p for q in('diagnostics_','regression_','live_proof_') if (p:=self.latest(q))]
        if not sel: sel=[self.diagnostics()]
        runs=self.results/'recorder/runs'; rf=max(list(runs.glob('*.json')),key=lambda p:p.stat().st_mtime) if runs.is_dir() and list(runs.glob('*.json')) else None
        pd=self.results/'packages'; pd.mkdir(parents=True,exist_ok=True); z=pd/f'WOF_RESULTS_{stamp()}.zip'; m={'toolkit':VERSION,'packageVersion':self.package_version or None,'created':datetime.now().isoformat(timespec='seconds'),'safety':SAFETY,'included':[p.name for p in sel]+([rf.name] if rf else [])}
        with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as f:
            f.writestr('PACKAGE_MANIFEST.json',json.dumps(m,ensure_ascii=False,indent=2)+'\n')
            for s in sel:
                for p in s.rglob('*'):
                    if p.is_file(): f.write(p,arcname=f'{s.name}/{p.relative_to(s)}')
            if rf:f.write(rf,arcname='recorder/'+rf.name)
        print('结果包已生成：',z)
    def open_results(self):
        print('\n[打开结果目录]')
        if os.name=='nt': os.startfile(str(self.results))
        else:
            x=shutil.which('xdg-open') or shutil.which('open')
            if x: subprocess.Popen([x,str(self.results)])
        print('已打开：',self.results)
    def loop(self):
        acts={'1':self.update,'2':self.launcher,'3':lambda:self.component('recorder'),'4':lambda:self.component('fleet'),'5':self.regression,'6':self.proof,'7':self.diagnostics,'8':self.package,'9':self.open_results}; self.log('start '+str(self.root))
        while 1:
            self.menu(); c=input('请选择 0-9：').strip()
            if c=='0': return 0
            if c not in acts: print('请输入 0 到 9 之间的数字。'); time.sleep(1); continue
            try: acts[c](); self.log('action '+c+' completed')
            except subprocess.TimeoutExpired: print('这个操作超时了。没有写游戏内存，也没有注入游戏输入。'); self.log('action '+c+' timeout')
            except Exception as e: print('工具箱未能完成这个操作。'); print('游戏本身没有受到影响。'); print('技术详情：',e); self.log('action '+c+' error='+repr(e))
            input('\n按 Enter 返回 WOF 工具箱...')

def main():
    a=argparse.ArgumentParser(); a.add_argument('--root',required=True); root=Path(a.parse_args().root)
    if not (root/'parallel/PYLAUNCH/launcher.py').is_file() or not (root/'parallel/OPTOOLKIT/toolkit.py').is_file():
        print('WOF 工具箱无法确认工具目录：',root); print('请重新双击 WOF_一键工具.cmd 修复/更新安装。'); return 2
    return Toolkit(root).loop()
if __name__=='__main__': raise SystemExit(main())