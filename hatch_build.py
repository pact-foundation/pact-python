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

ROOT_DIR = Path(__file__).parent.resolve()

PACT_BIN_VERSION = os.getenv("PACT_BIN_VERSION", "2.0.7")
PACT_BIN_URL = "https://github.com/pact-foundation/pact-ruby-standalone/releases/download/v{version}/pact-{version}-{os}-{machine}.{ext}"

PACT_LIB_VERSION = os.getenv("PACT_LIB_VERSION", "0.4.9")
PACT_LIB_URL = "https://github.com/pact-foundation/pact-reference/releases/download/libpact_ffi-v{version}/{prefix}pact_ffi-{os}-{machine}.{ext}"


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
        self.pact_lib_install(PACT_LIB_VERSION)

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

    def _pact_bin_url(self, version: str) -> str | None:  # noqa: PLR0911
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
                msg = f"Unknown macOS machine {platform}"
                warnings.warn(msg, RuntimeWarning, stacklevel=2)
                return None
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
                msg = f"Unknown Windows machine {platform}"
                warnings.warn(msg, RuntimeWarning, stacklevel=2)
                return None
            return PACT_BIN_URL.format(
                version=version,
                os=os,
                machine=machine,
                ext="zip",
            )

        if "linux" in platform and "musl" not in platform:
            os = "linux"
            if platform.endswith("x86_64"):
                machine = "x86_64"
            elif platform.endswith("aarch64"):
                machine = "arm64"
            else:
                msg = f"Unknown Linux machine {platform}"
                warnings.warn(msg, RuntimeWarning, stacklevel=2)
                return None
            return PACT_BIN_URL.format(
                version=version,
                os=os,
                machine=machine,
                ext="tar.gz",
            )

        msg = f"Unknown platform {platform}"
        warnings.warn(msg, RuntimeWarning, stacklevel=2)
        return None

    def _pact_bin_extract(self, artifact: Path) -> None:
        """
        Extract the Pact binaries.

        The upstream distributables contain a lot of files which are not needed
        for this library. This function ensures that only the files in
        `pact/bin` are extracted to avoid unnecessary bloat.

        Args:
            artifact: The path to the downloaded artifact.
        """
        (ROOT_DIR / "pact" / "bin").mkdir(parents=True, exist_ok=True)

        if str(artifact).endswith(".zip"):
            with zipfile.ZipFile(artifact) as f:
                for member in f.namelist():
                    if member.startswith("pact/bin"):
                        f.extract(member, ROOT_DIR)

        if str(artifact).endswith(".tar.gz"):
            with tarfile.open(artifact) as f:
                for member in f.getmembers():
                    if member.name.startswith("pact/bin"):
                        f.extract(member, ROOT_DIR)

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
            os = "osx"
            if platform.endswith("arm64"):
                machine = "aarch64-apple-darwin"
            elif platform.endswith("x86_64"):
                machine = "x86_64"
            else:
                msg = f"Unknown macOS machine {platform}"
                raise ValueError(msg)
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
            else:
                msg = f"Unknown Windows machine {platform}"
                raise ValueError(msg)
            return PACT_LIB_URL.format(
                prefix="",
                version=version,
                os=os,
                machine=machine,
                ext="lib.gz",
            )

        if "linux" in platform and "musl" in platform:
            os = "linux"
            if platform.endswith("x86_64"):
                machine = "x86_64-musl"
            else:
                msg = f"Unknown MUSL Linux machine {platform}"
                raise ValueError(msg)
            return PACT_LIB_URL.format(
                prefix="lib",
                version=version,
                os=os,
                machine=machine,
                ext="a.gz",
            )

        if "linux" in platform:
            os = "linux"
            if platform.endswith("x86_64"):
                machine = "x86_64"
            elif platform.endswith("aarch64"):
                machine = "aarch64"
            else:
                msg = f"Unknown Linux machine {platform}"
                raise ValueError(msg)

            return PACT_LIB_URL.format(
                prefix="lib",
                version=version,
                os=os,
                machine=machine,
                ext="a.gz",
            )

        msg = f"Unknown platform {platform}"
        raise ValueError(msg)

    def _pact_lib_extract(self, artifact: Path) -> None:
        """
        Extract the Pact library.

        Extract the Pact library from the downloaded artifact and place it in
        `pact/lib`.

        Args:
            artifact: The URL to download the Pact binaries from.
        """
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
        output = ffibuilder.compile(verbose=True, tmpdir=str(self.tmpdir))
        shutil.copy(output, ROOT_DIR / "pact" / "v3")

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
