# Contributing to Pact Python

Pact Python is the Python implementation of the [Pact](https://pact.io) integration testing framework. If you're interested in contributing to Pact Python, hopefully, this document makes the process for contributing clear.

The [Open Source Guides](https://opensource.guide/) website has a collection of resources for individuals, communities, and companies who want to learn how to run and contribute to an open source project. Contributors and people new to open source alike will find the following guides especially useful:

-   [How to Contribute to Open Source](https://opensource.guide/how-to-contribute/)
-   [Building Welcoming Communities](https://opensource.guide/building-community/)
-   [Contributing to Pact](https://docs.pact.io/contributing)

## Get Involved

There are many ways to contribute to Pact Python and the broader Pact ecosystem. Here's a few ideas to get started:

-   Look through the [open issues](https://github.com/pact-foundation/pact-python/issues). Provide workarounds, ask for clarification, or suggest labels. Help [triage issues](#triaging-issues-and-pull-requests).
-   If you find an issue you would like to fix, [open a pull request](#pull-requests). Issues tagged as [_Good first issue_](https://github.com/pact-foundation/pact-python/labels/Good%20first%20issue) are a good place to get started.
-   Read through the [docs](https://docs.pact.io). If you find anything that is confusing or can be improved, you can click "Edit this page" at the bottom of most docs, which takes you to the GitHub interface to make and propose changes.
-   Take a look at the [features requested](https://github.com/pact-foundation/pact-python/labels/feature) by others in the community and consider opening a pull request if you see something you want to work on.

Contributions are very welcome. If you think you need help planning your contribution, please ping us on [Slack](https://slack.pact.io) and let us know you are looking for a bit of help.

### Join our Community

We have a [Slack](https://slack.pact.io) to discuss all things about Pact and its development. Feel free to ask questions about Pact Python specifically in the [`#pact-python`](https://pact-foundation.slack.com/archives/C9VECUP6E) channel, or broader questions about the Pact ecosystem over in the [`#general`](https://pact-foundation.slack.com/archives/C5F4KFKR8) channel. We store a searchable archive of our Slack channels on [linen.dev](https://linen.dev/s/pact-foundation).

Questions have also been asked over on StackOverflow, under the [`pact`](https://stackoverflow.com/questions/tagged/pact) tag. This is a great place to ask more general usage questions for pact, and discover existing answers.

### Triaging Issues and Pull Requests

One great way you can contribute to the project without writing any code is to help triage issues and pull requests as they come in.

-   Ask for more information if you believe the issue does not provide all the details required to solve it.
-   Suggest [labels](https://github.com/pact-foundation/pact-python/labels) that can help categorize issues.
-   Flag issues that are stale or that should be closed.
-   Ask for test plans and review code.

## Our Development Process

Pact Python uses [GitHub](https://github.com/pact-foundation/pact-python) as its source of truth. The team will be working directly there. All changes will be public from the beginning.

All pull requests will be checked by the continuous integration system, GitHub actions. There are unit tests, end-to-end tests, performance tests, style tests, and much more.

### Branch Organization

Pact Python has one primary branch `master` and we use feature branches to deliver new features with pull requests. Typically, we scope the branch according to the [conventional commit](#conventional-commit-messages) categories. The more common ones are:

-   `feature/<name>` or `feat/<name>` for new features
-   `fix/<name>` for bug fixes
-   `chore/<name>` for chores
-   `docs/<name>` for documentation changes

## Issues

When [opening a new issue](https://github.com/pact-foundation/pact-python/issues/new/choose), always make sure to fill out the issue template. **This step is very important!** Not doing so may slow down the response. Don't take this personally if this happens, and feel free to open a new issue once you've gathered all the information required by the template.

**Please don't use the GitHub issue tracker for questions.** If you have questions about using Pact Python, prefer the [Discussion pages](https://github.com/pact-foundation/pact-python/discussions) or [Slack](https://slack.pact.io), and we will do our best to answer your questions.

### Bugs

We use [GitHub Issues](https://github.com/pact-foundation/pact-python/issues) for our public bugs. If you would like to report a problem, take a look around and see if someone already opened an issue about it. If you are certain this is a new, unreported bug, you can submit a [bug report](https://github.com/pact-foundation/pact-python/issues/new?assignees=&labels=bug%2Cstatus%3A+needs+triage&template=bug.yml).

-   **One issue, one bug:** Please report a single bug per issue.
-   **Provide reproduction steps:** List all the steps necessary to reproduce the issue. The person reading your bug report should be able to follow these steps to reproduce your issue with minimal effort.

If you're only fixing a bug, it's fine to submit a pull request right away but we still recommend filing an issue detailing what you're fixing. This is helpful in case we don't accept that specific fix but want to keep track of the issue.

### Feature requests

If you would like to request a new feature or enhancement but are not yet thinking about opening a pull request, you can file an issue with the [feature template](https://github.com/pact-foundation/pact-python/issues/new?assignees=&labels=feature%2Cstatus%3A+needs+triage&template=feature.yml) for more thought out ideas. Alternatively, you can use the [Canny board](https://pact.canny.io/) for more casual feature requests and gain enough traction before proposing an RFC.

### Claiming issues

We have a list of [beginner-friendly issues](https://github.com/pact-foundation/pact-python/labels/good%20first%20issue) to help you get your feet wet in the Pact Python codebase and familiar with our contribution process. This is a great place to get started.

Apart from the `good first issue`, it is also worth looking at the [`help wanted`](https://github.com/pact-foundation/pact-python/labels/help%20wanted) issues. If you have specific knowledge in one domain, working on these issues can make your expertise shine.

If you want to work on any of these issues, just drop a message saying "I'd like to work on this", and we will assign the issue to you and update the issue's status as "claimed".

Alternatively, when opening an issue, you can also click the "self service" checkbox to indicate that you'd like to work on the issue yourself, which will also make us see the issue as "claimed".

Once an issue is claimed, we hope to see a pull request; however we understand that life happens and you may not be able to complete the issue. If you are unable to complete the issue, please let us know so we can unassign the issue and make it available for others to work on.

The claiming process is there to help ensure effort is wasted. Even if you are not sure whether you can complete the issue, claiming it will help us know that someone is working on it. If you are not sure how to proceed, feel free to ask for help.

## Development

### Online one-click setup for contributing

You can also try using the new [github.dev](https://github.dev/pact-foundation/pact-python) feature. While you are browsing any file, changing the domain name from `github.com` to `github.dev` will turn your browser into an online editor. You can start making changes and send pull requests right away. This is a great way to get started quickly, but it does not offer the full development environment and you won't be able to run tests.

### Installation

1.  Ensure you have [Python](https://www.python.org/) installed.

2.  Ensure you have [Hatch](https://hatch.pypa.io/) installed. This is used to manage the development environment can be installed as follows:

    ```sh
    python -m pip install --user pipx # If you don't have pipx
    pipx install hatch
    ```

3.  After cloning the repository, run `hatch shell` in the root of the repository. This will install all dependencies in a Python virtual environment and then ensure that the virtual environment is activated.

4.  To run tests, run `hatch run test` to make sure the test suite is working. You should also make sure the example works by running `hatch run example`. For the examples, you will have to make sure that you have Docker (or a suitable alternative) installed and running.

5.  If you want to run the tests against all supported Python versions, you can run `hatch run test:all`.

### Code Conventions

-   **Most important: Look around.** Match the style you see used in the rest of the project. This includes formatting, naming files, naming things in code, naming things in documentation, etc.
-   "Attractive"
-   We do have Black (a formatter) and Ruff (a syntax linter) to catch most stylistic problems. If you are working locally, they should automatically fix some issues during git commits and push.

Don't worry too much about styles in general—the maintainers will help you fix them as they review your code.

To help catch a lot of simple formatting or linting issues, you can run `hatch run lint` to run Black and Ruff. This process can also be automated by installing [`pre-commit`](https://pre-commit.com/) hooks:

```sh
pre-commit install
```

## Pull Requests

So you are considering contributing to Pact Python's code? Great! We'd love to have you. First off, please make sure it is related to an existing issue. If not, please open a new issue to discuss the problem you are trying to solve before investing a lot of time into a pull request. While we do accept PRs that are not related to an issue (especially if the PR is very simple), it is best to discuss it first to avoid wasting your time.

Once you have opened a PR, we will do our best to work with you and get the PR looked at.

Working on your first Pull Request? You can learn how from this free video series:

[**How to Contribute to an Open Source Project on GitHub**](https://egghead.io/courses/how-to-contribute-to-an-open-source-project-on-github)

Please make sure the following is done when submitting a pull request:

1. **Keep your PR small.** Small pull requests (~300 lines of diff) are much easier to review and more likely to get merged. Make sure the PR does only one thing, otherwise please split it.
2. **Use descriptive titles.** It is recommended to follow this [commit message style](#semantic-commit-messages).
3. **Test your changes.** Describe your [**test plan**](#test-plan) in your pull request description.

All pull requests should be opened against the `master` branch.

We have a lot of integration systems that run automated tests to guard against mistakes. The maintainers will also review your code and may fix obvious issues for you. These systems' duty is to make you worry as little about the chores as possible. Your code contributions are more important than sticking to any procedures, although completing the checklist will surely save everyone's time.

### Conventional Commit Messages

Pact Python has adopted the [Conventional Commit](https://www.conventionalcommits.org/en/v1.0.0/) convention and we use it to generate our changelog and in the automation of our release process.

The format is:

```text
<type>(<scope>): <subject>
```

`<scope>` is optional. If your change is specific to one/two packages, consider adding the scope. Scopes should be brief but recognizable, e.g. `docs`, `ci`, etc. You can take a quick look at the Git history (`git log`) to get the gist.

The various types of commits:

-   `feat`: a new API or behavior **for the end user**.
-   `fix`: a bug fix **for the end user**.
-   `docs`: a change to the website or other Markdown documents in our repo.
-   `style`: a change to production code that leads to no behavior difference, e.g. splitting files, renaming internal variables, improving code style...
-   `test`: adding missing tests, refactoring tests; no production code change.
-   `chore`: upgrading dependencies, releasing new versions... Chores that are **regularly done** for maintenance purposes.
-   `misc`: anything else that doesn't change production code and doesn't fit in the above.

If you'd like to get some CLI assistance, you can install [commitizen](https://www.npmjs.com/package/commitizen). The `cz` command line tool will help you write conventional commit messages.

### Test Plan

A good test plan has the exact commands you ran and their output.

Tests are integrated into our continuous integration system, so you don't always need to run local tests. However, for significant code changes, it saves both your and the maintainers' time if you can do exhaustive tests locally first to make sure your PR is in good shape. There are many types of tests:

-   **Build and typecheck.** We use [mypy](https://mypy.readthedocs.io/en/stable/) in our codebase, which can make sure your code is consistent and catches some obvious mistakes early.
-   **Unit tests.** We use [pytest](https://pytest.org) for unit tests. You can run `hatch run test` in the root directory to run all tests, and `hatch run test:all` to test against all supported Python versions.

### Licensing

By contributing to Pact Python, you agree that your contributions will be licensed under its MIT license.

### Breaking Changes

When adding a new breaking change, follow this template in your pull request:

```md
### New breaking change here

-   **Who does this affect**:
-   **How to migrate**:
-   **Why make this breaking change**:
-   **Severity (number of people affected x effort)**:
```

### What Happens Next?

The team will be monitoring pull requests. Do help us by keeping pull requests consistent by following the guidelines above.
