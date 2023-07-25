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
PACT_STANDALONE_VERSION = '2.0.3'
PACT_STANDALONE_SUFFIXES = ['osx-x86_64.tar.gz',
                            'osx-arm64.tar.gz',
                            'linux-x86_64.tar.gz',
                            'linux-arm64.tar.gz',
                            'windows-x86_64.zip',
                            'windows-x86.zip',
                            ]

here = os.path.abspath(os.path.dirname(__file__))

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
        """Load our preconfigured options."""
        install.initialize_options(self)
        self.bin_path = None

    def finalize_options(self):
        """Load provided CLI arguments into our options."""
        install.finalize_options(self)

    def run(self):
        """Install python binary."""
        install.run(self)
        package_bin_path = os.path.join(self.install_lib, 'pact', 'bin')
        if not os.path.exists(package_bin_path):
            os.mkdir(package_bin_path)
        install_ruby_app(package_bin_path, self.bin_path)


def install_ruby_app(package_bin_path: str, download_bin_path=None):
    """
    Installs the ruby standalone application for this OS.

    :param package_bin_path: The path where we want our pact binaries unarchived.
    :param download_bin_path: An optional path containing pre-downloaded pact binaries.
    """
    binary = ruby_app_binary()

    # The compressed Pact .tar.gz, zip etc file is expected to be in download_bin_path (if provided).
    # Otherwise we will look in package_bin_path.
    source_dir = download_bin_path if download_bin_path else package_bin_path
    pact_unextracted_path = os.path.join(source_dir, binary['filename'])

    if os.path.isfile(pact_unextracted_path):
        # Already downloaded, so just need to extract
        extract_ruby_app_binary(source_dir, package_bin_path, binary['filename'])
    else:
        if download_bin_path:
            # An alternative source was provided, but did not contain the .tar.gz
            raise RuntimeError('Could not find {} binary.'.format(pact_unextracted_path))
        else:
            # Clean start, download an extract
            download_ruby_app_binary(package_bin_path, binary['filename'], binary['suffix'])
            extract_ruby_app_binary(package_bin_path, package_bin_path, binary['filename'])


def ruby_app_binary():
    """
    Determine the ruby app binary required for this OS.

    :return A dictionary of type {'filename': string, 'version': string, 'suffix': string }
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
        msg = ('Unfortunately, {} is not a supported platform. Only Linux,'
               ' Windows, and OSX are currently supported.').format(
            platform.platform())
        raise Exception(msg)

    binary = binary.format(version=PACT_STANDALONE_VERSION, suffix=suffix)
    return {'filename': binary, 'version': PACT_STANDALONE_VERSION, 'suffix': suffix}

def download_ruby_app_binary(path_to_download_to, filename, suffix):
    """
    Download `binary` into `path_to_download_to`.

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
    Extract the ruby app binary from `source` into `destination`.

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
            def is_within_directory(directory, target):

                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)

                prefix = os.path.commonprefix([abs_directory, abs_target])

                return prefix == abs_directory

            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):

                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")

                tar.extractall(path, members, numeric_owner=numeric_owner)

            safe_extract(f, destination)


def read(filename):
    """Read file contents."""
    path = os.path.realpath(os.path.join(os.path.dirname(__file__), filename))
    with open(path, 'rb') as f:
        return f.read().decode('utf-8')


dependencies = [
    'psutil>=5.9.4',
    'six>=1.16.0',
    'fastapi>=0.67.0',
    'urllib3>=1.26.12',
]

if sys.version_info < (3, 7):
    dependencies += [
        'click<=8.0.4',
        'httpx==0.22.0',
        'requests==2.27.1',
        'uvicorn==0.16.0',
    ]
else:
    dependencies += [
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
        classifiers=CLASSIFIERS,
        python_requires='>=3.6,<4',
        install_requires=dependencies,
        packages=['pact', 'pact.cli'],
        package_data={'pact': ['bin/*']},
        package_dir={'pact': 'pact'},
        license='MIT License')
