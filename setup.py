"""pact-python PyPI Package."""

import os
import platform
import shutil
import sys
import tarfile

from zipfile import ZipFile

from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
from distutils.command.sdist import sdist as sdist_orig


IS_64 = sys.maxsize > 2 ** 32
PACT_STANDALONE_VERSION = '1.88.51'
PACT_STANDALONE_SUFFIXES = ['osx.tar.gz',
                            'linux-x86_64.tar.gz',
                            'linux-x86.tar.gz',
                            'win32.zip']

here = os.path.abspath(os.path.dirname(__file__))

about = {}
with open(os.path.join(here, "pact", "__version__.py")) as f:
    exec(f.read(), about)

class sdist(sdist_orig):
    """
    Subclass sdist so that we can download all standalone ruby applications
    into ./pact/bin so our users receive all the binaries on pip install.
    """
    def run(self):
        package_bin_path = os.path.join(os.path.dirname(__file__), 'pact', 'bin')

        if os.path.exists(package_bin_path):
            shutil.rmtree(package_bin_path, ignore_errors=True)
        os.mkdir(package_bin_path)

        for suffix in PACT_STANDALONE_SUFFIXES:
            filename = ('pact-{version}-{suffix}').format(version=PACT_STANDALONE_VERSION, suffix=suffix)
            download_ruby_app_binary(package_bin_path, filename, suffix)
        super().run()


class PactPythonDevelopCommand(develop):
    """
    Custom develop mode installer for pact-python.

    When the package is installed using `python setup.py develop` or
    `pip install -e` it will download and unpack the appropriate Pact
    mock service and provider verifier.
    """

    def run(self):
        """Install ruby command."""
        develop.run(self)
        package_bin_path = os.path.join(os.path.dirname(__file__), 'pact', 'bin')
        if not os.path.exists(package_bin_path):
            os.mkdir(package_bin_path)

        install_ruby_app(package_bin_path, download_bin_path=None)


class PactPythonInstallCommand(install):
    """
    Custom installer for pact-python.

    Installs the Python package and unpacks the platform appropriate version
    of the Ruby mock service and provider verifier.

    User Options:
        --bin-path  An absolute folder path containing predownloaded pact binaries
                    that should be used instead of fetching from the internet.
    """

    user_options = install.user_options + [('bin-path=', None, None)]

    def initialize_options(self):
        """Load our preconfigured options"""
        install.initialize_options(self)
        self.bin_path = None

    def finalize_options(self):
        """Load provided CLI arguments into our options"""
        install.finalize_options(self)

    def run(self):
        """Install python binary."""
        install.run(self)
        package_bin_path = os.path.join(self.install_lib, 'pact', 'bin')
        if not os.path.exists(package_bin_path):
            os.mkdir(package_bin_path)
        install_ruby_app(package_bin_path, self.bin_path)


def install_ruby_app(package_bin_path, download_bin_path):
    """
    Installs the ruby standalone application for this OS.

    :param package_bin_path: The path where we want our pact binaries unarchived.
    :param download_bin_path: An optional path containing pre-downloaded pact binaries.
    """

    binary = ruby_app_binary()
    if download_bin_path is None:
        download_bin_path = package_bin_path

    path = os.path.join(download_bin_path, binary['filename'])

    if os.path.isfile(path) is True:
        extract_ruby_app_binary(download_bin_path, package_bin_path, binary['filename'])
    else:
        if download_bin_path is not None:
            if os.path.isfile(path) is not True:
                raise RuntimeError('Could not find {} binary.'.format(path))
            extract_ruby_app_binary(download_bin_path, package_bin_path, binary['filename'])
        else:
            download_ruby_app_binary(package_bin_path, binary['filename'], binary['suffix'])
            extract_ruby_app_binary(package_bin_path, package_bin_path, binary['filename'])

def ruby_app_binary():
    """
    Determines the ruby app binary required for this OS.

    :return A dictionary of type {'filename': string, 'version': string, 'suffix': string }
    """
    target_platform = platform.platform().lower()

    binary = ('pact-{version}-{suffix}')

    if 'darwin' in target_platform or 'macos' in target_platform:
        suffix = 'osx.tar.gz'
    elif 'linux' in target_platform and IS_64:
        suffix = 'linux-x86_64.tar.gz'
    elif 'linux' in target_platform:
        suffix = 'linux-x86.tar.gz'
    elif 'windows' in target_platform:
        suffix = 'win32.zip'
    else:
        msg = ('Unfortunately, {} is not a supported platform. Only Linux,'
               ' Windows, and OSX are currently supported.').format(
            platform.platform())
        raise Exception(msg)

    binary = binary.format(version=PACT_STANDALONE_VERSION, suffix=suffix)
    return {'filename': binary, 'version': PACT_STANDALONE_VERSION, 'suffix': suffix}

def download_ruby_app_binary(path_to_download_to, filename, suffix):
    """
    Downloads `binary` into `path_to_download_to`.

    :param path_to_download_to: The path where binaries should be downloaded.
    :param filename: The filename that should be installed.
    :param suffix: The suffix of the standalone app to install.
    """
    uri = ('https://github.com/pact-foundation/pact-ruby-standalone/releases'
           '/download/v{version}/pact-{version}-{suffix}')

    if sys.version_info.major == 2:
        from urllib import urlopen
    else:
        from urllib.request import urlopen

    path = os.path.join(path_to_download_to, filename)
    resp = urlopen(uri.format(version=PACT_STANDALONE_VERSION, suffix=suffix))
    with open(path, 'wb') as f:
        if resp.code == 200:
            f.write(resp.read())
        else:
            raise RuntimeError(
                'Received HTTP {} when downloading {}'.format(
                    resp.code, resp.url))

def extract_ruby_app_binary(source, destination, binary):
    """
    Extracts the ruby app binary from `source` into `destination`.

    :param source: The location of the binary to unarchive.
    :param destination: The location to unarchive to.
    :param binary: The binary that needs to be unarchived.
    """
    path = os.path.join(source, binary)
    if 'windows' in platform.platform().lower():
        with ZipFile(path) as f:
            f.extractall(destination)
    else:
        with tarfile.open(path) as f:
            f.extractall(destination)


def read(filename):
    """Read file contents."""
    path = os.path.realpath(os.path.join(os.path.dirname(__file__), filename))
    with open(path, 'rb') as f:
        return f.read().decode('utf-8')


dependencies = [
    'click>=2.0.0',
    'psutil>=2.0.0',
    'requests>=2.5.0',
    'six>=1.9.0',
    'fastapi>=0.67.0',
    'urllib3>=1.26.5',
    'uvicorn>=0.14.0'
]

if __name__ == '__main__':
    setup(
        cmdclass={
            'develop': PactPythonDevelopCommand,
            'install': PactPythonInstallCommand,
            'sdist': sdist},
        name='pact-python',
        version=about['__version__'],
        description=(
            'Tools for creating and verifying consumer driven '
            'contracts using the Pact framework.'),
        long_description=read('README.md'),
        long_description_content_type='text/markdown',
        author='Matthew Balvanz',
        author_email='matthew.balvanz@workiva.com',
        url='https://github.com/pact-foundation/pact-python',
        entry_points='''
            [console_scripts]
            pact-verifier=pact.cli.verify:main
        ''',
        install_requires=dependencies,
        packages=['pact', 'pact.cli'],
        package_data={'pact': ['bin/*']},
        package_dir={'pact': 'pact'},
        license='MIT License')
