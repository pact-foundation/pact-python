# FFI Upgrade

## Verifier

Replace `from pact import Verifier`
with `from pact import VerifierV3`

Replace `verify` or `verify_with_broker`
with `verify_pacts`

### Pact Sources

Pact-Python can now retrieve pacts from

- File Source
- Directory Source
- Url Source
- Broker Source

It is possible to set all 4 sources, and 4 verification tasks will be performed.

Publishing results will only be performed for Url and Broker source, if `publish_verification_results=True`

#### User Provided Sources

For the following

- File Source
- Directory Source
- Url Source

* You should provide them in the `sources` argument and not set the `broker_url`

```python
    verifier = VerifierV3(provider="area-calculator-provider",
                          provider_base_url="tcp://127.0.0.1:37757",
                          )
    result = verifier.verify_pacts(
        sources=["./examples/pacts/v4-grpc.json"],
    )
```

- You can provide multiple sources in the `sources` argument
- You can provide auth credentials, if a pact broker requires it

```python
    verifier = VerifierV3(provider="area-calculator-provider",
                          provider_base_url="tcp://127.0.0.1:37757",
                          )
    result = verifier.verify_pacts(
        sources=[
            "./examples/pacts/v3-http.json",
            "./examples/pacts/v4-grpc.json",
            'https://test.pactbroker.io/pacts/provider/Example%20API/consumer/Example%20App/latest'
            ],
        broker_username="username",
        broker_password="password",
    )
```

#### Dynamically Fetched Sources

- You can dynamically fetch pacts from the broker.
- You should not provide anything in the `sources` argument and set the `broker_url`

- The following will retrieve the latest pacts for the named `provider`

```python
    verifier = VerifierV3(provider="area-calculator-provider",
                          provider_base_url="tcp://127.0.0.1:37757",
                          )
    result = verifier.verify_pacts(
        broker_url="https://test.pactbroker.io",
        broker_username="username",
        broker_password="password",
    )
```

- You can dynamically fetch pacts from the broker.
  - Provide dynamic fetching arguments
    - `consumer_version_selectors`
    - `consumer_version_tags`

```python
    verifier = VerifierV3(provider="area-calculator-provider",
                          provider_base_url="tcp://127.0.0.1:37757",
                          )
    result = verifier.verify_pacts(
        broker_url="https://test.pactbroker.io",
        broker_username="username",
        broker_password="password",
    )
```

For different schemes or base paths for your provider, use `provider_base_url`

- grpc `provider_base_url="tcp://127.0.0.1:37757"`
- http without a port `provider_base_url="http://127.0.0.1"` (defaults to `8080`)
- provide a base path `provider_base_url="http://127.0.0.1/api/internal"` (defaults to `/`)

## Message Provider

Now utilises `VerifierV3` rather than the old ruby implementation.

No changes to interface.

Ideally should

- change to utilise all options of `VerifierV3`
- not hardcode `pact_dir` (use `sources` instead)
- replace `verify` & `verify_with_broker` with `verify_pacts`

## Consumer

WIP - Need to build out consumer interface

Rough examples in

`./tests/ffi/test_ffi_grpc_consumer.py`
`./tests/ffi/test_ffi_http_consumer.py`
`./tests/ffi/test_ffi_message_consumer.py`

### PactV3 Consumer

New imports and matchers/generators

```python
from pact import PactV3
from pact.matchers_v3 import Like, Regex, Format
```

* lifecyle changes
  * start_provider moves to inside test, after interaction setup
  * stop_provider no longer called
  * verify moves to inside test, after client has issued request
    * can be pre or post unit test assertions.

## Message Consumer

Not started

## Logging

By default, pact-python will log to a buffer, at INFO level

you can set

- PACT_LOG_LEVEL
  - NONE | ERROR | INFO | DEBUG | TRACE
- PACT_LOG_OUTPUT
  - STDOUT | FILE | BUFFER
- PACT_LOG_FILE
  - Location to logfile if PACT_LOG_OUTPUT=FILE (default `./log/pact.log`)

examples

`PACT_LOG_LEVEL=TRACE PACT_LOG_OUTPUT=STDOUT pytest tests/test_todo_consumer.py -rP`
`PACT_LOG_LEVEL=INFO PACT_LOG_OUTPUT=FILE pytest tests/test_todo_consumer.py -rP`
`PACT_LOG_LEVEL=DEBUG PACT_LOG_OUTPUT=BUFFER pytest tests/test_todo_consumer.py -rP`
