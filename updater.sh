#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

if ! command -v git >/dev/null 2>&1; then
  echo "git is required for update."
  exit 1
fi

cd "${REPO_DIR}"

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [[ "${CURRENT_BRANCH}" == "HEAD" ]]; then
  echo "Detached HEAD detected. Please checkout a branch first."
  exit 1
fi

echo "Updating ${CURRENT_BRANCH} from origin..."
git fetch --all --prune
git pull --ff-only origin "${CURRENT_BRANCH}"

echo "Reinstalling updated Linux files..."
"${REPO_DIR}/installer.sh"

echo "Update complete."
