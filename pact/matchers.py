"""Classes for defining request and response data that is variable."""
import six


class Matcher(object):
    """Base class for defining complex contract expectations."""

    def generate(self):
        """
        Get the value that the mock service should use for this Matcher.

        :rtype: any
        """
        raise NotImplementedError


class EachLike(Matcher):
    """
    Expect the data to be a list of similar objects.

    Example:

    >>> from pact import Consumer, Provider
    >>> pact = Consumer('consumer').has_pact_with(Provider('provider'))
    >>> (pact.given('there are three comments')
    ...  .upon_receiving('a request for the most recent 2 comments')
    ...  .with_request('get', '/comment', query={'limit': 2})
    ...  .will_respond_with(200, body={
    ...    'comments': EachLike(
    ...        {'name': SomethingLike('bob'),
    ...         'text': SomethingLike('Hello!')},
    ...        minimum=2)
    ...  }))

    Would expect the response to be a JSON object, with a comments list. In
    that list should be at least 2 items, and each item should be a `dict`
    with the keys `name` and `text`,
    """

    def __init__(self, matcher, minimum=1):
        """
        Create a new EachLike.

        :param matcher: The expected value that each item in a list should
            look like, this can be other matchers.
        :type matcher: None, list, dict, int, float, str, unicode, Matcher
        :param minimum: The minimum number of items expected.
            Must be greater than or equal to 1.
        :type minimum: int
        """
        self.matcher = matcher
        assert minimum >= 1, 'Minimum must be greater than or equal to 1'
        self.minimum = minimum

    def generate(self):
        """
        Generate the value the mock service will return.

        :return: A dict containing the information about the contents of the
            list and the provided minimum number of items for that list.
        :rtype: dict
        """
        return {
            'json_class': 'Pact::ArrayLike',
            'contents': from_term(self.matcher),
            'min': self.minimum}


class SomethingLike(Matcher):
    """
    Expect the type of the value to be the same as matcher.

    Example:

    >>> from pact import Consumer, Provider
    >>> pact = Consumer('consumer').has_pact_with(Provider('provider'))
    >>> (pact
    ...  .given('there is a random number generator')
    ...  .upon_receiving('a request for a random number')
    ...  .with_request('get', '/generate-number')
    ...  .will_respond_with(200, body={
    ...    'number': SomethingLike(1111222233334444)
    ...  }))

    Would expect the response body to be a JSON object, containing the key
    `number`, which would contain an integer. When the consumer runs this
    contract, the value `1111222233334444` will be returned by the mock
    service, instead of a randomly generated value.
    """

    def __init__(self, matcher):
        """
        Create a new SomethingLike.

        :param matcher: The object that should be expected. The mock service
            will return this value. When verified against the provider, the
            type of this value will be asserted, while the value will be
            ignored.
        :type matcher: None, list, dict, int, float, str, unicode, Matcher
        """
        valid_types = (
            type(None), list, dict, int, float, six.string_types, Matcher)

        assert isinstance(matcher, valid_types), (
            "matcher must be one of '{}', got '{}'".format(
                valid_types, type(matcher)))

        self.matcher = matcher

    def generate(self):
        """
        Return the value that should be used in the request/response.

        :return: A dict containing the information about what the contents of
            the response should be.
        :rtype: dict
        """
        return {
            'json_class': 'Pact::SomethingLike',
            'contents': self.matcher}


class Term(Matcher):
    """
    Expect the response to match a specified regular expression.

    Example:

    >>> from pact import Consumer, Provider
    >>> pact = Consumer('consumer').has_pact_with(Provider('provider'))
    >>> (pact.given('the current user is logged in as `tester`')
    ...  .upon_receiving('a request for the user profile')
    ...  .with_request('get', '/profile')
    ...  .will_respond_with(200, body={
    ...    'name': 'tester',
    ...    'theme': Term('light|dark|legacy', 'dark')
    ...  }))

    Would expect the response body to be a JSON object, containing the key
    `name`, which will contain the value `tester`, and `theme` which must be
    one of the values: light, dark, or legacy. When the consumer runs this
    contract, the value `dark` will be returned by the mock service.
    """

    def __init__(self, matcher, generate):
        """
        Create a new Term.

        :param matcher: A regular expression to find.
        :type matcher: basestring
        :param generate: A value to be returned by the mock service when
            generating the response to the consumer.
        :type generate: basestring
        """
        self.matcher = matcher
        self._generate = generate

    def generate(self):
        """
        Return the value that should be used in the request/response.

        :return: A dict containing the information about what the contents of
            the response should be, and what should match for the requests.
        :rtype: dict
        """
        return {
            'json_class': 'Pact::Term',
            'data': {
                'generate': self._generate,
                'matcher': {
                    'json_class': 'Regexp',
                    'o': 0,
                    's': self.matcher}}}


def from_term(term):
    """
    Parse the provided term into the JSON for the mock service.

    :param term: The term to be parsed.
    :type term: None, list, dict, int, float, str, unicode, Matcher
    :return: The JSON representation for this term.
    :rtype: dict, list, str
    """
    if term is None:
        return term
    elif isinstance(term, (six.string_types, int, float)):
        return term
    elif isinstance(term, dict):
        return {k: from_term(v) for k, v in term.items()}
    elif isinstance(term, list):
        return [from_term(t) for i, t in enumerate(term)]
    elif issubclass(term.__class__, (Matcher,)):
        return term.generate()
    else:
        raise ValueError('Unknown type: %s' % type(term))
