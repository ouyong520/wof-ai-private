from __future__ import annotations
import json, tempfile, unittest, zipfile
from pathlib import Path
from unittest import mock
from training.farm import windows_portable_real_wof_bundle as b

class BundleTests(unittest.TestCase):
    def setUp(self):
        self.td=tempfile.TemporaryDirectory(prefix="三国 10训 (portable) "); self.root=Path(self.td.name)/"source"; self.root.mkdir()
        self.old_proof=dict(b.PROOF_AUTHORITY_BLOBS); self.old_support=dict(b.PORTABLE_SUPPORT_BLOBS)
        fixture={
            "training/__init__.py":b"# t\n",
            "training/farm/__init__.py":b"# f\n",
            "training/farm/windows_oneclick_bootstrap.py":b"# bootstrap\n",
            "training/farm/real_wof_proof_owner_runner.py":b"# runner\n",
            "training/farm/beginner_real_wof_launcher.py":b"# launcher\n",
            "training/farm/requirements-r0.1.txt":b"stable-retro==0.9.8\n",
            "training/farm/windows_portable_real_wof_bundle_verifier.py":b"# verifier\n",
            "training/farm/windows_portable_real_wof_bundle.manifest.schema.json":b"{}\n",
        }
        proof={}; support={}
        for rel,data in fixture.items():
            p=self.root/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(data)
            (support if "windows_portable_real_wof_bundle" in rel else proof)[rel]=b.git_blob_sha1(data)
        b.PROOF_AUTHORITY_BLOBS.clear(); b.PROOF_AUTHORITY_BLOBS.update(proof)
        b.PORTABLE_SUPPORT_BLOBS.clear(); b.PORTABLE_SUPPORT_BLOBS.update(support)
        self.candidate="1"*40
    def tearDown(self):
        b.PROOF_AUTHORITY_BLOBS.clear(); b.PROOF_AUTHORITY_BLOBS.update(self.old_proof); b.PORTABLE_SUPPORT_BLOBS.clear(); b.PORTABLE_SUPPORT_BLOBS.update(self.old_support); self.td.cleanup()
    def build(self,name="a.zip"):
        z=Path(self.td.name)/name; s=Path(self.td.name)/(name+".manifest.json"); side=b.build_zip(self.root,self.candidate,z,s); return z,s,side
    def rewrite(self,z,mutator):
        with zipfile.ZipFile(z,"r") as src: entries=[(i.filename,src.read(i.filename)) for i in src.infolist()]
        mutator(entries); out=Path(self.td.name)/"mut.zip"
        with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_STORED) as dst:
            for name,data in entries: dst.writestr(b._zip_info(name),data)
        return out
    def test_deterministic_build_and_flags(self):
        zA,_,sideA=self.build("A.zip"); zB,_,sideB=self.build("B.zip")
        self.assertEqual(zA.read_bytes(),zB.read_bytes()); self.assertEqual(sideA["zipSha256"],sideB["zipSha256"])
        with zipfile.ZipFile(zA) as z: m=json.loads(z.read(b.INNER_MANIFEST))
        self.assertEqual(m["flags"],{"containsRomBytes":False,"realWofProof":False,"r0_5Authorized":False,"readOnlyProof":True,"ramWrites":0,"inputInjection":False})
        self.assertEqual(b.verify_zip(zA)["status"],"PASS")
    def test_tamper_missing_extra(self):
        z,_,_=self.build()
        tam=self.rewrite(z,lambda e:e.__setitem__(0,(e[0][0],e[0][1]+b"x")))
        with self.assertRaises(b.BundleError): b.verify_zip(tam)
        miss=self.rewrite(z,lambda e:e.pop(0))
        with self.assertRaises(b.BundleError): b.verify_zip(miss)
        extra=self.rewrite(z,lambda e:e.append(("unexpected.txt",b"x")))
        with self.assertRaises(b.BundleError): b.verify_zip(extra)
    def test_duplicate_traversal_absolute_rom_rejected(self):
        z,_,_=self.build()
        for bad in ["../evil.txt","/absolute.txt","C:/evil.txt","payload/game.zip"]:
            out=Path(self.td.name)/(bad.replace("/","_").replace(":","_")+".zip")
            with zipfile.ZipFile(z) as src, zipfile.ZipFile(out,"w",compression=zipfile.ZIP_STORED) as dst:
                for i in src.infolist(): dst.writestr(b._zip_info(i.filename),src.read(i.filename))
                dst.writestr(b._zip_info(bad),b"x")
            with self.assertRaises(b.BundleError): b.verify_zip(out)
        dup=Path(self.td.name)/"dup.zip"
        with zipfile.ZipFile(z) as src, zipfile.ZipFile(dup,"w",compression=zipfile.ZIP_STORED) as dst:
            items=src.infolist()
            for i in items: dst.writestr(b._zip_info(i.filename),src.read(i.filename))
            dst.writestr(b._zip_info(items[0].filename),src.read(items[0].filename))
        with self.assertRaises(b.BundleError): b.verify_zip(dup)
    def test_extracted_chinese_space_parentheses_and_extra(self):
        z,_,_=self.build(); dest=Path(self.td.name)/"中文 路径 (测试)"; dest.mkdir()
        with zipfile.ZipFile(z) as src: src.extractall(dest)
        self.assertEqual(b.verify_extracted(dest)["status"],"PASS")
        (dest/"extra.txt").write_text("x")
        with self.assertRaises(b.BundleError): b.verify_extracted(dest)
    def test_source_blob_drift_fails(self):
        p=self.root/next(iter(b.PROOF_AUTHORITY_BLOBS)); p.write_bytes(p.read_bytes()+b"x")
        with self.assertRaises(b.BundleError): b.build_manifest(self.root,self.candidate)
    def test_root_entry_preserves_local_root_and_child_code_contract(self):
        data=b._render_root_start().decode("utf-8-sig")
        self.assertIn('set "WOF_TRAINING_FARM_LOCAL_ROOT=%LOCAL_ROOT%"',data)
        self.assertIn('--evidence-root "%LOCAL_ROOT%\\evidence"',data)
        self.assertIn('set "RC=%ERRORLEVEL%"',data); self.assertIn('exit /b %RC%',data)
        self.assertIn('run_windows_oneclick_env_bootstrap.cmd',data)

if __name__=="__main__": unittest.main()
