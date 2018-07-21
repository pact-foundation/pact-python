import atexit
from mock import patch
from unittest import TestCase

import requests

from pact import Consumer
from pact import Provider

pact = Consumer('failing-consumer').has_pact_with(
    Provider('provider'), pact_dir='./pacts', port=1235)

pact.start_service()
atexit.register(pact.stop_service)


class FailingVerification(TestCase):
    def setUp(self):
        super(FailingVerification, self).setUp()
        self.addCleanup(patch.stopall)

    def test_post_user_wrong_response(self):
        expected = {'name': 'Robert'}
        (pact
         .given('the user Bob is returned instead of Robert')
         .upon_receiving('a query for the user Robert')
         .with_request(
            'post',
            '/users/',
            body={'kind': 'name'},
            headers={'Accept': 'application/json'},
            query='Robert')
         .will_respond_with(
            200,
            body=expected,
            headers={'Content-Type': 'application/json'}))

        with pact:
            result = requests.post(
                'http://localhost:1235/users/?Robert',
                headers={'Accept': 'application/json'},
                json={'kind': 'name'})

        self.assertEqual(result.json(), expected)
