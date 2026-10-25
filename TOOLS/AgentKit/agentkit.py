#!/usr/bin/env python3
"""AgentKit: environment-first AI probe helpers; Python stdlib only."""
import argparse, datetime as dt, json, os, re, shutil, subprocess, sys, time
from pathlib import Path
from agentkit_process import run_process
VERSION="0.1.0"
SKIP={".git",".hg",".svn","node_modules",".venv","venv","__pycache__","target","dist","build"}
TOOLS="git has isetup curl wget tar unzip zip find grep rg fd tree strace ltrace perf valgrind gdb lldb readelf objdump ldd lddtree nm file jq yq shellcheck hyperfine python3 python node npm pnpm bun deno rustc cargo gcc g++ clang clang++ go javac wasmtime wasm-tools timeout date sha256sum".split()
FORMATS={".py":["python3","python"],".js":["node"],".mjs":["node"],".ts":["tsc","node"],".tsx":["tsc","node"],".rs":["rustc","cargo"],".c":["cc","gcc","clang"],".h":["cc","gcc","clang"],".cc":["c++","g++","clang++"],".cpp":["c++","g++","clang++"],".go":["go"],".java":["javac"],".sh":["bash","sh"],".json":["jq","python3"],".yaml":["yq","python3"],".yml":["yq","python3"],".toml":["python3"],".xml":["xmllint","python3"],".wasm":["wasmtime","wasm-tools"],".so":["readelf","objdump"],".a":["ar","nm"],".o":["readelf","objdump"]}
def now(): return dt.datetime.now().astimezone()
def caps():
    commands=[{"name":x,"path":shutil.which(x)} for x in TOOLS if shutil.which(x)]
    formats={e:{"available":any(shutil.which(t) for t in ts),"tools":[t for t in ts if shutil.which(t)]} for e,ts in FORMATS.items()}
    return commands,formats
def scan(root,limit):
    files=[]
    for cur,dirs,names in os.walk(root):
        dirs[:]=sorted(d for d in dirs if d not in SKIP and not d.startswith(".cache"))
        for name in sorted(names):
            p=Path(cur)/name
            try: files.append({"path":p.relative_to(root).as_posix(),"suffix":p.suffix.lower(),"bytes":p.stat().st_size})
            except OSError: continue
            if len(files)>=limit: return files,True
    return files,False
def paginate(files):
    n=len(files); print("候補ファイル数:",n)
    if n<=49:
        print("49件以下のためページ選択を省略し全件表示")
        for x in files: print(f"{x['path']}\t{x['bytes']} B\t{x['suffix'] or '[no extension]'}")
        return
    print("ページサイズ: 50 / 100 / 200 / 500 / MAX")
    try: raw=input("選択 [50/100/200/500/MAX] (既定50): ").strip().upper()
    except EOFError: raw=""
    size=n if raw=="MAX" else min(int(raw),n) if raw in {"50","100","200","500"} else min(50,n)
    for start in range(0,n,size):
        chunk=files[start:start+size]
        print(f"--- page {start//size+1}/{(n+size-1)//size}; items {start+1}-{start+len(chunk)} ---")
        for x in chunk: print(f"{x['path']}\t{x['bytes']} B\t{x['suffix'] or '[no extension]'}")
        if start+size<n:
            try: more=input("次ページ [Enter=続行, q=終了]: ").strip().lower()
            except EOFError: more="q"
            if more=="q": break
def probe(a):
    root=Path(a.root).expanduser().resolve()
    if not root.is_dir(): print(f"ERROR: 探査ルートがディレクトリではありません: {root}",file=sys.stderr); return 2
    commands,formats=caps(); files,truncated=scan(root,max(1,a.max_scan))
    report={"version":VERSION,"local_time":now().isoformat(timespec="seconds"),"utc_time":dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),"root":str(root),"commands_found":commands,"format_capabilities":formats,"candidate_count":len(files),"scan_truncated":truncated,"files":files}
    print(f"AgentKit {VERSION} | root={root} | commands={len(commands)}/{len(TOOLS)}")
    for c in commands: print(f"  {c['name']}: {c['path']}")
    print("\n形式別の実行/解析候補:")
    for ext,v in formats.items():
        if v["available"]: print(f"  {ext}: YES ({', '.join(v['tools'])})")
    if truncated: print("WARNING: 最大走査件数に到達。候補数は下限です。")
    if a.json: Path(a.json).write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print("JSON:",Path(a.json).resolve())
    if a.list_files: paginate(files)
    print("判断: 既存コマンドを優先。存在確認だけでは対象コードの動作保証になりません。")
    return 0
def fetch_probe(a):
    if not shutil.which("git"):
        print("ERROR: gitなし。終了。", file=sys.stderr)
        return 2
    print(f"読み取り専用リポジトリ到達性テスト（1回のみ）: {a.url}; timeout={a.timeout}s")
    try:
        result = run_process(
            ["git", "ls-remote", "--heads", a.url],
            timeout=a.timeout,
            output_limit=4000,
            progress_interval=1.0,
            on_progress=lambda elapsed, remaining: print(
                f"更新中（経過秒数: {min(a.timeout, int(elapsed) + 1)}/{a.timeout}）…",
                flush=True,
            ),
        )
    except (OSError, ValueError) as exc:
        print(f"ERROR: 起動失敗: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    if result["status"] == "TIMEOUT":
        print(f"タイムアウト: 経過秒数 {a.timeout}/{a.timeout}。子プロセスを終了し、再試行せず停止。")
        return 124
    if result["status"] == "UNAVAILABLE":
        print(f"ERROR: 起動失敗: {result.get('launch_error')}", file=sys.stderr)
        return 2
    if result["returncode"]:
        print(f"ERROR: 初回テスト失敗 (exit={result['returncode']})")
        if str(result["stderr"]).strip():
            print("詳細:", str(result["stderr"]).strip()[-500:])
        if result.get("stderr_truncated"):
            print("詳細は末尾のみ保持されています。", file=sys.stderr)
        print("仕様により取得を再試行しません。")
        return int(result["returncode"]) or 1
    ref_count = int(result["stdout_line_count"])
    print(f"取得経路OK: refs={ref_count}; clone/downloadは未実施")
    if result["stdout_truncated"]:
        print("INFO: stdout 全量は ref 数に反映済み。診断用バッファのみ上限で切り詰めました。")
    if result.get("capture_error"):
        print(f"ERROR: 出力処理に失敗: {result['capture_error']}", file=sys.stderr)
        return 1
    return 0
def locate(a):
    p=Path(a.file).expanduser()
    if not p.is_file(): print("ERROR: ファイルなし:",p,file=sys.stderr); return 2
    lines=p.read_text(encoding="utf-8",errors="replace").splitlines(); start=max(1,a.start); end=min(len(lines),a.end or start+39)
    if start>len(lines): print(f"ERROR: 開始行が行数を超過 (total={len(lines)})",file=sys.stderr); return 2
    for i in range(start,end+1): print(f"{i:>{len(str(end))}} | {lines[i-1]}")
    return 0
def save_note(content,name,source):
    name=re.sub(r"[^A-Za-z0-9_-]+","_",name).strip("_") or "note"
    stamp=now().strftime("%Y%m%d-%H%M%S"); dirs=[]
    if os.getenv("AGENTKIT_NOTES_DIR"): dirs.append(Path(os.environ["AGENTKIT_NOTES_DIR"]).expanduser())
    dirs += [Path.home()/".cache"/"agentkit"/"notes",Path.cwd()/".agentkit-notes"]
    for d in dirs:
        try:
            d.mkdir(parents=True,exist_ok=True); t=d/".write-test"; t.write_text("ok"); t.unlink()
            dest=d/f"{stamp}-{name}.md"; dest.write_text(f"# Note\n\nCreated: {now().isoformat(timespec='seconds')}\nSource: {source}\n\n{content.rstrip()}\n",encoding="utf-8")
            print("メモ保存成功:",dest); return 0
        except Exception as e: print(f"保存先失敗 {d}: {type(e).__name__}",file=sys.stderr)
    print("WARNING: 保存先なし。stdoutへフォールバック。",file=sys.stderr); print(content); return 0
def note(a):
    content=Path(a.file).expanduser().read_text(encoding="utf-8",errors="replace") if a.file else a.text
    return save_note(content,a.name,a.source)
def ingest(a):
    if a.file=="-": content=sys.stdin.read(); source="stdin"
    else: p=Path(a.file).expanduser(); content=p.read_text(encoding="utf-8",errors="replace"); source=str(p.resolve())
    lines=content.splitlines()
    if a.query:
        hits=[(i,x) for i,x in enumerate(lines,1) if a.query.casefold() in x.casefold()]
        if not hits: print("一致なし:",a.query); return 1
        for i,x in hits: print(f"{i}: {x}")
    else:
        print(f"入力元={source}; 行数={len(lines)}; 文字数={len(content)}")
        if a.print_content: print(content)
    if a.save: return save_note("Imported source: "+source+"\n\n"+content,"conversation-import",source)
    return 0
def timer(a):
    start=now(); end=start+dt.timedelta(seconds=a.seconds)
    print("開始(local):",start.isoformat(timespec="seconds")); print("終了予定(local):",end.isoformat(timespec="seconds")); print("終了予定(UTC):",end.astimezone(dt.timezone.utc).isoformat(timespec="seconds"))
    if a.prompt: print("案内: タイマー終了まで、独立して進められる別タスクへ移ると効率的です。")
    deadline=time.monotonic()+a.seconds; last=None
    while True:
        remain=max(0,int(deadline-time.monotonic()+.999))
        if remain!=last: print("残り秒数:",remain,flush=True); last=remain
        if remain<=0: break
        time.sleep(min(1,remain))
    print("終了実時刻(local):",now().isoformat(timespec="seconds")); print("タイマー終了"); return 0
def versions(a):
    commands,formats=caps(); lines=["# AgentKit Capability Table","",f"AgentKit: {VERSION}",f"Generated local: {now().isoformat(timespec='seconds')}",f"Generated UTC: {dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')}",f"Root: {Path(a.root).expanduser().resolve()}","","## Commands","","| Command | Path | Version (best effort) |","|---|---|---|"]
    for c in commands:
        try: v=subprocess.run([c["name"],"--version"],capture_output=True,text=True,timeout=2).stdout.strip().splitlines()
        except Exception: v=[]
        lines.append(f"| {c['name']} | {c['path']} | {(v or ['unknown'])[0][:120]} |")
    lines += ["","## Format capability hints","","| Format | Available | Tools |","|---|---|---|"]
    for ext,v in formats.items(): lines.append(f"| {ext} | {'yes' if v['available'] else 'no'} | {', '.join(v['tools']) or 'none'} |")
    output="\n".join(lines)+"\n"
    if a.output: Path(a.output).write_text(output,encoding="utf-8"); print("更新:",Path(a.output).resolve())
    else: print(output)
    return 0
def main():
    p=argparse.ArgumentParser(prog="agentkit",description="AI-first environment probe and workflow helpers"); p.add_argument("--version",action="version",version=VERSION)
    s=p.add_subparsers(dest="cmd",required=True)
    x=s.add_parser("probe"); x.add_argument("--root",default="."); x.add_argument("--json"); x.add_argument("--list-files",action="store_true"); x.add_argument("--max-scan",type=int,default=100000); x.set_defaults(fn=probe)
    x=s.add_parser("fetch-probe"); x.add_argument("url"); x.add_argument("--timeout",type=int,default=5,choices=range(1,31)); x.set_defaults(fn=fetch_probe)
    x=s.add_parser("locate"); x.add_argument("file"); x.add_argument("--start",type=int,required=True); x.add_argument("--end",type=int); x.set_defaults(fn=locate)
    x=s.add_parser("note"); x.add_argument("text",nargs="?",default=""); x.add_argument("--file"); x.add_argument("--name",default="note"); x.add_argument("--source",default="manual"); x.set_defaults(fn=note)
    x=s.add_parser("ingest"); x.add_argument("file"); x.add_argument("--query"); x.add_argument("--print-content",action="store_true"); x.add_argument("--save",action="store_true"); x.set_defaults(fn=ingest)
    x=s.add_parser("timer"); x.add_argument("seconds",type=int); x.add_argument("--prompt",action="store_true"); x.set_defaults(fn=timer)
    x=s.add_parser("versions"); x.add_argument("--root",default="."); x.add_argument("--output"); x.set_defaults(fn=versions)
    a=p.parse_args()
    try: return a.fn(a)
    except KeyboardInterrupt: print("中断。開始/終了予定時刻は表示済みの値を参照してください。",file=sys.stderr); return 130
    except Exception as e: print(f"ERROR: {type(e).__name__}: {e}",file=sys.stderr); return 1
if __name__=="__main__": raise SystemExit(main())
