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

import gzip
import os
import shutil
import tarfile
import tempfile
import warnings
import zipfile
from pathlib import Path
from typing import Any, Dict

import cffi
import requests
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from packaging.tags import sys_tags

PACT_ROOT_DIR = Path(__file__).parent.resolve() / "src" / "pact"

# Latest version available at:
# https://github.com/pact-foundation/pact-ruby-standalone/releases
PACT_BIN_VERSION = os.getenv("PACT_BIN_VERSION", "2.4.1")
PACT_BIN_URL = "https://github.com/pact-foundation/pact-ruby-standalone/releases/download/v{version}/pact-{version}-{os}-{machine}.{ext}"

# Latest version available at:
# https://github.com/pact-foundation/pact-reference/releases
PACT_LIB_VERSION = os.getenv("PACT_LIB_VERSION", "0.4.21")
PACT_LIB_URL = "https://github.com/pact-foundation/pact-reference/releases/download/libpact_ffi-v{version}/{prefix}pact_ffi-{os}-{machine}.{ext}"


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
            shutil.rmtree(PACT_ROOT_DIR / subdir, ignore_errors=True)

        for ffi in (PACT_ROOT_DIR / "v3").glob("_ffi.*"):
            if ffi.name == "_ffi.pyi":
                continue
            ffi.unlink()

    def initialize(
        self,
        version: str,  # noqa: ARG002
        build_data: Dict[str, Any],
    ) -> None:
        """Hook into Hatchling's build process."""
        build_data["infer_tag"] = True
        build_data["pure_python"] = False

        binaries_included = False
        try:
            self.pact_bin_install(PACT_BIN_VERSION)
            binaries_included = True
        except UnsupportedPlatformError as err:
            msg = f"Pact binaries on not available for {err.platform}."
            warnings.warn(msg, RuntimeWarning, stacklevel=2)

        try:
            self.pact_lib_install(PACT_LIB_VERSION)
            binaries_included = True
        except UnsupportedPlatformError as err:
            msg = f"Pact library is not available for {err.platform}"
            warnings.warn(msg, RuntimeWarning, stacklevel=2)

        if not binaries_included:
            msg = "Wheel does not include any binaries. Aborting."
            raise UnsupportedPlatformError(msg)

    def pact_bin_install(self, version: str) -> None:
        """
        Install the Pact standalone binaries.

        The binaries are installed in `src/pact/bin`, and the relevant version for
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

        The binaries in the `bin` directory require the underlying Ruby runtime
        to be present, which is included in the `lib` directory.

        Args:
            artifact: The path to the downloaded artifact.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            if str(artifact).endswith(".zip"):
                with zipfile.ZipFile(artifact) as f:
                    f.extractall(tmpdir)  # noqa: S202

            if str(artifact).endswith(".tar.gz"):
                with tarfile.open(artifact) as f:
                    f.extractall(tmpdir)  # noqa: S202

            for d in ["bin", "lib"]:
                if (PACT_ROOT_DIR / d).is_dir():
                    shutil.rmtree(PACT_ROOT_DIR / d)
                shutil.copytree(
                    Path(tmpdir) / "pact" / d,
                    PACT_ROOT_DIR / d,
                )

    def pact_lib_install(self, version: str) -> None:
        """
        Install the Pact library binary.

        The library is installed in `pact/lib`, and the relevant version for
        the current operating system is determined automatically.

        Args:
            version: The Pact version to install.
        """
        url = self._pact_lib_url(version)
        artifact = self._download(url)
        self._pact_lib_extract(artifact)
        includes = self._pact_lib_header(url)
        self._pact_lib_cffi(includes)

    def _pact_lib_url(self, version: str) -> str:  # noqa: C901, PLR0912
        """
        Generate the download URL for the Pact library.

        Generate the download URL for the Pact library based on the current
        platform and specified version. This function mainly contains a lot of
        matching logic to determine the correct URL to use, due to the
        inconsistencies in naming conventions between ecosystems.

        Args:
            version: The upstream Pact version.

        Returns:
            The URL to download the Pact library from.

        Raises:
            ValueError:
                If the current platform is not supported.
        """
        platform = next(sys_tags()).platform

        if platform.startswith("macosx"):
            os = "macos"
            if platform.endswith("arm64"):
                machine = "aarch64"
            elif platform.endswith("x86_64"):
                machine = "x86_64"
            else:
                raise UnsupportedPlatformError(platform)
            return PACT_LIB_URL.format(
                prefix="lib",
                version=version,
                os=os,
                machine=machine,
                ext="a.gz",
            )

        if platform.startswith("win"):
            os = "windows"

            if platform.endswith("amd64"):
                machine = "x86_64"
            elif platform.endswith(("arm64", "aarch64")):
                machine = "aarch64"
            else:
                raise UnsupportedPlatformError(platform)
            return PACT_LIB_URL.format(
                prefix="",
                version=version,
                os=os,
                machine=machine,
                ext="lib.gz",
            )

        if "musllinux" in platform:
            os = "linux"
            if platform.endswith("x86_64"):
                machine = "x86_64-musl"
            elif platform.endswith("aarch64"):
                machine = "aarch64-musl"
            else:
                raise UnsupportedPlatformError(platform)
            return PACT_LIB_URL.format(
                prefix="lib",
                version=version,
                os=os,
                machine=machine,
                ext="a.gz",
            )

        if "manylinux" in platform:
            os = "linux"
            if platform.endswith("x86_64"):
                machine = "x86_64"
            elif platform.endswith("aarch64"):
                machine = "aarch64"
            else:
                raise UnsupportedPlatformError(platform)

            return PACT_LIB_URL.format(
                prefix="lib",
                version=version,
                os=os,
                machine=machine,
                ext="a.gz",
            )

        raise UnsupportedPlatformError(platform)

    def _pact_lib_extract(self, artifact: Path) -> None:
        """
        Extract the Pact library.

        Extract the Pact library from the downloaded artifact and place it in
        `pact/lib`.

        Args:
            artifact: The URL to download the Pact binaries from.
        """
        # Pypy does not guarantee that the directory exists.
        self.tmpdir.mkdir(parents=True, exist_ok=True)

        if not str(artifact).endswith(".gz"):
            msg = f"Unknown artifact type {artifact}"
            raise ValueError(msg)

        with gzip.open(artifact, "rb") as f_in, (
            self.tmpdir / (artifact.name.split("-")[0] + artifact.suffixes[0])
        ).open("wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    def _pact_lib_header(self, url: str) -> list[str]:
        """
        Download the Pact library header.

        Download the Pact library header from GitHub and place it in
        `pact/include`. This uses the same URL as for the artifact, replacing
        the final segment with `pact.h`.

        This also processes the header to strip out elements which are not
        supported by CFFI (i.e., any line starting with `#`). The list of
        `#include` statements is returned for use in the CFFI bindings.

        Args:
            url: The URL pointing to the Pact library artifact.
        """
        # Pypy does not guarantee that the directory exists.
        self.tmpdir.mkdir(parents=True, exist_ok=True)

        url = url.rsplit("/", 1)[0] + "/pact.h"
        artifact = self._download(url)
        includes: list[str] = []
        with artifact.open("r", encoding="utf-8") as f_in, (
            self.tmpdir / "pact.h"
        ).open("w", encoding="utf-8") as f_out:
            for line in f_in:
                sline = line.strip()
                if sline.startswith("#include"):
                    includes.append(sline)
                    continue
                if sline.startswith("#"):
                    continue

                f_out.write(line)
        return includes

    def _pact_lib_cffi(self, includes: list[str]) -> None:
        """
        Build the CFFI bindings for the Pact library.

        This will build the CFFI bindings for the Pact library and place them in
        `pact/lib`.

        A list of additional `#include` statements can be passed to this
        function, which will be included in the generated bindings.

        Args:
            includes:
                A list of additional `#include` statements to include in the
                generated bindings.
        """
        if os.name == "nt":
            extra_libs = [
                "advapi32",
                "bcrypt",
                "crypt32",
                "iphlpapi",
                "ncrypt",
                "netapi32",
                "ntdll",
                "ole32",
                "oleaut32",
                "pdh",
                "powrprof",
                "psapi",
                "secur32",
                "shell32",
                "user32",
                "userenv",
                "ws2_32",
            ]
        else:
            extra_libs = []

        ffibuilder = cffi.FFI()
        with (self.tmpdir / "pact.h").open(
            "r",
            encoding="utf-8",
        ) as f:
            ffibuilder.cdef(f.read())
        ffibuilder.set_source(
            "_ffi",
            "\n".join([*includes, '#include "pact.h"']),
            libraries=["pact_ffi", *extra_libs],
            library_dirs=[str(self.tmpdir)],
        )
        output = Path(ffibuilder.compile(verbose=True, tmpdir=str(self.tmpdir)))
        shutil.copy(output, PACT_ROOT_DIR / "v3")

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
        artifact = PACT_ROOT_DIR / "data" / filename
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
