# Releasing

## Preparing the release

The easiest way is to just run the following command from the root folder with
the HEAD commit on trunk and the appropriate version. We follow
`<MAJOR>.<MINOR>.<PATCH>` versioning.

   ```shell
   $ script/release_prep.sh X.Y.Z
   ```

This script effectively runs the following:

1. Increment the version according to semantic versioning rules in `pact/__version__.py`

2. Update the `CHANGELOG.md` using:
   ```shell
   $ git log --pretty=format:'  * %h - %s (%an, %ad)' vX.Y.Z..HEAD
   ```

3. Add files to git
   ```shell
   $ git add CHANGELOG.md pact/__version__.py
   ```

4. Commit
   ```shell
   $ git commit -m "Releasing version X.Y.Z"
   ```

5. Tag
   ```shell
   $ git tag -a vX.Y.Z -m "Releasing version X.Y.Z"
   $ git push origin master --tags
   ```

## Updating Pact Ruby

To upgrade the versions of `pact-mock_service` and `pact-provider-verifier`, change the
`PACT_STANDALONE_VERSION` in `setup.py` to match the latest version available from the
[pact-ruby-standalone](https://github.com/pact-foundation/pact-ruby-standalone/releases)
repository. Do this before preparing the release.

## Publishing to pypi

1. Wait until GitHub Actions have run and the new tag is available at
   https://github.com/pact-foundation/pact-python/releases/tag/vX.Y.Z

2. Set the title to `pact-python-X.Y.Z`

3. Save

4. Go to GitHub Actions for Pact Python and you should see an 'Upload Python 
   Package' action blocked for your version.

5. Click this and then 'Review deployments'. Select 'Upload Python Package'
  and Approve deploy. If you can't do this you may need an administrator to
  give you permissions or do it for you. You should see in Slack #pact-python
  that the release has happened. Verify in [pypi](https://pypi.org/project/pact-python/)
