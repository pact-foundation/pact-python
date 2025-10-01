
# Pact Python CLI

> [!NOTE]
>
> This package is used to package and bundle the Pact CLI _only_. It does not provide any Python functionality or API.

<!-- markdownlint-disable no-inline-html -->
<div align="center"><table>
    <tr>
        <td>Package</td>
        <td>
            <a href="https://pypi.python.org/pypi/pact-python-cli"><img src="https://img.shields.io/pypi/v/pact-python-cli.svg" alt="Version"></a>
            <a href="https://pypi.python.org/pypi/pact-python-cli"><img src="https://img.shields.io/pypi/pyversions/pact-python-cli.svg" alt="Python Versions"></a>
            <a href="https://pypi.python.org/pypi/pact-python-cli"><img src="https://img.shields.io/pypi/dm/pact-python-cli.svg" alt="Downloads"></a>
        </td>
    </tr>
    <tr>
        <td>CI/CD</td>
        <td>
            <a
                href="https://github.com/pact-foundation/pact-python/actions/workflows/test.yml?query=branch:main"><img
                src="https://img.shields.io/github/actions/workflow/status/pact-foundation/pact-python/test.yml?branch=main&label=test"
                alt="Test Status"></a>
            <a
                href="https://github.com/pact-foundation/pact-python/actions/workflows/build-cli.yml?query=branch:main"><img
                src="https://img.shields.io/github/actions/workflow/status/pact-foundation/pact-python/build-cli.yml?branch=main&label=build"
                alt="Build Status"></a>
            <a
                href="https://github.com/pact-foundation/pact-python/actions/workflows/docs.yml?query=branch:main"><img
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
                href="https://pypi.python.org/pypi/pact-python-cli"><img
                src="https://img.shields.io/pypi/l/pact-python-cli.svg"
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

This sub-package is part of the [Pact Python](https://github.com/pact-foundation/pact-python) project and exists solely to distribute the [Pact CLI](https://github.com/pact-foundation/pact-ruby-standalone) as a Python package. If you are looking for the main Pact Python library for contract testing, please see the [root package](https://github.com/pact-foundation/pact-python#pact-python).

It is used by version 2 of Pact Python, and can be used to install the Pact CLI in Python environments.

The versionining of `pact-python-cli` is aligned with the Pact CLI versioning. For example, version `2.4.26.2` corresponds to Pact CLI version `2.4.26`, with the `.2` indicating that this is the third release of that Pact CLI version in the Python package (with the first release being `.0`).

## Installation

You can install this package via pip:

```console
pip install pact-python-cli
```

## Contributing

Contributions to this package are generally not required as it contains minimal Python functionality and generally only requires updating the version number. This is done by pushing a tag of the form `pact-python-cli/<version>` which will automatically trigger a release build in the CI pipeline.

To contribute to the Pact CLI itself, please refer to the [Pact Ruby Standalone repository](https://github.com/pact-foundation/pact-ruby-standalone).

For contributing to Pact Python, see the [main contributing guide](https://github.com/pact-foundation/pact-python/blob/main/CONTRIBUTING.md).

---

For questions or support, please visit the [Pact Foundation Slack](https://slack.pact.io) or [GitHub Discussions](https://github.com/pact-foundation/pact-python/discussions).

---
