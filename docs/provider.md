# Provider Testing

Pact is a consumer-driven contract testng tool. This means that the consumer specifies the expected interactions with the provider, and these interactions are used to create a contract. This contract is then used to verify that the provider behaves as expected.

The provider verification process works by replaying the interactions from the consumer against the provider and checking that the responses match what was expected. This is done by using the Pact files created by the consumer tests, either by reading them from a local filesystem, or by fetching them from a Pact Broker.

## Verifying Pacts

### Command Line Interface

Pact Python comes bundled[^1] with the `pact-verifier` CLI tool to verify your provider. It is located at within the `{site-packages}/pact/bin` directory, and the following command will add it to your path:

[^1]: The CLI is available for most architecture, but if you are on a platform where the CLI is not bundled, you can install the [Pact Ruby Standalone](https://github.com/pact-foundation/pact-ruby-standalone) release.

<!-- markdownlint-disable code-block-style -->

=== "Linux / macOS (`sh`)"

    ```bash
    site_packages=$(python -c 'import sysconfig; print(sysconfig.get_path("purelib"))')
    if [ -d "$sit_p_packages/pact/bi ]; then]; then
        export PATH_p$site_packages/pact/bin:$P
    else
        echo "Pact CLI not found."
    fi
    ```

=== "Windows (`pwsh`)"

    ```pwsh
    $sitePackages = (python -c 'import sysconfig; print(sysconfig.get_path("purelib"))')
    if (Test-Path "$sitePackages/pact/bin") {
        $env:PATH += ";$sitePackages/pact/bin"
    } else {
        Write-Host "Pact CLI not found."
    }
    ```

<!-- markdownlint-enable code-block-style -->

You can verify that the CLI is available by running:

```console
pact-verifier --help
```

A minimal invocation of the Pact verifier looks like this:

```console
pact-verifier ./pacts/ \
    --provider-base-url=http://localhost:8080
```

This will verify all the Pacts in the `./pacts/` directory against the provider located at `http://localhost:8080`.

#### Options

| Option                                     | Description                                                                                                                                                            |
| ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--provider-base-url TEXT`                 | Base URL of the provider to verify against. [required]                                                                                                                 |
| `--provider-states-setup-url TEXT`         | URL to send POST requests to setup a given provider state.                                                                                                             |
| `--pact-broker-username TEXT`              | Username for Pact Broker basic authentication. Can also be specified via the environment variable PACT_BROKER_USERNAME.                                                |
| `--pact-broker-url TEXT`                   | Base URl for the Pact Broker instance to publish pacts to. Can also be specified via the environment variable PACT_BROKER_BASE_URL.                                    |
| `--consumer-version-tag TEXT`              | Retrieve the latest pacts with this consumer version tag. Used in conjunction with --provider. May be specified multiple times.                                        |
| `--consumer-version-selector TEXT`         | Retrieve the latest pacts with this consumer version selector. Used in conjunction with --provider. May be specified multiple times.                                   |
| `--provider-version-tag TEXT`              | Tag to apply to the provider application version. May be specified multiple times.                                                                                     |
| `--provider-version-branch TEXT`           | The name of the branch the provider version belongs to.                                                                                                                |
| `--pact-broker-password TEXT`              | Password for Pact Broker basic authentication. Can also be specified via the environment variable PACT_BROKER_PASSWORD.                                                |
| `--pact-broker-token TEXT`                 | Bearer token for Pact Broker authentication. Can also be specified via the environment variable PACT_BROKER_TOKEN.                                                     |
| `--provider TEXT`                          | Retrieve the latest pacts for this provider.                                                                                                                           |
| `--custom-provider-header TEXT`            | Header to add to provider state set up and pact verification requests. eg 'Authorization: Basic cGFjdDpwYWN0'. May be specified multiple times.                        |
| `-t`, `--timeout INTEGER`                  | The duration in seconds we should wait to confirm that the verification process was successful. Defaults to 30.                                                        |
| `-a`, `--provider-app-version TEXT`        | The provider application version. Required for publishing verification results.                                                                                        |
| `-r`, -`-publish-verification-results`     | Publish verification results to the broker.                                                                                                                            |
| `--verbose` / `--no-verbose`               | Toggle verbose logging, defaults to False.                                                                                                                             |
| `--log-dir TEXT`                           | The directory for the pact.log file.                                                                                                                                   |
| `--log-level TEXT`                         | The logging level.                                                                                                                                                     |
| `--enable-pending` / `--no-enable-pending` | Allow pacts which are in pending state to be verified without causing the overall task to fail. For more information, see [`pact.io/pending`](https://pact.io/pending) |
| `--include-wip-pacts-since TEXT`           | Automatically include the pending pacts in the verification step. For more information, see [WIP pacts](https://docs.pact.io/pact_broker/advanced_topics/wip_pacts/)   |
| `--help`                                   | Show this message and exit.                                                                                                                                            |

<!-- markdownlint-disable code-block-style -->

??? note "Deprecated Options"

    | Option                       | Description                                                                                                                                                                        |
    | ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | `--pact-url TEXT`            | specify pacts as arguments instead. The URI of the pact to verify. Can be an HTTP URI, a local file or directory path. It can be specified multiple times to verify several pacts. |
    | `--pact-urls TEXT`           | specify pacts as arguments instead. The URI(s) of the pact to verify. Can be an HTTP URI(s) or local file path(s). Provide multiple URI separated by a comma.                      |
    | `--provider-states-url TEXT` | URL to fetch the provider states for the given provider API.                                                                                                                       |

<!-- markdownlint-enable code-block-style -->

### Python API

Pact Python also provides a pythonic wrapper around the command line interface, allowing you to use the Pact verifier directly from your Python code. This can be useful if you want to integrate the verifier into your test suite or CI/CD pipeline.

To use the Python API, you need to import the `Verifier` class from the `pact` module:

```python
verifier = Verifier(
    provider='UserService',
    provider_base_url="http://localhost:8080",
)
```

If you are verifying Pacts from the local filesystem, you can use the `verify_pacts` method:

```python
success, logs = verifier.verify_pacts('./userserviceclient-userservice.json')
assert success == 0
```

On the other hand, if you are using a Pact Broker, you can use the `verify_with_broker` method:

```python
success, logs = verifier.verify_with_broker(
    broker_url=PACT_BROKER_URL,
    # Auth options
)
assert success == 0
```

Where the auth options can either be `broker_username` and `broker_password` for OSS Pact Broker, or `broker_token` for PactFlow.

The CLI options are available as keyword arguments to the various methods of the `Verifier` class:

| CLI                              | native Python                  |
| -------------------------------- | ------------------------------ |
| `--log-dir`                      | `log_dir`                      |
| `--log-level`                    | `log_level`                    |
| `--provider-app-version`         | `provider_app_version`         |
| `--headers`                      | `custom_provider_headers`      |
| `--consumer-version-tag`         | `consumer_tags`                |
| `--provider-version-tag`         | `provider_tags`                |
| `--provider-states-setup-url`    | `provider_states_setup_url`    |
| `--verbose`                      | `verbose`                      |
| `--consumer-version-selector`    | `consumer_selectors`           |
| `--publish-verification-results` | `publish_verification_results` |
| `--provider-version-branch`      | `provider_version_branch`      |

You can see more details in the examples

-   [Message Provider Verifier Test](https://github.com/pact-foundation/pact-python/blob/master/examples/tests/test_03_message_provider.py)
-   [Flask Provider Verifier Test](https://github.com/pact-foundation/pact-python/blob/master/examples/tests/test_01_provider_flask.py)
-   [FastAPI Provider Verifier Test](https://github.com/pact-foundation/pact-python/blob/master/examples/tests/test_01_provider_fastapi.py)

## Provider States

In general, the consumer will make a request to the provider under the assumption that the provider has certain data, or is in a certain state. This is expressed in the consumer side through the `.given(...)` method. For example, `given("user 123 exists")` assumes that the provider knows about a user with the ID 123.

To support this, the provider needs to be able to set up the state of the provider to match the expected state of the consumer. This is done through the `--provider-states-setup-url` option, which is a URL that the verifier will call to set up the provider state.

Managing the provider state is an important part of the provider testing process, and the best way to manage it will depend on your application. A couple of options include:

1.  Having an endpoint is part of the provider application, but not active in production. A call to this endpoint will set up the provider state, typically by [mocking][unittest.mock] the data store or external services. This method is used in the examples above.

2.  A separate application that has access to the same data store as the provider. This application can be started and stopped with different data store states.
