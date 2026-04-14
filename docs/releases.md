# Releases

Pact Python is made available through both GitHub releases and PyPI. The GitHub releases also come with a summary of changes and contributions since the last release.

The entire process is automated through three GitHub Actions workflows (one per package), each running a three-stage pipeline. A description of the process is provided [below](#release-pipeline).

## Packages

Pact Python is split into three independently versioned packages:

-   **[`pact-python`](https://pypi.org/p/pact-python)**: the core library. Versioned with [semantic versioning](https://semver.org/), derived from conventional commits via [git-cliff](https://git-cliff.org/).
-   **[`pact-python-ffi`](https://pypi.org/p/pact-python-ffi)**: Python bindings for the [pact-reference](https://github.com/pact-foundation/pact-reference) Rust library. Versioned as `{upstream}.{N}` (e.g. `0.4.28.0`), tracking upstream `libpact_ffi` releases.
-   **[`pact-python-cli`](https://pypi.org/p/pact-python-cli)**: Python wrapper for the [pact-standalone](https://github.com/pact-foundation/pact-standalone) CLI tools. Versioned as `{upstream}.{N}` (e.g. `2.4.0.0`), tracking upstream releases.

## Versioning

### pact-python (core)

The core package follows [semantic versioning](https://semver.org/). Breaking changes are indicated by a major version bump, new features by a minor version bump, and bug fixes by a patch version bump.

There are a couple of exceptions to the [semantic versioning](https://semver.org/) rules:

-   Dropping support for a Python version is not considered a breaking change and is not necessarily accompanied by a major version bump.
-   Private APIs are not considered part of the public API and are not subject to the same rules as the public API. They can be changed at any time without a major version bump. Private APIs are denoted by a leading underscore in the name.
-   Deprecations are not considered breaking changes and are not necessarily accompanied by a major version bump. Their removal is considered a breaking change and is accompanied by a major version bump.
-   Changes to the type annotations will not be considered breaking changes, unless they are accompanied by a change to the runtime behaviour.

Any deviation from the standard semantic versioning rules will be clearly documented in the release notes.

The next version is computed automatically by [git-cliff](https://git-cliff.org/) from the [conventional commit](https://www.conventionalcommits.org/) history since the last release tag.

### pact-python-ffi and pact-python-cli

These packages follow their upstream projects' versioning, extended with a fourth component `N` that starts at `0` for each new upstream version and increments with each packaging-only release. When a new upstream version is released, `N` resets to `0`.

### Version storage

Each package stores its version as a static string in its `pyproject.toml`. The version is updated automatically by the release pipeline during the prepare stage and committed to the release branch.

## Release Pipeline

Each package has its own release workflow (`.github/workflows/release-{core,ffi,cli}.yml`). All three follow the same three-stage process:

### Stage 1: Prepare

Triggered by every push to `main`.

The `prepare` job runs `scripts/release.py prepare <package>`, which:

1.  Computes the next version (via git-cliff for core; by fetching the latest upstream release for ffi/cli).
2.  Updates `pyproject.toml` with the new version.
3.  Prepends the new release entry to `CHANGELOG.md` using git-cliff, preserving all previous entries (including any manual edits).
4.  Force-pushes those changes to a fixed release branch (e.g. `release/pact-python`).
5.  Creates the release PR if it does not exist, or updates its title and body if it does.

The release PR gives maintainers an opportunity to review and manually adjust the changelog before it is published.

A PAT (`GH_TOKEN`) is used to create/update the release PR so that the PR triggers the expected downstream workflow runs (GitHub's loop-prevention rules block `GITHUB_TOKEN`-triggered events from starting new workflow runs).

### Stage 2: Tag

Triggered when the release PR is merged (GitHub fires a `pull_request` event with `action: closed` and `merged: true`).

The `tag` job runs `scripts/release.py tag <package>`, which reads the version from `pyproject.toml` on `main` and pushes a git tag of the form `<package>/<version>` (e.g. `pact-python/3.2.2`).

A PAT (`GH_TOKEN`) is used instead of the default `GITHUB_TOKEN` so that the tag push is able to trigger the downstream Stage 3 workflow run (GitHub's loop-prevention rules block `GITHUB_TOKEN`-triggered events from starting new workflow runs).

### Stage 3: Publish

Triggered by a tag push matching the package's tag prefix.

The `publish` job:

1.  Extracts the changelog entry for the tagged version directly from the committed `CHANGELOG.md` (preserving any manual edits made to the release PR).
2.  Builds the source distribution and wheels across all supported platforms and architectures.
3.  Creates a GitHub release with the extracted changelog.
4.  Publishes all artifacts to PyPI.

The `publish` job uses the `pypi` GitHub environment, which can be configured to require manual approval before publishing.
