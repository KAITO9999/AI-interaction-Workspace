#!/usr/bin/env python3
"""Package explicitly selected files into a ZIP bundle with hashes; no network or execution."""
import argparse,hashlib,json,sys,zipfile
from pathlib import Path
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--root",default=".");p.add_argument("--output",required=True);p.add_argument("--include",action="append",required=True);a=p.parse_args()
 root=Path(a.root).resolve();out=Path(a.output).resolve()
 if not root.is_dir():print("ERROR: root is not a directory",file=sys.stderr);return 2
 try:
  items=[]
  for n in a.include:
   f=(root/n).resolve()
   if not f.is_relative_to(root) or not f.is_file():raise ValueError(f"include must be an existing file under root: {n}")
   if f==out:raise ValueError("output cannot overwrite an included source")
   items.append((f,f.relative_to(root).as_posix()))
  if len({n for _,n in items})!=len(items):raise ValueError("duplicate include path")
  out.parent.mkdir(parents=True,exist_ok=True)
  with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
   manifest=[]
   for f,n in sorted(items,key=lambda x:x[1]):
    b=f.read_bytes();z.writestr(n,b);manifest.append({"path":n,"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()})
   z.writestr("AGENTKIT-BUNDLE-MANIFEST.json",json.dumps({"schema_version":1,"files":manifest},indent=2)+"\n")
  print(json.dumps({"bundle":str(out),"files":len(items),"bytes":out.stat().st_size,"sha256":hashlib.sha256(out.read_bytes()).hexdigest()}));return 0
 except (OSError,ValueError,zipfile.BadZipFile) as e:print(f"ERROR: {e}",file=sys.stderr);return 2
if __name__=="__main__":raise SystemExit(main())
