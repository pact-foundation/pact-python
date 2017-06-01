# pact-python

[![Join the chat at https://gitter.im/realestate-com-au/pact](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/realestate-com-au/pact?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Build Status](https://travis-ci.org/pact-foundation/pact-python.svg?branch=master)](https://travis-ci.org/pact-foundation/pact-python)
[![License](https://img.shields.io/github/license/pact-foundation/pact-python.svg?maxAge=2592000)](https://github.com/pact-foundation/pact-python/blob/master/LICENSE)

Python version of Pact. Enables consumer driven contract testing,
providing a mock service and DSL for the consumer project, and
interaction playback and verification for the service provider project.

For more information about what Pact is, and how it can help you
test your code more efficiently, check out the [Pact documentation].

# How to use pact-python

## Installation
```
pip install pact-python
```

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
````

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

### SomethingLike(matcher)
Asserts the element's type matches the matcher. For example:

```python
from pact import SomethingLike
SomethingLike(123)  # Matches if the value is an integer
SomethingLike('hello world')  # Matches if the value is a string
SomethingLike(3.14)  # Matches if the value is a float
```

The argument supplied to `SomethingLike` will be what the mock service responds with.

### EachLike(matcher, minimum=None, maximum=None)
Asserts the value is an array type that consists of elements
like the ones passed in. It can be used to assert simple arrays:

```python
from pact import EachLike
EachLike(1)  # All items are integers
EachLike('hello')  # All items are strings
```

Or other matchers can be nested inside to assert more complex objects:

```python
from pact import EachLike, SomethingLike, Term
EachLike({
    'username': Term('[a-zA-Z]+', 'username'),
    'id': SomethingLike(123),
    'groups': EachLike('administrators')
})
```

> Note, you do not need to specify everything that will be returned from the Provider in a
> JSON response, any extra data that is received will be ignored and the tests will still pass.

For more information see [Matching](https://docs.pact.io/documentation/matching.html)

## Verifying Pacts Against a Service

In addition to writing Pacts for Python consumers, you can also verify those Pacts
against a provider of any language. After installing pact-python a `pact-verifier`
application should be available. To get details about its use you can call it with the
help argument:

```bash
pact-verifier --help
```

The simplest example is verifying a server with locally stored Pact files and no provider
states:

```bash
pact-verifier --provider-base-url=http://localhost:8080 --pact-urls=./pacts/consumer-provider.json
```

Which will immediately invoke the Pact verifier, making HTTP requests to the server located
at `http://localhost:8080` based on the Pacts in `./pacts/consumer-provider.json` and
reporting the results.

There are several options for configuring how the Pacts are verified:

###### --provider-base-url

Required. Defines the URL of the server to make requests to when verifying the Pacts.  

###### --pact-urls

Required. The location of the Pact files you want to verify. This can be a URL to a [Pact Broker]
or one or more local paths, separated by a comma.

###### --provider-states-url

The URL where your provider application will produce the list of available provider states.
The verifier calls this URL to ensure the Pacts specify valid states before making the HTTP
requests.

###### --provider-states-setup-url

The URL which should be called to setup a specific provider state before a Pact is verified.
 
###### --pact-broker-username

The username to use when contacting the Pact Broker.

###### --pact-broker-password

The password to use when contacting the Pact Broker. You can also specify this value
as the environment variable `PACT_BROKER_PASSWORD`. 

### Provider States
In many cases, your contracts will need very specific data to exist on the provider
to pass successfully. If you are fetching a user profile, that user needs to exist,
if querying a list of records, one or more records needs to exist. To support
decoupling the testing of the consumer and provider, Pact offers the idea of provider
states to communicate from the consumer what data should exist on the provider.

When setting up the testing of a provider you will also need to setup the management of
these provider states. The Pact verifier does this by making additional HTTP requests to
the `provider_states_url` and `provider_states_setup_url` you provide. These URLs could be
on the provider application or a separate one. Some strategies for managing state include:

- Having endpoints in your application that are not active in production that create and delete your datastore state
- A separate application that has access to the same datastore to create and delete, like a separate App Engine module or Docker container pointing to the same datastore
- A standalone application that can start and stop the other server with different datastore states

For more information about provider states, refer to the [Pact documentation] on [Provider States].

# Development
Please read [CONTRIBUTING.md](CONTRIBUTING.md)

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

[bundler]: http://bundler.io/
[context manager]: https://en.wikibooks.org/wiki/Python_Programming/Context_Managers
[Pact]: https://www.gitbook.com/book/pact-foundation/pact/details
[Pact Broker]: https://docs.pact.io/documentation/sharings_pacts.html
[Pact documentation]: https://docs.pact.io/
[Pact Mock Service]: https://github.com/bethesque/pact-mock_service
[Provider States]: https://docs.pact.io/documentation/provider_states.html
[pact-provider-verifier]: https://github.com/pact-foundation/pact-provider-verifier
[pyenv]: https://github.com/pyenv/pyenv
[rvm]: https://rvm.io/
[rbenv]: https://github.com/rbenv/rbenv
[virtualenv]: http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/
