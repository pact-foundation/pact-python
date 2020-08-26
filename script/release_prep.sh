#!/bin/bash

VERSION=$1

if [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]*$ ]]; then
  echo "Updating version $VERSION."
else
  echo "Invalid version number $VERSION"
  exit 1;
fi

TAG_NAME="v$VERSION"
LAST_TAG=`git describe --abbrev=0`


cat pact/__version__.py | sed "s/__version__ = .*/__version__ = '${VERSION}'/" > tmp-version
mv tmp-version pact/__version__.py

echo "Releasing $TAG_NAME"

echo -e "`git log --pretty=format:'  * %h - %s (%an, %ad)' $LAST_TAG..HEAD`\n$(cat CHANGELOG.md)" > CHANGELOG.md
echo -e "### $VERSION\n$(cat CHANGELOG.md)" > CHANGELOG.md

echo "Appended Changelog to $VERSION"

git add CHANGELOG.md pact/__version__.py
git commit -m "chore: Releasing version $VERSION"

git tag -a "$TAG_NAME" -m "Releasing version $VERSION" && git push origin master --tags


