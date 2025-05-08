#!/bin/sh
TAG="$1"
REPO="yourusername/donate-when-idle"
if [ -z "$TAG" ]; then
  echo "Usage: $0 <tag>"
  exit 1
fi
echo "Downloading artifacts for release $TAG..."
gh release download "$TAG" -R "$REPO" -p "*.{exe,msi,dmg,AppImage}" -D "release-$TAG"
cd "release-$TAG" || exit 1
zip -9 -r "starter-kit-v$TAG.zip" .
echo "Packaged starter-kit-v$TAG.zip with release artifacts."
