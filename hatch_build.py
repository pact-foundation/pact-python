"""Hatchling build hook for Pact binary download."""

from __future__ import annotations

import os
import shutil
import typing
from pathlib import Path
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from packaging.tags import sys_tags

ROOT_DIR = Path(__file__).parent.resolve()
PACT_VERSION = "2.0.3"
PACT_URL = "https://github.com/pact-foundation/pact-ruby-standalone/releases/download/v{version}/pact-{version}-{os}-{machine}.{ext}"
PACT_DISTRIBUTIONS: list[tuple[str, str, str]] = [
    ("linux", "arm64", "tar.gz"),
    ("linux", "x86_64", "tar.gz"),
    ("osx", "arm64", "tar.gz"),
    ("osx", "x86_64", "tar.gz"),
    ("windows", "x86", "zip"),
    ("windows", "x86_64", "zip"),
]


class PactBuildHook(BuildHookInterface):
    """Custom hook to download Pact binaries."""

    PLUGIN_NAME = "custom"

    def clean(self, versions: list[str]) -> None:  # noqa: ARG002
        """Clean up any files created by the build hook."""
        for subdir in ["bin", "lib", "data"]:
            shutil.rmtree(ROOT_DIR / "pact" / subdir, ignore_errors=True)

    def initialize(
        self,
        version: str,  # noqa: ARG002
        build_data: dict[str, Any],
    ) -> None:
        """Hook into Hatchling's build process."""
        build_data["infer_tag"] = True
        build_data["pure_python"] = False

        pact_version = os.getenv("PACT_VERSION", PACT_VERSION)
        self.install_pact_binaries(pact_version)

    def install_pact_binaries(self, version: str) -> None:  # noqa: PLR0912
        """
        Install the Pact standalone binaries.

        The binaries are installed in `pact/bin`, and the relevant version for
        the current operating system is determined automatically.

        Args:
            version: The Pact version to install. Defaults to the value in
            `PACT_VERSION`.
        """
        platform = typing.cast(str, next(sys_tags()).platform)

        if platform.startswith("macosx"):
            os = "osx"
            if platform.endswith("arm64"):
                machine = "arm64"
            elif platform.endswith("x86_64"):
                machine = "x86_64"
            else:
                msg = f"Unknown macOS machine {platform}"
                raise ValueError(msg)
            url = PACT_URL.format(version=version, os=os, machine=machine, ext="tar.gz")

        elif platform.startswith("win"):
            os = "windows"

            if platform.endswith("amd64"):
                machine = "x86_64"
            elif platform.endswith(("x86", "win32")):
                machine = "x86"
            else:
                msg = f"Unknown Windows machine {platform}"
                raise ValueError(msg)

            url = PACT_URL.format(version=version, os=os, machine=machine, ext="zip")

        elif "linux" in platform:
            os = "linux"
            if platform.endswith("x86_64"):
                machine = "x86_64"
            elif platform.endswith("aarch64"):
                machine = "arm64"
            else:
                msg = f"Unknown Linux machine {platform}"
                raise ValueError(msg)

            url = PACT_URL.format(version=version, os=os, machine=machine, ext="tar.gz")

        else:
            msg = f"Unknown platform {platform}"
            raise ValueError(msg)

        self.download_and_extract_pact(url)

    def download_and_extract_pact(self, url: str) -> None:
        """
        Download and extract the Pact binaries.

        If the download artifact is already present, it will be used instead of
        downloading it again.

        Args:
            url: The URL to download the Pact binaries from.
        """
        filename = url.split("/")[-1]
        artifact = ROOT_DIR / "pact" / "data" / filename
        artifact.parent.mkdir(parents=True, exist_ok=True)

        if not filename.endswith((".zip", ".tar.gz")):
            msg = f"Unknown artifact type {filename}"
            raise ValueError(msg)

        if not artifact.exists():
            import requests

            response = requests.get(url, timeout=30)
            response.raise_for_status()
            with artifact.open("wb") as f:
                f.write(response.content)

        if filename.endswith(".zip"):
            import zipfile

            with zipfile.ZipFile(artifact) as f:
                f.extractall(ROOT_DIR)
        if filename.endswith(".tar.gz"):
            import tarfile

            with tarfile.open(artifact) as f:
                f.extractall(ROOT_DIR)

        # Move the README that is extracted from the Ruby standalone binaries to
        # the `data` subdirectory.
        if (ROOT_DIR / "pact" / "README.md").exists():
            shutil.move(
                ROOT_DIR / "pact" / "README.md",
                ROOT_DIR / "pact" / "data" / "README.md",
            )
