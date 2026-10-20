#!/usr/bin/env python3
"""Ten-slot copy-on-write editor for inspection during editing; originals stay unchanged until explicit apply."""
import argparse,hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone
SLOTS=[f"virtual-{i:02d}" for i in range(1,11)]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--root",default=".");s=p.add_subparsers(dest="action",required=True)
 st=s.add_parser("stage");st.add_argument("file");st.add_argument("--replace",required=True);st.add_argument("--with",dest="replacement",required=True);st.add_argument("--slot",choices=SLOTS,default=SLOTS[0])
 sh=s.add_parser("show");sh.add_argument("file");sh.add_argument("--slot",choices=SLOTS,default=SLOTS[0])
 li=s.add_parser("list");li.add_argument("--slot",choices=SLOTS)
 ap=s.add_parser("apply");ap.add_argument("file");ap.add_argument("--slot",choices=SLOTS,default=SLOTS[0]);ap.add_argument("--yes",action="store_true")
 a=p.parse_args();root=Path(a.root).resolve()
 if not root.is_dir():print("ERROR: root is not a directory",file=sys.stderr);return 2
 base=root/".agentkit-virtual-edit";state=base/"manifest.json"
 try:
  base.mkdir(parents=True,exist_ok=True);m=json.loads(state.read_text(encoding="utf-8")) if state.exists() else {"schema_version":1,"slots":{}}
  for slot in SLOTS:m["slots"].setdefault(slot,{})
  if a.action=="stage":
   src=(root/a.file).resolve()
   if not src.is_relative_to(root) or not src.is_file():raise ValueError("source must be an existing file under --root")
   original=src.read_text(encoding="utf-8")
   if a.replace not in original:raise ValueError("replacement target not found; nothing staged")
   overlay=base/a.slot/a.file;overlay.parent.mkdir(parents=True,exist_ok=True);overlay.write_text(original.replace(a.replace,a.replacement),encoding="utf-8")
   m["slots"][a.slot][a.file]={"overlay":str(overlay.relative_to(root)),"original_sha256":hashlib.sha256(src.read_bytes()).hexdigest(),"staged_utc":datetime.now(timezone.utc).isoformat()}
   state.write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(f"Staged {a.file} in {a.slot}; original unchanged. 10 isolated virtual slots available.");return 0
  if a.action=="show":
   e=m["slots"][a.slot].get(a.file)
   if not e:raise ValueError("no staged overlay")
   print(f"[{a.slot}] staged overlay; 10 isolated virtual slots available")
   print((root/e["overlay"]).read_text(encoding="utf-8"),end="");return 0
  if a.action=="list":
   for slot in ([a.slot] if a.slot else SLOTS):
    for name,e in sorted(m["slots"][slot].items()):print(f"{slot}\t{name}\t{e['overlay']}")
   print("10 isolated virtual slots available.");return 0
  if a.action=="apply":
   if not a.yes:raise ValueError("apply writes the original; review overlay then repeat with --yes")
   src=(root/a.file).resolve();e=m["slots"][a.slot].get(a.file)
   if not src.is_relative_to(root) or not src.is_file() or not e:raise ValueError("invalid source or missing overlay")
   if hashlib.sha256(src.read_bytes()).hexdigest()!=e["original_sha256"]:raise ValueError("original changed since staging; refusing to overwrite")
   overlay=(root/e["overlay"]).resolve()
   if not overlay.is_relative_to(base.resolve()):raise ValueError("overlay escaped virtual edit directory")
   src.write_text(overlay.read_text(encoding="utf-8"),encoding="utf-8");print(f"Applied overlay to {a.file}");return 0
 except (OSError,ValueError,json.JSONDecodeError) as e:print(f"ERROR: {e}",file=sys.stderr);return 2
 return 2
if __name__=="__main__":raise SystemExit(main())
