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

REPO_DIR=""
RUN_FROM_STDIN="0"
if [[ -n "${BASH_SOURCE[0]:-}" ]] && [[ -f "${BASH_SOURCE[0]}" ]]; then
  if [[ "${BASH_SOURCE[0]}" == "/dev/fd/"* ]] || [[ "${BASH_SOURCE[0]}" == "/proc/self/fd/"* ]]; then
    RUN_FROM_STDIN="1"
  fi
  REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi
LOCAL_GAME="${REPO_DIR}/game.py"
LOCAL_README="${REPO_DIR}/README.md"

REPO_URL="${VIBE_GAME_REPO_URL:-https://github.com/dulsara-pieris/VIBE-terminal_game.git}"

if [[ -f "${LOCAL_GAME}" && -f "${LOCAL_README}" ]]; then
  install -m 755 "${LOCAL_GAME}" "${TARGET_DIR}/game.py"
  install -m 644 "${LOCAL_README}" "${TARGET_DIR}/README.md"
else
  if [[ "${RUN_FROM_STDIN}" == "1" ]]; then
    echo "Installer is running from a curl pipe; cloning from ${REPO_URL}"
  else
    echo "Local repo files not found; cloning from ${REPO_URL}"
  fi

  TMP_DIR="$(mktemp -d)"
  cleanup_tmp() {
    rm -rf "${TMP_DIR}"
  }
  trap cleanup_tmp EXIT

  git clone --depth 1 "${REPO_URL}" "${TMP_DIR}/repo"
  install -m 755 "${TMP_DIR}/repo/game.py" "${TARGET_DIR}/game.py"
  install -m 644 "${TMP_DIR}/repo/README.md" "${TARGET_DIR}/README.md"
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
