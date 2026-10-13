#!/bin/sh
# Installs the standalone Python stdlib-only toolplan CLI; does not install packages.
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SOURCE="$HERE/toolplan.py"
if [ ! -f "$SOURCE" ]; then echo "ERROR: toolplan.py not found beside installer." >&2; exit 2; fi
if [ -n "${AGENTKIT_BIN_DIR:-}" ]; then
  BIN_DIR=$AGENTKIT_BIN_DIR
elif [ -n "${PREFIX:-}" ] && printf '%s' "$PREFIX" | grep -q 'com.termux'; then
  BIN_DIR="$PREFIX/bin"
else
  BIN_DIR="${HOME:?HOME is not set}/.local/bin"
fi
mkdir -p "$BIN_DIR"
cp "$SOURCE" "$BIN_DIR/agentkit-toolplan"
chmod 755 "$BIN_DIR/agentkit-toolplan"
echo "Installed: $BIN_DIR/agentkit-toolplan"
case ":$PATH:" in *":$BIN_DIR:"*) ;; *) echo "NOTE: add $BIN_DIR to PATH to call it by name." ;; esac
echo "Run: agentkit-toolplan --help"
