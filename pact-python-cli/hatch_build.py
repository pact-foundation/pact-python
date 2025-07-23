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

import logging
import os
import shutil
import sys
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

from hatchling.builders.config import BuilderConfig
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from packaging.tags import sys_tags

logger = logging.getLogger(__name__)

EXE = ".exe" if os.name == "nt" else ""
PKG_DIR = Path(__file__).parent.resolve() / "src" / "pact_cli"
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


class PactCliBuildHook(BuildHookInterface[BuilderConfig]):
    """Custom hook to download Pact binaries."""

    PLUGIN_NAME = "pact-cli"

    def __init__(self, *args: object, **kwargs: object) -> None:
        """
        Initialize the build hook.

        For this hook, we additionally define the lib extension based on the
        current platform.
        """
        super().__init__(*args, **kwargs)
        self.tmpdir = Path(tempfile.TemporaryDirectory().name)

    def clean(self, versions: list[str]) -> None:  # noqa: ARG002
        """Clean up any files created by the build hook."""
        for subdir in ["bin", "lib", "data"]:
            shutil.rmtree(PKG_DIR / subdir, ignore_errors=True)

    def initialize(
        self,
        version: str,  # noqa: ARG002
        build_data: dict[str, Any],
    ) -> None:
        """Hook into Hatchling's build process."""
        cli_version = ".".join(self.metadata.version.split(".")[:3])
        if not cli_version:
            self.app.display_error("Failed to determine Pact CLI version.")

        try:
            self._pact_bin_install(cli_version)
        except UnsupportedPlatformError as err:
            msg = f"Pact CLI is not available for {err.platform}."
            logger.exception(msg, RuntimeWarning, stacklevel=2)

        build_data["tag"] = self._infer_tag()

    def _sys_tag_platform(self) -> str:
        """
        Get the platform tag from the current system tags.

        This is used to determine the target platform for the Pact binaries.
        """
        return next(t.platform for t in sys_tags())

    def _pact_bin_install(self, version: str) -> None:
        """
        Install the Pact standalone binaries.

        The binaries are installed in `src/pact_cli/bin`, and the relevant
        version for the current operating system is determined automatically.

        Args:
            version:
                The Pact CLI version to install.
        """
        url = self._pact_bin_url(version)
        artifact = self._download(url)
        self._pact_bin_extract(artifact)

    def _pact_bin_url(self, version: str) -> str:
        """
        Generate the download URL for the Pact binaries.

        Args:
            version:
                The Pact CLI version to download.

        Returns:
            The URL to download the Pact binaries from. If the platform is not
            supported, the resulting URL may be invalid.
        """
        platform = self._sys_tag_platform()

        if platform.startswith("macosx"):
            os = "osx"
            ext = "tar.gz"
        elif "linux" in platform:
            os = "linux"
            ext = "tar.gz"
        elif platform.startswith("win"):
            os = "windows"
            ext = "zip"
        else:
            raise UnsupportedPlatformError(platform)

        if platform.endswith(("arm64", "aarch64")):
            machine = "arm64"
        elif platform.endswith(("x86_64", "amd64")):
            machine = "x86_64"
        elif platform.endswith(("i386", "i686", "x86", "win32")):
            machine = "x86"
        else:
            raise UnsupportedPlatformError(platform)

        return PACT_BIN_URL.format(
            version=version,
            os=os,
            machine=machine,
            ext=ext,
        )

    def _pact_bin_extract(self, artifact: Path) -> None:
        """
        Extract the Pact binaries.

        The binaries in the `bin` directory require the underlying Ruby runtime
        to be present, which is included in the `lib` directory.

        Args:
            artifact: The path to the downloaded artifact.
        """
        if str(artifact).endswith(".zip"):
            with zipfile.ZipFile(artifact) as f:
                f.extractall(self.tmpdir)  # noqa: S202

        if str(artifact).endswith(".tar.gz"):
            with tarfile.open(artifact) as f:
                f.extractall(self.tmpdir)  # noqa: S202

        for d in ["bin", "lib"]:
            if (PKG_DIR / d).is_dir():
                shutil.rmtree(PKG_DIR / d)
            shutil.copytree(
                Path(self.tmpdir) / "pact" / d,
                PKG_DIR / d,
            )

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
        artifact = PKG_DIR / "data" / filename
        artifact.parent.mkdir(parents=True, exist_ok=True)

        if not artifact.exists():
            urllib.request.urlretrieve(url, artifact)  # noqa: S310

        return artifact

    def _infer_tag(self) -> str:
        """
        Infer the tag for the current build.

        Since we have a pure Python wrapper around a binary CLI, we are not
        tied to any specific Python version or ABI. As a result, we generate
        `py3-none-{platform}` tags for the wheels.
        """
        platform = self._sys_tag_platform()

        # On macOS, the version needs to be set based on the deployment target
        # (i.e., the version of the system libraries).
        if sys.platform == "darwin" and (
            deployment_target := os.environ.get("MACOSX_DEPLOYMENT_TARGET")
        ):
            target = deployment_target.replace(".", "_")
            if platform.endswith("_arm64"):
                platform = f"macosx_{target}_arm64"
            elif platform.endswith("_x86_64"):
                platform = f"macosx_{target}_x86_64"
            else:
                raise UnsupportedPlatformError(platform)

        return f"py3-none-{platform}"
