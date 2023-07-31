## Example Consumer and provider test using Pact V3 features

This is an example project with a test that uses V3 Pact features. It has an example test for both JSON
and XML format. It has been ported from the Pact-JS project.

## To run it

Until the beta version of Pact-Python with V3 support is released, you need to do the following:

1. Install Rust

Use the Rustup tool from https://rustup.rs/ to do this.

2. Setup a Python virtual environment

```console
$ python3 -m venv venv
$ source venv/bin/activate
```

3. Generate the pact_python_v3 wheel

In the pact-python-v3 directory, use maturin to create the wheel for your architecture and OS:

```console
$ cd ../../../pact-python-v3
$ maturin build
```

This should output the path to the newly created wheel.

4. Install the wheel with pip

```console
# NOTE: this path is architecture and OS dependent, don't just copy this line and hope it works for you
$ pip install ../../../pact-python-v3/target/wheels/pact_python_v3-0.0.0-cp38-cp38-manylinux2010_x86_64.whl
```

5. In the project root, build the Pact-Python package as per the instructions in the Readme

```console
$ cd ../../..
$ make package
```

**NOTE:** I had to run the package command myself, because I have both Python 2 and 3 and the 
make file was picking up Python 2

```console
$ # If the command above fails 
$ python3 setup.py sdist
```

6. Install the Pact Python package

```console
$ cd -
$ pip install ../../../dist/pact-python-2.0.0b0.tar.gz 
```

5. Install all the required packages

```console
pip install -r requirements.txt
```

4. Run the tests

```console
$ pytest
```

## V3 features

This has 3 tests. The first uses generators and matchers for numbers and datetime values. The second 
test deals with XML responses. The last one posts an image to the provider.

## Enabling debug logs

The `LOG_LEVEL` environment variable controls the log output from the Rust libs.

```console
$ LOG_LEVEL=debug pytest --capture=no
```
