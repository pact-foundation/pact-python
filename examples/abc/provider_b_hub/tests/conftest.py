import pathlib
import sys
from multiprocessing import Process

import docker
import pytest
import requests_mock
from testcontainers.compose import DockerCompose

from src.provider_b import session
from .pact_provider_b import run_server


@pytest.fixture(scope="module")
def server():
    # Before running the server, setup a mock adapter to handle calls
    adapter = requests_mock.Adapter()
    session.mount("https://", adapter)

    proc = Process(target=run_server, args=(), daemon=True)
    proc.start()
    yield proc

    # Cleanup after test
    if sys.version_info >= (3, 7):
        # multiprocessing.kill is new in 3.7
        proc.kill()
    else:
        proc.terminate()


@pytest.fixture(scope="session", autouse=True)
def publish_existing_pact(broker):
    source = str(pathlib.Path.cwd().joinpath("..", "pacts").resolve())
    pacts = [f"{source}:/pacts"]
    envs = {
        "PACT_BROKER_BASE_URL": "http://broker_app:9292",
        "PACT_BROKER_USERNAME": "pactbroker",
        "PACT_BROKER_PASSWORD": "pactbroker",
    }

    client = docker.from_env()

    print("Publishing existing Pact")
    client.containers.run(
        remove=True,
        network="broker_default",
        volumes=pacts,
        image="pactfoundation/pact-cli:latest",
        environment=envs,
        command="publish /pacts --consumer-app-version 1",
    )
    print("Finished publishing")


@pytest.fixture(scope="session", autouse=True)
def broker():
    # Start up the broker using docker-compose
    print("Starting broker")
    with DockerCompose("../../broker", compose_file_name=["docker-compose.yml"], pull=True) as compose:
        stdout, stderr = compose.get_logs()
        if stderr:
            print("Errors\\n:{}".format(stderr))
        print("{}".format(stdout))
        print("Started broker")

        yield
        print("Stopping broker")
    print("Broker stopped")


# To help see what is going on, using this approach from: https://pythontesting.net/framework/pytest/pytest-session-scoped-fixtures/
# these are just some fun dividiers to make the output pretty
# completely unnecessary, I was just playing with autouse fixtures
@pytest.fixture(scope="function", autouse=True)
def divider_function(request):
    print("\n        --- function %s() start ---" % request.function.__name__)

    def fin():
        print("        --- function %s() done ---" % request.function.__name__)

    request.addfinalizer(fin)


@pytest.fixture(scope="module", autouse=True)
def divider_module(request):
    print("\n    ------- module %s start ---------" % request.module.__name__)

    def fin():
        print("    ------- module %s done ---------" % request.module.__name__)

    request.addfinalizer(fin)


@pytest.fixture(scope="session", autouse=True)
def divider_session(request):
    print("\n----------- session start ---------------")

    def fin():
        print("----------- session done ---------------")

    request.addfinalizer(fin)
