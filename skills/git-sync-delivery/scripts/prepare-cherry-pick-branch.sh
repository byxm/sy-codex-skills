#!/usr/bin/env bash

set -euo pipefail

if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo "Usage: $0 <target-branch> <temp-branch> [remote]" >&2
  exit 1
fi

target_branch="$1"
temp_branch="$2"
remote="${3:-origin}"
script_dir="$(cd "$(dirname "$0")" && pwd)"

"$script_dir/sync-target-branch.sh" "$target_branch" "$remote"

if git show-ref --verify --quiet "refs/heads/$temp_branch"; then
  echo "TEMP_BRANCH_ALREADY_EXISTS=$temp_branch" >&2
  exit 1
fi

git checkout -b "$temp_branch" "$target_branch"

echo "PREPARED_CHERRY_PICK_BRANCH=$temp_branch"
