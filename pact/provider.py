"""Classes and methods to describe contract Providers."""


class Provider(object):
    """A Pact provider."""

    def __init__(self, name):
        """
        Create a new Provider.

        :param name: The name of this provider. This will be shown in the Pact
            when it is published.
        :type name: str
        """
        self.name = name
