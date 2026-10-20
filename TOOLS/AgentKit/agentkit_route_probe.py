#!/usr/bin/env python3
"""Probe HTTPS HEAD and bounded GET routes; does not install or execute downloads."""
import argparse,json,sys,urllib.request,urllib.error
from pathlib import Path
from datetime import datetime,timezone
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("url");p.add_argument("--timeout",type=float,default=5);p.add_argument("--output",default="route-probe.json");a=p.parse_args()
 if not a.url.startswith("https://"):print("ERROR: HTTPS only",file=sys.stderr);return 2
 if not .5<=a.timeout<=15:print("ERROR: timeout must be 0.5–15 seconds",file=sys.stderr);return 2
 rows=[]
 for label,method,headers in [("HEAD","HEAD",{}),("GET-range","GET",{"Range":"bytes=0-0"}),("GET-small","GET",{"Range":"bytes=0-4095"})]:
  try:
   req=urllib.request.Request(a.url,method=method,headers={"User-Agent":"AgentKit-route-probe/1.0",**headers})
   with urllib.request.urlopen(req,timeout=a.timeout) as r:
    if method=="GET":r.read(4096)
    rows.append({"route":label,"ok":True,"status":r.status,"content_type":r.headers.get("Content-Type"),"content_length":r.headers.get("Content-Length"),"final_url":r.geturl()})
  except (OSError,urllib.error.URLError,TimeoutError) as e:rows.append({"route":label,"ok":False,"error":f"{type(e).__name__}: {e}"})
 report={"generated_utc":datetime.now(timezone.utc).isoformat(),"url":a.url,"routes":rows,"limitations":["Probes only unauthenticated URL-level HTTP access, not MCP, browser login, repository permissions, or full artifact download.","GET routes read at most 4096 bytes."]}
 try:Path(a.output).write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 except OSError as e:print(f"ERROR: cannot write report: {e}",file=sys.stderr);return 2
 print(json.dumps(report,ensure_ascii=False));return 0 if any(x["ok"] for x in rows) else 1
if __name__=="__main__":raise SystemExit(main())
