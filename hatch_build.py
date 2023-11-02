"""
Hatchling build hook for binary downloads.

Pact Python is built on top of the Ruby Pact binaries and the Rust Pact library.
This build script downloads the binaries and library for the current platform
and installs them in the `pact` directory under `/bin` and `/lib`.

The version of the binaries and library can be controlled with the
`PACT_BIN_VERSION` and `PACT_LIB_VERSION` environment variables. If these are
not set, a pinned version will be used instead.
"""

from __future__ import annotations

import os
import shutil
import tarfile
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Dict

import requests
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from packaging.tags import sys_tags

ROOT_DIR = Path(__file__).parent.resolve()

PACT_BIN_VERSION = os.getenv("PACT_BIN_VERSION", "2.0.10")
PACT_BIN_URL = "https://github.com/pact-foundation/pact-ruby-standalone/releases/download/v{version}/pact-{version}-{os}-{machine}.{ext}"


class UnsupportedPlatformError(RuntimeError):
    """Raised when the current platform is not supported."""

    def __init__(self, platform: str) -> None:
        """
        Initialize the exception.

        Args:
            platform: The unsupported platform.
        """
        self.platform = platform
        super().__init__(f"Unsupported platform {platform}")


class PactBuildHook(BuildHookInterface[Any]):
    """Custom hook to download Pact binaries."""

    PLUGIN_NAME = "custom"

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        """
        Initialize the build hook.

        For this hook, we additionally define the lib extension based on the
        current platform.
        """
        super().__init__(*args, **kwargs)
        self.tmpdir = Path(tempfile.TemporaryDirectory().name)
        self.tmpdir.mkdir(parents=True, exist_ok=True)

    def clean(self, versions: list[str]) -> None:  # noqa: ARG002
        """Clean up any files created by the build hook."""
        for subdir in ["bin", "lib", "data"]:
            shutil.rmtree(ROOT_DIR / "pact" / subdir, ignore_errors=True)

    def initialize(
        self,
        version: str,  # noqa: ARG002
        build_data: Dict[str, Any],
    ) -> None:
        """Hook into Hatchling's build process."""
        build_data["infer_tag"] = True
        build_data["pure_python"] = False

        self.pact_bin_install(PACT_BIN_VERSION)

    def pact_bin_install(self, version: str) -> None:
        """
        Install the Pact standalone binaries.

        The binaries are installed in `pact/bin`, and the relevant version for
        the current operating system is determined automatically.

        Args:
            version: The Pact version to install.
        """
        url = self._pact_bin_url(version)
        if url:
            artifact = self._download(url)
            self._pact_bin_extract(artifact)

    def _pact_bin_url(self, version: str) -> str | None:
        """
        Generate the download URL for the Pact binaries.

        Generate the download URL for the Pact binaries based on the current
        platform and specified version. This function mainly contains a lot of
        matching logic to determine the correct URL to use, due to the
        inconsistencies in naming conventions between ecosystems.

        Args:
            version: The upstream Pact version.

        Returns:
            The URL to download the Pact binaries from, or None if the current
            platform is not supported.
        """
        platform = next(sys_tags()).platform

        if platform.startswith("macosx"):
            os = "osx"
            if platform.endswith("arm64"):
                machine = "arm64"
            elif platform.endswith("x86_64"):
                machine = "x86_64"
            else:
                raise UnsupportedPlatformError(platform)
            return PACT_BIN_URL.format(
                version=version,
                os=os,
                machine=machine,
                ext="tar.gz",
            )

        if platform.startswith("win"):
            os = "windows"

            if platform.endswith("amd64"):
                machine = "x86_64"
            elif platform.endswith(("x86", "win32")):
                machine = "x86"
            else:
                raise UnsupportedPlatformError(platform)
            return PACT_BIN_URL.format(
                version=version,
                os=os,
                machine=machine,
                ext="zip",
            )

        if "manylinux" in platform:
            os = "linux"
            if platform.endswith("x86_64"):
                machine = "x86_64"
            elif platform.endswith("aarch64"):
                machine = "arm64"
            else:
                raise UnsupportedPlatformError(platform)
            return PACT_BIN_URL.format(
                version=version,
                os=os,
                machine=machine,
                ext="tar.gz",
            )

        raise UnsupportedPlatformError(platform)

    def _pact_bin_extract(self, artifact: Path) -> None:
        """
        Extract the Pact binaries.

        The upstream distributables contain a lot of files which are not needed
        for this library. This function ensures that only the files in
        `pact/bin` are extracted to avoid unnecessary bloat.

        Args:
            artifact: The path to the downloaded artifact.
        """
        if str(artifact).endswith(".zip"):
            with zipfile.ZipFile(artifact) as f:
                f.extractall(ROOT_DIR)

        if str(artifact).endswith(".tar.gz"):
            with tarfile.open(artifact) as f:
                f.extractall(ROOT_DIR)

        # Cleanup the extract `README.md`
        (ROOT_DIR / "pact" / "README.md").unlink()

    def _download(self, url: str) -> Path:
        """
        Download the target URL.

        This will download the target URL to the `pact/data` directory. If the
        download artifact is already present, its path will be returned.

        Args:
            url: The URL to download

        Return:
            The path to the downloaded artifact.
        """
        filename = url.split("/")[-1]
        artifact = ROOT_DIR / "pact" / "data" / filename
        artifact.parent.mkdir(parents=True, exist_ok=True)

        if not artifact.exists():
            response = requests.get(url, timeout=30)
            try:
                response.raise_for_status()
            except requests.HTTPError as e:
                msg = f"Failed to download from {url}."
                raise RuntimeError(msg) from e
            with artifact.open("wb") as f:
                f.write(response.content)

        return artifact
