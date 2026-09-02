from __future__ import annotations
import json, tempfile, zipfile
from pathlib import Path
from training.farm import windows_portable_real_wof_bundle as b

def main()->int:
    oldp=dict(b.PROOF_AUTHORITY_BLOBS); olds=dict(b.PORTABLE_SUPPORT_BLOBS)
    try:
        with tempfile.TemporaryDirectory(prefix="三国 10训 (offline) ") as td:
            root=Path(td)/"src"; root.mkdir(); proof={}; support={}
            fixture={"training/__init__.py":b"#t\n","training/farm/__init__.py":b"#f\n","training/farm/windows_oneclick_bootstrap.py":b"#b\n","training/farm/real_wof_proof_owner_runner.py":b"#r\n","training/farm/beginner_real_wof_launcher.py":b"#l\n","training/farm/requirements-r0.1.txt":b"stable-retro==0.9.8\n","training/farm/windows_portable_real_wof_bundle_verifier.py":b"#v\n","training/farm/windows_portable_real_wof_bundle.manifest.schema.json":b"{}\n"}
            for rel,data in fixture.items():
                p=root/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(data)
                (support if "windows_portable_real_wof_bundle" in rel else proof)[rel]=b.git_blob_sha1(data)
            b.PROOF_AUTHORITY_BLOBS.clear(); b.PROOF_AUTHORITY_BLOBS.update(proof); b.PORTABLE_SUPPORT_BLOBS.clear(); b.PORTABLE_SUPPORT_BLOBS.update(support)
            candidate="2"*40; z1=Path(td)/"一 (a).zip"; z2=Path(td)/"二 (b).zip"
            s1=b.build_zip(root,candidate,z1,Path(td)/"a.side"); s2=b.build_zip(root,candidate,z2,Path(td)/"b.side")
            assert z1.read_bytes()==z2.read_bytes(); assert s1["zipSha256"]==s2["zipSha256"]
            dest=Path(td)/"F 模拟/三国10训 (portable)"; dest.mkdir(parents=True)
            with zipfile.ZipFile(z1) as z: z.extractall(dest)
            out=b.verify_extracted(dest,candidate); assert out["status"]=="PASS" and out["realWofProof"] is False and out["r0_5Authorized"] is False
            print(json.dumps({"status":"PASS","deterministic":True,"unicodeSpaceParenthesesPath":True,"romAccessed":False,"realWofProof":False,"r0_5Authorized":False},ensure_ascii=False,sort_keys=True))
            return 0
    finally:
        b.PROOF_AUTHORITY_BLOBS.clear(); b.PROOF_AUTHORITY_BLOBS.update(oldp); b.PORTABLE_SUPPORT_BLOBS.clear(); b.PORTABLE_SUPPORT_BLOBS.update(olds)
if __name__=="__main__": raise SystemExit(main())
