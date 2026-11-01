#!/bin/sh
set -eu

SOURCE_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
CODEX_ROOT=${CODEX_HOME:-"$HOME/.codex"}
DEST="$CODEX_ROOT/skills/agentkit"

mkdir -p "$DEST/scripts" "$DEST/references"
cp "$SOURCE_DIR/SKILL.md" "$DEST/SKILL.md"
cp "$SOURCE_DIR/VERSION.json" "$DEST/VERSION.json"
cp "$SOURCE_DIR"/agentkit*.py "$DEST/scripts/"
cp "$SOURCE_DIR/mobile_test.py" "$DEST/scripts/mobile_test.py"
cp "$SOURCE_DIR/agentkit" "$DEST/scripts/agentkit"
cp "$SOURCE_DIR/agentkit.sh" "$DEST/scripts/agentkit.sh"
mkdir -p "$DEST/scripts/tests"
cp -R "$SOURCE_DIR/tests/." "$DEST/scripts/tests/"
cp "$SOURCE_DIR/AI_USAGE.md" "$DEST/references/AI_USAGE.md"
cp "$SOURCE_DIR/MOBILE_TESTING.md" "$DEST/references/mobile-testing.md"
cp "$SOURCE_DIR/TERMUX_TOOL_CANDIDATES.md" "$DEST/references/termux-tool-candidates.md"
cp "$SOURCE_DIR/MCP_CONNECTOR.md" "$DEST/CONNECTOR.md"
cp "$SOURCE_DIR/HYAI_INTEGRATION.md" "$DEST/HYAI_INTEGRATION.md"

printf 'Installed AgentKit skill to %s\n' "$DEST"
