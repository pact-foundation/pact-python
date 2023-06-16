"""pact-python PyPI Package."""

import gzip
import os
import platform
import shutil
import sys
import tarfile
from distutils.command.sdist import sdist as sdist_orig
from typing import NamedTuple
from zipfile import ZipFile

from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install

IS_64 = sys.maxsize > 2 ** 32
PACT_STANDALONE_VERSION = '2.0.1'
PACT_STANDALONE_SUFFIXES = [
    'osx-x86_64.tar.gz',
    'osx-arm64.tar.gz',
    'linux-x86_64.tar.gz',
    'linux-arm64.tar.gz',
    'windows-x86_64.zip',
    'windows-x86.zip',
]
PACT_FFI_VERSION = "0.4.5"
PACT_FFI_FILENAMES = [
    "libpact_ffi-linux-aarch64.so.gz",
    "libpact_ffi-linux-x86_64.so.gz",
    "libpact_ffi-osx-aarch64-apple-darwin.dylib.gz",
    "libpact_ffi-osx-x86_64.dylib.gz",
    "pact_ffi-windows-x86_64.dll.gz",
]
PACT_RUBY_FILENAME = "pact-{version}-{suffix}"

here = os.path.abspath(os.path.dirname(__file__))


class Binary(NamedTuple):
    filename: str  # For example: "pact-1.2.3-linux-x86_64.tar.gz"
    version: str  # For example: "1.2.3"
    suffix: str  # For example: "linux-x86_64.tar.gz"
    single_file: bool  # True for Pact Rust FFI where we have one library file


about = {}
with open(os.path.join(here, "pact", "__version__.py")) as f:
    exec(f.read(), about)


class sdist(sdist_orig):
    """Subclass sdist to download all standalone ruby applications into ./pact/bin."""

    def run(self):
        """Installs the dist."""
        package_bin_path = os.path.join(os.path.dirname(__file__), 'pact', 'bin')

        if os.path.exists(package_bin_path):
            shutil.rmtree(package_bin_path, ignore_errors=True)
        os.mkdir(package_bin_path)

        # Ruby binary
        for suffix in PACT_STANDALONE_SUFFIXES:
            filename = PACT_RUBY_FILENAME.format(version=PACT_STANDALONE_VERSION, suffix=suffix)
            download_binary(package_bin_path, filename, get_ruby_uri(suffix=suffix))

        # Rust FFI library
        for filename in PACT_FFI_FILENAMES:
            download_binary(package_bin_path, filename, get_rust_uri(filename=filename))
            download_binary(package_bin_path, 'pact.h', get_rust_uri(filename='pact.h'))
        super().run()


class PactPythonDevelopCommand(develop):
    """Custom develop mode installer for pact-python.

    When the package is installed using `python setup.py develop` or
    `pip install -e` it will download and unpack the appropriate Pact
    mock service and provider verifier.
    """

    def run(self):
        """Install ruby command."""
        develop.run(self)
        package_bin_path = os.path.join(os.path.dirname(__file__), "pact", "bin")
        if not os.path.exists(package_bin_path):
            os.mkdir(package_bin_path)

        # Ruby
        install_binary(package_bin_path, download_bin_path=None, binary=ruby_app_binary())

        # Rust
        install_binary(package_bin_path, download_bin_path=None, binary=rust_lib_binary())


class PactPythonInstallCommand(install):
    """Custom installer for pact-python.

    Installs the Python package and unpacks the platform appropriate version
    of the Ruby mock service and provider verifier.

    User Options:
        --bin-path  An absolute folder path containing pre-downloaded pact binaries
                    that should be used instead of fetching from the internet.
    """

    user_options = install.user_options + [("bin-path=", None, None)]

    def initialize_options(self):
        """Load our preconfigured options."""
        install.initialize_options(self)
        self.bin_path = None

    def finalize_options(self):
        """Load provided CLI arguments into our options."""
        install.finalize_options(self)

    def run(self):
        """Install python binary."""
        install.run(self)
        package_bin_path = os.path.join(self.install_lib, "pact", "bin")
        if not os.path.exists(package_bin_path):
            os.mkdir(package_bin_path)

        # Ruby
        install_binary(package_bin_path, self.bin_path, binary=ruby_app_binary())

        # Rust
        install_binary(package_bin_path, download_bin_path=None, binary=rust_lib_binary())


def get_ruby_uri(suffix) -> str:
    """Determine the full URI to download the Ruby binary from."""
    uri = (
        "https://github.com/pact-foundation/pact-ruby-standalone/releases"
        "/download/v{version}/pact-{version}-{suffix}"
    )
    return uri.format(version=PACT_STANDALONE_VERSION, suffix=suffix)


def get_rust_uri(filename) -> str:
    """Determine the full URI to download the Rust binary from."""
    uri = (
        "https://github.com/pact-foundation/pact-reference/releases"
        "/download/libpact_ffi-v{version}/{filename}"
    )
    return uri.format(version=PACT_FFI_VERSION, filename=filename)


def install_binary(package_bin_path, download_bin_path, binary: Binary):
    """Installs the ruby standalone application for this OS.

    :param package_bin_path: The path where we want our pact binaries unarchived.
    :param download_bin_path: An optional path containing pre-downloaded pact binaries.
    :param binary: Details of the zipped binary files required
    """
    print("-> install_binary({package_bin_path}, {download_bin_path}, {binary})".format(
        package_bin_path=package_bin_path,
        download_bin_path=download_bin_path,
        binary=binary
    ))

    if download_bin_path is not None:
        # If a download_bin_path has been provided, but does not contain what we
        # expect, do not continue
        path = os.path.join(download_bin_path, binary.filename)
        if not os.path.isfile(path):
            raise RuntimeError("Could not find {} binary.".format(path))
        else:
            if binary.single_file:
                extract_gz(download_bin_path, package_bin_path, binary.filename)
            else:
                extract_ruby_app_binary(download_bin_path, package_bin_path, binary.filename)
    else:
        # Otherwise, download to the destination package_bin_path, skipping to
        # just extract if we have it already
        path = os.path.join(package_bin_path, binary.filename)
        if not os.path.isfile(path):
            # Ruby binary
            if binary.suffix in PACT_STANDALONE_SUFFIXES:
                download_binary(package_bin_path, binary.filename, uri=get_ruby_uri(binary.suffix))

            # Rust FFI library
            if binary.filename in PACT_FFI_FILENAMES:
                print(binary.filename)
                download_binary(package_bin_path, binary.filename, get_rust_uri(filename=binary.filename))
                download_binary(package_bin_path, 'pact.h', get_rust_uri(filename='pact.h'))

        if binary.single_file:
            extract_gz(package_bin_path, package_bin_path, binary.filename)
        else:
            extract_ruby_app_binary(package_bin_path, package_bin_path, binary.filename)

    print("<- install_binary")


def ruby_app_binary() -> Binary:
    """Determines the ruby app binary required for this OS.

    :return Details of the binary file required
    """
    target_platform = platform.platform().lower()

    binary = ('pact-{version}-{suffix}')
    if ("darwin" in target_platform or "macos" in target_platform) and ("aarch64" in platform.machine() or "arm64" in platform.machine()):
        suffix = 'osx-arm64.tar.gz'
    elif ("darwin" in target_platform or "macos" in target_platform) and IS_64:
        suffix = 'osx-x86_64.tar.gz'
    elif 'linux' in target_platform and IS_64 and "aarch64" in platform.machine():
        suffix = 'linux-arm64.tar.gz'
    elif 'linux' in target_platform:
        suffix = 'linux-x86_64.tar.gz'
    elif 'windows' in target_platform and IS_64:
        suffix = 'windows-x86_64.zip'
    elif 'windows' in target_platform:
        suffix = 'windows-x86.zip'
    else:
        msg = (
            "Unfortunately, {} is not a supported platform. Only Linux," " Windows, and OSX are currently supported."
        ).format(platform.platform())
        raise Exception(msg)

    binary = PACT_RUBY_FILENAME.format(version=PACT_STANDALONE_VERSION, suffix=suffix)
    return Binary(filename=binary, version=PACT_STANDALONE_VERSION, suffix=suffix, single_file=False)


def rust_lib_binary() -> Binary:
    """Determines the Rust FFI library binary required for this OS.

    :return Details of the binary file required
    """
    target_platform = platform.platform().lower()
    print(target_platform)
    print(platform.machine())

    if ("darwin" in target_platform or "macos" in target_platform) and ("aarch64" in platform.machine() or "arm64" in platform.machine()):
        binary = "libpact_ffi-osx-aarch64-apple-darwin.dylib.gz"
    elif "darwin" in target_platform or "macos" in target_platform:
        binary = "libpact_ffi-osx-x86_64.dylib.gz"
    elif "linux" in target_platform and IS_64 and ("aarch64" in platform.machine() or "arm64" in platform.machine()):
        binary = "libpact_ffi-linux-aarch64.so.gz"
    elif "linux" in target_platform and IS_64:
        binary = "libpact_ffi-linux-x86_64.so.gz"
    elif "windows" in target_platform:
        binary = "pact_ffi-windows-x86_64.dll.gz"
    else:
        msg = (
            "Unfortunately, {} is not a supported platform. Only Linux x86_64,"
            " Windows, and OSX are currently supported."
        ).format(target_platform)
        raise Exception(msg)

    return Binary(filename=binary, version=PACT_STANDALONE_VERSION, suffix=None, single_file=True)


def download_binary(path_to_download_to, filename, uri):
    """Downloads `filename` into `path_to_download_to`.

    :param path_to_download_to: The path where binaries should be downloaded.
    :param filename: The filename that should be installed.
    :param uri: The URI to download the file from.
    """
    print("-> download_binary({path_to_download_to}, {filename}, {uri})".format(path_to_download_to=path_to_download_to, filename=filename, uri=uri))

    if sys.version_info.major == 2:
        from urllib import urlopen
    else:
        from urllib.request import urlopen

    path = os.path.join(path_to_download_to, filename)

    resp = urlopen(uri)
    with open(path, "wb") as f:
        if resp.code == 200:
            f.write(resp.read())
        else:
            raise RuntimeError("Received HTTP {} when downloading {}".format(resp.code, resp.url))

    print("<- download_binary")


def extract_ruby_app_binary(source: str, destination: str, binary: str):
    """Extracts the ruby app binary from `source` into `destination`.

    :param source: The location of the binary to unarchive.
    :param destination: The location to unarchive to.
    :param binary: The binary that needs to be unarchived.
    """
    print("-> extract_ruby_app_binary({source}, {destination}, {binary})".format(source=source, destination=destination, binary=binary))

    path = os.path.join(source, binary)
    if "windows" in platform.platform().lower():
        with ZipFile(path) as f:
            f.extractall(destination)
    else:
        with tarfile.open(path) as f:
            f.extractall(destination)
    os.remove(path)
    print("<- extract_ruby_app_binary")


def extract_gz(source: str, destination: str, binary: str):
    print("-> extract_gz({source}, {destination}, {binary})".format(source=source, destination=destination, binary=binary))

    path = os.path.join(source, binary)
    dest = os.path.splitext(os.path.join(destination, binary))[0]

    with gzip.open(path, "rb") as f_in, open(dest, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    os.remove(path)

    print("<- extract_gz")


def read(filename):
    """Read file contents."""
    path = os.path.realpath(os.path.join(os.path.dirname(__file__), filename))
    with open(path, "rb") as f:
        return f.read().decode("utf-8")


dependencies = [
    'cffi==1.15.1',
    'psutil>=5.9.4',
    'six>=1.16.0',
    'fastapi>=0.67.0',
    'urllib3>=1.26.12',
]

if sys.version_info.major < 4 and sys.version_info.minor < 7:
    dependencies += [
        'cffi==1.15.1',
        'click<=8.0.4',
        'httpx==0.22.0',
        'requests==2.27.1',
        'uvicorn==0.16.0',
    ]
else:
    dependencies += [
        'cffi==1.15.1',
        'click>=8.1.3',
        'httpx==0.23.3',
        'requests>=2.28.0',
        'uvicorn>=0.19.0',
    ]

# Classifiers: available ones listed at https://pypi.org/classifiers
CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',

    'Operating System :: OS Independent',

    'Intended Audience :: Developers',

    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',

    'License :: OSI Approved :: MIT License',
]

if __name__ == "__main__":
    setup(
        cmdclass={"develop": PactPythonDevelopCommand, "install": PactPythonInstallCommand, "sdist": sdist},
        name="pact-python",
        version=about["__version__"],
        description=("Tools for creating and verifying consumer driven " "contracts using the Pact framework."),
        long_description=read("README.md"),
        long_description_content_type="text/markdown",
        author="Matthew Balvanz",
        author_email="matthew.balvanz@workiva.com",
        url="https://github.com/pact-foundation/pact-python",
        entry_points="""
            [console_scripts]
            pact-verifier=pact.cli.verify:main
            pact-verifier-ffi=pact.ffi.cli.verify:main
        """,
        classifiers=CLASSIFIERS,
        python_requires='>=3.6,<4',
        install_requires=dependencies,
        packages=["pact", "pact.cli"],
        package_data={"pact": ["bin/*"]},
        package_dir={"pact": "pact"},
        license="MIT License",
    )
