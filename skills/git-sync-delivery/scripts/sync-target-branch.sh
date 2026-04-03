#!/usr/bin/env bash

set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 <branch> [remote]" >&2
  exit 1
fi

branch="$1"
remote="${2:-origin}"

git fetch "$remote" "$branch"

if git show-ref --verify --quiet "refs/heads/$branch"; then
  git checkout "$branch"
  git pull --ff-only "$remote" "$branch"
else
  git checkout -b "$branch" "$remote/$branch"
fi

echo "SYNCED_TARGET_BRANCH=$branch"
