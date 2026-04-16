#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="${HOME}/.local/share/vibe-terminal-game"
BIN_LINK="${HOME}/.local/bin/vibe-game"
DESKTOP_FILE="${HOME}/.local/share/applications/vibe-game.desktop"
MAN_FILE="${HOME}/.local/share/man/man6/vibe-game.6.gz"

action_rm() {
  local p="$1"
  if [[ -e "$p" || -L "$p" ]]; then
    rm -rf "$p"
    echo "Removed: $p"
  fi
}

action_rm "${BIN_LINK}"
action_rm "${DESKTOP_FILE}"
action_rm "${MAN_FILE}"
action_rm "${TARGET_DIR}"

echo "Uninstalled VIBE Terminal Game."
