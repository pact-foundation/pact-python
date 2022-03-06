import pathlib

import docker
import pytest
from testcontainers.compose import DockerCompose


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


@pytest.fixture(scope="session", autouse=True)
def publish_existing_pact(broker):
    """Publish the contents of the pacts folder to the Pact Broker.

    In normal usage, a Consumer would publish Pacts to the Pact Broker after
    running tests - this fixture would NOT be needed.
    .
    Because the broker is being used standalone here, it will not contain the
    required Pacts, so we must first spin up the pact-cli and publish them.

    In the Pact Broker logs, this corresponds to the following entry:
      PactBroker::Pacts::Service -- Creating new pact publication with params \
      {:consumer_name=>"UserServiceClient", :provider_name=>"UserService", \
      :revision_number=>nil, :consumer_version_number=>"1", :pact_version_sha=>nil, \
      :consumer_name_in_pact=>"UserServiceClient", :provider_name_in_pact=>"UserService"}
    """
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


def pytest_addoption(parser):
    parser.addoption(
        "--publish-pact", type=str, action="store", help="Upload generated pact file to pact broker with version"
    )

    parser.addoption("--run-broker", type=bool, action="store", help="Whether to run broker in this test or not.")
    parser.addoption("--provider-url", type=str, action="store", help="The url to our provider.")
