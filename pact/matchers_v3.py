"""Classes for defining request and response data that is variable for the V3 Pact Spec."""
# from pact_python_v3 import generate_datetime_string
import datetime

from enum import Enum

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

class Format:
    """
    Class of regular expressions for common formats.

    Example:
    >>> from pact import Consumer, Provider
    >>> from pact.matchers import Format
    >>> pact = Consumer('consumer').has_pact_with(Provider('provider'))
    >>> (pact.given('the current user is logged in as `tester`')
    ...  .upon_receiving('a request for the user profile')
    ...  .with_request('get', '/profile')
    ...  .will_respond_with(200, body={
    ...    'id': Format().identifier,
    ...    'lastUpdated': Format().time
    ...  }))

    Would expect `id` to be any valid int and `lastUpdated` to be a valid time.
    When the consumer runs this contract, the value of that will be returned
    is the second value passed to Term in the given function, for the time
    example it would be datetime.datetime(2000, 2, 1, 12, 30, 0, 0).time()

    """

    def __init__(self):
        """Create a new Formatter."""
        self.identifier = self.integer_or_identifier()
        self.integer = self.integer_or_identifier()
        self.decimal = self.decimal()
        self.ip_address = self.ip_address()
        self.hexadecimal = self.hexadecimal()
        self.ipv6_address = self.ipv6_address()
        self.uuid = self.uuid()
        self.timestamp = self.timestamp()
        self.date = self.date()
        self.time = self.time()
        self.iso_datetime = self.iso_8601_datetime()
        self.iso_datetime_ms = self.iso_8601_datetime(with_ms=True)

    def integer_or_identifier(self):
        """
        Match any integer.

        :return: a Like object with an integer.
        :rtype: Like
        """
        return Like(1)

    def decimal(self):
        """
        Match any decimal.

        :return: a Like object with a decimal.
        :rtype: Like
        """
        return Like(1.0)

    def ip_address(self):
        """
        Match any ip address.

        :return: a Term object with an ip address regex.
        :rtype: Term
        """
        return Regex(self.Regexes.ip_address.value, '127.0.0.1')

    def hexadecimal(self):
        """
        Match any hexadecimal.

        :return: a Term object with a hexdecimal regex.
        :rtype: Term
        """
        return Regex(self.Regexes.hexadecimal.value, '3F')

    def ipv6_address(self):
        """
        Match any ipv6 address.

        :return: a Term object with an ipv6 address regex.
        :rtype: Term
        """
        return Regex(self.Regexes.ipv6_address.value, '::ffff:192.0.2.128')

    def uuid(self):
        """
        Match any uuid.

        :return: a Term object with a uuid regex.
        :rtype: Term
        """
        return Regex(
            self.Regexes.uuid.value, 'fc763eba-0905-41c5-a27f-3934ab26786c'
        )

    def timestamp(self):
        """
        Match any timestamp.

        :return: a Term object with a timestamp regex.
        :rtype: Term
        """
        return Regex(
            self.Regexes.timestamp.value, datetime.datetime(
                2000, 2, 1, 12, 30, 0, 0
            ).isoformat()
        )

    def date(self):
        """
        Match any date.

        :return: a Term object with a date regex.
        :rtype: Term
        """
        return Regex(
            self.Regexes.date.value, datetime.datetime(
                2000, 2, 1, 12, 30, 0, 0
            ).date().isoformat()
        )

    def time(self):
        """
        Match any time.

        :return: a Term object with a time regex.
        :rtype: Term
        """
        return Regex(
            self.Regexes.time_regex.value, datetime.datetime(
                2000, 2, 1, 12, 30, 0, 0
            ).time().isoformat()
        )

    def iso_8601_datetime(self, with_ms=False):
        """
        Match a string for a full ISO 8601 Date.

        Does not do any sort of date validation, only checks if the string is
        according to the ISO 8601 spec.

        This method differs from :func:`~pact.Format.timestamp`,
        :func:`~pact.Format.date` and :func:`~pact.Format.time` implementations
        in that it is more stringent and tests the string for exact match to
        the ISO 8601 dates format.

        Without `with_ms` will match string containing ISO 8601 formatted dates
        as stated bellow:

        * 2016-12-15T20:16:01
        * 2010-05-01T01:14:31.876
        * 2016-05-24T15:54:14.00000Z
        * 1994-11-05T08:15:30-05:00
        * 2002-01-31T23:00:00.1234-02:00
        * 1991-02-20T06:35:26.079043+00:00

        Otherwise, ONLY dates with milliseconds will match the pattern:

        * 2010-05-01T01:14:31.876
        * 2016-05-24T15:54:14.00000Z
        * 2002-01-31T23:00:00.1234-02:00
        * 1991-02-20T06:35:26.079043+00:00

        :param with_ms: Enforcing millisecond precision.
        :type with_ms: bool
        :return: a Term object with a date regex.
        :rtype: Term
        """
        date = [1991, 2, 20, 6, 35, 26]
        if with_ms:
            matcher = self.Regexes.iso_8601_datetime_ms.value
            date.append(79043)
        else:
            matcher = self.Regexes.iso_8601_datetime.value

        return Regex(
            matcher,
            datetime.datetime(*date, tzinfo=datetime.timezone.utc).isoformat()
        )

    class Regexes(Enum):
        """Regex Enum for common formats."""

        ip_address = r'(\d{1,3}\.)+\d{1,3}'
        hexadecimal = r'[0-9a-fA-F]+'
        ipv6_address = r'(\A([0-9a-f]{1,4}:){1,1}(:[0-9a-f]{1,4}){1,6}\Z)|' \
            r'(\A([0-9a-f]{1,4}:){1,2}(:[0-9a-f]{1,4}){1,5}\Z)|(\A([0-9a-f]' \
            r'{1,4}:){1,3}(:[0-9a-f]{1,4}){1,4}\Z)|(\A([0-9a-f]{1,4}:)' \
            r'{1,4}(:[0-9a-f]{1,4}){1,3}\Z)|(\A([0-9a-f]{1,4}:){1,5}(:[0-' \
            r'9a-f]{1,4}){1,2}\Z)|(\A([0-9a-f]{1,4}:){1,6}(:[0-9a-f]{1,4})' \
            r'{1,1}\Z)|(\A(([0-9a-f]{1,4}:){1,7}|:):\Z)|(\A:(:[0-9a-f]{1,4})' \
            r'{1,7}\Z)|(\A((([0-9a-f]{1,4}:){6})(25[0-5]|2[0-4]\d|[0-1]' \
            r'?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3})\Z)|(\A(([0-9a-f]' \
            r'{1,4}:){5}[0-9a-f]{1,4}:(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25' \
            r'[0-5]|2[0-4]\d|[0-1]?\d?\d)){3})\Z)|(\A([0-9a-f]{1,4}:){5}:[' \
            r'0-9a-f]{1,4}:(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4' \
            r']\d|[0-1]?\d?\d)){3}\Z)|(\A([0-9a-f]{1,4}:){1,1}(:[0-9a-f]' \
            r'{1,4}){1,4}:(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]' \
            r'\d|[0-1]?\d?\d)){3}\Z)|(\A([0-9a-f]{1,4}:){1,2}(:[0-9a-f]{1,4}' \
            r'){1,3}:(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0' \
            r'-1]?\d?\d)){3}\Z)|(\A([0-9a-f]{1,4}:){1,3}(:[0-9a-f]{1,4}){1,' \
            r'2}:(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]' \
            r'?\d?\d)){3}\Z)|(\A([0-9a-f]{1,4}:){1,4}(:[0-9a-f]{1,4}){1,1}:' \
            r'(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?' \
            r'\d)){3}\Z)|(\A(([0-9a-f]{1,4}:){1,5}|:):(25[0-5]|2[0-4]\d|[0' \
            r'-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\Z)|(\A:(:[' \
            r'0-9a-f]{1,4}){1,5}:(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]' \
            r'|2[0-4]\d|[0-1]?\d?\d)){3}\Z)'
        uuid = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        timestamp = r'^([\+-]?\d{4}(?!\d{2}\b))((-?)((0[1-9]|1[0-2])(\3(' \
            r'[12]\d|0[1-9]|3[01]))?|W([0-4]\d|5[0-2])(-?[1-7])?|(00[1-' \
            r'9]|0[1-9]\d|[12]\d{2}|3([0-5]\d|6[1-6])))([T\s]((([01]\d|2' \
            r'[0-3])((:?)[0-5]\d)?|24\:?00)([\.,]\d+(?!:))?)?(\17[0-5]\d' \
            r'([\.,]\d+)?)?([zZ]|([\+-])([01]\d|2[0-3]):?([0-5]\d)?)?)?)?$'
        date = r'^([\+-]?\d{4}(?!\d{2}\b))((-?)((0[1-9]|1[0-2])(\3([12]\d|' \
            r'0[1-9]|3[01]))?|W([0-4]\d|5[0-2])(-?[1-7])?|(00[1-9]|0[1-9]\d|' \
            r'[12]\d{2}|3([0-5]\d|6[1-6])))?)'
        time_regex = r'^(T\d\d:\d\d(:\d\d)?(\.\d+)?(([+-]\d\d:\d\d)|Z)?)?$'
        iso_8601_datetime = r'^\d{4}-[01]\d-[0-3]\d\x54[0-2]\d:[0-6]\d:' \
                            r'[0-6]\d(?:\.\d+)?(?:(?:[+-]\d\d:\d\d)|\x5A)?$'
        iso_8601_datetime_ms = r'^\d{4}-[01]\d-[0-3]\d\x54[0-2]\d:[0-6]\d:' \
                               r'[0-6]\d\.\d+(?:(?:[+-]\d\d:\d\d)|\x5A)?$'
