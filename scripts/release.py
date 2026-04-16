#!/usr/bin/env python3
# ruff: noqa: S603, S607
"""Release management script for pact-python packages.

Usage:
    python scripts/release.py prepare core [--dry-run]
    python scripts/release.py prepare ffi  [--dry-run]
    python scripts/release.py prepare cli  [--dry-run]

    python scripts/release.py tag core
    python scripts/release.py tag ffi
    python scripts/release.py tag cli
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import tomllib

ROOT = Path(__file__).parent.parent
logger = logging.getLogger(__name__)


@dataclass
class PullRequest:
    """A GitHub pull request as returned by `gh pr list`."""

    number: int
    """GitHub PR number."""

    head_ref_name: str
    """The head branch name (JSON field `headRefName`)."""


@dataclass
class Package:
    """Configuration for a releasable package in the monorepo."""

    name: str
    """PyPI package name, e.g. `"pact-python"`."""

    key: str
    """Short identifier used as the CLI argument and as the `PACKAGES` lookup key."""

    directory: Path
    """Absolute path to the package root (where `pyproject.toml` lives)."""

    tag_prefix: str
    """Git tag prefix, e.g. `"pact-python/"` → tag `"pact-python/3.2.2"`."""

    upstream_repo: str | None
    """GitHub repo to track for the upstream version (`owner/repo`).
    `None` for the core package, which derives its version from git history
    via git cliff instead of following an external release."""

    upstream_tag_prefix: str | None
    """Prefix used to identify and strip upstream release tags.

    Releases whose `tagName` does not start with this prefix are ignored, and
    the prefix is stripped to produce the bare version string.  Examples:

    - `"libpact_ffi-v"` for `pact-foundation/pact-reference` (only libpact_ffi
      releases, not mock_server / verifier / etc.)
    - `"v"` for `pact-foundation/pact-standalone`

    `None` when `upstream_repo` is `None` (i.e., the core package).
    """

    release_branch: str
    """Fixed branch name for release PRs, e.g. `"release/pact-python"`."""

    def read_version(self) -> str:
        """Read the static version from the package's pyproject.toml."""
        with (self.directory / "pyproject.toml").open("rb") as f:
            data = tomllib.load(f)
        return data["project"]["version"]

    def write_version(self, version: str) -> None:
        """Update the version field in the package's pyproject.toml.

        Uses a regex substitution rather than TOML round-tripping so that
        comments, formatting, and key ordering in pyproject.toml are preserved.
        """
        toml_path = self.directory / "pyproject.toml"
        content = toml_path.read_text()
        new_content = re.sub(
            r'^(version\s*=\s*")[^"]*(")',
            rf"\g<1>{version}\g<2>",
            content,
            count=1,
            flags=re.MULTILINE,
        )
        if new_content == content:
            msg = f"Could not find version field to update in {toml_path}"
            raise ValueError(msg)
        logger.debug("Writing version %s to %s", version, toml_path)
        toml_path.write_text(new_content)

    def compute_tag_name(self, version: str) -> str:
        """Return the full git tag name for a package version."""
        return f"{self.tag_prefix}{version}"

    def fetch_upstream_version(self) -> str:
        """Fetch the latest upstream release version (without prefix) via gh CLI.

        Uses `gh release list` filtered by
        [`upstream_tag_prefix`][scripts.release.Package.upstream_tag_prefix]
        to find the most recent matching release, then strips the prefix to
        return the bare version string.

        Returns:
            The upstream version string without any prefix, e.g. `"0.4.28"`.

        Raises:
            ValueError: If this package has no upstream repo or tag prefix configured.
        """
        if self.upstream_repo is None or self.upstream_tag_prefix is None:
            msg = f"Package {self.name!r} has no upstream repo configured"
            raise ValueError(msg)

        prefix = self.upstream_tag_prefix
        logger.debug(
            "Fetching upstream version from %s (tag prefix: %r)",
            self.upstream_repo,
            prefix,
        )
        jq_filter = (
            f'[.[] | select(.tagName | startswith("{prefix}"))] | first | .tagName'
        )
        result = subprocess.check_output(
            [
                "gh",
                "release",
                "list",
                "--repo",
                self.upstream_repo,
                "--json",
                "tagName",
                "--jq",
                jq_filter,
            ],
            text=True,
        )
        tag = result.strip()
        if not tag or tag == "null":
            msg = f"No release with prefix {prefix!r} found in {self.upstream_repo!r}"
            raise ValueError(msg)
        version = tag.removeprefix(prefix)
        logger.debug("Upstream tag: %s → version: %s", tag, version)
        return version

    def compute_semver_version(self) -> str | None:
        """Return the next semver via git cliff, or None.

        Returns `None` when there are no unreleased commits that would produce a
        version bump (git cliff exits non-zero or returns empty output).

        Returns:
            The next version string (e.g. `"3.2.2"`), or `None` if no bump is
            needed.
        """
        logger.debug("Running git cliff --bumped-version in %s", self.directory)
        result = subprocess.run(
            ["git", "cliff", "--bumped-version"],
            capture_output=True,
            text=True,
            check=False,
            cwd=self.directory,
        )
        if result.returncode != 0 or not result.stdout.strip():
            logger.debug("git cliff: no version bump needed")
            return None
        raw = result.stdout.strip()
        # git cliff outputs the full tag name (e.g. "pact-python/3.2.2"); strip prefix
        version = strip_tag_prefix(raw, self.tag_prefix)
        logger.debug("git cliff bumped version: %s", version)
        return version

    def compute_next_version(self) -> str | None:
        """Return the proposed next version string, or None if no release is needed.

        Dispatches to one of two strategies based on whether the package tracks
        an upstream:

        - **Core** (`upstream_repo` is `None`): asks git cliff for the next
          semver implied by unreleased conventional commits; returns `None` when
          there is nothing to release.
        - **FFI / CLI** (`upstream_repo` set): fetches the latest upstream GitHub
          release and derives the 4-part version via `compute_wrapper_version`.

        Returns:
            The next version string, or `None` if nothing has changed since the
            last release.
        """
        if self.upstream_repo is None:
            logger.debug("Computing next version for %s via git cliff", self.name)
            return self.compute_semver_version()
        logger.debug(
            "Computing next version for %s via upstream %s",
            self.name,
            self.upstream_repo,
        )
        upstream = self.fetch_upstream_version()
        current = self.read_version()
        logger.debug("Current: %s  Upstream: %s", current, upstream)
        return compute_wrapper_version(upstream, current)

    def find_open_release_pr(self) -> PullRequest | None:
        """Return the open release PR for this package, or None."""
        logger.debug(
            "Looking for open release PR on branch %r",
            self.release_branch,
        )
        result = subprocess.check_output(
            [
                "gh",
                "pr",
                "list",
                "--head",
                self.release_branch,
                "--state",
                "open",
                "--json",
                "number,headRefName",
                "--jq",
                "first",
            ],
            text=True,
        )
        pr = parse_existing_pr(result)
        if pr is not None:
            logger.debug(
                "Found existing PR #%d on branch %s", pr.number, pr.head_ref_name
            )
        else:
            logger.debug("No existing release PR found")
        return pr

    def generate_changelog_body(self, version: str) -> str:
        """
        Generate the changelog entry body for a proposed version using git cliff.

        Uses `--tag` to assign the version to unreleased commits and
        `--strip header` to return only the entry body without the changelog
        header.

        Args:
            version:
                The proposed next version string.

        Returns:
            The rendered changelog body as a string.
        """
        tag = self.compute_tag_name(version)
        logger.debug("Generating changelog body for tag %s", tag)
        return subprocess.check_output(
            ["git", "cliff", "--tag", tag, "--unreleased", "--strip", "header"],
            text=True,
            cwd=self.directory,
        )

    def update_changelog_file(self, version: str) -> None:
        """
        Prepend the changelog entry for unreleased commits to CHANGELOG.md.

        Uses `--prepend` rather than `--output` so that only the new entry is
        inserted at the top of the file, leaving all previous entries (including
        any manual edits) untouched.

        Args:
            version:
                The version to assign to the unreleased commits.
        """
        tag = self.compute_tag_name(version)
        logger.debug(
            "Prepending changelog entry to CHANGELOG.md in %s for tag %s",
            self.directory,
            tag,
        )
        subprocess.check_call(
            ["git", "cliff", "--tag", tag, "--unreleased", "--prepend", "CHANGELOG.md"],
            text=True,
            cwd=self.directory,
        )

    def _configure_git_for_ci(self) -> None:
        """Configure git identity and authenticate the remote for CI operations.

        Sets `user.name` and `user.email` only when they are not already
        configured (preserving a developer's local git config when running
        outside CI).  If `GH_TOKEN` is set, embeds the token in the HTTPS
        remote URL so that `git push` and `gh` operations authenticate without
        a separate credential helper.
        """
        logger.debug("Configuring git identity for CI")
        if not subprocess.run(
            ["git", "config", "--get", "user.name"],
            text=True,
            check=False,
            capture_output=True,
            cwd=ROOT,
        ).stdout.strip():
            logger.debug("Setting git user.name to github-actions[bot]")
            subprocess.check_call(
                ["git", "config", "user.name", "github-actions[bot]"],
                text=True,
                cwd=ROOT,
            )
        if not subprocess.run(
            ["git", "config", "--get", "user.email"],
            text=True,
            check=False,
            capture_output=True,
            cwd=ROOT,
        ).stdout.strip():
            logger.debug("Setting git user.email to github-actions[bot]@...")
            subprocess.check_call(
                [
                    "git",
                    "config",
                    "user.email",
                    "github-actions[bot]@users.noreply.github.com",
                ],
                text=True,
                cwd=ROOT,
            )

    def _push_release_branch(
        self,
        pr_title: str,
        changelog: str,
        existing_pr: PullRequest | None,
    ) -> None:
        """Create or update the fixed release branch, then create or update the PR.

        Resets the fixed release branch to the current HEAD (main), commits the
        prepared files, force-pushes, and creates or updates the PR title and body.
        Using a fixed branch name means no old PRs need to be closed when the
        proposed version changes — the existing PR is simply updated in place.

        Args:
            pr_title:
                The PR title, e.g. `"chore(release): pact-python v3.2.2"`.
            changelog:
                The rendered changelog body to set as the PR description.
            existing_pr:
                The open [`PullRequest`][scripts.release.PullRequest] to update,
                or `None` to create a new PR.
        """
        branch = self.release_branch
        pkg_files = [
            str(self.directory / "pyproject.toml"),
            str(self.directory / "CHANGELOG.md"),
        ]
        if existing_pr is not None:
            logger.debug(
                "Updating existing release branch %s (PR #%d)",
                branch,
                existing_pr.number,
            )
        else:
            logger.debug("Creating new release branch %s", branch)
        subprocess.check_call(
            ["git", "checkout", "-B", branch, "origin/main"],
            text=True,
            cwd=ROOT,
        )
        subprocess.check_call(
            ["git", "add", *pkg_files],
            text=True,
            cwd=ROOT,
        )
        subprocess.check_call(
            ["git", "commit", "-m", pr_title],
            text=True,
            cwd=ROOT,
        )
        subprocess.check_call(
            ["git", "push", "--force", "origin", branch],
            text=True,
            cwd=ROOT,
        )
        if existing_pr is not None:
            subprocess.check_call(
                [
                    "gh",
                    "pr",
                    "edit",
                    str(existing_pr.number),
                    "--title",
                    pr_title,
                    "--body",
                    changelog,
                ],
                text=True,
            )
        else:
            subprocess.check_call(
                [
                    "gh",
                    "pr",
                    "create",
                    "--title",
                    pr_title,
                    "--body",
                    changelog,
                    "--base",
                    "main",
                    "--draft",
                ],
                text=True,
            )

    def prepare(self, *, dry_run: bool) -> None:
        """Create or update the release PR for this package.

        Determines the next version, generates a changelog, writes the version
        and changelog to disk, then (unless `dry_run` is set) creates or updates
        the release PR on GitHub.  The release branch is a fixed name
        (`release_branch`) that is force-pushed on every run, so the same PR
        is updated in place even when the proposed version changes.

        File writes (`pyproject.toml`, `CHANGELOG.md`) always happen so the
        output can be inspected locally; they are easily reverted with
        `git checkout`.  Git branch operations (push, PR create/edit) are
        skipped when `dry_run` is `True`.

        Args:
            dry_run:
                When `True`, write files to disk and print a summary of the
                GitHub actions that *would* be taken, but do not push, create,
                or update any branches or pull requests.
        """
        version = self.compute_next_version()
        if version is None:
            logger.info("No version bump needed for %s. Nothing to do.", self.name)
            return

        logger.info("Proposed next version for %s: %s", self.name, version)
        changelog = self.generate_changelog_body(version)
        pr_title = f"chore(release): {self.name} v{version}"
        existing_pr = self.find_open_release_pr()

        # Write version and changelog to disk.  These are always applied so the
        # result can be inspected locally; `git checkout` reverts them cleanly.
        logger.debug("Writing version and changelog to disk")
        self.write_version(version)
        self.update_changelog_file(version)

        if dry_run:
            logger.info(
                "\n--- Changelog for %s v%s ---\n%s",
                self.name,
                version,
                changelog,
            )
            if existing_pr is not None:
                logger.info(
                    "[dry-run] Would update PR #%d title and body on branch %r.",
                    existing_pr.number,
                    self.release_branch,
                )
            else:
                logger.info(
                    "[dry-run] Would create PR %r on branch %r targeting main.",
                    pr_title,
                    self.release_branch,
                )
            logger.info("[dry-run] Files written — use `git checkout` to revert.")
            return

        try:
            self._configure_git_for_ci()
            self._push_release_branch(pr_title, changelog, existing_pr)
        finally:
            # Return to main so the local repo is left in a clean state, even on failure
            logger.debug("Returning to main branch")
            subprocess.check_call(
                ["git", "checkout", "main"],
                text=True,
                cwd=ROOT,
            )

        logger.info("Release PR for %s v%s created/updated.", self.name, version)

    def tag(self, *, dry_run: bool = False) -> None:
        """Create and push the release git tag for this package.

        Reads the version from `pyproject.toml` (the unconditional source of truth)
        and pushes a tag of the form `{tag_prefix}{version}`.  Idempotent: exits
        cleanly with code 0 if the tag already exists, so the workflow can be
        re-triggered safely after a transient failure.

        Args:
            dry_run:
                When `True`, print the tag that would be created without
                pushing anything.
        """
        logger.debug("Reading version from %s/pyproject.toml", self.directory)
        version = self.read_version()
        tag_name = self.compute_tag_name(version)
        logger.debug("Computed tag name: %s", tag_name)

        # Fetch tags so the local repo reflects the remote state before checking
        logger.debug("Fetching tags from origin")
        subprocess.check_call(
            ["git", "fetch", "--tags", "origin"],
            cwd=ROOT,
        )

        # Check if the tag already exists
        logger.debug("Checking whether tag %s already exists", tag_name)
        result = subprocess.check_output(
            ["git", "tag", "-l", tag_name],
            text=True,
            cwd=ROOT,
        )
        if result.strip():
            logger.info("Tag %r already exists. Nothing to do.", tag_name)
            sys.exit(0)

        if dry_run:
            logger.info("[dry-run] Would create and push tag %r.", tag_name)
            return

        logger.info("Creating tag %r...", tag_name)
        subprocess.check_call(
            ["git", "tag", tag_name],
            text=True,
            cwd=ROOT,
        )
        logger.debug("Pushing tag %s to origin", tag_name)
        subprocess.check_call(
            ["git", "push", "origin", tag_name],
            text=True,
            cwd=ROOT,
        )
        logger.info("Tag %r pushed.", tag_name)


# Each package uses a different versioning strategy:
#   core  — git cliff --bumped-version derives the next semver from commit history.
#   ffi   — tracks pact-foundation/pact-reference; version is {upstream}.{N}.
#   cli   — tracks pact-foundation/pact-standalone; version is {upstream}.{N}.
# The {N} suffix increments when the upstream semver is unchanged, resets to 0
# on a new upstream release (see compute_wrapper_version).
PACKAGES: dict[str, Package] = {
    "core": Package(
        name="pact-python",
        key="core",
        directory=ROOT,
        tag_prefix="pact-python/",
        upstream_repo=None,
        upstream_tag_prefix=None,
        release_branch="release/pact-python",
    ),
    "ffi": Package(
        name="pact-python-ffi",
        key="ffi",
        directory=ROOT / "pact-python-ffi",
        tag_prefix="pact-python-ffi/",
        upstream_repo="pact-foundation/pact-reference",
        # Filter to libpact_ffi releases only — pact-reference hosts many crates
        upstream_tag_prefix="libpact_ffi-v",
        release_branch="release/pact-python-ffi",
    ),
    "cli": Package(
        name="pact-python-cli",
        key="cli",
        directory=ROOT / "pact-python-cli",
        tag_prefix="pact-python-cli/",
        upstream_repo="pact-foundation/pact-standalone",
        upstream_tag_prefix="v",
        release_branch="release/pact-python-cli",
    ),
}


def strip_tag_prefix(tag_or_version: str, prefix: str) -> str:
    """Strip a tag prefix from a version string if present.

    Args:
        tag_or_version:
            A full tag name (e.g. `"pact-python/3.2.2"`) or a bare version
            string (e.g. `"3.2.2"`).
        prefix:
            The prefix to remove (e.g. `"pact-python/"`).

    Returns:
        The version string with the prefix removed, or the original string if
        the prefix is not present.
    """
    return tag_or_version.removeprefix(prefix)


def compute_wrapper_version(upstream_version: str, current_version: str) -> str:
    """Compute the next 4-part version for wrapper packages.

    The version format is `{upstream_version}.{N}` where `N` is a per-packaging
    suffix, and upstream version will (typically) be a semver-compatible
    version.  When the upstream semver portion matches the current version's
    first three components the suffix is incremented; otherwise the suffix
    resets to 0.

    Args:
        upstream_version:
            The latest upstream semver string, e.g. `"0.4.28"`.
        current_version:
            The current 4-part package version, e.g. `"0.4.28.2"`.

    Returns:
        The next 4-part version string, e.g. `"0.4.28.3"` or `"0.4.29.0"`.
    """
    current_parts = current_version.split(".")
    current_upstream = ".".join(current_parts[:3])
    if upstream_version == current_upstream:
        return f"{upstream_version}.{int(current_parts[3]) + 1}"
    return f"{upstream_version}.0"


def parse_existing_pr(gh_output: str) -> PullRequest | None:
    """Parse JSON output from `gh pr list` into a `PullRequest`, or None.

    Args:
        gh_output:
            Raw stdout from a `gh pr list --json` call.

    Returns:
        A `PullRequest`, or `None` if the output is empty or the JSON
        literal `"null"`.
    """
    text = gh_output.strip()
    if not text or text == "null":
        return None
    data = json.loads(text)
    return PullRequest(number=data["number"], head_ref_name=data["headRefName"])


def check_github_token() -> None:
    """
    Ensure that a GitHub token is set for authenticated API access.

    In CI, the PAT is expected to be provided via the `GH_TOKEN` environment
    variable. When running locally, if `GITHUB_TOKEN` is not already set, this
    function will attempt to retrieve a token using the `gh` CLI tool (which may
    be authenticated via `gh auth login`) and set it in the environment for
    subsequent API calls.

    If no token can be found, a warning is logged and API requests may be
    subject to stricter rate limits.
    """
    if os.getenv("GITHUB_TOKEN"):
        return

    if token := os.getenv("GH_TOKEN"):
        logger.debug("Using GH_TOKEN from environment variable for authentication")
        os.environ["GITHUB_TOKEN"] = token
        return

    if "CI" not in os.environ:
        logger.info("Generating a GitHub token for authenticated API access")
        if token := subprocess.check_output(
            ["gh", "auth", "token"],
            text=True,
        ).strip():
            os.environ["GITHUB_TOKEN"] = token
            return
        logger.warning("No GitHub token found. API requests may be rate-limited.")


def main() -> None:
    """Entry point for the release management script."""
    parser = argparse.ArgumentParser(
        description="Release management for pact-python packages"
    )
    parser.add_argument("command", choices=["prepare", "tag"])
    parser.add_argument("package", choices=["core", "ffi", "cli"])
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Write files but skip all git/GitHub operations",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging to trace each step",
    )
    args = parser.parse_args()

    level = logging.DEBUG if args.debug else logging.INFO
    # Show the level prefix only in debug mode to keep normal output clean
    fmt = "%(levelname)s: %(message)s" if args.debug else "%(message)s"
    logging.basicConfig(level=level, format=fmt)

    pkg = PACKAGES[args.package]

    check_github_token()

    if args.command == "tag":
        pkg.tag(dry_run=args.dry_run)
    elif args.command == "prepare":
        pkg.prepare(dry_run=args.dry_run)
    else:
        sys.stderr.write(f"Unknown command {args.command!r}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
