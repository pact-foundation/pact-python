"""
Interaction module.

This module defines the classes that are used to define individual interactions
within a [`Pact`][pact.v3.pact.Pact] between a consumer and a provider. These
interactions can be of different types, such as HTTP requests, synchronous
messages, or asynchronous messages.

An interaction is a specific request that the consumer makes to the provider,
and the response that the provider should return. On the consumer side, the
interaction clearly defines the request that the consumer will make to the
provider and the response that the consumer expects to receive. On the provider
side, the interaction is replayed to the provider to ensure that the provider is
able to handle the request and return the expected response.

## Best Practices

When defining an interaction, it is important to ensure that the interaction is
as minimal as possible (which is in contrast to the way specifications like
OpenAPI are often written). This is because the interaction is used to verify
that the consumer and provider can communicate correctly, not to define the
entire API.

For example, consider a simple user API that has a `GET /user/{id}` endpoint
which returns an object of the form:

```json
{
    "id": 123,
    "username": "Alice"
    "email": "alice@example.com",
    "registered": "2021-02-26T10:17:51+11:00",
    "last_login": "2024-07-04T13:25:45+10:00"
}
```

The user client might have two functionalities:

1.  To check if the user exists, and
2.  To retrieve the user's username.

The implementation of these two would be:

```python
from pact.v3 import Pact


pact = Pact(consumer="UserClient", provider="UserService")

# Checking if a user exists
(
    pact.upon_receiving("A request to check if a user exists")
    .given("A user with ID 123 exists")
    .with_request("GET", "/user/123")
    .will_respond_with(200)
)

# Getting a user's username
(
    pact.upon_receiving("A request to get a user's username")
    .given("A user with ID 123 exists")
    .with_request("GET", "/user/123")
    .will_respond_with(200)
    .with_body({"username": "Alice"})
)
```

Importantly, even if the server returns more information than just the username,
since the client does not care about this information, it should not be included
in the interaction.
"""

from pact.v3.interaction._async_message_interaction import AsyncMessageInteraction
from pact.v3.interaction._base import Interaction
from pact.v3.interaction._http_interaction import HttpInteraction
from pact.v3.interaction._sync_message_interaction import SyncMessageInteraction

__all__ = [
    "AsyncMessageInteraction",
    "HttpInteraction",
    "Interaction",
    "SyncMessageInteraction",
]
