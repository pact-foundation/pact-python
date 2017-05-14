#!/usr/bin/env bash

set -e


build() {
    echo "Building..."
    pushd $(pwd)
    mkdir -p build
    cd build
    if [ ! -d "${PROJECT_NAME}-${GEM_VERSION}" ]; then
      wget https://github.com/${REPOSITORY}/archive/v${GEM_VERSION}.zip -O temp.zip
      unzip temp.zip
      rm temp.zip
    fi

    cd ${PROJECT_NAME}-${GEM_VERSION}

    bundle
    bundle exec rake package
    popd
}


package() {
    echo "Packaging $STANDALONE_PACKAGE_NAME.$EXTENSION for pypi as $PYPI_PACKAGE_NAME.$EXTENSION"
    pushd $(pwd)
    mkdir -p pact/bin

    cd build
    cp ${PROJECT_NAME}-${GEM_VERSION}/pkg/${PROJECT_NAME//_/-}-* .
    rm -rf $STANDALONE_PACKAGE_NAME

    if [ $EXTENSION = "zip" ]; then
      unzip $STANDALONE_PACKAGE_NAME.$EXTENSION
    else
      tar -xzf $STANDALONE_PACKAGE_NAME.$EXTENSION
    fi

    mv $STANDALONE_PACKAGE_NAME $PYPI_PACKAGE_NAME
    cd $PYPI_PACKAGE_NAME

    tar -czf ../../pact/bin/${PYPI_PACKAGE_NAME}.tar.gz *
    popd
}


echo "Packaging the Mock Service for distribution."
export GEM_VERSION=2.1.0
export RELEASE_VERSION=1
export PACKAGE_VERSION=${GEM_VERSION}-${RELEASE_VERSION}

export PROJECT_NAME='pact-mock_service'
export REPOSITORY='bethesque/pact-mock_service'
build

export STANDALONE_PACKAGE_NAME="${PROJECT_NAME//_/-}-${PACKAGE_VERSION}-win32"
export PYPI_PACKAGE_NAME="${PROJECT_NAME//_/-}-win32"
export SUFFIX='win32'
export EXTENSION='zip'
package

export STANDALONE_PACKAGE_NAME="${PROJECT_NAME//_/-}-${PACKAGE_VERSION}-osx"
export PYPI_PACKAGE_NAME="${PROJECT_NAME//_/-}-darwin"
export SUFFIX='osx'
export EXTENSION='tar.gz'
package

export STANDALONE_PACKAGE_NAME="${PROJECT_NAME//_/-}-${PACKAGE_VERSION}-linux-x86"
export PYPI_PACKAGE_NAME="${PROJECT_NAME//_/-}-ia32"
export SUFFIX='linux-x86'
export EXTENSION='tar.gz'
package

export STANDALONE_PACKAGE_NAME="${PROJECT_NAME//_/-}-${PACKAGE_VERSION}-linux-x86_64"
export PYPI_PACKAGE_NAME="${PROJECT_NAME//_/-}-linux-x64"
export SUFFIX='linux-x86_64'
export EXTENSION='tar.gz'
package

echo "Packaging the Verifier for distribution."
export GEM_VERSION=1.0.1
export RELEASE_VERSION=1
export PACKAGE_VERSION=${GEM_VERSION}-${RELEASE_VERSION}
export PROJECT_NAME='pact-provider-verifier'
export REPOSITORY='pact-foundation/pact-provider-verifier'
build

export STANDALONE_PACKAGE_NAME="${PROJECT_NAME}-${PACKAGE_VERSION}-win32"
export PYPI_PACKAGE_NAME="${PROJECT_NAME}-win32"
export SUFFIX='win32'
export EXTENSION='zip'
package

export STANDALONE_PACKAGE_NAME="${PROJECT_NAME}-${PACKAGE_VERSION}-osx"
export PYPI_PACKAGE_NAME="${PROJECT_NAME}-darwin"
export SUFFIX='osx'
export EXTENSION='tar.gz'
package

export STANDALONE_PACKAGE_NAME="${PROJECT_NAME}-${PACKAGE_VERSION}-linux-x86"
export PYPI_PACKAGE_NAME="${PROJECT_NAME}-linux-ia32"
export SUFFIX='linux-x86'
export EXTENSION='tar.gz'
package

export STANDALONE_PACKAGE_NAME="${PROJECT_NAME}-${PACKAGE_VERSION}-linux-x86_64"
export PYPI_PACKAGE_NAME="${PROJECT_NAME}-linux-x64"
export SUFFIX='linux-x86_64'
export EXTENSION='tar.gz'
package
