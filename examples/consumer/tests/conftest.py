import pytest
from testcontainers.compose import DockerCompose


def pytest_addoption(parser):
    parser.addoption(
        "--publish-pact",
        type=str,
        action="store",
        help="Upload generated Pact file to Pact Broker with the version provided",
    )

    parser.addoption("--run-broker", type=bool, action="store", help="Whether to run broker in this test or not")


# This fixture is to simulate a managed Pact Broker or Pactflow account.
# For almost all purposes outside this example, you will want to use a real
# broker. See https://github.com/pact-foundation/pact_broker for further details.
@pytest.fixture(scope="session", autouse=True)
def broker(request):
    version = request.config.getoption("--publish-pact")
    publish = True if version else False

    # If the results are not going to be published to the broker, there is
    # nothing further to do anyway
    if not publish:
        yield
        return

    run_broker = request.config.getoption("--run-broker")

    if run_broker:
        # Start up the broker using docker-compose
        print("Starting broker")
        with DockerCompose("../broker", compose_file_name=["docker-compose.yml"], pull=True) as compose:
            stdout, stderr = compose.get_logs()
            if stderr:
                print("Errors\\n:{}".format(stderr))
            print("{}".format(stdout))
            print("Started broker")

            yield
            print("Stopping broker")
        print("Broker stopped")
    else:
        # Assuming there is a broker available already, docker-compose has been
        # used manually as the --run-broker option has not been provided
        yield
        return
