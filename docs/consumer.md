# Consumer Testing

Pact is a consumer-driven contract testing tool. This means that the consumer specifies the expected interactions with the provider, and these interactions are used to create a contract. This contract is then used to verify that the provider meets the consumer's expectations.

The consumer is the client that makes requests, and the provider is the server that responds to those requests. In most straightforward cases, the consumer is a front-end application and the provider is a back-end service; however, a back-end service may also require information from another service, making it a consumer of that service.

## Writing the Test

For an illustrative example, consider a simple API client that fetches user data from a service. The client might look like this:

```python
import requests


class UserClient:
    def __init__(
        self,
        base_url: str = "https://example.com/api/v1",
    ):
        self.base_url = base_url

    def get_user(self, user_id) -> dict[str, str | int | list[str]]:
        """
        Fetch a user's data.

        Args:
            user_id: The user's ID.

        Returns:
            The user's data as a dictionary. It should have the following keys:

            -   id: The user's ID.
            -   username: The user's username.
            -   groups: A list of groups the user belongs to.
        """
        return requests.get("/".join([self.base_url, "user", user_id])).json()
```

The Pact test for this client would look like this:

```python
import atexit
import unittest

from user_client import UserClient
from pact import Consumer, Provider

pact = Consumer("UserConsumer").has_pact_with(Provider("UserProvider"))
pact.start_service()
atexit.register(pact.stop_service)


class GetUserData(unittest.TestCase):
    def test_get_user(self) -> None:
        expected = {
            "username": "UserA",
            "id": 123,
            "groups": ["Editors"],
        }

        (
            pact.given("User 123 exists")
            .upon_receiving("a request for user 123")
            .with_request("get", "/user/123")
            .will_respond_with(200, body=expected)
        )

        client = UserClient(pact.uri)

        with pact:
            result = client.get_user(123)
            self.assertEqual(result, expected)
```

This test does the following:

-   defines the Consumer and Provider objects that describe the product and the service under test,
-   uses `given` to define the setup criteria for the Provider, and
-   defines the expected request and response for the interaction.

The mock service is started when the `pact` object is used as a context manager. The `UserClient` object is created with the URI of the mock service, and the `get_user` method is called. The mock service responds with the expected data, and the test asserts that the response matches the expected data.

<!-- markdownlint-disable code-block-style -->

!!! info

    A common mistake is to use a generic HTTP client to make requests to the mock service. This defeats the purpose of the test as it does not verify that the client is making the correct requests and handling the responses correctly.

<!-- markdownlint-enable code-block-style -->

An alternative to using the `pact` object as a context manager is to manually call the `setup` and `verify` methods:

```python
with pact:
    result = client.get_user(123)
    self.assertEqual(result, expected)

# Is equivalent to

pact.setup()
result = client.get_user(123)
self.assertEqual(result, expected)
pact.verify()
```

## Mock Service

Pact provides a mock service that simulates the provider service based on the defined interactions. The mock service is started when the `pact` object is used as a context manager, or when the `setup` method is called.

The mock service is started by default on `localhost:1234`, but you can adjust this during Pact creation. This is particularly useful if the consumer interactions with multiple services.

```python
pact = Consumer('Consumer').has_pact_with(
    Provider('Provider'),
    host_name='mockservice',
    port=8080,
)
```

The mock service offers you several important features when building your contracts:

-   It provides a real HTTP server that your code can contact during the test and provides the responses you defined.
-   You provide it with the expectations for the request your code will make and it will assert the contents of the actual requests made based on your expectations.
-   If a request is made that does not match one you defined or if a request from your code is missing it will return an error with details.
-   Finally, it will record your contracts as a JSON file that you can store in your repository or publish to a Pact broker.

## Requests

The expected request in the example above is defined with the `with_request` method. It is possible to customize the request further by specifying the method, path, body, headers, and query with the `method`, `path`, `body`, `headers` and `query` keyword arguments.

-   Adding query parameters:

    ```python
    pact.with_request(
        path="/user/search",
        query={"group": "editor"},
    )
    ```

-   Using different HTTP methods:

    ```python
    pact.with_request(
        method="DELETE",
        path="/user/123",
    )
    ```

-   Adding a request body and headers:

    ```python
    pact.with_request(
        method="POST",
        path="/user/123",
        body={"username": "UserA"},
        headers={"Content-Type": "application/json"},
    )
    ```

You can define exact values for your expected request like the examples above, or you can use the matchers defined later to assist in handling values that are variable.

It is important to note that the code you are testing _must_ complete all requests defined. Similarly, if a client makes a request that is not defined in the contract, the test will also fail.

## Pattern Matching

Simple equality checks might be sufficient for simple requests, but more realistic tests will require more flexible matching. For example, the above scenario works great if the user information is always static, but will fail if the user has a datetime field that is regularly updated.

In order to handle variable data and make tests more robust, there are a number of matchers available as described below.

### Terms

The `Term` matcher allows you to define a regular expression that the value should match, along with an example value. The pattern is used by Pact for determining the validity of the response, while the example value is returned by Pact in cases where a response needs to be generated.

This is useful when you need to assert that a value has a particular format, but you are unconcerned about the exact value.

```python
body = {
    "id": 123,
    "reference": Term(r"[A-Z]\d{3,6}-[0-9a-f]{6}", "X1234-456def"),
    "last_modified": Term(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z",
        "2024-07-20T13:27:03Z",
    ),
}

(
    pact.given("User 123 exists")
    .upon_receiving("a request for user 123")
    .with_request("get", "/user/123")
    .will_respond_with(200, body=body, headers={
        "X-Request-ID": Term(
            r"[a-z]{4}[0-9]{8}-[A-Z]{3}",
            "abcd1234-EFG",
        ),
    })
)

client = UserClient(pact.uri)

with pact:
    result = client.get_user(123)
    assert result["id"] == 123
    assert result["reference"] == "X1234-456def"
    assert result["last_modified"] == "2024-07-20T13:27:03Z"
```

In this example, the `UserClient` must include a `X-Request-ID` header matching the pattern (irrespective of the actual value), and the mock service will respond with the example values.

### Like

The `Like` matcher asserts that the element's type matches the matcher. If the mock service needs to produce an answer, the example value provided will be returned. Some examples of the `Like` matcher are:

```python
from pact import Like

Like(123)            # Requires any integer
Like("hello world")  # Requires any string
Like(3.14)           # Requires any float
Like(True)           # Requires any boolean
```

More complex object can be defined, in which case the `Like` matcher will be applied recursively:

```python
from pact import Like, Term

Like({
    'id': 123,  # Requires any integer
    "reference": Term(r"[A-Z]\d{3,6}-[0-9a-f]{6}", "X1234-456def"),
    'confirmed': False, # Requires any boolean
    'address': { # Requires a dictionary
        'street': '200 Bourke St' # Requires any string
    }
})
```

### EachLike

The `EachLike` matcher asserts the value is an array type that consists of elements like the one passed in. It can be used to assert simple arrays,

```python
from pact import EachLike

EachLike(1)        # All items are integers
EachLike('hello')  # All items are strings
```

or other matchers can be nested inside to assert more complex objects

```python
from pact import EachLike, Term
EachLike({
    'username': Term('[a-zA-Z]+', 'username'),
    'id': 123,
    'groups': EachLike('administrators')
})
```

> Note, you do not need to specify everything that will be returned from the Provider in a JSON response, any extra data that is received will be ignored and the tests will still pass.

<!-- block quote separator -->

> Note, to get the generated values from an object that can contain matchers like Term, Like, EachLike, etc. for assertion in self.assertEqual(result, expected) you may need to use get_generated_values() helper function:

```python
from pact.matchers import get_generated_values
self.assertEqual(result, get_generated_values(expected))
```

### Common Formats

As you have seen above, regular expressions are a powerful tool for matching complex patterns; however, they can be cumbersome to write and maintain. A number of common formats have been predefined for ease of use:

| matcher           | description                                                                                                            |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `identifier`      | Match an ID (e.g. 42)                                                                                                  |
| `integer`         | Match all numbers that are integers (both ints and longs)                                                              |
| `decimal`         | Match all real numbers (floating point and decimal)                                                                    |
| `hexadecimal`     | Match all hexadecimal encoded strings                                                                                  |
| `date`            | Match string containing basic ISO8601 dates (e.g. 2016-01-01)                                                          |
| `timestamp`       | Match a string containing an RFC3339 formatted timestamp (e.g. Mon, 31 Oct 2016 15:21:41 -0400)                        |
| `time`            | Match string containing times in ISO date format (e.g. T22:44:30.652Z)                                                 |
| `iso_datetime`    | Match string containing ISO 8601 formatted dates (e.g. 2015-08-06T16:53:10+01:00)                                      |
| `iso_datetime_ms` | Match string containing ISO 8601 formatted dates, enforcing millisecond precision (e.g. 2015-08-06T16:53:10.123+01:00) |
| `ip_address`      | Match string containing IP4 formatted address                                                                          |
| `ipv6_address`    | Match string containing IP6 formatted address                                                                          |
| `uuid`            | Match strings containing UUIDs                                                                                         |

These can be used to replace other matchers

```python
from pact import Like, Format

Like({
    'id': Format().integer,
    'lastUpdated': Format().timestamp,
    'location': {
        'host': Format().ip_address
    },
})
```

For more information see [Matching](https://docs.pact.io/getting_started/matching)

## Broker

The above example showed how to test a single consumer; however, without also testing the provider, the test is incomplete. The Pact Broker is a service that allows you to share your contracts between your consumer and provider tests.

The Pact Broker acts as a central repository for all your contracts and verification results, and provides a number of features to help you get the most out of your Pact workflow.

Once the tests are complete, the contracts can be uploaded to the Pact Broker. The provider can then download the contracts and run its own tests to ensure it meets the consumer's expectations. There are two ways to upload contracts as shown below.

### Broker CLI (_recommended_)

The Broker CLI is a command-line tool that is bundled with the Pact Python package. It can be used to publish contracts to the Pact Broker. See [Publishing and retrieving pacts](https://docs.pact.io/pact_broker/publishing_and_retrieving_pacts)

The general syntax for the CLI is:

```console
pact-broker publish \
    /path/to/pacts/consumer-provider.json \
    --consumer-app-version 1.0.0 \
    --branch main \
    --broker-base-url https://test.pactflow.io \
    --broker-username someUsername \
    --broker-password somePassword
```

If the broker requires a token, you can use the `--broker-token` flag instead of `--broker-username` and `--broker-password`.

### Python API

If you wish to use a more programmatic approach within Python, it is possible to use the `Broker` class to publish contracts to the Pact Broker. Note that it is ultimately a wrapper around the CLI, and as a result, the CLI is recommended for most use cases.

```python
broker = Broker(broker_base_url="http://localhost")
broker.publish(
    "TestConsumer",
    "2.0.1",
    branch="consumer-branch",
    pact_dir=".",
)
```

The parameters for this differ slightly in naming from their CLI equivalents:

| CLI                                | native Python                    |
| ---------------------------------- | -------------------------------- |
| `--branch`                         | `branch`                         |
| `--build-url`                      | `build_url`                      |
| `--auto-detect-version-properties` | `auto_detect_version_properties` |
| `--tag=TAG`                        | `consumer_tags`                  |
| `--tag-with-git-branch`            | `tag_with_git_branch`            |
| `PACT_DIRS_OR_FILES`               | `pact_dir`                       |
| `--consumer-app-version`           | `version`                        |
| `n/a`                              | `consumer_name`                  |
