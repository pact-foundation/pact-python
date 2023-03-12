import datetime

from unittest import TestCase

from pact.matchers import EachLike, Like, Matcher, SomethingLike, \
    Term, Format, from_term, get_generated_values


class MatcherTestCase(TestCase):
    def test_generate(self):
        with self.assertRaises(NotImplementedError):
            Matcher().generate()


class EachLikeTestCase(TestCase):
    def test_default_options(self):
        generate = EachLike(1).generate()

        self.assertEqual(
            generate,
            {'json_class': 'Pact::ArrayLike', 'contents': 1, 'min': 1})

    def test_minimum(self):
        generate = EachLike(1, minimum=2).generate()

        self.assertEqual(
            generate,
            {'json_class': 'Pact::ArrayLike', 'contents': 1, 'min': 2})

    def test_minimum_assertion_error(self):
        with self.assertRaises(AssertionError) as e:
            EachLike(1, minimum=0)

        self.assertEqual(
            str(e.exception), 'Minimum must be greater than or equal to 1')

    def test_nested_matchers(self):
        matcher = EachLike({
            'username': Term('[a-z]+', 'user'),
            'id': SomethingLike(123)})

        generate = matcher.generate()

        self.assertEqual(
            generate,
            {'json_class': 'Pact::ArrayLike',
             'contents': {
                 'username': {
                     'json_class': 'Pact::Term',
                     'data': {
                         'matcher': {
                             'json_class': 'Regexp',
                             's': '[a-z]+',
                             'o': 0},
                         'generate': 'user'}},
                 'id': {
                     'json_class': 'Pact::SomethingLike',
                     'contents': 123}},
             'min': 1})


class LikeTestCase(TestCase):
    def test_is_something_like(self):
        self.assertIs(SomethingLike, Like)


class SomethingLikeTestCase(TestCase):
    def test_valid_types(self):
        types = [None, list(), dict(), 1, 1.0, 'string', u'unicode', Matcher()]

        for t in types:
            SomethingLike(t)

    def test_invalid_types(self):
        with self.assertRaises(AssertionError) as e:
            SomethingLike(set())

        self.assertIn('matcher must be one of ', str(e.exception))

    def test_basic_type(self):
        generate = SomethingLike(123).generate()

        self.assertEqual(
            generate,
            {'json_class': 'Pact::SomethingLike', 'contents': 123})

    def test_complex_type(self):
        generate = SomethingLike({'name': Term('.+', 'admin')}).generate()

        self.assertEqual(
            generate,
            {'json_class': 'Pact::SomethingLike',
             'contents': {'name': {
                 'json_class': 'Pact::Term',
                 'data': {
                     'matcher': {
                         'json_class': 'Regexp',
                         's': '.+',
                         'o': 0
                     },
                     'generate': 'admin'
                 }
             }}})


class TermTestCase(TestCase):
    def test_regex(self):
        generate = Term('[a-zA-Z]', 'abcXYZ').generate()

        self.assertEqual(
            generate,
            {'json_class': 'Pact::Term',
             'data': {
                 'matcher': {
                     'json_class': 'Regexp',
                     's': '[a-zA-Z]',
                     'o': 0},
                 'generate': 'abcXYZ'}})


class FromTermTestCase(TestCase):
    def test_dict(self):
        expected = {'administrator': False, 'id': 123, 'username': 'user'}
        self.assertEqual(from_term(expected), expected)

    def test_none(self):
        self.assertIsNone(from_term(None))

    def test_unicode(self):
        self.assertEqual(from_term(u'testing'), 'testing')

    def test_int(self):
        self.assertEqual(from_term(123), 123)

    def test_float(self):
        self.assertEqual(from_term(3.14), 3.14)

    def test_bytes(self):
        self.assertEqual(from_term(b'testing'), b'testing')

    def test_list(self):
        term = [1, 123, 'sample']
        self.assertEqual(from_term(term), term)

    def test_each_like(self):
        self.assertEqual(
            from_term(EachLike({'a': 1})),
            {'json_class': 'Pact::ArrayLike', 'contents': {'a': 1}, 'min': 1})

    def test_something_like(self):
        self.assertEqual(
            from_term(SomethingLike(123)),
            {'json_class': 'Pact::SomethingLike', 'contents': 123})

    def test_term(self):
        self.assertEqual(
            from_term(Term('[a-f0-9]+', 'abc123')),
            {'json_class': 'Pact::Term',
             'data': {
                 'matcher': {
                     'json_class': 'Regexp',
                     's': '[a-f0-9]+',
                     'o': 0},
                 'generate': 'abc123'}})

    def test_nested(self):
        request = [
            EachLike({
                'username': Term('[a-zA-Z]+', 'firstlast'),
                'id': SomethingLike(123)})]

        self.assertEqual(
            from_term(request),
            [{'contents': {
                'id': {
                    'contents': 123,
                    'json_class': 'Pact::SomethingLike'},
                'username': {
                    'data': {
                        'generate': 'firstlast',
                        'matcher': {
                            'json_class': 'Regexp',
                            'o': 0,
                            's': '[a-zA-Z]+'}},
                        'json_class': 'Pact::Term'}},
                'json_class': 'Pact::ArrayLike',
                'min': 1}])

    def test_unknown_type(self):
        with self.assertRaises(ValueError):
            from_term(set())


class GetGeneratedValuesTestCase(TestCase):
    def test_none(self):
        self.assertIsNone(get_generated_values(None))

    def test_bool(self):
        self.assertFalse(get_generated_values(False))

    def test_unicode(self):
        self.assertEqual(get_generated_values(u'testing'), 'testing')

    def test_int(self):
        self.assertEqual(get_generated_values(123), 123)

    def test_float(self):
        self.assertEqual(get_generated_values(3.14), 3.14)

    def test_list(self):
        term = [1, 123, 'sample']
        self.assertEqual(get_generated_values(term), term)

    def test_dict(self):
        expected = {'administrator': False, 'id': 123, 'username': 'user'}
        self.assertEqual(get_generated_values(expected), expected)

    def test_each_like(self):
        self.assertEqual(
            get_generated_values(EachLike({'a': 1})), [{'a': 1}])

    def test_each_like_minimum(self):
        self.assertEqual(get_generated_values(EachLike({'a': 1}, minimum=5)),
                         [{'a': 1}] * 5)

    def test_something_like(self):
        self.assertEqual(
            get_generated_values(SomethingLike(123)), 123)

    def test_term(self):
        self.assertEqual(
            get_generated_values(Term('[a-f0-9]+', 'abc123')), 'abc123')

    def test_nested(self):
        input = [
            EachLike({
                'username': Term('[a-zA-Z]+', 'firstlast'),
                'id': SomethingLike(123)})]
        self.assertEqual(
            get_generated_values(input),
            [[{'username': 'firstlast', 'id': 123}]])

    def test_unknown_type(self):
        with self.assertRaises(ValueError):
            get_generated_values(set())


class FormatTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.formatter = Format()

    def test_identifier(self):
        identifier = self.formatter.identifier.generate()
        self.assertEqual(
            identifier,
            {
                "json_class": "Pact::SomethingLike",
                "contents": 1
            }
        )

    def test_integer(self):
        integer = self.formatter.integer.generate()
        self.assertEqual(
            integer,
            {
                "json_class": "Pact::SomethingLike",
                "contents": 1
            }
        )

    def test_decimal(self):
        decimal = self.formatter.integer.generate()
        self.assertEqual(
            decimal,
            {
                "json_class": "Pact::SomethingLike",
                "contents": 1.0
            }
        )

    def test_ip_address(self):
        ip_address = self.formatter.ip_address.generate()
        self.assertEqual(
            ip_address,
            {
                "json_class": "Pact::Term",
                "json_class": "Pact::Term",
                "data": {
                    "matcher": {
                        "json_class": "Regexp",
                        "s": self.formatter.Regexes.ip_address.value,
                        "o": 0,
                    },
                    "generate": "127.0.0.1",
                },
            },
        )

    def test_hexadecimal(self):
        hexadecimal = self.formatter.hexadecimal.generate()
        self.assertEqual(
            hexadecimal,
            {
                "json_class": "Pact::Term",
                "json_class": "Pact::Term",
                "data": {
                    "matcher": {
                        "json_class": "Regexp",
                        "s": self.formatter.Regexes.hexadecimal.value,
                        "o": 0,
                    },
                    "generate": "3F",
                },
            },
        )

    def test_ipv6_address(self):
        ipv6_address = self.formatter.ipv6_address.generate()
        self.assertEqual(
            ipv6_address,
            {
                "json_class": "Pact::Term",
                "json_class": "Pact::Term",
                "data": {
                    "matcher": {
                        "json_class": "Regexp",
                        "s": self.formatter.Regexes.ipv6_address.value,
                        "o": 0,
                    },
                    "generate": "::ffff:192.0.2.128",
                },
            },
        )

    def test_uuid(self):
        uuid = self.formatter.uuid.generate()
        self.assertEqual(
            uuid,
            {
                "json_class": "Pact::Term",
                "json_class": "Pact::Term",
                "data": {
                    "matcher": {
                        "json_class": "Regexp",
                        "s": self.formatter.Regexes.uuid.value,
                        "o": 0,
                    },
                    "generate": "fc763eba-0905-41c5-a27f-3934ab26786c",
                },
            },
        )

    def test_timestamp(self):
        timestamp = self.formatter.timestamp.generate()
        self.assertEqual(
            timestamp,
            {
                "json_class": "Pact::Term",
                "json_class": "Pact::Term",
                "data": {
                    "matcher": {
                        "json_class": "Regexp",
                        "s": self.formatter.Regexes.timestamp.value,
                        "o": 0,
                    },
                    "generate": datetime.datetime(2000, 2, 1, 12, 30, 0, 0).isoformat(),
                },
            },
        )

    def test_date(self):
        date = self.formatter.date.generate()
        self.assertEqual(
            date,
            {
                "json_class": "Pact::Term",
                "json_class": "Pact::Term",
                "data": {
                    "matcher": {
                        "json_class": "Regexp",
                        "s": self.formatter.Regexes.date.value,
                        "o": 0,
                    },
                    "generate": datetime.datetime(
                        2000, 2, 1, 12, 30, 0, 0).date().isoformat(),
                },
            },
        )

    def test_time(self):
        time = self.formatter.time.generate()
        self.assertEqual(
            time,
            {
                "json_class": "Pact::Term",
                "json_class": "Pact::Term",
                "data": {
                    "matcher": {
                        "json_class": "Regexp",
                        "s": self.formatter.Regexes.time_regex.value,
                        "o": 0,
                    },
                    "generate": datetime.datetime(
                        2000, 2, 1, 12, 30, 0, 0).time().isoformat(),
                },
            },
        )

    def test_iso_8601_datetime(self):
        date = self.formatter.iso_datetime.generate()
        self.assertEqual(
            date,
            {
                "json_class": "Pact::Term",
                "json_class": "Pact::Term",
                "data": {
                    "matcher": {
                        "json_class": "Regexp",
                        "s": self.formatter.Regexes.iso_8601_datetime.value,
                        "o": 0,
                    },
                    "generate": datetime.datetime(
                        1991, 2, 20, 6, 35, 26,
                        tzinfo=datetime.timezone.utc
                    ).isoformat(),
                },
            },
        )

    def test_iso_8601_datetime_mills(self):
        date = self.formatter.iso_datetime_ms.generate()
        self.assertEqual(
            date,
            {
                "json_class": "Pact::Term",
                "json_class": "Pact::Term",
                "data": {
                    "matcher": {
                        "json_class": "Regexp",
                        "s": self.formatter.Regexes.iso_8601_datetime_ms.value,
                        "o": 0,
                    },
                    "generate": datetime.datetime(
                        1991, 2, 20, 6, 35, 26, 79043,
                        tzinfo=datetime.timezone.utc
                    ).isoformat(),
                },
            },
        )
