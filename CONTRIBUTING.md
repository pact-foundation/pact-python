# Raising issues

_Before raising an issue, please ensure that you are using the latest version of pact-python._

Please provide the following information with your issue to enable us to respond as quickly as possible.

- The relevant versions of the packages you are using.
- The steps to recreate your issue.
- The full stacktrace if there is an exception.
- An executable code example where possible. You can fork this repository and
  use the [examples] directory to quickly recreate your issue.

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

[examples]: https://github.com/pact-foundation/pact-python/tree/master/examples

## Commit messages

pact-python is adopting the [Conventional Commits](https://www.conventionalcommits.org)
convention. Please ensure you follow the guidelines, we don't want to be that person,
but the commit messages are very important to the automation of our release process.

Take a look at the git history (`git log`) to get the gist of it.

If you'd like to get some CLI assistance there is a node npm package. Example usage is:

```shell
npm install -g commitizen
npm install -g cz-conventional-changelog
echo '{ "path": "cz-conventional-changelog" }' > ~/.czrc
```

When you commit with Commitizen, you'll be prompted to fill out any required
commit fields at commit time. Simply use `git cz` or just `cz` instead of
`git commit` when committing. You can also use `git-cz`, which is an alias
for `cz`.

See https://www.npmjs.com/package/commitizen for more info.

There is a pypi package that does similar [commitizen](https://pypi.org/project/commitizen/).

## Running the tests

You can run the tests locally with `make test`, this will run the tests with `tox`

You will need `pyenv` to test on different versions `3.6`, `3.7`, `3.8`, `3.9`,
`3.10`, `3.11`.

Download and install python versions:
```
pyenv install 3.6.15 3.7.16 3.8.16 3.9.16 3.10.10 3.11.2
```

Set these versions locally for the project:
```
pyenv local 3.6.15 3.7.16 3.8.16 3.9.16 3.10.10 3.11.2
```

Run the tests:
```
make test
```

### macOS Setup Guide

See the following guides to setup Python and configure `pyenv` on your Mac.

- [How to Install Python on macOS](https://realpython.com/installing-python/#how-to-install-python-on-macos)
- [Managing Multiple Python Versions With pyenv](https://realpython.com/intro-to-pyenv/)

## Running the examples

Make sure you have docker running!
