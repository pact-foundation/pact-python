import multiprocessing
import pytest
from ..src.todo_provider import create_app
from pact import VerifierV3
from flask import url_for
import platform
target_platform = platform.platform().lower()

@pytest.mark.skipif(
    'windows' in target_platform,
    reason="https://github.com/jarus/flask-testing/issues/44")
@pytest.fixture(scope='session')
def app():
    if 'macos' in target_platform:
        multiprocessing.set_start_method("fork")  # Issue on MacOS - https://github.com/pytest-dev/pytest-flask/issues/104
        # Also an issue on windows - using fork or using spawn
        # see https://github.com/jarus/flask-testing/issues/44
        # and https://github.com/uqfoundation/dill/issues/245
    return create_app()

@pytest.mark.skipif(
    'windows' in target_platform,
    reason="https://github.com/jarus/flask-testing/issues/44")
@pytest.mark.usefixtures('live_server')
def test_pact_json():
    verifier = VerifierV3(provider='TodoServiceV3',
                          provider_base_url=url_for('index', _external=True))
    result, logs = verifier.verify_pacts(
        sources=['./pacts/TodoApp-TodoServiceV3.json'],
        filter_description='"a request for projects"'
        # Note filter_description takes a regex, so it also matches a request for projects in XML
        # unless wrapped in quotes.
    )
    assert result == 0

@pytest.mark.skipif(
    'windows' in target_platform,
    reason="https://github.com/jarus/flask-testing/issues/44")
@pytest.mark.usefixtures('live_server')
def test_pact_image():
    verifier = VerifierV3(provider='TodoServiceV3',
                          provider_base_url=url_for('index', _external=True))
    result, logs = verifier.verify_pacts(
        sources=['./pacts/TodoApp-TodoServiceV3.json'],
        filter_description='a request to store an image against the project'
    )
    assert result == 0

@pytest.mark.skipif(
    'windows' in target_platform,
    reason="https://github.com/pact-foundation/pact-reference/issues/305")
@pytest.mark.usefixtures('live_server')
def test_pact_xml():
    verifier = VerifierV3(provider='TodoServiceV3',
                          provider_base_url=url_for('index', _external=True))
    result, logs = verifier.verify_pacts(
        sources=['./pacts/TodoApp-TodoServiceV3.json'],
        filter_description='a request for projects in XML',
    )
    assert result == 0
