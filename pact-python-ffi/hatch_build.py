"""
Hatchling build hook.

This hook is responsible for downloading the Pact FFI library and building the
CFFI bindings for it.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import sysconfig
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING, Any

import cffi
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from packaging.tags import sys_tags

if TYPE_CHECKING:
    from collections.abc import Mapping, MutableMapping, Sequence

PKG_DIR = Path(__file__).parent.resolve() / "src" / "pact_ffi"
PACT_RELEASE_URL = "https://github.com/pact-foundation/pact-reference/releases/download/pact_ffi-v{version}"


def _stable_abi() -> str:
    """
    Determine the stable ABI targeted by the current interpreter.

    CFFI compiles against `abi3t` on free-threaded CPython 3.15+ and against
    `abi3` otherwise. Free-threaded interpreters do not load `abi3` extensions.

    Returns:
        Either `abi3` or `abi3t`.
    """
    if sysconfig.get_config_var("Py_GIL_DISABLED"):
        return "abi3t"
    return "abi3"


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

    def clean(self, versions: Sequence[str]) -> None:  # noqa: ARG002
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
        build_data: MutableMapping[str, object],
    ) -> None:
        """
        Code called immediately before each build.

        Args:
            version:
                Not used (but required by the parent class).

            build_data:
                A mutable mapping to modify in-place used by Hatch when creating
                the final wheel.

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
            raise

        self.app.display_debug(f"Wheel artefacts: {build_data['force_include']}")
        build_data["tag"] = self._infer_tag()

    def _sys_tag_platform(self) -> str:
        """
        Get the platform tag from the current system tags.

        This is used to determine the target platform for the Pact library.

        On Linux, the generic `linux_{arch}` tag conveys no information about
        the platform's C library, so the more specific `manylinux`/`musllinux`
        tag is preferred when one is available.

        Returns:
            The most specific platform tag supported by the current system.
        """
        platforms = (t.platform for t in sys_tags())
        preferred = next(platforms)
        if preferred.startswith("linux_"):
            return next(
                (p for p in platforms if not p.startswith("linux_")),
                preferred,
            )
        return preferred

    def _install(self, version: str) -> Mapping[str, str]:
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
        release_url = PACT_RELEASE_URL.format(version=version)
        target = self._target()
        header = self._download(f"{release_url}/pact.h")
        if "windows" in target:
            archive_url = f"{release_url}/pact_ffi-{target}.zip"
        else:
            archive_url = f"{release_url}/pact_ffi-{target}.tar.xz"
        archive = self._download(archive_url)
        self._verify(archive, self._download(f"{archive_url}.sha256"))

        dll_lib: Path | None = None
        if "windows" in target:
            lib = self._extract_lib(archive, "pact_ffi.dll", "pact_ffi.dll")
            # MSVC resolves `pact_ffi` to `pact_ffi.lib`. The archive's own
            # `pact_ffi.lib` is the static library, so the import library
            # takes its name.
            dll_lib = self._extract_lib(archive, "pact_ffi.dll.lib", "pact_ffi.lib")
        elif "darwin" in target:
            lib = self._extract_lib(archive, "libpact_ffi.dylib", "libpact_ffi.dylib")
        elif "musl" in target:
            # MUSL uses static library
            lib = self._extract_lib(archive, "libpact_ffi.a", "libpact_ffi.a")
        else:
            lib = self._extract_lib(archive, "libpact_ffi.so", "libpact_ffi.so")

        # Compile the FFI extension
        extension = self._compile(lib, header)

        # Copy into the package directory, using the stable ABI marking for
        # broad compatibility.
        # NOTE: Windows does _not_ use the version infixation
        name = extension.name.split(".")[0]
        suffix = extension.suffix
        infix = f".{_stable_abi()}" if os.name != "nt" else ""
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

    def _target(self) -> str:
        """
        Determine the Rust target triple matching the wheel platform.

        Returns:
            The Rust target triple of the upstream Pact library archive.

        Raises:
            UnsupportedPlatformError:
                If the current platform is not supported.
        """
        wheel_platform = self._sys_tag_platform()

        if wheel_platform.endswith(("_arm64", "_aarch64")):
            arch = "aarch64"
        elif wheel_platform.endswith(("_x86_64", "_amd64")):
            arch = "x86_64"
        else:
            raise UnsupportedPlatformError(wheel_platform)

        if wheel_platform.startswith("macosx"):
            return f"{arch}-apple-darwin"
        if wheel_platform.startswith("musllinux"):
            return f"{arch}-unknown-linux-musl"
        if wheel_platform.startswith("manylinux"):
            return f"{arch}-unknown-linux-gnu"
        if wheel_platform.startswith("win"):
            return f"{arch}-pc-windows-msvc"
        raise UnsupportedPlatformError(wheel_platform)

    def _verify(self, artefact: Path, checksum: Path) -> None:
        """
        Verify an artefact against its SHA-256 checksum file.

        A mismatched artefact is removed so that the next build downloads it
        again.

        Args:
            artefact:
                The path to the downloaded artefact.

            checksum:
                The path to the checksum file, in the `sha256sum` format
                `<hex> *<filename>`.

        Raises:
            ValueError:
                If the checksum does not match.
        """
        expected = checksum.read_text().split()[0].lower()
        digest = hashlib.sha256()
        with artefact.open("rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                digest.update(chunk)
        if digest.hexdigest() != expected:
            artefact.unlink()
            checksum.unlink()
            msg = (
                f"Checksum mismatch for {artefact.name}: "
                f"expected {expected}, got {digest.hexdigest()}"
            )
            self.app.display_error(msg)
            raise ValueError(msg)
        self.app.display_debug(f"Verified checksum of {artefact.name}")

    def _extract_lib(self, archive: Path, member: str, name: str) -> Path:
        """
        Extract a file from the Pact library archive.

        The `.tar.xz` archives nest their files under a `pact_ffi-<target>`
        directory, while the `.zip` archives keep them at the root.

        Args:
            archive:
                The path to the downloaded archive.

            member:
                The file name within the archive.

            name:
                The file name to extract to within the package directory.

        Returns:
            The path to the extracted file.
        """
        target = PKG_DIR / name
        if archive.suffix == ".zip":
            with (
                zipfile.ZipFile(archive) as zf,
                zf.open(member) as f_in,
                target.open("wb") as f_out,
            ):
                shutil.copyfileobj(f_in, f_out)
        else:
            prefix = archive.name.removesuffix(".tar.xz")
            with tarfile.open(archive, "r:xz") as tf:
                f_tar = tf.extractfile(f"{prefix}/{member}")
                if f_tar is None:
                    msg = f"{member} in {archive.name} is not a regular file"
                    raise ValueError(msg)
                with f_tar, target.open("wb") as f_out:
                    shutil.copyfileobj(f_tar, f_out)
        self.app.display_debug(f"Extracted {member} from {archive.name} to {target}")
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

        source = self._patch_header(header.read_text())

        ffibuilder = cffi.FFI()
        ffibuilder.cdef(
            "\n".join(
                line for line in source.splitlines() if not line.strip().startswith("#")
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
            source,
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

    def _patch_header(self, source: str) -> str:
        """
        Patch the upstream header so that CFFI can compile it.

        The upstream `pact.h` emits the callback parameter of
        `pactffi_register_log_callback` as an opaque struct passed by value,
        which cannot be compiled. The Rust signature is
        `Option<extern "C" fn(...)>`, whose ABI is a nullable function pointer.
        See https://github.com/pact-foundation/pact-reference/issues/544.

        Args:
            source:
                The contents of the upstream `pact.h`.

        Returns:
            The header contents with the callback declared as a function
            pointer.
        """
        opaque = "typedef struct Option_LogCallback Option_LogCallback;"
        if opaque not in source:
            return source
        self.app.display_debug("Patching Option_LogCallback in pact.h")
        return source.replace(
            opaque,
            "typedef void (*LogCallback)("
            "const char *log_id, "
            "const char *test_run_id, "
            "const char *level, "
            "const char *target, "
            "const char *message);",
        ).replace(
            "void pactffi_register_log_callback(struct Option_LogCallback callback);",
            "void pactffi_register_log_callback(LogCallback callback);",
        )

    def _download(self, url: str) -> Path:
        """
        Download the target URL.

        This will download the target URL to the `src/pact_ffi/data` directory.
        If the download artefact is already present, the existing artefact's
        path will be returned without downloading it again.

        Args:
            url:
                The URL to download

        Returns:
            The path to the downloaded artefact.
        """
        filename = url.rsplit("/", maxsplit=1)[-1]
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

        The bindings are built to target the stable ABI, which is compatible
        with multiple Python versions. As a result, we generate
        `cp{version}-abi3-{platform}` tags for the wheels.

        While the ABI3 interface was introduced in Python 3.2, we target the
        earliest supported version of Python in the Python wrapper.

        A free-threaded build targets `abi3t`, which requires Python 3.15. Its
        wheel takes the `cp{version}-abi3.abi3t-{platform}` tag, as the
        extension also loads on GIL-enabled builds.

        Returns:
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

        abi = "abi3.abi3t" if _stable_abi() == "abi3t" else "abi3"
        return f"cp{python_version}-{abi}-{platform}"
