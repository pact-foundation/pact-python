# Raising issues

_Before raising an issue, please ensure that you are using the latest version of pact-python._

Please provide the following information with your issue to enable us to respond as quickly as possible.

- The relevant versions of the packages you are using.
- The steps to recreate your issue.
- The full stacktrace if there is an exception.
- An executable code example where possible. You can fork this repository and use the [e2e] directory to quickly recreate your issue.

# Contributing

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request

If you are intending to implement a fairly large feature we'd appreciate if you open
an issue with GitHub detailing your use case and intended solution to discuss how it
might impact other work that is in flight.

We also appreciate it if you take the time to update and write tests for any changes
you submit.

[e2e]: https://github.com/pact-foundation/pact-python/tree/master/e2e

## Commit messages

Pact Python is adopting the Conventional Changelog commit message conventions. Please ensure you follow the guidelines, we don't want to be that person, but the commit messages are very important to the automation of our release process.

Take a look at the git history (git log) to get the gist of it.

If you'd like to get some CLI assistance there is a node npm package. Example usage is:

```
npm install commitizen -g
npm i -g cz-conventional-changelog
```

git cz to commit and commitizen will guide you.

There is a pypi package that does similar [commitizen]: https://pypi.org/project/commitizen/. This would make a great feature to add! There is a check on the travis build that your commits follow this convention. On creating a PR any commits that don't will instantly fail the build and you will have to rename them.

## Running the tests

You can run the tests locally with `make test`, this will run the tests with `tox`

You will need `pyenv` to test on different versions `3.6`, `3.7`, `3.8`, `3.9`, `3.10`

`pyenv install 3.6.15 3.7.13 3.8.13 3.9.14 3.10.6` - Download and install python versions
`pyenv local 3.6.15 3.8.13 3.7.13 3.9.14 3.10.6` - Set these versions locally for the project
`make test` - Run the tests

### MacOS Setup Guide

See the following guides to setup `Python` and configure `pyenv` on your Mac.

- https://yellowdesert.consulting/2018/02/04/python-on-mac-one-of-the-good-ways/
- https://yellowdesert.consulting/2020/10/24/tox-testing-multiple-python-versions-with-pyenv/

## Running the examples

Make sure you have docker running!
