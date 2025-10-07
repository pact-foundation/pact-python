# Migration Guide

> [!INFO]
>
> This document is best viewed on the [Pact Python docs site](https://pact-foundation.github.io/pact-python/MIGRATION/).

This document outlines the key changes and migration steps for users transitioning between major Pact Python versions. It focuses on breaking changes, new features, and best practices to ensure a smooth upgrade.

## Migrating from `2.x` to `3.x`

### Key Changes

-   Replaced the entire Pact CLI-based implementation with a brand new version leveraging the [core Pact FFI](https://github.com/pact-foundation/pact-reference) written in Rust.
    -   This will help ensure feature parity between different language implementations and improve performance and reliability. This also brings compatibility with the latest Pact Specification (v4).
-   The bundled CLI is now a separate package: [`pact-python-cli`](https://pypi.org/project/pact-python-cli/).
-   The programmatic API has been completely overhauled to be more Pythonic and easier to use. Legacy process calls and return code checks have been removed in favour of proper exception handling.
-   The old programmatic interface is available in the `pact.v2` module for backwards compatibility. This is deprecated, will not receive new features, and will be removed in a future release.

### Using the `pact.v2` Compatibility Module

For teams with larger codebases that need time to fully migrate to the new v3 API, a backwards compatibility module is provided at `pact.v2`. This module contains the same API as Pact Python v2.x and serves as an interim measure to assist gradual migration.

To use the v2 compatibility module, you must install pact-python with the `compat-v2` feature enabled:

```bash
pip install pact-python[compat-v2]
```

All existing `pact.*` imports need to be updated to use `pact.v2.*` instead. Here are some common examples:

```python
# Old v2.x imports
from pact import Consumer, Provider
from pact.matchers import Like, EachLike
from pact.verifier import Verifier

# New v3.x imports using the v2 compatibility module
from pact.v2 import Consumer, Provider
from pact.v2.matchers import Like, EachLike
from pact.v2.verifier import Verifier
```

Please note that this compatibility module is intended as a temporary solution. A full migration to the new v3 API is strongly recommended as soon as feasible. The compatibility module will only receive critical bug fixes and no new features.

Pact, by default, updates existing Pact contracts in place, so migrating consumer tests incrementally should be feasible. However, newer features (e.g., message pacts) will likely require a full migration, and mixed usage of v2 and v3 APIs is not officially supported.

### Consumer Changes

The v3 API introduces significant changes to how consumer tests are structured and written. The main changes simplify the API, making it more Pythonic and flexible.

#### Defining a Pact

The `Consumer` and `Provider` classes have been removed. Instead, a single `Pact` class is used to define the consumer-provider relationship:

```python title="v2"
from pact.v2 import Consumer, Provider

consumer = Consumer('my-web-front-end')
provider = Provider('my-backend-service')

pact = consumer.has_pact_with(provider, pact_dir='/path/to/pacts')
```

```python title="v3"
from pact import Pact

pact = Pact('my-web-front-end', 'my-backend-service')
```

#### Defining Interactions

The v3 interface favours method chaining and provides more granular control over request and response definitions.

```python title="v2"
(
    pact
    .given('user exists')
    .upon_receiving('a request for user data')
    .with_request(
        'GET',
        '/users/123',
        headers={'Accept': 'application/json'},
        query={'include': 'profile'}
    )
    .will_respond_with(
        200,
        headers={'Content-Type': 'application/json'},
        body={'id': 123, 'name': 'Alice'}
    )
)
```

```python title="v3"
(
    pact
    .upon_receiving('a request for user data')
    .given('user exists', id=123, name='Alice')  # (1)
    .with_request('GET', '/users/123')
    .with_header('Accept', 'application/json')
    .with_query_parameter('include', 'profile')
    .will_respond_with(200)
    .with_header('Content-Type', 'application/json')
    .with_body({'id': 123, 'name': 'Alice'}, content_type='application/json'))
```

1.  In v2, there was limited support for parameterizing provider states, and each state variation often required a separate definition. For example, `given("user Alice exists with id 123")` and `given("user Bob exists with id 456")` would be two distinct states, which would then need to be handled separately in the provider state setup.

    The new interface can now define a common descriptor that can be reused with different parameters: `.given("user exists", id=123, name='Alice')` and `.given("user exists", id=456, name='Bob')`. This approach reduces redundancy and makes it easier to manage provider states.

Some methods are shared across request and response definitions, such as `with_header()` and `with_body()`. Pact Python automatically applies them to the correct part of the interaction based on whether they are called before or after `will_respond_with()`. Alternatively, these methods accept an optional `part` argument to explicitly specify whether they apply to the request or response.

#### Running Tests

Pact Python v2 had two different ways to run consumer tests, both of which spawned a separate mock service process. The new v3 API provides a single, consistent way to run tests using the `serve()` method.

```python title="v2 - with context manager"
pact = Consumer("my-consumer").has_pact_with(
    Provider("my-provider"),
    host_name="localhost",
    port=1234,
)

# Context manager automatically calls setup() and verify()
with pact:
    response = requests.get(pact.uri + '/users/123')
# Pact file written automatically on exit
```

```python title="v2 - with manual service management"
pact = Consumer("my-consumer").has_pact_with(
    Provider("my-provider"),
    host_name="localhost",
    port=1234,
)

# Manually start the mock service
pact.start_service()
pact.setup()  # Configure interactions

# Make requests
response = requests.get(pact.uri + '/users/123')
# Assertions...

# Verify and stop
pact.verify()  # Writes pact file
pact.stop_service()
```

The new API entirely replaces both of these approaches with a single, consistent method:

```python title="v3"
pact = Pact("my-consumer", "my-provider")

with pact.serve() as srv:
    response = requests.get(f"{srv.url}/users/123")
```

The server host and port can be specified in `serve()` if needed, but by default, the server binds to `localhost` on a random available port. More details can be found in the [API reference][pact.pact.Pact.serve].

##### Writing Pact Files

Since the old v2 API executed a sub-process for the mock service, the Pact file was automatically written when the context manager exited or when `pact.verify()` was called. The new v3 API runs the mock service in-process, so the Pact file must be written explicitly using the `write_file()` method:

```python title="v2"
with pact:
    # tests...
# Pact file written automatically
```

```python title="v3"
pact = Pact('consumer', 'provider')
# Define interactions and run tests...
pact.write_file('/path/to/pacts')
```

#### Matchers

Support for matchers has been greatly expanded and improved in the v3 API. The older v2 classes defined a limited set of matchers, while the new API provides a more comprehensive and flexible approach.

```python title="v2"
from pact.v2.matchers import Like, EachLike, Regex, Term

# Usage:
Like({'id': 123})
EachLike({'item': 'value'})
Regex('hello world', r'^hello')
```

```python title="v3"
from pact import match

# Usage:
match.like({'id': 123})
match.each_like({'item': 'value'})
match.regex('hello world', r'^hello')
```

For a full list of available matchers and their usage, refer to the [API documentation][pact.match].

### Provider Changes

The provider verification API has been completely redesigned in v3 to provide a more intuitive and flexible interface. The old `Provider` and `Verifier` classes have been replaced by a single `Verifier` class with a fluent interface.

#### Creating a Verifier

```python title="v2"
from pact.v2 import Provider, Verifier

# Create separate Provider and Verifier instances
provider = Provider('my-provider')
verifier = Verifier(provider, 'http://localhost:8080')
```

```python title="v3"
from pact import Verifier

# Single Verifier instance with provider name
verifier = Verifier('my-provider')
```

The protocol specification is now done through the `add_transport` method, which allows for more flexible configuration and supports multiple transports if needed.

```python title="v2"
verifier = Verifier(provider, 'http://localhost:8080')
```

```python title="v3"
verifier = (
    Verifier('my-provider')
    .add_transport(url='http://localhost:8080')
    # Or more granular control:
    .add_transport(
        protocol='http',
        port=8080,
        path='/api/v1',
        scheme='https'
    )
)
```

#### Adding Pact Sources

Support for both local files and Pact Brokers is retained in v3, with the `verify_pacts` and `verify_with_broker` methods replaced by a more flexible source configuration. This allows multiple sources to be combined, and selectors to be applied.

<!-- markdownlint-disable code-block-style -->

=== "Local Files"

    ```python title="v2"
    success, logs = verifier.verify_pacts(
        './pacts/consumer1-provider.json',
        './pacts/consumer2-provider.json'
    )
    ```

    ```python title="v3"
    verifier = (
        Verifier('my-provider')
        # It can discover all Pact files in a directory
        .add_source('./pacts/')
        # Or read individual files
        .add_source('./pacts/specific-consumer.json')
    )
    ```

=== "Pact Broker"

    ```python title="v2"
    success, logs = verifier.verify_with_broker(
        broker_url='https://pact-broker.example.com',
        broker_username='username',
        broker_password='password'
    )
    ```

    ```python title="v3"
    verifier = (
        Verifier('my-provider')
        .broker_source(
            'https://pact-broker.example.com',
            username='username',
            password='password'
        )
    )

    # Or with selectors for more control
    broker_builder = (
        verifier
        .broker_source(
            'https://pact-broker.example.com',
            selector=True
        )
        .include_pending()
        .provider_branch('main')
        .consumer_tags('main', 'develop')
        .build()
    )
    ```

    The `selector=True` argument returns a [`BrokerSelectorBuilder`][pact.verifier.BrokerSelectorBuilder] instance, which provides methods to configure which pacts to fetch. The `build()` call finalizes the configuration and returns the `Verifier` instance which can then be further configured.

<!-- markdownlint-enable code-block-style -->

#### Provider State Handling

The old v2 API required the provider to expose an HTTP endpoint dedicated to handling provider states. This is still supported in v3, but there are now more flexible options, allowing Python functions (or mappings of state names to functions) to be used instead.

<!-- markdownlint-disable code-block-style -->

=== "URL-based State Handling"

    ```python title="v2"
    success, logs = verifier.verify_pacts(
        './pacts/consumer-provider.json',
        provider_states_setup_url='http://localhost:8080/_pact/provider_states'
    )
    ```

    ```python title="v3"
    # Option 1: URL-based (similar to v2)
    verifier = (
        Verifier('my-provider')
        .add_transport(url='http://localhost:8080')
        .state_handler(
            'http://localhost:8080/_pact/provider_states',
            body=True  # (1)
        )
        .add_source('./pacts/')
    )
    ```

    1.  The `body` argument specifies whether to use a `POST` request and pass information in the body, or to use a `GET` request and pass information through HTTP headers. For more details, see the [`state_handler` API documentation][pact.verifier.Verifier.state_handler].

=== "Functional State Handling"

    ```python title="v2"
    # Not supported
    ```

    ```python title="v3 - Function"
        def handler(name, params=None):
            if name == 'user exists':
                # Set up user in database/mock
                create_user(params.get('id', 123))
            elif name == 'no users exist':
                # Clear users
                clear_users()

        verifier = (
            Verifier('my-provider')
            .add_transport(url='http://localhost:8080')
            .state_handler(handler)
            .add_source('./pacts/')
        )
    ```

    ```python title="v3 - Mapping"
    state_handlers = {
        'user exists': lambda name, params: create_user(params.get('id', 123)),
        'no users exist': lambda name, params: clear_users(),
    }

    verifier = (
        Verifier('my-provider')
        .add_transport(url='http://localhost:8080')
        .state_handler(state_handlers)
        .add_source('./pacts/')
    )
    ```

    More information on the state handler function signature can be found in the [`state_handler` API documentation][pact.verifier.Verifier.state_handler]. By default, the handlers only _set up_ the provider state. If you need to also _tear down_ the state after verification, you can use the `teardown=True` argument to enable this behaviour.

    !!! warning

        These functions run in the test process, so any side effects must be properly shared with the provider. If using mocking libraries, ensure the provider is started in a separate thread of the same process (using `threading.Thread` or similar), rather than a separate process (e.g., using `multiprocessing.Process` or `subprocess.Popen`).

<!-- markdownlint-enable code-block-style -->

#### Message Verification

Message verification is now much more straightforward in v3, with a a similar interface to HTTP verification and fixes a number of issues and deficiencies present in the v2 implementation (including the swapped behaviour of `expects_to_receive` and `given`, and the lack of support for matchers and generators).

```python title="v3 - Functional Handler"
def message_handler(description, metadata):
    if description == 'user created event':
        return {
            'id': 123,
            'name': 'Alice',
            'event': 'created'
        }
    elif description == 'user deleted event':
        return {'id': 123, 'event': 'deleted'}

verifier = (
    Verifier('my-provider')
    .message_handler(message_handler)
    .add_source('./pacts/')
)
```

```python title="v3 - Dictionary Mapping"
messages = {
    'user created event': {'id': 123, 'name': 'Alice', 'event': 'created'},
    'user deleted event': lambda desc, meta: {'id': 123, 'event': 'deleted'}
}

verifier = (
    Verifier('my-provider')
    .message_handler(messages)
    .add_source('./pacts/')
)
```

#### Running Verification

Verification has been simplified and no longer requires checking return codes. Instead, the `verify()` method raises an exception on failure, or returns normally on success.

```python title="v2"
success, logs = verifier.verify_pacts('./pacts/consumer-provider.json')
if not success:
    print(logs)
    raise AssertionError("Verification failed!")
```

```python title="v3"
verifier.verify()
```
