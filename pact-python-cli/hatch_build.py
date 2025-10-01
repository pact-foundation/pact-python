"""
Hatchling build hook.

This hook is responsible for downloading and packaging the Pact CLI.
"""

from __future__ import annotations

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

PKG_DIR = Path(__file__).parent.resolve() / "src" / "pact_cli"
PACT_CLI_URL = "https://github.com/pact-foundation/pact-standalone/releases/download/v{version}/pact-{version}-{os}-{machine}.{ext}"


class UnsupportedPlatformError(RuntimeError):
    """
    Custom error raised when the current platform is not supported.
    """

    def __init__(self, platform: str) -> None:
        """
        Initialize the exception.

        Args:
            platform:
                The unsupported platform.
        """
        self.platform = platform
        super().__init__(f"Unsupported platform {platform}")


class PactCliBuildHook(BuildHookInterface[BuilderConfig]):
    """
    Custom hook to download Pact CLI binaries.

    This build hook is invoked by Hatch during the build process. Within
    `pyproject.toml`, it takes the special name of `custom` (despite the name
    below).

    For more references, see [Build hook
    plugins](https://hatch.pypa.io/1.3/plugins/build-hook/reference/).
    """

    PLUGIN_NAME = "pact-cli"

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        """
        Initialize the build hook.

        For this hook, we additionally define the lib extension based on the
        current platform.
        """
        super().__init__(*args, **kwargs)
        self.tmpdir = Path(tempfile.TemporaryDirectory().name)
        self.tmpdir.mkdir(parents=True, exist_ok=True)

    def __del__(self) -> None:
        """
        Clean up temporary files.
        """
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def clean(self, versions: list[str]) -> None:  # noqa: ARG002
        """
        Code called to clean.

        This is called by `hatch clean` or when the `-c`/`--clean` flag is
        passed to `hatch build`.
        """
        for subdir in ["bin", "lib", "data"]:
            shutil.rmtree(PKG_DIR / subdir, ignore_errors=True)

    def initialize(
        self,
        version: str,  # noqa: ARG002
        build_data: dict[str, object],
    ) -> None:
        """
        Code called immediately before each build.

        The CLI version is inferred from the package metadata. Specifically, the
        first three segments of the version string are used.

        Args:
            version:
                Not used (but required by the parent class).

            build_data:
                A dictionary to modify in-place used by Hatch when creating the
                final wheel.

        Raises:
            UnsupportedPlatformError:
                If the CLI cannot be built (presumably due to an
                incompatible platform).
        """
        cli_version = ".".join(self.metadata.version.split(".")[:3])
        if not cli_version:
            msg = "Failed to determine Pact CLI version."
            self.app.display_error(msg)
            raise ValueError(msg)

        try:
            build_data["force_include"] = self._install(cli_version)
        except UnsupportedPlatformError as err:
            msg = f"Pact CLI is not available for {err.platform}."
            self.app.display_error(msg)
            raise

        build_data["tag"] = self._infer_tag()

    def _sys_tag_platform(self) -> str:
        """
        Get the platform tag from the current system tags.

        This is used to determine the target platform for the Pact binaries.
        """
        return next(t.platform for t in sys_tags())

    def _install(self, version: str) -> dict[str, str]:
        """
        Install the Pact standalone binaries.

        The binaries are installed in `src/pact_cli/bin`, and the relevant
        version for the current operating system is determined automatically.

        Args:
            version:
                The Pact CLI version to install.

        Returns:
            A mapping of `src` to `dst` to be used by Hatch when creating the
            wheel. Each `src` is a full path in the current filesystem, and the
            `dst` is the corresponding path within the wheel.
        """
        url = self._pact_bin_url(version)
        artefact = self._download(url)
        self._extract(artefact)
        return {
            str(PKG_DIR / "bin"): "pact_cli/bin",
            str(PKG_DIR / "lib"): "pact_cli/lib",
        }

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
            os_name = "osx"
            ext = "tar.gz"
        elif "linux" in platform:
            os_name = "linux"
            ext = "tar.gz"
        elif platform.startswith("win"):
            os_name = "windows"
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

        return PACT_CLI_URL.format(
            version=version,
            os=os_name,
            machine=machine,
            ext=ext,
        )

    def _extract(self, artefact: Path) -> None:
        """
        Extract the Pact binaries.

        The binaries in the `bin` directory require the underlying Ruby runtime
        to be present, which is included in the `lib` directory.

        Args:
            artefact:
                The path to the downloaded artefact.
        """
        if str(artefact).endswith(".zip"):
            with zipfile.ZipFile(artefact) as f:
                f.extractall(self.tmpdir)  # noqa: S202

        if str(artefact).endswith(".tar.gz"):
            with tarfile.open(artefact) as f:
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

        This will download the target URL to the `src/pact_cli/data` directory.
        If the download artefact is already present, the existing artefact's
        path will be returned without downloading it again.

        Args:
            url:
                The URL to download

        Return:
            The path to the downloaded artefact.
        """
        filename = url.split("/")[-1]
        artefact = PKG_DIR / "data" / filename
        artefact.parent.mkdir(parents=True, exist_ok=True)

        if not artefact.exists():
            urllib.request.urlretrieve(url, artefact)  # noqa: S310
        return artefact

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
