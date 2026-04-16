#!/usr/bin/env bash
set -euo pipefail

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "This installer is Linux-first and currently supports Linux only."
  exit 1
fi

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="${HOME}/.local/share/vibe-terminal-game"
BIN_DIR="${HOME}/.local/bin"
APP_DIR="${HOME}/.local/share/applications"
MAN_DIR="${HOME}/.local/share/man/man6"
SCRIPT_NAME="vibe-game"

mkdir -p "${TARGET_DIR}" "${BIN_DIR}" "${APP_DIR}" "${MAN_DIR}"

install -m 755 "${REPO_DIR}/game.py" "${TARGET_DIR}/game.py"
install -m 644 "${REPO_DIR}/README.md" "${TARGET_DIR}/README.md"
ln -sf "${TARGET_DIR}/game.py" "${BIN_DIR}/${SCRIPT_NAME}"

cat > "${APP_DIR}/vibe-game.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=VIBE Terminal Game
Comment=Terminal RPG adventure
Exec=${BIN_DIR}/${SCRIPT_NAME}
Terminal=true
Categories=Game;RolePlaying;
EOF

cat > "${MAN_DIR}/vibe-game.6" <<'EOF'
.TH VIBE-GAME 6
.SH NAME
vibe-game \- terminal RPG game
.SH SYNOPSIS
.B vibe-game
.RI [ --smoke-test ]
.SH DESCRIPTION
VIBE Terminal Game is a Linux-first movement sandbox RPG
with save/load, crafting, combat, and git-based updates.
EOF

gzip -f "${MAN_DIR}/vibe-game.6"

echo "Installed VIBE Terminal Game on Linux."
echo "Run: ${BIN_DIR}/${SCRIPT_NAME}"
echo "Desktop entry: ${APP_DIR}/vibe-game.desktop"
if [[ ":${PATH}:" != *":${BIN_DIR}:"* ]]; then
  echo "Tip: add ${BIN_DIR} to PATH."
fi
