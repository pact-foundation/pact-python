# Examples

## Table of Contents

  * [Overview](#overview)
  * [broker](#broker)
  * [consumer](#consumer)
  * [flask_provider](#flask_provider)
  * [fastapi_provider](#fastapi_provider)
  * [message](#message)

## Overview

TODO

## broker

The [Pact Broker] stores Pacts and verification results. It is used here for the [consumer](#consumer), [flask_provider](#flask-provider) and [message](#message) tests.

### Running

These examples run the broker as part of the tests when specified. It can be run outside the tests as well by performing the following command from a separate terminal in the examples/broker folder:
```bash
docker-compose up
```

You should then be able to open a browser and navigate to http://localhost where you will initially be able to see the default Example App/Example API Pact.

Running the broker outside the tests will mean you are able to then see the Pacts submitted to the broker as the various tests are performed.

## consumer

Pact is consumer-driven, which means first the contracts are created. These Pact contracts are generated during execution of the consumer tests.

### Running

When the tests are run, the "minimum" is to generate the Pact contract JSON. Additional options are available, from the `examples/consumer` folder:

- To startup the broker, run the tests, and publish the results to the broker:
    ```bash
    pytest --publish-pact 2 --run-broker True
    ```

- To run the tests, and publish the results to the broker which is already running:
    ```bash
    pytest --publish-pact 2
    ```
- To just run the tests:
    ```bash
    pytest
    ```
In these examples, `2` is just used to meet the need of having *some* consumer version.

### Output

The following files will be created when the tests are run:

 - **consumer/pact-mock-service.log**: All interactions with the mock provider such as expected interactions, requests, and interaction verifications.
 - **consumer/userserviceclient-userservice.json**: This contains the Pact interactions between the `UserServiceClient` and `UserService`, as defined in the tests.

## flask_provider

TODO

## fastapi_provider

TODO

## message

TODO

[Pact Broker]: https://docs.pact.io/pact_broker