#!/usr/bin/env bash

set -euo pipefail

remote="origin"
branches=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --remote)
      if [[ $# -lt 2 ]]; then
        echo "Missing value for --remote" >&2
        exit 1
      fi
      remote="$2"
      shift 2
      ;;
    --)
      shift
      while [[ $# -gt 0 ]]; do
        branches+=("$1")
        shift
      done
      ;;
    *)
      branches+=("$1")
      shift
      ;;
  esac
done

if [[ ${#branches[@]} -eq 0 ]]; then
  echo "Usage: $0 <branch>... [--remote <remote>]" >&2
  exit 1
fi

git fetch "$remote" --prune

existing_branches=()
missing_branches=()
for branch in "${branches[@]}"; do
  if git show-ref --verify --quiet "refs/remotes/$remote/$branch"; then
    existing_branches+=("$branch")
  else
    missing_branches+=("$branch")
  fi
done

if [[ ${#existing_branches[@]} -gt 0 ]]; then
  git push "$remote" --delete "${existing_branches[@]}"
fi

for branch in "${missing_branches[@]}"; do
  echo "REMOTE_BRANCH_MISSING=$remote/$branch"
done

for branch in "${existing_branches[@]}"; do
  echo "REMOTE_BRANCH_DELETED=$remote/$branch"
done
