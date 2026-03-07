#!/usr/bin/env bash
set -euo pipefail

PART="${1:-patch}"
MSG="${2:-}"
MANIFEST="custom_components/everlights/manifest.json"

if [[ ! -f "$MANIFEST" ]]; then
  echo "Missing $MANIFEST"
  exit 1
fi

if [[ "$PART" != "major" && "$PART" != "minor" && "$PART" != "patch" ]]; then
  echo "Version part must be one of: major, minor, patch"
  exit 1
fi

git rev-parse --is-inside-work-tree >/dev/null

if ! git diff --quiet -- "$MANIFEST"; then
  echo "$MANIFEST already has local changes. Commit/stash/revert first."
  exit 1
fi

VER="$(jq -r '.version' "$MANIFEST")"
IFS='.' read -r MAJOR MINOR PATCH <<< "$VER"

case "$PART" in
  major)
    ((MAJOR+=1))
    MINOR=0
    PATCH=0
    ;;
  minor)
    ((MINOR+=1))
    PATCH=0
    ;;
  patch)
    ((PATCH+=1))
    ;;
esac

NEW_VER="${MAJOR}.${MINOR}.${PATCH}"
MSG="${MSG:-Release ${NEW_VER}}"

if git rev-parse --verify --quiet "refs/tags/$NEW_VER" >/dev/null; then
  echo "Tag $NEW_VER already exists locally."
  exit 1
fi

TMP="$(mktemp)"
jq --arg v "$NEW_VER" '.version = $v' "$MANIFEST" > "$TMP"
mv "$TMP" "$MANIFEST"

git add "$MANIFEST"
git commit -m "$MSG"
git tag -a "$NEW_VER" -m "$NEW_VER"
git push origin main
git push origin "$NEW_VER"

echo "Released $NEW_VER"
