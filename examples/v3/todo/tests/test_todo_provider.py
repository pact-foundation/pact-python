import pytest
from ..src.todo_provider import create_app
from pact import VerifierV3
from flask import url_for


@pytest.fixture(scope='session')
def app():
    return create_app()


@pytest.mark.usefixtures('live_server')
def test_pact_verification():
    verifier = VerifierV3(provider='TodoServiceV3',
                          provider_base_url=url_for('index', _external=True))
    assert verifier.verify_pacts(
        sources=['./pacts/TodoApp-TodoServiceV3.json']
    )

