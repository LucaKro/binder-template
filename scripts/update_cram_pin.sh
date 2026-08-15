#!/bin/bash
# Pin binder/Dockerfile to the current tip of the CRAM tutorial branch.
#
# BinderHub keys its image cache on this repository's commits, so a push to CRAM alone
# never rebuilds the lab. Run this, then commit and push -- that push is the rebuild.
#
#   scripts/update_cram_pin.sh           bump ARG CRAM_COMMIT to the branch tip
#   scripts/update_cram_pin.sh --check   report what would change, touch nothing
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCKERFILE="${REPO_ROOT}/binder/Dockerfile"

check_only=false
case "${1:-}" in
  --check) check_only=true ;;
  "") ;;
  *) echo "usage: $(basename "$0") [--check]" >&2; exit 2 ;;
esac

die() { echo "error: $*" >&2; exit 1; }

# Read an ARG's default value out of the Dockerfile, so the repository and branch are
# never restated here and cannot drift from what actually gets built.
arg_value() { sed -n "s/^ARG $1=\(.*\)$/\1/p" "$DOCKERFILE" | head -1; }

[ -f "$DOCKERFILE" ] || die "no Dockerfile at $DOCKERFILE"

cram_repo="$(arg_value CRAM_REPO)"
cram_branch="$(arg_value CRAM_BRANCH)"
current="$(arg_value CRAM_COMMIT)"

[ -n "$cram_repo" ]   || die "no 'ARG CRAM_REPO=' in $DOCKERFILE"
[ -n "$cram_branch" ] || die "no 'ARG CRAM_BRANCH=' in $DOCKERFILE"
[ -n "$current" ]     || die "no 'ARG CRAM_COMMIT=' in $DOCKERFILE"

echo "branch:  ${cram_branch}"
echo "repo:    ${cram_repo}"

latest="$(git ls-remote --exit-code "$cram_repo" "refs/heads/${cram_branch}" | cut -f1)" \
  || die "branch '${cram_branch}' not found in ${cram_repo} (is it pushed, and the repo public?)"

echo "pinned:  ${current}"
echo "tip:     ${latest}"

if [ "$latest" = "$current" ]; then
  echo
  echo "Already at the branch tip -- nothing to do."
  exit 0
fi

echo
echo "changes: ${cram_repo%.git}/compare/${current}...${latest}"

if $check_only; then
  echo
  echo "--check given, Dockerfile left alone."
  exit 0
fi

sed -i "s/^ARG CRAM_COMMIT=.*/ARG CRAM_COMMIT=${latest}/" "$DOCKERFILE"

# Trust nothing: confirm the file now says what it should.
[ "$(arg_value CRAM_COMMIT)" = "$latest" ] || die "failed to rewrite CRAM_COMMIT in $DOCKERFILE"

echo
echo "Updated binder/Dockerfile. Next:"
echo "  git commit -am 'Bump CRAM pin to ${latest:0:9}' && git push"
echo "BinderHub rebuilds the lab on that push."
