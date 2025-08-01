# Pact Python FFI

> [!NOTE]
>
> This package provides direct access to the Pact Foreign Function Interface (FFI) with minimal abstraction. It is intended for advanced users who need low-level control over Pact operations in Python.

<!-- markdownlint-disable no-inline-html -->
<div align="center"><table>
    <tr>
        <td>Package</td>
        <td>
            <a href="https://pypi.python.org/pypi/pact-python-ffi"><img src="https://img.shields.io/pypi/v/pact-python-ffi.svg" alt="Version"></a>
            <a href="https://pypi.python.org/pypi/pact-python-ffi"><img src="https://img.shields.io/pypi/pyversions/pact-python-ffi.svg" alt="Python Versions"></a>
            <a href="https://pypi.python.org/pypi/pact-python-ffi"><img src="https://img.shields.io/pypi/dm/pact-python-ffi.svg" alt="Downloads"></a>
        </td>
    </tr>
    <tr>
        <td>CI/CD</td>
        <td>
            <a
                href="https://github.com/pact-foundation/pact-python/actions/workflows/test.yml"><img
                src="https://img.shields.io/github/actions/workflow/status/pact-foundation/pact-python/test.yml?branch=main&label=test"
                alt="Test Status"></a>
            <a
                href="https://github.com/pact-foundation/pact-python/actions/workflows/build-cli.yml"><img
                src="https://img.shields.io/github/actions/workflow/status/pact-foundation/pact-python/build-cli.yml?branch=main&label=build"
                alt="Build Status"></a>
            <a
                href="https://github.com/pact-foundation/pact-python/actions/workflows/docs.yml"><img
                src="https://img.shields.io/github/actions/workflow/status/pact-foundation/pact-python/docs.yml?branch=main&label=docs"
                alt="Build Status"></a>
        </td>
    </tr>
    <tr>
        <td>Meta</td>
        <td>
            <a
                href="https://github.com/pypa/hatch"><img
                src="https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg"
                alt="Hatch project"></a>
            <a href="https://github.com/astral-sh/ruff"><img
                src="https://img.shields.io/badge/ruff-ruff?label=linting&color=%23261230"
                alt="linting - Ruff"></a>
            <a href="https://github.com/astral-sh/ruff"><img
                src="https://img.shields.io/badge/ruff-ruff?label=style&color=%23261230"
                alt="style - Ruff"></a>
            <a
                href="https://github.com/python/mypy"><img
                src="https://img.shields.io/badge/types-Mypy-blue.svg"
                alt="types - Mypy"></a>
            <a
                href="https://pypi.python.org/pypi/pact-python-ffi"><img
                src="https://img.shields.io/pypi/l/pact-python-ffi.svg"
                alt="License"></a>
        </td>
    </tr>
    <tr>
        <td>Community</td>
        <td>
            <a
                href="https://github.com/pact-foundation/pact-python/issues"><img
                src="https://img.shields.io/github/issues/pact-foundation/pact-python.svg"
                alt="Issues"></a>
            <a
                href="https://github.com/pact-foundation/pact-python/discussions"><img
                src="https://img.shields.io/github/discussions/pact-foundation/pact-python.svg"
                alt="Discussions"></a>
            <a
                href="https://github.com/pact-foundation/pact-python"><img
                src="https://img.shields.io/github/stars/pact-foundation/pact-python.svg?style=flat"
                alt="GitHub Stars"></a>
            <br/>
            <a
                href="http://slack.pact.io"><img
                src="https://img.shields.io/badge/slack-pact--foundation-4A154B.svg"
                alt="Slack"></a>
            <a
                href="https://stackoverflow.com/questions/tagged/pact"><img
                src="https://img.shields.io/badge/stackoverflow-pact-F48024.svg"
                alt="Stack Overflow"></a>
            <a
                href="https://twitter.com/pact_up"><img
                src="https://img.shields.io/badge/X-@pact__up-black.svg"
                alt="Twitter"></a>
        </td>
    </tr>
</table></div>
<!-- markdownlint-enable no-inline-html -->

---

This sub-package is part of the [Pact Python](https://github.com/pact-foundation/pact-python) project and exists to expose the [Pact FFI](https://github.com/pact-foundation/pact-reference) directly to Python. If you are looking for the main Pact Python library for contract testing, please see the [root package](https://github.com/pact-foundation/pact-python#pact-python).

## Overview

-   The module provides a thin Python wrapper around the Pact FFI (C API).
-   Most classes correspond directly to structs from the FFI, and are designed to wrap the underlying C pointers.
-   Many classes implement the `__del__` method to ensure memory allocated by the Rust library is freed when the Python object is destroyed, preventing memory leaks.
-   Functions from the FFI are exposed directly: if a function `foo` exists in the FFI, it is accessible as `pact_ffi.foo`.
-   The API is not guaranteed to be stable and is intended for use by advanced users or for building higher-level libraries. For typical contract testing, use the main Pact Python client library.

## Installation

You can install this package via pip:

```console
pip install pact-python-ffi
```

## Usage

This package exposes the raw FFI bindings for Pact. It is suitable for advanced use cases, custom integrations, or for building higher-level libraries. For typical contract testing, prefer using the main Pact Python library.

## Contributing

As this is a relatively thin wrapper around the Pact FFI, the code is unlikely to change frequently; however, contributions to improve the coverage of the FFI bindings or to improve existing functionality are welcome. See the [main contributing guide](https://github.com/pact-foundation/pact-python/blob/main/CONTRIBUTING.md) for details.

To release a new version of `pact-python-ffi`, simply push a tag in the format `pact-python-ffi/x.y.z.w`. This will automatically trigger a release process, pulling in version `x.y.z` of the underlying Pact FFI. Before creating and pushing such a tag, please ensure that the Python wrapper has been updated to reflect any changes or updates in the corresponding FFI version.

Higher-level abstractions or utilities should be implemented in separate libraries (such as [`pact-python`](https://github.com/pact-foundation/pact-python)).

---

For questions or support, please visit the [Pact Foundation Slack](https://slack.pact.io) or [GitHub Discussions](https://github.com/pact-foundation/pact-python/discussions)

---
