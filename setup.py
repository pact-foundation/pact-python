"""pact-python PyPI Package."""

import os
import platform
import sys
import tarfile

from setuptools import setup
from setuptools.command.install import install

import pact


class PactPythonInstallCommand(install):
    """
    Custom installer for pact-python.

    Installs the Python package and unpacks the platform appropriate version
    of Python mock service.
    """
    def run(self):
        install.run(self)
        bin_path = os.path.join(self.install_lib, 'pact', 'bin')
        self.mock_service(bin_path)
        self.verifier(bin_path)

    def mock_service(self, bin_path):
        """Install the Ruby mock service for this platform."""
        is_64 = sys.maxsize > 2 ** 32
        target_platform = platform.platform().lower()
        if 'darwin' in target_platform:
            platform_tar = 'pact-mock-service-darwin.tar.gz'
        elif 'linux' in target_platform and is_64:
            platform_tar = 'pact-mock-service-linux-x64.tar.gz'
        elif 'linux' in target_platform:
            platform_tar = 'pact-mock-service-ia32.tar.gz'
        elif 'windows' in target_platform:
            platform_tar = 'pact-mock-service-win32.tar.gz'
        else:
            msg = ('Unfortunately, {} is not a supported platform. Only Linux,'
                   ' Windows, and OSX are currently supported.').format(
                platform.platform())
            raise Exception(msg)

        self.announce(u'Extracting {} to {}'.format(platform_tar, bin_path))
        with tarfile.open(os.path.join(bin_path, platform_tar)) as f:
            f.extractall(os.path.join(bin_path, 'mock-service'))

    def verifier(self, bin_path):
        """Install the Ruby Pact Verifier for this platform."""
        is_64 = sys.maxsize > 2 ** 32
        target_platform = platform.platform().lower()
        if 'darwin' in target_platform:
            platform_tar = 'pact-provider-verifier-darwin.tar.gz'
        elif 'linux' in target_platform and is_64:
            platform_tar = 'pact-provider-verifier-linux-x64.tar.gz'
        elif 'linux' in target_platform:
            platform_tar = 'pact-provider-verifier-linux-ia32.tar.gz'
        elif 'windows' in target_platform:
            platform_tar = 'pact-provider-verifier-win32.tar.gz'
        else:
            msg = ('Unfortunately, {} is not a supported platform. Only Linux,'
                   ' Windows, and OSX are currently supported.').format(
                platform.platform())
            raise Exception(msg)

        self.announce(u'Extracting {} to {}'.format(platform_tar, bin_path))
        with tarfile.open(os.path.join(bin_path, platform_tar)) as f:
            f.extractall(os.path.join(bin_path, 'verifier'))


def read(filename):
    """Read file contents."""
    path = os.path.realpath(os.path.join(os.path.dirname(__file__), filename))
    with open(path, 'rb') as f:
        return f.read().decode('utf-8')


dependencies = read('requirements.txt').split()

if sys.version_info.major == 2:
    dependencies.append('subprocess32')

setup_args = dict(
    cmdclass={'install': PactPythonInstallCommand},
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
