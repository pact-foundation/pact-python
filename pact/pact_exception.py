"""Custom Pact Exception."""

class PactException(Exception):
    """PactException when input isn't valid.

    Args:
        Exception ([type]): [description]

    Raises:
        KeyError: [description]
        Exception: [description]

    Returns:
        [type]: [description]

    """

    def __init__(self, *args, **kwargs):
        """Create wrapper."""
        super().__init__(*args, **kwargs)
        self.message = args[0]
