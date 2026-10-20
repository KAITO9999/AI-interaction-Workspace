#!/usr/bin/env python3
"""Probe HTTPS HEAD and bounded GET routes; does not install or execute downloads."""
import argparse,json,sys,urllib.request,urllib.error,socket,ipaddress
from urllib.parse import urlsplit
from pathlib import Path
from datetime import datetime,timezone

def validate_public_https(url):
 parts=urlsplit(url)
 if parts.scheme!="https" or not parts.hostname or parts.username or parts.password:
  raise ValueError("only credential-free HTTPS URLs are accepted")
 try: addresses={item[4][0] for item in socket.getaddrinfo(parts.hostname,parts.port or 443,type=socket.SOCK_STREAM)}
 except OSError as exc: raise ValueError(f"could not resolve host: {exc}") from exc
 for address in addresses:
  ip=ipaddress.ip_address(address)
  if not ip.is_global: raise ValueError(f"refusing non-public destination address: {address}")
 return url

class PublicRedirectHandler(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  validate_public_https(newurl)
  return super().redirect_request(req,fp,code,msg,headers,newurl)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("url");p.add_argument("--timeout",type=float,default=5);p.add_argument("--output",default="route-probe.json");p.add_argument("--alternate-url",action="append",default=[]);p.add_argument("--github-ref");p.add_argument("--plan-only",action="store_true");a=p.parse_args()
 if not .5<=a.timeout<=15:print("ERROR: timeout must be 0.5–15 seconds",file=sys.stderr);return 2
 urls=[a.url,*a.alternate_url]
 parts=urlsplit(a.url)
 if a.github_ref and parts.hostname=="github.com":
  segments=[x for x in parts.path.strip("/").split("/") if x]
  if len(segments)==2:
   owner,repo=segments
   ref=a.github_ref
   urls.extend([f"https://github.com/{owner}/{repo}/archive/refs/heads/{ref}.zip",
                f"https://codeload.github.com/{owner}/{repo}/zip/refs/heads/{ref}",
                f"https://api.github.com/repos/{owner}/{repo}/zipball/{ref}"])
 urls=list(dict.fromkeys(urls))
 try:
  for url in urls:
   if a.plan_only:
    if not url.startswith("https://"):raise ValueError("only HTTPS URLs are accepted")
   else:validate_public_https(url)
 except ValueError as e:print(f"ERROR: {e}",file=sys.stderr);return 2
 if a.plan_only:
  report={"generated_utc":datetime.now(timezone.utc).isoformat(),"mode":"plan-only","url_candidates":[{"url":url,"methods":["HEAD","GET Range bytes=0-0","GET Range bytes=0-4095"]} for url in urls],
          "limitations":["Plan-only lists candidate URL routes; it does not prove DNS resolution, authentication, permission, or download success."]}
  try:Path(a.output).write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\\n",encoding="utf-8")
  except OSError as e:print(f"ERROR: cannot write report: {e}",file=sys.stderr);return 2
  print(json.dumps(report,ensure_ascii=False));return 0
 rows=[]
 for url in urls:
  for label,method,headers in [("HEAD","HEAD",{}),("GET-range","GET",{"Range":"bytes=0-0"}),("GET-small","GET",{"Range":"bytes=0-4095"})]:
   try:
    req=urllib.request.Request(url,method=method,headers={"User-Agent":"AgentKit-route-probe/1.0",**headers})
    opener=urllib.request.build_opener(PublicRedirectHandler)
    with opener.open(req,timeout=a.timeout) as r:
     if method=="GET":r.read(4096)
     rows.append({"url":url,"route":label,"ok":True,"status":r.status,"content_type":r.headers.get("Content-Type"),"content_length":r.headers.get("Content-Length"),"final_url":r.geturl()})
   except (OSError,urllib.error.URLError,TimeoutError) as e:rows.append({"url":url,"route":label,"ok":False,"error":f"{type(e).__name__}: {e}"})
 report={"generated_utc":datetime.now(timezone.utc).isoformat(),"url":a.url,"url_candidates":urls,"routes":rows,"limitations":["Probes only unauthenticated URL-level HTTP access, not MCP, browser login, repository permissions, or full artifact download.","GET routes read at most 4096 bytes."]}
 try:Path(a.output).write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 except OSError as e:print(f"ERROR: cannot write report: {e}",file=sys.stderr);return 2
 print(json.dumps(report,ensure_ascii=False));return 0 if any(x["ok"] for x in rows) else 1
if __name__=="__main__":raise SystemExit(main())
