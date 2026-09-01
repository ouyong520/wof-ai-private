import importlib.util
import os
import tempfile
import unittest
import zipfile
from pathlib import Path

HERE=Path(__file__).resolve()
SPEC=importlib.util.spec_from_file_location('wof_toolkit',HERE.parents[1]/'toolkit.py')
M=importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(M)

class ToolkitTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.base=Path(self.tmp.name); self.root=self.base/'repo'
        (self.root/'parallel/PYLAUNCH').mkdir(parents=True); (self.root/'product/alpha').mkdir(parents=True)
        self.old=os.environ.get('WOF_RESULTS_DIR'); os.environ['WOF_RESULTS_DIR']=str(self.base/'results'); self.t=M.Toolkit(self.root)
    def tearDown(self):
        if self.old is None: os.environ.pop('WOF_RESULTS_DIR',None)
        else: os.environ['WOF_RESULTS_DIR']=self.old
        self.tmp.cleanup()
    def touch(self,rel,text='@echo off\n'):
        p=self.root/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text,encoding='utf-8'); return p
    def test_safety_contract(self):
        self.assertEqual(M.SAFETY,{'readOnly':True,'ramWrites':0,'inputInjection':False})
    def test_current_052l_recorder_is_discovered(self):
        p=self.touch('parallel/WOF052L_RECORDER/recorder.py','print("recorder")\n'); self.assertEqual(self.t.comp('recorder'),p)
    def test_old_generic_recorder_is_not_discovered(self):
        self.touch('parallel/RAWMINE/old_multiroom_recorder.py','print("old")\n'); self.assertIsNone(self.t.comp('recorder'))
    def test_current_browser_fleet_is_discovered(self):
        p=self.touch('parallel/BROWSER_FLEET/RUN_WOF_FLEET.cmd'); self.assertEqual(self.t.comp('fleet'),p)
    def test_unrelated_fleet_name_is_not_discovered(self):
        self.touch('parallel/OTHER/fleet.py','print("not browser fleet")\n'); self.assertIsNone(self.t.comp('fleet'))
    def test_product_alpha_tools_are_never_components(self):
        self.touch('product/alpha/WOF052L_RECORDER.cmd'); self.touch('product/alpha/BROWSER_FLEET.cmd')
        self.assertIsNone(self.t.comp('recorder')); self.assertIsNone(self.t.comp('fleet'))
    def test_package_includes_latest_categories_and_manifest(self):
        for name in ('diagnostics_20260901_010101','regression_20260901_010102','live_proof_20260901_010103'):
            d=self.t.results/name; d.mkdir(parents=True); (d/'x.txt').write_text(name,encoding='utf-8')
        self.t.package(); zips=list((self.t.results/'packages').glob('WOF_RESULTS_*.zip')); self.assertEqual(len(zips),1)
        with zipfile.ZipFile(zips[0]) as z: names=set(z.namelist())
        self.assertIn('PACKAGE_MANIFEST.json',names); self.assertTrue(any(n.startswith('diagnostics_') for n in names)); self.assertTrue(any(n.startswith('regression_') for n in names)); self.assertTrue(any(n.startswith('live_proof_') for n in names))
    def test_external_results_override(self):
        self.assertEqual(self.t.results,self.base/'results')

if __name__=='__main__': unittest.main()
