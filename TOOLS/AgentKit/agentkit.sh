#!/bin/sh
# Reduced fallback for systems without Python. Supports probe only.
set -f
COMMANDS="git has isetup curl wget tar unzip zip find grep rg fd tree strace ltrace perf valgrind gdb lldb readelf objdump ldd lddtree nm file jq yq shellcheck hyperfine python3 python node npm pnpm bun deno rustc cargo gcc g++ clang clang++ go javac wasmtime wasm-tools timeout date sha256sum"
usage() {
  echo "AgentKit shell fallback 0.1.0"
  echo "Usage: agentkit.sh probe [--root DIR] [--list-files]"
}
if [ "$#" -lt 1 ]; then usage; exit 2; fi
ACTION=$1
shift
if [ "$ACTION" != "probe" ]; then
  echo "ERROR: shell fallback supports only 'probe'; use Python implementation for other commands." >&2
  exit 2
fi
ROOT=.
LIST=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --root) shift; if [ "$#" -eq 0 ]; then echo "ERROR: --root needs a path" >&2; exit 2; fi; ROOT=$1 ;;
    --list-files) LIST=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: unsupported argument: $1" >&2; usage; exit 2 ;;
  esac
  shift
done
if [ ! -d "$ROOT" ]; then echo "ERROR: search root is not a directory: $ROOT" >&2; exit 2; fi
echo "AgentKit shell fallback 0.1.0"
echo "探査ルート: $(cd "$ROOT" 2>/dev/null && pwd)"
echo "検出コマンド:"
for tool in $COMMANDS; do
  if command -v "$tool" >/dev/null 2>&1; then
    printf "  %-14s %s\n" "$tool" "$(command -v "$tool")"
  fi
done
if [ "$LIST" -eq 1 ]; then
  if ! command -v find >/dev/null 2>&1; then
    echo "ERROR: find is unavailable; command inventory completed, file scan skipped." >&2
    exit 0
  fi
  TMP=$(mktemp 2>/dev/null) || { echo "ERROR: cannot create temporary list; command inventory completed." >&2; exit 0; }
  trap 'rm -f "$TMP"' 0 HUP INT TERM
  find "$ROOT" -type d \( -name .git -o -name node_modules -o -name .venv -o -name venv -o -name target -o -name dist -o -name build \) -prune -o -type f -print 2>/dev/null | sort > "$TMP"
  COUNT=$(wc -l < "$TMP" | tr -d ' ')
  echo "候補ファイル数: $COUNT"
  if [ "$COUNT" -le 49 ]; then
    echo "49件以下のためページ選択を省略し全件表示します。"
    cat "$TMP"
  else
    echo "ページサイズ: 50 / 100 / 200 / 500 / MAX"
    printf "選択 [50/100/200/500/MAX] (既定50): "
    read SIZE
    case "$SIZE" in
      100|200|500) ;;
      MAX) SIZE=$COUNT ;;
      *) SIZE=50 ;;
    esac
    START=1
    while [ "$START" -le "$COUNT" ]; do
      END=$((START + SIZE - 1))
      if [ "$END" -gt "$COUNT" ]; then END=$COUNT; fi
      echo "--- page $(((START - 1) / SIZE + 1)); items $START-$END ---"
      awk -v s="$START" -v e="$END" 'NR >= s && NR <= e' "$TMP"
      START=$((END + 1))
      if [ "$START" -le "$COUNT" ]; then
        printf "次ページ [Enter=続行, q=終了]: "
        read MORE
        if [ "$MORE" = "q" ]; then break; fi
      fi
    done
  fi
fi
echo "注意: shell fallbackはコマンド存在確認とファイル列挙のみ。形式対応判定、JSON、メモ、タイマー等はPython版を使用してください。"
exit 0
