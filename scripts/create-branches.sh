#!/usr/bin/env bash
# ============================================================
# Fincepto — Create all feature branches from current HEAD
# ============================================================
# Usage:
#   chmod +x scripts/create-branches.sh
#   ./scripts/create-branches.sh
#
# Run this script once after cloning / on the maintainer's machine
# to seed all feature branches in the remote repository.
# ============================================================
set -euo pipefail

REMOTE="${1:-origin}"
SHA=$(git rev-parse HEAD)

echo "Creating Fincepto feature branches from $SHA …"
echo ""

branches=(
  "develop"
  "feature/backend-core"
  "feature/accounting"
  "feature/inventory"
  "feature/hrm"
  "feature/crm"
  "feature/projects"
  "feature/farm-livestock"
  "feature/manufacturing"
  "feature/hospitality"
  "feature/travel-tour"
  "feature/trading-retail"
  "feature/reports-forecasting"
  "feature/frontend"
  "feature/devops"
)

for branch in "${branches[@]}"; do
  if git show-ref --verify --quiet "refs/remotes/$REMOTE/$branch"; then
    echo "  [SKIP] $branch already exists on $REMOTE"
  else
    git branch --force "$branch" "$SHA"
    git push "$REMOTE" "$branch"
    echo "  [OK]   $branch created"
  fi
done

echo ""
echo "Done! All branches have been pushed to $REMOTE."
