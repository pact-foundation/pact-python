"""Classes and methods to describe contract Consumers."""
from .message_pact import MessagePact
from .provider import Provider


class MessageConsumer(object):
    """
    A Pact message consumer.

    Use this class to describe the service making requests to the provider and
    then use `has_pact_with` to create a contract with a specific service:

    >>> from pact import MessageConsumer, Provider
    >>> message_consumer = MessageConsumer('my-web-front-end')
    >>> message_consumer.has_pact_with(Provider('my-backend-serivce'))
    """

    def __init__(
        self,
        name,
        service_cls=MessagePact,
        tags=None,
        tag_with_git_branch=False,
        version="0.0.0",
    ):
        """
        Create the Message Consumer class.

        :param name: The name of this Consumer. This will be shown in the Pact
            when it is published.
        :type name: str
        :param service_cls: Pact, or a sub-class of it, to use when creating
            the contracts. This is useful when you have a custom URL or port
            for your mock service and want to use the same value on all of
            your contracts.
        :type service_cls: pact.Pact
        :param tags: A list of strings to use as tags to use when publishing
            to a pact broker. Defaults to None.
        :type tags: list
        :param tag_with_git_branch: A flag to determine whether to
            automatically tag a pact with the current git branch name.
            Defaults to False.
        :type tag_with_git_branch: bool
        :param version: The version of this Consumer. This will be used when
            publishing pacts to a pact broker. Defaults to '0.0.0'
        """
        self.name = name
        self.service_cls = service_cls
        self.tags = tags
        self.tag_with_git_branch = tag_with_git_branch
        self.version = version

    def has_pact_with(
        self,
        provider,
        publish_to_broker=False,
        broker_base_url=None,
        broker_username=None,
        broker_password=None,
        broker_token=None,
        pact_dir=None,
        version="3.0.0",
        file_write_mode="merge",
    ):
        """
        Create a contract between the `provider` and this consumer.

        If you are running the Pact mock service in a non-default location,
        you can provide the host name and port here:

        >>> from pact import Consumer, Provider
        >>> consumer = Consumer('my-web-front-end')
        >>> consumer.has_pact_with(
        ...   Provider('my-backend-serivce'),
        ...   host_name='192.168.1.1',
        ...   port=8000)

        :param provider: The provider service for this contract.
        :type provider: pact.Provider
        :param host_name: An optional host name to use when contacting the
            Pact mock service. This will need to be the same host name used by
            your code under test to contact the mock service. It defaults to:
            `localhost`.
        :type host_name: str
        :param publish_to_broker: Flag to control automatic publishing of
            pacts to a pact broker. Defaults to False.
        :type publish_to_broker: bool
        :param broker_base_url: URL of the pact broker that pacts will be
            published to. Defaults to None.
        :type broker_base_url: str
        :param broker_username: Username to use when connecting to the pact
            broker if authentication is required. Defaults to None.
        :type broker_username: str
        :param broker_password: Password to use when connecting to the pact
            broker if authentication is required. Defaults to None.
        :type broker_password: str
        :param broker_token: Authentication token to use when connecting to
            the pact broker. Defaults to None.
        :type broker_token: str
        :param pact_dir: Directory where the resulting pact files will be
            written. Defaults to the current directory.
        :type pact_dir: str
        :param version: The Pact Specification version to use, defaults to
            '3.0.0'.
        :type version: str
        :param file_write_mode: How the mock service should apply multiple
            calls to .verify(). Pass 'overwrite' to overwrite the generated
            JSON file on every call to .verify() or pass 'merge' to merge all
            interactions into the same JSON file. When using 'merge', make
            sure to delete any existing JSON file before calling .verify()
            for the first time. Defaults to 'merge'.
        :type version: str
        :return: A Pact object which you can use to define the specific
            interactions your code will have with the provider.
        :rtype: pact.Pact
        """
        if not isinstance(provider, (Provider,)):
            raise ValueError("provider must be an instance of the Provider class.")

        return self.service_cls(
            broker_base_url=broker_base_url,
            broker_username=broker_username,
            broker_password=broker_password,
            broker_token=broker_token,
            consumer=self,
            provider=provider,
            pact_dir=pact_dir,
            publish_to_broker=publish_to_broker,
            version=version,
            file_write_mode=file_write_mode,
        )
