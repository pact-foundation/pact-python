#!/usr/bin/env bash -e

: "${1?Please supply the pact-ruby-standalone version to upgrade to}"

STANDALONE_VERSION=$1
TYPE=${2:-feat}
DASHERISED_VERSION=$(echo "${STANDALONE_VERSION}" | sed 's/\./\-/g')
BRANCH_NAME="chore/upgrade-to-pact-ruby-standalone-${DASHERISED_VERSION}"

git checkout master
git checkout setup.py
git pull origin master

git checkout -b ${BRANCH_NAME}

cat setup.py | sed "s/PACT_STANDALONE_VERSION =.*/PACT_STANDALONE_VERSION = '${STANDALONE_VERSION}'/" > tmp-setup
mv tmp-setup setup.py

git add setup.py
git commit -m "${TYPE}: update standalone to ${STANDALONE_VERSION}"
git push --set-upstream origin ${BRANCH_NAME}

# hub pull-request --browse --message "${TYPE}: update standalone to ${STANDALONE_VERSION}"
gh pr create -w --title "${TYPE}: update standalone to ${STANDALONE_VERSION}"
git checkout master
