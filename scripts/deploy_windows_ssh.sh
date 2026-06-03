#!/usr/bin/env bash
# Sync this project to a Windows host reachable by SSH and install it there.
set -euo pipefail

if [[ -z "${REMOTE:-}" ]]; then
  cat >&2 <<'EOF'
Usage:
  REMOTE=user@windows-host scripts/deploy_windows_ssh.sh

Optional:
  DEST=C:/windows-gui-mcp

The target Windows host must have Python 3.12 available as `py -3.12`.
EOF
  exit 2
fi

DEST="${DEST:-C:/windows-gui-mcp}"

here="$(cd "$(dirname "$0")/.." && pwd)"
echo ">>> rsync $here -> $REMOTE:$DEST"

rsync -avz --delete \
  --exclude '.venv' \
  --exclude '__pycache__' \
  --exclude '.pytest_cache' \
  --exclude '.git' \
  --exclude 'dist' \
  --exclude '*.egg-info' \
  "$here/" "$REMOTE:$DEST/"

echo ">>> remote install"
ssh "$REMOTE" "cd '$DEST' && py -3.12 -m venv .venv && .venv/Scripts/pip install --upgrade pip && .venv/Scripts/pip install -e '.[windows,ocr]' && .venv/Scripts/windows-gui-mcp --help"

echo ">>> done"
cat <<EOF
Example MCP client config:
{
  "mcpServers": {
    "windows-gui": {
      "command": "ssh",
      "args": ["$REMOTE", "$DEST/.venv/Scripts/windows-gui-mcp.exe"]
    }
  }
}
EOF
