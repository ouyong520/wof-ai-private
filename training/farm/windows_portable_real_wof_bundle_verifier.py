"""ROM-free verifier shipped inside the R0.4.7 portable package."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
import zipfile
from pathlib import Path, PurePosixPath

SCHEMA = "wof-training-farm-windows-portable-real-wof-proof-bundle-manifest-v1"
INNER_MANIFEST = "portable_manifest.json"
FIXED_ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
_SHA40 = re.compile(r"[0-9a-f]{40}\Z")
_SHA64 = re.compile(r"[0-9a-f]{64}\Z")
_DRIVE = re.compile(r"^[A-Za-z]:")
FORBIDDEN_COMPONENTS = {".git",".venv","venv","__pycache__",".pytest_cache",".mypy_cache",".ruff_cache",".tox","evidence","logs","runtime","training-data","checkpoints","rom","roms","bios","secrets"}
FORBIDDEN_SUFFIXES = {".zip",".7z",".rar",".rom",".bin",".chd",".iso",".cue",".gba",".gb",".gbc",".nes",".sfc",".smc",".mdf",".nrg",".a26",".pce",".gen",".bios"}

class VerifyError(RuntimeError): pass

def sha256(data: bytes) -> str: return hashlib.sha256(data).hexdigest()
def git_blob(data: bytes) -> str: return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()
def key(name: str) -> str: return unicodedata.normalize("NFC", name).casefold()

def safe(name: str) -> str:
    if not isinstance(name,str) or not name or "\\" in name or "\x00" in name: raise VerifyError(f"INVALID_PATH: {name!r}")
    if name.startswith("/") or name.startswith("//") or _DRIVE.match(name): raise VerifyError(f"ABSOLUTE_PATH: {name}")
    p=PurePosixPath(name)
    if not p.parts or any(x in {"",".",".."} for x in p.parts) or str(p)!=name: raise VerifyError(f"PATH_TRAVERSAL_OR_NON_NORMALIZED: {name}")
    if any(unicodedata.normalize("NFC",x).casefold() in FORBIDDEN_COMPONENTS for x in p.parts): raise VerifyError(f"FORBIDDEN_LOCAL_PATH: {name}")
    if p.suffix.casefold() in FORBIDDEN_SUFFIXES: raise VerifyError(f"ROM_LIKE_PAYLOAD: {name}")
    return name

def aggregate(rows: list[dict[str,object]]) -> str:
    b="".join(f"{r['path']}\0{r['size']}\0{r['sha256']}\n" for r in sorted(rows,key=lambda r:str(r['path']))).encode()
    return sha256(b)

def validate_manifest(m: object) -> dict[str,object]:
    if not isinstance(m,dict) or m.get("schema")!=SCHEMA or m.get("version")!=1: raise VerifyError("MANIFEST_SCHEMA")
    flags=m.get("flags")
    if flags!={"containsRomBytes":False,"realWofProof":False,"r0_5Authorized":False,"readOnlyProof":True,"ramWrites":0,"inputInjection":False}: raise VerifyError("MANIFEST_FLAGS")
    if not isinstance(m.get("sourceCandidate"),str) or not _SHA40.fullmatch(m["sourceCandidate"]): raise VerifyError("SOURCE_CANDIDATE")
    files=m.get("files")
    if not isinstance(files,list) or not files: raise VerifyError("FILES")
    seen=set(); folded=set()
    for r in files:
        if not isinstance(r,dict) or set(r)!={"path","size","sha256","role","sourcePath","gitBlobSha1"}: raise VerifyError("FILE_RECORD")
        p=safe(r["path"]); k=key(p)
        if p in seen or k in folded: raise VerifyError(f"DUPLICATE_MEMBER: {p}")
        seen.add(p); folded.add(k)
        if type(r["size"]) is not int or r["size"]<0: raise VerifyError(f"SIZE: {p}")
        if not isinstance(r["sha256"],str) or not _SHA64.fullmatch(r["sha256"]): raise VerifyError(f"SHA256: {p}")
        if r["gitBlobSha1"] is not None and (not isinstance(r["gitBlobSha1"],str) or not _SHA40.fullmatch(r["gitBlobSha1"])): raise VerifyError(f"GIT_BLOB: {p}")
    if m.get("payloadAggregateSha256")!=aggregate(files): raise VerifyError("AGGREGATE")
    proof=m.get("proofAuthority")
    if not isinstance(proof,dict) or proof.get("r0_2RealWofPassAvailable") is not False or proof.get("r0_4RealWofForkPassAvailable") is not False: raise VerifyError("PROOF_BOUNDARY")
    return m

def verify_extracted(root: Path) -> dict[str,object]:
    root=root.resolve(strict=False); mp=root/INNER_MANIFEST
    if not mp.is_file(): raise VerifyError("MISSING_MANIFEST")
    m=validate_manifest(json.loads(mp.read_text(encoding="utf-8")))
    expected={INNER_MANIFEST}|{str(r["path"]) for r in m["files"]}; observed=set(); folded=set()
    for p in root.rglob("*"):
        rel=p.relative_to(root).as_posix()
        if p.is_symlink(): raise VerifyError(f"SYMLINK: {rel}")
        if p.is_dir(): continue
        safe(rel); k=key(rel)
        if rel in observed or k in folded: raise VerifyError(f"DUPLICATE_MEMBER: {rel}")
        observed.add(rel); folded.add(k)
    if observed!=expected: raise VerifyError(f"FILESET_DRIFT: missing={sorted(expected-observed)} extra={sorted(observed-expected)}")
    for r in m["files"]:
        p=root/Path(*PurePosixPath(str(r["path"])).parts); data=p.read_bytes()
        if len(data)!=r["size"] or sha256(data)!=r["sha256"]: raise VerifyError(f"PAYLOAD_TAMPERED: {r['path']}")
        if r["gitBlobSha1"] is not None and git_blob(data)!=r["gitBlobSha1"]: raise VerifyError(f"GIT_BLOB_TAMPERED: {r['path']}")
    return {"status":"PASS","sourceCandidate":m["sourceCandidate"],"payloadAggregateSha256":m["payloadAggregateSha256"],"containsRomBytes":False,"realWofProof":False,"r0_5Authorized":False}

def verify_zip(path: Path) -> dict[str,object]:
    with zipfile.ZipFile(path,"r") as z:
        names=[]; folded=set()
        for info in z.infolist():
            n=safe(info.filename); k=key(n)
            if info.is_dir() or n in names or k in folded: raise VerifyError(f"DUPLICATE_OR_DIRECTORY: {n}")
            if info.date_time!=FIXED_ZIP_TIMESTAMP or info.compress_type!=zipfile.ZIP_STORED: raise VerifyError(f"NONDETERMINISTIC_ZIP: {n}")
            names.append(n); folded.add(k)
        if INNER_MANIFEST not in names: raise VerifyError("MISSING_MANIFEST")
        m=validate_manifest(json.loads(z.read(INNER_MANIFEST).decode("utf-8")))
        expected={INNER_MANIFEST}|{str(r["path"]) for r in m["files"]}
        if set(names)!=expected: raise VerifyError(f"FILESET_DRIFT: missing={sorted(expected-set(names))} extra={sorted(set(names)-expected)}")
        for r in m["files"]:
            data=z.read(str(r["path"]))
            if len(data)!=r["size"] or sha256(data)!=r["sha256"]: raise VerifyError(f"PAYLOAD_TAMPERED: {r['path']}")
            if r["gitBlobSha1"] is not None and git_blob(data)!=r["gitBlobSha1"]: raise VerifyError(f"GIT_BLOB_TAMPERED: {r['path']}")
    raw=path.read_bytes(); return {"status":"PASS","sourceCandidate":m["sourceCandidate"],"zipSha256":sha256(raw),"zipSize":len(raw),"containsRomBytes":False,"realWofProof":False,"r0_5Authorized":False}

def main(argv=None)->int:
    ap=argparse.ArgumentParser(); g=ap.add_mutually_exclusive_group(required=True); g.add_argument("--bundle-root"); g.add_argument("--zip"); a=ap.parse_args(argv)
    try: out=verify_extracted(Path(a.bundle_root)) if a.bundle_root else verify_zip(Path(a.zip)); print(json.dumps(out,ensure_ascii=False,sort_keys=True)); return 0
    except (VerifyError,OSError,UnicodeError,json.JSONDecodeError,zipfile.BadZipFile) as e: print(json.dumps({"status":"BLOCKED","reason":f"{type(e).__name__}: {e}","realWofProof":False,"r0_5Authorized":False},ensure_ascii=False,sort_keys=True)); return 5
if __name__=="__main__": raise SystemExit(main())
