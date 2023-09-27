"""Classes and methods to describe contract Providers."""


import warnings


class Provider(object):
    """A Pact provider."""

    def __init__(self, name):
        """
        Create a new Provider.

        :param name: The name of this provider. This will be shown in the Pact
            when it is published.
        :type name: str
        """
        warnings.warn(
            "This class will be deprecated Pact Python v3 "
            "(see pact-foundation/pact-python#396)",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self.name = name
