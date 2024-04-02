# Pact Python

<!-- markdownlint-disable no-inline-html -->
<div align="center">
    <b>Fast, easy and reliable testing for your APIs and microservices.</b>
</div>

<div align="center"><table>
    <tr>
        <td>Package</td>
        <td>
            <a href="https://pypi.python.org/pypi/pact-python"><img src="https://img.shields.io/pypi/v/pact-python.svg" alt="Version"></a>
            <a href="https://pypi.python.org/pypi/pact-python"><img src="https://img.shields.io/pypi/pyversions/pact-python.svg" alt="Python Versions"></a>
            <a href="https://pypi.python.org/pypi/pact-python"><img src="https://img.shields.io/pypi/dm/pact-python.svg" alt="Downloads"></a>
        </td>
    </tr>
    <tr>
        <td>CI/CD</td>
        <td>
            <a
                href="https://github.com/pact-foundation/pact-python/actions/workflows/test.yml"><img
                src="https://img.shields.io/github/actions/workflow/status/pact-foundation/pact-python/test.yml?branch=master&label=test"
                alt="Test Status"></a>
            <a
                href="https://github.com/pact-foundation/pact-python/actions/workflows/build.yml"><img
                src="https://img.shields.io/github/actions/workflow/status/pact-foundation/pact-python/build.yml?branch=master&label=build"
                alt="Build Status"></a>
            <a
                href="https://github.com/pact-foundation/pact-python/actions/workflows/docs.yml"><img
                src="https://img.shields.io/github/actions/workflow/status/pact-foundation/pact-python/docs.yml?branch=master&label=docs"
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
                href="https://pypi.python.org/pypi/ruff"><img
                src="https://img.shields.io/pypi/l/pact-python.svg"
                alt="License"></a>
        </td>
    </tr>
    <tr>
        <td>Community</td>
        <td>
            <a
                href="http://slack.pact.io"><img
                src="https://slack.pact.io/badge.svg"
                alt="Slack"></a>
            <a
                href="https://stackoverflow.com/questions/tagged/pact"><img
                src="https://img.shields.io/badge/stackoverflow-pact-orange.svg"
                alt="Stack Overflow"></a>
            <a
                href="https://twitter.com/pact_up"><img
                src="https://img.shields.io/twitter/follow/pact_up?style=social"
                alt="Twitter"></a>
        </td>
    </tr>
</table></div>

<div align="center"><table><tr><td>
<b>Pact</b> is the de-facto API contract testing tool. Replace expensive and brittle end-to-end integration tests with fast, reliable and easy to debug unit tests.

<ul style="list-style-type: none">
    <li>⚡ Lightning fast</li>
    <li>🎈 Effortless full-stack integration testing - from the front-end to the back-end</li>
    <li>🔌 Supports HTTP/REST and event-driven systems</li>
    <li>🛠️ Configurable mock server</li>
    <li>😌 Powerful matching rules prevents brittle tests</li>
    <li>🤝 Integrates with Pact Broker / PactFlow for powerful CI/CD workflows</li>
    <li>🔡 Supports 12+ languages</li>
</ul>

<b>Why use Pact?</b> Contract testing with Pact lets you:

<ul style="list-style-type: none">
    <li>⚡ Test locally</li>
    <li>🚀 Deploy faster</li>
    <li>⬇️ Reduce the lead time for change</li>
    <li>💰 Reduce the cost of API integration testing</li>
    <li>💥 Prevent breaking changes</li>
    <li>🔎 Understand your system usage</li>
    <li>📃 Document your APIs for free</li>
    <li>🗄 Remove the need for complex data fixtures</li>
    <li>🤷‍♂️ Reduce the reliance on complex test environments</li>
</ul>

Watch our <a href="https://www.youtube.com/playlist?list=PLwy9Bnco-IpfZ72VQ7hce8GicVZs7nm0i">series</a> on the problems with end-to-end integrated tests, and how contract testing can help.

</td></tr></table></div>

<!-- markdownlint-enable no-inline-html -->

## Documentation

This readme provides a high-level overview of the Pact Python library. For detailed documentation, please refer to the [full Pact Python documentation](https://pact-foundation.github.io/pact-python). For a more general overview of Pact and the rest of the ecosystem, please refer to the [Pact documentation](https://docs.pact.io).

-   [Installation](#installation)
-   [Consumer testing](docs/consumer.md)
-   [Provider testing](docs/provider.md)
-   [Examples](examples/README.md)

Documentation for the API is generated from the docstrings in the code which you can view [here](https://pact-foundation.github.io/pact-python/pact). Please be aware that only the [`pact.v3` module][pact.v3] is thoroughly documented at this time.

### Need Help

-   [Join](https://slack.pact.io) our community [slack workspace][Pact Foundation Slack].
-   [Stack Overflow](https://stackoverflow.com/questions/tagged/pact) is a great place to ask questions.
-   Say 👋 on Twitter: [@pact_up](https://twitter.com/pact_up)
-   Join a discussion 💬 on [GitHub Discussions]
-   [Raise an issue][GitHub Issues] on GitHub

[Pact Foundation Slack]: https://pact-foundation.slack.com/
[GitHub Discussions]: https://github.com/pact-foundation/pact-python/discussions
[GitHub Issues]: https://github.com/pact-foundation/pact-python/issues

## V3 Preview

Pact Python is currently undergoing a major rewrite which will be released with the `3.0.0` version. This rewrite will replace the existing Ruby backend with a Rust backend which will provide a significant performance improvement and will allow us to support more features in the future. You can find more information about this rewrite in [this tracking issue on GitHub](https://github.com/pact-foundation/pact-python/issues/396).

You can preview the new version by using the [`pact.v3` module][pact.v3]. The new version is not yet feature complete, and may be subject to changes. Having said that, we would love to get your feedback on the new version:

-   For any issues you find, please [raise an issue][GitHub Issues] on GitHub.
-   For any feedback you have, please join the discussion either on [GitHub Discussions] or in the [`#pact-python`](https://pact-foundation.slack.com/archives/C9VECUP6E) channel on the [Pact Foundation Slack].

## Installation

The latest version of Pact Python can be installed from PyPi:

```sh
pip install pact-python
# 🚀 now write some tests!
```

### Requirements

Pact Python tries to support all versions of Python that are still supported by the Python Software Foundation. Older version of Python may work, but are not officially supported.

In order to support the broadest range of use cases, Pact Python tries to impose the least restrictions on the versions of libraries that it uses.

### Do Not Track

In order to get better statistics as to who is using Pact, we have an anonymous tracking event that triggers when Pact installs for the first time. The only things we [track](https://docs.pact.io/metrics) are your type of OS, and the version information for the package being installed. No personally identifiable information is sent as part of this request. You can disable tracking by setting the environment variable `PACT_DO_NOT_TRACK=1`:

## Contributing

We welcome contributions to the Pact Python library in many forms. There are many ways to help, from writing code, to providing new examples, to writing documentation, to testing the library and providing feedback. For more information, see the [contributing guide](CONTRIBUTING.md).

[![Table of contributors](https://contrib.rocks/image?repo=pact-foundation/pact-python)](https://github.com/pact-foundation/pact-python/graphs/contributors)
