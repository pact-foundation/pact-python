# Changelog

All notable changes to this project will be documented in this file.

<!-- markdownlint-disable no-duplicate-heading -->
<!-- markdownlint-disable emph-style -->
<!-- markdownlint-disable strong-style -->

## [pact-python/3.3.1] _2026-04-22_

### 🐛 Bug Fixes

-   Avoid rare port clash

### ⚙️ Miscellaneous Tasks

-   Simplify find_free_port
-   Replace pre-commit with prek

### Contributors

-   @JP-Ellis

## [pact-python/3.3.0] _2026-04-17_

### 🚀 Features

-   Add xml matching

    A new `pact.xml` module provides builder functions for constructing XML request and response bodies with embedded Pact matchers. Use `xml.element()` to describe the XML structure and attach matchers where needed, then wrap the result with `xml.body()` before passing it to `with_body(..., content_type="application/xml")`:

    ```python
    from pact import match, xml

    response = xml.body(
        xml.element(
            "user",
            xml.element("id", match.int(123)),
            xml.element("name", match.str("Alice")),
        )
    )
    interaction.with_body(response, content_type="application/xml")
    ```

    Repeating elements are supported via `.each(min=1, examples=2)` on any `XmlElement`. Attributes (including namespace declarations) can be passed via the `attrs` keyword argument.
-   Allow iteration over all interactions
-   Use common `PactInteraction` type
-   Can toggle follow redirects
-   Allow plugin loading delay

### 📚 Documentation

-   Update changelog for pact-python/3.2.1
-   _(examples)_ Add http+xml example
-   Update xml example to use new matcher
-   _(examples)_ Add service consumer/provider HTTP example

### ⚙️ Miscellaneous Tasks

-   _(ci)_ Re-enable 3.14 tests
-   Upgrade stable python version
-   Add .worktrees to .gitignore
-   _(ci)_ Reduce ci usage
-   _(ci)_ Downgrade stable python version
-   _(ci)_ Remove unused workflows
-   Remove versioningit, switch to static version in pyproject.toml
-   Add release script
-   Minor update to cliff config
-   Authenticate gh api calls
-   Remove release label
-   Replace taplo with tombi
-   _(ci)_ Have wheel target 310
-   _(ci)_ Avoid most of CI on draft PRs
-   Fix hatch env workspaces
-   Remove connect test

### � Other

-   Fix coverage upload overwrite and add example coverage

### Contributors

-   @JP-Ellis
-   @adityagiri3600
-   @benaduo
-   @Nikhil172913832

## [pact-python/3.2.1] _2025-12-10_

### 📚 Documentation

-   Update changelog for pact-python/3.2.0
-   Fix internal references
-   Add v3 blog post
-   Fix partial url highlight
-   Fix tooltips in code
-   Remove redundant header from blog post

### ⚙️ Miscellaneous Tasks

-   _(ci)_ Use strict docs building
-   Switch to versioningit

### Contributors

-   @JP-Ellis

## [pact-python/3.2.0] _2025-12-02_

### 🚀 Features

-   Add consumer_version method
-   Add content type matcher
-   Add 'and' matcher

### 🐛 Bug Fixes

-   Use correct matching rule serialisation

### 📚 Documentation

-   Update changelog for pact-python/3.1.0
-   Add agents.md
-   Update configuration
-   Add logging documentation
-   Add multipart/form-data matching rule example
-   Add consumer_version

### ⚙️ Miscellaneous Tasks

-   Add llm instructions
-   Update non-compliant docstrings and types
-   Upgrade pymdownx extensions
-   Set telemetry environment variables
-   _(docs)_ Api docs link on pact-python site is case sensitive
-   Fix json schema url
-   _(tests)_ Fix skipped tests on windows
-   _(ci)_ Update macos runners
-   Remove unused pytest config
-   Remove ruff sub-configs
-   Switch to markdownlint-cli2
-   Rerun flaky tests
-   Remove unused function
-   Don't except AssertionError
-   _(devcontainer)_ Add multi-arch development container support

### Contributors

-   @Nikhil172913832
-   @JP-Ellis
-   @YOU54F
-   @Copilot

## [pact-python/3.1.0] _2025-10-07_

### 🐛 Bug Fixes

-   [**breaking**] Replace v2 extra with compat-v2
    > Installing Pact Python with v2 compatibility requires `pip install 'pact-python[compat-v2]'`, and the old `pip install 'pact-python[v2]'` is no longer supported.

### 📚 Documentation

-   Update changelogs

### ⚙️ Miscellaneous Tasks

-   _(ci)_ Add area-core label
-   _(ci)_ Fix labels workflow permissions
-   Remove no longer relevant todo
-   _(docs)_ Use normalized project url keys

### Contributors

-   @JP-Ellis

## [pact-python/3.0.1] _2025-10-06_

### 📚 Documentation

-   Update changelog for pact-python/3.0.0

### ⚙️ Miscellaneous Tasks

-   Drop cffi dependency
-   _(ci)_ Fix publish step

### Contributors

-   @JP-Ellis

## [pact-python/3.0.0] _2025-10-06_

### 🚀 Features

-   [**breaking**] Default to v4 specification
    > Pact instances default to version 4 of the Pact specification (previously used version 3). This should be mostly backwards compatible, but can be reverted by using `with_specification("V3")`.
-   Populate broker source from env

### 🚜 Refactor

-   _(ci)_ If statement

### 🎨 Styling

-   _(tests)_ Add sections

### 📚 Documentation

-   Update changelog for pact-python/3.0.0a1
-   Add mascot
-   Give mascot outline
-   Set mascot width and height
-   _(examples)_ Add requests and fastapi
-   Generate llms.txt
-   Update mkdocs material features
-   Fix CI badge links
-   Update matcher docs
-   Improve matchers
-   Improve generators
-   Update for v3 and add migration guide

### ⚙️ Miscellaneous Tasks

-   _(ci)_ Remove spelling check
-   _(examples)_ Minor improvements
-   Store hatch venv in .venv
-   Update mismatch repr
-   Save mismatches before exiting the server
-   _(examples)_ Remove old http example
-   Fix sub-project git cliff config
-   Hide import from traceback
-   Fix flask integer coercion
-   Add v3 matching rules test
-   Add v4 matching rules tests
-   _(ci)_ Add publish as completion dependency
-   _(tests)_ Add generators to interaction defn
-   _(tests)_ Test v3 generators
-   _(test)_ Add v4 generators tests
-   Re-add pytest rerunfailrure
-   _(tests)_ Add v3 http generators
-   Prefer prek over pre-commit
-   Disable reruns in vscode
-   _(ci)_ Fix prek caching
-   _(ci)_ Generate junit xml files
-   Move mascot file out of root
-   Update uuid format names
-   Fix import warning
-   Make Unset falsey
-   [**breaking**] Rename abstract matcher class
    > The abstract `pact.match.Matcher` class has been renamed to `pact.match.AbstractMatcher`.
-   [**breaking**] Rename abstract generator
    > The abstract `pact.generate.Generator` class has been renamed to `pact.generate.AbstractGenerator`.
-   Clarify explanation of given
-   [**breaking**] Drop python 3.9 add 3.14
    > Python 3.9 is no longer supported.
-   _(ci)_ Disable 3.14 tests using pydantic

### Contributors

-   @JP-Ellis

## [pact-python/3.0.0a1] _2025-08-12_

### 🚀 Features

-   Create pact-python-cli package
-   _(cli)_ Build abi-agnostic wheels
-   _(ffi)_ Add standalone ffi package
-   _(v3)_ [**breaking**] Remove pact.v3.ffi module
    > `pact.v3.ffi` is removed, and to be replaced by `pact_ffi`. That is, `pact.v3.ffi.$fn` should be replaced by `pact_ffi.$fn`.
-   [**breaking**] Prepare for v3 release
    > This prepares for version 3. Pact Python v2 will be still accessible under `pact.v2` and all imports should be appropriate renamed. Everyone is encouraged to migrate to Pact Python v3.
-   [**breaking**] Simplify `given`
    > The signature of `Interaction.given` has been updated. The following changes are required: - Change `given("state", key="user_id", value=123)` to `given("state", user_id=123)`. This can take an arbitrary number of keyword arguments. If the key is not a valid Python keyword argument, use the dictionary input below. - Change `given("state", parameters={"user_id": 123})` to `given("state", {"user_id": 123})`.
-   [**breaking**] Deserialize metadata values
    > As the metadata values are now deserialised, the type of the metadata values may change. For example, setting metadata `user_id=123` will now pass `{"user_id": 123}` through to the function handler. Previously, this would have been `{"user_id": "123"}`.

### 🐛 Bug Fixes

-   Matcher type variance
-   With metadata function signature
-   [**breaking**] Use correct datetime default format
    > If you relied on the previous default (undocumented) behaviour, prefer specifying the format explicitly now: `match.datetime(regex="%Y-%m-%dT%H:%M:%S.%f%z")`.
-   Handle empty state callback
-   _(verifier)_ [**breaking**] Propagate branch
    > If a branch is set through either `set_publish_options` or `provider_branch`, the value will be saved and used as a default for both in subsequent calls.

### 🚜 Refactor

-   Functional state handler

### 📚 Documentation

-   Update changelog for v2.3.3
-   _(blog)_ Fix v3 references
-   Fix v3 references
-   V3 review
-   Update git cliff configuration

### ⚙️ Miscellaneous Tasks

-   Update pre-commit hooks
-   Use the new `pact_cli` package
-   Remove packaging of pact cli
-   _(ci)_ Incorporate tests of pact cli
-   _(ci)_ Use new `pact-python/*` tags
-   _(ci)_ Add build cli pipeline
-   Exclude hatch_build from mypy checks
-   _(ci)_ Narrow token permissions
-   Remove macosx deployment target
-   _(ci)_ Fix cli publish permissions
-   Properly extract tag version
-   Update gitignore
-   _(ci)_ Fix core package build
-   Split out dependencies and tests
-   _(ci)_ Update labels
-   _(ci)_ Fix labels
-   _(tests)_ Re-organise tests
-   Fix bad copy-paste in tests
-   Log exceptions from apply_args
-   Improve logging from apply_args
-   _(examples)_ Start examples overhaul
-   _(ci)_ Use new examples
-   Update protobuf examples
-   _(ci)_ Cancel ci on PRs
-   Add vscode settings and extensions
-   Add envrc
-   Replace yamlfix with yamlfmt
-   Remove deptry config
-   Support pre and post release tags
-   Fix typo

### Contributors

-   @JP-Ellis
-   @kevinrvaz

## [2.3.3] _2025-07-17_

### 🚀 Features

-   _(v3)_ Add will_respond_with for sync

### 🐛 Bug Fixes

-   _(v3)_ Avoid error if there's no mismatch type

### 📚 Documentation

-   _(examples)_ Add proto module documentation
-   Add protobuf and grpc links

### ⚙️ Miscellaneous Tasks

-   _(ci)_ Remove pre-commit cache restore key
-   Update biome
-   _(examples)_ Add protobuf example
-   Add version stub file
-   _(examples)_ Parametrize protobuf example
-   _(ci)_ Update runners
-   Split mypy calls

### Contributors

-   @JP-Ellis

## [2.3.2] _2025-05-05_

### 🚀 Features

-   _(v3)_ [**breaking**] Allow more flexible functional arguments
    > The signature of functional arguments must form a subset of the `MessageProducerArgs` and `StateHandlerArgs` typed dictionaries.

### 📚 Documentation

-   Replace commitizen with git cliff
-   Update blog post
-   Rename params -> parameters
-   _(example)_ Elaborate on state handler

### ⚙️ Miscellaneous Tasks

-   Update pre-commit hooks
-   Update committed configuration
-   Add taplo
-   _(ci)_ Update ubuntu runners
-   Reduce noise from taiki-e/install-action
-   _(ci)_ Upload test results to codecov
-   Add apply_arg utility
-   _(tests)_ Use consistent return value
-   _(test)_ Tweak type signature
-   _(examples)_ Fix state handler args

### Contributors

-   @JP-Ellis

## [2.3.1] _2025-01-22_

### 🐛 Bug Fixes

-   _(v3)_ Defer setting pact broker source

### Contributors

-   @JP-Ellis

## [2.3.0] _2024-12-30_

### 🚀 Features

-   _(v3)_ Add message relay and callback servers
-   _(v3)_ [**breaking**] Integrate message relay server
    > The provider name must be given as an argument of the `Verifier` constructor, instead of the first argument of the `set_info` method.
-   _(v3)_ [**breaking**] Add state handler server
    > `set_state` has been renamed to `state_handler`. If using a URL still, the `body` keyword argument is now a _required_ parameter.
-   _(v3)_ [**breaking**] Further simplify message interface
    > `message_handler` signature has been changed and expanded.

### 🎨 Styling

-   Lint
-   Lint

### 📚 Documentation

-   Fix minor typos
-   _(blog)_ Add functional arguments post

### ⚙️ Miscellaneous Tasks

-   Fix __url__
-   _(ci)_ Pin full version
-   Add yamlfix
-   Remove docker files and scripts
-   Update biome version
-   Rename master to main
-   _(ci)_ Pin typos to version
-   _(ci)_ Pin minor version of checkout action
-   Silence unset default fixture loop scope
-   _(ci)_ Replace pre-commit/action
-   _(v3)_ [**breaking**] Remove unnecessary underscores
    > The PactServer `__exit__` arguments no longer have leading underscores. This is typically handled by Python itself and therefore is unlikely to be a change for any user, unless the end user was calling the `__exit__` method explicitly _and_ using keyword arguments.
-   _(v3)_ [**breaking**] Make util module private
    > `pact.v3.util` has been renamed to `pact.v3._util` and is now private.
-   _(ci)_ Upgrade macos-12 to macos-13
-   _(c)_ Specify full action version
-   Add pytest-xdist
-   _(ci)_ Remove condition on examples
-   Update tests to use new message/state fns
-   Adapt examples to use function handlers
-   Move matchers test out of examples
-   Adjust tests based on new implementation
-   Remove dead code
-   Fix compatibility with 3.9, 3.10
-   Add pytest-rerunfailures
-   Fix windows compatibility
-   _(ci)_ Automerge renovate PRs

### Contributors

-   @JP-Ellis

## [2.2.2] _2024-10-10_

### 🚀 Features

-   _(examples)_ Add post and delete
-   Add matchable typevar
-   Add strftime to java date format converter
-   Add match aliases
-   Add uuid matcher
-   Add each key/value matchers
-   Add ArrayContainsMatcher
-   [**breaking**] Improve mismatch error
    > The `srv.mismatches` is changed from a `list[dict[str, Any]]` to a `list[Mismatch]`.
-   [**breaking**] Add Python 3.13, drop 3.8
    > Python 3.8 support dropped

### 🐛 Bug Fixes

-   Missing typing arguments
-   Incompatible override
-   Kwargs typing
-   Ensure matchers optionally use generators
-   _(examples)_ Do not overwrite pact file on every test
-   _(examples)_ Use wget for broker healthcheck
-   _(examples)_ Correct URL for healthcheck
-   _(examples)_ Do not publish postgres port
-   Typing annotations
-   ISO 8601 incompatibility

### 🚜 Refactor

-   Prefer `|` over Optional and Union
-   Rename matchers to match
-   Split types into stub
-   Matcher
-   Rename generators to generate
-   Generate module in style of match module
-   Create pact.v3.types module
-   Generators module
-   Match module

### 📚 Documentation

-   _(blog)_ Don't use footnote numbers
-   _(blog)_ Add async message blog post
-   Update example docs
-   Add matcher module preamble
-   Add module docstring

### ⚙️ Miscellaneous Tasks

-   _(ci)_ Use pypi trusted publishing
-   Fix typo in previous blog post
-   _(ci)_ Update docs on push to master
-   Regroup ruff in renovate
-   Add extra checks
-   Added v3 http interaction examples
-   _(ci)_ Add codecov
-   Refactor tests
-   Prefer ABC over ABCMeta
-   Re-organise match module
-   Split stdlib and 3rd party types
-   Silence a few mypy complaints
-   Add pyi to editor config
-   Add test for full ISO 8601 date
-   Minor improvements to match.matcher
-   Align generator with matcher
-   Remove MatchableT
-   Get test to run again
-   Add boolean alias
-   Fix compatibility with Python <= 3.9
-   Fix match tests
-   Remove unused generalisation
-   Use matchers in v3 examples
-   Use native Python datetime object
-   Adjust tests to use new Mismatch class
-   Disable wait
-   _(ci)_ Switch to uv fully
-   _(ci)_ Disable docs workflow on tags
-   _(ci)_ Tweak build conditions
-   Disable pypy builds

### Contributors

-   @JP-Ellis
-   @individual-it
-   @valkolovos
-   @amit828as

## [2.2.1] _2024-07-22_

### 🚀 Features

-   _(ffi)_ Upgrade ffi 0.4.21
-   _(v3)_ Add enum type aliases
-   _(v3)_ Improve exception types
-   _(v3)_ Remove deprecated messages iterator
-   _(v3)_ Implement message verification
-   _(v3)_ Add async message provider
-   _(ffi)_ Upgrade ffi to 0.4.22

### 🐛 Bug Fixes

-   _(ffi)_ Use `with_binary_body`

### 🚜 Refactor

-   _(v3)_ New interaction iterators
-   _(tests)_ Make `_add_body` a method of Body
-   _(tests)_ Move InteractionDefinition in own module

### 📚 Documentation

-   _(CONTRIBUTING.md)_ Update installation steps
-   Add additional code capabilities
-   Add blog post about rust ffi
-   _(ffi)_ Properly document exceptions
-   Minor refinements
-   _(example)_ Clarify purpose of fs interface

### ⚙️ Miscellaneous Tasks

-   Group renovate updates
-   Use uv to install packages
-   _(v3)_ Re-export Pact and Verifier at root
-   _(ffi)_ Disable private usage lint
-   _(ffi)_ Implement AsynchronousMessage
-   _(ffi)_ Implement Generator
-   _(ffi)_ Implement MatchingRule
-   _(ffi)_ Remove old message and message handle
-   _(ffi)_ Implement MessageContents
-   _(ffi)_ Implement MessageMetadataPair and Iterator
-   _(ffi)_ Implement ProviderState and related
-   _(ffi)_ Implement SynchronousHttp
-   _(ffi)_ Implement SynchronousMessage
-   _(ffi)_ Bump links to 0.4.21
-   _(tests)_ Implement v3/v4 consumer message compatibility suite
-   _(examples)_ Add v3 message consumer examples
-   Update GitHub templates
-   _(examples)_ Add asynchronous message
-   _(tests)_ Replace stderr with logger
-   _(tests)_ Increase message shown by `truncate`
-   Minor typing fix
-   _(tests)_ Significant refactor of InteractionDefinition
-   _(tests)_ Add v4 message provider compatibility suite
-   _(tests)_ Skip windows tests
-   _(ci)_ Disable windows arm wheels

### � Other

-   Fix macos-latest
-   Narrow when docs are built and published

### Contributors

-   @JP-Ellis
-   @valkolovos
-   @qmg-drettie

## [2.2.0] _2024-04-11_

### 🚀 Features

-   _(v3)_ Add verifier class
-   _(v3)_ Add verbose mismatches
-   Upgrade FFI to 0.4.19

### 🐛 Bug Fixes

-   Delay pytest 8.1
-   _(v3)_ Allow optional publish options
-   _(v3)_ Strip embedded user/password from urls

### 🚜 Refactor

-   _(tests)_ Move parse_headers/matching_rules out of class
-   Remove relative imports

### 📚 Documentation

-   Setup mkdocs
-   Update README
-   Rework mkdocs-gen-files scripts
-   Ignore private python modules
-   Overhaul readme
-   Update v3 docs
-   Fix links to docs/
-   Add social image support
-   Add blog post about v2.2

### ⚙️ Miscellaneous Tasks

-   _(ci)_ Remove cirrus
-   _(ffi)_ Implement verifier handle
-   _(v3)_ Add basic verifier tests
-   Unskip tests
-   Fix missed s/test/devel-test/
-   _(v3)_ Improve body representation
-   _(test)_ Improve test logging
-   _(tests)_ Update log formatting
-   _(test)_ Add state to interaction definition
-   _(test)_ Adapt InteractionDefinition for provider
-   _(test)_ Add serialize function
-   _(test)_ Add provider utilities
-   _(tests)_ Add v1 provider compatibility suite
-   _(tests)_ Fixes for lower python versions
-   _(tests)_ Re-enable warning check
-   _(tests)_ Improve logging from provider
-   _(test)_ Strip authentication from url
-   _(tests)_ Use long-lived pact broker
-   _(test)_ Apply a temporary diff to compatibility suite
-   _(test)_ Fix misspelling in step name
-   _(tests)_ Improve logging
-   _(tests)_ Allow multiple states with parameters
-   _(tests)_ Implement http provider compatibility suite
-   _(tests)_ Fix compatibility with py38
-   _(docs)_ Update emoji indices/generators
-   _(docs)_ Fix typos
-   _(docs)_ Enforce fenced code blocks
-   _(docs)_ Minor fixes in examples/
-   Remove redundant __all__
-   _(docs)_ Update examples/readme.md
-   _(ci)_ Update environment variables
-   _(docs)_ Only publish from master
-   _(test)_ Disable failing tests on windows

### Contributors

-   @JP-Ellis
-   @JosephBJoyce

## [2.1.3] _2024-03-07_

### 🐛 Bug Fixes

-   Avoid wheel bloat

### 📚 Documentation

-   Fix repository link typo
-   Fix links to `CONTRIBUTING.md`

### ⚙️ Miscellaneous Tasks

-   _(ci)_ Fix pypy before-build
-   _(ci)_ Pin os to older versions
-   _(ci)_ Set osx deployment target
-   _(ci)_ Replace hatch clean with rm
-   _(ci)_ Update concurrency group
-   _(ci)_ Adapt before-build for windows

### Contributors

-   @JP-Ellis

## [2.1.2] _2024-03-05_

### 🚀 Features

-   _(v3)_ Add v3.ffi module
-   _(v3)_ Implement pact class
-   _(v3)_ Implement interaction methods
-   _(ffi)_ Add OwnedString class
-   _(v3)_ Implement Pact Handle methods
-   _(v3)_ Add mock server mismatches
-   _(v3)_ Implement server log methods
-   Add python 3.12 support
-   _(v3)_ Add with_matching_rules
-   Determine version from vcs
-   _(v3)_ Upgrade ffi to 0.4.18
-   _(v3)_ Add specification attribute to pacts
-   Add support for musllinux_aarch64

### 🐛 Bug Fixes

-   _(ci)_ Add missing environment
-   _(test)_ Ignore internal deprecation warnings
-   _(v3)_ Unconventional __repr__ implementation
-   _(v3)_ Add __next__ implementation
-   _(example)_ Unknown action
-   _(example)_ Publish_verification_results typo
-   _(example)_ Publish message pact
-   _(v3)_ Rename `with_binary_file`
-   _(v3)_ Incorrect arg order
-   Clean pact interactions on exception

### 🚜 Refactor

-   _(v3)_ Split interactions into modules

### 🎨 Styling

-   Fix pre-commit lints
-   [**breaking**] Refactor constants
    > The public functions within the constants module have been removed. If you previously used them, please make use of the constants. For example, instead of `pact.constants.broker_client_exe()` use `pact.constants.BROKER_CLIENT_PATH` instead.

### 📚 Documentation

-   _(v3)_ Update ffi documentation
-   _(readme)_ Fix links to examples
-   Add git submodule init
-   Fix typos

### ⚙️ Miscellaneous Tasks

-   Add future deprecation warnings
-   _(ci)_ Disable on draft pull requests
-   _(ci)_ Separate concurrency groups for builds
-   Fix hatch test scripts
-   _(test)_ Add pytest options in root
-   _(build)_ Update packaging to build ffi
-   _(tests)_ Add ruff.toml for tests directory
-   _(ci)_ Update build targets
-   _(v3)_ Create ffi.py
-   _(tests)_ Remove empty file
-   _(v3)_ Add str and repr to enums
-   _(test)_ Move pytest cli args definition
-   Add label sync
-   _(test)_ Automatically generated xml coverage
-   Enable lints fully
-   _(pre-commit)_ Add mypy
-   _(ffi)_ Add typing
-   _(labels)_ Fix incorrect label alias
-   Exclude python 3.12
-   Fix wheel builds
-   _(ci)_ Revise pypi publishing
-   _(tests)_ Reduce log verbosity
-   Fix ruff lints
-   _(tests)_ Add compatibility suite as submodule
-   _(ruff)_ Disable TD002
-   Allow None content type
-   _(tests)_ Implement consumer v1 feature
-   _(ci)_ Checkout submodules
-   _(ci)_ Fix examples testing
-   _(ci)_ Clone submodules in Cirrus
-   _(tests)_ Automatic submodule init
-   Fix lints
-   Update submodule
-   _(ci)_ Set hatch to be verbose
-   _(ci)_ Add test conclusion step
-   _(ci)_ Breaking changes with for artifacts
-   _(ci)_ Re-enable pypy builds on Windows
-   _(dev)_ Replace black with ruff
-   _(dev)_ Add markdownlint pre-commit
-   _(ci)_ Fix pypy linux builds
-   _(test/v3)_ Move bdd steps into shared module
-   _(test/v3)_ Add v2 consumer compatibility suite
-   _(tests)_ Add v3 consumer compatibility suite
-   Update metadata
-   _(tests)_ Move the_pact_file_for_the_test_is_generated to share util
-   _(tests)_ Add v4 http consumer compatibility suite
-   _(ci)_ Speed up wheels building on prs
-   _(ci)_ Add caching
-   Migrate from flat to src layout
-   _(ci)_ Automate release process
-   _(v3)_ Add warning on pact.v3 import
-   _(ci)_ Remove check of wheels
-   _(ci)_ Speed up build pipeline
-   _(ci)_ Another build pipeline fix
-   _(ci)_ Typo

### � Other

-   Add g++ to cirrus linux image

### Contributors

-   @JP-Ellis
-   @YOU54F
-   @dryobates
-   @filipsnastins
-   @neringaalt

## [2.1.0] _2023-10-03_

### 🚀 Features

-   _(example)_ Simplify docker-compose
-   Bump pact standalone to 2.0.7

### 🐛 Bug Fixes

-   _(github)_ Fix typo in template
-   _(ci)_ Pypi publish

### 🎨 Styling

-   Add pre-commit hooks and editorconfig

### 📚 Documentation

-   Rewrite contributing.md
-   Add issue and pr templates
-   Incorporate suggestions from @YOU54F

### ⚙️ Miscellaneous Tasks

-   Add pact-foundation triage automation
-   Update pre-commit config
-   [**breaking**] Migrate to pyproject.toml and hatch
    > Drop support for Python 3.6 and 3.7
-   _(ci)_ Migrate cicd to hatch
-   _(example)_ Migrate consumer example
-   _(example)_ Migrate fastapi provider example
-   _(example)_ Migrate flask provider example
-   _(example)_ Update readme
-   _(example)_ Migrate message pact example
-   _(ci)_ Split tests examples and lints
-   _(example)_ Avoid changing python path
-   Address pr comments
-   _(gitignore)_ Update from upstream templates
-   V2.1.0

### Contributors

-   @JP-Ellis
-   @mefellows

## [2.0.1] _2023-07-26_

### 🚀 Features

-   Update standalone to 2.0.3

### ⚙️ Miscellaneous Tasks

-   Update MANIFEST file to note 2.0.2 standalone
-   _(examples)_ Update docker setup for non linux os
-   Releasing version 2.0.1

### Contributors

-   @YOU54F

## [2.0.0] _2023-07-10_

### 🚀 Features

-   Describe classifiers and python version for pypi package
-   _(test)_ Add docker images for Python 3.9-3.11 for testing purposes
-   Add matchers for ISO 8601 date format
-   Support arm64 osx/linux
-   Support x86 and x86_64 windows
-   Use pact-ruby-standalone 2.0.0 release

### 🐛 Bug Fixes

-   Actualize doc on how to make contributions
-   Remove dead code
-   Fix cors parameter not doing anything

### 🎨 Styling

-   Add missing newline/linefeed

### 📚 Documentation

-   Add Python 3.11 to CONTRIBUTING.md
-   Fix link for GitHub badge
-   Fix instruction to build python 3.11 image
-   Paraphrase the instructions for running the tests
-   Rephrase the instructions for running the tests
-   Reformat releasing documentation

### 🧪 Testing

-   V2.0.1 (pact-2.0.1) - pact-ruby-standalone

### ⚙️ Miscellaneous Tasks

-   Releasing version 1.7.0
-   Do not add merge commits to the change log
-   _(docs)_ Update provider verifier options table
-   _(docs)_ Correct table
-   _(docs)_ Improve table alignment and abs links
-   Update to 2.0.2 pact-ruby-standalone
-   Releasing version 2.0.0

### � Other

-   Correct links in contributing manual
-   Improve commit messages guide
-   Add python 3.11 to test matrix
-   Use compatible dependency versions for Python 3.6
-   Use a single Dockerfile, providing args for the Python version instead of multiple files
-   Test arm64 on cirrus-ci / test win/osx on gh
-   Skip 3.6 python arm64 failing in cirrus, passing locally with cirrus run
-   _(deps)_ Bump flask from 2.2.2 to 2.2.5 in /examples/message
-   _(deps)_ Bump flask from 2.2.2 to 2.2.5 in /examples/flask_provider
-   _(deps-dev)_ Bump flask from 2.2.2 to 2.2.5

### Contributors

-   @YOU54F
-   @sergeyklay
-   @Lukas-dev-threads
-   @elliottmurray
-   @mikegeeves

## [1.7.0] _2023-02-19_

### 🚀 Features

-   Enhance provider states for pact-message (#322)

### 🐛 Bug Fixes

-   Requirements_dev.txt to reduce vulnerabilities (#317)
-   Setup security issue (#318)

### ⚙️ Miscellaneous Tasks

-   Add workflow to create a jira issue for pactflow team when smartbear-supported label added to github issue
-   /s/Pactflow/PactFlow
-   Releasing version 1.7.0

### Contributors

-   @elliottmurray
-   @YOU54F
-   @nsfrias
-   @bethesque
-   @mefellows

## [1.6.0] _2022-09-11_

### 🚀 Features

-   Support publish pact with branch (#300)
-   Support verify with branch (#302)

### 📚 Documentation

-   Update docs to reflect usage for native Python

### ⚙️ Miscellaneous Tasks

-   _(test)_ Fix consumer message test (#301)
-   Releasing version 1.6.0

### � Other

-   Correct download logic when installing. Add a helper target to setup a pyenv via make (#297)

### Contributors

-   @elliottmurray
-   @YOU54F
-   @B3nnyL
-   @mikegeeves
-   @jnfang

## [1.5.2] _2022-03-21_

### ⚙️ Miscellaneous Tasks

-   Update PACT_STANDALONE_VERSION to 1.88.83
-   Releasing version 1.5.2

### Contributors

-   @elliottmurray
-   @YOU54F

## [1.5.1] _2022-03-10_

### 🚀 Features

-   Message_pact -> with_metadata() updated to accept term (#289)

### 📚 Documentation

-   _(examples-consumer)_ Add pip install requirements to the consumer… (#291)

### 🧪 Testing

-   _(examples)_ Move shared fixtures to a common folder so they can b… (#280)

### ⚙️ Miscellaneous Tasks

-   Releasing version 1.5.1

### Contributors

-   @elliottmurray
-   @sunsathish88
-   @mikegeeves

## [1.5.0] _2022-02-05_

### 🚀 Features

-   No include pending (#284)

### ⚙️ Miscellaneous Tasks

-   Releasing version 1.5.0

### � Other

-   Python36-support-removed (#283)

### Contributors

-   @elliottmurray
-   @abgora
-   @mikegeeves

## [1.4.6] _2022-01-03_

### 🚀 Features

-   _(matcher)_ Allow bytes type in from_term function (#281)

### 🐛 Bug Fixes

-   _(consumer)_ Ensure a description is provided for all interactions

### 📚 Documentation

-   Docs/examples (#273)

### 🧪 Testing

-   _(examples-fastapi)_ Tidy FastAPI example, making consistent with Flask (#274)

### ⚙️ Miscellaneous Tasks

-   Flake8 config to ignore direnv
-   Releasing version 1.4.6

### Contributors

-   @elliottmurray
-   @joshua-badger
-   @mikegeeves

## [1.4.5] _2021-10-11_

### 🐛 Bug Fixes

-   Update standalone to 1.88.77 to fix Let's Encrypt CA issue

### ⚙️ Miscellaneous Tasks

-   Releasing version 1.4.5

### Contributors

-   @mefellows

## [1.4.4] _2021-10-02_

### 🐛 Bug Fixes

-   _(ruby)_ Update ruby standalone to support disabling SSL verification via an environment variable

### ⚙️ Miscellaneous Tasks

-   Releasing version 1.4.4

### Contributors

-   @mefellows
-   @m-aciek

## [1.4.3] _2021-09-05_

### 🚀 Features

-   Added support for message provider using pact broker (#257)

### ⚙️ Miscellaneous Tasks

-   Releasing version 1.4.3

### Contributors

-   @elliottmurray
-   @pulphix

## [1.4.2] _2021-08-22_

### ⚙️ Miscellaneous Tasks

-   Bundle Ruby standalones into dist artifact. (#256)
-   Releasing version 1.4.2

### Contributors

-   @elliottmurray
-   @taj-p

## [1.4.1] _2021-08-17_

### 🐛 Bug Fixes

-   Make uvicorn versions over 0.14

### ⚙️ Miscellaneous Tasks

-   Releasing version 1.4.1

### Contributors

-   @elliottmurray

## [1.4.0] _2021-08-07_

### 🚀 Features

-   Added support for message provider (#251)

### 🐛 Bug Fixes

-   Issue originating from snyk with requests and urllib

### ⚙️ Miscellaneous Tasks

-   _(snyk)_ Update fastapi
-   Releasing version 1.4.0

### Contributors

-   @elliottmurray
-   @pulphix

## [1.3.9] _2021-05-13_

### 🐛 Bug Fixes

-   Change default from empty string to empty list (#235)

### ⚙️ Miscellaneous Tasks

-   _(ruby)_ Update ruby standalen
-   Releasing version 1.3.9

### Contributors

-   @elliottmurray
-   @tephe

## [1.3.8] _2021-05-01_

### 🐛 Bug Fixes

-   Fix datetime serialization issues in Format

### 📚 Documentation

-   Example uses date matcher

### ⚙️ Miscellaneous Tasks

-   Releasing version 1.3.8

### Contributors

-   @elliottmurray
-   @DawoudSheraz

## [1.3.7] _2021-04-24_

### 🐛 Bug Fixes

-   _(broker)_ Token added to verify steps

### ⚙️ Miscellaneous Tasks

-   Releasing version 1.3.7

### Contributors

-   @elliottmurray

## [1.3.6] _2021-04-20_

### 🐛 Bug Fixes

-   Docker/py36.Dockerfile to reduce vulnerabilities
-   Docker/py38.Dockerfile to reduce vulnerabilities
-   Docker/py37.Dockerfile to reduce vulnerabilities
-   Publish verification results was wrong (#222)

### ⚙️ Miscellaneous Tasks

-   Releasing version 1.3.6

### � Other

-   Revert docker36 back

### Contributors

-   @elliottmurray
-   @snyk-bot

## [1.3.5] _2021-03-28_

### 🐛 Bug Fixes

-   _(publish)_ Fixing the fix. Pact Python api uses only publish_version and ensures it follows that

### ⚙️ Miscellaneous Tasks

-   Releasing version 1.3.5

### Contributors

-   @elliottmurray

## [1.3.4] _2021-03-27_

### 🐛 Bug Fixes

-   Verifier should now publish

### ⚙️ Miscellaneous Tasks

-   Releasing version 1.3.4

### Contributors

-   @elliottmurray

## [1.3.3] _2021-03-25_

### 🐛 Bug Fixes

-   Pass pact_dir to publish()

### ⚙️ Miscellaneous Tasks

-   Releasing version 1.3.3

### Contributors

-   @elliottmurray
-   @

## [1.3.2] _2021-03-21_

### 🐛 Bug Fixes

-   Ensure path is passed to broker and allow running from root rather than test file
-   Remove pacts from examples

### ⚙️ Miscellaneous Tasks

-   Move from nose to pytests as we are now 3.6+
-   Update ci stuff
-   More clean up
-   Wip on using test containers on examples
-   Spiking testcontainers
-   Added some docs about how to use the e2e example
-   Releasing version 1.3.2

### Contributors

-   @elliottmurray

## [1.3.1] _2021-02-27_

### 🐛 Bug Fixes

-   Introduced and renamed specification version

### ⚙️ Miscellaneous Tasks

-   Releasing version 1.3.1

### Contributors

-   @elliottmurray

## [1.3.0] _2021-01-26_

### 🚀 Features

-   Initial interface
-   Add MessageConsumer
-   Single message flow
-   Create basic tests for single pact message
-   Update MessageConsumer and tests
-   Add constants test
-   Add pact-message integration
-   Add pact-message integration test
-   Add more test
-   Update message pact tests
-   Change dummy handler to a message handler
-   Update handler to handle error exceptions
-   Move publish function to broker class
-   Update message handler to be independent of pact
-   Address PR comments

### 🐛 Bug Fixes

-   Send to cli pact_files with the pact_dir in their path
-   Add e2e example test into ci back in
-   Remove publish fn for now
-   Linting
-   Add missing conftest
-   Try different way to mock
-   Flake8 warning
-   Revert changes to quotes
-   Improve test coverage
-   Few more tests to improve coverage

### 📚 Documentation

-   Add readme for message consumer
-   Update readme

### 🧪 Testing

-   Create external dummy handler in test
-   Update message handler condition based on content
-   Remove mock and check generated json file
-   Consider publish to broker with no pact_dir argument

### ⚙️ Miscellaneous Tasks

-   Remove python35 and 34 and add 39
-   Fix bad merge
-   Add missing files in src
-   Add generate_pact_test
-   Remove log_dir, refactor test
-   Flake8 revert
-   Remove test param for provider
-   Flake8, clean up deadcode
-   Pydocstyle
-   Add missing import
-   Releasing version 1.3.0

### � Other

-   Pr not triggering workflow

### Contributors

-   @elliottmurray
-   @williaminfante
-   @tuan-pham
-   @cdambo

## [1.2.11] _2020-12-29_

### 🐛 Bug Fixes

-   Not creating wheel

### ⚙️ Miscellaneous Tasks

-   Releasing version 1.2.11

### Contributors

-   @elliottmurray

## [1.2.10] _2020-12-19_

### 📚 Documentation

-   Fix small typo in `with_request` doc string
-   _(example)_ Created example and have relative imports kinda working. Provider not working as it cant find one of our urls
-   Typo in pact-verifier help string: PUT -> POST for --provider-states-setup-url
-   Added badge to README

### ⚙️ Miscellaneous Tasks

-   _(upgrade)_ Upgrade python version to 3.8
-   Wqshell script to run flask in examples
-   Added run test to travis
-   Releasing version 1.2.10

### � Other

-   _(github actions)_ Added Github Actions configuration for build and test
-   Removed Travis CI configuration
-   Add publishing actions

### Contributors

-   @elliottmurray
-   @matthewbalvanz-wf
-   @noelslice
-   @hstoebel

## [1.2.9] _2020-10-19_

### 🚀 Features

-   _(verifier)_ Allow setting consumer_version_selectors on Verifier

### 🐛 Bug Fixes

-   Fix flaky tests using OrderedDict

### 🎨 Styling

-   Fix linting issues
-   Fix one more linting issue

### ⚙️ Miscellaneous Tasks

-   Releasing version 1.2.9

### Contributors

-   @elliottmurray
-   @thatguysimon

## [1.2.8] _2020-10-18_

### 🚀 Features

-   _(verifier)_ Support include-wip-pacts-since in CLI

### 🐛 Bug Fixes

-   Fix command building bug

### 🚜 Refactor

-   Extract input validation in call_verify out into a dedicated method

### 🎨 Styling

-   Fix linting

### 📚 Documentation

-   _(examples)_ Tweak to readme
-   _(examples)_ Changed provider example to use atexit

### ⚙️ Miscellaneous Tasks

-   Releasing version 1.2.8

### Contributors

-   @elliottmurray
-   @thatguysimon

## [1.2.7] _2020-10-09_

### 🐛 Bug Fixes

-   _(verifier)_ Headers not propagated properly

### 📚 Documentation

-   _(examples)_ Removed manual publish to broker

### ⚙️ Miscellaneous Tasks

-   Releasing version 1.2.7

### Contributors

-   @elliottmurray

## [1.2.6] _2020-09-11_

### 🚀 Features

-   _(verifier)_ Allow to use unauthenticated brokers

### ⚙️ Miscellaneous Tasks

-   Releasing version 1.2.6

### Contributors

-   @elliottmurray
-   @copalco

## [1.2.5] _2020-09-10_

### 🚀 Features

-   _(verifier)_ Add enable_pending argument handling in verify wrapper
-   _(verifier)_ Pass enable_pending flag in Verifier's methods
-   _(verifier)_ Support --enable-pending flag in CLI

### 🐛 Bug Fixes

-   _(verifier)_ Remove superfluous option from verify CLI command
-   _(verifier)_ Remove superfluous verbose mentions

### 🚜 Refactor

-   _(verifier)_ Add enable_pending to signature of verify methods

### 🧪 Testing

-   Bump mock to 3.0.5

### ⚙️ Miscellaneous Tasks

-   Releasing version 1.2.5

### � Other

-   _(pre-commit)_ Add commitizen to pre-commit configuration

### Contributors

-   @elliottmurray
-   @
-   @m-aciek

## [1.2.4] _2020-08-27_

### 🚀 Features

-   _(cli)_ Add consumer-version-selector option

### 📚 Documentation

-   Update README.md with relevant option documentation
-   _(cli)_ Improve cli help grammar

### ⚙️ Miscellaneous Tasks

-   Releasing version 1.2.4

### Contributors

-   @elliottmurray
-   @alecgerona

## [1.2.3] _2020-08-26_

### 🚀 Features

-   Update standalone to 1.88.3

### ⚙️ Miscellaneous Tasks

-   Script now uses gh over hub
-   Release script updates version automatically now
-   Fix release script
-   Releasing version 1.2.3

### Contributors

-   @elliottmurray

## [1.2.2] _2020-08-24_

### 🚀 Features

-   Added env vars for broker verify

### 📚 Documentation

-   Https svg

### ⚙️ Miscellaneous Tasks

-   Releasing version 1.2.2

### Contributors

-   @elliottmurray

## [1.2.1] _2020-08-08_

### 🐛 Bug Fixes

-   Custom headers had a typo

### 📚 Documentation

-   Example code verifier
-   Merged 2 examples

### ⚙️ Miscellaneous Tasks

-   Releasing version 1.2.1

### Contributors

-   @elliottmurray

## [1.2.0] _2020-07-24_

### 🚀 Features

-   Create beta verifier class and api
-   Fixing up tests and examples and code for provider class

### 🐛 Bug Fixes

-   Change to head from master

### 📚 Documentation

-   Update links for rendering page correctly in docs.pact.io
-   Update stackoverflow link
-   Contributing md updated for commit messages

### ⚙️ Miscellaneous Tasks

-   Add workflow to trigger pact docs update when markdown files change
-   Added semantic yml for git messages
-   Releasing version 1.2.0
-   Releasing with fix version v1.2.0

### � Other

-   Add check for commit messages
-   Tweak to regex
-   Temporary fix for testing purposes of messages:
-   Remove commit message as it is breaking releases

### Contributors

-   @elliottmurray
-   @bethesque

## [1.1.0] _2020-06-25_

### 🚀 Features

-   Update standalone to 1.86.0

### ⚙️ Miscellaneous Tasks

-   Removed some files and moved a few things around

### Contributors

-   @elliottmurray
-   @bethesque
-   @hstoebel

## [0.22.0] _2020-05-11_

### 🚀 Features

-   Update standalone to 1.84.0

### 📚 Documentation

-   Update RELEASING.md

### ⚙️ Miscellaneous Tasks

-   Add script to create a PR to update the pact-ruby-standalone version

### Contributors

-   @pyasi
-   @elliottmurray
-   @bethesque
-   @

## [0.20.0] _2020-01-16_

### 🚀 Features

-   Support using environment variables to set pact broker configuration
-   Update to pact-ruby-standalone-1.79.0

### Contributors

-   @bethesque
-   @matthewbalvanz-wf
-   @elliottmurray
-   @mikahjc
-   @mefellows
-   @dlmiddlecote
-   @ejrb

## [0.18.0] _2018-08-21_

### ⚙️ Miscellaneous Tasks

-   _(docs)_ Update contact information

### Contributors

-   @matthewbalvanz-wf
-   @mefellows

## [0.13.0] _2018-01-20_

### 📚 Documentation

-   Remove reference to v3 pact in provider-states-setup-url

### Contributors

-   @matthewbalvanz-wf
-   @bethesque
-   @

## [0.1.0] _2017-04-07_

### Contributors

-   @jslvtr
-   @matthewbalvanz-wf
-   @mefellows

<!-- generated by git-cliff on 2025-12-10-->
