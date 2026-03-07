#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 \"commit message\" [major|minor|patch]"
  exit 1
fi

MSG="$1"
PART="${2:-patch}"
MANIFEST="custom_components/everlights/manifest.json"

if [[ ! -f "$MANIFEST" ]]; then
  echo "Missing $MANIFEST"
  exit 1
fi

if [[ "$PART" != "major" && "$PART" != "minor" && "$PART" != "patch" ]]; then
  echo "Version part must be one of: major, minor, patch"
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

TMP="$(mktemp)"
jq --arg v "$NEW_VER" '.version = $v' "$MANIFEST" > "$TMP"
mv "$TMP" "$MANIFEST"

git add "$MANIFEST"
git commit -m "$MSG"
git tag -a "$NEW_VER" -m "$NEW_VER"
git push origin main
git push origin "$NEW_VER"

echo "Released $NEW_VER"
