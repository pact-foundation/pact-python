---
authors:
    - JP-Ellis
date:
    created: 2024-12-30
---

# Functional Arguments

Today marks the [release of Pact Python version 2.3.0](https://github.com/pact-foundation/pact-python/releases/tag/v2.3.0). Among the many incremental improvements, the most significant is the [support of functional arguments](https://github.com/pact-foundation/pact-python/pull/890). This feature provides an improved user experience for providers, and also introduces several breaking changes to the `pact.v3` preview.

If you just want to update your existing code to the latest version without any other changes, you can skip to the [Breaking Changes TL;DR](#breaking-changes-tldr) section. Otherwise, key new features now allow you to [define provider states using functions](#functional-state-handler) and [use functions to produce messages](#functional-message-producer).
<!-- more -->

## Breaking Changes TL;DR

While I highly recommend everyone experiment with the new possibilities that functional arguments bring, if you merely want to update your existing code to the latest version, here is a quick summary of the breaking changes:

-   The `Verifier` initialization now requires a `name` argument which is used to identify the provider in the Pact file. This information was previously given through the `set_info` method which has been removed. The change required is:

    <!-- markdownlint-disable code-block-style -->
    === "Before"

        ```python
        verifier = Verifier()
        verifier.set_info("provider_name", ...)
        ```

    === "After"

        ```python
        verifier = Verifier(name="provider_name")
        ```
    <!-- markdownlint-enable code-block-style -->

-   The `Verifier.set_info` method has been entirely removed. Instead, the `Verifier` class now has a `name` attribute which is set during initialization for the provider's name, and the transport information that was previously set is now passed through the `add_transport` method:

    <!-- markdownlint-disable code-block-style -->
    === "Before"

        ```python
        verifier = Verifier()
        verifier.set_info(
            "provider_name",
            url="http://localhost:8123",
        )
        ```

    === "After"

        ```python
        verifier = Verifier("provider_name")
        verifier.add_transport(url="http://localhost:8123")
        ```
    <!-- markdownlint-enable code-block-style -->

-   The `Verifier.set_state` function has been renamed to `Verifier.state_handler`. Furthermore, if you have already set up a custom endpoint to handle provider state changes, you will now need to explicitly state whether your endpoint expects data to be passed through the query string or through a `POST` body:

    <!-- markdownlint-disable code-block-style -->
    === "Before"

        ```python
        verifier = Verifier()
        verifier.set_state("http://localhost:8123/provider-states")
        ```

    === "After"

        ```python
        verifier = Verifier()
        verifier.state_handler(
            "http://localhost:8123/provider-states",
            body=False,  # the previous default must be explicitly set
        )
        ```
    <!-- markdownlint-enable code-block-style -->

## Functional State Handler

When a Pact interaction is to be verified, the consumer will often expect the provider to be in a particular state. For example, a consumer might want to fetch a specific user's details, and therefore the provider must be in a state where that user exists. The user experience prior to version 2.3.0 was less than ideal: the developers behind the provider had to set up a custom endpoint to handle the state changes, and then pass the URL of that endpoint to the `Verifier` object.

The new `state_handler` method replaces the `set_state` method and simplifies this process significantly by allowing functions to be called to set up and tear down the provider state. For example, the following code snippet demonstrates how to set up a state handler that uses a custom endpoint to handle the provider state:

<!-- markdownlint-disable code-block-style -->
???+ example

    ```python
    from pact.v3 import Verifier

    def provider_state_callback(
        name: str,  # (1)
        action: Literal["setup", "teardown"],  # (2)
        params: dict[str, Any] | None,  # (3)
    ) -> None:
        """
        Callback to set up and tear down the provider state.

        Args:
            name:
                The name of the provider state. For example, `"a user with ID 123
                exists"` or `"no users exist"`.

            action:
                The action to perform. Either `"setup"` or `"teardown"`. The setup
                action should create the provider state, and the teardown action
                should remove it.

            params:
                If the provider state has additional parameters, they will be
                passed here. For example, instead of `"a user with ID 123 exists"`,
                the provider state might be `"a user with the given ID exists"` and
                the specific ID would be passed in the params.
        """
        ...

    def test_provider():
        verifier = Verifier("provider_name")
        verifier.state_handler(provider_state_callback, teardown=True)
    ```

    1.  The `name` parameter is the name of the provider state. For example, `"a user with ID 123 exists"` or `"no users exist"`. If you instead use a mapping of provider state names to functions, this parameter is not passed to the function.
    2.  The `action` parameter is either `"setup"` or `"teardown"`. The setup action should create the provider state, and the teardown action should remove it. If you specify `teardown=False`, then the `action` parameter is _not_ passed to the callback function.
    3.  The `params` parameter is a dictionary of additional parameters that the provider state requires. For example, instead of `"a user with ID 123 exists"`, the provider state might be `"a user with the given ID exists"` and the specific ID would be passed in the `params` dictionary. Note that `params` is always present, but may be `None` if no parameters are specified by the consumer.
<!-- markdownlint-enable code-block-style -->

This snippet showcases a way to set up the provider state with a function that is fully parameterized. The `state_handler` method also handles the following scenarios:

-   If teardowns are never required, then one should specify `teardown=False` in which case the `action` parameter is _not_ passed to the callback function.

    <!-- markdownlint-disable code-block-style -->
    ??? example

        ```python
        from pact.v3 import Verifier

        def provider_state_callback(
            name: str,
            params: dict[str, Any] | None,
        ) -> None:
            ...

        def test_provider():
            verifier = Verifier("provider_name")
            verifier.state_handler(provider_state_callback, teardown=False)
        ```
    <!-- markdownlint-enable code-block-style -->

-   A mapping can be provided to the `state_handler` method with keys as the provider state names and values as the function to call. This can help to keep the code organized and to avoid a large number of `if` statements in the callback function.

    <!-- markdownlint-disable code-block-style -->
    ??? example

        ```python
        from pact.v3 import Verifier

        def user_state_callback(
            action: Literal["setup", "teardown"],
            params: dict[str, Any] | None,
        ) -> None:
            ...

        def no_users_state_callback(
            action: Literal["setup", "teardown"],
            params: dict[str, Any] | None,
        ) -> None:
            ...

        def test_provider():
            verifier = Verifier("provider_name")
            verifier.state_handler(
                {
                    "a user with ID 123 exists": user_state_callback,
                    "no users exist": no_users_state_callback,
                },
            )
        ```
    <!-- markdownlint-enable code-block-style -->

-   Both scenarios can be combined, in which a mapping of provide state names to functions is provided, and the `teardown=False` option is specified. In this case, the function should expect only one argument: the `params` dictionary (which itself may be `None`).

    <!-- markdownlint-disable code-block-style -->
    ??? example

        ```python
        from pact.v3 import Verifier

        def user_state_callback(
            params: dict[str, Any] | None,
        ) -> None:
            ...

        def no_users_state_callback(
            params: dict[str, Any] | None,
        ) -> None:
            ...

        def test_provider():
            verifier = Verifier("provider_name")
            verifier.state_handler(
                {
                    "a user with ID 123 exists": user_state_callback,
                    "no users exist": no_users_state_callback,
                },
                teardown=False,
            )
        ```

## Functional Message Producer

In the messaging paradigm, the Pact consumer consumes the message produced by the provider (which is often referred to as the "producer"). As there are many and varied transport mechanisms for messages, Pact approaches the verification of messages in a transport-agnostic way. Previously, the provider would need to define a special HTTP endpoint to generate the message, and then pass the URL of that endpoint to the `Verifier` object. This process was cumbersome, especially considering that most producers do not expose any HTTP endpoints to begin with.

With the update to 2.3.0, the `Verifier` class has a new `message_handler` method which allows the provider to pass a function that generates the message. This function is called by the `Verifier` object when it needs a message to verify. The following code snippet demonstrates how to set up a message producer that uses a custom endpoint to generate the message:

<!-- markdownlint-disable code-block-style -->
???+ example

    ```python
    from pact.v3 import Verifier
    from pact.v3.types import Message

    def message_producer_callback(
        name: str,  # (1)
        params: dict[str, Any] | None,  # (2)
    ) -> Message:
        """
        Callback to produce the message that the consumer expects.

        Args:
            name:
                The name of the message. For example `"request to delete a user"`.

            params:
                If the message has additional parameters, they will be passed here.
                For example, one could specify the user ID to delete in the
                parameters instead of the message.

        Returns:
            The message that the consumer expects.
        """
        ...

    def test_provider():
        verifier = Verifier("provider_name")
        verifier.message_handler(message_producer_callback)
    ```

    1.  The `name` parameter is the name of the message. For example, `"request to delete a user"`. If you instead use a mapping of message names to functions, this parameter is not passed to the function.
    2.  The `params` parameter is a dictionary of additional parameters that the message requires. For example, one could specify the user ID to delete in the parameters instead of the message. Note that `params` is always present, but may be `None` if no parameters are specified by the consumer.
<!-- markdownlint-enable code-block-style -->

The output of the callback function should be an instance of the `Message` type. This is a simple [TypedDict][typing.TypedDict] that represents the message that the consumer expects and can be specified as a simple dictionary, or with typing hints through the `Message` constructor:

<!-- markdownlint-disable code-block-style -->
=== "With typing hints"

    ```python
    from pact.v3.types import Message

    def message_producer_callback(
        name: str,
        params: dict[str, Any] | None,
    ) -> Message:
        assert name == "request to delete a user"
        return Message(
            contents=json.dumps({
                "action": "delete_user",
                "user_id": "123",
            }).encode("utf-8"),
            metadata=None,
            content_type="application/json",
        )
    ```

=== "Without typing hints"

    ```python
    def message_producer_callback(
        name: str,
        params: dict[str, Any] | None,
    ) -> dict[str, Any]:
        assert name == "request to delete a user"
        return {
            "contents": json.dumps({
                "action": "delete_user",
                "user_id": "123",
            }).encode("utf-8"),
            "metadata": None,
            "content_type": "application/json",
        }
    ```

In much the same way as the `state_handler` method, the `message_handler` method can also accept a mapping of message names to functions or raw messages. The function should expect only one argument: the `params` dictionary (which itself may be `None`); or if the message is static, the message can be provided directly:

<!-- markdownlint-disable code-block-style -->
???+ example

    ```python
    from pact.v3 import Verifier
    from pact.v3.types import Message

    def delete_user_message(params: dict[str, Any] | None) -> Message:
        ...

    def test_provider():
        verifier = Verifier("provider_name")
        verifier.message_handler(
            {
                "request to delete a user": delete_user_message,
                "create user": {
                    "contents": b"some message",
                    "metadata": None,
                    "content_type": "text/plain",
                },
            },
        )
    ```
<!-- markdownlint-enable code-block-style -->
