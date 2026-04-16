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
ALT_REMOTE_BASE="${VIBE_GAME_ALT_REMOTE_BASE:-https://github.com/dulsara-pieris/VIBE-terminal_game/raw/main}"

download_file() {
  local rel_path="$1"
  local out_path="$2"

  local candidates=(
    "${REMOTE_BASE}/${rel_path}"
    "${ALT_REMOTE_BASE}/${rel_path}"
  )

  local url
  for url in "${candidates[@]}"; do
    if curl -fL --retry 2 --connect-timeout 10 -A "vibe-terminal-game-installer" "${url}" -o "${out_path}"; then
      return 0
    fi
  done

  echo "Failed to download ${rel_path}. Tried:" >&2
  printf "  - %s\n" "${candidates[@]}" >&2
  return 1
}

if [[ -f "${LOCAL_GAME}" && -f "${LOCAL_README}" ]]; then
  install -m 755 "${LOCAL_GAME}" "${TARGET_DIR}/game.py"
  install -m 644 "${LOCAL_README}" "${TARGET_DIR}/README.md"
else
  echo "Local repo files not found; downloading release files"
  download_file "game.py" "${TARGET_DIR}/game.py"
  chmod 755 "${TARGET_DIR}/game.py"
  download_file "README.md" "${TARGET_DIR}/README.md"
fi

mkdir -p "${HOME}/.config/vibe-terminal-game"

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
