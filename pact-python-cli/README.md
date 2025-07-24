
# Pact Python CLI

> [!NOTE]
>
> This package is used to package and bundle the Pact CLI _only_. It does not provide any Python functionality or API.

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
