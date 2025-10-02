"""
Hatchling build hook.

This hook is responsible for download the Pact FFI library and building the
CFFI bindings for it.
"""

from __future__ import annotations

import gzip
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

import cffi
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from packaging.tags import sys_tags

PKG_DIR = Path(__file__).parent.resolve() / "src" / "pact_ffi"
PACT_LIB_URL = "https://github.com/pact-foundation/pact-reference/releases/download/libpact_ffi-v{version}/{prefix}pact_ffi-{os}-{platform}{suffix}.{ext}"


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


class PactBuildHook(BuildHookInterface[Any]):
    """
    Custom hook to download Pact binaries.

    This build hook is invoked by Hatch during the build process. Within
    `pyproject.toml`, is takes the special name of `custom` (despite the name
    below).

    For more references, see [Build hook
    plugins](https://hatch.pypa.io/1.3/plugins/build-hook/reference/).
    """

    PLUGIN_NAME = "pact-ffi"

    def __init__(self, *args: object, **kwargs: object) -> None:
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
        # Cleanup the Python extension
        for ffi in PKG_DIR.glob("ffi.*"):
            if ffi.suffix in (".so", ".dylib", ".dll", ".a", ".pyd"):
                ffi.unlink()
        # Cleanup the Pact FFI library
        for lib in PKG_DIR.glob("*pact_ffi.*"):
            lib.unlink()
        # Cleanup the data directory
        shutil.rmtree(PKG_DIR / "data", ignore_errors=True)

    def initialize(
        self,
        version: str,  # noqa: ARG002
        build_data: dict[str, object],
    ) -> None:
        """
        Code called immediately before each build.

        Args:
            version:
                Not used (but required by the parent class).

            build_data:
                A dictionary to modify in-place used by Hatch when creating the
                final wheel.

        Raises:
            UnsupportedPlatformError:
                If the C extension cannot be built (presumably due to an
                incompatible platform).
        """
        ffi_version = ".".join(self.metadata.version.split(".")[:3])
        if not ffi_version:
            msg = "Failed to determine Pact FFI version."
            self.app.display_error(msg)
            raise ValueError(msg)

        try:
            build_data["force_include"] = self._install(ffi_version)
        except UnsupportedPlatformError as err:
            msg = f"Pact FFI library is not available for {err.platform}"
            self.app.display_error(msg)

        self.app.display_debug(f"Wheel artefacts: {build_data['force_include']}")
        build_data["tag"] = self._infer_tag()

    def _sys_tag_platform(self) -> str:
        """
        Get the platform tag from the current system tags.

        This is used to determine the target platform for the Pact library.
        """
        return next(t.platform for t in sys_tags())

    def _install(self, version: str) -> dict[str, str]:
        """
        Install the Pact library binary.

        This will download the Pact library binary for the current platform and
        build the CFFI bindings for it.

        Args:
            version:
                The Pact version to install.

        Returns:
            A mapping of `src` to `dst` to be used by Hatch when creating the
            wheel. Each `src` is a full path in the current filesystem, and the
            `dst` is the corresponding path within the wheel.
        """
        # Download the Pact library binary and header file
        lib_url = self._lib_url(version)
        header = self._download(lib_url.rsplit("/", 1)[0] + "/pact.h")
        lib = self._extract_lib(self._download(lib_url))
        if lib.suffix == ".dll":
            dll_lib = self._extract_lib(
                self._download(lib_url.replace(".dll.gz", ".dll.lib.gz"))
            )
        else:
            dll_lib = None

        # Compile the FFI extension
        extension = self._compile(lib, header)

        # Copy into the package directory, using the ABI3 marking for broad
        # compatibility.
        # NOTE: Windows does _not_ use the version infixation
        name = extension.name.split(".")[0]
        suffix = extension.suffix
        infix = ".abi3" if os.name != "nt" else ""
        extension_dest = f"{name}{infix}{suffix}"
        shutil.copy(extension, PKG_DIR / extension_dest)

        if pact_lib_dir := os.getenv("PACT_LIB_DIR"):
            # Copy the library to make it available by other processes (such as
            # the wheel repair).
            dir_path = Path(pact_lib_dir)
            dir_path.mkdir(parents=True, exist_ok=True)
            self.app.display_debug(f"Copying {lib.name} into {dir_path}")
            shutil.copy(lib, dir_path / lib.name)
            if dll_lib:
                self.app.display_debug(f"Copying {dll_lib.name} into {dir_path}")
                shutil.copy(dll_lib, dir_path / dll_lib.name)

        return {str(extension): f"pact_ffi/{extension_dest}"}

    def _lib_url(self, version: str) -> str:  # noqa: C901, PLR0912
        """
        Generate the download URL for the Pact library.

        Args:
            version:
                The upstream Pact version.

        Returns:
            The URL to download the Pact library from.

        Raises:
            UnsupportedPlatformError:
                If the current platform is not supported.
        """
        wheel_platform = self._sys_tag_platform()

        aarch64 = ("_arm64", "_aarch64")
        x86_64 = ("_x86_64", "_amd64")

        # Simplified platform and architecture detection
        if wheel_platform.startswith("macosx"):
            os, ext = "macos", "dylib.gz"
            prefix = "lib"
            suffix = ""
            if wheel_platform.endswith(aarch64):
                platform = "aarch64"
            elif wheel_platform.endswith(x86_64):
                platform = "x86_64"
            else:
                raise UnsupportedPlatformError(wheel_platform)

        elif wheel_platform.startswith("musllinux"):
            os, ext = "linux", "a.gz"  # MUSL uses static library
            prefix = "lib"
            suffix = "-musl"
            if wheel_platform.endswith(aarch64):
                platform = "aarch64"
            elif wheel_platform.endswith(x86_64):
                platform = "x86_64"
            else:
                raise UnsupportedPlatformError(wheel_platform)

        elif wheel_platform.startswith("manylinux"):
            os, ext = "linux", "so.gz"
            prefix = "lib"
            suffix = ""
            if wheel_platform.endswith(aarch64):
                platform = "aarch64"
            elif wheel_platform.endswith(x86_64):
                platform = "x86_64"
            else:
                raise UnsupportedPlatformError(wheel_platform)

        elif wheel_platform.startswith("win"):
            # TODO: Switch to using `dll.gz`
            # https://github.com/python-cffi/cffi/issues/182
            os, ext = "windows", "dll.gz"
            prefix = ""
            suffix = ""
            if wheel_platform.endswith(aarch64):
                platform = "aarch64"
            elif wheel_platform.endswith(x86_64):
                platform = "x86_64"
            else:
                raise UnsupportedPlatformError(wheel_platform)

        else:
            raise UnsupportedPlatformError(wheel_platform)

        return PACT_LIB_URL.format(
            version=version,
            prefix=prefix,
            os=os,
            platform=platform,
            suffix=suffix,
            ext=ext,
        )

    def _extract_lib(self, artefact: Path) -> Path:
        """
        Extract the Pact library.

        Args:
            artefact:
                The URL to download the Pact binaries from.
        """
        target = PKG_DIR / (artefact.name.split("-")[0] + artefact.suffixes[-2])
        with (
            gzip.open(artefact, "rb") as f_in,
            target.open("wb") as f_out,
        ):
            shutil.copyfileobj(f_in, f_out)
        self.app.display_debug(f"Extracted Pact library to {target}")
        return target

    def _compile(self, lib: Path, header: Path) -> Path:
        """
        Build the CFFI bindings for the Pact library.

        Args:
            lib:
                The path to the Pact library binary.

            header:
                The path to the Pact library header file.
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
                "secur32",  # spellchecker:disable-line
                "shell32",
                "user32",
                "userenv",
                "ws2_32",
            ]
        else:
            extra_libs = []

        ffibuilder = cffi.FFI()
        ffibuilder.cdef(
            "\n".join(
                line
                for line in header.read_text().splitlines()
                if not line.strip().startswith("#")
            )
        )

        linker_args: list[str] = []
        if sys.platform == "darwin":
            # On macOS, we pad the headers so that install_name_tool can
            # subsequently adjust them.
            linker_args.append("-Wl,-headerpad_max_install_names")
        elif sys.platform == "linux":
            # On Linux, we set the RPATH
            linker_args.append(f"-Wl,-rpath,{lib.parent}")
        elif sys.platform == "win32":
            # Windows has no equivalent to RPATH, instead, the end-user must
            # ensure that the PATH environment variable is updated to include
            # the directory containing the Pact library.
            self.app.display_warning(
                "On Windows, ensure that the PATH environment variable includes "
                f"{lib.parent} to load the Pact library at runtime."
            )

        ffibuilder.set_source(
            "ffi",
            header.read_text(),
            libraries=["pact_ffi", *extra_libs],
            library_dirs=[str(lib.parent)],
            extra_link_args=linker_args,
        )
        extension = Path(ffibuilder.compile(verbose=True, tmpdir=str(self.tmpdir)))

        if sys.platform == "darwin":
            self.app.display_debug(f"Updating install names for {extension}")
            subprocess.check_call([  # noqa: S603, S607
                "install_name_tool",
                "-change",
                "libpact_ffi.dylib",
                str(lib),
                str(extension),
            ])

        self.app.display_debug(f"Compiled CFFI bindings to {extension}")
        return extension

    def _download(self, url: str) -> Path:
        """
        Download the target URL.

        This will download the target URL to the `src/pact_ffi/data` directory.
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
            self.app.display_debug(f"Downloading {url} to {artefact}")
            urllib.request.urlretrieve(url, artefact)  # noqa: S310
        else:
            self.app.display_debug(f"Using cached artefact {artefact}")

        return artefact

    def _infer_tag(self) -> str:
        """
        Infer the tag for the current build.

        The bindings are built to target ABI3, which is compatible with multiple
        Python versions. As a result, we generate `py{version}-abi3-{platform}`
        tags for the wheels.

        While the ABI3 interface was introduced in Python 3.2, we target the
        earliest supported version of Python in the Python wrapper.

        Return:
            The tag for the current build.
        """
        python_version = f"{sys.version_info.major}{sys.version_info.minor}"

        platform = self._sys_tag_platform()

        # On macOS, the version needs to be set based on the deployment target
        # (i.e., the version of the system libraries).
        if sys.platform == "darwin" and (
            deployment_target := os.getenv("MACOSX_DEPLOYMENT_TARGET")
        ):
            target = deployment_target.replace(".", "_")
            if platform.endswith("_arm64"):
                platform = f"macosx_{target}_arm64"
            elif platform.endswith("_x86_64"):
                platform = f"macosx_{target}_x86_64"
            else:
                raise UnsupportedPlatformError(platform)

        return f"cp{python_version}-abi3-{platform}"
