# pact-python

[![slack](https://slack.pact.io/badge.svg)](https://slack.pact.io)
[![License](https://img.shields.io/github/license/pact-foundation/pact-python.svg?maxAge=2592000)](https://github.com/pact-foundation/pact-python/blob/master/LICENSE)
![Build and Test](https://github.com/pact-foundation/pact-python/workflows/Build%20and%20Test/badge.svg)

Python version of Pact. Enables consumer driven contract testing,
providing a mock service and DSL for the consumer project, and
interaction playback and verification for the service provider project.
Currently supports version 2 of the [Pact specification].

For more information about what Pact is, and how it can help you
test your code more efficiently, check out the [Pact documentation].

Note: As of Version 1.0 deprecates support for python 2.7 to allow us to incorporate python 3.x features more readily. If you want to still use Python 2.7 use the 0.x.y versions. Only bug fixes will now be added to that release.

# How to use pact-python

## Installation
```
pip install pact-python
```

## Getting started
<!-- Absolute link for rendering page in docs.pact.io -->
A guide follows but if you go to the [e2e examples](https://github.com/pact-foundation/pact-python/tree/master/examples/e2e). This has a consumer, provider and pact-broker set of tests.

## Writing a Pact

Creating a complete contract is a two step process:

1. Create a test on the consumer side that declares the expectations it has of the provider
2. Create a provider state that allows the contract to pass when replayed against the provider

## Writing the Consumer Test

If we have a method that communicates with one of our external services, which we'll call
`Provider`, and our product, `Consumer` is hitting an endpoint on `Provider` at
`/users/<user>` to get information about a particular user.

If the code to fetch a user looked like this:

```python
import requests


def user(user_name):
    """Fetch a user object by user_name from the server."""
    uri = 'http://localhost:1234/users/' + user_name
    return requests.get(uri).json()
```

Then `Consumer`'s contract test might look something like this:

```python
import atexit
import unittest

from pact import Consumer, Provider


pact = Consumer('Consumer').has_pact_with(Provider('Provider'))
pact.start_service()
atexit.register(pact.stop_service)


class GetUserInfoContract(unittest.TestCase):
  def test_get_user(self):
    expected = {
      'username': 'UserA',
      'id': 123,
      'groups': ['Editors']
    }

    (pact
     .given('UserA exists and is not an administrator')
     .upon_receiving('a request for UserA')
     .with_request('get', '/users/UserA')
     .will_respond_with(200, body=expected))

    with pact:
      result = user('UserA')

    self.assertEqual(result, expected)

```

This does a few important things:

 - Defines the Consumer and Provider objects that describe our product and our service under test
 - Uses `given` to define the setup criteria for the Provider `UserA exists and is not an administrator`
 - Defines what the request that is expected to be made by the consumer will contain
 - Defines how the server is expected to respond

Using the Pact object as a [context manager], we call our method under test
which will then communicate with the Pact mock service. The mock service will respond with
the items we defined, allowing us to assert that the method processed the response and
returned the expected value. If you want more control over when the mock service is
configured and the interactions verified, use the `setup` and `verify` methods, respectively:

```python
   (pact
     .given('UserA exists and is not an administrator')
     .upon_receiving('a request for UserA')
     .with_request('get', '/users/UserA')
     .will_respond_with(200, body=expected))

    pact.setup()
    # Some additional steps before running the code under test
    result = user('UserA')
    # Some additional steps before verifying all interactions have occurred
    pact.verify()
```

### Requests

When defining the expected HTTP request that your code is expected to make you
can specify the method, path, body, headers, and query:

```python
pact.with_request(
    method='GET',
    path='/api/v1/my-resources/',
    query={'search': 'example'}
)
```

`query` is used to specify URL query parameters, so the above example expects
a request made to `/api/v1/my-resources/?search=example`.

```python
pact.with_request(
    method='POST',
    path='/api/v1/my-resources/123',
    body={'user_ids': [1, 2, 3]},
    headers={'Content-Type': 'application/json'},
)
```

You can define exact values for your expected request like the examples above,
or you can use the matchers defined later to assist in handling values that are
variable.

The default hostname and port for the Pact mock service will be
`localhost:1234` but you can adjust this during Pact creation:

```python
from pact import Consumer, Provider
pact = Consumer('Consumer').has_pact_with(
    Provider('Provider'), host_name='mockservice', port=8080)
```

This can be useful if you need to run to create more than one Pact for your test
because your code interacts with two different services. It is important to note
that the code you are testing with this contract _must_ contact the mock service.
So in this example, the `user` method could accept an argument to specify the
location of the server, or retrieve it from an environment variable so you can
change its URI during the test.

The mock service offers you several important features when building your contracts:
- It provides a real HTTP server that your code can contact during the test and provides the responses you defined.
- You provide it with the expectations for the request your code will make and it will assert the contents of the actual requests made based on your expectations.
- If a request is made that does not match one you defined or if a request from your code is missing it will return an error with details.
- Finally, it will record your contracts as a JSON file that you can store in your repository or publish to a Pact broker.

## Expecting Variable Content
The above test works great if that user information is always static, but what happens if
the user has a last updated field that is set to the current time every time the object is
modified? To handle variable data and make your tests more robust, there are 3 helpful matchers:

### Term(matcher, generate)
Asserts the value should match the given regular expression. You could use this
to expect a timestamp with a particular format in the request or response where
you know you need a particular format, but are unconcerned about the exact date:

```python
from pact import Term
...
body = {
    'username': 'UserA',
    'last_modified': Term('\d+-\d+-\d+T\d+:\d+:\d+', '2016-12-15T20:16:01')
}

(pact
 .given('UserA exists and is not an administrator')
 .upon_receiving('a request for UserA')
 .with_request('get', '/users/UserA/info')
 .will_respond_with(200, body=body))
```

When you run the tests for the consumer, the mock service will return the value you provided
as `generate`, in this case `2016-12-15T20:16:01`. When the contract is verified on the
provider, the regex will be used to search the response from the real provider service
and the test will be considered successful if the regex finds a match in the response.

### Like(matcher)
Asserts the element's type matches the matcher. For example:

```python
from pact import Like
Like(123)  # Matches if the value is an integer
Like('hello world')  # Matches if the value is a string
Like(3.14)  # Matches if the value is a float
```
The argument supplied to `Like` will be what the mock service responds with.

When a dictionary is used as an argument for Like, all the child objects (and their child objects etc.) will be matched according to their types, unless you use a more specific matcher like a Term.

```python
from pact import Like, Term
Like({
    'username': Term('[a-zA-Z]+', 'username'),
    'id': 123, # integer
    'confirmed': False, # boolean
    'address': { # dictionary
        'street': '200 Bourke St' # string
    }
})

```

### EachLike(matcher, minimum=1)
Asserts the value is an array type that consists of elements
like the one passed in. It can be used to assert simple arrays:

```python
from pact import EachLike
EachLike(1)  # All items are integers
EachLike('hello')  # All items are strings
```

Or other matchers can be nested inside to assert more complex objects:

```python
from pact import EachLike, Term
EachLike({
    'username': Term('[a-zA-Z]+', 'username'),
    'id': 123,
    'groups': EachLike('administrators')
})
```

> Note, you do not need to specify everything that will be returned from the Provider in a
> JSON response, any extra data that is received will be ignored and the tests will still pass.

> Note, to get the generated values from an object that can contain matchers like Term, Like, EachLike, etc.
> for assertion in self.assertEqual(result, expected) you may need to use get_generated_values() helper function:

```python
from pact.matchers import get_generated_values
self.assertEqual(result, get_generated_values(expected))
```

### Match common formats
Often times, you find yourself having to re-write regular expressions for common formats.

```python
from pact import Format
Format().integer  # Matches if the value is an integer
Format().ip_address  # Matches if the value is a ip address
```

We've created a number of them for you to save you the time:

| matcher          | description                                                                                     |
|-----------------|-------------------------------------------------------------------------------------------------|
| `identifier`  | Match an ID (e.g. 42)                                                                           |
| `integer`     | Match all numbers that are integers (both ints and longs)                                       |
| `decimal`     | Match all real numbers (floating point and decimal)                                             |
| `hexadecimal`    | Match all hexadecimal encoded strings                                                           |
| `date`        | Match string containing basic ISO8601 dates (e.g. 2016-01-01)                                   |
| `timestamp`   | Match a string containing an RFC3339 formatted timestapm (e.g. Mon, 31 Oct 2016 15:21:41 -0400) |
| `time`        | Match string containing times in ISO date format (e.g. T22:44:30.652Z)                          |
| `ip_address` | Match string containing IP4 formatted address                                                   |
| `ipv6_address` | Match string containing IP6 formatted address                                                   |
| `uuid`        | Match strings containing UUIDs                                                                  |

These can be used to replace other matchers

```python
from pact import Like, Format
Like({
    'id': Format().integer, # integer
    'lastUpdated': Format().timestamp, # timestamp
    'location': { # dictionary
        'host': Format().ip_address # ip address
    }
})
```

For more information see [Matching](https://docs.pact.io/getting_started/matching)

## Verifying Pacts Against a Service

In addition to writing Pacts for Python consumers, you can also verify those Pacts
against a provider of any language. There are two ways to do this.

### CLI

After installing pact-python a `pact-verifier`
application should be available. To get details about its use you can call it with the
help argument:

```bash
pact-verifier --help
```

The simplest example is verifying a server with locally stored Pact files and no provider
states:

```bash
pact-verifier --provider-base-url=http://localhost:8080 --pact-url=./pacts/consumer-provider.json
```

Which will immediately invoke the Pact verifier, making HTTP requests to the server located
at `http://localhost:8080` based on the Pacts in `./pacts/consumer-provider.json` and
reporting the results.

There are several options for configuring how the Pacts are verified:

###### --provider-base-url

Required. Defines the URL of the server to make requests to when verifying the Pacts.

###### --pact-url

Required if --pact-urls not specified. The location of a Pact file you want
to verify. This can be a URL to a [Pact Broker] or a local path, to provide
multiple files, specify multiple arguments.

```
pact-verifier --provider-base-url=http://localhost:8080 --pact-url=./pacts/one.json --pact-url=./pacts/two.json
```

###### --pact-urls

Required if --pact-url not specified. The location of the Pact files you want
to verify. This can be a URL to a [Pact Broker] or one or more local paths, separated by a comma.

###### --provider-states-url

_DEPRECATED AFTER v 0.6.0._ The URL where your provider application will produce the list of available provider states.
The verifier calls this URL to ensure the Pacts specify valid states before making the HTTP
requests.

###### --provider-states-setup-url

The URL which should be called to setup a specific provider state before a Pact is verified. This URL will be called with a POST request, and the JSON body `{consumer: 'Consumer name', state: 'a thing exists'}`.

###### --pact-broker-url

Base URl for the Pact Broker instance to publish pacts to. Can also be specified via the environment variable
`PACT_BROKER_BASE_URL`.

###### --pact-broker-username

The username to use when contacting the Pact Broker. Can also be specified via the environment variable
`PACT_BROKER_USERNAME`.

###### --pact-broker-password

The password to use when contacting the Pact Broker. You can also specify this value
as the environment variable `PACT_BROKER_PASSWORD`.

###### --pact-broker-token

The bearer token to use when contacting the Pact Broker. You can also specify this value
as the environment variable `PACT_BROKER_TOKEN`.

###### --consumer-version-tag

Retrieve the latest pacts with this consumer version tag. Used in conjunction with `--provider`.
May be specified multiple times.

###### --consumer-version-selector

You can also retrieve pacts with consumer version selector, a more flexible approach in specifying which pacts you need.
May be specified multiple times. Read more about selectors [here](https://docs.pact.io/pact_broker/advanced_topics/consumer_version_selectors/).

###### --provider-version-tag

Tag to apply to the provider application version. May be specified multiple times.

###### --custom-provider-header

Header to add to provider state set up and pact verification requests e.g.`Authorization: Basic cGFjdDpwYWN0`
May be specified multiple times.

###### -t, --timeout

The duration in seconds we should wait to confirm that the verification process was successful. Defaults to 30.

###### -a, --provider-app-version

The provider application version. Required for publishing verification results.

###### -r, --publish-verification-results

Publish verification results to the broker.

### Python API
You can use the Verifier class. This has all the same parameters as the cli tool but allows you to write native python code and the test framework of your choice.

```python
verifier = Verifier(provider='UserService',
                    provider_base_url=PACT_URL)

output, logs = verifier.verify_pacts('./userserviceclient-userservice.json')

```
You can see more details in the [e2e examples](https://github.com/pact-foundation/pact-python/tree/master/examples/e2e/tests/provider/test_provider.py).

### Provider States
In many cases, your contracts will need very specific data to exist on the provider
to pass successfully. If you are fetching a user profile, that user needs to exist,
if querying a list of records, one or more records needs to exist. To support
decoupling the testing of the consumer and provider, Pact offers the idea of provider
states to communicate from the consumer what data should exist on the provider.

When setting up the testing of a provider you will also need to setup the management of
these provider states. The Pact verifier does this by making additional HTTP requests to
the `--provider-states-setup-url` you provide. This URL could be
on the provider application or a separate one. Some strategies for managing state include:

- Having endpoints in your application that are not active in production that create and delete your datastore state
- A separate application that has access to the same datastore to create and delete, like a separate App Engine module or Docker container pointing to the same datastore
- A standalone application that can start and stop the other server with different datastore states

For more information about provider states, refer to the [Pact documentation] on [Provider States].

# Development
<!-- Absolute link for rendering page in docs.pact.io -->
Please read [CONTRIBUTING.md](https://github.com/pact-foundation/pact-python/blob/master/CONTRIBUTING.md)

To setup a development environment:

1. If you want to run tests for all Python versions, install 2.7, 3.3, 3.4, 3.5, and 3.6 from source or using a tool like [pyenv]
2. Its recommended to create a Python [virtualenv] for the project

The setup the environment, run tests, and package the application, run:
`make release`

If you are just interested in packaging pact-python so you can install it using pip:

`make package`

This creates a `dist/pact-python-N.N.N.tar.gz` file, where the Ns are the current version.
From there you can use pip to install it:

`pip install ./dist/pact-python-N.N.N.tar.gz`

## Testing

This project has unit and end to end tests, which can both be run from make:

Unit: `make test`

End to end: `make e2e`

## Contact

Join us in slack: [![slack](https://slack.pact.io/badge.svg)](https://slack.pact.io)

or

- Twitter: [@pact_up](https://twitter.com/pact_up)
- Stack Overflow: [stackoverflow.com/questions/tagged/pact](https://stackoverflow.com/questions/tagged/pact)

[bundler]: http://bundler.io/
[context manager]: https://en.wikibooks.org/wiki/Python_Programming/Context_Managers
[Pact]: https://docs.pact.io
[Pact Broker]: https://docs.pact.io/pact_broker
[Pact documentation]: https://docs.pact.io/
[Pact Mock Service]: https://github.com/pact-foundation/pact-mock_service
[Pact specification]: https://github.com/pact-foundation/pact-specification
[Provider States]: https://docs.pact.io/getting_started/provider_states
[pact-provider-verifier]: https://github.com/pact-foundation/pact-provider-verifier
[pyenv]: https://github.com/pyenv/pyenv
[rvm]: https://rvm.io/
[rbenv]: https://github.com/rbenv/rbenv
[virtualenv]: http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/
