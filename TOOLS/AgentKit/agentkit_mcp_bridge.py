#!/usr/bin/env python3
"""Local payload bridge: extract selected JSON/text/file payloads without printing whole documents. Not an MCP client."""
import argparse,json,sys,hashlib,mimetypes
from pathlib import Path
def pointer(v,p):
 if p in ("","/"):return v
 for token in p.lstrip("/").split("/"):
  token=token.replace("~1","/").replace("~0","~")
  if isinstance(v,list):
   try:v=v[int(token)]
   except (ValueError,IndexError) as e:raise ValueError("JSON pointer index missing") from e
  elif isinstance(v,dict) and token in v:v=v[token]
  else:raise ValueError(f"JSON pointer key missing: {token}")
 return v
def main():
 p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest="action",required=True)
 x=s.add_parser("extract-json");x.add_argument("source");x.add_argument("pointer");x.add_argument("--output",required=True);x.add_argument("--flow",choices=["mcp-to-gpt","gpt-to-mcp","mcp-via-gpt-to-mcp"],default="mcp-to-gpt")
 c=s.add_parser("copy-file");c.add_argument("source");c.add_argument("--output",required=True);c.add_argument("--flow",choices=["mcp-to-gpt","gpt-to-mcp","mcp-via-gpt-to-mcp"],default="mcp-to-gpt")
 t=s.add_parser("slice-text");t.add_argument("source");t.add_argument("--start-marker",required=True);t.add_argument("--end-marker",required=True);t.add_argument("--output",required=True);t.add_argument("--flow",choices=["mcp-to-gpt","gpt-to-mcp","mcp-via-gpt-to-mcp"],default="mcp-to-gpt")
 h=s.add_parser("hash");h.add_argument("source");h.add_argument("--flow",choices=["mcp-to-gpt","gpt-to-mcp","mcp-via-gpt-to-mcp"],default="mcp-to-gpt")
 a=p.parse_args();src=Path(a.source)
 try:
  if not src.is_file():raise ValueError(f"source not found: {src}")
  if a.action=="hash":print(json.dumps({"flow":a.flow,"bytes":src.stat().st_size,"sha256":hashlib.sha256(src.read_bytes()).hexdigest(),"media_type":mimetypes.guess_type(src.name)[0] or "application/octet-stream"}));return 0
  out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
  if src.resolve()==out.resolve():raise ValueError("output must not overwrite source")
  if a.action=="copy-file":out.write_bytes(src.read_bytes())
  elif a.action=="extract-json":out.write_text(json.dumps(pointer(json.loads(src.read_text(encoding="utf-8")),a.pointer),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
  else:
   data=src.read_text(encoding="utf-8");i=data.find(a.start_marker)
   if i<0:raise ValueError("start marker not found")
   i+=len(a.start_marker);j=data.find(a.end_marker,i)
   if j<0:raise ValueError("end marker not found")
   out.write_text(data[i:j],encoding="utf-8")
  print(json.dumps({"status":"written","flow":a.flow,"source":str(src),"output":str(out),"bytes":out.stat().st_size,"sha256":hashlib.sha256(out.read_bytes()).hexdigest(),"media_type":mimetypes.guess_type(out.name)[0] or "application/octet-stream","note":"Flow is provenance metadata only; use an authorized connector action to transfer this file to/from MCP."},ensure_ascii=False));return 0
 except (OSError,ValueError,json.JSONDecodeError) as e:print(f"ERROR: {e}",file=sys.stderr);return 2
if __name__=="__main__":raise SystemExit(main())
