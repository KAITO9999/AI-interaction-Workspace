#!/usr/bin/env python3
"""Report useful lightweight CLI availability and print reviewed install commands."""
from __future__ import annotations
import argparse, json, os, platform, shutil, sys

TOOLS = {
    "git": ("Git/version control", "git", "git"),
    "gh": ("GitHub CLI", "gh", "gh"),
    "rg": ("Fast text search", "ripgrep", "ripgrep"),
    "tree": ("Directory tree", "tree", "tree"),
    "shellcheck": ("Shell static analysis", "shellcheck", "shellcheck"),
    "jq": ("JSON query/validation", "jq", "jq"),
    "pytest": ("Python tests", "pytest", "python3-pytest"),
    "ruff": ("Python lint/format", "ruff", "ruff"),
    "tsc": ("TypeScript compiler", "typescript", "node-typescript"),
    "node": ("JavaScript runtime", "nodejs", "nodejs"),
    "npm": ("JavaScript package manager", "nodejs", "npm"),
    "rustc": ("Rust compiler", "rust", "rustc"),
    "cargo": ("Rust package/build manager", "rust", "cargo"),
    "clang": ("C/C++ toolchain", "clang", "clang"),
    "cmake": ("Native build configuration", "cmake", "cmake"),
    "ninja": ("Fast build runner", "ninja", "ninja-build"),
    "pkg-config": ("Native dependency discovery", "pkg-config", "pkg-config"),
    "strace": ("System-call tracing", "strace", "strace"),
    "lsof": ("Open-file inspection", "lsof", "lsof"),
    "rsync": ("Incremental file sync", "rsync", "rsync"),
}
def detect_platform(requested):
    if requested != "auto": return requested
    if "com.termux" in os.environ.get("PREFIX", ""): return "termux"
    if shutil.which("apt-get"): return "debian"
    return "unknown"
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--platform", choices=("auto","termux","debian","unknown"), default="auto")
    p.add_argument("--only-missing", action="store_true")
    p.add_argument("--format", choices=("markdown","json"), default="markdown")
    a=p.parse_args()
    plat=detect_platform(a.platform)
    items=[]
    for name,(purpose,termux_pkg,debian_pkg) in TOOLS.items():
        path=shutil.which(name)
        items.append({"command":name,"purpose":purpose,"installed":bool(path),"path":path,
                      "termux_package":termux_pkg,"debian_package":debian_pkg})
    installed=[x for x in items if x["installed"]]
    missing=[x for x in items if not x["installed"]]
    packages=sorted({x["termux_package" if plat=="termux" else "debian_package"] for x in missing})
    if plat=="termux":
        pkg_cmd="pkg install "+" ".join(packages)
        pip_cmd="python -m pip install pytest" if any(x["command"]=="pytest" for x in missing) else ""
        npm_cmd="npm install --global typescript" if any(x["command"]=="tsc" for x in missing) else ""
    elif plat=="debian":
        pkg_cmd="sudo apt-get install "+" ".join(packages)
        pip_cmd="python3 -m pip install pytest  # prefer a venv if externally-managed"
        npm_cmd="npm install --global typescript"
        if not any(x["command"]=="pytest" for x in missing): pip_cmd=""
        if not any(x["command"]=="tsc" for x in missing): npm_cmd=""
    else:
        pkg_cmd=pip_cmd=npm_cmd=""
    report={"platform":plat,"installed":installed,"missing":missing,
            "install_commands":[x for x in (pkg_cmd,pip_cmd,npm_cmd) if x],
            "notes":["Discovery checks PATH only; it does not execute discovered tools.",
                     "No packages are installed automatically.",
                     "Review package names and commands for the target distribution before running them."]}
    if a.format=="json":
        print(json.dumps(report,ensure_ascii=False,indent=2)); return 0
    print(f"Platform: {plat}\nInstalled useful tools: {len(installed)} / {len(items)}")
    show=missing if a.only_missing else installed
    heading="Missing tools" if a.only_missing else "Available tools"
    print(f"\n## {heading}")
    for x in show: print(f"- {'MISSING' if not x['installed'] else 'OK'} {x['command']}: {x['purpose']}" + (f" — {x['path']}" if x["path"] else ""))
    if not a.only_missing:
        print("\n## Missing")
        for x in missing: print(f"- {x['command']}: {x['purpose']}")
    print("\n## Suggested install commands (not executed)")
    if report["install_commands"]:
        for cmd in report["install_commands"]: print(f"  {cmd}")
    else: print("No automatic command suggestion for this platform.")
    for note in report["notes"]: print(f"NOTE: {note}")
    return 0
if __name__=="__main__": raise SystemExit(main())
