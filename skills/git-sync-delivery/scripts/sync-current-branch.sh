#!/usr/bin/env bash

set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 <branch> [remote]" >&2
  exit 1
fi

branch="$1"
remote="${2:-origin}"

git fetch "$remote" "$branch"

if ! git show-ref --verify --quiet "refs/remotes/$remote/$branch"; then
  echo "REMOTE_BRANCH_MISSING=$remote/$branch"
  exit 0
fi

current_branch="$(git branch --show-current)"
if [[ "$current_branch" != "$branch" ]]; then
  git checkout "$branch"
fi

counts="$(git rev-list --left-right --count "$branch...$remote/$branch")"
ahead="${counts%%$'\t'*}"
behind="${counts##*$'\t'}"

if [[ "$ahead" == "0" && "$behind" == "0" ]]; then
  echo "CURRENT_BRANCH_IN_SYNC=$branch"
  exit 0
fi

if [[ "$ahead" != "0" && "$behind" == "0" ]]; then
  echo "CURRENT_BRANCH_LOCAL_AHEAD=$branch"
  exit 0
fi

git merge --no-edit "$remote/$branch"

echo "CURRENT_BRANCH_MERGED_REMOTE=$branch"
