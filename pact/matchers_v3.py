"""Classes for defining request and response data that is variable for the V3 Pact Spec."""
# from pact_python_v3 import generate_datetime_string


class V3Matcher(object):
    """Base class for defining complex contract expectations."""

    def generate(self):
        """
        Convert this matcher into an intermediate JSON format.

        :rtype: any
        """
        raise NotImplementedError


class EachLike(V3Matcher):
    """Expect the data to be a list of similar objects."""

    def __init__(self, template, minimum=None, maximum=None, examples=1):
        """
        Create a new EachLike.

        :param template: The template value that each item in a list should
            look like, this can be other matchers.
        :type template: None, list, dict, int, float, str, unicode, Matcher
        :param minimum: The minimum number of items expected.
            Must be greater than or equal to 0.
        :type minimum: int
        :param maximum: The maximum number of items expected.
            Must be greater than or equal to 1.
        :type minimum: int
        :param examples: The number of examples values to generate.
            Must be greater than or equal to 1.
        :type examples: int
        """
        self.template = template
        self.minimum = minimum
        self.maximum = maximum
        self.examples = examples

    def generate(self):
        """Generate the object."""
        json = {
            "pact:matcher:type": "type",
            'value': [self.template for i in range(self.examples)]
        }
        if self.minimum is not None:
            json['min'] = self.minimum
        if self.maximum is not None:
            json['max'] = self.maximum

        return json


class AtLeastOneLike(V3Matcher):
    """An array that has to have at least one element and each element must match the given template."""

    def __init__(self, template, examples=1):
        """
        Create a new EachLike.

        :param template: The template value that each item in a list should
            look like, this can be other matchers.
        :type template: None, list, dict, int, float, str, unicode, Matcher
        :param examples: The number of examples values to generate.
            Must be greater than or equal to 1.
        :type examples: int
        """
        self.template = template
        self.examples = examples

    def generate(self):
        """Generate the object."""
        return {
            "pact:matcher:type": "type",
            "min": 1,
            'value': [self.template for i in range(self.examples)]
        }


class Like(V3Matcher):
    """Value must be the same type as the example."""

    def __init__(self, example):
        """
        Create a new Like.

        :param example: The template value that each item in a list should
            look like,
        :type example: None, list, dict, int, float, str, unicode, Matcher
        """
        self.example = example

    def generate(self):
        """Generate the object."""
        return {
            "pact:matcher:type": "type",
            'value': self.example
        }


class Integer(V3Matcher):
    """Value must be an integer (must be a number and have no decimal places)."""

    def __init__(self, *args):
        """
        Define a new integer matcher.

        :param example: Example value to use. If not provided a random value will be generated.
        :type example: int
        """
        if len(args) > 0:
            self.example = args[0]
        else:
            self.example = None

    def generate(self):
        """Generate the object."""
        if self.example is not None:
            return {
                'pact:matcher:type': 'integer',
                'value': self.example
            }
        else:
            return {
                "pact:generator:type": "RandomInt",
                "pact:matcher:type": "integer",
                "value": 101
            }

class Regex(V3Matcher):
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
    ...    'theme': Regex('light|dark|legacy', 'dark')
    ...  }))

    Would expect the response body to be a JSON object, containing the key
    `name`, which will contain the value `tester`, and `theme` which must be
    one of the values: light, dark, or legacy. When the consumer runs this
    contract, the value `dark` will be returned by the mock service.

    """

    def __init__(self, matcher, generate):
        """
        Create a new Regex.

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
                "pact:matcher:type": "regex",
                "regex": self.matcher,
                "value": self._generate
            }

# class DateTime(V3Matcher):
#     """String value that must match the provided datetime format string."""

#     def __init__(self, format, *args):
#         """
#         Define a new datetime matcher.

#         :param format: Datetime format string. See [Java SimpleDateFormat](https://docs.oracle.com/javase/8/docs/api/java/text/SimpleDateFormat.html)
#         :type format: str
#         :param example: Example value to use. If omitted a value using the current system date and time will be generated.
#         :type example: str
#         """
#         self.format = format
#         if len(args) > 0:
#             self.example = args[0]
#         else:
#             self.example = None

#     def generate(self):
#         """Generate the object."""
#         if self.example is not None:
#             return {
#                 "pact:generator:type": "DateTime",
#                 "pact:matcher:type": "timestamp",
#                 "format": self.format,
#                 "value": self.example
#             }
#         else:
#             return {
#                 "pact:generator:type": "DateTime",
#                 "pact:matcher:type": "timestamp",
#                 "format": self.format,
#                 "value": generate_datetime_string(self.format),
#             }
