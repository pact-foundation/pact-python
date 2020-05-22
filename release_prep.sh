#!/bin/bash

VERSION=$1

if [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]*$ ]]; then
  echo "Updating version $VERSION."
else
  echo "Invalid version number $VERSION"
  exit 1;
fi

TAG_NAME="v$VERSION"

echo "Releasing $TAG_NAME"

echo -e "`git log --pretty=format:'  * %h - %s (%an, %ad)' $TAG_NAME..HEAD`\n$(cat CHANGELOG.md)" > CHANGELOG.md

echo "Appended Changelog to $VERSION"

git add CHANGELOG.md pact/__version__.py
git commit -m "Releasing version $VERSION"

git tag -a "$TAG_NAME" -m "Releasing version $VERSION"

# && git push origin master --tags`


