"""pact-python PyPI Package."""

import os
from setuptools import find_packages, setup


def get_version():
    """Return latest version noted in CHANGES.txt."""
    lastline = [line for line in read('CHANGES.txt').split('\n') if line][-1]
    version = lastline.split(',')[0]
    return version[1:]


def read(filename):
    """Read file contents."""
    path = os.path.realpath(os.path.join(os.path.dirname(__file__), filename))
    with open(path, 'rb') as f:
        return f.read().decode('utf-8')


dependencies = [
    dep.strip() for dep in read('requirements.txt').split('\n') if dep.strip()]
setup_args = dict(
    name='pact-python',
    version=get_version(),
    description=('Tools for creating and verifying consumer driven contracts'
                 ' using the Pact framework.'),
    long_description=read('README.md'),
    author='Matthew Balvanz',
    author_email='matthew.balvanz@workiva.com',
    url='https://github.com/pact-foundation/pact-python',
    install_requires=dependencies,
    packages=find_packages(exclude=['*.test', '*.test.*', 'test.*', 'test']),
    license=read('LICENSE'))


if __name__ == '__main__':
    setup(**setup_args)
