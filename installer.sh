#!/usr/bin/env bash
set -euo pipefail

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "This installer is Linux-first and currently supports Linux only."
  exit 1
fi

TARGET_DIR="${HOME}/.local/share/vibe-terminal-game"
BIN_DIR="${HOME}/.local/bin"
APP_DIR="${HOME}/.local/share/applications"
MAN_DIR="${HOME}/.local/share/man/man6"
SCRIPT_NAME="vibe-game"

mkdir -p "${TARGET_DIR}" "${BIN_DIR}" "${APP_DIR}" "${MAN_DIR}"

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_GAME="${REPO_DIR}/game.py"
LOCAL_README="${REPO_DIR}/README.md"

REMOTE_BASE="${VIBE_GAME_REMOTE_BASE:-https://raw.githubusercontent.com/dulsara-pieris/VIBE-terminal_game/main}"

if [[ -f "${LOCAL_GAME}" && -f "${LOCAL_README}" ]]; then
  install -m 755 "${LOCAL_GAME}" "${TARGET_DIR}/game.py"
  install -m 644 "${LOCAL_README}" "${TARGET_DIR}/README.md"
else
  echo "Local repo files not found; downloading from ${REMOTE_BASE}"
  curl -fsSL "${REMOTE_BASE}/game.py" -o "${TARGET_DIR}/game.py"
  chmod 755 "${TARGET_DIR}/game.py"
  curl -fsSL "${REMOTE_BASE}/README.md" -o "${TARGET_DIR}/README.md"
fi

ln -sf "${TARGET_DIR}/game.py" "${BIN_DIR}/${SCRIPT_NAME}"

cat > "${APP_DIR}/vibe-game.desktop" <<EOF2
[Desktop Entry]
Type=Application
Name=VIBE Terminal Game
Comment=Terminal RPG adventure
Exec=${BIN_DIR}/${SCRIPT_NAME}
Terminal=true
Categories=Game;RolePlaying;
EOF2

cat > "${MAN_DIR}/vibe-game.6" <<'EOF2'
.TH VIBE-GAME 6
.SH NAME
vibe-game \- terminal RPG game
.SH SYNOPSIS
.B vibe-game
.RI [ --smoke-test ]
.SH DESCRIPTION
VIBE Terminal Game is a Linux-first movement sandbox RPG
with save/load, crafting, combat, and git-based updates.
EOF2

gzip -f "${MAN_DIR}/vibe-game.6"

echo "Installed VIBE Terminal Game on Linux."
echo "Run: ${BIN_DIR}/${SCRIPT_NAME}"
echo "Desktop entry: ${APP_DIR}/vibe-game.desktop"
if [[ ":${PATH}:" != *":${BIN_DIR}:"* ]]; then
  echo "Tip: add ${BIN_DIR} to PATH."
fi
