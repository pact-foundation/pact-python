"""pact-python PyPI Package."""

import os
import platform
import sys
import tarfile

from zipfile import ZipFile

from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install

import pact


IS_64 = sys.maxsize > 2 ** 32
PACT_STANDALONE_VERSION = '1.0.0'


class PactPythonDevelopCommand(develop):
    """
    Custom develop mode installer for pact-python.

    When the package is installed using `python setup.py develop` or
    `pip install -e` it will download and unpack the appropriate Pact
    mock service and provider verifier.
    """
    def run(self):
        develop.run(self)
        bin_path = os.path.join(os.path.dirname(__file__), 'pact', 'bin')
        if not os.path.exists(bin_path):
            os.mkdir(bin_path)

        install_ruby_app(bin_path)


class PactPythonInstallCommand(install):
    """
    Custom installer for pact-python.

    Installs the Python package and unpacks the platform appropriate version
    of the Ruby mock service and provider verifier.
    """
    def run(self):
        install.run(self)
        bin_path = os.path.join(self.install_lib, 'pact', 'bin')
        os.mkdir(bin_path)
        install_ruby_app(bin_path)


def install_ruby_app(bin_path):
    """
    Download a Ruby application and install it for use.

    :param bin_path: The path where binaries should be installed.
    """
    target_platform = platform.platform().lower()
    uri = ('https://github.com/pact-foundation/pact-ruby-standalone/releases'
           '/download/v{version}/pact-{version}-{suffix}')

    if 'darwin' in target_platform:
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

    if sys.version_info.major == 2:
        from urllib import urlopen
    else:
        from urllib.request import urlopen

    path = os.path.join(bin_path, suffix)
    resp = urlopen(uri.format(version=PACT_STANDALONE_VERSION, suffix=suffix))
    with open(path, 'wb') as f:
        f.write(resp.read())

    if 'windows' in platform.platform().lower():
        with ZipFile(path) as f:
            f.extractall(bin_path)
    else:
        with tarfile.open(path) as f:
            f.extractall(bin_path)


def read(filename):
    """Read file contents."""
    path = os.path.realpath(os.path.join(os.path.dirname(__file__), filename))
    with open(path, 'rb') as f:
        return f.read().decode('utf-8')


dependencies = read('requirements.txt').split()

if sys.version_info.major == 2:
    dependencies.append('subprocess32')

setup_args = dict(
    cmdclass={'develop': PactPythonDevelopCommand,
              'install': PactPythonInstallCommand},
    name='pact-python',
    version=pact.__version__,
    description=('Tools for creating and verifying consumer driven contracts'
                 ' using the Pact framework.'),
    long_description=read('README.md'),
    author='Matthew Balvanz',
    author_email='matthew.balvanz@workiva.com',
    url='https://github.com/pact-foundation/pact-python',
    entry_points='''
        [console_scripts]
        pact-verifier=pact.verify:main
    ''',
    install_requires=dependencies,
    packages=['pact'],
    package_data={'pact': ['bin/*']},
    package_dir={'pact': 'pact'},
    license=read('LICENSE'))


if __name__ == '__main__':
    setup(**setup_args)
