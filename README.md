# pact-python
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

## Running the Mock Service
This library does not yet automatically handle running the [Pact Mock Service] so you will need to
start that manually before running the tests. There are two primary ways to run the mock service:

1. [Install it and run it using Ruby](https://github.com/bethesque/pact-mock_service#usage)
2. Run it as a Docker container

Using the Docker container additionally has two options. You can run it via the `docker` command:

```
docker run -d -p "1234:1234" -v /tmp/log:/var/log/pacto -v $(pwd)/contracts:/opt/contracts madkom/pact-mock-service
```

Which will start the service and expose it as port `1234` on your computer, mount
`/tmp/log` on your machine to house the mock service log files, and the directory
`contracts` in the current working directory to house the contracts when they are published.

Additionally, you could run the mock service using `docker-compose`:

```yaml
version: '2'
services:
  pactmockservice:
    image: madkom/pact-mock-service
    ports:
      - "1234:1234"
    volumes:
      - /tmp/pact:/var/log/pacto
      - ./contracts:/opt/contracts
```

> Note: How you run the mock service may change what hostname and port you should
> use when running your consumer tests. For example: If you change the host port on
> the command line to be `8080`, your tests would need to contact `localhost:8080`.

## Verifying Pacts Against a Service
> pact-python does not yet have any involvement in the process of verifying a contract against
> a provider. This section is included to provide insight into the full cycle of a
> contract for those getting started.

Like the mock service, the provider verifier can be run in two ways:

1. [Install and use it as a Ruby application][pact-provider-verifier]
2. Run it as a Docker container

> Both choices have very similar configuration options. We will illustrate the Docker
> method below, but the Ruby method supports the same features.

When verifying your contracts, you may find it easier to run the provider application
and the verifier in separate Docker containers. This gives you a nice isolated
network, where you can set the DNS records of the services to anything you desire
and not have to worry about port conflicts with other services on your computer.
Launching the provider verifier in a `docker-compose.yml` might look like this:

```yaml
version: '2'
services:
  app:
    image: the-provider-application-to-test

  pactverifier:
    command: ['tail', '-f', '/dev/null']
    image: dius/pact-provider-verifier-docker
    depends_on:
      - app
    volumes:
      - ./contracts:/tmp/pacts
    environment:
      - pact_urls=/tmp/pacts/consumer-provider.json
      - provider_base_url=http://app
      - provider_states_url=http://app/_pact/provider-states
      - provider_states_active_url=http://app/_pact/provider-states/active
```

In this example, our `app` container may take a few moments to start, so we don't
immediately start running the verification, and instead `tail -f /dev/null` which will keep
the container running forever. We can then use `docker-compose` to run the tests like so:

```
docker-compose up -d
# Insert code to check that `app` has finished starting and is ready for requests
docker-compose exec pactverifier bundle exec rake verify_pacts
```

You configure the verifier in Docker using 4 environment variables:
- `pact_urls` - a comma delimited list of pact file urls
- `provider_base_url` - the base url of the pact provider
- `provider_states_url` - the full url of the endpoint which returns provider states by consumer
- `provider_states_active_url` - the full url of the endpoint which sets the active pact consumer and provider state

### Provider States
In many cases, your contracts will need very specific data to exist on the provider
to pass successfully. If you are fetching a user profile, that user needs to exist,
if querying a list of records, one or more records needs to exist. To support
decoupling the testing of the consumer and provider, Pact offers the idea of provider
states to communicate from the consumer what data should exist on the provider.

When setting up the testing of a provider you will also need to setup the management of
these provider states. The Pact verifier does this by making additional HTTP requests to
the `provider_states_url` and `provider_stats_active_url` you provide. These URLs could be
on the provider application or a separate one. Some strategies for managing state include:

- Having endpoints in your application that are not active in production that create and delete your datastore state
- A separate application that has access to the same datastore to create and delete, like a separate App Engine module or Docker container pointing to the same datastore
- A standalone application that can start and stop the other server with different datastore states

For more information about provider states, refer to the [Pact documentation] on [Provider States].

# Development
Please read [CONTRIBUTING.md](.github/CONTRIBUTING.md)

Create a Python virtualenv for use with this project
`make release`

## Testing
Unit: `make test`

End to end: `make e2e`

[context manager]: https://en.wikibooks.org/wiki/Python_Programming/Context_Managers
[Pact]: https://www.gitbook.com/book/pact-foundation/pact/details
[Pact documentation]: https://docs.pact.io/
[Pact Mock Service]: https://github.com/bethesque/pact-mock_service
[Provider States]: https://docs.pact.io/documentation/provider_states.html
[pact-provider-verifier]: https://github.com/pact-foundation/pact-provider-verifier
