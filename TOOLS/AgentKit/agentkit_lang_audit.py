#!/usr/bin/env python3
"""Read-only heuristic audit for native, Kotlin, graphics, Android API, and ABI requirements."""
import argparse,json,re,sys,os
from pathlib import Path
from datetime import datetime,timezone
EXT={".py":"python",".js":"javascript",".ts":"typescript",".tsx":"typescript",".c":"c",".h":"c-header",".cc":"cpp",".cpp":"cpp",".cxx":"cpp",".hpp":"cpp-header",".rs":"rust",".kt":"kotlin",".kts":"kotlin-script",".java":"java",".gradle":"gradle",".xml":"xml",".glsl":"glsl",".vert":"glsl",".frag":"glsl",".comp":"glsl",".cmake":"cmake",".toml":"toml",".mk":"make"}
SKIP={".git","node_modules",".venv","venv","build","dist","target",".gradle",".idea",".agentkit-logs"}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--root",default=".");p.add_argument("--json",default="language-audit.json");p.add_argument("--log-dir",default=".agentkit-logs");a=p.parse_args()
 root=Path(a.root).resolve()
 if not root.is_dir(): print("ERROR: root is not a directory",file=sys.stderr);return 2
 langs=set();files=[];findings=[];abis=set()
 patterns=[(r"\b(?:eval|exec)\s*\(","DYNAMIC_EXECUTION","HIGH","Dynamic execution candidate"),(r"\b(?:while\s*\(\s*true\s*\)|loop\s*\{)","UNBOUNDED_LOOP","MEDIUM","Potential unbounded loop"),(r"\bThread\.sleep\s*\(","BLOCKING_WAIT","MEDIUM","Blocking sleep candidate"),(r"\b(?:vkQueueWaitIdle|vkDeviceWaitIdle)\s*\(","VULKAN_SYNC","MEDIUM","Potential Vulkan global wait"),(r"\bglFinish\s*\(","OPENGL_SYNC","MEDIUM","Potential OpenGL full pipeline wait"),(r"\b(?:runOnUiThread|Dispatchers\.Main)\b","KOTLIN_UI","LOW","UI-thread dispatch candidate"),(r"\b(?:JNIEXPORT|extern\s+\"C\")\b","NATIVE_BOUNDARY","LOW","Native/JNI boundary candidate")]
 for cur,dirs,names in os.walk(root):
  dirs[:]=sorted(x for x in dirs if x not in SKIP)
  for name in sorted(names):
   path=Path(cur)/name;lang=EXT.get(path.suffix.lower())
   if not lang: continue
   try: src=path.read_text(encoding="utf-8",errors="replace")
   except OSError as e: print(f"ERROR: cannot read {path}: {e}",file=sys.stderr);return 2
   rel=str(path.relative_to(root));langs.add(lang);files.append({"path":rel,"language":lang,"bytes":path.stat().st_size,"lines":len(src.splitlines())})
   if re.search(r"arm64-v8a|aarch64|CMAKE_ANDROID_ARCH_ABI\s*[:=]\s*arm64",src,re.I):abis.add("arm64-v8a/AArch64")
   if re.search(r"x86_64|amd64",src,re.I):abis.add("x86_64")
   if re.search(r"(?<![A-Za-z0-9_])x86(?!_64)|i[3-6]86",src,re.I):abis.add("x86-32")
   for n,line in enumerate(src.splitlines(),1):
    t=line.strip()
    if not t or t.startswith(("//","*","#","<!--")):continue
    for pat,cat,conf,title in patterns:
     if re.search(pat,line):findings.append({"path":rel,"line":n,"category":cat,"priority":"HIGH" if conf=="HIGH" else "MEDIUM","title":title,"detail":t[:240],"detection_confidence":conf,"review_recommended":conf!="HIGH","evidence":"Line-level heuristic; not a parsed control-flow graph or compiler."})
   if path.name=="AndroidManifest.xml":
    m=re.search(r"<uses-sdk\b[^>]*\bandroid:minSdkVersion\s*=\s*[\"'](\d+)[\"']",src)
    if m and int(m.group(1))<30:findings.append({"path":rel,"line":1,"category":"ANDROID_SECURITY_BASELINE","priority":"HIGH","title":"Minimum Android API below configured baseline","detail":f"minSdkVersion={m.group(1)}; policy threshold is Android 11 / API 30.","detection_confidence":"HIGH","review_recommended":False,"evidence":"Explicit manifest value; API 30 is a project policy threshold, not a universal security guarantee."})
    gl=re.search(r"android:glEsVersion\s*=\s*[\"']0x([0-9a-fA-F]{8})[\"']",src)
    if gl:
     raw=int(gl.group(1),16);v=((raw>>16)&65535,(raw>>8)&255)
     if v<(3,0):findings.append({"path":rel,"line":1,"category":"GRAPHICS_BASELINE","priority":"HIGH","title":"OpenGL ES requirement below configured baseline","detail":f"Manifest declares {v[0]}.{v[1]}; baseline is 3.0.","detection_confidence":"HIGH","review_recommended":False,"evidence":"Explicit android:glEsVersion value; runtime GPU support still requires testing."})
    vk=re.search(r"<uses-feature\b(?=[^>]*android:name\s*=\s*[\"']android\.hardware\.vulkan\.version[\"'])[^>]*android:version\s*=\s*[\"']0x([0-9a-fA-F]{8})[\"']",src)
    if vk:
     raw=int(vk.group(1),16);v=((raw>>22)&1023,(raw>>12)&1023)
     if v<(1,1):findings.append({"path":rel,"line":1,"category":"VULKAN_BASELINE","priority":"HIGH","title":"Vulkan manifest requirement below configured baseline","detail":f"Manifest declares Vulkan {v[0]}.{v[1]}; project baseline is 1.1.","detection_confidence":"HIGH","review_recommended":False,"evidence":"Explicit android.hardware.vulkan.version feature; driver capabilities/extensions still require runtime checks."})
 report={"tool":"agentkit_lang_audit","generated_utc":datetime.now(timezone.utc).isoformat(),"root":str(root),"languages_detected":sorted(langs),"abis_detected":sorted(abis),"files":files,"findings":findings,"android_min_sdk":30,"opengl_es_minimum":"3.0","vulkan_policy":{"minimum_api":"1.1","rationale":"Recommended modern Android baseline; verify required features/extensions and driver support at runtime.","legacy_compatibility_level":"1.0","advanced_optional_level":"1.3","rationale_advanced":"Treat newer capabilities as optional unless target devices are intentionally restricted."},"native_abi_policy":{"arm64":"arm64-v8a / AArch64","x86_64":"x86_64 ISA; OS and ABI compatibility are separate","x86_32":"x86","warning":"Architecture names do not prove binary/OS/ABI/instruction-extension compatibility."},"limitations":["heuristic: only explicit manifest requirements are checked; no live device/GPU probing","heuristic: Kotlin UI and coroutine behavior are not semantically analyzed","heuristic: C/C++/Rust/shader code is not compiled or type-checked","heuristic: dynamic dispatch, macros, generated code, and false positives remain","Android API 30, OpenGL ES 3.0, and Vulkan 1.1 are configurable project baselines, not universal guarantees"]}
 out=Path(a.json);out=out if out.is_absolute() else root/out
 try:out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 except OSError as e:print(f"ERROR: cannot write report: {e}",file=sys.stderr);return 2
 log=Path(a.log_dir);log=log if log.is_absolute() else root/log
 try:
  log.mkdir(parents=True,exist_ok=True)
  with (log/"language-audit.jsonl").open("a",encoding="utf-8") as f:
   for x in findings:f.write(json.dumps(x,ensure_ascii=False)+"\n")
   f.write(json.dumps({"record_type":"summary","files":len(files),"languages":sorted(langs),"findings":len(findings)})+"\n")
 except OSError as e:print(f"ERROR: cannot append log: {e}",file=sys.stderr);return 2
 print(f"Languages: {', '.join(sorted(langs)) or '(none)'}; scanned {len(files)}; findings {len(findings)}; report {out}");return 0
if __name__=="__main__":raise SystemExit(main())
