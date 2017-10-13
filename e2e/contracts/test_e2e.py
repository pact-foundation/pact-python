import atexit

import requests
import unittest

from pact import EachLike, SomethingLike, Term
from pact.consumer import Consumer
from pact.provider import Provider


pact = Consumer('consumer').has_pact_with(
    Provider('provider'), pact_dir='./pacts')

pact.start_service()
atexit.register(pact.stop_service)


class BaseTestCase(unittest.TestCase):
    pass


class ExactMatches(BaseTestCase):
    def test_get_user_sparse(self):
        expected = {'name': 'Jonas'}
        (pact
            .given('a simple json blob exists')
            .upon_receiving('a request for a user')
            .with_request('get', '/users/Jonas')
            .will_respond_with(200, body=expected))

        with pact:
            result = requests.get('http://localhost:1234/users/Jonas')

        self.assertEqual(result.json(), expected)

    def test_post_user_complex(self):
        expected = {'name': 'Jonas'}
        (pact
         .given('a simple json blob exists')
         .upon_receiving('a query for the user Jonas')
         .with_request(
            'post',
            '/users/',
            body={'kind': 'name'},
            headers={'Accept': 'application/json'},
            query='Jonas')
         .will_respond_with(
            200,
            body=expected,
            headers={'Content-Type': 'application/json'}))

        with pact:
            result = requests.post(
                'http://localhost:1234/users/?Jonas',
                headers={'Accept': 'application/json'},
                json={'kind': 'name'})

        self.assertEqual(result.json(), expected)

    def test_multiple_exact_matches(self):
        expected = {'name': 'Jonas'}
        (pact
         .given('a simple json blob exists')
         .upon_receiving('a request for a user')
         .with_request('get', '/users/Jonas')
         .will_respond_with(200, body=expected)
         .given('a complex json blob exists')
         .upon_receiving('a query for the user Jonas')
         .with_request(
            'post',
            '/users/',
            body={'kind': 'name'},
            headers={'Accept': 'application/json'},
            query='Jonas')
         .will_respond_with(
            200,
            body=expected,
            headers={'Content-Type': 'application/json'}))

        with pact:
            result_get = requests.get('http://localhost:1234/users/Jonas')
            result_post = requests.post(
                'http://localhost:1234/users/?Jonas',
                headers={'Accept': 'application/json'},
                json={'kind': 'name'})

        self.assertEqual(result_get.json(), expected)
        self.assertEqual(result_post.json(), expected)


class InexactMatches(BaseTestCase):
    def test_sparse(self):
        (pact
         .given('the user `bob` exists')
         .upon_receiving('a request for the user object of `bob`')
         .with_request('get', '/users/bob')
         .will_respond_with(200, body={
             'username': SomethingLike('bob'),
             'id': Term('\d+', '123')}))

        with pact:
            result = requests.get('http://localhost:1234/users/bob')

        self.assertEqual(result.json(), {'username': 'bob', 'id': '123'})

    def test_nested(self):
        (pact
         .given('a list of users exists')
         .upon_receiving('a query of all users')
         .with_request('get', '/users/', query={'limit': Term('\d+', '5')})
         .will_respond_with(200, body={'results': EachLike({
            'username': Term('\w+', 'bob'),
            'id': SomethingLike(123),
            'groups': EachLike(123),
            'meta': SomethingLike({
                'name': Term('.+', 'sample'),
                'value': Term('.+', 'data')
            })
         }, minimum=2)}))

        with pact:
            results = requests.get(
                'http://localhost:1234/users/?limit=4')

        self.assertEqual(results.json(), {
            'results': [
                {'username': 'bob', 'id': 123, 'groups': [123],
                 'meta': {'name': 'sample', 'value': 'data'}},
                {'username': 'bob', 'id': 123, 'groups': [123],
                 'meta': {'name': 'sample', 'value': 'data'}}]})

    def test_falsey_bodies(self):
        (pact
         .given('no users exist')
         .upon_receiving('a request to insert no users')
         .with_request('post', '/users/', body=[])
         .will_respond_with(200, body=[]))

        with pact:
            results = requests.post('http://localhost:1234/users/', json=[])

        self.assertEqual(results.json(), [])


class SyntaxErrors(BaseTestCase):
    def test_incorrect_number_of_arguments(self):
        (pact
         .given('a list of users exists')
         .upon_receiving('a request for a user')
         .with_request('get', '/users/')
         .will_respond_with(200, body={'results': []}))

        def two(a, b):
            print('Requires two arguments')

        with self.assertRaises(TypeError) as e:
            with pact:
                two('one')

            self.assertEqual(
                e.exception.message,
                'two() takes exactly 2 arguments (1 given)'
            )
